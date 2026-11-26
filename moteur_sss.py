import base64
import hashlib
import hmac
import html
import json
import os
import socket
import sys
import threading
import time

import sss_auth


def chemin_ressource(chemin_relatif):
    """Recupere le chemin exact, en script ou en binaire PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, chemin_relatif)
    return os.path.join(os.path.abspath("."), chemin_relatif)


HOST = '127.0.0.1'
PORT = 1965
ORIGINE_SERVEUR = "sss://127.0.0.1"
LANGUE_ACTIVE = "fr"

def tr(fr, en):
    return en if LANGUE_ACTIVE == "en" else fr
PUBLIC_DIR = chemin_ressource('public')
MAX_TAILLE_REQUETE = 16384  # 16 Ko : couvre Ed25519 + ML-DSA-65 tout en bloquant les abus RAM

LOCK_AUTH = threading.Lock()
DEFIS_ACTIFS = {}   # nonce_hex -> {"exp": int, "action": str, "fields": list[str]}
COMPTES_DEMO = {}   # id_compte -> {"ed_pub": bytes, "ml_pub": bytes, "totp_secret": str, "dernier_step": int}
FICHIER_COMPTES_DEMO = os.path.join(os.path.expanduser("~"), ".comptes_demo_sss.json")

def charger_comptes_demo():
    if not os.path.exists(FICHIER_COMPTES_DEMO):
        return
    try:
        with open(FICHIER_COMPTES_DEMO, "r", encoding="utf-8") as f:
            brut = json.load(f)
        for cid, c in brut.items():
            COMPTES_DEMO[cid] = {
                "ed_pub": base64.b64decode(c["ed_pub_b64"]),
                "ml_pub": base64.b64decode(c["ml_pub_b64"]),
                "totp_secret": c["totp_secret"],
                "dernier_step": int(c.get("dernier_step", -1)),
            }
    except Exception:
        pass

def sauvegarder_comptes_demo():
    try:
        brut = {
            cid: {
                "ed_pub_b64": base64.b64encode(c["ed_pub"]).decode("ascii"),
                "ml_pub_b64": base64.b64encode(c["ml_pub"]).decode("ascii"),
                "totp_secret": c["totp_secret"],
                "dernier_step": c["dernier_step"],
            }
            for cid, c in COMPTES_DEMO.items()
        }
        with open(FICHIER_COMPTES_DEMO, "w", encoding="utf-8") as f:
            json.dump(brut, f, indent=2)
    except Exception:
        pass

charger_comptes_demo()

def lire_requete(client):
    """Lit une ligne TCP complete jusqu'a \\n dans la limite de 16 Ko."""
    tampon = bytearray()
    while len(tampon) < MAX_TAILLE_REQUETE:
        morceau = client.recv(4096)
        if not morceau:
            break
        tampon.extend(morceau)
        if b"\n" in morceau:
            break
    return tampon.decode('utf-8', errors='ignore').strip()


def creer_defi_serveur(action, fields):
    nonce_bytes, exp = sss_auth.generer_defi(300)
    nonce_hex = nonce_bytes.hex()
    maintenant = int(time.time())
    with LOCK_AUTH:
        # Nettoyage des defis expires
        expires = [k for k, v in DEFIS_ACTIFS.items() if v["exp"] < maintenant]
        for k in expires:
            del DEFIS_ACTIFS[k]
        DEFIS_ACTIFS[nonce_hex] = {"exp": exp, "action": action, "fields": list(fields)}
    return nonce_hex, exp


def verifier_totp_unique(compte, code_saisi):
    """Verifie le code TOTP (RFC 6238) et interdit sa reutilisation dans la meme tranche de 30 s."""
    code_propre = code_saisi.strip().replace(" ", "")
    if len(code_propre) != 6 or not code_propre.isdigit():
        return False
    step_actuel = int(time.time()) // 30
    for decalage in (-1, 0, 1):
        step = step_actuel + decalage
        if step <= compte["dernier_step"]:
            continue
        attendu = sss_auth.calculer_code_totp(compte["totp_secret"], timestamp=step * 30)
        if hmac.compare_digest(code_propre, attendu):
            compte["dernier_step"] = step
            return True
    return False


