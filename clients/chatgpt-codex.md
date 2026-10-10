# ChatGPT desktop app (and Codex CLI)

The ChatGPT desktop app supports local stdio MCP servers. Configuration is
shared with the Codex CLI and IDE extension via `~/.codex/config.toml`
(docs: https://learn.chatgpt.com/docs/extend/mcp?surface=app).

## Option A: Settings UI

Settings -> MCP servers -> Add server: name it `fw-workshop`, choose
STDIO, and enter the command below. Save, then Restart.

```
uvx --from git+https://github.com/Cognisn/spindl-workshop spindl-workshop --mode naive
```

## Option B: config file

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.fw-workshop]
command = "uvx"
args = [
  "--from", "git+https://github.com/Cognisn/spindl-workshop",
  "spindl-workshop", "--mode", "naive",
]
```

For Exercise 2, change `"naive"` to `"spindl"` and restart the server
(Settings -> MCP servers -> Restart, or restart the app). The Codex CLI
picks up the same configuration unchanged.

## ChatGPT on the web

The web product accepts remote HTTPS MCP connectors only and cannot spawn
local stdio servers. Use the desktop app for this workshop, or expose the
server over HTTP (spindl `run_http`) and add it as a custom connector.
