# SubSnatch 🕵️‍♂️

Fast, async subdomain enumerator with passive (crt.sh) + brute-force support.

> ⚠️ **For authorized use only.** Never scan without permission.

## Features
- Passive subdomain discovery via crt.sh
- Wordlist-based brute-forcing
- Async HTTP probing (HTTP/HTTPS)
- Save results as JSON, CSV, or TXT
- Clean Rich-based terminal output

## Install
```bash
git clone https://github.com/yourusername/subsnatch.git
cd subsnatch
pip install -r requirements.txt



# Passive scan only
python3 subsnatch.py -d example.com

# Passive + wordlist → save as JSON
python3 subsnatch.py -d example.com -w wordlist.txt -o live.json

# Skip passive, use wordlist only
python3 subsnatch.py -d example.com -w subs.txt --no-passive
