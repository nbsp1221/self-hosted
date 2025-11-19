# LiteLLM Proxy Server

🌐 **Standardized proxy server for accessing 100+ LLM providers**

LiteLLM provides a unified API interface for interacting with multiple LLM providers including OpenAI, Anthropic, Cohere, and many more.

## 🚀 Quick Start

### 1. ⚙️ Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file to set your secure credentials.

💡 **Generate Secure Keys:**
```bash
# For database passwords
openssl rand -base64 32

# For LiteLLM API keys
openssl rand -hex 32
```

### 2. 🚀 Launch Services

Start PostgreSQL and LiteLLM:

```bash
docker compose up -d
```

### 3. 🌐 Setup Caddy Reverse Proxy

This service uses Caddy for HTTPS/SSL termination. Create the external network:

```bash
docker network create caddy-network
```

Configure your Caddy reverse proxy to point to `http://litellm:4000`.

Example Caddyfile:
```
your-domain.com {
    reverse_proxy litellm:4000
}
```

### 4. 🎯 Access LiteLLM

Once everything is running and Caddy is configured:

- **🌐 LiteLLM API**: `https://your-domain.com`
- **📊 Admin Dashboard**: `https://your-domain.com/ui`

Login to the admin dashboard using the credentials set in your `.env` file (`LITELLM_UI_USERNAME` and `LITELLM_UI_PASSWORD`).

**Note**: LiteLLM is not directly exposed on localhost. Access is only available through your Caddy reverse proxy for security.

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker compose logs -f

# LiteLLM only
docker compose logs -f litellm

# PostgreSQL only
docker compose logs -f postgres
```

### Stop Services

```bash
docker compose down
```

### Restart Services

```bash
docker compose restart
```

### Upgrade to Latest Version

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose down
docker compose up -d
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file to configure:

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: Database name for LiteLLM
- `LITELLM_PORT`: LiteLLM service port (default: 4000)
- `LITELLM_MASTER_KEY`: Master API key for LiteLLM
- `LITELLM_SALT_KEY`: Salt key for encrypting credentials
- `LITELLM_UI_USERNAME`: Admin dashboard username
- `LITELLM_UI_PASSWORD`: Admin dashboard password

### LiteLLM Settings

Modify `litellm-config.yaml` to customize:

- Logging levels
- Retry behavior
- Caching settings
- User tracking

## 🔗 Adding LLM Providers

1. Access the admin dashboard at `https://your-domain.com/ui`
2. Navigate to **Models** or **Providers** section
3. Add your API keys for various providers (OpenAI, Anthropic, etc.)
4. Configure model routing as needed

## 📊 Architecture

This setup includes:

- **PostgreSQL 17**: Persistent database for storing model configurations, API keys, and usage data
- **LiteLLM Proxy**: Main service providing standardized API access
- **Internal Networks**:
  - `litellm-network`: Secure isolated network for database communication
  - `caddy-network`: External network for Caddy reverse proxy integration

## 🔒 Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use strong, randomly generated passwords and keys
- The PostgreSQL database is only accessible within the Docker network
- LiteLLM is NOT directly exposed to the host - access only through Caddy reverse proxy
- Always use HTTPS in production via Caddy with valid SSL certificates
- The `caddy-network` must be created before starting services

## 📝 Important Notes

- All data is persisted in Docker volumes
- Database data survives container restarts
- LiteLLM configuration is stored in the database
- Health checks ensure services are running correctly

## 📚 Resources

- **LiteLLM Documentation**: [https://docs.litellm.ai/](https://docs.litellm.ai/)
- **Supported Providers**: [https://docs.litellm.ai/docs/providers](https://docs.litellm.ai/docs/providers)
- **API Reference**: [https://docs.litellm.ai/docs/api](https://docs.litellm.ai/docs/api)

## 🐛 Troubleshooting

### Services won't start

**Network not found error:**
```bash
# Create the caddy-network if it doesn't exist
docker network create caddy-network
```

**Check if internal port 5432 is in use (PostgreSQL):**
```bash
lsof -i :5432
```

### Database connection errors

Ensure PostgreSQL is healthy:
```bash
docker compose ps
docker compose logs postgres
```

### Reset everything

⚠️ **Warning**: This will delete all data!
```bash
docker compose down -v
docker compose up -d
```

---

**LiteLLM Proxy Server** - 🌐 *One API for all LLMs*
