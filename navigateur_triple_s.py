import re
import sys
import socket
import ssl
import os
if sys.platform == "win32":
    import winreg
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
import urllib.request
import threading
import moteur_sss
import secrets
import json
from PyQt6.QtGui import QDesktopServices

class PageTripleS(QWebEnginePage):
    def __init__(self, navigateur, parent=None):
        super().__init__(parent)
        self.navigateur = navigateur

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()

        # 1. Autorise l'affichage interne du HTML (bloque l'erreur Windows 'data')
        if url.scheme() == "data":
            return True

        # 2. Interception de la barre de recherche centrale
        if "/recherche?q=" in url_str:
            mot_cle = url_str.split("?q=")[1].replace("+", " ")
            self.navigateur.barre_adresse.setText(mot_cle)
            self.navigateur.charger_url()
            return False

        # 3. Interception des liens sss:// et des fichiers locaux .html
        if url_str.startswith("sss://") or (url_str.endswith(".html") and not url_str.startswith("http")):
            if not url_str.startswith("sss://"):
                nom_fichier = url_str.split("/")[-1]
                url_str = f"sss://127.0.0.1/{nom_fichier}"
            self.navigateur.barre_adresse.setText(url_str)
            self.navigateur.charger_reseau_sss(url_str)
            return False
        # 4. Garde les liens relatifs des sites https_statique dans le protocole sss://
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked and url_str.startswith(("http://", "https://")):
            for dom, infos in REGISTRE_SSS.items():
                if infos.get("mode") == "https_statique":
                    cible = infos.get("cible", "").rstrip("/")
                    if cible and (url_str == cible or url_str.startswith(cible + "/")):
                        reste = url_str[len(cible):] or "/index.html"
                        nouvelle_url = f"sss://{dom}{reste}"
                        self.navigateur.barre_adresse.setText(nouvelle_url)
                        self.navigateur.charger_reseau_sss(nouvelle_url)
                        return False

        return super().acceptNavigationRequest(url, _type, isMainFrame)
class PageSecuriseeSSS(QWebEnginePage):
    def __init__(self, fenetre_principale):
        super().__init__(fenetre_principale)
        self.fenetre_principale = fenetre_principale

    def acceptNavigationRequest(self, url, type_nav, isMainFrame):
        if url.scheme() == "mailto":
            QDesktopServices.openUrl(url)
            return False
        if url.scheme() == "sss" and type_nav == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            self.fenetre_principale.barre_adresse.setText(url.toString())
            self.fenetre_principale.charger_reseau_sss(url.toString())
            return False
        return super().acceptNavigationRequest(url, type_nav, isMainFrame)

