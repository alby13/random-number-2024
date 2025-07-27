# Random Number Generator 2024 (Updated July 2025) &nbsp;🎲
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

> Hardware‑grade randomness with automatic fall‑back – wrapped in a friendly GUI.

![Screenshot of the GUI](2025.png)

---

## ✨  Features
| Back‑end | Source of entropy | Supported OS | Auto‑detects? | Notes |
|----------|------------------|--------------|---------------|-------|
| **Entropy Pool** | `os.urandom` / `getrandom` | All | ✅ | Always available |
| **Windows CryptoAPI** | `advapi32!CryptGenRandom` | Windows 10+ | ✅ | FIPS‑compliant |
| **Intel / AMD RDRAND** | CPU hardware RNG | Windows (64‑bit) with RDRAND‑capable CPU | ✅ | Greyed‑out if unsupported |

*At start‑up the app probes the host PC and disables buttons for any methods that are unavailable, so nothing ever crashes.*

---

## 🚀  Quick Start

```bash
# 1 Get the code
git clone https://github.com/alby13/random-number-2024.git
cd random-number-2024

# 2 Create a venv (recommended) and install Tk if it's missing
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install pillow  # <-- only if your Python build lacks Tk images

# 3 Run the GUI
python rng_gui.py
````

No command‑line flags are required – the window opens immediately.

---

## 🧐  Why True Randomness Is Hard

Computers are deterministic: given the same input they always produce the same output.
“True” randomness, by contrast, is unpredictable and pattern‑less. Software **alone** can’t create that unpredictability, so this project leans on:

1. **Operating‑system entropy pools**
   Keyboard timing, disk‑seek jitter, network interrupts… all mixed by the kernel.

2. **Hardware RNG instructions** (`RDRAND`)
   Thermal noise on modern x86 chips converted directly into random bits.

3. **CryptGenRandom**
   Microsoft’s long‑standing, FIPS‑validated CSPRNG.

Each generator is isolated; if one fails (or simply doesn’t exist on a user’s machine) the rest of the program keeps running.

---

## 🛠️  Developer Notes

* **Python ≥ 3.10** required.
  The code is tested on 3.10 – 3.12.
* The GUI is pure Tkinter; no extra GUI libraries to install.
* Headless mode (e.g. CI servers) works too – `python rng_gui.py --nogui` runs a quick self‑test and exits.

---

## 🤝  Contributing

Bug reports, feature requests, or pull‑requests are warmly welcomed!

1. Fork the repo
2. Create a branch (`git checkout -b my-feature`)
3. Commit your changes (`git commit -am "Add amazing feature"`)
4. Push to the branch (`git push origin my-feature`)
5. Open a Pull Request

---

## 📄  License

This project is released under the MIT License – see [`LICENSE`](LICENSE) for details.

```
**What changed?**

* Added a clean screenshot link (no raw HTML).
* New **Features** table explaining auto‑detection.
* Installation & run instructions spelled out.
* Headless/CI note and `--nogui` flag mention.
* Fixed repository URL in the clone snippet.
* Tidier markdown (consistent lists, code fences, emoji for quick scanning).
```
