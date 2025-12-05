#!/bin/bash

# Deployment script for Avito AI API
# Usage: cd production_vibe && ./deploy.sh [development|production]

set -e  # Exit on error

# Ensure we're in the production_vibe directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check environment argument
ENVIRONMENT=${1:-production}

if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment. Use 'development' or 'production'"
    exit 1
fi

log_info "Deploying in ${ENVIRONMENT} mode..."

# Check if .env exists
if [ ! -f .env ]; then
    log_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        log_success ".env created. Please edit it with your configuration."
        log_warning "Stopping deployment. Please configure .env first."
        exit 0
    else
        log_error ".env.example not found!"
        exit 1
    fi
fi

# Check Python version
log_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    log_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi
log_success "Python version: $PYTHON_VERSION"

# Check CUDA availability
log_info "Checking CUDA availability..."
if command -v nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n1)
    log_success "CUDA driver version: $CUDA_VERSION"
else
    log_error "nvidia-smi not found. CUDA may not be available."
    exit 1
fi

# Create/activate virtual environment
log_info "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

source venv/bin/activate
log_success "Virtual environment activated"

# Install/update dependencies
log_info "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
log_success "Dependencies installed"

# Create log directory
LOG_DIR="/var/log/avito-ai"
if [ ! -d "$LOG_DIR" ]; then
    log_info "Creating log directory..."
    if sudo mkdir -p "$LOG_DIR" 2>/dev/null; then
        sudo chown $USER:$USER "$LOG_DIR"
        log_success "Log directory created: $LOG_DIR"
    else
        log_warning "Could not create log directory. Using local logs."
    fi
fi

# Test imports
log_info "Testing imports..."
python3 -c "
import torch
import transformers
from PIL import Image
import flask
from flask_cors import CORS
print('All imports successful')
" 2>&1
if [ $? -eq 0 ]; then
    log_success "All imports successful"
else
    log_error "Import test failed"
    exit 1
fi

# Test CUDA in Python
log_info "Testing CUDA in Python..."
CUDA_AVAILABLE=$(python3 -c "import torch; print(torch.cuda.is_available())" 2>&1)
if [ "$CUDA_AVAILABLE" = "True" ]; then
    GPU_NAME=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>&1)
    log_success "CUDA available: $GPU_NAME"
else
    log_error "CUDA not available in Python"
    exit 1
fi

# Test configuration
log_info "Testing configuration..."
python3 -c "
from config import config
print(f'Environment: {config.environment}')
print(f'Host: {config.server.host}')
print(f'Port: {config.server.port}')
" 2>&1
if [ $? -eq 0 ]; then
    log_success "Configuration loaded successfully"
else
    log_error "Configuration test failed"
    exit 1
fi

# Start application based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    log_info "Starting in development mode..."
    log_warning "Press CTRL+C to stop"
    python3 app_production.py
    
elif [ "$ENVIRONMENT" = "production" ]; then
    # Check if systemd service exists
    if [ -f "/etc/systemd/system/avito-ai.service" ]; then
        log_info "Restarting systemd service..."
        sudo systemctl restart avito-ai
        sleep 2
        
        if sudo systemctl is-active --quiet avito-ai; then
            log_success "Service started successfully"
            log_info "Status:"
            sudo systemctl status avito-ai --no-pager -l
            log_info ""
            log_info "View logs: sudo journalctl -u avito-ai -f"
        else
            log_error "Service failed to start"
            log_info "View logs: sudo journalctl -u avito-ai -n 50"
            exit 1
        fi
    else
        log_warning "Systemd service not installed. Installing..."
        log_info "Copying service file..."
        sudo cp avito-ai.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable avito-ai
        log_success "Service installed"
        
        log_info "Starting service..."
        sudo systemctl start avito-ai
        sleep 2
        
        if sudo systemctl is-active --quiet avito-ai; then
            log_success "Service started successfully"
        else
            log_error "Service failed to start"
            exit 1
        fi
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    sleep 5  # Give server time to start
    
    PORT=$(grep "^PORT=" .env | cut -d'=' -f2)
    PORT=${PORT:-8085}
    
    if curl -s -f "http://localhost:${PORT}/api/health" > /dev/null; then
        log_success "Health check passed"
        log_info ""
        log_success "==================================="
        log_success "Deployment successful!"
        log_success "==================================="
        log_info "API URL: http://localhost:${PORT}"
        log_info "Health check: http://localhost:${PORT}/api/health"
        log_info "Metrics: http://localhost:${PORT}/api/metrics"
        log_info ""
        log_info "Useful commands:"
        log_info "  - View logs: sudo journalctl -u avito-ai -f"
        log_info "  - Stop service: sudo systemctl stop avito-ai"
        log_info "  - Restart service: sudo systemctl restart avito-ai"
        log_info "  - Service status: sudo systemctl status avito-ai"
    else
        log_warning "Health check failed. Server may still be starting..."
        log_info "Check logs: sudo journalctl -u avito-ai -f"
    fi
fi