def page_html(titre, corps):
    return (
        f"20 text/html\r\n"
        f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{html.escape(titre)}</title>"
        f"<style>body{{background:#0b101b;color:#e2e8f0;font-family:Segoe UI,sans-serif;padding:40px;max-width:760px;margin:auto;line-height:1.6;}}"
        f".card{{background:#111827;border:1px solid #1e293b;border-radius:10px;padding:24px;margin-top:20px;}}"
        f".btn{{display:inline-block;background:#38bdf8;color:#05080f;padding:12px 20px;border-radius:6px;text-decoration:none;font-weight:700;margin-right:10px;margin-top:10px;}}"
        f".btn-gold{{background:#D4AF37;color:#05080f;}}"
        f"code{{background:#1e293b;padding:3px 7px;border-radius:4px;color:#38bdf8;word-break:break-all;}}"
        f"</style></head><body>{corps}</body></html>"
    )


def generer_page_espace_client():
    n_reg, exp_reg = creer_defi_serveur("inscription", [])
    n_log, exp_log = creer_defi_serveur("connexion", ["nom", "prenom", "adresse_livraison"])
    n_contact, exp_contact = creer_defi_serveur("contact_entreprise", ["nom", "prenom", "email", "telephone"])
    n_achat, exp_achat = creer_defi_serveur("validation_achat", ["nom", "prenom", "adresse_livraison", "montant", "beneficiaire"])
    nb_comptes = len(COMPTES_DEMO)
    if LANGUE_ACTIVE == "en":
        corps = f"""
        <a href="sss://127.0.0.1/index.html" style="color:#94a3b8;text-decoration:none;">⬅ Triple S Home</a>
        <h1 style="color:#D4AF37;">🔐 Sovereign Client Portal (Demo v2.0)</h1>
        <p>100% native <code>sss://</code> authentication (port 1965, zero HTTP, zero JavaScript, zero passwords).</p>
        <div class="card">
            <h3>Step 1: Register your cryptographic identity</h3>
            <p>Sends only your public keys <b>Ed25519 + ML-DSA-65</b> derived for <code>sss://127.0.0.1</code> and generates your 2FA key (6 digits).</p>
            <p style="color:#94a3b8;font-size:13px;">Accounts stored locally: <b>{nb_comptes}</b></p>
            <a class="btn btn-gold" href="sss-auth://register?nonce={n_reg}&exp={exp_reg}">1. Register my Triple S identity</a>
        </div>
        <div class="card">
            <h3>Step 2: Two-factor login + consent</h3>
            <p>Requires post-quantum dual signature, your 6-digit code, and manual approval to share <code>nom</code>, <code>prenom</code> and <code>adresse_livraison</code>.</p>
            <a class="btn" href="sss-auth://login?nonce={n_log}&exp={exp_log}&fields=nom,prenom,adresse_livraison">2. Log in with Triple S</a>
        </div>
        <div class="card">
            <h3>Step 3: Contact the company (Demo — Zero spam)</h3>
            <p>Simulation: sends your chosen contact details with cryptographic proof that you are human.</p>
            <a class="btn" href="sss-auth://login?action=contact_entreprise&nonce={n_contact}&exp={exp_contact}&fields=nom,prenom,email,telephone">3. Contact the company (Demo)</a>
        </div>
        <div class="card">
            <h3>Step 4: Validate a purchase (Demo — 0.00 EUR)</h3>
            <p>No-charge simulation: signs the mock amount (<b>0.00 EUR</b>), beneficiary (<b>Groupe RIGAUD Tech</b>), and your delivery address.</p>
            <a class="btn btn-gold" href="sss-auth://login?action=validation_achat&montant=0.00%20EUR&beneficiaire=Groupe%20RIGAUD%20Tech&nonce={n_achat}&exp={exp_achat}&fields=nom,prenom,adresse_livraison">4. Validate purchase (Demo 0.00 EUR)</a>
        </div>
        <div class="card" style="border-color:#334155;">
            <h3>Help &amp; Reset</h3>
            <ul style="color:#94a3b8; font-size:13px; padding-left:18px; margin:0;">
                <li style="margin-bottom:8px;"><b>Lost passphrase:</b> your vault is encrypted locally and cannot be recovered. Delete <code>.identite_sss.vault</code> in your user folder (e.g. <code>C:\\Users\\YourName\\.identite_sss.vault</code>) to start fresh with a new identity.</li>
                <li><b>Lost 2FA link (demo mode only):</b> simply run <b>Step 1</b> again to generate a new QR code. <i>(In production, resetting 2FA requires verification with the company.)</i></li>
            </ul>
        </div>
        """
        return page_html("Triple S Client Portal", corps)

    corps = f"""
    <a href="sss://127.0.0.1/index.html" style="color:#94a3b8;text-decoration:none;">⬅ Accueil Triple S</a>
    <h1 style="color:#D4AF37;">🔐 Espace Client Souverain (Demo v2.0)</h1>
    <p>Authentification 100 % native <code>sss://</code> (port 1965, zero HTTP, zero JavaScript, zero mot de passe).</p>
    <div class="card">
        <h3>Etape 1 : Enregistrer votre identite cryptographique</h3>
        <p>Transmet uniquement vos cles publiques <b>Ed25519 + ML-DSA-65</b> derivees pour <code>sss://127.0.0.1</code> et genere votre cle 2FA (6 chiffres).</p>
        <p style="color:#94a3b8;font-size:13px;">Comptes enregistres en memoire locale : <b>{nb_comptes}</b></p>
        <a class="btn btn-gold" href="sss-auth://register?nonce={n_reg}&exp={exp_reg}">1. Inscrire mon identite Triple S</a>
    </div>
    <div class="card">
        <h3>Etape 2 : Connexion double facteur + consentement</h3>
        <p>Exige la double signature post-quantique, votre code a 6 chiffres et votre accord manuel pour transmettre <code>nom</code>, <code>prenom</code> et <code>adresse_livraison</code>.</p>
        <a class="btn" href="sss-auth://login?nonce={n_log}&exp={exp_log}&fields=nom,prenom,adresse_livraison">2. Me connecter avec Triple S</a>
    </div>
    <div class="card">
        <h3>Etape 3 : Contacter l'entreprise (Demo — Zero spam)</h3>
        <p>Simulation : transmet vos coordonnees choisies avec une preuve cryptographique que vous etes humain.</p>
        <a class="btn" href="sss-auth://login?action=contact_entreprise&nonce={n_contact}&exp={exp_contact}&fields=nom,prenom,email,telephone">3. Contacter l'entreprise (Demo)</a>
    </div>
    <div class="card">
        <h3>Etape 4 : Valider un achat (Demo — 0.00 EUR)</h3>
        <p>Simulation sans debit : signe le montant fictif (<b>0.00 EUR</b>), le beneficiaire (<b>Groupe RIGAUD Tech</b>) et votre adresse de livraison.</p>
        <a class="btn btn-gold" href="sss-auth://login?action=validation_achat&montant=0.00%20EUR&beneficiaire=Groupe%20RIGAUD%20Tech&nonce={n_achat}&exp={exp_achat}&fields=nom,prenom,adresse_livraison">4. Valider l'achat (Demo 0.00 EUR)</a>
    </div>
    <div class="card" style="border-color:#334155;">
        <h3>Aide et reinitialisation</h3>
        <ul style="color:#94a3b8; font-size:13px; padding-left:18px; margin:0;">
            <li style="margin-bottom:8px;"><b>Phrase secrete perdue :</b> votre coffre est chiffre localement et irrecuperable. Supprimez le fichier <code>.identite_sss.vault</code> dans votre dossier utilisateur (ex. <code>C:\\Users\\VotreNom\\.identite_sss.vault</code>) pour repartir a zero avec une nouvelle identite.</li>
            <li><b>Lien 2FA perdu (mode demo uniquement) :</b> relancez simplement l'<b>Etape 1</b> pour generer un nouveau QR code. <i>(En production, la reinitialisation du 2FA exige une verification aupres de l'entreprise.)</i></li>
        </ul>
    </div>
    """
    return page_html("Espace Client Triple S", corps)




