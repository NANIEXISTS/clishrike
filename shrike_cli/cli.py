import os
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich import box

from shrike_cli import __version__
from shrike_cli.audit import scan_directory
from shrike_cli.watch import watch_log_file
from shrike_cli.license import activate_license, check_license

# Lazy import analyzer — it depends on optional google-genai package
try:
    from shrike_cli.analyzer import StripeDiagnosticEngine, HAS_GENAI
except ImportError:
    StripeDiagnosticEngine = None
    HAS_GENAI = False

console = Console()

def render_report(filename: str, report: dict):
    # ─── Header ──────────────────────────────────────────
    header_text = Text(f"SHRIKE STRIPE DIAGNOSTIC ENGINE v1.0\n", style="bold cyan")
    header_text.append(f"File: {filename}\n", style="cyan")
    header_text.append(f"Mode: Automated Vulnerability & Logic Analysis", style="cyan")
    console.print(Panel(header_text, title="SYSTEM BOOT", border_style="cyan", box=box.HEAVY))
    
    issues = report.get('issues', [])
    if not issues:
        console.print("[dim]No issues detected.[/dim]")
        return
        
    console.print(Panel(f"DETECTED ISSUES (Ranked by Severity)\n", title="AUDIT SUMMARY", border_style="bold blue", box=box.HEAVY))
    for idx, issue in enumerate(issues, 1):
        severity_color = "red" if issue['severity'] == "CRITICAL" else "yellow"
        console.print(f"[bold white]{idx}.[/bold white] [bold {severity_color}]{issue['issue_type']}[/bold {severity_color}] ({issue['confidence']}%)")
    print("\n")

    for idx, issue in enumerate(issues, 1):
        severity_style = "bold red" if issue['severity'] == "CRITICAL" else "bold yellow"
        
        failure_table = Table(show_header=False, box=box.SIMPLE)
        failure_table.add_column("Key", style="bold white")
        failure_table.add_column("Value")
        
        failure_table.add_row("Issue Type:", Text(issue['issue_type'], style=severity_style))
        failure_table.add_row("Severity:", Text(issue['severity'], style=severity_style))
        failure_table.add_row("Confidence:", Text(f"{issue['confidence']}%", style="bold green"))
        
        evidence_text = Text(f"\nEvidence:\n", style="bold cyan")
        for ev in issue.get('evidence', []):
            evidence_text.append(f"• Found \"{ev}\"\n", style="cyan")
            
        root_cause = Text(f"\nRoot Cause:\n", style="bold white")
        root_cause.append(issue['root_cause'], style="white")
        
        console.print(Panel(failure_table, title=f"[{idx}] PRIMARY FAILURE DETECTED", border_style="red" if issue['severity'] == "CRITICAL" else "yellow", box=box.HEAVY))
        console.print(evidence_text)
        console.print(root_cause)
        print("\n")

        # ─── Minimal Patch ───────────────────────────────────
        code = issue['minimal_patch']
        lexer = "python" if "stripe.Subscription" in code else "javascript"
        syntax = Syntax(code, lexer, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"[{idx}] MINIMAL PATCH", border_style="green", box=box.HEAVY))
        print("\n")

        # ─── Production Risk ─────────────────────────────────
        risk = Text(issue['impact'], style="yellow")
        console.print(Panel(risk, title=f"[{idx}] PRODUCTION RISK ANALYSIS", border_style="yellow", box=box.HEAVY))
        print("\n")

        # ─── Verification Checklist ──────────────────────────
        checklist = Text()
        for step in issue['verification_steps']:
            checklist.append(f"{step}\n", style="bold cyan")
        console.print(Panel(checklist, title=f"[{idx}] VERIFICATION CHECKLIST", border_style="cyan", box=box.HEAVY))
        print("\n")
    
    console.print(Text("────────────────────────────────────────────\nEND OF REPORT\n────────────────────────────────────────────", style="dim"))

def main():
    parser = argparse.ArgumentParser(
        description="Shrike CLI - Deterministic Stripe Diagnostic Engine",
        epilog="Examples: shrike audit ./my-project | shrike analyze payload.txt | shrike activate BETA-SHRIKE-POC"
    )
    parser.add_argument("--version", action="version", version=f"shrike-cli {__version__}")
    parser.add_argument("command", choices=["analyze", "audit", "watch", "activate"], help="Command to execute")
    parser.add_argument("target", nargs="?", default=".", help="License key or path to file/directory (default: current directory)")

    # Optional flags
    parser.add_argument("--exit-on-critical", action="store_true", help="For watch mode: Exit with status 1 on CRITICAL detection.")

    args = parser.parse_args()
    
    if args.command == "activate":
        activate_license(args.target)
        sys.exit(0)
        
    # Enforce License for analysis tools
    if not check_license():
        sys.exit(1)
    
    if args.command == "analyze":
        if StripeDiagnosticEngine is None:
            console.print("[bold red]Error:[/bold red] The 'analyze' command requires the google-genai package.")
            console.print("Install it with: [bold cyan]pip install 'shrike-cli[analyze]'[/bold cyan]")
            sys.exit(1)

        if not os.path.exists(args.target) or args.target == ".":
            console.print(f"[bold red]Error:[/bold red] 'analyze' requires a specific file path. Usage: shrike analyze <payload.txt>")
            sys.exit(1)

        with open(args.target, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Initialize Engine (Checking for GEMINI API KEY for fallback)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            console.print("[dim yellow]Warning: GEMINI_API_KEY not found in environment. LLM fallback disabled. Operating in strict deterministic mode.[/dim yellow]")

        engine = StripeDiagnosticEngine(gemini_api_key=api_key)

        with console.status("[bold cyan]Analyzing payload vectors...[/bold cyan]", spinner="bouncingBar"):
            report = engine.analyze(raw_text)

        render_report(args.target, report)

    elif args.command == "audit":
        if not os.path.exists(args.target):
            console.print(f"[bold red]Error:[/bold red] Target '{args.target}' not found.")
            sys.exit(1)
        
        scan_directory(args.target)

    elif args.command == "watch":
        if not os.path.exists(args.target):
            console.print(f"[bold red]Error:[/bold red] Log file '{args.target}' not found.")
            sys.exit(1)
            
        try:
            watch_log_file(args.target, exit_on_critical=args.exit_on_critical)
        except KeyboardInterrupt:
            console.print("\n[dim]Shrike Watch terminated by user.[/dim]")
            sys.exit(0)

if __name__ == "__main__":
    main()
