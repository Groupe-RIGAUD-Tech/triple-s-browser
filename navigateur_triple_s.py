import re
import sys
import socket
import os
if sys.platform == "win32":
    import winreg
from PyQt6.QtCore import QUrl, QTimer, QLocale
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtGui import QDesktopServices
import urllib.request
import threading
import moteur_sss
import sss_ui_auth
import secrets
import json

VERSION_ACTUELLE = "2.0.0"
URL_VERSION = "https://grouperigaudtech.fr/fichiers/version.txt"
URL_REGISTRE = "https://grouperigaudtech.fr/fichiers/registre.json"

# Registre par défaut si hors-ligne
REGISTRE_DEFAUT = {
    "grt.sss": {"mode": "local", "fichier": "/mon_site_sss.html"},
    "sss.grt.sss": {"mode": "local", "fichier": "/mon_site_sss.html"}
}
REGISTRE_SSS = dict(REGISTRE_DEFAUT)

TRADUCTIONS = {
    "fr": {
        "titre_fenetre": "Triple S - Navigateur Sécurisé",
        "btn_retour": "⬅ Retour",
        "btn_accueil": "🏠 Accueil",
        "placeholder_url": "Entrez une adresse http:// ou sss://",
        "tooltip_sync": "Synchroniser le registre officiel (.sss)",
        "tooltip_langue": "Passer l'interface en anglais (EN)",
        "bandeau_local": "🏠 Accueil Local Triple S (127.0.0.1:1965)  •  Bouclier Zéro-JS actif",
        "bandeau_annuaire": "📖 Annuaire Officiel Triple S  •  Domaines vérifiés en direct (Zéro-JS)",
        "bandeau_verifie": "🛡️ Domaine Vérifié : sss://{domaine}  •  ID Légal : {id_legal}  •  Zéro-JS / Zéro-Cookie",
        "bandeau_inconnu": "⚠️ Domaine non enregistré : sss://{domaine}  •  Absent du registre souverain",
        "bandeau_web": "🌐 Web classique (hors réseau .sss)  •  Identité légale non vérifiée par Triple S (Scripts bloqués)",
        "bandeau_sync_erreur": "⚠️ Synchronisation impossible : mode hors-ligne actif",
        "verifie": "Vérifié",
        "err_site_inaccessible": "Site SSS inaccessible",
        "err_connexion": "Erreur de connexion SSS",
        "non_enregistre_titre": "Domaine non enregistré : {domaine}",
        "non_enregistre_p1": "Ce domaine <code>.sss</code> n'existe pas encore dans le registre souverain.",
        "non_enregistre_p2": "Pour le réserver gratuitement (1er millier offert aux entreprises) : <b>contact@grouperigaudtech.fr</b>",
        "annuaire_retour": "← Retour Accueil",
        "annuaire_titre": "Annuaire Officiel Triple S",
        "annuaire_sous_titre": "Domaines souverains vérifiés et synchronisés en direct depuis le registre.",
        "annuaire_meta": "Identifiant légal : {id_legal} • Mode : {mode}",
        "annuaire_vide": "Aucun domaine enregistré pour le moment.",
        "maj_titre": "Mise à jour Triple S",
        "maj_texte": "Une nouvelle version ({version}) est disponible.\nTéléchargez-la sur grouperigaudtech.fr.",
        "cle_titre": "Identité Cryptographique Triple S",
        "cle_texte": (
            "Bienvenue sur le réseau souverain Triple S.\n\n"
            "Voici votre clé d'identification unique (52 caractères — 264 bits) :\n\n"
            "{cle}\n\n"
            "Aucune copie n'est stockée sur un serveur central. Cliquez ci-dessous pour la copier.",
        ),
        "cle_btn": "📋 Copier la clé et fermer",
        "maj_btn_dl": "⬇️ Télécharger maintenant",
        "maj_btn_plus_tard": "Plus tard",
    },
    "en": {
        "titre_fenetre": "Triple S - Secure Browser",
        "btn_retour": "⬅ Back",
        "btn_accueil": "🏠 Home",
        "placeholder_url": "Enter an http:// or sss:// address",
        "tooltip_sync": "Sync official sovereign registry (.sss)",
        "tooltip_langue": "Switch interface to French (FR)",
        "bandeau_local": "🏠 Triple S Local Home (127.0.0.1:1965)  •  Zero-JS Shield Active",
        "bandeau_annuaire": "📖 Official Triple S Directory  •  Live Verified Domains (Zero-JS)",
        "bandeau_verifie": "🛡️ Verified Domain: sss://{domaine}  •  Legal ID: {id_legal}  •  Zero-JS / Zero-Cookie",
        "bandeau_inconnu": "⚠️ Unregistered Domain: sss://{domaine}  •  Not in Sovereign Registry",
        "bandeau_web": "🌐 Standard Web (outside .sss network)  •  Legal identity not verified by Triple S (Scripts blocked)",
        "bandeau_sync_erreur": "⚠️ Sync failed: offline mode active",
        "verifie": "Verified",
        "err_site_inaccessible": "SSS Site Unreachable",
        "err_connexion": "SSS Connection Error",
        "non_enregistre_titre": "Unregistered domain: {domaine}",
        "non_enregistre_p1": "This <code>.sss</code> domain does not exist in the sovereign registry yet.",
        "non_enregistre_p2": "Reserve it for free (first 1,000 domains offered to businesses): <b>contact@grouperigaudtech.fr</b>",
        "annuaire_retour": "← Back to Home",
        "annuaire_titre": "Official Triple S Directory",
        "annuaire_sous_titre": "Verified sovereign domains synced live from the registry.",
        "annuaire_meta": "Legal ID: {id_legal} • Mode: {mode}",
        "annuaire_vide": "No registered domains yet.",
        "maj_titre": "Triple S Update",
        "maj_texte": "A new version ({version}) is available.\nDownload it at grouperigaudtech.fr.",
        "cle_titre": "Triple S Cryptographic Identity",
        "cle_texte": (
            "Welcome to the Triple S sovereign network.\n\n"
            "Here is your unique cryptographic identity key (52 characters — 264-bit):\n\n"
            "{cle}\n\n"
            "No copy is stored on any central server. Click below to copy it."
        ),
        "cle_btn": "📋 Copy key and close",
        "maj_btn_dl": "⬇️ Download now",
        "maj_btn_plus_tard": "Later",
    }
}


