# Avito AI API - Production Deployment Guide

## 🚀 Production-Ready Features

This upgraded API includes:

- ✅ **Configuration Management** - Environment-based config with `.env` support
- ✅ **Error Handling** - Comprehensive error handling with custom exceptions
- ✅ **Rate Limiting** - Protect API from abuse (configurable per minute/hour)
- ✅ **Request Tracing** - Unique request IDs for debugging
- ✅ **Health Checks** - `/api/health`, `/api/health/ready`, `/api/health/live`
- ✅ **Metrics** - `/api/metrics` endpoint with system and application metrics
- ✅ **Input Validation** - Validates prompts and image uploads
- ✅ **CORS Support** - Configurable cross-origin requests
- ✅ **Structured Logging** - Request context in all logs
- ✅ **Graceful Shutdown** - Proper cleanup on termination
- ✅ **JSON API Endpoints** - RESTful API alongside web interface
- ✅ **Production Server** - Gunicorn configuration included
- ✅ **Systemd Service** - Auto-restart and process management

---

## 📁 File Structure

```
/home/zarina/Work/BakaiMarket/Avito/
├── app_production.py          # Main production application
├── config.py                  # Configuration management
├── middleware.py              # Middleware (rate limiting, validation, errors)
├── health.py                  # Health checks and metrics
├── requirements.txt           # Python dependencies
├── gunicorn_config.py        # Gunicorn production server config
├── avito-ai.service          # Systemd service file
├── .env.example              # Example environment configuration
├── .env                      # Your actual environment config (create this)
└── README_PRODUCTION.md      # This file
```

---

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
# Create virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

Key configuration options:

```bash
# Security
RATE_LIMIT_PER_MINUTE=10      # Max requests per minute per IP
RATE_LIMIT_PER_HOUR=100       # Max requests per hour per IP
MAX_PROMPT_LENGTH=2000        # Max characters in prompts
ALLOWED_ORIGINS=*             # CORS origins (comma-separated)

# Model Performance
MAX_TOKENS_AVIBE=256          # Max tokens for text generation
MAX_TOKENS_AVISION=200        # Max tokens for image analysis
TEMPERATURE=0.7               # Generation temperature

# Logging
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
LOG_FILE=/var/log/avito-ai/app.log  # Optional log file
```

### 3. Create Log Directory (Optional)

```bash
sudo mkdir -p /var/log/avito-ai
sudo chown $USER:$USER /var/log/avito-ai
```

---

## 🏃 Running the Application

### Development Mode (Flask development server)

```bash
source venv/bin/activate
python app_production.py
```

### Production Mode (Gunicorn)

```bash
source venv/bin/activate
gunicorn -c gunicorn_config.py app_production:app
```

### As Systemd Service (Recommended for Production)

```bash
# Copy service file
sudo cp avito-ai.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable avito-ai

# Start service
sudo systemctl start avito-ai

# Check status
sudo systemctl status avito-ai

# View logs
sudo journalctl -u avito-ai -f
```

Useful systemd commands:

```bash
sudo systemctl stop avito-ai      # Stop service
sudo systemctl restart avito-ai   # Restart service
sudo systemctl reload avito-ai    # Reload without downtime (graceful)
```

---

## 📊 API Endpoints

### Web Interface

- `GET /` - Main web interface

### Health & Monitoring

- `GET /api/health` - Basic health check
- `GET /api/health/ready` - Readiness probe (checks GPU)
- `GET /api/health/live` - Liveness probe
- `GET /api/metrics` - Detailed metrics (system, GPU, application)
- `POST /api/metrics/reset` - Reset application metrics

### AI Endpoints (Web Forms)

- `POST /avibe` - Text generation (form data)
- `POST /avision` - Image analysis (multipart form)

### AI Endpoints (JSON API)

**Text Generation:**

```bash
curl -X POST http://localhost:8085/api/v1/text/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Привет, подскажи рецепт борща",
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

Response:

```json
{
  "success": true,
  "data": {
    "text": "Конечно! Вот классический рецепт борща...",
    "generated_tokens": 187,
    "input_tokens": 15
  },
  "metrics": {
    "generation_time": 2.145,
    "total_time": 2.156,
    "tokens_per_second": 87.12
  },
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 🔐 Security Features

### Rate Limiting

Automatically limits requests per IP:
- 10 requests per minute (default)
- 100 requests per hour (default)

Exceeded limits return HTTP 429:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded: 10 requests per minute",
  "request_id": "..."
}
```

### Input Validation

- **Prompt validation**: Max length, type checking
- **Image validation**: File type, size limits (16MB max)
- All validation errors return HTTP 400

### CORS Protection

Configure `ALLOWED_ORIGINS` in `.env`:

```bash
# Allow all (development)
ALLOWED_ORIGINS=*

# Specific domains (production)
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

---

## 📈 Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8085/api/health

# Readiness (checks GPU availability)
curl http://localhost:8085/api/health/ready

