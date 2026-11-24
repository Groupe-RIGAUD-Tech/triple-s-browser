# 🧭 Vision, Technical Challenges & Roadmap — Triple S (`sss://`)

## Why Triple S Exists
The modern web has drifted away from its original purpose: sharing information safely. Today, loading a simple corporate page triggers dozens of third-party JavaScript trackers, heavy frameworks, and automated scraping by autonomous AI agents. 

**Triple S** is an engineering experiment and B2B-focused MVP exploring a radical alternative: **what if we strip the web back to pure static content, strict protocol-level isolation, and local cryptographic identity?**

---

## Current Status (v1.0.0 — Pre-release)
This release is an early working prototype for Windows (64-bit). We are publishing it early to gather honest technical feedback and build a community of security-minded developers.

**What works today:**
* PyQt6-based browser engine blocking JavaScript, plugins, and cookies on `sss://` domains.
* Local static server (`moteur_sss.py`, port 1965) with Path Traversal protection.
* Local 52-character CSPRNG key generation (264-bit entropy, >128-bit effective security against Grover's algorithm).

**Known limitations (honest list):**
* Windows executable is not yet EV code-signed (triggers SmartScreen).
* Symmetric local key only (asymmetric post-quantum signing is planned for V2).
* No native video streaming support yet.
* Linux and macOS builds are not packaged yet.

---

## Core Engineering Challenges (Where We Need Help)
Rethinking a zero-script web means solving hard technical problems from scratch. Contributions, RFCs, and architectural critiques are welcome on the following topics:

1. **Safe Media & Video Without JavaScript:**
   * *The challenge:* Modern video platforms rely heavily on JS players and `<iframe>` embeds, which break our security model.
   * *Goal:* Explore native HTML5 `<video>` support using strictly sandboxed, static media formats (e.g., direct `.webm`/`.mp4` streams) without reintroducing tracking or script execution vectors.
2. **Post-Quantum Asymmetric Authentication (V2):**
   * *The challenge:* Transitioning from a 264-bit local identifier to full cryptographic request signing to block unauthorized AI scrapers.
   * *Goal:* Integrate NIST-standardized **ML-DSA-65** (signatures) and **ML-KEM-768** (key encapsulation) via `liboqs` without bloating the client binary.
3. **Hybrid & P2P Hosting Architecture:**
   * *The challenge:* Allowing businesses to self-host their static `.sss` site on a local PC without losing availability when the machine goes offline.
   * *Goal:* Design a lightweight, signed static-file replication layer (P2P / static nodes) where nodes only cache verified HTML/CSS—eliminating malware execution risks.
4. **Cross-Platform Packaging:**
   * *Goal:* Build clean native packages for Linux (`.AppImage` / `.deb`) and macOS.

---

## How to Contribute
* **Open an Issue:** Found a security flaw, a bug, or a flaw in our threat model? Report it directly in the *Issues* tab.
* **Discuss Architecture:** Propose improvements to the `sss://` protocol specification.
* **Pull Requests:** Clean, minimal Python/PyQt6 contributions are welcome.

*Project initiated by Groupe RIGAUD Tech SASU (Sophia Antipolis, France).*
