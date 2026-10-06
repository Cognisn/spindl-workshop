# ChatGPT / Codex users (untested-live appendix)

The ChatGPT chat product does not run local stdio MCP servers; it accepts
remote HTTPS connectors only. Two workable paths, neither supported live in
the room:

## Option A: Codex CLI (stdio supported)

The Codex CLI and IDE extension can run local stdio MCP servers. Add via the
Codex MCP configuration:

```toml
[mcp_servers.fw-workshop]
command = "uvx"
args = ["--from", "git+https://github.com/Cognisn/spindl-workshop", "spindl-workshop", "--mode", "naive"]
```

## Option B: Bridge to a remote endpoint

Expose the server over HTTP with spindl's HTTP transport, or wrap the stdio
server with a bridge such as `mcp-remote`, then add the resulting HTTPS URL
as a custom connector in ChatGPT developer mode. This requires a host or
tunnel you control and is left as an exercise.
