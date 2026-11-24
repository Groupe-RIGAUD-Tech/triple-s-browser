# 🧭 Vision, Technical Challenges & Roadmap — Triple S (`sss://`)

## Why Triple S Exists
The modern web has drifted away from its original purpose: sharing information safely. Today, loading a simple corporate page triggers dozens of third-party JavaScript trackers, heavy frameworks, and automated scraping by autonomous AI agents.

**Triple S** is an engineering experiment and B2B-focused POC exploring a radical alternative: **what if we strip the web back to pure static content, strict protocol-level isolation, and local cryptographic identity?**

---

## Current Status (v1.1.0 — Pre-release)
This release transitions Triple S from a local prototype (`127.0.0.1`) into an operational B2B network POC for **Windows (64-bit)** and **Linux (x64)**. We publish early to gather honest technical feedback and build a community of security-minded developers.

**What works today:**
- PyQt6-based browser engine blocking JavaScript, plugins, and cookies on `sss://` domains.
- Local static server (`moteur_sss.py`, port 1965) with Path Traversal protection.
- Local 52-character CSPRNG key generation ($34^{52} \approx 4.33 \times 10^{79}$ combinations; 264-bit entropy, >128-bit effective security against Grover's algorithm) with zero central database.
- Sovereign remote registry (`registre.json`) mapping `.sss` domains to verified corporate legal IDs (SIRET, EU VAT, Swiss UID, D-U-N-S).
- Hybrid `https_statique` hosting mode: companies can serve their static `.sss` site from a `/sss/` subfolder on their existing HTTPS host (24/7 availability, zero open ports).
- On-the-fly Zero-JS official directory (`sss://annuaire.sss`) synced from the registry.
- Verifiable pre-built binaries for Windows 64-bit and Linux x64 (SHA-256 checksums published).

**Known limitations (honest list):**
- Windows executable is not yet EV code-signed (triggers Windows SmartScreen).
- Relative external assets (images, external CSS stylesheets) in `https_statique` mode require `<base href>` injection (planned for v1.2.0).
- Symmetric local key only (challenge-response auth and asymmetric post-quantum signing are planned for V2/V3).
- No native video streaming support yet.
- macOS builds and native Linux packages (`.AppImage` / `.deb`) are not packaged yet.

---

## Upcoming Milestones (v1.2.0 → v3.0.0)

### 🚧 v1.2.0 — B2B UX & Trust Layer (Next Release)
1. **External Images & CSS Support (Priority #1):**
   Automatically inject `<base href="https://client-domain.tld/sss/">` before rendering HTML in `https_statique` mode so relative assets (`logo.png`, `style.css`) load natively.
2. **Verified Corporate Identity Badge:**
   Display a dedicated gold trust indicator in the browser UI showing `Verified Domain • Legal ID: ...` for registered `.sss` domains, alongside a neutral grey status bar when browsing standard `https://` sites.
3. **Live Registry Hot-Reload (`🔄`):**
   Add a refresh button next to the address bar to re-sync `registre.json` on the fly without restarting the browser.

### 🔮 v2.0.0 — Sovereign Authentication & Decentralized Nodes
4. **Passwordless 264-bit Challenge-Response Authentication:**
   Allow `.sss` portals to authenticate visitors locally using `.identite_sss.json` without passwords or centralized credential databases.
5. **P2P / Static Node Replication:**
   Replicate signed static HTML/CSS files across decentralized nodes so self-hosted business sites stay online even if a local machine powers down.

### 🛡️ v3.0.0 — Post-Quantum Hardware Convergence
6. **Native Post-Quantum FIDO2 / CTAP2 USB Key Integration:**
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
