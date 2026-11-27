"""Triple S - Coffre d'identite chiffre multi-OS (Windows, Linux, macOS).

Chiffrement : Argon2id (RFC 9106) + AES-256-GCM (NIST SP 800-38D).
"""

from __future__ import annotations

import base64
import json
import os
import secrets
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

FORMAT_COFFRE = "sss-vault-v2"
CHEMIN_COFFRE_DEFAUT = Path.home() / ".identite_sss.vault"

# Parametres Argon2id (64 MiB, 3 iterations, 4 voies) conformes aux recommandations OWASP
PARAMS_ARGON2_DEFAUT = {
    "memory_cost": 65536,  # en KiB (64 MiB)
    "iterations": 3,
    "lanes": 4,
    "length": 32,
}


def _deriver_cle_coffre(phrase_secrete: str, sel: bytes, params: dict[str, int]) -> bytes:
    if not phrase_secrete or len(phrase_secrete) < 8:
        raise ValueError("La phrase secrete doit contenir au moins 8 caracteres.")
    kdf = Argon2id(
        salt=sel,
        length=params["length"],
        iterations=params["iterations"],
        lanes=params["lanes"],
        memory_cost=params["memory_cost"],
    )
    return kdf.derive(phrase_secrete.encode("utf-8"))


def _ecriture_atomique(chemin: Path, contenu_bytes: bytes) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tmp = chemin.with_suffix(chemin.suffix + f".tmp.{secrets.token_hex(6)}")
    try:
        with open(tmp, "wb") as f:
            f.write(contenu_bytes)
            f.flush()
            os.fsync(f.fileno())
        if os.name == "posix":
            os.chmod(tmp, 0o600)
        os.replace(tmp, chemin)
        if os.name == "posix":
            os.chmod(chemin, 0o600)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def creer_coffre(
    phrase_secrete: str,
    chemin: Path = CHEMIN_COFFRE_DEFAUT,
    presence_humaine: dict[str, str] | None = None,
    ecraser: bool = False,
) -> dict[str, Any]:
    """Genere un secret maitre 256 bits et sauvegarde le coffre chiffre."""
    if chemin.exists() and not ecraser:
        raise FileExistsError(f"Un coffre existe deja : {chemin}")

    donnees = {
        "version_protocole": "2.0",
        "version_cle": 1,
        "secret_maitre_b64": base64.b64encode(secrets.token_bytes(32)).decode("ascii"),
        "presence_humaine": presence_humaine
        or {
            "nom": "",
            "prenom": "",
            "date_naissance": "",
            "email": "",
            "telephone": "",
            "adresse_livraison": "",
        },
        "facteurs_2": {},  # Reserve par domaine : ex. {"grt.sss": {"type": "totp", ...}}
    }
    sauvegarder_coffre(donnees, phrase_secrete, chemin)
    return donnees


def sauvegarder_coffre(
    donnees: dict[str, Any],
    phrase_secrete: str,
    chemin: Path = CHEMIN_COFFRE_DEFAUT,
) -> None:
    """Chiffre et enregistre le coffre sur disque de maniere atomique."""
    sel = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    cle = _deriver_cle_coffre(phrase_secrete, sel, PARAMS_ARGON2_DEFAUT)

    aad = FORMAT_COFFRE.encode("ascii")
    texte_clair = json.dumps(donnees, ensure_ascii=False).encode("utf-8")
    chiffre = AESGCM(cle).encrypt(nonce, texte_clair, aad)

    enveloppe = {
        "format": FORMAT_COFFRE,
        "kdf": "argon2id",
        "kdf_params": PARAMS_ARGON2_DEFAUT,
        "salt_b64": base64.b64encode(sel).decode("ascii"),
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "ciphertext_b64": base64.b64encode(chiffre).decode("ascii"),
    }
    _ecriture_atomique(chemin, json.dumps(enveloppe, indent=2).encode("utf-8"))


def charger_coffre(
    phrase_secrete: str,
    chemin: Path = CHEMIN_COFFRE_DEFAUT,
) -> dict[str, Any]:
    """Dechiffre et retourne le contenu du coffre."""
    if not chemin.exists():
        raise FileNotFoundError(f"Coffre introuvable : {chemin}")

    enveloppe = json.loads(chemin.read_text(encoding="utf-8"))
    if enveloppe.get("format") != FORMAT_COFFRE or enveloppe.get("kdf") != "argon2id":
        raise ValueError("Format de coffre non reconnu.")

    sel = base64.b64decode(enveloppe["salt_b64"])
    nonce = base64.b64decode(enveloppe["nonce_b64"])
    chiffre = base64.b64decode(enveloppe["ciphertext_b64"])
    params = enveloppe["kdf_params"]

    cle = _deriver_cle_coffre(phrase_secrete, sel, params)
    try:
        texte_clair = AESGCM(cle).decrypt(nonce, chiffre, FORMAT_COFFRE.encode("ascii"))
    except InvalidTag as exc:
        raise ValueError("Phrase secrete incorrecte ou fichier coffre altere.") from exc

    return json.loads(texte_clair.decode("utf-8"))


def extraire_secret_maitre(donnees_coffre: dict[str, Any]) -> bytes:
    """Retourne les 32 octets du secret maitre depuis le coffre dechiffre."""
    secret = base64.b64decode(donnees_coffre["secret_maitre_b64"])
    if len(secret) < 32:
        raise ValueError("Secret maitre invalide (32 octets minimum requis).")
    return secret