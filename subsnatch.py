#!/usr/bin/env python3
"""
SubSnatch - Fast & Clean Subdomain Enumerator
Author: Hammad Khan
GitHub: https://github.com/yourusername/subsnatch
License: MIT

⚠️ ETHICAL REMINDER:
This tool is for authorized security testing ONLY.
Never scan domains you don't own or don't have explicit permission to test.
Misuse may violate laws like the CFAA, GDPR, or local cybercrime statutes.
"""

import argparse
import asyncio
import os
import sys
import json
import csv
import httpx
import dns.resolver
from rich.console import Console

console = Console()

# === BANNER ===
def print_banner():
    banner = r"""
   _____       _   _           _   _                
  / ____|     | | | |         | | | |               
 | (___  _   _| |_| |__   ___ | |_| | ___ _ __ ___  
  \___ \| | | | __| '_ \ / _ \| __| |/ _ \ '__/ __|
  ____) | |_| | |_| | | | (_) | |_| |  __/ |  \__ \
 |_____/ \__, |\__|_| |_|\___/ \__|_|\___|_|  |___/
          __/ |                                    
         |___/                                     
    Fast Subdomain Enumerator • by HK
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[bold yellow]⚠️  For authorized use only. Respect privacy & laws.[/bold yellow]\n")

# === REST OF YOUR EXISTING CODE BELOW ===

async def fetch_subdomains_crtsh(domain):
    subdomains = set()
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        async with httpx.AsyncClient(timeout=10, verify=False) as client:
            r = await client.get(url)
            if r.status_code != 200:
                console.print(f"[yellow][!] crt.sh returned status {r.status_code}[/yellow]")
                return subdomains

            try:
                data = r.json()
            except ValueError:
                console.print("[yellow][!] crt.sh response is not valid JSON[/yellow]")
                return subdomains

            if not isinstance(data, list):
                console.print("[yellow][!] crt.sh returned unexpected data format[/yellow]")
                return subdomains

            for entry in data:
                if not isinstance(entry, dict):
                    continue
                name_value = entry.get("name_value")
                if not isinstance(name_value, str):
                    continue
                for line in name_value.split("\n"):
                    line = line.strip().lower()
                    if line and line.endswith(f".{domain}") and "*" not in line:
                        subdomains.add(line)

    except httpx.RequestError as e:
        console.print(f"[yellow][!] crt.sh request failed: {e}[/yellow]")
    except Exception as e:
        console.print(f"[yellow][!] Unexpected error during crt.sh fetch: {e}[/yellow]")

    return subdomains

def resolve_ip(subdomain):
    try:
        answers = dns.resolver.resolve(subdomain, 'A', lifetime=2.0)
        return str(answers[0])
    except:
        return None

async def probe_subdomain(client, subdomain, results, semaphore):
    async with semaphore:
        ip = resolve_ip(subdomain)
        status = "DEAD"
        url_used = ""

        if ip:
            for scheme in ["https://", "http://"]:
                url = f"{scheme}{subdomain}"
                try:
                    response = await client.get(url, follow_redirects=True, timeout=6)
                    url_used = str(response.url)
                    status = "LIVE"
                    results.append({
                        "subdomain": subdomain,
                        "ip": ip,
                        "url": url_used
                    })
                    break
                except:
                    continue

        if status == "LIVE":
            console.print(f"[green]✅ {subdomain} ({ip}) → {url_used}[/green]")
        else:
            console.print(f"[dim]❌ {subdomain} (unreachable)[/dim]")

        return {"subdomain": subdomain, "ip": ip or "N/A", "status": status, "url": url_used}

def save_results(results, output_file):
    _, ext = os.path.splitext(output_file)
    ext = ext.lower().lstrip('.')

    try:
        if ext == "json":
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
        elif ext == "csv":
            with open(output_file, "w", newline="") as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=["subdomain", "ip", "url"])
                    writer.writeheader()
                    writer.writerows(results)
                else:
                    writer = csv.DictWriter(f, fieldnames=["subdomain", "ip", "url"])
                    writer.writeheader()
        else:  # .txt or any other → one URL per line
            with open(output_file, "w") as f:
                for r in results:
                    f.write(r["url"] + "\n")
        console.print(f"[cyan][*] Results saved to: {output_file}[/cyan]")
    except Exception as e:
        console.print(f"[red][!] Failed to save results: {e}[/red]")

async def main():
    print_banner()  # 🖨️ Show banner first!

    parser = argparse.ArgumentParser(
        description="SubSnatch: Fast Subdomain Enumerator (Passive + Bruteforce)",
        epilog="Example: python3 subsnatch.py -d example.com -w wordlist.txt -o live.json"
    )
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g., example.com)")
    parser.add_argument("-w", "--wordlist", help="Optional: subdomain wordlist for brute-forcing")
    parser.add_argument("--no-passive", action="store_true", help="Skip crt.sh passive enumeration")
    parser.add_argument("-t", "--threads", type=int, default=80, help="Max concurrent requests (default: 80)")
    parser.add_argument("-o", "--output", help="Output file (e.g., results.json, live.csv). No save if omitted.")
    
    args = parser.parse_args()

    subdomains = set()

    if not args.no_passive:
        console.print("[blue][*] Fetching subdomains from crt.sh (passive)...[/blue]")
        crt_subs = await fetch_subdomains_crtsh(args.domain)
        subdomains.update(crt_subs)
        console.print(f"[blue][+] Got {len(crt_subs)} subdomains from crt.sh[/blue]")

    if args.wordlist:
        if os.path.exists(args.wordlist):
            count = 0
            with open(args.wordlist) as f:
                for line in f:
                    sub = line.strip().lower()
                    if sub:
                        subdomains.add(f"{sub}.{args.domain}")
                        count += 1
            console.print(f"[green][+] Loaded {count} subdomains from wordlist[/green]")
        else:
            console.print(f"[yellow][!] Wordlist not found: {args.wordlist} — skipping bruteforce[/yellow]")
    elif args.no_passive:
        console.print("[red][!] No scanning method enabled (no wordlist + --no-passive). Exiting.[/red]")
        return

    subdomains = list(subdomains)
    if not subdomains:
        console.print("[red][!] No subdomains to scan.[/red]")
        return

    console.print(f"\n[bold green]→ Starting scan on {len(subdomains)} subdomains[/bold green]")

    live_results = []
    semaphore = asyncio.Semaphore(args.threads)

    async with httpx.AsyncClient(http2=True, verify=False, timeout=10) as client:
        tasks = [
            probe_subdomain(client, sub, live_results, semaphore)
            for sub in subdomains
        ]
        await asyncio.gather(*tasks)

    # Summary
    live_count = len(live_results)
    total = len(subdomains)
    console.print(f"\n[bold magenta]{'='*50}[/bold magenta]")
    console.print(f"[bold cyan]✅ Scan Complete[/bold cyan]")
    console.print(f"• Total scanned: {total}")
    console.print(f"• Live hosts: [bold green]{live_count}[/bold green]")

    if live_count:
        console.print(f"\n[bold green]🌐 Live Subdomains:[/bold green]")
        for r in live_results[:5]:
            console.print(f"  → {r['url']}")
        if live_count > 5:
            console.print(f"  ... and {live_count - 5} more")

    if args.output:
        save_results(live_results, args.output)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow][!] Scan interrupted by user.[/yellow]")
        sys.exit(1)