def detecter_langue():
    return "fr" if QLocale.system().name().lower().startswith("fr") else "en"


class PageTripleS(QWebEnginePage):
    def __init__(self, navigateur, parent=None):
        super().__init__(parent)
        self.navigateur = navigateur

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        url_str = url.toString()

        # 1. Autorise l'affichage interne du HTML (bloque l'erreur Windows 'data')
        if url.scheme() == "data":
            return True

        # 2. Ouverture native des liens mailto:
        if url.scheme() == "mailto":
            QDesktopServices.openUrl(url)
            return False

        # 2 bis. Interception native de l'authentification sss-auth:// (bloquee si la page vient de HTTP/HTTPS)
        if url.scheme() == "sss-auth":
            if not isMainFrame or self.url().scheme() in ("http", "https"):
                QMessageBox.critical(self.navigateur, "Securite Triple S", "Authentification refusee depuis le web HTTP/HTTPS.")
                return False
            QTimer.singleShot(0, lambda u=url_str: self.navigateur.executer_auth_sss(u))
            return False

        # 3. Interception de la barre de recherche centrale
        if "/recherche?q=" in url_str:
            mot_cle = url_str.split("?q=")[1].replace("+", " ")
            self.navigateur.barre_adresse.setText(mot_cle)
            self.navigateur.charger_url()
            return False

        # 4. Interception des liens sss:// et des fichiers locaux .html
        if url_str.startswith("sss://") or (url_str.endswith(".html") and not url_str.startswith("http")):
            if not url_str.startswith("sss://"):
                nom_fichier = url_str.split("/")[-1]
                url_str = f"sss://127.0.0.1/{nom_fichier}"
            self.navigateur.barre_adresse.setText(url_str)
            self.navigateur.charger_reseau_sss(url_str)
            
            return False

        # 5. Garde les liens relatifs des sites https_statique dans le protocole sss://
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


