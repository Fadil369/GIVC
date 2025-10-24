#!/bin/bash

# GIVC Platform - Health Monitoring
# Purpose: Continuous health monitoring with alerts

HEALTH_LOG="/var/log/givc-health.log"
ALERT_THRESHOLD=3
FAILED_CHECKS=0

check_service() {
    local service=$1
    local endpoint=$2
    
    if curl -s --max-time 5 "$endpoint" >/dev/null 2>&1; then
        echo "$(date) - ✓ $service healthy" >> "$HEALTH_LOG"
        return 0
    else
        echo "$(date) - ✗ $service failed" >> "$HEALTH_LOG"
        return 1
    fi
}

# Check all services
check_service "Frontend" "http://localhost/" || FAILED_CHECKS=$((FAILED_CHECKS+1))
check_service "Backend" "http://localhost:8000/health" || FAILED_CHECKS=$((FAILED_CHECKS+1))
check_service "API" "http://localhost:8000/api/v1/status" || FAILED_CHECKS=$((FAILED_CHECKS+1))

# Check containers
if ! docker ps | grep -q "givc-backend.*healthy"; then
    FAILED_CHECKS=$((FAILED_CHECKS+1))
    echo "$(date) - ✗ Backend container unhealthy" >> "$HEALTH_LOG"
fi

# Alert if threshold exceeded
if [ $FAILED_CHECKS -ge $ALERT_THRESHOLD ]; then
    echo "$(date) - ALERT: $FAILED_CHECKS services failed!" >> "$HEALTH_LOG"
    # Send alert (email, Slack, etc.)
    # ./send-alert.sh "GIVC Platform: $FAILED_CHECKS services down"
fi

exit $FAILED_CHECKS
