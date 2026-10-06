"""Simulated firewall tools for the workshop.

All three tools read from the committed data set (data/firewall.json).
The data is fabricated; the device, vendor, addresses, and findings are fictional.

Spooling is controlled by the server, not the tools: when the server is built
without a SpoolerConfig (naive mode) the spooler attributes below are inert and
every tool returns its full payload inline. With a SpoolerConfig (spindl mode)
large arrays are spooled automatically.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from spindl import BaseTool

from spindl_workshop.datasource import load_data


class GetDeviceInfo(BaseTool):
    name = "get_device_info"
    description = "Return firewall device details (hostname, model, OS, HA state)"
    category = "inventory"

    def guide(self) -> str:
        return (
            "# @get_device_info\n\n"
            "Small, always-inline response describing the simulated firewall.\n"
            "Useful as a connectivity smoke test: if this works, your client\n"
            "is wired up correctly.\n"
        )

    async def execute(self, **params) -> dict:
        return {"success": True, "data": load_data()["device"]}


class GetRulebase(BaseTool):
    name = "get_rulebase"
    description = "Return the full firewall security rulebase"
    category = "policy"
    spooler_auto_detect = True

    class InputModel(BaseModel):
        enabled_only: bool = Field(
            default=False, description="Return only enabled rules"
        )

    def guide(self) -> str:
        return (
            "# @get_rulebase\n\n"
            "Returns every rule in the security policy. The rulebase is large.\n"
            "When spooling is enabled the result is stored server-side and you\n"
            "receive a summary with a spool_id.\n\n"
            "## Follow-up\n\n"
            "- @spooler_query to filter (e.g. service = tcp/3389, action = allow)\n"
            "- @spooler_aggregate to group (e.g. rules per owner, per action)\n"
            "- @spooler_distinct for unique values, filterable (e.g. services in use)\n"
        )

    async def execute(self, **params) -> dict:
        validated = self.InputModel(**params)
        rules = load_data()["rulebase"]
        if validated.enabled_only:
            rules = [r for r in rules if r["enabled"]]
        return {"success": True, "data": rules}


class GetTrafficLogs(BaseTool):
    name = "get_traffic_logs"
    description = "Return firewall traffic logs for the last 24 hours"
    category = "logs"
    spooler_auto_detect = True

    class InputModel(BaseModel):
        action: str | None = Field(
            default=None, description="Filter by action: allow or deny"
        )
        destination_ip: str | None = Field(
            default=None, description="Filter by destination IP"
        )

    def guide(self) -> str:
        return (
            "# @get_traffic_logs\n\n"
            "Returns traffic log entries. Unfiltered, this is tens of thousands\n"
            "of tokens. When spooling is enabled the result is stored server-side\n"
            "and you receive a summary with a spool_id.\n\n"
            "## Follow-up\n\n"
            "- @spooler_query to page through matching sessions\n"
            "- @spooler_aggregate for denies grouped by source_ip\n"
            "- @spooler_distinct for unique services, filterable to a single host\n"
        )

    async def execute(self, **params) -> dict:
        validated = self.InputModel(**params)
        logs = load_data()["traffic_logs"]
        if validated.action:
            logs = [x for x in logs if x["action"] == validated.action]
        if validated.destination_ip:
            logs = [x for x in logs if x["destination_ip"] == validated.destination_ip]
        return {"success": True, "data": logs}
