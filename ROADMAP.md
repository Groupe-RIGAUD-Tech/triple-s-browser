# 🧭 Vision, Technical Challenges & Roadmap — Triple S (`sss://`)

## Why Triple S Exists
The modern web has drifted away from its original purpose: sharing information safely. Today, loading a simple corporate page triggers dozens of third-party JavaScript trackers, heavy frameworks, and automated scraping by autonomous AI agents.

**Triple S** is an engineering project and sovereign B2B network protocol (`sss://`, TCP port 1965) exploring a radical alternative: **stripping the web back to pure static content, strict protocol-level isolation, and native post-quantum cryptographic identity.**

---

## Current Status (v2.0.0 — Public Release)
Triple S is an operational, cross-platform B2B browser and protocol for **Windows (64-bit)** and **Linux (x64)**.

**What works today:**
- PyQt6-based browser engine blocking JavaScript, plugins, and cookies on `sss://` domains.
- Native post-quantum passwordless authentication (`sss-auth://`) using hybrid **Ed25519 + ML-DSA-65 (NIST FIPS 204)** dual signatures, **TOTP 2FA**, and one-time anti-replay nonces.
- Local encrypted vault (`.identite_sss.vault`, **Argon2id + AES-256-GCM**, 12-char min. passphrase) with per-domain key derivation and automatic RAM locking after every action.
- 4 sovereign B2B workflows in the built-in Client Portal Demo: Cryptographic Registration, 2FA Login with granular consent, Zero-Spam Company Contact, and Signed Purchase Validation (`0.00 EUR` simulation).
- Sovereign remote registry (`registre.json`) mapping `.sss` domains to verified corporate legal IDs (SIRET, EU VAT, Swiss UID, D-U-N-S) with permanent B2B Trust Banner and Zero-JS Directory (`sss://annuaire.sss`).
- Hybrid `https_statique` hosting mode with automatic `<base href>` injection and built-in Zero-JS `.sss` domain reservation template.
- Unified bilingual UI (**FR / EN**) with OS locale detection and single-button toolbar switcher (`🌐 FR / EN`).
- Verifiable pre-built binaries for Windows 64-bit and Linux x64 (SHA-256 checksums published).

**Known limitations (honest list):**
- Windows executable is not yet EV code-signed (triggers Windows SmartScreen).
- Software-stored local vault (hardware FIDO2/CTAP2 post-quantum USB key support is planned for v3.0).
- No native video streaming support yet.
- macOS builds and native Linux packages (`.AppImage` / `.deb`) are not packaged yet.

---

## Milestones & Delivery History (v1.0.0 → v3.0.0)

### ✅ v1.0.0 — Core Engine & Static Shield (Shipped)
- [x] **Zero-JS / Zero-Cookie Browser Engine:** Cross-platform PyQt6 desktop client with native script, plugin, and cookie blocking on `sss://`.
- [x] **Local Static Server (`port 1965`):** Built-in `moteur_sss.py` with Path Traversal protection.
- [x] **264-bit Local Cryptographic Identity:** Offline CSPRNG key generation with zero central storage.

### ✅ v1.1.0 — Sovereign B2B Network & Registry (Shipped)
- [x] **Sovereign Remote Registry (`registre.json`):** Maps `.sss` domains to verified corporate legal IDs.
- [x] **Hybrid `https_statique` Hosting:** Zero-port-forwarding static site routing from a company's existing `/sss/` HTTPS folder.
- [x] **Dynamic Zero-JS Directory (`sss://annuaire.sss`):** Live directory generated directly from the registry.
- [x] **Multi-Platform Distribution:** Standalone Windows 64-bit and Linux x64 binaries with SHA-256 verification.

### ✅ v1.2.0 — B2B UX, Trust Layer & Bilingual UI (Shipped)
- [x] **External Images & CSS Support:** Automatic `<base href>` injection in `https_statique` mode.
- [x] **Verified Corporate Identity Badge:** Gold trust banner for verified `.sss` domains, amber for unregistered, grey for standard `https://`.
- [x] **Live Registry Hot-Reload (`🔄`):** Instant `registre.json` synchronization from the toolbar.

### ✅ v2.0.0 — Post-Quantum Identity & Sovereign B2B Auth (Current Release)
- [x] **Hybrid Post-Quantum Authentication (`sss-auth://`):** Passwordless **Ed25519 + ML-DSA-65 (NIST FIPS 204)** dual signatures with TOTP 2FA and anti-replay nonces.
- [x] **Encrypted Local Vault (`.identite_sss.vault`):** Argon2id + AES-256-GCM local encryption, per-domain key derivation, and automatic RAM locking.
- [x] **4 B2B Sovereign Workflows:** Registration, 2FA Login, Zero-Spam Contact, and Signed Purchase Validation (`0.00 EUR` demo).
- [x] **Unified Bilingual Interface (`🌐 FR / EN`):** Single toolbar toggle translating the browser, local pages, client portal, and native consent dialogs.

### 🚧 v2.1.0 — Signed Registry & Dedicated Nodes (Next Release)
- [ ] **ML-DSA-65 Signed Registry:** Cryptographic verification of `registre.json` using Groupe RIGAUD Tech's post-quantum public key to prevent tampering.
- [ ] **Production `noeud_sss` Deployments:** Reference server kit for companies hosting their own port-1965 sovereign portals.
- [ ] **Native Packaging:** `.AppImage` / `.deb` packages for Linux and EV code-signing for Windows.

### 🛡️ v3.0.0 — Post-Quantum Hardware & Decentralized Anchoring
- [ ] **Post-Quantum FIDO2 / CTAP2 USB Key Integration:** Hardware-backed **ML-DSA-65** signatures and **ML-KEM-768** key encapsulation on open-source USB microcontrollers.
- [ ] **Decentralized Static Node Replication & Anchoring:** Replicate signed static HTML/CSS files across decentralized nodes and anchor `.sss` registry state cryptographically.

---

## Core Engineering Challenges (Where We Need Help)
Contributions, security audits, and architectural critiques are welcome on the following topics:

1. **Safe Media & Video Without JavaScript:** Explore native HTML5 `<video>` support using strictly sandboxed, static media formats without reintroducing tracking or script execution vectors.
2. **Post-Quantum Hardware Convergence (v3.0):** Offload **ML-DSA-65** signing and **ML-KEM-768** encapsulation to dedicated hardware USB keys.
3. **Decentralized Static Replication:** Design a lightweight, signed static-file replication layer where nodes only cache verified HTML/CSS—eliminating malware execution risks.
4. **Cross-Platform Packaging:** Clean native packages for Linux (`.AppImage` / `.deb`) and macOS, plus reproducible CI builds.

---

## Security Audits & Feedback
- **Open an Issue:** Found a security flaw, a bug, or a weakness in our threat model? Report it directly in the *Issues* tab.
- **License:** Source-Available (see [`LICENSE`](LICENSE)) — open for transparency and security auditing; commercial use or redistribution requires written permission.

*Project initiated by Cyril Rigaud from Groupe RIGAUD Tech SASU (Sophia Antipolis, France).*
