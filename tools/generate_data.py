#!/usr/bin/env python3
"""Generate the fabricated firewall data set for the CyberCon2026 spindl workshop.

Deterministic: the same SEED always produces byte-identical output, so every
attendee, and the presenter, sees exactly the same data and the same numbers.

The output (data/firewall.json) is committed to the repository. Attendees never
run this script; it exists so the presenter can regenerate or re-tune the data.

Planted findings (the "bad rules") are listed in docs/PRESENTER-NOTES.md.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20261014  # conference date, never change without updating exercises
RULE_COUNT = 1200
LOG_COUNT = 2000

rng = random.Random(SEED)

ZONES = ["untrust", "dmz", "trust", "mgmt", "vpn", "guest"]
SERVICES = [
    ("tcp/443", "HTTPS"), ("tcp/80", "HTTP"), ("tcp/22", "SSH"),
    ("tcp/3389", "RDP"), ("udp/53", "DNS"), ("tcp/25", "SMTP"),
    ("tcp/445", "SMB"), ("tcp/1433", "MSSQL"), ("tcp/3306", "MySQL"),
    ("tcp/8443", "HTTPS-ALT"), ("udp/123", "NTP"), ("tcp/23", "TELNET"),
    ("tcp/21", "FTP"), ("tcp/5432", "PostgreSQL"), ("tcp/636", "LDAPS"),
]
APPS = ["web-browsing", "ssl", "ssh", "ms-rdp", "dns", "smtp", "ms-ds-smb",
        "mssql-db", "mysql", "ntp", "telnet", "ftp", "postgres", "ldap"]
ACTIONS = ["allow", "deny"]
TEAMS = ["netops", "secops", "appteam-crm", "appteam-erp", "dba", "vendor"]


def _subnet() -> str:
    return f"10.{rng.randint(0, 254)}.{rng.randint(0, 254)}.0/24"


def _host() -> str:
    return f"10.{rng.randint(0, 254)}.{rng.randint(0, 254)}.{rng.randint(1, 254)}"


def _public_ip() -> str:
    return f"{rng.choice([13, 20, 34, 52, 104, 143, 172, 185, 203])}." \
           f"{rng.randint(0, 254)}.{rng.randint(0, 254)}.{rng.randint(1, 254)}"


def build_rules() -> list[dict]:
    rules = []
    for i in range(1, RULE_COUNT + 1):
        svc, svc_name = rng.choice(SERVICES)
        src_zone = rng.choice(ZONES)
        dst_zone = rng.choice([z for z in ZONES if z != src_zone])
        rules.append({
            "rule_id": f"R{i:05d}",
            "name": f"{src_zone}-to-{dst_zone}-{svc_name.lower()}-{i}",
            "enabled": rng.random() > 0.06,
            "action": rng.choices(ACTIONS, weights=[7, 3])[0],
            "source_zone": src_zone,
            "source_address": [_subnet() for _ in range(rng.randint(1, 3))],
            "destination_zone": dst_zone,
            "destination_address": [_subnet() for _ in range(rng.randint(1, 2))],
            "service": [svc],
            "application": [rng.choice(APPS)],
            "logging": rng.random() > 0.15,
            "created": (datetime(2019, 1, 1) + timedelta(days=rng.randint(0, 2600))).strftime("%Y-%m-%d"),
            "last_hit": (datetime(2026, 1, 1) + timedelta(days=rng.randint(0, 200))).strftime("%Y-%m-%d") if rng.random() > 0.2 else None,
            "owner": rng.choice(TEAMS),
            "description": f"Auto-migrated rule {i} from legacy platform",
        })

    # ---- Planted findings. Positions are deterministic under SEED. ----
    planted = [
        {  # F1: any/any permit, the classic
            "rule_id": "R00666", "name": "TEMP-troubleshooting-DO-NOT-REMOVE",
            "enabled": True, "action": "allow",
            "source_zone": "any", "source_address": ["any"],
            "destination_zone": "any", "destination_address": ["any"],
            "service": ["any"], "application": ["any"], "logging": False,
            "created": "2021-03-14", "last_hit": "2026-08-01",
            "owner": "netops",
            "description": "Temporary rule for P1 incident bridge, remove after change CHG0042311",
        },
        {  # F2: RDP open to the internet
            "rule_id": "R01037", "name": "vendor-remote-support-rdp",
            "enabled": True, "action": "allow",
            "source_zone": "untrust", "source_address": ["0.0.0.0/0"],
            "destination_zone": "trust", "destination_address": ["10.20.30.15/32"],
            "service": ["tcp/3389"], "application": ["ms-rdp"], "logging": True,
            "created": "2022-11-02", "last_hit": "2026-07-29",
            "owner": "vendor",
            "description": "Sapphire Systems remote support access, contract ended 2024",
        },
        {  # F3: telnet permitted to mgmt zone
            "rule_id": "R00913", "name": "legacy-switch-mgmt-telnet",
            "enabled": True, "action": "allow",
            "source_zone": "trust", "source_address": ["10.0.0.0/8"],
            "destination_zone": "mgmt", "destination_address": ["10.99.1.0/24"],
            "service": ["tcp/23"], "application": ["telnet"], "logging": False,
            "created": "2019-06-21", "last_hit": "2026-06-11",
            "owner": "netops",
            "description": "Legacy switch management, replacement project stalled",
        },
        {  # F4: SMB inbound from guest
            "rule_id": "R01155", "name": "guest-fileshare-access",
            "enabled": True, "action": "allow",
            "source_zone": "guest", "source_address": ["172.16.40.0/22"],
            "destination_zone": "trust", "destination_address": ["10.10.5.0/24"],
            "service": ["tcp/445"], "application": ["ms-ds-smb"], "logging": True,
            "created": "2020-02-10", "last_hit": None,
            "owner": "appteam-crm",
            "description": "Guest wifi to file server for contractor onboarding",
        },
        {  # F5: disabled deny that would have shadowed F2
            "rule_id": "R01036", "name": "block-inbound-rdp",
            "enabled": False, "action": "deny",
            "source_zone": "untrust", "source_address": ["any"],
            "destination_zone": "trust", "destination_address": ["any"],
            "service": ["tcp/3389"], "application": ["ms-rdp"], "logging": True,
            "created": "2022-10-30", "last_hit": None,
            "owner": "secops",
            "description": "Disabled during vendor onboarding, re-enable pending",
        },
    ]
    for p in planted:
        idx = int(p["rule_id"][1:]) - 1
        rules[idx] = p
    return rules


def build_logs(rules: list[dict]) -> list[dict]:
    logs = []
    base = datetime(2026, 8, 7, 0, 0, 0)
    suspect = "10.20.30.15"  # the RDP-exposed host, appears as a talker
    for i in range(LOG_COUNT):
        rule = rng.choice(rules)
        ts = base + timedelta(seconds=rng.randint(0, 86400))
        src = _public_ip() if rule["source_zone"] == "untrust" else _host()
        dst = suspect if rng.random() < 0.04 else _host()
        svc = rule["service"][0] if rule["service"][0] != "any" else "tcp/443"
        logs.append({
            "log_id": f"L{i:07d}",
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rule_id": rule["rule_id"],
            "action": rule["action"],
            "source_ip": src,
            "source_zone": rule["source_zone"],
            "destination_ip": dst,
            "destination_zone": rule["destination_zone"],
            "service": svc,
            "application": rule["application"][0],
            "bytes_sent": rng.randint(200, 900000),
            "bytes_received": rng.randint(200, 4000000),
            "session_duration_s": rng.randint(0, 7200),
        })
    # ---- Planted finding F6: a noisy external scanner. ----
    scanner = "185.220.101.42"
    for i in range(140):
        ts = base + timedelta(seconds=rng.randint(0, 86400))
        port = rng.choice(["tcp/3389", "tcp/22", "tcp/445", "tcp/1433", "tcp/23"])
        logs.append({
            "log_id": f"L{LOG_COUNT + i:07d}",
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rule_id": "R01037" if port == "tcp/3389" else f"R{rng.randint(1, RULE_COUNT):05d}",
            "action": "allow" if port == "tcp/3389" and rng.random() < 0.15 else "deny",
            "source_ip": scanner,
            "source_zone": "untrust",
            "destination_ip": suspect,
            "destination_zone": "trust",
            "service": port,
            "application": "unknown",
            "bytes_sent": rng.randint(60, 400),
            "bytes_received": rng.randint(0, 200),
            "session_duration_s": rng.randint(0, 4),
        })
    logs.sort(key=lambda x: x["timestamp"])
    return logs


def main() -> None:
    rules = build_rules()
    logs = build_logs(rules)
    out = {
        "device": {
            "hostname": "fw-edge-01",
            "model": "FabricGate 5200",
            "os_version": "FG-OS 11.4.2",
            "serial": "FG5200-AU-004417",
            "ha_state": "active",
            "last_config_change": "2026-08-05T22:14:03Z",
        },
        "rulebase": rules,
        "traffic_logs": logs,
    }
    dest = Path(__file__).resolve().parent.parent / "data" / "firewall.json"
    dest.write_text(json.dumps(out, separators=(",", ":")))
    size = dest.stat().st_size
    print(f"Wrote {dest} ({size/1024:.0f} KB, ~{size//4:,} tokens estimated)")


if __name__ == "__main__":
    main()
