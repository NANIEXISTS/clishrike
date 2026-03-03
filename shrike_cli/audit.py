import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Configuration
EXCLUDED_DIRS = {'node_modules', '.git', '.next', 'dist', 'build', 'venv', '__pycache__'}
MAX_FILE_SIZE_BYTES = 500 * 1024  # 500KB
PRE_FLIGHT_KEYWORDS = ['stripe', 'Stripe', 'sk_test', 'sk_live']

# Data Structure
# {
#   "HARDCODED_LIVE_KEY": [{"file": "...", "line": 5, "severity": "CRITICAL", "impact": "...", "patch": "..."}],
#   ...
# }

RULES = {
    "HARDCODED_LIVE_KEY": {
        "severity": "CRITICAL",
        "impact": "Live Stripe secret exposed in source code. Immediate account compromise risk.",
        "patch": "Move secret to environment variable and rotate immediately.",
        "order": 1
    },
    "WEBHOOK_SIGNATURE_BYPASS": {
        "severity": "CRITICAL",
        "impact": "Webhook payloads can be forged to grant free access.",
        "patch": "Implement stripe.webhooks.constructEvent() validation.",
        "order": 2
    },
    "MISSING_IDEMPOTENCY_KEY": {
        "severity": "CRITICAL",
        "impact": "Network timeouts cause duplicate charges and immediate chargebacks.",
        "patch": "Pass idempotencyKey (or idempotency_key) in the PaymentIntent/Charge creation payload.",
        "order": 3
    },
    "NEXTJS_APP_ROUTER_WEBHOOK_BODY_TRAP": {
        "severity": "HIGH",
        "impact": "Webhook signatures will permanently fail in production due to stream consumption.",
        "patch": "Use req.text() instead of req.json() to capture the raw body buffer.",
        "order": 4
    }
}

def get_line_number(content: str, index: int) -> int:
    return content.count('\n', 0, index) + 1

def scan_directory(target_path: str):
    start_time = time.time()
    
    files_traversed = 0
    files_ignored = 0
    stripe_files = []
    
    target_dir = Path(target_path).resolve()
    
    for root, dirs, files in os.walk(target_dir):
        # Apply strict directory exclusions
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            files_traversed += 1
            file_path = Path(root) / file
            
            # Size cap
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    files_ignored += 1
                    continue
            except OSError:
                files_ignored += 1
                continue
                
            # Pre-flight check
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if any(kw in content for kw in PRE_FLIGHT_KEYWORDS):
                    stripe_files.append((file_path, content))
                else:
                    files_ignored += 1
            except UnicodeDecodeError:
                files_ignored += 1 # Ignore binary files
            except IOError:
                files_ignored += 1
                
    results: Dict[str, List[Dict[str, Any]]] = {}
    
    for file_path, content in stripe_files:
        path_str = str(file_path.relative_to(target_dir))
        
        # 1. HARDCODED_LIVE_KEY
        if not file_path.name.startswith('.env'):
            for match in re.finditer(r'sk_live_[a-zA-Z0-9]+', content):
                line = get_line_number(content, match.start())
                _add_finding(results, "HARDCODED_LIVE_KEY", path_str, line)
                
        # 2. WEBHOOK_SIGNATURE_BYPASS
        webhook_match = re.search(r'(stripe\.webhooks|/webhook)', content, re.IGNORECASE)
        if webhook_match and 'constructEvent' not in content:
            line = get_line_number(content, webhook_match.start())
            _add_finding(results, "WEBHOOK_SIGNATURE_BYPASS", path_str, line)
            
        # 3. MISSING_IDEMPOTENCY_KEY
        for match in re.finditer(r'stripe\.(?:PaymentIntent|Charge|Subscription|Refund|Invoice|Transfer)\.create', content):
            # Look ahead ~500 chars for idempotency key
            start_idx = match.start()
            end_idx = min(len(content), start_idx + 500)
            payload_block = content[start_idx:end_idx]
            
            if not re.search(r'(idempotency[Kk]ey|_key)', payload_block, re.IGNORECASE):
                line = get_line_number(content, start_idx)
                _add_finding(results, "MISSING_IDEMPOTENCY_KEY", path_str, line)
                
        # 4. NEXTJS_APP_ROUTER_WEBHOOK_BODY_TRAP
        if path_str.endswith(('.ts', '.js')) and 'req.json()' in content and ('next/server' in content or 'app/api' in path_str.replace('\\', '/')):
            match = re.search(r'req\.json\(\)', content)
            line = get_line_number(content, match.start()) if match else 1
            _add_finding(results, "NEXTJS_APP_ROUTER_WEBHOOK_BODY_TRAP", path_str, line)

    duration = time.time() - start_time
    _render_results(files_traversed, files_ignored, len(stripe_files), duration, results)

def _add_finding(results: Dict[str, List[Dict]], rule_name: str, file_path: str, line: int):
    if rule_name not in results:
        results[rule_name] = []
    results[rule_name].append({
        "file": file_path,
        "line": line
    })

def _render_results(traversed: int, ignored: int, isolated: int, duration: float, results: Dict[str, List[Dict]]):
    # Header
    summary_text = (
        f"[bold green][✓][/bold green] Traversed {traversed} files. "
        f"Ignored {ignored}. Isolated {isolated} Stripe files in {duration:.3f} seconds."
    )
    console.print(Panel(summary_text, title="SHRIKE REPO AUDIT START", border_style="cyan"))
    print("\n")
    
    if not results:
        console.print("[bold green]No financial risks detected.[/bold green]")
        return
        
    critical_rules = []
    high_rules = []
    
    for rule in results.keys():
        if RULES[rule]["severity"] == "CRITICAL":
            critical_rules.append(rule)
        elif RULES[rule]["severity"] == "HIGH":
            high_rules.append(rule)
            
    critical_rules.sort(key=lambda r: RULES[r]["order"])
    high_rules.sort(key=lambda r: RULES[r]["order"])
    
    sorted_rules = critical_rules + high_rules
    
    # Ranked Groups Summary
    summary_panel = Text()
    if critical_rules:
        summary_panel.append(f"CRITICAL RISKS ({len(critical_rules)})\n", style="bold red")
        for i, rule in enumerate(critical_rules, 1):
            summary_panel.append(f"  {i}. {rule}\n", style="red")
        summary_panel.append("\n")
        
    if high_rules:
        summary_panel.append(f"HIGH RISKS ({len(high_rules)})\n", style="bold yellow")
        for i, rule in enumerate(high_rules, len(critical_rules) + 1):
            summary_panel.append(f"  {i}. {rule}\n", style="yellow")
            
    console.print(Panel(summary_panel, title="FINANCIAL THREAT MATRIX", border_style="bold blue"))
    print("\n")
    
    # Risk Blocks
    for rule_name in sorted_rules:
        rule_data = RULES[rule_name]
        severity = rule_data["severity"]
        color = "red" if severity == "CRITICAL" else "yellow"
        
        block = Text()
        block.append(f"[{severity}] {rule_name}\n\n", style=f"bold {color}")
        
        block.append("Location:\n", style="bold white")
        for finding in results[rule_name]:
            block.append(f"- {finding['file']}:{finding['line']}\n", style="cyan")
            
        block.append("\nFinancial Impact:\n", style="bold white")
        block.append(f"{rule_data['impact']}\n", style=color)
        
        block.append("\nPatch Goal:\n", style="bold white")
        block.append(f"{rule_data['patch']}", style="green")
        
        print("────────────────────────────────────────────")
        console.print(block)
        print("────────────────────────────────────────────\n")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    scan_directory(target)