class NavigateurSSS(QMainWindow):
    def __init__(self, langue="fr"):
        super().__init__()
        self.langue = langue
        self.setGeometry(100, 100, 1200, 800)

        layout_navigation = QHBoxLayout()
        layout_navigation.setContentsMargins(6, 6, 6, 6)

        self.bouton_retour = QPushButton()
        self.bouton_retour.setStyleSheet("background-color: #303134; color: #e8eaed; padding: 10px; border-radius: 4px;")
        self.bouton_retour.clicked.connect(self.action_retour)

        self.bouton_accueil = QPushButton()
        self.bouton_accueil.setStyleSheet("background-color: #303134; color: #e8eaed; padding: 10px; border-radius: 4px;")
        self.bouton_accueil.clicked.connect(self.action_accueil)

        self.barre_adresse = QLineEdit()
        self.barre_adresse.setStyleSheet("padding: 10px; font-size: 14px; background: #202124; color: #00ff00; border: 1px solid #5f6368; border-radius: 4px;")
        self.barre_adresse.returnPressed.connect(self.charger_url)

        self.bouton_sync = QPushButton("🔄")
        self.bouton_sync.setStyleSheet("background-color: #303134; color: #D4AF37; padding: 10px 14px; border-radius: 4px; font-weight: bold;")
        self.bouton_sync.clicked.connect(self.action_synchroniser_registre)

        self.bouton_langue = QPushButton()
        self.bouton_langue.setStyleSheet("background-color: #303134; color: #D4AF37; padding: 10px 12px; border-radius: 4px; font-weight: bold;")
        self.bouton_langue.clicked.connect(self.action_basculer_langue)

        self.auth_sss = sss_ui_auth.GestionnaireAuthSSS()
        self.origine_courante_sss = None
        self.cible_tcp_courante = None

        self.bouton_coffre = QPushButton("🔑")
        self.bouton_coffre.setToolTip("Coffre chiffre Triple S")
        self.bouton_coffre.setStyleSheet("background-color: #303134; color: #D4AF37; padding: 10px 12px; border-radius: 4px; font-weight: bold;")
        self.bouton_coffre.clicked.connect(lambda: self.auth_sss.ouvrir_profil(self))

        layout_navigation.addWidget(self.bouton_retour)
        layout_navigation.addWidget(self.bouton_accueil)
        layout_navigation.addWidget(self.barre_adresse)
        layout_navigation.addWidget(self.bouton_sync)
        layout_navigation.addWidget(self.bouton_langue)
        layout_navigation.addWidget(self.bouton_coffre)

        self.bandeau_confiance = QLabel()
        self.bandeau_confiance.setFixedHeight(32)
        self.bandeau_confiance.setStyleSheet("background-color: #16171a; color: #9aa0a6; padding: 6px 14px; font-size: 12px; font-weight: bold; border-bottom: 1px solid #303134;")

        self.moteur = QWebEngineView()
        self.page_personnalisee = PageTripleS(self, self.moteur)
        self.moteur.setPage(self.page_personnalisee)

        reglages = self.moteur.settings()
        reglages.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)
        reglages.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)

        self.moteur.urlChanged.connect(self.mettre_a_jour_barre)

        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        layout_principal.addLayout(layout_navigation)
        layout_principal.addWidget(self.bandeau_confiance)
        layout_principal.addWidget(self.moteur,1)

        conteneur = QWidget()
        conteneur.setLayout(layout_principal)
        conteneur.setStyleSheet("background-color: #0a0a0a;")
        self.setCentralWidget(conteneur)

        self.appliquer_langue(recharger_page=False)
        self.action_accueil()

    def t(self, cle, **kwargs):
        texte = TRADUCTIONS[self.langue][cle]
        return texte.format(**kwargs) if kwargs else texte

    def appliquer_langue(self, recharger_page=True):
        moteur_sss.LANGUE_ACTIVE = self.langue
        sss_ui_auth.LANGUE_ACTIVE = self.langue
        self.setWindowTitle(self.t("titre_fenetre"))
        self.bouton_retour.setText(self.t("btn_retour"))
        self.bouton_accueil.setText(self.t("btn_accueil"))
        self.barre_adresse.setPlaceholderText(self.t("placeholder_url"))
        self.bouton_sync.setToolTip(self.t("tooltip_sync"))
        self.bouton_langue.setText(f"🌐 {self.langue.upper()}")
        self.bouton_langue.setToolTip(self.t("tooltip_langue"))

        url_courante = self.barre_adresse.text().strip()
        if url_courante:
          self.mettre_a_jour_bandeau(url_courante)
          if recharger_page and url_courante.startswith("sss://"):
              sans_proto = url_courante.replace("sss://", "", 1)
              domaine = sans_proto.split("/", 1)[0].lower()
              if domaine in ("annuaire.sss", "127.0.0.1") or domaine not in REGISTRE_SSS:
                  self.charger_reseau_sss(url_courante)         

    def action_basculer_langue(self):
        self.langue = "en" if self.langue == "fr" else "fr"
        self.appliquer_langue(recharger_page=True)

    def mettre_a_jour_barre(self, qurl):
        url_str = qurl.toString()
        self.barre_adresse.setText(url_str)
        self.mettre_a_jour_bandeau(url_str)

    def mettre_a_jour_bandeau(self, url_str):
        if not url_str or url_str.startswith(("data:", "about:")):
            return

        style_base = "padding: 6px 14px; font-size: 12px; font-weight: bold;"

        if url_str.startswith("sss://"):
            sans_proto = url_str.replace("sss://", "", 1)
            domaine = sans_proto.split("/", 1)[0].lower()
            chemin = "/" + sans_proto.split("/", 1)[1] if "/" in sans_proto else "/index.html"

           
            if domaine == "annuaire.sss" or chemin == "/annuaire.html":
                   self.bandeau_confiance.setText(self.t("bandeau_annuaire"))
                   self.bandeau_confiance.setStyleSheet(
                    f"background-color: #141a24; color: #D4AF37; border-bottom: 1px solid #26334d; {style_base}"
                )
            elif domaine in REGISTRE_SSS:
                infos = REGISTRE_SSS[domaine]
                id_legal = infos.get("id_legal", infos.get("siret", self.t("verifie")))
                self.bandeau_confiance.setText(
                    self.t("bandeau_verifie", domaine=domaine, id_legal=id_legal)
                )
                self.bandeau_confiance.setStyleSheet(
                    f"background-color: #1f1b0d; color: #D4AF37; border-bottom: 1px solid #D4AF37; {style_base}"
                )
            elif domaine == "127.0.0.1":
                self.bandeau_confiance.setText(self.t("bandeau_local"))
                self.bandeau_confiance.setStyleSheet(
                    f"background-color: #16171a; color: #9aa0a6; border-bottom: 1px solid #303134; {style_base}"
                )
            else:
                self.bandeau_confiance.setText(self.t("bandeau_inconnu", domaine=domaine))
                self.bandeau_confiance.setStyleSheet(
                    f"background-color: #261a0d; color: #f59e0b; border-bottom: 1px solid #f59e0b; {style_base}"
                )
        else:
            self.origine_courante_sss = None
            self.cible_tcp_courante = None
            self.bandeau_confiance.setText(self.t("bandeau_web"))
            self.bandeau_confiance.setStyleSheet(
                f"background-color: #202124; color: #9aa0a6; border-bottom: 1px solid #3c4043; {style_base}"
            )

    def action_synchroniser_registre(self):
        self.bouton_sync.setText("⏳")
        QApplication.processEvents()
        ok = charger_registre()
        if ok:
            self.bouton_sync.setText("✅")
            url_courante = self.barre_adresse.text().strip()
            if url_courante.startswith("sss://"):
                self.charger_reseau_sss(url_courante)
            else:
                self.mettre_a_jour_bandeau(url_courante)
        else:
            self.bouton_sync.setText("⚠️")
            self.bandeau_confiance.setText(self.t("bandeau_sync_erreur"))
            self.bandeau_confiance.setStyleSheet(
                "background-color: #261a0d; color: #f59e0b; padding: 6px 14px; font-size: 12px; font-weight: bold; border-bottom: 1px solid #f59e0b;"
            )
        QTimer.singleShot(1500, lambda: self.bouton_sync.setText("🔄"))

    def action_retour(self):
        self.moteur.back()

    def action_accueil(self):
        self.barre_adresse.setText("sss://127.0.0.1/index.html")
        self.charger_url()

    def executer_auth_sss(self, url_str):
        html_resultat = self.auth_sss.traiter_lien_auth(
            self,
            url_str,
            self.origine_courante_sss,
            self.cible_tcp_courante,
        )
        if html_resultat:
            url_actuelle = self.barre_adresse.text().strip()
            self.moteur.setHtml(html_resultat, QUrl(url_actuelle))

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
        self.mettre_a_jour_bandeau(url)
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

        self.origine_courante_sss = f"sss://{domaine}"
        self.cible_tcp_courante = None

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
                    req = urllib.request.Request(url_distante, headers={"User-Agent": f"TripleS-Browser/{VERSION_ACTUELLE}"})
                    reponse = urllib.request.urlopen(req, timeout=5)
                    html_brut = reponse.read().decode('utf-8', errors='ignore')
                    base_url = url_distante.rsplit("/", 1)[0] + "/"
                    html_brut = self._injecter_base_href(html_brut, base_url)
                    self.moteur.setHtml(html_brut, QUrl(url))
                    return
                except Exception as erreur:
                    msg = f"<h1 style='color:red;'>{self.t('err_site_inaccessible')}</h1><p>{str(erreur)}</p>"
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
                f"<body style='background:#0a0a0a; color:#e8eaed; font-family:Segoe UI, sans-serif; padding:40px;'>"
                f"<h1 style='color:#D4AF37;'>{self.t('non_enregistre_titre', domaine=domaine)}</h1>"
                f"<p>{self.t('non_enregistre_p1')}</p>"
                f"<p>{self.t('non_enregistre_p2')}</p>"
                f"</body>"
            )
            self.moteur.setHtml(msg, QUrl(url))

    def _requete_tcp_sss(self, ip, port, chemin, url_originale):
        try:
            self.cible_tcp_courante = (ip, port)
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
            msg = f"<h1 style='color:red;'>{self.t('err_connexion')}</h1><p>{str(erreur)}</p>"
            self.moteur.setHtml(msg, QUrl(url_originale))

    def generer_annuaire_html(self):
        lignes_html = ""
        for dom, infos in REGISTRE_SSS.items():
            if dom in ("sss.grt.sss", "demo.sss"):
                continue
            id_legal = infos.get("id_legal", infos.get("siret", self.t("verifie")))
            mode = infos.get("mode", "https_statique")
            meta = self.t("annuaire_meta", id_legal=id_legal, mode=mode)
            lignes_html += (
                f"<div style='background:#151c2c; border:1px solid #26334d; border-radius:8px; padding:16px; margin-bottom:12px;'>"
                f"<a href='sss://{dom}' style='color:#D4AF37; font-size:18px; font-weight:bold; text-decoration:none;'>sss://{dom}</a>"
                f"<div style='color:#94a3b8; font-size:13px; margin-top:6px;'>{meta}</div>"
                f"</div>"
            )

        if not lignes_html:
            lignes_html = f"<p style='color:#94a3b8;'>{self.t('annuaire_vide')}</p>"

        return f"""
        <html>
        <body style="background:#0a0a0a; color:#e8eaed; font-family:Segoe UI, sans-serif; padding:40px; max-width:800px; margin:auto;">
            <a href="sss://127.0.0.1/index.html" style="color:#94a3b8; text-decoration:none;">{self.t('annuaire_retour')}</a>
            <h1 style="color:#D4AF37; margin-top:20px;">{self.t('annuaire_titre')}</h1>
            <p style="color:#94a3b8; margin-bottom:30px;">{self.t('annuaire_sous_titre')}</p>
            {lignes_html}
        </body>
        </html>
        """


