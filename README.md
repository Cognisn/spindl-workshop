# spindl-workshop: MCP Response Spooling (CyberCon2026)

Hands-on companion repository for the CyberCon2026 workshop on MCP spooling
architecture, built on [spindl](https://github.com/Cognisn/spindl).

You will run the same simulated firewall MCP server twice, ask it the same
security questions, and watch what happens to your client's context window.

- **Exercise 1 (naive mode):** the server returns raw dumps. A 1,200 rule
  rulebase lands in your model's context in full.
- **Exercise 2 (spindl mode):** the same server, same data, same tools, with
  spindl's response spooler enabled. Large results are stored server-side and
  you explore them with query, aggregate, and distinct tools.

All data is fabricated. The device, vendor, addresses, rules, and logs are
fictional and generated deterministically, so everyone in the room sees
identical data.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`uv --version` to confirm).
  uv will fetch a suitable Python (3.10+) automatically if needed.
- An MCP client that supports local stdio servers. Tested with
  **Claude Desktop** and **VS Code (Copilot agent mode)**. See
  `clients/` for configuration snippets, including notes for ChatGPT/Codex
  users.
- You should be comfortable editing your client's MCP configuration file.

## Smoke test (do this before the workshop)

```bash
uvx --from git+https://github.com/Cognisn/spindl-workshop spindl-workshop --help
```

If you see the usage text with `--mode {naive,spindl}`, you are ready.

## Exercise 1: the naive server

Configure your client with mode `naive` (snippets in `clients/`), then work
through `exercises/EXERCISE-1.md`. You will ask questions such as:

- Which enabled rules allow inbound RDP from the internet?
- Which source IP generated the most denies in the last 24 hours?

Watch your client's context/token indicators while you do it.

## Exercise 2: the spindl server

Change one word in your client config, `naive` to `spindl`, restart the
client, and work through `exercises/EXERCISE-2.md`. Same questions. Note the
spool summaries, then let the model drive `fw_spooler_query`,
`fw_spooler_aggregate`, and `fw_spooler_distinct`.

## What is in the box

| Path | Purpose |
| --- | --- |
| `data/firewall.json` | Committed, deterministic fabricated data set |
| `src/spindl_workshop/` | The MCP server and its three firewall tools |
| `exercises/` | The two hands-on exercise sheets |
| `clients/` | Per-client MCP configuration snippets |
| `tools/generate_data.py` | Presenter-only data generator (seeded) |

## The tools exposed

With prefix `fw`, the server exposes:

- `fw_get_device_info`: tiny response, use as a connectivity check
- `fw_get_rulebase`: the full security policy (large)
- `fw_get_traffic_logs`: 24 hours of traffic logs (very large)
- `fw_list_tools` and `fw_describe_tool`: spindl's built-in skills guides
- `fw_spooler_list` / `fw_spooler_query` / `fw_spooler_aggregate` /
  `fw_spooler_distinct`: present in spindl mode only

## Licence

MIT. Fabricated data, no real systems were harmed.
