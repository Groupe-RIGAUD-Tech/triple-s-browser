# 🛡️ Triple S Browser (`sss://`) — Sovereign Static Web & Post-Quantum Identity

[![Version](https://img.shields.io/badge/Version-2.0.0-D4AF37?style=for-the-badge)](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20(64--bit)-202124?style=for-the-badge)](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)
[![Security](https://img.shields.io/badge/Security-Zero--JS%20%7C%20Ed25519%20%2B%20ML--DSA--65-D4AF37?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-Source--Available-1e293b?style=for-the-badge)](LICENSE)

[🇫🇷 Version Française](#-version-française) | [🇬🇧 English Version](#-english-version)

---

## 🇫🇷 Version Française

### Qu'est-ce que le Navigateur Triple S ?
**Triple S** est un navigateur souverain et un protocole réseau natif (`sss://`, port TCP 1965) conçu pour les infrastructures critiques, les entreprises et l'ère post-quantique.

Contrairement aux navigateurs classiques qui exécutent des milliers de lignes de code dynamique à chaque visite, Triple S applique une règle architecturale stricte : **zéro JavaScript, zéro plugin, zéro cookie et zéro exécutable sur les domaines `sss://`**.

### Nouveautés & Caractéristiques Clés (V2.0.0)
- **Authentification Post-Quantique Native (`sss-auth://`) :** Connexion sans mot de passe par double signature cryptographique **Ed25519 + ML-DSA-65 (standard NIST FIPS 204)**, couplée à un second facteur **2FA TOTP** et un nonce anti-rejeu.
- **Coffre Chiffré Local (`.identite_sss.vault`) :** Clé maître 256 bits et coordonnées chiffrées localement (**Argon2id + AES-256-GCM**), dérivation de clés unique par domaine et verrouillage automatique en RAM après chaque action.
- **4 Parcours B2B Souverains (Espace Client Démo) :** Inscription cryptographique, Connexion double facteur avec consentement granulaire, Contact entreprise zéro-spam et Validation d'achat signée (simulation `0.00 EUR`).
- **Bouclier Statique & Registre Souverain (`sss://annuaire.sss`) :** Résolution native des domaines `.sss` vérifiés par identifiant légal (SIRET, TVA UE, UID, D-U-N-S) et interface 100 % bilingue **FR / EN**.
- **Architecture *Zero-Knowledge* :** Zéro base de données centrale. Aucune clé privée ni donnée personnelle n'est collectée par l'éditeur.

### Feuille de Route (Roadmap)
- **v2.0 (Actuelle) :** Navigateur bilingue FR/EN, coffre chiffré local, double signature Ed25519 + ML-DSA-65, 2FA TOTP et 4 parcours B2B.
- **v2.1 :** Signature cryptographique ML-DSA-65 du registre officiel `.sss` et déploiement de nœuds `noeud_sss` dédiés.
- **v3.0 :** Décentralisation, réplication de nœuds statiques et ancrage cryptographique du registre `.sss`.

### Téléchargement & Installation
Téléchargez les binaires vérifiés (Windows 64-bit et Linux x64, avec empreintes SHA-256) :  
👉 **[Télécharger via l'onglet Releases](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)** *(ou sur [grouperigaudtech.fr](https://www.grouperigaudtech.fr/telechargement.html))*.

### Offre de Lancement Entreprises
Les **1 000 premiers noms de domaine `.sss` sont attribués gratuitement la première année** (1 domaine par entreprise vérifiée).  
📩 Contact & pré-réservation : `contact@grouperigaudtech.fr`

### Licence & Propriété Intellectuelle
Ce projet est distribué sous licence **Source-Available** (voir le fichier [`LICENSE`](LICENSE)) et protégé par un **dépôt e-Soleau auprès de l'INPI**. Le code est ouvert à l'audit de sécurité ; toute copie ou exploitation commerciale sans autorisation écrite est interdite.

---

## 🇬🇧 English Version

### What is Triple S Browser?
**Triple S** is a sovereign browser and native network protocol (`sss://`, TCP port 1965) built for critical infrastructures, businesses, and the post-quantum era.

Unlike conventional browsers that execute complex dynamic code on every page load, Triple S enforces a strict architectural rule: **zero JavaScript, zero plugins, zero cookies, and zero executables on `sss://` domains**.

### Core Features (V2.0.0)
- **Native Post-Quantum Authentication (`sss-auth://`):** Passwordless authentication powered by hybrid **Ed25519 + ML-DSA-65 (NIST FIPS 204)** dual signatures, **TOTP 2FA**, and one-time anti-replay nonces.
- **Local Encrypted Vault (`.identite_sss.vault`):** 256-bit master key and user profile encrypted locally (**Argon2id + AES-256-GCM**), per-domain key derivation, and automatic RAM locking after every action.
- **4 Sovereign B2B Workflows (Client Portal Demo):** Cryptographic registration, 2FA login with granular consent, zero-spam company contact, and signed purchase validation (`0.00 EUR` simulation).
- **Static Shield & Sovereign Registry (`sss://annuaire.sss`):** Native resolution of `.sss` domains verified by legal corporate ID (SIRET, EU VAT, UID, D-U-N-S) with a unified **FR / EN** interface.
- **Zero-Knowledge Architecture:** Zero central database. Groupe RIGAUD Tech never collects or stores private keys or personal data.

### Roadmap
- **v2.0 (Current):** Bilingual FR/EN browser, local encrypted vault, Ed25519 + ML-DSA-65 dual signatures, TOTP 2FA, and 4 B2B flows.
- **v2.1:** ML-DSA-65 cryptographic signing of the official `.sss` registry and dedicated `noeud_sss` server deployments.
- **v3.0:** Decentralization, static node replication, and cryptographic anchoring of the `.sss` registry.

### Download & Installation
Download the verifiable binaries (Windows 64-bit & Linux x64, with SHA-256 checksums):  
👉 **[Download from Releases](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)** *(or via [grouperigaudtech.fr](https://www.grouperigaudtech.fr/telechargement.html))*.

### Early-Adopter Business Offer
The **first 1,000 `.sss` domain names are granted free of charge for the first year** (limit 1 domain per verified company).  
📩 Registration & inquiries: `contact@grouperigaudtech.fr`

### License & Intellectual Property
This project is distributed under a **Source-Available** license (see [`LICENSE`](LICENSE)) and protected by an **INPI e-Soleau filing**. Source code is open for security auditing; commercial use or redistribution without prior written permission is prohibited.

---

**Édité par / Published by:** Groupe RIGAUD Tech SASU — Sophia Antipolis, France
