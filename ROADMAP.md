# 🧭 Vision, Technical Challenges & Roadmap — Triple S (`sss://`)

## Why Triple S Exists
The modern web has drifted away from its original purpose: sharing information safely. Today, loading a simple corporate page triggers dozens of third-party JavaScript trackers, heavy frameworks, and automated scraping by autonomous AI agents.

**Triple S** is an engineering experiment and B2B-focused POC exploring a radical alternative: **what if we strip the web back to pure static content, strict protocol-level isolation, and local cryptographic identity?**

---

## Current Status (v1.2.0 — Pre-release)
Triple S is an operational, multi-platform B2B network POC for **Windows (64-bit)** and **Linux (x64)**. We publish early to gather honest technical feedback and build a community of security-minded developers.

**What works today:**
- PyQt6-based browser engine blocking JavaScript, plugins, and cookies on `sss://` domains.
- Local static server (`moteur_sss.py`, port 1965) with Path Traversal protection.
- Local 52-character CSPRNG key generation ($34^{52} \approx 4.33 \times 10^{79}$ combinations; 264-bit entropy, >128-bit effective security against Grover's algorithm) with zero central database.
- Sovereign remote registry (`registre.json`) mapping `.sss` domains to verified corporate legal IDs (SIRET, EU VAT, Swiss UID, D-U-N-S).
- Hybrid `https_statique` hosting mode with automatic `<base href>` injection: companies serve their static `.sss` site (including relative images and CSS) from a `/sss/` subfolder on their existing HTTPS host (24/7 availability, zero open ports) while keeping internal navigation inside `sss://`.
- Permanent B2B Trust Banner below the address bar (Gold for verified `.sss` domains with Legal ID, Amber for unregistered domains, Grey for standard `https://` web).
- Live registry hot-reload (`🔄`) and on-the-fly Zero-JS official directory (`sss://annuaire.sss`).
- Full bilingual UI (**FR / EN**) with OS locale detection and instant toolbar switcher (`🌐 FR / EN`).
- Verifiable pre-built binaries for Windows 64-bit and Linux x64 (SHA-256 checksums published).

**Known limitations (honest list):**
- Windows executable is not yet EV code-signed (triggers Windows SmartScreen).
- Symmetric local key only (challenge-response auth and asymmetric post-quantum signing are planned for V2/V3).
- No native video streaming support yet.
- macOS builds and native Linux packages (`.AppImage` / `.deb`) are not packaged yet.

---

## Milestones & Delivery History (v1.0.0 → v3.0.0)

### ✅ v1.0.0 — Core Engine & Static Shield (Shipped)
- [x] **Zero-JS / Zero-Cookie Browser Engine:** Cross-platform PyQt6 desktop client with native script, plugin, and cookie blocking on `sss://`.
- [x] **Local Static Server (`port 1965`):** Built-in `moteur_sss.py` with Path Traversal protection.
- [x] **264-bit Local Cryptographic Identity:** Automatic offline CSPRNG key generation (`.identite_sss.json`) with zero central storage.

### ✅ v1.1.0 — Sovereign B2B Network & Registry (Shipped)
- [x] **Sovereign Remote Registry (`registre.json`):** Maps `.sss` domains to verified corporate legal IDs (SIRET, EU VAT, Swiss UID, D-U-N-S).
- [x] **Hybrid `https_statique` Hosting:** Zero-port-forwarding static site routing from a company's existing `/sss/` HTTPS folder.
- [x] **Dynamic Zero-JS Directory (`sss://annuaire.sss`):** Live directory generated directly from the registry.
- [x] **Multi-Platform Distribution:** Standalone Windows 64-bit installer and Linux x64 binary with SHA-256 verification.

### ✅ v1.2.0 — B2B UX, Trust Layer & Bilingual UI (Current Release)
- [x] **External Images & CSS Support:** Automatic `<base href>` injection in `https_statique` mode with relative link interception to keep users inside `sss://`.
- [x] **Verified Corporate Identity Badge:** Dedicated gold trust banner (`Verified Domain • Legal ID: ...`), amber warning for unregistered `.sss` domains, and grey indicator on standard `https://` sites.
- [x] **Live Registry Hot-Reload (`🔄`):** Instant `registre.json` synchronization from the toolbar without restarting the browser.
- [x] **Full Bilingual Interface (`🌐 FR / EN`):** OS locale auto-detection and one-click language switching across the UI, banner, directory, and alerts.

### 🚧 v2.0.0 — Sovereign Authentication & Decentralized Nodes (Next Release)
- [ ] **Passwordless 264-bit Challenge-Response Authentication:**
  Allow `.sss` portals to authenticate visitors locally using `.identite_sss.json` without passwords or centralized credential databases.
- [ ] **P2P / Static Node Replication:**
  Replicate signed static HTML/CSS files across decentralized nodes so self-hosted business sites stay online even if a local machine powers down.

### 🛡️ v3.0.0 — Post-Quantum Hardware Convergence
- [ ] **Native Post-Quantum FIDO2 / CTAP2 USB Key Integration:**
  Replace the software-stored local key with hybrid hardware-backed authentication (ECDSA P-256 + NIST FIPS 204 **ML-DSA-65** signatures and NIST FIPS 203 **ML-KEM-768**).

---

## Core Engineering Challenges (Where We Need Help)
Rethinking a zero-script web means solving hard technical problems from scratch. Contributions, RFCs, and architectural critiques are welcome on the following topics:

1. **Safe Media & Video Without JavaScript:**
   - *The challenge:* Modern video platforms rely heavily on JS players and `<iframe>` embeds, which break our security model.
   - *Goal:* Explore native HTML5 `<video>` support using strictly sandboxed, static media formats (e.g., direct `.webm`/`.mp4` streams) without reintroducing tracking or script execution vectors.
2. **Post-Quantum Asymmetric Authentication (V2/V3):**
   - *The challenge:* Transitioning from a 264-bit local identifier to full cryptographic request signing to block unauthorized AI scrapers.
   - *Goal:* Integrate NIST-standardized **ML-DSA-65** (signatures) and **ML-KEM-768** (key encapsulation) via `liboqs` or hardware CTAP2 without bloating the client binary.
3. **Hybrid & P2P Hosting Architecture:**
   - *The challenge:* Allowing businesses to self-host their static `.sss` site on a local PC without losing availability when the machine goes offline.
   - *Goal:* Design a lightweight, signed static-file replication layer (P2P / static nodes) where nodes only cache verified HTML/CSS—eliminating malware execution risks.
4. **Cross-Platform Packaging:**
   - *Goal:* Move beyond standalone binaries to clean native packages for Linux (`.AppImage` / `.deb`) and macOS, plus automated CI builds.

---

## How to Contribute
- **Open an Issue:** Found a security flaw, a bug, or a flaw in our threat model? Report it directly in the *Issues* tab.
- **Discuss Architecture:** Propose improvements to the `sss://` protocol specification.
- **Pull Requests:** Clean, minimal Python/PyQt6 contributions are welcome (please open an Issue first to discuss major changes).

*Project initiated by Groupe RIGAUD Tech SASU (Sophia Antipolis, France).*
