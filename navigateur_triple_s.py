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

    def charger_reseau_sss(self, url):
        # Traduction de ton domaine officiel vers ton fichier local
        if url.startswith("sss://grt.sss") or url.startswith("sss://sss.grt.sss"):
            url = "sss://127.0.0.1/mon_site_sss.html"

        contexte = ssl._create_unverified_context()
        try:
            connexion = socket.create_connection(('127.0.0.1', 1965), timeout=5)

            chemin = url.replace("sss://127.0.0.1", "")
            if not chemin or chemin == "/":
                chemin = "/index.html"

            requete = f"sss://127.0.0.1{chemin}\r\n"
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

            self.moteur.setHtml(html_brut, QUrl(url))

        except Exception as erreur:
            message_erreur = f"<h1 style='color:red;'>Erreur de connexion SSS</h1><p>{str(erreur)}</p>"
            self.moteur.setHtml(message_erreur, QUrl(url))

VERSION_ACTUELLE = "1.0.0"
URL_VERSION = "https://grouperigaudtech.fr/fichiers/version.txt"

def verifier_mise_a_jour():
    try:
        reponse = urllib.request.urlopen(URL_VERSION, timeout=3)
        version_serveur = reponse.read().decode('utf-8').strip()
        if version_serveur != VERSION_ACTUELLE and len(version_serveur) < 15 and "<" not in version_serveur:
            QMessageBox.information(
                None,
                "Mise à jour Triple S",
                f"Une nouvelle version ({version_serveur}) est disponible.\nTéléchargez-la sur grouperigaudtech.fr."
            )
    except:
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
    initialiser_identite_crypto()  # <-- Génère la clé au 1er lancement uniquement
    verifier_mise_a_jour()
    fenetre = NavigateurSSS()
    fenetre.show()
    sys.exit(app.exec())
