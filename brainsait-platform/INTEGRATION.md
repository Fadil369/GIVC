# 🧠 BrainSAIT Platform - Service Integration Guide

## ✅ All Services Completed

### 1. OID Registry Service
- **OID**: 1.3.6.1.4.1.61026.2.1
- **Port**: 8010
- **Purpose**: Central agent registry and service discovery
- **Status**: ✅ Complete
- **Features**:
  - Agent registration and lookup
  - OID management
  - Health monitoring
  - RESTful API

### 2. MCP Gateway Service
- **OID**: 1.3.6.1.4.1.61026.8.1
- **Port**: 8020
- **Purpose**: Message routing and orchestration between agents
- **Status**: ✅ Complete
- **Features**:
  - Message routing
  - Workflow orchestration
  - Agent communication
  - Load balancing

### 3. Template Engine (TemplateLINC)
- **OID**: 1.3.6.1.4.1.61026.6.1
- **Port**: 8030
- **Purpose**: Template management with Notion integration
- **Status**: ✅ Complete
- **Features**:
  - Notion API integration
  - Template CRUD operations
  - Search and filtering
  - Template analysis
  - Sync from Notion databases

### 4. Chat Engine (ChatLINC)
- **OID**: 1.3.6.1.4.1.61026.7.1
- **Port**: 8040
- **Purpose**: AI-powered chat with WebSocket support
- **Status**: ✅ Complete
- **Features**:
  - WebSocket real-time chat
  - OpenAI/Anthropic integration
  - Session management
  - Context awareness
  - Multi-agent coordination

### 5. Payment Engine (PaymentLINC)
- **OID**: 1.3.6.1.4.1.61026.5.1
- **Port**: 8050
- **Purpose**: Multi-gateway payment processing
- **Status**: ✅ Complete
- **Features**:
  - Stripe integration
  - Mada (Saudi Arabia) support
  - STC Pay integration
  - Card validation (Luhn algorithm)
  - Refund processing
  - Payment statistics

## 🔗 Service Integration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP Gateway (8020)                      │
│              Routes messages between agents                  │
└─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬────────────┘
      │     │     │     │     │     │     │     │
      ▼     ▼     ▼     ▼     ▼     ▼     ▼     ▼
   ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │OID │ │NPHIES│Claim│Tmpl│Chat│Pay │N8N │GIVC│
   │8010│ │     │8030│8030│8040│8050│5678│3000│
   └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘
      │
      ▼
   ┌──────────────────────────────────────────────────────┐
   │  Shared Infrastructure                                │
   │  • PostgreSQL (Multi-DB: givc, workflow, registry)   │
   │  • Redis (Caching & Message Queue)                   │
   │  • Ollama (Local LLM)                                │
   └──────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Core Services Only
```bash
cd /home/pi/brainsait-platform
./quick-start.sh
# Select option 1
```

### Option 2: All New Services
```bash
cd /home/pi/brainsait-platform
./quick-start.sh
# Select option 2
```

### Option 3: Full Stack
```bash
cd /home/pi/brainsait-platform
./quick-start.sh
# Select option 4
```

## 🧪 Testing Integration

### 1. Check Service Health
```bash
# Test all services
for port in 8010 8020 8030 8040 8050; do
  echo "Testing port $port..."
  curl -s "http://localhost:$port/health" | jq
done
```

### 2. Run Integration Tests
```bash
cd /home/pi/brainsait-platform
python3 scripts/test-services-integration.py
```

### 3. Register All Agents
```bash
python3 scripts/register-agents.py
```

## 📊 Service Dependencies

```yaml
Services:
  oid-registry:
    depends_on: [postgres, redis]
    
  mcp-gateway:
    depends_on: [oid-registry, redis]
    
  template-engine:
    depends_on: [oid-registry]
    
  chat-engine:
    depends_on: [mcp-gateway, postgres]
    
  payment-engine:
    depends_on: [oid-registry]
    
  givc-app:
    depends_on: [postgres, redis, mcp-gateway]
    
  n8n:
    depends_on: [postgres]
    
  workflow-orchestrator:
    depends_on: [redis, postgres, mcp-gateway]
```

## 🔧 Environment Variables Required

### Core Services
```bash
POSTGRES_USER=brainsait
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
```

### Template Engine
```bash
NOTION_API_KEY=secret_your-notion-key
NOTION_DATABASE_ID=your-database-id
```

### Chat Engine
```bash
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key
```

### Payment Engine
```bash
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
MADA_API_KEY=your-mada-key
STC_PAY_API_KEY=your-stc-pay-key
```

## 📝 API Examples

### Template Engine

**Create Template:**
```bash
curl -X POST http://localhost:8030/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Claim Template",
    "content": "Template content here",
    "category": "healthcare",
    "tags": ["claim", "medical"]
  }'
```

**Search Templates:**
```bash
curl -X POST http://localhost:8030/api/v1/templates/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "claim",
    "category": "healthcare",
    "limit": 10
  }'
```

### Payment Engine

**Validate Card:**
```bash
curl -X POST http://localhost:8050/api/v1/payments/validate \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "4111111111111111",
    "exp_month": 12,
    "exp_year": 25,
    "cvv": "123"
  }'
```

**Process Payment:**
```bash
curl -X POST http://localhost:8050/api/v1/payments/charge \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 250.00,
    "currency": "SAR",
    "gateway": "stripe",
    "description": "Healthcare service payment"
  }'
```

### Chat Engine

**WebSocket Chat:**
```javascript
const ws = new WebSocket('ws://localhost:8040/chat/session123');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Help me submit a claim",
    context: {"patient_id": "12345"}
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('AI:', response.content);
};
```

## 🔄 Service Communication Patterns

### 1. Direct API Call
```
Client → Service API → Response
```

### 2. Via MCP Gateway
```
Client → MCP Gateway → Agent Router → Service → Response
```

### 3. Orchestrated Workflow
```
Client → MCP Gateway → [Service1 → Service2 → Service3] → Aggregated Response
```

### 4. Event-Driven
```
Service1 → Redis Queue → Service2 → Redis Queue → Service3
```

## 🎯 Next Steps

1. **Start Services**: Run `./quick-start.sh`
2. **Register Agents**: Run `python3 scripts/register-agents.py`
3. **Test Integration**: Run `python3 scripts/test-services-integration.py`
4. **Configure Nginx**: Set up reverse proxy (optional)
5. **Set up Monitoring**: Configure Prometheus/Grafana (optional)

## 📚 Additional Documentation

- [Architecture Overview](./README.md)
- [API Documentation](http://localhost:8010/docs) (after starting services)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)

---

**All services are now complete and ready for integration testing! 🎉**
