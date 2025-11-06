# Celery & RabbitMQ Runtime Architecture

**Version:** 1.0  
**Phase:** 2 - Celery / RabbitMQ Runtime  
**Owner:** Runtime Engineering, DevOps, SRE  
**Status:** Implementation Ready

---

## 📋 Overview

This document details the asynchronous task processing architecture for ClaimLinc-GIVC using Celery with RabbitMQ as the message broker and Redis as the result backend. The architecture is designed for high availability, fault tolerance, and HIPAA compliance.

---

## 🏗️ Architecture Design

### High-Level Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                       FastAPI Application                         │
│                    (Task Publishers)                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │ TLS 1.3 (mTLS)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    RabbitMQ Cluster (Quorum Queues)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ RabbitMQ-1   │  │ RabbitMQ-2   │  │ RabbitMQ-3   │           │
│  │ (Primary)    │  │ (Member)     │  │ (Member)     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────┬─────────────────────────────────────┘
                             │ TLS 1.3 (mTLS)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Celery Workers                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Worker-1    │  │  Worker-2    │  │  Worker-N    │           │
│  │ (NPHIES)     │  │ (Claims)     │  │ (General)    │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │ TLS 1.3                              │
│                            ▼                                      │
│                  ┌──────────────────┐                             │
│                  │  Redis Cluster   │                             │
│                  │  (Result Backend) │                            │
│                  └──────────────────┘                             │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ Prometheus + Flower │
                    │   (Monitoring)      │
                    └────────────────────┘
```

---

## 🐰 RabbitMQ Configuration

### Cluster Specifications

| Component | Specification | Rationale |
|:----------|:-------------|:----------|
| **Nodes** | 3 nodes (quorum queues) | Fault tolerance, no split-brain |
| **vCPU** | 4 cores per node | Message routing + persistence |
| **Memory** | 16 GB per node | Message buffer + metadata |
| **Storage** | 1 TB SSD per node | Persistent messages, logs |
| **Network** | 10 Gbps, private subnet | Low latency replication |
| **TLS** | 1.3, mutual auth | HIPAA §164.312 compliance |

### RabbitMQ Configuration File

`/etc/rabbitmq/rabbitmq.conf`:

```ini
# Clustering
cluster_formation.peer_discovery_backend = rabbit_peer_discovery_classic_config
cluster_formation.classic_config.nodes.1 = rabbit@rabbitmq-1
cluster_formation.classic_config.nodes.2 = rabbit@rabbitmq-2
cluster_formation.classic_config.nodes.3 = rabbit@rabbitmq-3

# Network & Ports
listeners.tcp = none
listeners.ssl.default = 5671

# TLS Configuration
ssl_options.cacertfile = /etc/rabbitmq/tls/ca.pem
ssl_options.certfile = /etc/rabbitmq/tls/server-cert.pem
ssl_options.keyfile = /etc/rabbitmq/tls/server-key.pem
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
ssl_options.versions.1 = tlsv1.3

# Management Plugin TLS
management.ssl.port = 15671
management.ssl.cacertfile = /etc/rabbitmq/tls/ca.pem
management.ssl.certfile = /etc/rabbitmq/tls/server-cert.pem
management.ssl.keyfile = /etc/rabbitmq/tls/server-key.pem

# Memory & Disk
vm_memory_high_watermark.relative = 0.6
disk_free_limit.absolute = 50GB

# Queue Settings
queue_master_locator = min-masters
default_queue_type = quorum

# Logging
log.file.level = info
log.console.level = info
log.file = /var/log/rabbitmq/rabbitmq.log
log.file.rotation.count = 10
log.file.rotation.size = 104857600

# Heartbeat
heartbeat = 60

# Channel limits
channel_max = 2048