def charger_registre():
    try:
        req = urllib.request.Request(
            URL_REGISTRE,
            headers={"User-Agent": f"TripleS-Browser/{VERSION_ACTUELLE}", "Cache-Control": "no-cache"}
        )
        reponse = urllib.request.urlopen(req, timeout=3)
        contenu = reponse.read().decode('utf-8').strip()
        if contenu.startswith("{"):
            donnees = json.loads(contenu)
            REGISTRE_SSS.clear()
            REGISTRE_SSS.update(REGISTRE_DEFAUT)
            REGISTRE_SSS.update(donnees)
            return True
    except Exception:
        pass
    return False


def verifier_mise_a_jour(langue="fr"):
    try:
        req = urllib.request.Request(URL_VERSION, headers={"User-Agent": f"TripleS-Browser/{VERSION_ACTUELLE}"})
        reponse = urllib.request.urlopen(req, timeout=3)
        version_serveur = reponse.read().decode('utf-8').strip()
        if len(version_serveur) < 15 and "<" not in version_serveur:
            v_srv = tuple(int(x) for x in version_serveur.split(".") if x.isdigit())
            v_loc = tuple(int(x) for x in VERSION_ACTUELLE.split(".") if x.isdigit())
            if v_srv > v_loc:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle(TRADUCTIONS[langue]["maj_titre"])
                msg.setText(TRADUCTIONS[langue]["maj_texte"].format(version=version_serveur))
                btn_dl = msg.addButton(TRADUCTIONS[langue]["maj_btn_dl"], QMessageBox.ButtonRole.AcceptRole)
                msg.addButton(TRADUCTIONS[langue]["maj_btn_plus_tard"], QMessageBox.ButtonRole.RejectRole)
                msg.exec()
                if msg.clickedButton() == btn_dl:
                    QDesktopServices.openUrl(QUrl("https://www.grouperigaudtech.fr/#triple-s"))
    except Exception:
        pass


