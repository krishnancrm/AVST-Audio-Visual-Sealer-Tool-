# Mighty Forensic Seal & Mirror Auditor (v4.0 Beta)

A high-integrity forensic watermarking toolset designed to survive aggressive social media compression (WhatsApp, X, Instagram) and provide verifiable timestamps through temporal rolling seeds.

## 🛡️ Core Features

- **Dual-Layer Encoding**: Simultaneously embeds a "Fragile" layer (L1) for tamper detection and a "Robust" layer (L2) for survival against extreme compression.
- **Temporal Rolling Seed (2-Hour Lifecycle)**: The cryptographic one-time-arbitrary self-clock rotates every 2 hours. **Note:** Seals are time-gated; verification must occur within the specific forensic window as the seal itself expires after 120 minutes to ensure maximum temporal security.
- **Hardened Executables**: The core logic is distributed via compiled binaries (`.exe`) which are hardened against reverse engineering. This ensures the proprietary sealing math and coordinate mapping remain secure and tamper-proof—a unique novelty in forensic software distribution.
- **Adaptive Radius Search**: Auditor compensates for up to ±5 pixels of anchor drift caused by resampling or JPEG block alignment.
- **Visual Richness (Decoy Injection)**: Injects 450+ non-syncing decoy pixels to maintain a natural image texture and mask the payload coordinates.

## 📂 Project Structure

- `bin/`: Contains the core hardened binaries (`mighty_seal.exe` and `mighty_decode.exe`).
- `Surveillance_Data/`: The primary input directory. Place raw, unsealed images here for batch processing.
- `Sealed_Compressed/`: Output directory for sealed images processed with standard compression for web/social media distribution.
- `Sealed_Lossless/`: Output directory for high-fidelity sealed images, preserving 100% of the L1 Fragile layer for maximum forensic evidence.
- `execute_stress_test.py`: Python automation script for batch processing, folder management, and compression simulation.

## ⚠️ Beta Version Notice
This is a **Beta** release. While the L2 (Robust) layer has shown 100% credibility in current testing, the software is provided for evaluation purposes. Features such as temporal syncing and hardware-specific optimizations are subject to refinement.

## 🚀 Quick Start

### 1. Requirements
- Windows 10/11
- Python 3.x
- `pip install Pillow` (Required for the stress test automation script)

### 2. Running a Stress Test
Ensure your source images are in `Surveillance_Data/` and run:

```bash
python execute_stress_test.py

## 📊 Verified Performance (v4.0)

The following metrics were captured using the internal `execute_stress_test.py` manager across a 20-image surveillance suite:

| Threat Model | Resolution | L1 (Fragile) | L2 (Robust) | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Lossless Transfer** | Original | 100% | 100% | **MIGHTY** |
| **WhatsApp Wash** | 1600px | 30% | 100% | **MIGHTY** |
| **X (Twitter) Feed** | 2048px | 28% | 99% | **MIGHTY** |
| **Heavy Blur/Noise** | Variable | 15% | 92% | **SECURE** |

**Note:** Survival of L2 (Robust) allows for 100% reconstruction of embedded MAC/GPS strings.