# Authentication
auth_mechanisms.1 = PLAIN
auth_mechanisms.2 = AMQPLAIN
```

### Queue Definitions

`/etc/rabbitmq/definitions.json`:

```json
{
  "queues": [
    {
      "name": "celery.nphies.eligibility",
      "vhost": "/claimlinc",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-queue-type": "quorum",
        "x-max-length": 100000,
        "x-overflow": "reject-publish",
        "x-dead-letter-exchange": "dlx.nphies",
        "x-dead-letter-routing-key": "dlq.nphies.eligibility"
      }
    },
    {
      "name": "celery.nphies.claims",
      "vhost": "/claimlinc",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-queue-type": "quorum",
        "x-max-length": 100000,
        "x-overflow": "reject-publish",
        "x-dead-letter-exchange": "dlx.nphies",
        "x-dead-letter-routing-key": "dlq.nphies.claims"
      }
    },
    {
      "name": "celery.general",
      "vhost": "/claimlinc",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-queue-type": "quorum",
        "x-max-length": 50000,
        "x-overflow": "reject-publish",
        "x-dead-letter-exchange": "dlx.general",
        "x-dead-letter-routing-key": "dlq.general"
      }
    }
  ],
  "exchanges": [
    {
      "name": "dlx.nphies",
      "vhost": "/claimlinc",
      "type": "topic",
      "durable": true,
      "auto_delete": false
    },
    {
      "name": "dlx.general",
      "vhost": "/claimlinc",
      "type": "topic",
      "durable": true,
      "auto_delete": false
    }
  ],
  "bindings": [
    {
      "source": "dlx.nphies",
      "vhost": "/claimlinc",
      "destination": "dlq.nphies.eligibility",
      "destination_type": "queue",
      "routing_key": "dlq.nphies.eligibility"
    },
    {
      "source": "dlx.nphies",
      "vhost": "/claimlinc",
      "destination": "dlq.nphies.claims",
      "destination_type": "queue",
      "routing_key": "dlq.nphies.claims"
    },
    {
      "source": "dlx.general",
      "vhost": "/claimlinc",
      "destination": "dlq.general",
      "destination_type": "queue",
      "routing_key": "dlq.general"
    }
  ]
}
```

---

## 🔴 Redis Configuration

### Cluster Specifications

| Component | Specification | Rationale |
|:----------|:-------------|:----------|
| **Topology** | 1 primary + 2 replicas | HA with automatic failover |
| **vCPU** | 2 cores per node | Result processing |
| **Memory** | 32 GB per node | Task results + metadata |
| **Persistence** | AOF (Always) | Durability for HIPAA |
| **Network** | 10 Gbps, private subnet | Low latency replication |

### Redis Configuration

`/etc/redis/redis.conf`:

```ini
# Network
bind 0.0.0.0
port 6379
protected-mode yes
tcp-backlog 511

# TLS
tls-port 6380
tls-cert-file /etc/redis/tls/redis-cert.pem
tls-key-file /etc/redis/tls/redis-key.pem
tls-ca-cert-file /etc/redis/tls/ca.pem
tls-auth-clients yes
tls-protocols "TLSv1.3"

# Replication
replicaof redis-primary.claimlinc.local 6380
masterauth ${REDIS_PASSWORD}
replica-read-only yes

# Persistence
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Memory
maxmemory 28gb
maxmemory-policy allkeys-lru

# Security
requirepass ${REDIS_PASSWORD}

# Logging
loglevel notice
logfile /var/log/redis/redis.log

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128
```

---

## 🌿 Celery Configuration

### Worker Configuration

`config/celery_config.py`:

```python
"""
Celery Configuration for ClaimLinc-GIVC
HIPAA-compliant task processing with DLQ and idempotency
"""

from kombu import Exchange, Queue
from config.security.vault_client import get_rabbitmq_credentials, get_secret

# Get credentials from Vault
rabbitmq_creds = get_rabbitmq_credentials()
redis_password = get_secret('celery/redis-password', 'password')

# Broker Configuration
broker_url = (
    f"amqps://{rabbitmq_creds['username']}:{rabbitmq_creds['password']}"
    f"@rabbitmq.claimlinc.local:5671/claimlinc"
)

broker_use_ssl = {
    'ca_certs': '/etc/claimlinc/tls/ca.pem',
    'certfile': '/etc/claimlinc/tls/client-cert.pem',
    'keyfile': '/etc/claimlinc/tls/client-key.pem',
    'cert_reqs': __import__('ssl').CERT_REQUIRED,
    'ssl_version': __import__('ssl').PROTOCOL_TLSv1_3
}

# Result Backend Configuration
result_backend = f"rediss://:{redis_password}@redis.claimlinc.local:6380/0"
redis_backend_use_ssl = {
    'ssl_cert_reqs': __import__('ssl').CERT_REQUIRED,
    'ssl_ca_certs': '/etc/claimlinc/tls/ca.pem',
    'ssl_certfile': '/etc/claimlinc/tls/client-cert.pem',
    'ssl_keyfile': '/etc/claimlinc/tls/client-key.pem',
}

# Task Configuration
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Riyadh'
enable_utc = True

# Reliability & Idempotency
task_acks_late = True
task_reject_on_worker_lost = True
task_track_started = True
task_time_limit = 3600  # 1 hour
task_soft_time_limit = 3300  # 55 minutes
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

# Retry Policy
task_autoretry_for = (Exception,)
task_retry_kwargs = {'max_retries': 5, 'countdown': 60}
task_retry_backoff = True
task_retry_backoff_max = 600  # 10 minutes
task_retry_jitter = True

