# BrainSait Agentic Workflow System

AI-powered multi-agent content creation and publishing workflow system for automated generation of online courses, blog posts, and social media content.

## 🎯 Features

### Multi-Agent System
- **Research Agent**: Information gathering and topic research
- **Content Writer**: High-quality content creation
- **Editor Agent**: Content review and improvement
- **SEO Agent**: Search engine optimization
- **Course Designer**: Educational course structure design
- **Social Media Agent**: Platform-optimized social content

### Content Types
1. **Blog Posts**: SEO-optimized articles with research
2. **Online Courses**: Complete course structures with modules
3. **Social Media Posts**: Multi-platform content (Twitter, LinkedIn, Instagram, Facebook)
4. **Video Scripts**: Engaging video content scripts

### Integrations
- **WordPress**: Automated blog post publishing
- **Moodle**: Course deployment and management
- **Portainer**: Container management interface
- **N8N**: Workflow automation and scheduling
- **Ollama**: Local LLM inference (privacy-focused)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 8GB+ RAM recommended
- Cloudflare Tunnel configured (for public access)

### Installation

1. **Deploy the stack:**
```bash
cd ~/brainsait-agentic-workflow
docker-compose up -d
```

2. **Pull Ollama models:**
```bash
docker exec -it brainsait-ollama ollama pull llama3.2
docker exec -it brainsait-ollama ollama pull llama3.2:1b
```

3. **Access the services:**
- Dashboard: http://localhost:3001
- Orchestrator API: http://localhost:8000/docs
- N8N Workflow: http://localhost:5678 (admin/brainsait2024)
- Open WebUI: http://localhost:3000
- Portainer: http://localhost:9000

### Update Cloudflare Tunnel

Add these services to your `/etc/cloudflared/config.yml`:

```yaml
ingress:
  - hostname: workflow.brainsait.com
    service: http://localhost:3001
  - hostname: api.brainsait.com
    service: http://localhost:8000
  - hostname: n8n.brainsait.com
    service: http://localhost:5678
  - hostname: ai.brainsait.com
    service: http://localhost:3000
  - hostname: wordpress.brainsait.com
    service: http://localhost:8080
  - hostname: moodle.brainsait.com
    service: http://localhost:8081
  - hostname: portainer.brainsait.com
    service: http://localhost:9000
  - service: http_status:404
```

Then restart the tunnel:
```bash
sudo systemctl restart cloudflared
```

## 📖 Usage

### Creating Content via Dashboard

1. Open the dashboard at http://localhost:3001
2. Click "Create Workflow"
3. Select content type (blog post, course, social media)
4. Fill in the topic and parameters
5. Submit and monitor progress
6. Review generated content
7. Publish to WordPress or Moodle

### Using the API

Create a blog post:
```bash
curl -X POST http://localhost:8000/workflow/create \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "blog_post",
    "topic": "The Future of AI in Education",
    "target_audience": "educators",
    "tone": "professional",
    "keywords": ["AI", "education", "technology"]
  }'
```

Check workflow status:
```bash
curl http://localhost:8000/workflow/{workflow_id}
```

### Creating Courses

```bash
curl -X POST http://localhost:8000/workflow/create \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "course",
    "topic": "Introduction to Machine Learning",
    "target_audience": "beginners",
    "length": "medium"
  }'
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in the project root:

```env
# Ollama
OLLAMA_MODEL=llama3.2

# Database
POSTGRES_DB=brainsait_workflow
POSTGRES_USER=brainsait
POSTGRES_PASSWORD=your_secure_password

# N8N
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_password

# WordPress
WORDPRESS_URL=http://host.docker.internal:8080
WORDPRESS_API_USER=your_user
WORDPRESS_API_TOKEN=your_token

# Moodle
MOODLE_URL=http://host.docker.internal:8081
MOODLE_TOKEN=your_moodle_token
```

## 🔄 Workflow Architecture

```
User Request → Dashboard → Orchestrator API
                              ↓
                    Multi-Agent Processing
                    (Research → Write → Edit → SEO)
                              ↓
                    Content Generation
                              ↓
                    Review & Approval
                              ↓
                Publishing (WordPress/Moodle)
```

## 📊 Monitoring

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f workflow-orchestrator
docker-compose logs -f ollama
```

Check service health:
```bash
curl http://localhost:8000/health
```

## 🛠️ Maintenance

### Update containers:
```bash
docker-compose pull
docker-compose up -d
```

### Backup database:
```bash
docker exec brainsait-postgres pg_dump -U brainsait brainsait_workflow > backup.sql
```

### Restore database:
```bash
cat backup.sql | docker exec -i brainsait-postgres psql -U brainsait brainsait_workflow
```

## 📈 Scaling

For production deployment:
1. Use external PostgreSQL database
2. Configure Redis cluster
3. Set up load balancer
4. Enable HTTPS with proper certificates
5. Implement API rate limiting
6. Add monitoring (Prometheus/Grafana)

## 🔒 Security

- Change default passwords in production
- Use environment variables for secrets
- Enable HTTPS for all services
- Implement proper authentication
- Regular security updates

## 📝 API Documentation

Full API documentation available at: http://localhost:8000/docs

Key endpoints:
- `POST /workflow/create` - Create new workflow
- `GET /workflow/{id}` - Get workflow status
- `GET /workflows` - List all workflows
- `POST /publish/wordpress/{id}` - Publish to WordPress
- `POST /publish/moodle/{id}` - Publish to Moodle
- `GET /agents` - List available agents

## 🤝 Contributing

This is a proprietary system for BrainSait. For feature requests or issues, contact the development team.

## 📄 License

Proprietary - BrainSait © 2025

## 🆘 Support

For support and questions:
- Email: support@brainsait.com
- Documentation: https://docs.brainsait.com
- Dashboard: https://workflow.brainsait.com