def traiter_auth_register(json_str):
    try:
        data = json.loads(json_str)
        nonce_hex = data["nonce"]
        ed_pub = base64.b64decode(data["ed_pub_b64"])
        ml_pub = base64.b64decode(data["ml_pub_b64"])
        sig_ed = base64.b64decode(data["sig_ed_b64"])
        sig_ml = base64.b64decode(data["sig_ml_b64"])
    except Exception:
        return page_html("Erreur", "<h2 style='color:#ef4444;'>Requete d'inscription invalide.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    with LOCK_AUTH:
        defi = DEFIS_ACTIFS.pop(nonce_hex, None)
    if not defi or defi["action"] != "inscription":
        return page_html("Refuse", "<h2 style='color:#ef4444;'>Defi introuvable ou deja consomme.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    maintenant = int(time.time())
    if maintenant > defi["exp"]:
        return page_html("Refuse", f"<h2 style='color:#ef4444;'>Defi expire depuis {maintenant - defi['exp']} s (limite : 60 s).</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    msg = sss_auth.construire_message(ORIGINE_SERVEUR, "inscription", bytes.fromhex(nonce_hex), defi["exp"], b"")
    if not sss_auth.verifier_signature((ed_pub, ml_pub), (sig_ed, sig_ml), msg, expires=defi["exp"], maintenant=maintenant):
        return page_html("Refuse", "<h2 style='color:#ef4444;'>Double signature Ed25519 + ML-DSA-65 invalide.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    id_compte = hashlib.sha256(ed_pub + ml_pub).hexdigest()[:16]
    secret_totp = sss_auth.generer_secret_totp()
    uri = sss_auth.uri_totp(secret_totp, f"client-{id_compte}", "Triple S Demo")

    try:
     import segno
     qr_html = segno.make(uri).svg_inline(scale=4, dark="#e2e8f0", light="#111827")
    except Exception:
     qr_html = ""

    with LOCK_AUTH:
        COMPTES_DEMO[id_compte] = {
            "ed_pub": ed_pub,
            "ml_pub": ml_pub,
            "totp_secret": secret_totp,
            "dernier_step": -1,  
        }
        sauvegarder_comptes_demo()

    if LANGUE_ACTIVE == "en":
        corps = f"""
        <h1 style="color:#22c55e;">✅ Identity Registered (Ed25519 + ML-DSA-65)</h1>
        <div class="card">
            <p><b>Public account fingerprint:</b> <code>{html.escape(id_compte)}</code></p>
            <div style="margin: 16px 0;">{qr_html}</div>
            <p><b>2FA Secret (for Aegis, FreeOTP or Bitwarden):</b><br><code>{html.escape(secret_totp)}</code></p>
            <p style="font-size:12px;color:#94a3b8;">Standard URI: <code>{html.escape(uri)}</code></p>
            <p style="color:#f59e0b;font-size:13px;">No master secret was sent to this server.</p>
            <p style="background:#1c1917; border-left:3px solid #f59e0b; padding:10px 12px; font-size:13px; color:#fde68a;">
            <b>Important:</b> Save this QR code in your 2FA app before continuing — it will not be shown again.<br>
            <i>If lost, simply run <b>Step 1</b> again to generate a new 2FA link (the previous one will be replaced).</i>
            </p>
            <a class="btn" href="sss://127.0.0.1/espace-client.html">Go to Step 2: Login →</a>
        </div>
        """
        return page_html("Registration confirmed", corps)

    corps = f"""
    <h1 style="color:#22c55e;">✅ Identite enregistree (Ed25519 + ML-DSA-65)</h1>
    <div class="card">
        <p><b>Empreinte publique du compte :</b> <code>{html.escape(id_compte)}</code></p>
        <div style="margin: 16px 0;">{qr_html}</div>
        <p><b>Secret 2FA (a saisir dans Aegis, FreeOTP ou Bitwarden) :</b><br><code>{html.escape(secret_totp)}</code></p>
        <p style="font-size:12px;color:#94a3b8;">URI standard : <code>{html.escape(uri)}</code></p>
        <p style="color:#f59e0b;font-size:13px;">Aucun secret maitre n'a ete recu par ce serveur.</p>
        <p style="background:#1c1917; border-left:3px solid #f59e0b; padding:10px 12px; font-size:13px; color:#fde68a;">
        <b>Important :</b> Enregistrez bien ce QR code dans votre application 2FA (Aegis, FreeOTP, Bitwarden) avant de continuer — il ne sera plus affiché.<br>
        <i>En cas d'oubli ou de perte, il suffit de relancer l'<b>Étape 1 (Inscrire mon identité)</b> pour générer un nouveau lien 2FA (l'ancien sera automatiquement remplacé).</i>
        </p>
        <a class="btn" href="sss://127.0.0.1/espace-client.html">Passer a l'etape 2 : Connexion →</a>
    </div>
    """
    return page_html("Inscription validee", corps)


def traiter_auth_verify(json_str):
    try:
        data = json.loads(json_str)
        nonce_hex = data["nonce"]
        ed_pub = base64.b64decode(data["ed_pub_b64"])
        ml_pub = base64.b64decode(data["ml_pub_b64"])
        sig_ed = base64.b64decode(data["sig_ed_b64"])
        sig_ml = base64.b64decode(data["sig_ml_b64"])
        payload_json = data.get("payload_json", "{}")
        code_totp = data.get("code_totp", "")
        champs_recus = json.loads(payload_json)
        if not isinstance(champs_recus, dict):
            raise ValueError("Payload invalide")
    except Exception:
        return page_html("Erreur", "<h2 style='color:#ef4444;'>Requete d'authentification invalide.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    with LOCK_AUTH:
        defi = DEFIS_ACTIFS.pop(nonce_hex, None)
        id_compte = hashlib.sha256(ed_pub + ml_pub).hexdigest()[:16]
        compte = COMPTES_DEMO.get(id_compte)

    if not defi or defi["action"] not in ("connexion", "contact_entreprise", "validation_achat"):
        return page_html("Refuse", "<h2 style='color:#ef4444;'>Defi introuvable ou deja utilise.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    maintenant = int(time.time())
    if maintenant > defi["exp"]:
        return page_html("Refuse", f"<h2 style='color:#ef4444;'>Defi expire depuis {maintenant - defi['exp']} s (limite : 60 s).</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    if compte is None:
        return page_html("Inconnu", "<h2 style='color:#f59e0b;'>Compte non inscrit sur ce serveur.</h2><a class='btn btn-gold' href='sss://127.0.0.1/espace-client.html'>Inscrire mon identite</a>")

    if not set(champs_recus.keys()).issubset(set(defi["fields"])):
        return page_html("Refuse", "<h2 style='color:#ef4444;'>Champs non autorises dans le payload.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    msg = sss_auth.construire_message(
    ORIGINE_SERVEUR,
    defi["action"],
    bytes.fromhex(nonce_hex),
    defi["exp"],
    payload_json.encode("utf-8"),
)
    if not sss_auth.verifier_signature((compte["ed_pub"], compte["ml_pub"]), (sig_ed, sig_ml), msg, expires=defi["exp"], maintenant=maintenant):
        return page_html("Refuse", "<h2 style='color:#ef4444;'>Double signature Ed25519 + ML-DSA-65 refusee (cles ou message differents).</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    with LOCK_AUTH:
        totp_ok = verifier_totp_unique(compte, code_totp)
    if not totp_ok:
        return page_html("Refuse", "<h2 style='color:#ef4444;'>Code 2FA a 6 chiffres incorrect ou deja utilise.</h2><a class='btn' href='sss://127.0.0.1/espace-client.html'>Reessayer</a>")

    lignes = "".join(
        f"<li><b>{html.escape(str(k))} :</b> {html.escape(str(v) or '(non transmis)')}</li>"
        for k, v in champs_recus.items()
    )
    if LANGUE_ACTIVE == "en":
        corps = f"""
        <h1 style="color:#22c55e;">🛡️ Access Granted — Two-Factor Validated</h1>
        <p style="color:#94a3b8; font-size:13px;">Sessionless mode: no cookie is stored. Leaving this page or clicking Back immediately ends this access.</p>
        <div class="card">
            <p><b>Verified account:</b> <code>{html.escape(id_compte)}</code></p>
            <p><b>Verified proofs:</b> Ed25519 (64 B) + ML-DSA-65 (3,309 B) + 6-digit TOTP + One-time Nonce.</p>
            <h3>Data shared with your consent:</h3>
            <ul>{lignes}</ul>
            <a class="btn" href="sss://127.0.0.1/espace-client.html">Back to Client Portal</a>
        </div>
        """
        return page_html("Connected", corps)

    corps = f"""
    <h1 style="color:#22c55e;">🛡️ Acces autorise — Double facteur valide</h1>
    <p style="color:#94a3b8; font-size:13px;">Mode sans session : aucun cookie n'est stocké. Quitter cette page ou cliquer sur Retour met immédiatement fin à cet accès.</p>
    <div class="card">
        <p><b>Compte verifie :</b> <code>{html.escape(id_compte)}</code></p>
        <p><b>Preuves controlees :</b> Ed25519 (64 o) + ML-DSA-65 (3 309 o) + TOTP 6 chiffres + Nonce unique.</p>
        <h3>Donnees transmises avec votre consentement :</h3>
        <ul>{lignes}</ul>
        <a class="btn" href="sss://127.0.0.1/espace-client.html">Retour a l'espace client</a>
    </div>
    """
    return page_html("Connecte", corps)


def trouver_fichier(requete):
    nom = requete.replace('\\', '/').split('/')[-1] or "index.html"
    if not nom.endswith('.html'):
        return None
    racine = os.path.realpath(PUBLIC_DIR)
    if LANGUE_ACTIVE == "en" and not nom.endswith("-en.html"):
        nom_en = nom[:-5] + "-en.html"
        chemin_en = os.path.realpath(os.path.join(racine, nom_en))
        if os.path.normcase(os.path.dirname(chemin_en)) == os.path.normcase(racine) and os.path.isfile(chemin_en):
            return chemin_en
    chemin = os.path.realpath(os.path.join(racine, nom))
    if os.path.normcase(os.path.dirname(chemin)) != os.path.normcase(racine):
        return None
    if not os.path.isfile(chemin):
        return None
    return chemin


def traiter_client(client):
    try:
        client.settimeout(5)
        requete = lire_requete(client)

        if requete.startswith("AUTH_REGISTER "):
            client.sendall(traiter_auth_register(requete[14:]).encode('utf-8'))
            return

        if requete.startswith("AUTH_VERIFY "):
            client.sendall(traiter_auth_verify(requete[12:]).encode('utf-8'))
            return

        # Rejet strict de tout protocole non-SSS (ex: requetes HTTP GET/POST)
        if not requete.startswith("sss://"):
            client.sendall(b"59 Erreur : Protocole non autorise (HTTP refuse)\r\n")
            return

        if requete.rstrip("/") == "sss://127.0.0.1/espace-client.html":
            client.sendall(generer_page_espace_client().encode('utf-8'))
            return

        chemin = trouver_fichier(requete)
        if chemin is None:
            client.sendall(b"51 Erreur : Format interdit ou introuvable\r\n")
            return

        with open(chemin, 'r', encoding='utf-8') as f:
            contenu = f.read()

        if "<script" in contenu.lower() or "<iframe" in contenu.lower():
            client.sendall(b"52 Erreur fatale : Code dynamique bloque\r\n")
            return

        reponse = f"20 text/html\r\n{contenu}"
        client.sendall(reponse.encode('utf-8'))
    except Exception:
        pass
    finally:
        try:
            client.close()
        except Exception:
            pass


def demarrer_serveur_sss():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind((HOST, PORT))
    serveur.listen(5)

    while True:
        try:
            client, _adresse = serveur.accept()
        except OSError:
            continue
        threading.Thread(target=traiter_client, args=(client,), daemon=True).start()


if __name__ == "__main__":
    demarrer_serveur_sss()