# Result Backend
result_expires = 86400  # 24 hours
result_compression = 'gzip'
result_extended = True

# Queue Routing
task_routes = {
    'tasks.nphies.check_eligibility': {'queue': 'celery.nphies.eligibility'},
    'tasks.nphies.submit_claim': {'queue': 'celery.nphies.claims'},
    'tasks.nphies.poll_response': {'queue': 'celery.nphies.claims'},
    'tasks.general.*': {'queue': 'celery.general'},
}

# Dead Letter Queue Configuration
task_default_exchange = 'celery'
task_default_routing_key = 'celery'

task_queues = (
    Queue('celery.nphies.eligibility',
          Exchange('celery', type='direct'),
          routing_key='celery.nphies.eligibility',
          queue_arguments={
              'x-queue-type': 'quorum',
              'x-dead-letter-exchange': 'dlx.nphies',
              'x-dead-letter-routing-key': 'dlq.nphies.eligibility'
          }),
    
    Queue('celery.nphies.claims',
          Exchange('celery', type='direct'),
          routing_key='celery.nphies.claims',
          queue_arguments={
              'x-queue-type': 'quorum',
              'x-dead-letter-exchange': 'dlx.nphies',
              'x-dead-letter-routing-key': 'dlq.nphies.claims'
          }),
    
    Queue('celery.general',
          Exchange('celery', type='direct'),
          routing_key='celery.general',
          queue_arguments={
              'x-queue-type': 'quorum',
              'x-dead-letter-exchange': 'dlx.general',
              'x-dead-letter-routing-key': 'dlq.general'
          }),
)

# Monitoring
worker_send_task_events = True
task_send_sent_event = True

# Logging
worker_log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
worker_task_log_format = '%(asctime)s - %(task_name)s[%(task_id)s] - %(levelname)s - %(message)s'
```

### Celery Application

`workers/celery_app.py`:

```python
"""
Celery Application Instance
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import logging
import uuid

logger = logging.getLogger(__name__)

# Create Celery app
app = Celery('claimlinc')
app.config_from_object('config.celery_config')

# Auto-discover tasks
app.autodiscover_tasks(['workers.tasks'])


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Add correlation ID for audit trail"""
    correlation_id = kwargs.get('correlation_id') or str(uuid.uuid4())
    logger.info(f"Task started: {task.name}[{task_id}] - Correlation ID: {correlation_id}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, **extra):
    """Log task completion"""
    logger.info(f"Task completed: {task.name}[{task_id}]")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, **extra):
    """Log task failures and send alerts"""
    logger.error(f"Task failed: {sender.name}[{task_id}] - {exception}")
    
    # Send alert to monitoring system
    # (Implementation depends on alerting infrastructure)


if __name__ == '__main__':
    app.start()
```

---

## 📊 Monitoring & Metrics

### Flower Dashboard

Deploy Flower for real-time monitoring:

```bash
celery -A workers.celery_app flower \
    --port=5555 \
    --broker_api=https://rabbitmq.claimlinc.local:15671/api/ \
    --basic_auth=admin:${FLOWER_PASSWORD}
```

### Prometheus Metrics

Celery Prometheus exporter configuration in `docker-compose.yml`:

```yaml
celery-exporter:
  image: danihodovic/celery-exporter:latest
  environment:
    - CELERY_BROKER_URL=amqps://user:pass@rabbitmq.claimlinc.local:5671/claimlinc
    - CELERY_RESULT_BACKEND=rediss://:pass@redis.claimlinc.local:6380/0
  ports:
    - "9808:9808"
```

### Key Metrics

| Metric | Alert Threshold | Action |
|:-------|:----------------|:-------|
| Queue Depth | > 10,000 | Scale workers |
| Task Failure Rate | > 5% | Investigate errors |
| DLQ Size | > 100 | Manual review required |
| Worker Response Time | > 30s (p95) | Optimize tasks |
| Redis Memory | > 90% | Increase capacity |

---

## ✅ Validation Checklist

- [ ] RabbitMQ 3-node cluster operational with quorum queues
- [ ] Redis cluster with AOF persistence configured
- [ ] TLS 1.3 enforced for all broker/backend connections
- [ ] Celery workers deployed with proper queue routing
- [ ] DLQ configured for all primary queues
- [ ] Idempotency keys implemented in critical tasks
- [ ] Vault integration for dynamic credentials
- [ ] Flower dashboard accessible and secured
- [ ] Prometheus metrics exporter deployed
- [ ] Alert rules configured and tested

---

**Last Updated:** 2025-11-05  
**Next Review:** 2025-12-05  
**Document Owner:** Runtime Engineering Team
