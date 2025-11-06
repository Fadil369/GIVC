# 🚀 BrainSAIT Platform - Quick Start Card

## ⚡ Fastest Way to Deploy

```bash
cd /home/pi/brainsait-platform
./quick-start.sh
# Select option 4 (Full Stack)
```

---

## 🔗 Service URLs (After Deployment)

| Service | URL | API Docs |
|---------|-----|----------|
| OID Registry | http://localhost:8010 | http://localhost:8010/docs |
| MCP Gateway | http://localhost:8020 | http://localhost:8020/docs |
| Template Engine | http://localhost:8030 | http://localhost:8030/docs |
| Chat Engine | http://localhost:8040 | http://localhost:8040/docs |
| Payment Engine | http://localhost:8050 | http://localhost:8050/docs |
| GIVC Healthcare | http://localhost:3000 | - |
| N8N Workflow | http://localhost:5678 | - |
| Orchestrator | http://localhost:8000 | - |

---

## ✅ Health Check (One Command)

```bash
for p in 8010 8020 8030 8040 8050; do curl -s http://localhost:$p/health | jq -r '"\(.service): \(.status)"'; done
```

---

## 🛠️ Common Commands

### Start Everything
```bash
docker compose -f docker-compose.unified.yml up -d
```

### Stop Everything
```bash
docker compose -f docker-compose.unified.yml down
```

### View Logs
```bash
docker compose -f docker-compose.unified.yml logs -f
```

### Restart Service
```bash
docker compose -f docker-compose.unified.yml restart SERVICE_NAME
```

---

## 🔍 Quick Tests

### Test Agent Registry
```bash
curl http://localhost:8010/api/v1/registry/agents | jq
```

### Test Template Search
```bash
curl -X POST http://localhost:8030/api/v1/templates/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 5}' | jq
```

### Test Multi-Agent Workflow
```bash
curl -X POST http://localhost:8020/orchestrate \
  -H "Content-Type: application/json" \
  -d '[{"agent": "1.3.6.1.4.1.61026.6.1", "action": "search", "params": {"query": "test"}}]' | jq
```

---

## 📚 Documentation Files

- `DEPLOYMENT_READY.md` - Deployment status & overview
- `BUILD_GUIDE.md` - Complete build instructions
- `AUDIT_REPORT.md` - Audit findings & fixes
- `INTEGRATION.md` - Service integration guide
- `README.md` - Platform overview

---

## 🆘 Troubleshooting

**Service not starting?**
```bash
docker compose -f docker-compose.unified.yml logs SERVICE_NAME
```

**Need to rebuild?**
```bash
docker compose -f docker-compose.unified.yml up -d --build SERVICE_NAME
```

**Database issues?**
```bash
docker compose -f docker-compose.unified.yml restart postgres
```

---

## 📊 Status: ✅ READY FOR DEPLOYMENT

**All services audited, enhanced, and production-ready!**
