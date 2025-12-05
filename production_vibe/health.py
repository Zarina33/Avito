"""
Health Checks and Metrics
Provides monitoring endpoints for the API
"""
import time
import psutil
import torch
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass, field
from threading import Lock

from flask import Blueprint, jsonify


# ===============================
# Metrics Collection
# ===============================

@dataclass
class RequestMetrics:
    """Track request metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avibe_requests: int = 0
    avision_requests: int = 0
    total_response_time: float = 0.0
    total_tokens_generated: int = 0
    
    def __post_init__(self):
        self.lock = Lock()
    
    def record_request(self, endpoint: str, success: bool, response_time: float, tokens: int = 0):
        """Record a request"""
        with self.lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
            
            if endpoint == "avibe":
                self.avibe_requests += 1
            elif endpoint == "avision":
                self.avision_requests += 1
            
            self.total_response_time += response_time
            self.total_tokens_generated += tokens
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        with self.lock:
            avg_response_time = (
                self.total_response_time / self.total_requests
                if self.total_requests > 0 else 0
            )
            success_rate = (
                self.successful_requests / self.total_requests * 100
                if self.total_requests > 0 else 0
            )
            
            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": f"{success_rate:.2f}%",
                "avibe_requests": self.avibe_requests,
                "avision_requests": self.avision_requests,
                "avg_response_time": f"{avg_response_time:.3f}s",
                "total_tokens_generated": self.total_tokens_generated,
            }
    
    def reset(self):
        """Reset all metrics"""
        with self.lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.avibe_requests = 0
            self.avision_requests = 0
            self.total_response_time = 0.0
            self.total_tokens_generated = 0


# Global metrics instance
metrics = RequestMetrics()


# ===============================
# Health Check Blueprint
# ===============================

health_bp = Blueprint('health', __name__)

# Track application start time
app_start_time = time.time()


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - app_start_time)
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check - ensures models are loaded and GPU is available
    Returns 200 if service is ready to accept requests
    """
    try:
        # Check CUDA availability
        if not torch.cuda.is_available():
            return jsonify({
                "status": "not_ready",
                "reason": "CUDA not available",
                "timestamp": datetime.utcnow().isoformat()
            }), 503
        
        # Check GPU memory
        gpu_memory = torch.cuda.get_device_properties(0).total_memory
        if gpu_memory == 0:
            return jsonify({
                "status": "not_ready",
                "reason": "GPU memory not available",
                "timestamp": datetime.utcnow().isoformat()
            }), 503
        
        return jsonify({
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "cuda_available": True,
            "gpu_memory_gb": f"{gpu_memory / (1024**3):.2f}"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Liveness check - simple ping to verify service is alive
    Returns 200 if process is running
    """
    return jsonify({
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get detailed metrics about the service
    """
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU metrics
        gpu_metrics = {}
        if torch.cuda.is_available():
            gpu_metrics = {
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_allocated_gb": f"{torch.cuda.memory_allocated(0) / (1024**3):.2f}",
                "gpu_memory_reserved_gb": f"{torch.cuda.memory_reserved(0) / (1024**3):.2f}",
                "gpu_memory_total_gb": f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f}",
                "gpu_utilization": f"{(torch.cuda.memory_allocated(0) / torch.cuda.get_device_properties(0).total_memory * 100):.2f}%"
            }
        
        # Application metrics
        app_metrics = metrics.get_stats()
        
        return jsonify({
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - app_start_time),
            "system": {
                "cpu_percent": f"{cpu_percent}%",
                "memory_percent": f"{memory.percent}%",
                "memory_available_gb": f"{memory.available / (1024**3):.2f}",
                "disk_percent": f"{disk.percent}%",
                "disk_free_gb": f"{disk.free / (1024**3):.2f}"
            },
            "gpu": gpu_metrics,
            "application": app_metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Failed to collect metrics",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@health_bp.route('/metrics/reset', methods=['POST'])
def reset_metrics():
    """
    Reset application metrics (admin endpoint)
    """
    metrics.reset()
    return jsonify({
        "message": "Metrics reset successfully",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


# ===============================
# Helper function to record metrics
# ===============================

def record_inference_metrics(endpoint: str, success: bool, response_time: float, tokens: int = 0):
    """Helper function to record inference metrics"""
    metrics.record_request(endpoint, success, response_time, tokens)

