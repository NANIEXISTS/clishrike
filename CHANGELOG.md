# Changelog

All notable changes to CLI.SHRIKE are documented here.

---

## [1.0.0-poc] — February 2026

### 🎉 Public Beta Release

**This is the first public Proof of Concept release of CLI.SHRIKE.**

The core engine is fully functional and deterministic. The beta key `BETA-SHRIKE-POC` grants full access to all current commands.

### Added
- `shrike activate <key>` — License activation with validation
- `shrike audit <path>` — Full repository AST scan. Traverses source files, isolates Stripe-related code, and evaluates against the financial threat matrix
- `shrike analyze <file>` — Forensic webhook log parser with deterministic state-machine matching and optional Gemini LLM fallback for advanced multi-event correlation
- `shrike watch <logfile>` — Real-time file system monitor for live Stripe log files with `--exit-on-critical` flag for CI integration
- **12-rule threat matrix** covering:
  - Framework-specific webhook errors (Next.js App Router, Express.js)
  - Payment Intent state machine failures
  - Idempotency and concurrency race conditions
  - Database transaction boundary failures
  - Float precision and currency unit errors
  - API environment key cross-contamination

### Architecture
- 100% local execution. No cloud uploads. No telemetry.
- Deterministic AST-based scanning — same code always produces the same result
- Optional LLM layer (Gemini) for forensic payload analysis in `shrike analyze`
- Rich terminal output with severity-ranked threat matrix

---

## Upcoming — [Pro Tier]

- Expanded rule set (50+ rules)
- `shrike report` — HTML/PDF audit export
- GitHub Action for CI/CD enforcement
- Multi-framework support (Django, FastAPI, Rails, Laravel)

## Upcoming — [Team Tier]

- `shrike fix` — AI-assisted code patch generation
- Multi-seat licensing
- Priority support
