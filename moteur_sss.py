
import socket
import os
import sys
import threading
 
 
def chemin_ressource(chemin_relatif):
    """Récupère le chemin exact, que le code tourne en script ou en .exe PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, chemin_relatif)
    return os.path.join(os.path.abspath("."), chemin_relatif)
 
 
# Le serveur n'écoute QUE sur ce PC (127.0.0.1) : il n'est pas visible depuis le réseau.
HOST = '127.0.0.1'
PORT = 1965
PUBLIC_DIR = chemin_ressource('public')
 
 
def trouver_fichier(requete):
    """Retourne le chemin d'un fichier .html situé directement dans le dossier public,
    ou None si la demande est invalide ou sort du dossier."""
    # On ne garde que le dernier morceau, qu'il soit séparé par / ou par \ (Windows)
    nom = requete.replace('\\', '/').split('/')[-1] or "index.html"
    if not nom.endswith('.html'):
        return None
 
    racine = os.path.realpath(PUBLIC_DIR)
    chemin = os.path.realpath(os.path.join(racine, nom))
 
    # Le fichier doit se trouver exactement dans le dossier public
    if os.path.normcase(os.path.dirname(chemin)) != os.path.normcase(racine):
        return None
    if not os.path.isfile(chemin):
        return None
    return chemin
 
 
def traiter_client(client):
    try:
        client.settimeout(5)  # évite qu'un client silencieux bloque le serveur
        requete = client.recv(1024).decode('utf-8', errors='ignore').strip()
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
    # Autorise la réutilisation immédiate du port 1965 sans attendre le délai Windows
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind((HOST, PORT))
    serveur.listen(5)
 
    while True:
        try:
            client, _adresse = serveur.accept()
        except OSError:
            continue
        # Un thread par demande : un client lent ne bloque plus les autres
        threading.Thread(target=traiter_client, args=(client,), daemon=True).start()
 
 
if __name__ == "__main__":
    demarrer_serveur_sss()
