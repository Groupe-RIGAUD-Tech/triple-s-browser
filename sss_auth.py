"""Triple S - Authentification hybride Ed25519 + ML-DSA-65 et TOTP (RFC 6238).

Prototype multi-OS (Windows, Linux, macOS) — a soumettre a un audit cryptographique
avant tout deploiement en production ou usage financier.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.mldsa import (
    MLDSA65PrivateKey,
    MLDSA65PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

PROTO = b"sss-auth-v1"
TAILLE_NONCE = 32


def normaliser_origine(origin: str) -> str:
    """Normalise le domaine fourni par le navigateur (jamais par la page)."""
    propre = origin.strip().lower().rstrip("/")
    if not propre or not propre.isascii():
        raise ValueError("Origine invalide ou non ASCII.")
    return propre


def _lp(*parts: bytes) -> bytes:
    """Encodage sans ambiguite : chaque champ est precede de sa taille sur 4 octets."""
    return b"".join(len(p).to_bytes(4, "big") + p for p in parts)


def _deriver_graine(master: bytes, algo: bytes, origin: str, version: int) -> bytes:
    if len(master) < 32:
        raise ValueError("Secret maitre : 32 octets minimum.")
    if version < 1:
        raise ValueError("Numero de version invalide.")
    origine_norm = normaliser_origine(origin)
    info = _lp(PROTO, algo, origine_norm.encode("ascii"), version.to_bytes(4, "big"))
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"sss-kdf-v1",
        info=info,
    ).derive(master)


def cles_site(master: bytes, origin: str, version: int = 1) -> tuple[Ed25519PrivateKey, MLDSA65PrivateKey]:
    """Derive la paire de cles privees (Ed25519 + ML-DSA-65) unique pour ce domaine."""
    return (
        Ed25519PrivateKey.from_private_bytes(_deriver_graine(master, b"ed25519", origin, version)),
        MLDSA65PrivateKey.from_seed_bytes(_deriver_graine(master, b"mldsa65", origin, version)),
    )


def cles_publiques_site(master: bytes, origin: str, version: int = 1) -> tuple[bytes, bytes]:
    """Retourne les deux cles publiques brutes (Ed25519 32 o, ML-DSA-65 1952 o) a enregistrer cote serveur."""
    ed, ml = cles_site(master, origin, version)
    return ed.public_key().public_bytes_raw(), ml.public_key().public_bytes_raw()


def generer_defi(duree_secondes: int = 60) -> tuple[bytes, int]:
    """Cote serveur : genere un nonce aleatoire de 32 octets et son horodatage d'expiration."""
    return secrets.token_bytes(TAILLE_NONCE), int(time.time()) + duree_secondes


def construire_message(
    origin: str,
    action: str,
    nonce: bytes,
    expires: int,
    payload: bytes = b"",
) -> bytes:
    """Construit le message canonique liant origine, action, nonce, expiration et donnees validees."""
    if len(nonce) != TAILLE_NONCE:
        raise ValueError(f"Le nonce doit faire exactement {TAILLE_NONCE} octets.")
    origine_norm = normaliser_origine(origin)
    digest = hashes.Hash(hashes.SHA256())
    digest.update(payload)
    return _lp(
        PROTO,
        origine_norm.encode("ascii"),
        action.strip().encode("ascii"),
        nonce,
        int(expires).to_bytes(8, "big"),
        digest.finalize(),
    )


def signer_defi(
    master: bytes,
    origin: str,
    msg: bytes,
    version: int = 1,
) -> tuple[bytes, bytes]:
    """Signe le message avec Ed25519 et ML-DSA-65."""
    ed, ml = cles_site(master, origin, version)
    return ed.sign(msg), ml.sign(msg, PROTO)


def verifier_signature(
    pubs: tuple[bytes, bytes],
    sigs: tuple[bytes, bytes],
    msg: bytes,
    expires: int | None = None,
    maintenant: int | None = None,
) -> bool:
    """Verifie l'expiration et exige la validite des DEUX signatures."""
    if expires is not None:
        horloge = int(time.time()) if maintenant is None else maintenant
        if horloge > expires:
            return False
    try:
        Ed25519PublicKey.from_public_bytes(pubs[0]).verify(sigs[0], msg)
        MLDSA65PublicKey.from_public_bytes(pubs[1]).verify(sigs[1], msg, PROTO)
        return True
    except (InvalidSignature, ValueError):
        return False


