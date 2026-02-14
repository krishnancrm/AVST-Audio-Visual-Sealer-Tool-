\# Mighty Forensic Seal \& Mirror Auditor (v4.0)



A high-integrity forensic watermarking toolset designed to survive aggressive social media compression (WhatsApp, X, Instagram) and provide verifiable timestamps through temporal rolling seeds.



\## 🛡️ Core Features



\- \*\*Dual-Layer Encoding\*\*: Simultaneously embeds a "Fragile" layer (high-precision) and a "Robust" layer (2x2 cluster blocks) for comparative forensic analysis.

\- \*\*Adaptive Radius Search\*\*: Auditor compensates for up to ±5 pixels of anchor drift caused by resampling or JPEG block alignment.

\- \*\*Temporal Rolling Seed\*\*: The robust cryptographic cloack rotates every 2 hours, effectively timestamping the image to a specific forensic window.

\- \*\*Visual Richness (Decoy Injection)\*\*: Injects 450+ non-syncing decoy pixels to maintain a natural image texture and mask the payload coordinates.

\- \*\*Time-Gated Integrity\*\*: Distributed binaries feature a 30-day lifecycle to ensure tooling is always up-to-date with current forensic standards.



\## 📂 Project Structure



\- `bin/mighty\_seal.exe`: The secure encoder (Hardened Binary).

\- `bin/mighty\_decode.exe`: The adaptive forensic auditor (Hardened Binary).

\- `execute\_stress\_test.py`: Python automation script for batch processing and compression simulation.



\## 🚀 Quick Start



\### 1. Requirements

\- Windows 10/11

\- Python 3.x (with `Pillow` library)

\- `pip install Pillow`



\### 2. Running a Stress Test

Place your source images in a folder named `Surveillance\_Data/` and run:



```bash

python execute\_stress\_test.py

## 📊 Verified Performance (v4.0)

The following metrics were captured using the internal `execute_stress_test.py` manager across a 20-image surveillance suite:

| Threat Model | Resolution | L1 (Fragile) | L2 (Robust) | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Lossless Transfer** | Original | 100% | 100% | **MIGHTY** |
| **WhatsApp Wash** | 1600px | 30% | 100% | **MIGHTY** |
| **X (Twitter) Feed** | 2048px | 28% | 99% | **MIGHTY** |
| **Heavy Blur/Noise** | Variable | 15% | 92% | **SECURE** |

**Note:** Survival of L2 (Robust) allows for 100% reconstruction of embedded MAC/GPS strings.

