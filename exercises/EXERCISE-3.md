# Exercise 3: Turn the Dials (70 to 80 min, optional follow-along)

This segment is presenter-led: a walk through spindl's internals, the
spool summary anatomy, the prefix system, and what 0.3.0 added for
model-facing hardening and production deployment. You can just watch, or
follow along with the experiment below.

## The experiment: make spindl behave naive without touching the code

Spooling is governed by two thresholds, not by the tools. Raise the
thresholds past the data size and the architecture steps aside.

Add an `env` block to your spindl-mode client config:

```json
"fw-workshop": {
  "command": "uvx",
  "args": [
    "--from", "git+https://github.com/Cognisn/spindl-workshop",
    "spindl-workshop", "--mode", "spindl"
  ],
  "env": {
    "SPOOLER_MAX_INLINE_TOKENS": "200000",
    "SPOOLER_MAX_INLINE_ITEMS": "5000"
  }
}
```

Restart the client and repeat the rulebase question from Exercise 1.
Despite running in spindl mode, the full dump lands in your context
again: the thresholds, not the mode, decide what spools.

## Points to take away

- Defaults are `SPOOLER_MAX_INLINE_TOKENS=2000` and
  `SPOOLER_MAX_INLINE_ITEMS=10`; every `SpoolerConfig` field has a
  matching `SPOOLER_*` environment variable.
- Tools opt in via `spooler_auto_detect` or explicit
  `spooler_array_paths`; responses under the thresholds are passed
  through inline untouched.
- Since 0.3.0, unknown tool arguments are rejected with a structured
  `INVALID_ARGUMENTS` error naming the accepted parameters, because a
  silently ignored argument makes a model confidently wrong.

**Remove the `env` block afterwards** so Exercise 2 behaviour returns.