# ==================== FACTEUR 2 : TOTP HORS-LIGNE (RFC 6238) ====================


def generer_secret_totp() -> str:
    """Genere un secret TOTP Base32 de 160 bits (compatible Aegis, FreeOTP, Bitwarden)."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def uri_totp(secret_b32: str, compte: str, emetteur: str = "Triple S") -> str:
    """Construit l'URI otpauth:// pour import dans une application d'authentification."""
    label = quote(f"{emetteur}:{compte}")
    return f"otpauth://totp/{label}?secret={secret_b32}&issuer={quote(emetteur)}&digits=6&period=30"


def _decoder_b32(secret_b32: str) -> bytes:
    propre = secret_b32.strip().replace(" ", "").upper()
    remplissage = "=" * ((8 - len(propre) % 8) % 8)
    return base64.b32decode(propre + remplissage, casefold=True)


def calculer_code_totp(secret_b32: str, timestamp: int | None = None, periode: int = 30) -> str:
    """Calcule le code TOTP a 6 chiffres (RFC 6238, HMAC-SHA1)."""
    t = int(time.time()) if timestamp is None else int(timestamp)
    compteur = struct.pack(">Q", t // periode)
    cle = _decoder_b32(secret_b32)
    h = hmac.new(cle, compteur, hashlib.sha1).digest()
    decalage = h[-1] & 0x0F
    code_int = struct.unpack(">I", h[decalage : decalage + 4])[0] & 0x7FFFFFFF
    return f"{code_int % 1_000_000:06d}"


def verifier_code_totp(
    secret_b32: str,
    code_saisi: str,
    fenetre: int = 1,
    timestamp: int | None = None,
    periode: int = 30,
) -> bool:
    """Verifie un code TOTP a temps constant avec tolerance de +/- 30 s par defaut."""
    code_propre = code_saisi.strip().replace(" ", "")
    if len(code_propre) != 6 or not code_propre.isdigit():
        return False
    t = int(time.time()) if timestamp is None else int(timestamp)
    for decalage in range(-fenetre, fenetre + 1):
        attendu = calculer_code_totp(secret_b32, timestamp=t + decalage * periode, periode=periode)
        if hmac.compare_digest(code_propre, attendu):
            return True
    return False


# ==================== AUTO-TEST MULTI-OS ====================

if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    from sss_coffre import charger_coffre, creer_coffre, extraire_secret_maitre

    with tempfile.TemporaryDirectory() as dossier_tmp:
        chemin_test = Path(dossier_tmp) / ".identite_sss.vault"
        creer_coffre("MaPhraseSecrete2026!", chemin=chemin_test)

        # 1. Mauvaise phrase secrete refusee
        try:
            charger_coffre("MauvaisePhrase", chemin=chemin_test)
            raise AssertionError("Le coffre aurait du refuser la mauvaise phrase.")
        except ValueError:
            pass

        # 2. Ouverture et derivation par domaine
        coffre = charger_coffre("MaPhraseSecrete2026!", chemin=chemin_test)
        master = extraire_secret_maitre(coffre)

        pubs_grt = cles_publiques_site(master, "sss://grt.sss")
        pubs_autre = cles_publiques_site(master, "sss://client.sss")
        assert pubs_grt[0] != pubs_autre[0] and pubs_grt[1] != pubs_autre[1]

        # 3. Signature et verification hybride Ed25519 + ML-DSA-65
        nonce, exp = generer_defi(60)
        payload = b'{"adresse_livraison":"230 route des Dolines, Sophia Antipolis"}'
        msg = construire_message("sss://grt.sss", "valider_livraison", nonce, exp, payload)
        sigs = signer_defi(master, "sss://grt.sss", msg)

        assert verifier_signature(pubs_grt, sigs, msg, expires=exp) is True
        assert verifier_signature(pubs_autre, sigs, msg, expires=exp) is False
        assert verifier_signature(pubs_grt, sigs, msg, expires=exp, maintenant=exp + 5) is False

        # 4. Verification TOTP (Facteur 2)
        secret_2fa = generer_secret_totp()
        code_valide = calculer_code_totp(secret_2fa)
        assert verifier_code_totp(secret_2fa, code_valide) is True
        assert verifier_code_totp(secret_2fa, "000000") is False

        print(f"OK - Coffre Argon2id/AES-GCM + Ed25519 ({len(sigs[0])} o) + ML-DSA-65 ({len(sigs[1])} o) + TOTP valides.")