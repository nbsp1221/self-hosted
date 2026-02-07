#!/usr/bin/env python3
from __future__ import annotations

import os
import secrets
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _upsert_env_kv(path: Path, key: str, value: str) -> bool:
    """
    Insert or replace KEY=VALUE in a dotenv file.
    - Preserves unknown lines, comments, and ordering.
    - If the key exists but is empty (KEY=), it will be filled.
    Returns True if the file was modified.
    """
    original = _read_text(path)
    lines = original.splitlines(keepends=True) if original else []

    def parse_kv(line: str) -> tuple[str | None, str | None]:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            return None, None
        k, v = s.split("=", 1)
        return k.strip(), v

    changed = False
    found = False
    out: list[str] = []
    for line in lines:
        k, v = parse_kv(line)
        if k == key:
            found = True
            # Only fill if empty; otherwise keep user's value.
            if v is None or v == "":
                out.append(f"{key}={value}\n")
                changed = True
            else:
                out.append(line)
            continue
        out.append(line)

    if not found:
        # Ensure trailing newline.
        if out and not out[-1].endswith("\n"):
            out[-1] = out[-1] + "\n"
        out.append(f"{key}={value}\n")
        changed = True

    if changed:
        path.write_text("".join(out), encoding="utf-8")
    return changed


def _run(cmd: list[str]) -> None:
    # Let Docker/Compose print their own error messages.
    subprocess.run(cmd, cwd=str(ROOT), check=True)


def main() -> int:
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "").strip()
    if not token:
        token = secrets.token_hex(32)

    # Ensure state dirs exist (safe even if .gitkeep already created them).
    (ROOT / ".openclaw").mkdir(parents=True, exist_ok=True)
    (ROOT / ".openclaw" / "workspace").mkdir(parents=True, exist_ok=True)

    _upsert_env_kv(ENV_PATH, "OPENCLAW_GATEWAY_TOKEN", token)

    # Baseline onboarding (non-interactive).
    # - Skips channels: bot tokens (Telegram/Discord/etc) are user-provided.
    # - Skips skills/UI and health: keep setup fast and avoid requiring a running gateway.
    _run(
        [
            "docker",
            "compose",
            "run",
            "--rm",
            "openclaw-cli",
            "onboard",
            "--non-interactive",
            "--accept-risk",
            "--mode",
            "local",
            "--gateway-bind",
            "lan",
            "--gateway-port",
            "18789",
            "--gateway-auth",
            "token",
            "--gateway-token",
            token,
            "--skip-channels",
            "--skip-skills",
            "--skip-ui",
            "--skip-health",
            "--no-install-daemon",
        ]
    )

    # Start the gateway.
    _run(["docker", "compose", "up", "-d", "openclaw-gateway"])

    print("")
    print("Next steps:")
    print("")
    print("  # Control UI")
    print(
        "  Open your reverse proxy URL (e.g. https://openclaw.your-domain) and paste OPENCLAW_GATEWAY_TOKEN."
    )
    print("")
    print("  # Configure model/provider (required)")
    print(
        "  docker compose exec openclaw-gateway node dist/index.js configure --section model"
    )
    print("")
    print("  # Configure web tools (optional)")
    print(
        "  docker compose exec openclaw-gateway node dist/index.js configure --section web"
    )
    print("")
    print("  # Channels (interactive wizard)")
    print("  docker compose run --rm openclaw-cli channels add")
    print("")
    print("  # Channels (non-interactive examples)")
    print(
        "  docker compose run --rm openclaw-cli channels add --channel telegram --token <token>"
    )
    print(
        "  docker compose run --rm openclaw-cli channels add --channel discord --token <token>"
    )
    print(
        "  docker compose run --rm openclaw-cli channels login  # WhatsApp QR (optional)"
    )
    print("")
    print("  # Device pairing (if the UI says 'pairing required')")
    print("  docker compose exec openclaw-gateway node dist/index.js devices list")
    print(
        "  docker compose exec openclaw-gateway node dist/index.js devices approve <requestId>"
    )
    print("")
    print(
        "  # Tip: Control UI also supports channel setup (Channels tab), including QR-based logins."
    )
    print("  docker compose logs -f openclaw-gateway")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        # Keep output minimal; Docker/Compose already printed the real error.
        returncode = e.returncode if isinstance(e.returncode, int) else 1
        raise SystemExit(returncode)
