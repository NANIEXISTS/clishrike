import time
import os
import sys
import re
import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from shrike_cli.analyzer import StripeDiagnosticEngine
from shrike_cli.rules import STRIPE_RULES

console = Console()

def watch_log_file(file_path: str, exit_on_critical: bool):
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File '{file_path}' not found.")
        sys.exit(1)
        
    engine = StripeDiagnosticEngine()
    
    console.print(f"[bold cyan]Watching {file_path}...[/bold cyan]\n")
    
    with open(file_path, "r", encoding="utf-8") as file:
        file.seek(0, os.SEEK_END)
        
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
                
            # Perform a fast deterministic check instead of initializing full analyzer payload
            for rule_name, rule_data in STRIPE_RULES.items():
                if rule_data["severity"] == "CRITICAL" or rule_data["severity"] == "HIGH":
                    for trigger in rule_data["regex_triggers"]:
                        if re.search(trigger, line, re.IGNORECASE):
                            _render_alert(rule_name, rule_data, line.strip())
                            
                            if rule_data["severity"] == "CRITICAL" and exit_on_critical:
                                console.print("[bold red]Exiting due to --exit-on-critical flag.[/bold red]")
                                sys.exit(1)
                            
def _render_alert(rule_name: str, rule_data: dict, trigger_line: str):
    severity_color = "red" if rule_data["severity"] == "CRITICAL" else "yellow"
    
    alert = Text()
    alert.append(f"[{rule_data['severity']}] {rule_name}\n", style=f"bold {severity_color}")
    alert.append(f"Detected at {datetime.datetime.now().strftime('%H:%M:%S')}\n\n", style="dim")
    
    alert.append(f"Trigger: ", style="bold white")
    alert.append(f"{trigger_line[:100]}...\n", style="cyan")
    
    alert.append(f"\nRoot Cause:\n", style="bold white")
    alert.append(f"{rule_data['root_cause']}\n", style=severity_color)
    
    alert.append(f"\nPatch Goal:\n", style="bold white")
    alert.append(f"{rule_data.get('minimal_patch', 'Review application configuration.')}\n", style="green")
    
    console.print(Panel(alert, title=f"FINANCIAL RISK DETECTED", border_style=severity_color))
    print("\n")
