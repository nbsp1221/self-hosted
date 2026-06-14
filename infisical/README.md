# Infisical

Self-hosted Infisical behind the external Caddy network used by this repository.

This stack:

- runs Infisical with internal PostgreSQL and Redis
- joins the external Docker network `caddy-network`
- does not publish ports to the host
- expects your reverse proxy to route to `infisical:8080`

## Prerequisites

- Docker Engine
- Docker Compose v2
- External Docker network `caddy-network`
- External reverse proxy configuration that routes your Infisical domain to `infisical:8080`

Minimum resources from the upstream Docker Compose guide are 2 CPU cores, 4 GB
RAM, and 20 GB disk. Recommended baseline is 4 CPU cores, 8 GB RAM, and 50 GB+
SSD.

Create the shared proxy network once if needed:

```bash
docker network inspect caddy-network >/dev/null 2>&1 || docker network create caddy-network
```

## Quick Start

```bash
cd infisical
cp .env.example .env
chmod 600 .env
$EDITOR .env

docker compose up -d
docker compose ps
docker compose logs -f
```

## Generate Secrets

```bash
# ENCRYPTION_KEY, exactly 32 hex characters
openssl rand -hex 16

# AUTH_SECRET
openssl rand -base64 32

# POSTGRES_PASSWORD and REDIS_PASSWORD
# These are embedded in connection URLs, so keep them URL-safe.
openssl rand -hex 32
```

Keep `ENCRYPTION_KEY` backed up outside Infisical. Losing it can make stored
secrets unrecoverable even if the database is intact.

## Configuration Guidelines

- Set `SITE_URL` to the public HTTPS URL served by Caddy.
- The Infisical image uses the floating `latest` tag so `docker compose pull`
  can pick up new upstream releases. Review release notes before upgrades.
- Keep `ENCRYPTION_KEY`, `AUTH_SECRET`, `POSTGRES_PASSWORD`, and `REDIS_PASSWORD` long and random.
- Configure SMTP before relying on email invites, password resets, or account notifications.
- After the first admin user is created, disable public signups from the Infisical admin settings.

## Reverse Proxy

Example Caddyfile snippet:

```caddy
infisical.example.com {
  reverse_proxy infisical:8080
}
```

If you later assign a stable subnet to the proxy network, you can optionally set
`TRUSTED_PROXY_CIDRS` to that subnet. Do not hard-code the current auto-assigned
Docker subnet unless you also control it in network configuration.

## Operations

```bash
docker compose pull
docker compose up -d
docker compose logs -f
docker compose restart
docker compose down
```

## Verification

Validate the stack file:

```bash
docker compose config -q
```

Check database readiness:

```bash
docker compose exec -T postgres pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"
```

Check Redis readiness:

```bash
docker compose exec -T redis redis-cli ping
```

Check Infisical readiness:

```bash
docker compose exec -T infisical curl -fsS http://127.0.0.1:8080/api/status
```

## Data Persistence / Backups

Persistent data is stored in named Docker volumes:

- `infisical_postgres-data`
- `infisical_redis-data`

Back up PostgreSQL data and the `ENCRYPTION_KEY` before upgrades.

## References

- Project: https://github.com/Infisical/infisical
- Docker Compose docs: https://infisical.com/docs/self-hosting/deployment-options/docker-compose
- Environment variables: https://infisical.com/docs/self-hosting/configuration/envars
- Production hardening: https://infisical.com/docs/self-hosting/guides/production-hardening
