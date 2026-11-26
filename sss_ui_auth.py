"""Triple S - Fenetres natives de coffre chiffre et de consentement sss-auth://."""

from __future__ import annotations

import base64
import json
import socket
from urllib.parse import parse_qs, urlparse

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

import sss_auth
import sss_coffre

CHAMPS_AUTORISES = ("nom", "prenom", "date_naissance", "email", "telephone", "adresse_livraison")

LANGUE_ACTIVE = "fr"


def tr(fr: str, en: str) -> str:
    return en if LANGUE_ACTIVE == "en" else fr


class GestionnaireAuthSSS:
    
    def __init__(self):
        self.coffre: dict | None = None
        self._phrase: str | None = None

    def deverrouiller_ou_creer(self, parent) -> bool:
        if self.coffre is not None:
            return True

        if not sss_coffre.CHEMIN_COFFRE_DEFAUT.exists():
            return self._dialogue_creation(parent)
        return self._dialogue_deverrouillage(parent)

    def verrouiller(self) -> None:
        """Efface le coffre et la phrase secrete de la RAM apres chaque action."""
        self.coffre = None
        self._phrase = None

    def _dialogue_creation(self, parent) -> bool:
        dlg = QDialog(parent)
        dlg.setWindowTitle(tr("Creer votre coffre chiffre Triple S (v2.0)", "Create your Triple S encrypted vault (v2.0)"))
        dlg.setMinimumWidth(440)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(tr("Votre cle maitre 256 bits et vos donnees seront chiffrees localement (Argon2id + AES-256-GCM).", "Your 256-bit master key and data will be encrypted locally (Argon2id + AES-256-GCM).")))

        form = QFormLayout()
        p1 = QLineEdit(); p1.setEchoMode(QLineEdit.EchoMode.Password)
        p2 = QLineEdit(); p2.setEchoMode(QLineEdit.EchoMode.Password)
        nom = QLineEdit()
        prenom = QLineEdit()
        adresse = QLineEdit()

        form.addRow(tr("Phrase secrete (12 car. min) :", "Passphrase (12 chars min):"), p1)
        form.addRow(tr("Confirmer la phrase :", "Confirm passphrase:"), p2)
        form.addRow(tr("Nom (optionnel) :", "Last name (optional):"), nom)
        form.addRow(tr("Prenom (optionnel) :", "First name (optional):"), prenom)
        form.addRow(tr("Adresse livraison (optionnel) :", "Delivery address (optional):"), adresse)
        layout.addLayout(form)

        boutons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(dlg.accept)
        boutons.rejected.connect(dlg.reject)
        layout.addWidget(boutons)

        while dlg.exec() == QDialog.DialogCode.Accepted:
            if len(p1.text()) < 12:
               QMessageBox.warning(dlg, tr("Erreur", "Error"), tr("La phrase secrete doit faire au moins 12 caracteres.", "Passphrase must be at least 12 characters long."))
               continue
            if p1.text() != p2.text():
                QMessageBox.warning(dlg, tr("Erreur", "Error"), tr("Les deux phrases secretes ne correspondent pas.", "Passphrases do not match."))
                continue
            presence = {
                "nom": nom.text().strip(),
                "prenom": prenom.text().strip(),
                "date_naissance": "",
                "email": "",
                "telephone": "",
                "adresse_livraison": adresse.text().strip(),
            }
            self.coffre = sss_coffre.creer_coffre(p1.text(), presence_humaine=presence)
            self._phrase = p1.text()
            return True
        return False

    def _dialogue_deverrouillage(self, parent) -> bool:
        dlg = QDialog(parent)
        dlg.setWindowTitle(tr("Deverrouiller le coffre Triple S", "Unlock Triple S Vault"))
        dlg.setMinimumWidth(380)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(tr("Saisissez votre phrase secrete pour debloquer la signature locale :", "Enter your passphrase to unlock local signing:")))
        champ = QLineEdit()
        champ.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(champ)

        boutons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(dlg.accept)
        boutons.rejected.connect(dlg.reject)
        layout.addWidget(boutons)

        while dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.coffre = sss_coffre.charger_coffre(champ.text())
                self._phrase = champ.text()
                return True
            except ValueError as err:
                QMessageBox.warning(dlg, tr("Acces refuse", "Access Denied"), str(err))
                champ.clear()
        return False

    def ouvrir_profil(self, parent) -> None:
        if not self.deverrouiller_ou_creer(parent):
            return
        dlg = QDialog(parent)
        dlg.setWindowTitle(tr("Mon coffre chiffre Triple S", "My Triple S Encrypted Vault"))
        dlg.setMinimumWidth(440)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel(tr("Ces informations restent chiffrees sur votre PC et ne sortent jamais sans votre validation :", "This information stays encrypted on your PC and is never shared without your approval:")))

        form = QFormLayout()
        champs_ui = {}
        presence = self.coffre.get("presence_humaine", {})
        for cle in CHAMPS_AUTORISES:
            ed = QLineEdit(presence.get(cle, ""))
            champs_ui[cle] = ed
            form.addRow(f"{cle} :", ed)
        layout.addLayout(form)

        boutons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        boutons.accepted.connect(dlg.accept)
        boutons.rejected.connect(dlg.reject)
        layout.addWidget(boutons)

        if dlg.exec() == QDialog.DialogCode.Accepted and self._phrase:
            self.coffre["presence_humaine"] = {k: ed.text().strip() for k, ed in champs_ui.items()}
            sss_coffre.sauvegarder_coffre(self.coffre, self._phrase)
            QMessageBox.information(parent, tr("Coffre sauvegarde", "Vault Saved"), tr("Vos donnees chiffrees ont ete mises a jour.", "Your encrypted data has been updated."))

    def _envoyer_tcp(self, cible_tcp: tuple[str, int], commande: str) -> str:
        ip, port = cible_tcp
        with socket.create_connection((ip, port), timeout=5) as sock:
            sock.sendall((commande + "\r\n").encode("utf-8"))
            morceaux = []
            while True:
                bloc = sock.recv(8192)
                if not bloc:
                    break
                morceaux.append(bloc)
        reponse = b"".join(morceaux).decode("utf-8", errors="ignore")
        parties = reponse.split("\r\n", 1)
        return parties[1] if len(parties) > 1 else reponse

    def traiter_lien_auth(
        self,
        parent,
        url_str: str,
        origine_sss: str | None,
        cible_tcp: tuple[str, int] | None,
    ) -> str | None:
        # Isolation stricte : interdit tout appel venant de http:// ou https://
        if not origine_sss or not origine_sss.startswith("sss://") or not cible_tcp:
            QMessageBox.critical(
              parent,
              tr("Securite Triple S", "Triple S Security"),
              tr("Action bloquee : seul un noeud natif sss:// peut demander une authentification.", "Action blocked: only a native sss:// node can request authentication."),
          )
            return None

        parsed = urlparse(url_str)
        mode = parsed.netloc.lower()
        params = parse_qs(parsed.query)
        nonce_hex = params.get("nonce", [""])[0]
        exp_str = params.get("exp", ["0"])[0]
        if not nonce_hex or not exp_str.isdigit():
            QMessageBox.warning(parent, tr("Defi invalide", "Invalid Challenge"), tr("Parametres cryptographiques manquants.", "Missing cryptographic parameters."))
            return None

        nonce_bytes = bytes.fromhex(nonce_hex)
        exp = int(exp_str)

        if not self.deverrouiller_ou_creer(parent):
            return None

        try:
            master = sss_coffre.extraire_secret_maitre(self.coffre)
            version = int(self.coffre.get("version_cle", 1))
            ed_pub, ml_pub = sss_auth.cles_publiques_site(master, origine_sss, version)

            if mode == "register":
                rep = QMessageBox.question(
                    parent,
                    tr("Consentement Triple S", "Triple S Consent"),
                    tr(
                        f"Domaine verifie : {origine_sss}\n"
                        "Action : Inscription cryptographique\n\n"
                        "Envoyer uniquement vos cles publiques Ed25519 + ML-DSA-65 dediees a ce domaine ?\n"
                        "(Aucun secret ni donnee personnelle ne quitte votre PC.)",
                        f"Verified domain: {origine_sss}\n"
                        "Action: Cryptographic registration\n\n"
                        "Send only your Ed25519 + ML-DSA-65 public keys dedicated to this domain?\n"
                        "(No secret or personal data leaves your PC.)",
                    ),
                )
                if rep != QMessageBox.StandardButton.Yes:
                    return None

                msg = sss_auth.construire_message(origine_sss, "inscription", nonce_bytes, exp, b"")
                sig_ed, sig_ml = sss_auth.signer_defi(master, origine_sss, msg, version)
                paquet = {
                    "nonce": nonce_hex,
                    "ed_pub_b64": base64.b64encode(ed_pub).decode("ascii"),
                    "ml_pub_b64": base64.b64encode(ml_pub).decode("ascii"),
                    "sig_ed_b64": base64.b64encode(sig_ed).decode("ascii"),
                    "sig_ml_b64": base64.b64encode(sig_ml).decode("ascii"),
                }
                return self._envoyer_tcp(cible_tcp, "AUTH_REGISTER " + json.dumps(paquet, separators=(",", ":")))

            if mode == "login":
                action = params.get("action", ["connexion"])[0]
                montant = params.get("montant", [""])[0]
                beneficiaire = params.get("beneficiaire", [""])[0]

                demandes = [
                    f.strip()
                    for f in params.get("fields", [""])[0].split(",")
                    if f.strip() in CHAMPS_AUTORISES
                ]
                dlg = QDialog(parent)
                dlg.setWindowTitle(tr(f"Consentement — {origine_sss}", f"Consent — {origine_sss}"))
                dlg.setMinimumWidth(460)
                layout = QVBoxLayout(dlg)
                layout.addWidget(QLabel(tr(f"<b>Domaine verifie par le navigateur :</b> {origine_sss}", f"<b>Browser-verified domain:</b> {origine_sss}")))

                if action == "contact_entreprise":
                  layout.addWidget(QLabel(tr("<b>Action :</b> Contacter l'entreprise (demande signee sans spam)", "<b>Action:</b> Contact company (signed zero-spam request)")))
                elif action == "validation_achat":
                  layout.addWidget(QLabel(tr("<b>Action :</b> Validation d'achat souveraine (Ed25519 + ML-DSA-65 + 2FA)", "<b>Action:</b> Sovereign purchase validation (Ed25519 + ML-DSA-65 + 2FA)")))
                  layout.addWidget(QLabel(tr(f"<b style='color:#D4AF37;'>Montant :</b> {montant} — <b>Beneficiaire :</b> {beneficiaire}", f"<b style='color:#D4AF37;'>Amount:</b> {montant} — <b>Beneficiary:</b> {beneficiaire}")))
                else:
                  layout.addWidget(QLabel(tr("<b>Action :</b> Connexion double facteur (Ed25519 + ML-DSA-65 + 2FA)", "<b>Action:</b> Two-factor login (Ed25519 + ML-DSA-65 + 2FA)")))

                presence = self.coffre.get("presence_humaine", {})
                cases = {}
                if demandes:
                  layout.addWidget(QLabel(tr("Cochez les donnees que vous acceptez de transmettre a ce domaine :", "Check the data you agree to share with this domain:")))
                  for champ in demandes:
                      val = presence.get(champ, "")
                      vide = tr("(vide)", "(empty)")
                      cb = QCheckBox(f"{champ} : {val if val else vide}")
                      cb.setChecked(bool(val))
                      cases[champ] = (cb, val)
                      layout.addWidget(cb)

                form_totp = QFormLayout()
                champ_totp = QLineEdit()
                champ_totp.setPlaceholderText("Ex. 482910")
                champ_totp.setMaxLength(6)
                form_totp.addRow(tr("Code 2FA a 6 chiffres :", "6-digit 2FA code:"), champ_totp)
                layout.addLayout(form_totp)

                boutons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
                boutons.accepted.connect(dlg.accept)
                boutons.rejected.connect(dlg.reject)
                layout.addWidget(boutons)

                if dlg.exec() != QDialog.DialogCode.Accepted:
                    return None

                donnees_validees = {k: val for k, (cb, val) in cases.items() if cb.isChecked()}
                if action == "validation_achat":
                    donnees_validees["montant"] = montant
                    donnees_validees["beneficiaire"] = beneficiaire

                payload_json = json.dumps(donnees_validees, ensure_ascii=False, sort_keys=True)
                msg = sss_auth.construire_message(
                    origine_sss, action, nonce_bytes, exp, payload_json.encode("utf-8")
                )
                sig_ed, sig_ml = sss_auth.signer_defi(master, origine_sss, msg, version)
                paquet = {
                    "nonce": nonce_hex,
                    "ed_pub_b64": base64.b64encode(ed_pub).decode("ascii"),
                    "ml_pub_b64": base64.b64encode(ml_pub).decode("ascii"),
                    "sig_ed_b64": base64.b64encode(sig_ed).decode("ascii"),
                    "sig_ml_b64": base64.b64encode(sig_ml).decode("ascii"),
                    "payload_json": payload_json,
                    "code_totp": champ_totp.text().strip(),
                }
                return self._envoyer_tcp(cible_tcp, "AUTH_VERIFY " + json.dumps(paquet, separators=(",", ":")))

            return None
        finally:
            self.verrouiller()