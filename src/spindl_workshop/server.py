"""CyberCon2026 workshop server: a simulated firewall behind MCP.

Run in one of two modes:

    spindl-workshop --mode naive    Exercise 1: no spooling, raw dumps
    spindl-workshop --mode spindl   Exercise 2: spindl spooling enabled

Same data, same tools, same questions. The only variable is the architecture.
"""

from __future__ import annotations

import argparse
import asyncio

from spindl import MCPServer, SpoolerConfig

from spindl_workshop.tools import GetDeviceInfo, GetRulebase, GetTrafficLogs


def build_server(mode: str) -> MCPServer:
    spooler = SpoolerConfig() if mode == "spindl" else None
    server = MCPServer(prefix="fw", spooler=spooler)
    server.register_all(
        [
            GetDeviceInfo(),
            GetRulebase(),
            GetTrafficLogs(),
        ]
    )
    return server


def main() -> None:
    parser = argparse.ArgumentParser(prog="spindl-workshop")
    parser.add_argument(
        "--mode",
        choices=["naive", "spindl"],
        default="naive",
        help="naive = raw dumps (exercise 1), spindl = spooled (exercise 2)",
    )
    args = parser.parse_args()
    asyncio.run(build_server(args.mode).run_stdio())


if __name__ == "__main__":
    main()
