# 🛡️ Triple S Browser (`sss://`) — Sovereign Static Web & Post-Quantum Identity

[![Version](https://img.shields.io/badge/Version-2.1.0-D4AF37?style=for-the-badge)](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20(64--bit)-202124?style=for-the-badge)](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)
[![Security](https://img.shields.io/badge/Security-Zero--JS%20%7C%20Ed25519%20%2B%20ML--DSA--65-D4AF37?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-Source--Available-1e293b?style=for-the-badge)](LICENSE)

[🇫🇷 Version Française](#-version-française) | [🇬🇧 English Version](#-english-version)

---

## 🇫🇷 Version Française

### Qu'est-ce que le Navigateur Triple S ?
**Triple S** est un navigateur souverain et un protocole réseau natif (`sss://`, port TCP 1965) conçu pour les infrastructures critiques, les entreprises et l'ère post-quantique.

Contrairement aux navigateurs classiques qui exécutent des milliers de lignes de code dynamique à chaque visite, Triple S applique une règle architecturale stricte : **zéro JavaScript, zéro plugin, zéro cookie et zéro exécutable sur les domaines `sss://`**.

### Nouveautés & Caractéristiques Clés (V2.1.0)
- **Authentification Post-Quantique Native (`sss-auth://`) :** Connexion sans mot de passe par double signature cryptographique **Ed25519 + ML-DSA-65 (standard NIST FIPS 204)**, **2FA TOTP avec enrôlement par QR Code hors-ligne (`segno`)** et nonce anti-rejeu.
- **Registre Souverain Signé (`registre.json.sig`) :** Vérification cryptographique **ML-DSA-65** du registre officiel `.sss` pour empêcher toute altération, avec résolution par identifiant légal (SIRET, TVA UE, UID, D-U-N-S) et annuaire statique `sss://annuaire.sss`.
- **Coffre Chiffré Local (`.identite_sss.vault`) :** Clé maître 256 bits et coordonnées chiffrées localement (**Argon2id + AES-256-GCM**), dérivation de clés unique par domaine et verrouillage automatique en RAM après chaque action.
- **4 Parcours B2B Souverains (Espace Client Démo) :** Inscription cryptographique, Connexion double facteur avec consentement granulaire, Contact entreprise zéro-spam et Validation d'achat signée (simulation `0.00 EUR`).
- **Transparence & Intégrité :** Installeur Windows dédié (Inno Setup), binaire Linux x64, empreintes **SHA-256** et **SBOM CycloneDX (`sbom-v2.1.0.json`)** publiés à chaque version.
- **Architecture *Zero-Knowledge* :** Zéro base de données centrale. Aucune clé privée ni donnée personnelle n'est collectée par l'éditeur.

### Feuille de Route (Roadmap)
- **v2.1 (Actuelle) :** Registre signé ML-DSA-65, QR Code 2FA hors-ligne, installeur Windows dédié et publication du SBOM CycloneDX.
- **v2.2 :** Mise à jour intégrée avec vérification SHA-256, kit B2B clé en main (`noeud_sss` + convertisseur HTML-to-SSS) et paquets natifs (`.AppImage` / `.deb`).
- **v3.0 :** Clé matérielle USB FIDO2/CTAP2 post-quantique, réplication décentralisée de nœuds statiques et ancrage cryptographique du registre `.sss`.

### Téléchargement & Installation
Téléchargez les binaires vérifiés (installeur Windows 64-bit `installer_triple_s.exe` et binaire Linux x64 `TripleS-Browser-v2.1.0-linux-x64`, avec empreintes SHA-256 et SBOM) :  
👉 **[Télécharger via l'onglet Releases](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)** *(ou sur [grouperigaudtech.fr](https://www.grouperigaudtech.fr/telechargement.html))*.

*Note Linux (Ubuntu / Wayland) :*
```bash
chmod +x TripleS-Browser-v2.1.0-linux-x64
QT_QPA_PLATFORM=xcb ./TripleS-Browser-v2.1.0-linux-x64
