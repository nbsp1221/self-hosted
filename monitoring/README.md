# Monitoring

Prometheus-based monitoring stack for host and container visibility.

## Overview

This stack provides:

- Prometheus for metrics scraping and storage
- node-exporter for host-level metrics (CPU, memory, disk, filesystem, processes, systemd)
- cAdvisor for container-level metrics
- Grafana for dashboards and visualization

Current default scrape targets:

- `prometheus:9090` (self metrics)
- `node-exporter:9100` (host metrics)
- `cadvisor:8080` (container metrics)

## Architecture

- `prometheus`, `node-exporter`, and `cadvisor` run on `monitoring-network`
- `grafana` runs on `monitoring-network` and also joins external `caddy-network`
- Prometheus and Grafana data are persisted in named volumes

## Directory Layout

- `compose.yaml`: stack definition
- `.env.example`: environment variables for Grafana
- `prometheus/prometheus.yml`: scrape configuration
- `grafana/provisioning/`: datasource and dashboard provisioning
- `grafana/dashboards/`: dashboard JSON files loaded at startup

## Prerequisites

- Docker Engine
- Docker Compose v2 (`docker compose`)
- External reverse proxy network `caddy-network`

Create the external network once if needed:

```bash
docker network inspect caddy-network >/dev/null 2>&1 || docker network create caddy-network
```

## Quick Start

```bash
cd monitoring
cp .env.example .env
# edit .env before first run

docker compose up -d
docker compose ps
```

## Access

Grafana is intentionally exposed only through your reverse proxy.

- Upstream service: `grafana:3000` on `caddy-network`
- Default login user: `admin`
- Default login password: value of `GRAFANA_ADMIN_PASSWORD` in `.env`

## Verification

Check Prometheus scrape status from inside the stack:

```bash
docker compose exec -T prometheus wget -qO- \
  'http://127.0.0.1:9090/api/v1/query?query=up' | jq .
```

Expected: `prometheus`, `node-exporter`, and `cadvisor` appear with value `1`.

Check Grafana health:

```bash
docker compose exec -T grafana wget -qO- http://127.0.0.1:3000/api/health
```

## Default Dashboards

Provisioned at startup from `grafana/dashboards/`:

- `node-exporter-full.json`
- `cadvisor-dashboard.json`

Home dashboard path is controlled by:

- `GRAFANA_HOME_DASHBOARD_PATH` in `.env`

## Persistence

Named volumes:

- `prometheus-data` (`/prometheus`)
- `grafana-data` (`/var/lib/grafana`)

Inspect volume locations on host:

```bash
docker volume inspect prometheus-data
docker volume inspect grafana-data
```

## Operations

```bash
docker compose pull
docker compose up -d
docker compose logs -f
docker compose restart
docker compose down
```

Destructive reset (removes all monitoring history and Grafana state):

```bash
docker compose down -v
```