class NavigateurSSS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Triple S - Navigateur Sécurisé")
        self.setGeometry(100, 100, 1200, 800)

        layout_navigation = QHBoxLayout()

        self.bouton_retour = QPushButton("⬅ Retour")
        self.bouton_retour.setStyleSheet("background-color: #303134; color: #e8eaed; padding: 10px; border-radius: 4px;")
        self.bouton_retour.clicked.connect(self.action_retour)


        self.bouton_accueil = QPushButton("🏠 Accueil")
        self.bouton_accueil.setStyleSheet("background-color: #303134; color: #e8eaed; padding: 10px; border-radius: 4px;")
        self.bouton_accueil.clicked.connect(self.action_accueil)

        self.barre_adresse = QLineEdit()
        self.barre_adresse.setPlaceholderText("Entrez une adresse http:// ou sss://")
        self.barre_adresse.setStyleSheet("padding: 10px; font-size: 14px; background: #202124; color: #00ff00; border: 1px solid #5f6368; border-radius: 4px;")
        self.barre_adresse.returnPressed.connect(self.charger_url)

        layout_navigation.addWidget(self.bouton_retour)
        layout_navigation.addWidget(self.bouton_accueil)
        layout_navigation.addWidget(self.barre_adresse)

        self.moteur = QWebEngineView()
        
        # Injection de la page d'interception globale unique
        self.page_personnalisee = PageTripleS(self, self.moteur)
        self.moteur.setPage(self.page_personnalisee)
        
        reglages = self.moteur.settings()
        reglages.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        reglages.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)

        # Synchronisation de l'affichage de la barre d'adresse lors du changement de page
        self.moteur.urlChanged.connect(self.mettre_a_jour_barre)
       
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0) # Colle les éléments aux bords
        layout_principal.addLayout(layout_navigation)
        
        # 1. La page web prend tout l'espace central
        layout_principal.addWidget(self.moteur)
        
       

        conteneur = QWidget()
        conteneur.setLayout(layout_principal)
        conteneur.setStyleSheet("background-color: #0a0a0a;")
        self.setCentralWidget(conteneur)

        self.action_accueil()

    def mettre_a_jour_barre(self, qurl):
        self.barre_adresse.setText(qurl.toString())

    def action_retour(self):
        self.moteur.back()


    def action_accueil(self):
        self.barre_adresse.setText("sss://127.0.0.1/index.html")
        self.charger_url()

    def charger_url(self):
        saisie = self.barre_adresse.text().strip()
        if saisie.startswith("mailto:"):
            QDesktopServices.openUrl(QUrl(saisie))
            return
        
        if saisie.startswith("sss://"):
            self.charger_reseau_sss(saisie)
        elif saisie.startswith("http://") or saisie.startswith("https://"):
            self.moteur.setUrl(QUrl(saisie))
        elif "." in saisie and " " not in saisie:
            self.moteur.setUrl(QUrl("https://" + saisie))
        else:
            recherche_formatee = saisie.replace(" ", "+")
            url_moteur = f"https://lite.duckduckgo.com/lite/?q={recherche_formatee}"
            self.moteur.setUrl(QUrl(url_moteur))

    def _injecter_base_href(self, html_brut, base_url):
        if re.search(r"<base\b", html_brut, flags=re.IGNORECASE):
            return html_brut
        balise_base = f'<base href="{base_url}">'
        if re.search(r"<head[^>]*>", html_brut, flags=re.IGNORECASE):
            return re.sub(
                r"<head[^>]*>",
                lambda m: m.group(0) + "\n    " + balise_base,
                html_brut,
                count=1,
                flags=re.IGNORECASE
            )
        return balise_base + "\n" + html_brut        

    def charger_reseau_sss(self, url):
        # Découpage de l'URL : sss://domaine/chemin
        sans_protocole = url.replace("sss://", "", 1)
        if "/" in sans_protocole:
            domaine, reste = sans_protocole.split("/", 1)
            chemin = "/" + reste
        else:
            domaine = sans_protocole
            chemin = "/index.html"

        if chemin == "/":
            chemin = "/index.html"

        domaine = domaine.lower()

        # Annuaire dynamique généré directement depuis registre.json (Zéro-JS)
        if chemin == "/annuaire.html" or domaine == "annuaire.sss":
            self.moteur.setHtml(self.generer_annuaire_html(), QUrl("sss://annuaire.sss"))
            return

        # 1. Vérification dans le registre officiel .sss
        if domaine in REGISTRE_SSS:
            entree = REGISTRE_SSS[domaine]
            mode = entree.get("mode")

            # MODE 1 : Hébergement sur le domaine HTTPS actuel du client
            if mode == "https_statique":
                cible = entree["cible"].rstrip("/")
                url_distante = f"{cible}{chemin}"
                try:
                    req = urllib.request.Request(url_distante, headers={"User-Agent": "TripleS-Browser/1.2"})
                    reponse = urllib.request.urlopen(req, timeout=5)
                    html_brut = reponse.read().decode('utf-8', errors='ignore')
                    base_url = url_distante.rsplit("/", 1)[0] + "/"
                    html_brut = self._injecter_base_href(html_brut, base_url)
                    self.moteur.setHtml(html_brut, QUrl(url))
                    return
                except Exception as erreur:
                    msg = f"<h1 style='color:red;'>Site SSS inaccessible</h1><p>{str(erreur)}</p>"
                    self.moteur.setHtml(msg, QUrl(url))
                    return

            # MODE 2 : Fichier embarqué en local
            elif mode == "local":
                domaine = "127.0.0.1"
                chemin = entree.get("fichier", "/index.html")

            # MODE 3 : Serveur SSS distant (port 1965)
            elif mode == "noeud_sss":
                ip_cible = entree.get("ip", "127.0.0.1")
                port_cible = entree.get("port", 1965)
                self._requete_tcp_sss(ip_cible, port_cible, chemin, url)
                return

        # 2. Connexion locale directe (127.0.0.1)
        if domaine == "127.0.0.1":
            self._requete_tcp_sss("127.0.0.1", 1965, chemin, url)
        else:
            msg = (
                f"<h1 style='color:#D4AF37;'>Domaine non enregistré : {domaine}</h1>"
                f"<p>Ce domaine <code>.sss</code> n'existe pas encore dans le registre souverain.</p>"
                f"<p>Pour le réserver gratuitement (1er millier offert aux entreprises) : <b>contact@grouperigaudtech.fr</b></p>"
            )
            self.moteur.setHtml(msg, QUrl(url))

    def _requete_tcp_sss(self, ip, port, chemin, url_originale):
        try:
            connexion = socket.create_connection((ip, port), timeout=5)
            requete = f"sss://{ip}{chemin}\r\n"
            connexion.sendall(requete.encode('utf-8'))

            frag = []
            while True:
                donnees = connexion.recv(8192)
                if not donnees:
                    break
                frag.append(donnees)
            connexion.close()

            reponse = b"".join(frag).decode('utf-8', errors='ignore')
            lignes = reponse.split('\r\n', 1)
            html_brut = lignes[1] if len(lignes) > 1 else reponse
            self.moteur.setHtml(html_brut, QUrl(url_originale))
        except Exception as erreur:
            msg = f"<h1 style='color:red;'>Erreur de connexion SSS</h1><p>{str(erreur)}</p>"
            self.moteur.setHtml(msg, QUrl(url_originale))

    def generer_annuaire_html(self):
        lignes_html = ""
        for dom, infos in REGISTRE_SSS.items():
            if dom in ("sss.grt.sss", "demo.sss"):
                continue
            id_legal = infos.get("id_legal", infos.get("siret", "Vérifié"))
            mode = infos.get("mode", "https_statique")
            lignes_html += (
                f"<div style='background:#151c2c; border:1px solid #26334d; border-radius:8px; padding:16px; margin-bottom:12px;'>"
                f"<a href='sss://{dom}' style='color:#D4AF37; font-size:18px; font-weight:bold; text-decoration:none;'>sss://{dom}</a>"
                f"<div style='color:#94a3b8; font-size:13px; margin-top:6px;'>Identifiant légal : {id_legal} • Mode : {mode}</div>"
                f"</div>"
            )

        if not lignes_html:
            lignes_html = "<p style='color:#94a3b8;'>Aucun domaine enregistré pour le moment.</p>"

        return f"""
        <html>
        <body style="background:#0a0a0a; color:#e8eaed; font-family:Segoe UI, sans-serif; padding:40px; max-width:800px; margin:auto;">
            <a href="sss://127.0.0.1/index.html" style="color:#94a3b8; text-decoration:none;">← Retour Accueil</a>
            <h1 style="color:#D4AF37; margin-top:20px;">Annuaire Officiel Triple S</h1>
            <p style="color:#94a3b8; margin-bottom:30px;">Domaines souverains vérifiés et synchronisés en direct depuis le registre.</p>
            {lignes_html}
        </body>
        </html>
        """        