# Liveness (process is alive)
curl http://localhost:8085/api/health/live
```

### Metrics

```bash
curl http://localhost:8085/api/metrics
```

Returns:

```json
{
  "timestamp": "2025-11-28T10:30:00",
  "uptime_seconds": 3600,
  "system": {
    "cpu_percent": "15.2%",
    "memory_percent": "45.8%",
    "memory_available_gb": "128.5",
    "disk_percent": "60.2%"
  },
  "gpu": {
    "gpu_name": "NVIDIA H200",
    "gpu_memory_allocated_gb": "12.5",
    "gpu_memory_total_gb": "141.0",
    "gpu_utilization": "8.87%"
  },
  "application": {
    "total_requests": 1234,
    "successful_requests": 1200,
    "failed_requests": 34,
    "success_rate": "97.24%",
    "avibe_requests": 800,
    "avision_requests": 400,
    "avg_response_time": "2.345s",
    "total_tokens_generated": 250000
  }
}
```

---

## 🐛 Debugging

### Request Tracing

Every request gets a unique ID for tracing:

```bash
# Request
curl -H "X-Request-ID: my-custom-id" http://localhost:8085/api/health

# Response includes request ID
X-Request-ID: my-custom-id
X-Response-Time: 0.003s
```

Logs include request ID:

```
2025-11-28 10:30:00 [INFO] [my-custom-id] Processing request...
```

### Error Responses

All errors include request ID for debugging:

```json
{
  "error": "validation_error",
  "message": "Prompt too long. Maximum length: 2000 characters",
  "request_id": "a1b2c3d4-..."
}
```

### Common Issues

**GPU Not Available:**

```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Check GPU visibility
echo $CUDA_VISIBLE_DEVICES
```

**Rate Limit Too Restrictive:**

Edit `.env`:

```bash
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

**High Memory Usage:**

Reduce max tokens in `.env`:

```bash
MAX_TOKENS_AVIBE=128
MAX_TOKENS_AVISION=100
```

---

## 🔄 Deployment Workflow

### Standard Deployment

```bash
# 1. Pull latest code
git pull

# 2. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 3. Test configuration
python -c "from config import config; print(config.environment)"

# 4. Restart service
sudo systemctl restart avito-ai

# 5. Check status
sudo systemctl status avito-ai

# 6. Monitor logs
sudo journalctl -u avito-ai -f --lines=100
```

### Zero-Downtime Reload

```bash
# Graceful reload (requires gunicorn)
sudo systemctl reload avito-ai
```

### Rollback

```bash
# If deployment fails, rollback
git checkout previous-commit
sudo systemctl restart avito-ai
```

---

## 🧪 Testing

### Basic Tests

```bash
# Health check
curl http://localhost:8085/api/health

# Text generation
curl -X POST http://localhost:8085/api/v1/text/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Привет"}'

# Rate limit test
for i in {1..15}; do
  curl http://localhost:8085/api/health
  echo ""
done
# Should see 429 errors after 10 requests
```

### Load Testing (with Apache Bench)

```bash
# Install ab
sudo apt-get install apache2-utils

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8085/api/health

# Check metrics
curl http://localhost:8085/api/metrics
```

---

## 📦 Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV CUDA_VISIBLE_DEVICES=1
CMD ["gunicorn", "-c", "gunicorn_config.py", "app_production:app"]
```

Build and run:

```bash
docker build -t avito-ai .
docker run --gpus all -p 8085:8085 --env-file .env avito-ai
```

---

## 🛡️ Production Checklist

- [ ] Change default rate limits in `.env`
- [ ] Set `ALLOWED_ORIGINS` to specific domains (not `*`)
- [ ] Configure `LOG_FILE` for persistent logs
- [ ] Set up log rotation (logrotate)
- [ ] Enable firewall rules for port 8085
- [ ] Set up SSL/TLS (nginx reverse proxy)
- [ ] Configure monitoring (Prometheus, Grafana)
- [ ] Set up alerting (email, Slack)
- [ ] Test graceful shutdown (`kill -TERM <pid>`)
- [ ] Document API for your team
- [ ] Set up automated backups

---

## 📞 Support

For issues or questions:

1. Check logs: `sudo journalctl -u avito-ai -f`
2. Check metrics: `curl http://localhost:8085/api/metrics`
3. Review configuration: `cat .env`
4. Test GPU: `python -c "import torch; print(torch.cuda.is_available())"`

---

## 🔄 Comparison: Old vs New

| Feature | Old (`app.py`) | New (`app_production.py`) |
|---------|---------------|---------------------------|
| Configuration | Hardcoded | Environment variables |
| Error Handling | Basic | Comprehensive with custom exceptions |
| Rate Limiting | ❌ | ✅ Configurable per IP |
| Request Tracing | ❌ | ✅ Unique request IDs |
| Health Checks | ❌ | ✅ 3 endpoints (health/ready/live) |
| Metrics | Basic | Detailed (system, GPU, app) |
| Input Validation | ❌ | ✅ Comprehensive |
| CORS | ❌ | ✅ Configurable |
| Logging | Basic | Structured with context |
| Graceful Shutdown | ❌ | ✅ Signal handlers |
| JSON API | ❌ | ✅ RESTful endpoints |
| Production Server | Flask dev | Gunicorn |
| Systemd Support | ❌ | ✅ Service file included |

---

## 📄 License

Internal use - Avito AI Demo Project

---

*Generated: 2025-11-28*

