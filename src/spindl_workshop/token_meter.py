"""Live token meter for the workshop server.

A transparent stdio proxy that sits between your MCP client and the
workshop server, counting an estimate of the tokens every MCP message
contributes to the model's context. The traffic itself is relayed
byte-for-byte untouched; accounting happens on a copy.

Two roles, one command:

Proxy (replaces ``spindl-workshop`` in your MCP client config)::

    spindl-workshop-meter --mode naive
    spindl-workshop-meter --mode spindl

Display (run in a terminal beside your client, e.g. on a projector)::

    spindl-workshop-meter watch

The proxy appends one JSON line per message to a meter log
(default: ~/.spindl-workshop/meter.jsonl, override with
SPINDL_METER_LOG). The watcher tails that file and renders a running
total plus the most recent tool calls. Token counts are the same
chars/4 estimate used throughout the workshop materials.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

DEFAULT_LOG = Path(
    os.environ.get("SPINDL_METER_LOG")
    or Path.home() / ".spindl-workshop" / "meter.jsonl"
)

CHARS_PER_TOKEN = 4


def _estimate_tokens(raw: bytes) -> int:
    return max(1, len(raw) // CHARS_PER_TOKEN)


class MeterLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def emit(self, record: dict) -> None:
        record["ts"] = round(time.time(), 3)
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with self._lock, open(self.path, "a", encoding="utf-8") as fh:
            fh.write(line)


# ---------------------------------------------------------------- proxy ----

def run_proxy(server_args: list[str], log_path: Path) -> int:
    log = MeterLog(log_path)
    mode = "naive"
    if "--mode" in server_args:
        try:
            mode = server_args[server_args.index("--mode") + 1]
        except IndexError:
            pass
    log.emit({"event": "start", "mode": mode})

    proc = subprocess.Popen(
        [sys.executable, "-m", "spindl_workshop.server", *server_args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        bufsize=0,
    )
    assert proc.stdin is not None and proc.stdout is not None

    # request id -> tool/method name, so responses can be attributed
    pending: dict[object, str] = {}
    pending_lock = threading.Lock()

    def client_to_server() -> None:
        while True:
            line = sys.stdin.buffer.readline()
            if not line:
                try:
                    proc.stdin.close()
                except OSError:
                    pass
                return
            proc.stdin.write(line)
            proc.stdin.flush()
            try:
                msg = json.loads(line)
                method = msg.get("method", "")
                label = method
                if method == "tools/call":
                    label = msg.get("params", {}).get("name", "tools/call")
                if "id" in msg and method:
                    with pending_lock:
                        pending[msg["id"]] = label
                log.emit(
                    {
                        "dir": "in",
                        "tokens": _estimate_tokens(line),
                        "label": label or "notification",
                    }
                )
            except (json.JSONDecodeError, AttributeError):
                log.emit({"dir": "in", "tokens": _estimate_tokens(line), "label": "?"})

    def server_to_client() -> None:
        while True:
            line = proc.stdout.readline()
            if not line:
                return
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
            label = "?"
            try:
                msg = json.loads(line)
                if "id" in msg and "method" not in msg:
                    with pending_lock:
                        label = pending.pop(msg["id"], "response")
                else:
                    label = msg.get("method", "notification")
            except (json.JSONDecodeError, AttributeError):
                pass
            log.emit({"dir": "out", "tokens": _estimate_tokens(line), "label": label})

    t_in = threading.Thread(target=client_to_server, daemon=True)
    t_out = threading.Thread(target=server_to_client, daemon=True)
    t_in.start()
    t_out.start()
    t_out.join()
    try:
        proc.terminate()
    except OSError:
        pass
    return proc.wait()


# --------------------------------------------------------------- watcher ---

def _load_session(log_path: Path) -> tuple[str, int, int, list[tuple[str, int]]]:
    """Aggregate records since the most recent 'start' marker."""
    mode = "?"
    total_out = 0
    total_in = 0
    calls: list[tuple[str, int]] = []
    if not log_path.exists():
        return mode, total_out, total_in, calls
    session: list[dict] = []
    with open(log_path, encoding="utf-8") as fh:
        for raw in fh:
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if rec.get("event") == "start":
                session = [rec]
            else:
                session.append(rec)
    for rec in session:
        if rec.get("event") == "start":
            mode = rec.get("mode", "?")
        elif rec.get("dir") == "out":
            total_out += rec.get("tokens", 0)
            calls.append((rec.get("label", "?"), rec.get("tokens", 0)))
        elif rec.get("dir") == "in":
            total_in += rec.get("tokens", 0)
    return mode, total_out, total_in, calls


def run_watch(log_path: Path, once: bool = False) -> int:
    try:
        while True:
            mode, total_out, total_in, calls = _load_session(log_path)
            if not once:
                sys.stdout.write("\x1b[2J\x1b[H")  # clear screen, home
            print("SPINDL WORKSHOP TOKEN METER")
            print(f"server mode: {mode}    log: {log_path}")
            print()
            print(f"  tokens into model context (est.):  {total_out:>10,}")
            print(f"  tokens sent by client (est.):      {total_in:>10,}")
            print()
            print("  recent server responses:")
            for label, tokens in calls[-10:]:
                print(f"    {label:<28} {tokens:>10,}")
            if not calls:
                print("    (waiting for traffic)")
            sys.stdout.flush()
            if once:
                return 0
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0


# ------------------------------------------------------------------ main ---

def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0] == "watch":
        parser = argparse.ArgumentParser(prog="spindl-workshop-meter watch")
        parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
        parser.add_argument("--once", action="store_true", help=argparse.SUPPRESS)
        args = parser.parse_args(argv[1:])
        raise SystemExit(run_watch(args.log, once=args.once))

    parser = argparse.ArgumentParser(
        prog="spindl-workshop-meter",
        description="Token-metering stdio proxy for the workshop server. "
        "All arguments other than --log are passed through to spindl-workshop.",
    )
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    args, passthrough = parser.parse_known_args(argv)
    raise SystemExit(run_proxy(passthrough, args.log))


if __name__ == "__main__":
    main()
