# SubSnatch 🕵️‍♂️
### Fast asynchronous subdomain enumerator with passive + brute-force modes.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ⚡ About
SubSnatch is a lightweight, async-powered subdomain enumeration tool that combines:

- Passive reconnaissance via **crt.sh**
- Brute‑force discovery using a wordlist
- Live host checking (HTTP/HTTPS)
- Modern terminal output powered by **Rich**
- Multiple export formats: **JSON, CSV, TXT**

Designed for pentesters, bug bounty hunters, and researchers.

> ⚠️ **Use only on assets you are authorized to test.**

---

## 🚀 Features

- 🔎 Passive discovery with crt.sh  
- 🧨 Wordlist‑based brute forcing  
- ⚡ Asynchronous probing for live hosts  
- 🖥️ Clean terminal UI using Rich  
- 💾 Export results to **JSON / CSV / TXT**  
- 🧵 Fully async for maximum speed  

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/subsnatch.git
cd subsnatch
pip install -r requirements.txt

🔧 Usage
Passive scan only
python3 subsnatch.py -d example.com

Passive + brute-force, save results
python3 subsnatch.py -d example.com -w wordlist.txt -o live.json

Brute-force only (skip passive)
python3 subsnatch.py -d example.com -w subs.txt --no-passive

📂 Output Formats
output.json
output.csv
output.txt

📝 Options
| Flag           | Description                      |
| -------------- | -------------------------------- |
| `-d`           | Target domain                    |
| `-w`           | Wordlist for brute forcing       |
| `--no-passive` | Disable crt.sh lookup            |
| `-o`           | Output file name                 |
| `--threads`    | Set async concurrency (optional) |


❗ Disclaimer
This tool is intended for authorized security testing only.
The developer assumes no responsibility for misuse.

📄 License
MIT License
