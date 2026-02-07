# OpenClaw (Docker, custom image)

This setup runs OpenClaw in Docker using a thin custom image that is based on
the upstream image (`ghcr.io/openclaw/openclaw:main`) but bakes in a larger set
of CLI tools (for example `gh`, `jq`, `rg`) so the agent can work smoothly.

## Why this layout

- Persistent data lives on the host under `./.openclaw/` so container recreation is
  safe and expected.
- We still keep the compose file minimal and configurable via `.env`.

## Quick start

1. Ensure the external network exists (one-time):

```bash
docker network inspect caddy-network >/dev/null 2>&1 || docker network create caddy-network
```

2. Run the setup script (creates/updates `.env`, writes minimal gateway config, starts the gateway):

```bash
python3 setup.py
```

## After `setup.py`: what to do next

`setup.py` intentionally does only the "bootstrap" onboarding:

- It creates/updates `./.env` (gateway token)
- It writes a minimal OpenClaw config under `./.openclaw/`
- It starts the gateway container

To actually *use* OpenClaw, you typically still need:

- A model/provider (OpenAI/Anthropic/etc)
- Optional: web search key (Brave Search) for `web_search`
- One or more chat channels (Telegram/Discord/WhatsApp/etc)

### 1) Open the Control UI

- Use your reverse proxy URL (example: `https://openclaw.your-domain`).
- Paste the gateway token from `./.env` (`OPENCLAW_GATEWAY_TOKEN`).

Note: With the current `compose.yaml`, ports are not published to the host. This is
intentional. Access should go through your reverse proxy on `caddy-network`.

### 2) Configure a model/provider (required)

Run the interactive configure wizard from the gateway container (so `127.0.0.1:18789`
probes work inside Docker without host port publishing):

```bash
docker compose exec openclaw-gateway node dist/index.js configure --section model
```

If you want to do multiple sections at once:

```bash
docker compose exec openclaw-gateway node dist/index.js configure --section model --section web
```

### 3) Configure web tools (optional but recommended)

`web_fetch` works without a key, but `web_search` requires a Brave Search API key.
Recommended path (stores `tools.web.search.apiKey` in config):

```bash
docker compose exec openclaw-gateway node dist/index.js configure --section web
```

Alternative: set `BRAVE_API_KEY` in the gateway environment (not wired by default in this stack).

Docs: https://docs.openclaw.ai/tools/web

### 4) Set up channels

Interactive wizard (recommended; prompts for channel selection + required fields):

```bash
docker compose run --rm openclaw-cli channels add
```

Non-interactive examples:

```bash
docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"
docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
```

WhatsApp (QR):

```bash
docker compose run --rm openclaw-cli channels login
```

Tip: The Control UI also supports channel setup (Channels tab), including QR-based logins.

Docs: https://docs.openclaw.ai/channels

## Health check

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

## Device pairing (if required)

If the Control UI shows "unauthorized" or "pairing required" (close code 1008),
list and approve pending devices:

```bash
docker compose exec openclaw-gateway node dist/index.js devices list
docker compose exec openclaw-gateway node dist/index.js devices approve <requestId>
```

## Token consistency (important)

The onboarding wizard writes a token to `./.openclaw/openclaw.json`
(`gateway.auth.token`). The gateway reads `OPENCLAW_GATEWAY_TOKEN` from `.env`.
If those two values differ, the CLI will log `token_mismatch` and fail to
connect.

If you already onboarded with a different token, resync with:

```bash
docker compose run --rm openclaw-cli \
  config set gateway.auth.token "$OPENCLAW_GATEWAY_TOKEN"
```

## Configuration

- This stack intentionally binds the gateway with `--bind lan` (see `openclaw/compose.yaml`).
  - This is required for reverse-proxy access from other containers on `caddy-network`.
  - If you change it to loopback, your reverse proxy will not be able to reach the gateway.
- `OPENCLAW_GATEWAY_TOKEN` is required for access control in this stack (the setup script generates it
  and keeps `./.env` and `./.openclaw/openclaw.json` in sync).

## Data persistence

The following host paths are mounted into the containers:

- `./.openclaw` → `/home/node/.openclaw`
- `./.openclaw/workspace` → `/home/node/.openclaw/workspace`

This mirrors the official guidance: long-lived state belongs on the host and
should persist across restarts.

## Notes on the custom image

- The upstream `docker-setup.sh` script is optimized for local builds from the
  OpenClaw repo. Here, we keep a small wrapper `Dockerfile` and let Compose
  build the image.
- The `Dockerfile` installs additional OS packages at build time. If you need
  more tools, add them there and rebuild.
- To pick up upstream `:main` updates, rebuild with:

```bash
docker compose build --pull
docker compose up -d
```
