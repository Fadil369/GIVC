# 🧠 BrainSAIT Unified Platform

**Complete integration of GIVC Healthcare, Agentic Workflows, and BrainSAIT Services**

OID Root: `1.3.6.1.4.1.61026`

## 🎯 What This Is

A unified, containerized platform that combines:

1. **GIVC Healthcare Platform** - Claims management, NPHIES integration
2. **Agentic Workflow System** - N8N automation, Ollama AI
3. **BrainSAIT Services** - Chat engine, template management, payment processing

All services communicate via the **MCP (Message Context Protocol) Gateway** and are registered in the central **OID Registry**.

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd /home/pi/brainsait-platform

# 2. Copy environment variables
cp .env.example .env
nano .env  # Add your API keys

# 3. Run quick start script
chmod +x quick-start.sh
./quick-start.sh

# 4. Access services
# OID Registry:     http://localhost:8010
# MCP Gateway:      http://localhost:8020
# Template Engine:  http://localhost:8030
# Chat Engine:      http://localhost:8040
# Payment Engine:   http://localhost:8050
# GIVC Healthcare:  http://localhost:3000
# N8N Workflow:     http://localhost:5678
```

## 📦 Architecture

```
┌─────────────────────────────────────────────────────┐
│             BrainSAIT Unified Platform               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ GIVC Health  │  │ Agentic      │                 │
│  │ (Existing)   │  │ Workflow     │                 │
│  │              │  │ (Existing)   │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                         │
│         └─────────┬───────┘                         │
│                   │                                 │
│         ┌─────────▼─────────┐                       │
│         │  MCP Gateway      │ (NEW)                 │
│         │  Agent Router     │                       │
│         └─────────┬─────────┘                       │
│                   │                                 │
│         ┌─────────▼─────────┐                       │
│         │  OID Registry     │ (NEW)                 │
│         │  Service Discovery│                       │
│         └───────────────────┘                       │
│                                                      │
│  ┌──────────────────────────────────────┐           │
│  │  New Services                        │           │
│  │  • Chat Engine (AI)                  │           │
│  │  • Template Engine (Notion)          │           │
│  │  • Payment Engine (Stripe/Mada)      │           │
│  │  • Analytics Engine                  │           │
│  └──────────────────────────────────────┘           │
│                                                      │
│  ┌──────────────────────────────────────┐           │
│  │  Shared Infrastructure               │           │
│  │  • PostgreSQL (multi-database)       │           │
│  │  • Redis (caching & queues)          │           │
│  │  • Ollama (local AI)                 │           │
│  └──────────────────────────────────────┘           │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 🔧 Services

### Core Services (NEW)

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| OID Registry | 8010 | Agent discovery & registry | ✅ Ready |
| MCP Gateway | 8020 | Message routing between agents | ✅ Ready |
| Template Engine | 8030 | Notion template management | ✅ Ready |
| Chat Engine | 8040 | AI chat with WebSocket | ✅ Ready |
| Payment Engine | 8050 | Multi-gateway payment processing | ✅ Ready |

### Existing Services (Integrated)

| Service | Port | Purpose | Integration |
|---------|------|---------|-------------|
| GIVC App | 3000 | Healthcare platform | ✅ Via MCP |
| N8N | 5678 | Workflow automation | ✅ Via MCP |
| Orchestrator | 8000 | Workflow orchestration | ✅ Via MCP |
| Ollama | 11434 | Local LLM | ✅ Direct |

### Infrastructure

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Multi-database (givc/workflow/registry) |
| Redis | 6379 | Caching & message queues |

## 🎮 Usage Examples

### 1. Register an Agent

```bash
curl -X POST http://localhost:8010/api/v1/registry/agents \
  -H "Content-Type: application/json" \
  -d '{
    "oid": "1.3.6.1.4.1.61026.4.2",
    "name": "claimlinc",
    "domain": "healthcare",
    "version": "1.0.0",
    "endpoints": {"rest": "http://localhost:3000/api/claims"},
    "capabilities": ["submit", "track"],
    "dependencies": []
  }'
```

### 2. List All Agents

```bash
curl http://localhost:8010/api/v1/registry/agents
```

### 3. Route a Message

```bash
curl -X POST http://localhost:8020/route \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "claimlinc",
    "to_agent": "nphieslinc",
    "type": "request",
    "payload": {"action": "validate", "claim_id": "123"}
  }'
```

### 4. Orchestrate Workflow

