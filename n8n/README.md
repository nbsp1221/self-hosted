<div align="center">

# 🚀 n8n Docker Setup

**Production-ready n8n workflow automation setup**

[![n8n](https://img.shields.io/badge/n8n-FF6D5A?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![Caddy](https://img.shields.io/badge/Caddy-1F88C0?style=for-the-badge&logo=caddy&logoColor=white)](https://caddyserver.com)

*Self-hosted workflow automation with Caddy reverse proxy*

[⚡ Quick Start](#-quick-start) •
[⚙️ Configuration](#️-configuration) •
[🌐 Caddy Setup](#-caddy-setup) •
[🛠️ Management](#️-management) •
[📚 Resources](#-resources)

</div>

---

## 🎯 What is this?

My personal Docker Compose setup for running n8n with supporting services, designed to work behind a Caddy reverse proxy for HTTPS access.

**Key Features**:

- **🔄 n8n**: Workflow automation platform
- **🗄️ PostgreSQL**: Persistent database storage
- **📦 Redis**: In-memory data store for caching and state management
- **🔒 HTTPS Ready**: Designed for Caddy reverse proxy
- **🏥 Health Checks**: Automatic service recovery
- **📦 Minimal Setup**: Just a few commands to get started

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/nbsp1221/n8n-docker-setup.git
cd n8n-docker-setup

# 2. Set up environment
cp .env.example .env

# 3. Create Caddy network
docker network create caddy-network

# 4. Start services
docker compose up -d
```

**Note**: n8n will be accessible via your Caddy reverse proxy, not directly via ports.

## 📋 Prerequisites

- Docker & Docker Compose
- Caddy reverse proxy setup (see [Caddy Setup](#-caddy-setup))
- Domain name (for HTTPS)

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_ROOT_USER` | PostgreSQL admin user | `postgres` |
| `POSTGRES_ROOT_PASSWORD` | PostgreSQL admin password | *set your own* |
| `N8N_POSTGRES_DB` | n8n database name | `n8n` |
| `N8N_POSTGRES_USER` | n8n database user | `n8n` |
| `N8N_POSTGRES_PASSWORD` | n8n database password | *set your own* |
| `N8N_PORT` | n8n internal port | `5678` |
| `N8N_PROTOCOL` | Protocol for n8n | `https` |
| `N8N_HOST` | Your domain name | `localhost` |
| `WEBHOOK_URL` | Webhook base URL | `https://localhost:5678` |
| `GENERIC_TIMEZONE` | Timezone setting | `Asia/Seoul` |

### Essential Setup

1. **Set secure passwords**:

   ```bash
   # Generate random passwords (replace with your own)
   openssl rand -base64 32
   ```

2. **Configure your domain**:

   ```bash
   # In .env file
   N8N_HOST=n8n.yourdomain.com
   WEBHOOK_URL=https://n8n.yourdomain.com
   ```

## 🌐 Caddy Setup

Since this setup requires Caddy reverse proxy, here's a basic Caddy configuration.

### Caddyfile Example

```caddy
n8n.yourdomain.com {
    reverse_proxy n8n:5678
}
```

### Docker Compose for Caddy

```yaml
services:
  caddy:
    image: caddy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
    networks:
      - caddy-network

networks:
  caddy-network:
    name: caddy-network
    external: true
```

## 🛠️ Management

### Stopping the Service

To stop the containers:

```bash
docker compose down
```

### Upgrading Services

To upgrade to the latest versions:

```bash
# Pull latest versions
docker compose pull

# Stop and remove older versions
docker compose down

# Start the containers
docker compose up -d
```

## 📚 Resources

- **[n8n Documentation](https://docs.n8n.io)** - Official workflow guides
- **[PostgreSQL Documentation](https://www.postgresql.org/docs)** - Database reference
- **[Redis Documentation](https://redis.io/docs/latest)** - In-memory data store
- **[Caddy Documentation](https://caddyserver.com/docs)** - Reverse proxy setup

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**⭐ Found this helpful? Give it a star!**

*Personal n8n setup for workflow automation*

[![GitHub stars](https://img.shields.io/github/stars/nbsp1221/n8n-docker-setup?style=social)](https://github.com/nbsp1221/n8n-docker-setup)

</div>
