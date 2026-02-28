<div align="center">

<img src="https://cli.shrike.pro/favicon.ico" width="60" alt="Shrike CLI">

# CLI.SHRIKE

**Deterministic Financial Risk Scanner for Stripe Integrations**

[![Version](https://img.shields.io/badge/version-1.0.0--poc-red?style=flat-square)](https://cli.shrike.pro)
[![License](https://img.shields.io/badge/license-Commercial-gray?style=flat-square)](https://cli.shrike.pro/terms.html)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue?style=flat-square)](#installation)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://python.org)

**[Website](https://cli.shrike.pro) · [Demo](https://cli.shrike.pro/demo-video.html) · [Terms](https://cli.shrike.pro/terms.html)**

---

*If it prints red — you are going to lose money.*

</div>

---

## What is Shrike?

Shrike is a locally-executed, deterministic CLI that performs deep static analysis and forensic parsing of your Stripe integration. It goes beyond generic linting to catch the specific, silent bugs that cause:

- 💸 Double charges on network timeouts (missing idempotency keys)
- 🔑 Hardcoded live API secrets in source code
- 🔄 Duplicate webhook processing (missing event deduplication)
- 🧩 Partial database commits after successful payment
- 🚫 Subscription stuck in `incomplete` state
- 🔀 Race conditions between frontend confirmation and webhook delivery

**Zero cloud. Zero uploads. Runs entirely on your machine.**

---

## Commands

```
shrike activate <LICENSE_KEY>    Activate your license
shrike audit   <./path>          Deep AST scan of a repository
shrike analyze <payload.txt>     Forensic parse of a Stripe webhook log
shrike watch   <logfile.txt>     Real-time file monitor for live Stripe logs
```

---

## Installation

### Prerequisites
- Python 3.10+
- `pip`

### macOS / Linux

```bash
# 1. Unzip the release
unzip shrike-cli-early-access.zip && cd shrike-cli

# 2. (Recommended) Create a virtual environment
python3 -m venv venv && source venv/bin/activate

# 3. Install the engine
pip install .

# 4. Activate with the Public Beta key
shrike activate BETA-SHRIKE-POC
```

### Windows (PowerShell)

```powershell
# 1. Expand the downloaded archive
Expand-Archive .\shrike-cli-early-access.zip -DestinationPath .\shrike-cli
cd .\shrike-cli

# 2. Create a virtual environment
py -m venv venv
.\venv\Scripts\activate

# 3. Install the engine
pip install .

# 4. Activate
shrike activate BETA-SHRIKE-POC
```

**[⬇ Download Free Beta](https://cli.shrike.pro/#download)**

---

## Example Output

```
╭──────────────────── SHRIKE REPO AUDIT START ────────────────────╮
│ ✓ Traversed 412 files. Ignored 300. Isolated 12 Stripe files.   │
╰─────────────────────────────────────────────────────────────────╯

╭──────────────────── FINANCIAL THREAT MATRIX ────────────────────╮
│ CRITICAL RISKS (2)                                               │
│  1. HARDCODED_LIVE_KEY                                           │
│  2. MISSING_IDEMPOTENCY_KEY                                      │
╰─────────────────────────────────────────────────────────────────╯

──────────────────────────────────────────────
[CRITICAL] HARDCODED_LIVE_KEY

Location:  src/app/api/webhook/route.ts:4

Financial Impact:
  Live Stripe secret exposed in source code.
  Immediate account compromise risk.

Patch Goal:
  Move secret to runtime env var immediately.
```

---

## Rule Categories

Shrike ships with rules across 5 risk domains:

| Layer | Category | Example Rules |
|---|---|---|
| 1 | State Machine Integrity | `PAYMENT_INTENT_REQUIRES_ACTION`, `SUBSCRIPTION_STUCK_INCOMPLETE` |
| 2 | Idempotency & Concurrency | `WEBHOOK_IDEMPOTENCY_FAILURE`, `RACE_CONDITION_DUPLICATE_PAYMENT` |
| 3 | Database & Logic Boundaries | `PARTIAL_TRANSACTION_COMMIT`, `REFUND_STATE_INCONSISTENCY` |
| 4 | Configuration & Edge Cases | `FLOAT_PRECISION_CURRENCY_ERROR`, `ENVIRONMENT_KEY_MISMATCH` |
| 5 | Framework-Specific | `NEXTJS_APP_ROUTER_WEBHOOK_RAW_BODY_ERROR`, `EXPRESS_WEBHOOK_SIGNATURE_VERIFICATION_FAILURE` |

---

## Forensic Analysis (`shrike analyze`)

For webhook log analysis, Shrike uses a combination of deterministic state-machine pattern matching and an optional Gemini LLM fallback layer for complex multi-event correlation.

```bash
# Analyze a captured Stripe webhook event log
shrike analyze ./webhook_log.txt

# Works offline without GEMINI_API_KEY (deterministic mode only)
export GEMINI_API_KEY=your_key_here
shrike analyze ./webhook_log.txt
```

---

## Privacy

- `shrike audit` runs **100% locally**. Your source code never leaves your machine.
- `shrike analyze` optionally uses the Gemini API for advanced correlation. Do not include PII or raw secrets in payload files passed to this command.
- License activation makes a single HTTPS request to verify your key. No telemetry, no analytics.

---

## Roadmap

- [x] `shrike audit` — AST-based repo scanning
- [x] `shrike analyze` — Forensic webhook payload parsing  
- [x] `shrike watch` — Real-time log file monitoring
- [ ] Expanded rule set (50+ rules) — *Pro tier*
- [ ] `shrike report` — HTML/PDF audit export — *Pro tier*
- [ ] GitHub Action for CI/CD pipeline enforcement — *Pro tier*
- [ ] `shrike fix` — AI-assisted patch generation — *Team tier*

---

## License

Shrike CLI is commercial software. The Public Beta is freely available under the key `BETA-SHRIKE-POC`.

A commercial license is required for production use, team deployment, or access to Pro features.

[Terms of Service](https://cli.shrike.pro/terms.html) · [Refund Policy](https://cli.shrike.pro/refund.html) · [cli.shrike.pro](https://cli.shrike.pro)

---

<div align="center">
Built by <a href="https://shrike.pro">NANIEXISTS</a> · <a href="mailto:support@shrike.pro">support@shrike.pro</a>
</div>
