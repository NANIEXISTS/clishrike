# Contributing to CLI.SHRIKE

Thank you for your interest in Shrike. 

The core engine source is not open-source at this time. However, contributions to the following are welcome:

## What You Can Contribute

- **Bug reports** — If `shrike audit` or `shrike analyze` produces incorrect or unexpected output for a valid Stripe pattern, open an issue with a minimal reproduction.
- **Rule requests** — If you've encountered a real Stripe failure mode that Shrike does not currently detect, open an issue with a description of the bug and its financial impact. Well-documented requests are fast-tracked into the rule set.
- **Documentation** — Corrections to the README or examples are always welcome via PR.

## Opening an Issue

Please use the following format:

```
**Command:** shrike audit / shrike analyze
**Stripe pattern:** (describe the integration pattern)
**Expected behaviour:** (what Shrike should detect)
**Actual behaviour:** (what Shrike actually outputs)
**Shrike version:** (output of `shrike --version`)
```

## Contact

For anything not suited to a public GitHub issue:
**support@shrike.pro**