VERSION_ACTUELLE = "1.2.0"
URL_VERSION = "https://grouperigaudtech.fr/fichiers/version.txt"

URL_REGISTRE = "https://grouperigaudtech.fr/fichiers/registre.json"

# Registre par défaut si hors-ligne ou avant la mise en ligne du fichier
REGISTRE_SSS = {
    "grt.sss": {"mode": "local", "fichier": "/mon_site_sss.html"},
    "sss.grt.sss": {"mode": "local", "fichier": "/mon_site_sss.html"}
}

def charger_registre():
    global REGISTRE_SSS
    try:
        req = urllib.request.Request(URL_REGISTRE, headers={"User-Agent": "TripleS-Browser/1.2"})
        reponse = urllib.request.urlopen(req, timeout=3)
        contenu = reponse.read().decode('utf-8').strip()
        if contenu.startswith("{"):
            donnees = json.loads(contenu)
            REGISTRE_SSS.update(donnees)
    except Exception:
        pass

def verifier_mise_a_jour():
    try:
        reponse = urllib.request.urlopen(URL_VERSION, timeout=3)
        version_serveur = reponse.read().decode('utf-8').strip()
        if len(version_serveur) < 15 and "<" not in version_serveur:
            v_srv = tuple(int(x) for x in version_serveur.split(".") if x.isdigit())
            v_loc = tuple(int(x) for x in VERSION_ACTUELLE.split(".") if x.isdigit())
            if v_srv > v_loc:
                QMessageBox.information(
                    None,
                    "Mise à jour Triple S",
                    f"Une nouvelle version ({version_serveur}) est disponible.\nTéléchargez-la sur grouperigaudtech.fr."
                )
    except Exception:
        pass

