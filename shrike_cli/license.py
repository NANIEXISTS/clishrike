import os
import json
import hashlib
from pathlib import Path
from rich.console import Console

console = Console()

# We will store the hashed license in ~/.shrike/license.json
SHRIKE_DIR = Path.home() / ".shrike"
LICENSE_FILE = SHRIKE_DIR / "license.json"

def activate_license(key: str):
    # Strip all whitespace and invisible characters
    key = key.strip().replace('\r', '').replace('\n', '').replace('\t', '').replace('\u200b', '').upper()
    if not key or len(key) < 3:
        console.print("[bold red]Error:[/bold red] Please provide a valid license key.")
        return False
        
    try:
        SHRIKE_DIR.mkdir(parents=True, exist_ok=True)
        
        # We only save a hash locally, not the plaintext key
        # Adding a fixed salt just to prevent basic hash lookups if somehow leaked
        salted_key = f"shrike_v1_{key}"
        key_hash = hashlib.sha256(salted_key.encode()).hexdigest()
        
        with open(LICENSE_FILE, 'w') as f:
            json.dump({"hashed_key": key_hash, "schema_version": 1}, f)
            
        console.print("[bold green]Shrike CLI activated successfully![/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]Activation Exception:[/bold red] Could not write to {LICENSE_FILE}. {e}")
        return False

def check_license():
    if not LICENSE_FILE.exists():
        console.print("\n[bold red]Shrike is not activated.[/bold red]")
        console.print("Run: [bold cyan]shrike activate <LICENSE_KEY>[/bold cyan]\n")
        return False
        
    try:
        with open(LICENSE_FILE, 'r') as f:
            data = json.load(f)
            
        if "hashed_key" in data:
            return True
        else:
            console.print("\n[bold red]License file corrupted.[/bold red]")
            console.print("Run: [bold cyan]shrike activate <LICENSE_KEY>[/bold cyan]\n")
            return False
    except Exception as e:
        console.print(f"\n[bold red]Failed to read license.[/bold red]\n{e}")
        return False
