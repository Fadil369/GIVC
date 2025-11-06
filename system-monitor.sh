#!/bin/bash

# GIVC Platform - System Resource Monitoring
# Purpose: Monitor system resources and alert on issues

echo "GIVC Platform - System Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# CPU and Memory
echo "System Resources:"
echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "  Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "  Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"
echo ""

# Docker stats
echo "Container Resources:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker ps --filter "name=givc" -q)
echo ""

# Network
echo "Network Activity:"
RX_BYTES=$(cat /sys/class/net/eth0/statistics/rx_bytes 2>/dev/null || cat /sys/class/net/wlan0/statistics/rx_bytes 2>/dev/null || echo 0)
TX_BYTES=$(cat /sys/class/net/eth0/statistics/tx_bytes 2>/dev/null || cat /sys/class/net/wlan0/statistics/tx_bytes 2>/dev/null || echo 0)
echo "  RX: $(numfmt --to=iec-i --suffix=B $RX_BYTES)"
echo "  TX: $(numfmt --to=iec-i --suffix=B $TX_BYTES)"
echo ""

# Disk space alerts
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  WARNING: Disk usage above 80%!"
fi
