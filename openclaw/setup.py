#!/usr/bin/env python3

import os
import secrets
import subprocess
import shutil
from pathlib import Path
from typing import TypeAlias


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"

CliArg: TypeAlias = str | list[str] | tuple[str, ...]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def upsert_env_kv(path: Path, key: str, value: str) -> bool:
    """
    Insert or replace KEY=VALUE in a dotenv file.
    - Preserves unknown lines, comments, and ordering.
    - If the key exists but is empty (KEY=), it will be filled.
    Returns True if the file was modified.
    """
    original = read_text(path)
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


def dotenv_get(path: Path, key: str) -> str:
    for raw in read_text(path).splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip() != key:
            continue
        return v.strip()
    return ""


def run(*args: str) -> None:
    # Let Docker/Compose print their own error messages.
    subprocess.run(list(args), cwd=str(ROOT), check=True)


def flatten_cli_args(*args: CliArg) -> list[str]:
    out: list[str] = []
    for arg in args:
        if isinstance(arg, str):
            out.append(arg)
            continue
        if isinstance(arg, (list, tuple)):
            out.extend(arg)
            continue
        raise TypeError(f"Unsupported CLI arg type: {type(arg)!r}")
    return out


def run_cli(*args: CliArg) -> None:
    # Let Docker/Compose print their own error messages.
    subprocess.run(flatten_cli_args(*args), cwd=str(ROOT), check=True)


def openclaw(*args: CliArg) -> None:
    """Run an OpenClaw CLI command inside the compose one-off container."""
    run_cli("docker", "compose", "run", "--rm", "openclaw-cli", *args)


def openclaw_node(*args: CliArg) -> None:
    """Run a Node entrypoint inside the OpenClaw CLI container."""
    run_cli(
        "docker",
        "compose",
        "run",
        "--rm",
        ["--entrypoint", "node"],
        "openclaw-cli",
        *args,
    )


def main() -> int:
    if not ENV_PATH.exists() and ENV_EXAMPLE_PATH.exists():
        shutil.copyfile(ENV_EXAMPLE_PATH, ENV_PATH)

    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "").strip()
    if not token:
        token = dotenv_get(ENV_PATH, "OPENCLAW_GATEWAY_TOKEN")
    if not token:
        token = secrets.token_hex(32)

    # Ensure state dirs exist (safe even if .gitkeep already created them).
    (ROOT / ".openclaw").mkdir(parents=True, exist_ok=True)
    (ROOT / ".openclaw" / "workspace").mkdir(parents=True, exist_ok=True)

    # If `.env` exists and already has a value, keep it (stable token).
    upsert_env_kv(ENV_PATH, "OPENCLAW_GATEWAY_TOKEN", token)

    # ---------------------------
    # Onboard + config sync
    # ---------------------------
    # Baseline onboarding (non-interactive).
    # - Skips channels: bot tokens (Telegram/Discord/etc) are user-provided.
    # - Skips skills/UI and health: keep setup fast and avoid requiring a running gateway.
    openclaw(
        "onboard",
        "--non-interactive",
        "--accept-risk",
        ["--mode", "local"],
        ["--gateway-bind", "lan"],
        ["--gateway-port", "18789"],
        ["--gateway-auth", "token"],
        ["--gateway-token", token],
        "--skip-channels",
        "--skip-skills",
        "--skip-ui",
        "--skip-health",
        "--no-install-daemon",
    )

    # Keep CLI and gateway in sync with the compose-provided token.
    openclaw("config", "set", "gateway.auth.token", token)

    # ---------------------------
    # Browser (Playwright)
    # ---------------------------
    # Official Docker doc "power-user" path:
    # - persist `/home/node` (compose volume)
    # - set PLAYWRIGHT_BROWSERS_PATH (compose env)
    # - install chromium via playwright-core CLI (avoid npx override conflicts)
    #
    # Keep this idempotent: if chromium is already installed, it should be fast.
    openclaw_node("/app/node_modules/playwright-core/cli.js", "install", "chromium")

    # Default browser config for Docker: use the managed browser profile, headless.
    openclaw("config", "set", "browser.defaultProfile", "openclaw")
    openclaw("config", "set", "browser.headless", "true")
    openclaw("config", "set", "browser.noSandbox", "true")

    # Start the gateway.
    run_cli("docker", "compose", "up", "-d", "openclaw-gateway")
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
