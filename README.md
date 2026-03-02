<div align="center">

<img src="https://cli.shrike.pro/favicon.ico" width="80" alt="Shrike CLI Logo">

# 🦅 Shrike CLI

**The Deterministic Financial Risk Scanner for Stripe Integrations.**

[![Version](https://img.shields.io/badge/version-1.0.0--poc-red?style=for-the-badge)](https://cli.shrike.pro)
[![License](https://img.shields.io/badge/license-Commercial-gray?style=for-the-badge)](https://cli.shrike.pro/terms.html)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue?style=for-the-badge)](#quick-start)
[![Status](https://img.shields.io/badge/status-Public_Beta-success?style=for-the-badge)](#quick-start)

**[Website](https://cli.shrike.pro) • [Demo](https://cli.shrike.pro/#demo) • [Terms](https://cli.shrike.pro/terms.html)**

<br>
<i>If it prints red — you are going to lose money.</i>
<br><br>

</div>

---

## 🛑 The Problem

Generic linters (ESLint, Prettier, Semgrep) check for code style, syntax errors, and common security flaws. **They do not understand business logic.**

They will not tell you when a network timeout silently double-charges your customer. They will not warn you when a webhook handler consumes a stream improperly, permanently breaking signature verification in production. 

Stripe bugs don't crash your app—they silently bleed revenue, upset customers, and ruin unit economics.

## 🛡️ The Solution

**Shrike CLI** is a locally-executed, deterministic engine that performs deep static analysis and forensic parsing of your Stripe integration. It is purpose-built to catch financial edge cases before they reach production.

### Core Capabilities

| Mode | Command | Description |
|---|---|---|
| **Audit** | `shrike audit <path>` | Scans repositories in milliseconds to flag missing idempotency keys, unprotected endpoints, and exposed live secrets. |
| **Analyze** | `shrike analyze <file>` | Forensically parses Stripe webhook payloads and server logs to diagnose complex state-machine failures. |
| **Watch** | `shrike watch <file>` | Securely tails local log files during development, throwing instant alerts when vulnerabilities are triggered. |

> **Privacy First:** Shrike runs **100% locally**. Your source code never leaves your filesystem. There is zero telemetry, zero cloud calls, and zero analytics. The only outbound network call is the optional Gemini LLM fallback in the `analyze` command.

---

## ⚡ Quick Start

Shrike is distributed as a cross-platform Python package. Requires Python 3.10+.

### 1. Download
Download the latest `shrike-cli.zip` from [cli.shrike.pro](https://cli.shrike.pro/#download).

### 2. Install (macOS / Linux)
```bash
# Unzip and enter directory
unzip shrike-cli-early-access.zip -d shrike-cli && cd shrike-cli

# Create isolated environment (recommended)
python3 -m venv venv && source venv/bin/activate

# Install the engine
pip install .

# Activate the Free Beta
shrike activate BETA-SHRIKE-POC
```

### 2. Install (Windows PowerShell)
```powershell
# Expand and enter directory
Expand-Archive .\shrike-cli-early-access.zip -DestinationPath .\shrike-cli
cd .\shrike-cli

# Create isolated environment (recommended)
py -m venv venv
.\venv\Scripts\activate

# Install the engine
pip install .

# Activate the Free Beta
shrike activate BETA-SHRIKE-POC
```

### 3. Run
```bash
# Scan your entire project repository
shrike audit ./my-saas-backend
```

---

## 📊 Example Output

When Shrike detects a vulnerability, it outputs a ranked, CFO-level financial risk matrix with exact file locations, financial impacts, and required patches.

```text
╭──────────────────── SHRIKE REPO AUDIT START ────────────────────╮
│ ✓ Traversed 412 files. Ignored 300. Isolated 12 Stripe files.   │
╰─────────────────────────────────────────────────────────────────╯

╭──────────────────── FINANCIAL THREAT MATRIX ────────────────────╮
│ CRITICAL RISKS (2)                                              │
│  1. HARDCODED_LIVE_KEY                                          │
│  2. MISSING_IDEMPOTENCY_KEY                                     │
╰─────────────────────────────────────────────────────────────────╯

──────────────────────────────────────────────
[CRITICAL] MISSING_IDEMPOTENCY_KEY

Location:
- src/services/billing.ts:42

Financial Impact:
Network timeouts will cause duplicate charges and immediate chargebacks.

Patch Goal:
Pass idempotencyKey (or idempotency_key) in the PaymentIntent creation payload.
──────────────────────────────────────────────
```

---

## 🧠 Rule Engine Domains

Shrike ships with rules mapped across 5 specific risk tiers:

1. **State Machine Integrity** (e.g., `PAYMENT_INTENT_REQUIRES_ACTION`)
2. **Idempotency & Concurrency** (e.g., `RACE_CONDITION_DUPLICATE_PAYMENT`)
3. **Database Boundaries** (e.g., `PARTIAL_TRANSACTION_COMMIT`)
4. **Configuration Edge Cases** (e.g., `FLOAT_PRECISION_CURRENCY_ERROR`)
5. **Framework-Specific Traps** (e.g., `NEXTJS_APP_ROUTER_WEBHOOK_BODY_TRAP`)

---

## 🗺️ Roadmap

- [x] **v1.0.0-poc:** Public Beta (Audit, Analyze, Watch)
- [ ] **Pro Tier:** 50+ Extended Rules (Subscriptions, Connect, Multi-currency)
- [ ] **Pro Tier:** CI/CD GitHub Action enforcement
- [ ] **Pro Tier:** PDF/HTML Export Reports
- [ ] **Team Tier:** AI-assisted patch generation

---

## ⚖️ License & Legal

Shrike CLI is commercial software built by [NANIEXISTS](https://shrike.pro).

The current version is available as a **Free Public Beta** using the activation key `BETA-SHRIKE-POC`. A commercial license will be required for the upcoming Pro tier and production CI/CD deployments.

- **[Terms of Service](https://cli.shrike.pro/terms.html)**
- **[Refund Policy](https://cli.shrike.pro/refund.html)**

<br>
<div align="center">
  <sub>Built securely by <a href="https://shrike.pro">Rahul</a>. Needs help? <a href="mailto:support@shrike.pro">support@shrike.pro</a></sub>
</div>