def initialiser_identite_crypto():
    chemin_cle = os.path.join(os.path.expanduser("~"), ".identite_sss.json")
    
    if not os.path.exists(chemin_cle):
        # Alphabet de 34 caractères (Chiffres 1-9 et Lettres A-Z sans le 0 ni le O)
        alphabet_sss = "123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
        
        # Tirage cryptographique matériel de 52 caractères (Entropie > 264 bits / Post-Quantique)
        raw_key = "".join(secrets.choice(alphabet_sss) for _ in range(52))
        
        # Formatage avec tirets de confort (13 blocs de 4)
        cle_formatee = "-".join([raw_key[i:i+4] for i in range(0, 52, 4)])
        
        coffre_identite = {
            "cle_publique_sss": cle_formatee,
            "version_protocole": "1.0",
            "presence_humaine": {
                "nom": "",
                "prenom": "",
                "date_naissance": "",
                "email": "",
                "telephone": "",
                "adresse_livraison": ""
            }
        }
        
        try:
            with open(chemin_cle, "w", encoding="utf-8") as f:
                json.dump(coffre_identite, f, indent=4)
                
            msg = QMessageBox()
            msg.setWindowTitle("Identité Cryptographique Triple S")
            msg.setText(
                f"Bienvenue sur le réseau souverain Triple S.\n\n"
                f"Voici votre clé d'identification unique (52 caractères — 264 bits) :\n\n"
                f"{cle_formatee}\n\n"
                f"Aucune copie n'est stockée sur un serveur central. Cliquez ci-dessous pour la copier."
            )
            btn_copier = msg.addButton("📋 Copier la clé et fermer", QMessageBox.ButtonRole.AcceptRole)
            msg.exec()
            
            QApplication.clipboard().setText(cle_formatee)
        except Exception:
            pass

def installer_registre():

    if sys.platform != "win32":
        return
    # (laisse le reste de ta fonction Windows intact en dessous)
    
    chemin_exe = os.path.abspath(sys.executable)
    # L'installation s'arrête si le script n'est pas un .exe compilé
    if not chemin_exe.endswith('.exe'):
        return 

    cle_chemin = r"Software\Classes\sss"
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, cle_chemin)
        cle = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cle_chemin, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(cle, "", 0, winreg.REG_SZ, "URL:Protocole Triple S")
        winreg.SetValueEx(cle, "URL Protocol", 0, winreg.REG_SZ, "")
        
        cle_commande = winreg.CreateKey(cle, r"shell\open\command")
        winreg.SetValueEx(cle_commande, "", 0, winreg.REG_SZ, f'"{chemin_exe}" "%1"')
        
        winreg.CloseKey(cle_commande)
        winreg.CloseKey(cle)
    except:
        pass

if __name__ == '__main__':
    installer_registre()
    
    # 1. On démarre le serveur en arrière-plan EN PREMIER
    thread_serveur = threading.Thread(target=moteur_sss.demarrer_serveur_sss, daemon=True)
    thread_serveur.start()
    
    # 2. On lance l'interface graphique ensuite
    app = QApplication(sys.argv)
    initialiser_identite_crypto()
    verifier_mise_a_jour()
    charger_registre()
    
    fenetre = NavigateurSSS()
    fenetre.show()
    sys.exit(app.exec())