def initialiser_identite_crypto(langue="fr"):
    chemin_cle = os.path.join(os.path.expanduser("~"), ".identite_sss.json")

    if not os.path.exists(chemin_cle):
        alphabet_sss = "123456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
        raw_key = "".join(secrets.choice(alphabet_sss) for _ in range(52))
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
            msg.setWindowTitle(TRADUCTIONS[langue]["cle_titre"])
            msg.setText(TRADUCTIONS[langue]["cle_texte"].format(cle=cle_formatee))
            msg.addButton(TRADUCTIONS[langue]["cle_btn"], QMessageBox.ButtonRole.AcceptRole)
            msg.exec()

            QApplication.clipboard().setText(cle_formatee)
        except Exception:
            pass


def installer_registre():
    if sys.platform != "win32":
        return

    chemin_exe = os.path.abspath(sys.executable)
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
    except Exception:
        pass


if __name__ == '__main__':
    installer_registre()

    thread_serveur = threading.Thread(target=moteur_sss.demarrer_serveur_sss, daemon=True)
    thread_serveur.start()

    app = QApplication(sys.argv)
    langue_init = detecter_langue()
    initialiser_identite_crypto(langue_init)
    verifier_mise_a_jour(langue_init)
    charger_registre()

    fenetre = NavigateurSSS(langue=langue_init)
    fenetre.show()
    sys.exit(app.exec())
