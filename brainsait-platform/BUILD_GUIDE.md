# 🚀 BrainSAIT Platform - Build & Deploy Guide

## 🎯 Quick Start (Recommended)

```bash
cd /home/pi/brainsait-platform
./quick-start.sh
```

Select option **4** for full stack deployment.

---

## 📋 What's Been Fixed & Enhanced

### ✅ Critical Fixes Applied
1. **Chat Engine** - Added missing `datetime` import
2. **MCP Gateway** - Fixed OID mismatch (now 1.3.6.1.4.1.61026.8.1)
3. **Quick Start Script** - Updated to use modern `docker compose` syntax
4. **Template Engine** - Added PostgreSQL persistence and Redis caching
5. **All Services** - Verified Python syntax and imports

### ✨ Enhancements Added
1. **Template Engine**:
   - PostgreSQL database integration
   - Redis caching for performance
   - Proper dependency injection
   - Cache invalidation on updates

2. **Integration Layer**:
   - Cross-service communication via MCP Gateway
   - Multi-agent workflow orchestration
   - Enhanced error handling

3. **Testing**:
   - Integration test script
   - Enhancement validation script
   - Health check automation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    BrainSAIT Platform                    │
│                 (All Services Integrated)                │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │     MCP Gateway (8020)    │
        │   OID: ...61026.8.1       │
        └──┬────┬────┬────┬────┬───┘
           │    │    │    │    │
           ▼    ▼    ▼    ▼    ▼
        ┌───┬────┬────┬────┬────┐
        │OID│Tmpl│Chat│Pay │GIVC│
        │Reg│Eng │Eng │Eng │App │
        └───┴────┴────┴────┴────┘
           │
           ▼
    ┌──────────────────┐
    │   PostgreSQL     │
    │   Redis          │
    │   Ollama (opt)   │
    └──────────────────┘
```

---

## 📦 Services Overview

| Service | Port | OID | Status | Database | Cache |
|---------|------|-----|--------|----------|-------|
| OID Registry | 8010 | ...61026.2.1 | ✅ Ready | PostgreSQL | Redis |
| MCP Gateway | 8020 | ...61026.8.1 | ✅ Ready | - | Redis |
| Template Engine | 8030 | ...61026.6.1 | ✅ Enhanced | PostgreSQL | Redis |
| Chat Engine | 8040 | ...61026.7.1 | ✅ Fixed | PostgreSQL | Redis |
| Payment Engine | 8050 | ...61026.5.1 | ✅ Ready | In-memory* | - |
| GIVC Healthcare | 3000 | - | ✅ Ready | PostgreSQL | - |
| N8N Workflow | 5678 | - | ✅ Ready | PostgreSQL | - |
| Orchestrator | 8000 | - | ✅ Ready | PostgreSQL | Redis |

*Payment Engine will be enhanced with PostgreSQL in Phase 2

---

## 🔧 Build Steps

### 1. Prerequisites Check
```bash
# Check Docker
docker --version

# Check Docker Compose
docker compose version

# Check Python
python3 --version
```

### 2. Environment Setup
```bash
cd /home/pi/brainsait-platform

# Copy and edit environment variables
cp .env.example .env
nano .env  # Add your API keys
```

### 3. Build Services
```bash
# Build all Docker images
docker compose -f docker-compose.unified.yml build

# Or build individually
docker compose -f docker-compose.unified.yml build oid-registry
docker compose -f docker-compose.unified.yml build mcp-gateway
docker compose -f docker-compose.unified.yml build template-engine
docker compose -f docker-compose.unified.yml build chat-engine
docker compose -f docker-compose.unified.yml build payment-engine
```

### 4. Start Services
```bash
# Start infrastructure first
docker compose -f docker-compose.unified.yml up -d postgres redis

# Wait for databases
sleep 10

# Start core services
docker compose -f docker-compose.unified.yml up -d oid-registry mcp-gateway

# Start application services
docker compose -f docker-compose.unified.yml up -d \
  template-engine chat-engine payment-engine

# Start optional services
docker compose -f docker-compose.unified.yml up -d \
  givc-app n8n workflow-orchestrator ollama
```

### 5. Register Agents
```bash
# Wait for services to be ready
sleep 15

# Register all LINC agents
python3 scripts/register-agents.py
```

### 6. Verify Deployment
```bash
# Test integration
python3 scripts/test-services-integration.py

# Enhanced integration tests
python3 scripts/enhance-integrations.py
```

---

## 🧪 Testing

### Quick Health Check
```bash
# Check all services
for port in 8010 8020 8030 8040 8050; do
  echo "Testing port $port..."
  curl -s "http://localhost:$port/health" | jq
done
```

### Manual Testing

#### 1. OID Registry
```bash
# List all agents
curl http://localhost:8010/api/v1/registry/agents | jq

# Get specific agent
curl http://localhost:8010/api/v1/registry/agents/1.3.6.1.4.1.61026.6.1 | jq
```

#### 2. Template Engine
```bash
# Create a template
curl -X POST http://localhost:8030/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Medical Claim Template",
    "content": "Patient: {{name}}\nDiagnosis: {{diagnosis}}",
    "category": "healthcare",
    "tags": ["medical", "claim"]
  }' | jq

