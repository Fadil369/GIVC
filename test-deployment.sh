#!/bin/bash

echo "🧪 GIVC Platform Deployment Test"
echo "=================================="
echo ""

echo "1. Testing Local Frontend..."
if curl -s http://localhost/ | grep -q "GIVC Healthcare"; then
    echo "   ✅ Frontend responding"
else
    echo "   ❌ Frontend not responding"
fi

echo ""
echo "2. Testing Backend Health..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "   ✅ Backend healthy"
else
    echo "   ❌ Backend unhealthy"
fi

echo ""
echo "3. Testing API Status..."
if curl -s http://localhost:8000/api/v1/status | grep -q "nphies"; then
    echo "   ✅ API endpoints available"
else
    echo "   ❌ API not responding"
fi

echo ""
echo "4. Testing Database..."
if docker exec givc-postgres pg_isready -U givc > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL connected"
else
    echo "   ❌ PostgreSQL not connected"
fi

echo ""
echo "5. Testing Redis..."
if docker exec givc-redis redis-cli -a redis_pass ping | grep -q "PONG"; then
    echo "   ✅ Redis connected"
else
    echo "   ❌ Redis not connected"
fi

echo ""
echo "6. Testing Nginx Integration..."
if curl -s http://localhost/health | grep -q "healthy"; then
    echo "   ✅ Nginx proxying correctly"
else
    echo "   ❌ Nginx not proxying"
fi

echo ""
echo "7. Testing Public URL (DNS may take 2-5 min)..."
if curl -s -k https://givc.brainsait.com | grep -q "GIVC" 2>/dev/null; then
    echo "   ✅ Public URL accessible"
else
    echo "   ⏳ Public URL not yet propagated (try again in a few minutes)"
fi

echo ""
echo "=================================="
echo "Test complete!"
echo ""
echo "🌐 Public URL: https://givc.brainsait.com"
echo "🏠 Local URL:  http://localhost"
echo "🔌 Backend:    http://localhost:8000"
