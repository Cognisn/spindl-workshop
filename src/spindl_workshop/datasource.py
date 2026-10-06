"""Loads the committed firewall data set, cached for the process lifetime."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any


@lru_cache(maxsize=1)
def load_data() -> dict[str, Any]:
    """Read data/firewall.json packaged alongside the module.

    The file is included as package data (see pyproject.toml) so the server
    works identically whether installed from a git URL, a wheel, or a local
    checkout via uv.
    """
    ref = resources.files("spindl_workshop").joinpath("data/firewall.json")
    try:
        return json.loads(ref.read_text())
    except (FileNotFoundError, OSError):
        # Editable install or plain checkout: fall back to <repo-root>/data/
        repo_root = Path(__file__).resolve().parents[2]
        return json.loads((repo_root / "data" / "firewall.json").read_text())
