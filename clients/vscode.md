# VS Code (Copilot agent mode)

Requires VS Code 1.99+ with MCP support enabled.

Add to your user `settings.json`, or a workspace `.vscode/mcp.json`:

```json
{
  "mcp": {
    "servers": {
      "fw-workshop": {
        "type": "stdio",
        "command": "uvx",
        "args": [
          "--from",
          "git+https://github.com/Cognisn/spindl-workshop",
          "spindl-workshop",
          "--mode",
          "naive"
        ]
      }
    }
  }
}
```

For Exercise 2, change `"naive"` to `"spindl"`, then restart the server from
the MCP servers view (or reload the window).