# Search templates
curl -X POST http://localhost:8030/api/v1/templates/search \
  -H "Content-Type: application/json" \
  -d '{"query": "medical", "limit": 10}' | jq
```

#### 3. Payment Engine
```bash
# Validate card
curl -X POST http://localhost:8050/api/v1/payments/validate \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "4111111111111111",
    "exp_month": 12,
    "exp_year": 26,
    "cvv": "123"
  }' | jq

# Get payment stats
curl http://localhost:8050/api/v1/payments/stats | jq
```

#### 4. MCP Gateway (Orchestration)
```bash
# Multi-agent workflow
curl -X POST http://localhost:8020/orchestrate \
  -H "Content-Type: application/json" \
  -d '[
    {
      "agent": "1.3.6.1.4.1.61026.6.1",
      "action": "search",
      "params": {"query": "claim", "limit": 1}
    },
    {
      "agent": "1.3.6.1.4.1.61026.5.1",
      "action": "validate",
      "params": {
        "card_number": "4111111111111111",
        "exp_month": 12,
        "exp_year": 26,
        "cvv": "123"
      }
    }
  ]' | jq
```

---

## 📊 Monitoring

### View Logs
```bash
# All services
docker compose -f docker-compose.unified.yml logs -f

# Specific service
docker compose -f docker-compose.unified.yml logs -f template-engine

# Last 100 lines
docker compose -f docker-compose.unified.yml logs --tail=100 chat-engine
```

### Check Status
```bash
# Service status
docker compose -f docker-compose.unified.yml ps

# Resource usage
docker stats
```

### Database Access
```bash
# PostgreSQL
docker compose -f docker-compose.unified.yml exec postgres \
  psql -U brainsait -d brainsait

# List databases
\l

# Connect to specific database
\c registry

# List tables
\dt
```

### Redis Access
```bash
# Redis CLI
docker compose -f docker-compose.unified.yml exec redis \
  redis-cli -a brainsait2024

# List all keys
KEYS *

# Get agent info
GET agent:1.3.6.1.4.1.61026.6.1
```

---

## 🔄 Common Operations

### Restart Service
```bash
docker compose -f docker-compose.unified.yml restart template-engine
```

### Rebuild Service
```bash
docker compose -f docker-compose.unified.yml up -d --build template-engine
```

### Stop All
```bash
docker compose -f docker-compose.unified.yml down
```

### Stop and Remove Volumes
```bash
docker compose -f docker-compose.unified.yml down -v
```

### Scale Service
```bash
docker compose -f docker-compose.unified.yml up -d --scale chat-engine=3
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose -f docker-compose.unified.yml logs service-name

# Check if port is already in use
sudo netstat -tulpn | grep PORT_NUMBER

# Remove old containers
docker compose -f docker-compose.unified.yml down
docker compose -f docker-compose.unified.yml up -d
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker compose -f docker-compose.unified.yml ps postgres

# Check PostgreSQL logs
docker compose -f docker-compose.unified.yml logs postgres

# Recreate database
docker compose -f docker-compose.unified.yml down
docker volume rm brainsait-platform_postgres-data
docker compose -f docker-compose.unified.yml up -d postgres
```

### Redis Connection Issues
```bash
# Check Redis
docker compose -f docker-compose.unified.yml exec redis redis-cli ping

# With password
docker compose -f docker-compose.unified.yml exec redis \
  redis-cli -a brainsait2024 ping
```

---

## 🎯 Next Steps

### Phase 2 Enhancements (This Week)
- [ ] Add real Stripe integration to Payment Engine
- [ ] Implement PostgreSQL persistence for Payment Engine
- [ ] Add Anthropic Claude support to Chat Engine
- [ ] Implement streaming responses in Chat Engine
- [ ] Add function calling for agent integration
- [ ] Set up Prometheus/Grafana monitoring

### Phase 3 Production (Next Week)
- [ ] Add JWT authentication
- [ ] Implement API rate limiting
- [ ] Set up HTTPS/TLS
- [ ] Configure load balancing
- [ ] Add comprehensive logging
- [ ] Deploy to production environment

---

## 📚 Documentation

- **API Docs**: http://localhost:8010/docs (FastAPI auto-docs)
- **Integration Guide**: `/home/pi/brainsait-platform/INTEGRATION.md`
- **Audit Report**: `/home/pi/brainsait-platform/AUDIT_REPORT.md`
- **README**: `/home/pi/brainsait-platform/README.md`

---

## 🆘 Support

### Check Service Health
All services expose a `/health` endpoint:
- http://localhost:8010/health - OID Registry
- http://localhost:8020/health - MCP Gateway
- http://localhost:8030/health - Template Engine
- http://localhost:8040/health - Chat Engine
- http://localhost:8050/health - Payment Engine

### Get Help
```bash
# Run diagnostics
docker compose -f docker-compose.unified.yml ps
docker compose -f docker-compose.unified.yml logs --tail=50

# Check network
docker network ls
docker network inspect brainsait-platform_brainsait-network
```

---

**Built with ❤️ by the BrainSAIT Team**  
**Version:** 1.0.0  
**Last Updated:** October 27, 2025