```bash
curl -X POST http://localhost:8020/orchestrate \
  -H "Content-Type: application/json" \
  -d '[
    {"agent": "nphieslinc", "action": "validate"},
    {"agent": "claimlinc", "action": "submit"},
    {"agent": "paymentlinc", "action": "charge"}
  ]'
```

### 5. Chat WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8040/chat/session123');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "How do I submit a claim?"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('AI:', data.content);
};
```

## 📁 Project Structure

```
brainsait-platform/
├── docker-compose.unified.yml    # Main orchestration file
├── .env.example                  # Environment template
├── quick-start.sh               # Setup script
│
├── services/                    # Microservices
│   ├── oid-registry/           # Agent registry
│   ├── mcp-gateway/            # Message router
│   └── chat-engine/            # AI chat service
│
├── database/                   # Database initialization
│   ├── init-multi-db.sh       # Multi-DB setup
│   └── schemas/               # SQL schemas
│
├── scripts/                   # Utility scripts
│   └── register-agents.py     # Register initial agents
│
├── nginx/                     # Reverse proxy config
│   ├── nginx.conf
│   └── conf.d/
│
└── monitoring/                # Observability
    ├── prometheus.yml
    └── grafana/
```

## 🔐 Environment Variables

Required in `.env`:

```bash
# Database
POSTGRES_USER=brainsait
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# AI
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-your-key

# Payments
STRIPE_SECRET_KEY=sk_test_your-key

# N8N
N8N_USER=admin
N8N_PASSWORD=your_password
```

## 🛠️ Development

```bash
# Start in development mode (with hot reload)
./quick-start.sh
# Select option 5

# View logs
docker-compose -f docker-compose.unified.yml logs -f [service-name]

# Rebuild a service
docker-compose -f docker-compose.unified.yml build [service-name]
docker-compose -f docker-compose.unified.yml up -d [service-name]

# Access database
docker exec -it brainsait-postgres psql -U brainsait -d registry

# Access Redis
docker exec -it brainsait-redis redis-cli -a brainsait2024
```

## 📊 Monitoring

```bash
# Check all service health
for port in 8010 8020 8040; do
  echo "Port $port:"
  curl -s "http://localhost:$port/health" | jq
done

# View Docker stats
docker stats

# Check logs for errors
docker-compose -f docker-compose.unified.yml logs --tail=100 | grep -i error
```

## 🧪 Testing

```bash
# Test OID Registry
cd services/oid-registry
pytest tests/

# Test MCP Gateway
cd services/mcp-gateway
pytest tests/

# Integration tests
python3 scripts/integration-tests.py
```

## 📚 API Documentation

- **OID Registry API**: http://localhost:8010/docs
- **MCP Gateway API**: http://localhost:8020/docs
- **Chat Engine API**: http://localhost:8040/docs

## 🚢 Deployment

### Production Deployment

```bash
# 1. Set production environment
export NODE_ENV=production

# 2. Build all services
docker-compose -f docker-compose.unified.yml build

# 3. Deploy
docker-compose -f docker-compose.unified.yml up -d

# 4. Verify
./scripts/health-check.sh
```

### Kubernetes Deployment

```bash
# Generate Kubernetes manifests
kompose convert -f docker-compose.unified.yml

# Apply to cluster
kubectl apply -f k8s/
```

## 🔄 Updates & Maintenance

```bash
# Pull latest changes
git pull origin main

# Rebuild changed services
docker-compose -f docker-compose.unified.yml build

# Rolling update
docker-compose -f docker-compose.unified.yml up -d --no-deps [service-name]

# Backup databases
./scripts/backup-databases.sh
```

## 🆘 Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose -f docker-compose.unified.yml logs [service-name]

# Check resource usage
docker stats

# Restart service
docker-compose -f docker-compose.unified.yml restart [service-name]
```

### Database connection issues

```bash
# Verify PostgreSQL is running
docker exec -it brainsait-postgres pg_isready

# Check database list
docker exec -it brainsait-postgres psql -U brainsait -c "\l"
```

### Agent not found

```bash
# Re-register agents
python3 scripts/register-agents.py

# Verify registration
curl http://localhost:8010/api/v1/registry/agents
```

## 📖 Additional Resources

- [Full Architecture Documentation](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Development Guide](./docs/DEVELOPMENT.md)

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📝 License

GPL-3.0 - See [LICENSE](./LICENSE)

## 👤 Author

**Dr. Mohamed Elfadil** - BrainSAIT LTD  
OID: 1.3.6.1.4.1.61026

---

**Built with ❤️ for integrated healthcare and AI workflows**
