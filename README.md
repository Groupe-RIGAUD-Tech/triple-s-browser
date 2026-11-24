# 🛡️ Triple S Browser (`sss://`) — Sovereign Static Web & Post-Quantum Identity

[![Version](https://img.shields.io/badge/Version-1.1.0-D4AF37?style=for-the-badge)](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20(64--bit)-202124?style=for-the-badge)](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)
[![Security](https://img.shields.io/badge/Architecture-Zero--JS%20%7C%20264--bit%20Entropy-D4AF37?style=for-the-badge)](#)

[🇫🇷 Version Française](#-version-française) | [🇬🇧 English Version](#-english-version)

---

## 🇫🇷 Version Française

### Qu'est-ce que le Navigateur Triple S ?
**Triple S** est un navigateur souverain et un protocole réseau (`sss://`, port 1965) conçu pour réduire drastiquement la surface d'attaque sur le web B2B et protéger les données des entreprises contre l'exploitation automatisée.

Contrairement aux navigateurs classiques qui exécutent des milliers de lignes de code dynamique à chaque visite, Triple S applique une règle architecturale stricte : **aucun script (JavaScript), aucun plugin, aucun cookie et aucun fichier exécutable n'est transmis ni exécuté sur les domaines `sss://`**.

### Caractéristiques Clés (V1.1)
- **Bouclier Statique Natif :** Bloque à la racine les vecteurs d'attaque XSS, le pistage publicitaire et le scraping automatisé par des agents IA autonomes.
- **Registre Souverain & Annuaire Dynamique (`sss://annuaire.sss`) :** Résolution native des domaines `.sss` vérifiés par identifiant légal d'entreprise (SIRET, TVA UE, UID, D-U-N-S) et génération à la volée de l'annuaire sans une seule ligne de JavaScript.
- **Identité Cryptographique Locale Post-Quantique (264 bits) :** Au premier lancement, le navigateur génère localement dans le profil utilisateur (`.identite_sss.json`) une clé aléatoire de **52 caractères** (alphabet sans ambiguïté de 34 signes excluant `0` et `O`), offrant $34^{52} \approx 4,33 \times 10^{79}$ combinaisons (soit 264 bits d'entropie CSPRNG, conservant > 128 bits de sécurité face à l'algorithme quantique de Grover).
- **Architecture *Zero-Knowledge* (Zéro Base de Données Centrale) :** Aucune clé ni donnée personnelle n'est collectée ou stockée par l'éditeur. L'utilisateur conserve le contrôle matériel exclusif de son identité.
- **Modèle d'Hébergement Hybride (3 Modes) :**
  1. *Routage statique HTTPS (`https_statique`) :* Liaison d'un domaine `sss://` vers un sous-dossier `/sss/` de l'hébergement existant de l'entreprise (disponibilité 24h/24, zéro port à ouvrir).
  2. *Auto-hébergement local (`noeud_sss`) :* Le PC ou serveur de l'entreprise diffuse directement ses pages statiques sur le port 1965 (zéro abonnement cloud).
  3. *Réplication Pair-à-Pair / Nœuds statiques (Feuille de route V2) :* Distribution décentralisée de pages HTML signées entre pairs sans risque d'exécution virale.

### Téléchargement & Installation
Téléchargez les binaires vérifiés (Windows 64-bit et Linux x64, avec empreintes SHA-256) :  
👉 **[Télécharger via l'onglet Releases](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)** *(ou sur [grouperigaudtech.fr](https://www.grouperigaudtech.fr/telechargement.html))*.

### Offre de Lancement Entreprises
Les **1 000 premiers noms de domaine `.sss` sont attribués gratuitement la première année** (1 domaine par entreprise vérifiée) afin de bâtir l'écosystème du web statique souverain.  
📩 Contact & enregistrement : `contact@grouperigaudtech.fr`

---

## 🇬🇧 English Version

### What is Triple S Browser?
**Triple S** is a sovereign web browser and network protocol (`sss://`, port 1965) engineered to drastically shrink the B2B attack surface and shield corporate assets from automated exploitation.

Unlike conventional browsers that execute complex dynamic code on every page load, Triple S enforces a strict architectural rule: **zero JavaScript, zero plugins, zero cookies, and zero executables are transmitted or executed on `sss://` domains**.

### Core Features (V1.1)
- **Native Static Shield:** Blocks XSS attack vectors, ad trackers, and automated scraping by autonomous AI agents at the protocol level.
- **Sovereign Registry & Zero-JS Directory (`sss://annuaire.sss`):** Native resolution of `.sss` domains verified by legal corporate ID (SIRET, EU VAT, UID, D-U-N-S) with an on-the-fly directory generated without JavaScript.
- **Local Post-Quantum Cryptographic Identity (264-bit):** On first launch, the client generates a **52-character** local cryptographic key (`.identite_sss.json`) using an unambiguous 34-character alphabet (excluding `0` and `O`), yielding $34^{52} \approx 4.33 \times 10^{79}$ combinations (264 bits of CSPRNG entropy, maintaining > 128-bit effective security against Grover's quantum algorithm).
- **Zero-Knowledge Architecture:** Zero central database. Groupe RIGAUD Tech never collects or stores user keys or personal data.
- **Hybrid Hosting Architecture (3 Modes):**
  1. *Static HTTPS Routing (`https_statique`):* Maps an official `sss://` domain to an existing `/sss/` static directory on the company's current web host (24/7 availability, zero open ports).
  2. *Local On-Premise Self-Hosting (`noeud_sss`):* The company's own PC or local server serves static HTML pages directly on port 1965 (zero recurring cloud fees).
  3. *Peer-to-Peer / Static Node Replication (V2 Roadmap):* Decentralized distribution of signed static HTML pages across network nodes without malware execution risks.

### Download & Installation
Download the verifiable binaries (Windows 64-bit & Linux x64, with SHA-256 checksums):  
👉 **[Download from Releases](https://github.com/Groupe-RIGAUD-Tech/triple-s-browser/releases)** *(or via [grouperigaudtech.fr](https://www.grouperigaudtech.fr/telechargement.html))*.

### Early-Adopter Business Offer
The **first 1,000 `.sss` domain names are granted free of charge for the first year** (limit 1 domain per verified company).  
📩 Registration & inquiries: `contact@grouperigaudtech.fr`

---

**Édité par / Published by:** Groupe RIGAUD Tech SASU — Sophia Antipolis, France
