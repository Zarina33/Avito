#!/bin/bash

# Gunicorn configuration for production deployment
# Usage: gunicorn -c gunicorn_config.py app_production:app

import multiprocessing
import os

# Server socket
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8085')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', '1'))  # Для GPU лучше использовать 1 worker
worker_class = 'sync'
worker_connections = 1000
timeout = 300  # 5 minutes timeout for inference
keepalive = 5

# Process naming
proc_name = 'avito-ai-api'

# Logging
accesslog = os.getenv('ACCESS_LOG', '/var/log/avito-ai/access.log')
errorlog = os.getenv('ERROR_LOG', '/var/log/avito-ai/error.log')
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server mechanics
daemon = False
pidfile = '/var/run/avito-ai/gunicorn.pid'
umask = 0o007
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("="*70)
    print("🚀 Starting Avito AI API Server")
    print("="*70)

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("🔄 Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    print("="*70)
    print(f"✅ Server is ready! Listening on {bind}")
    print(f"📊 Health check: http://{bind}/api/health")
    print(f"📈 Metrics: http://{bind}/api/metrics")
    print("="*70)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"⚠️  Worker {worker.pid} received SIGINT/SIGQUIT")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print(f"❌ Worker {worker.pid} aborted")

