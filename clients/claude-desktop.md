# Claude Desktop

Config file location:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fw-workshop": {
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
```

For Exercise 2, change `"naive"` to `"spindl"` and fully restart
Claude Desktop (quit from the tray/menu bar, not just the window).

**Windows note:** if `uvx` is not found, use the full path to the executable,
typically `%USERPROFILE%\.local\bin\uvx.exe`, as the `command` value.
