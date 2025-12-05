"""
Production Configuration Management
Centralizes all configuration with environment variables support
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Model-specific configuration"""
    vibe_model_dir: str
    vibe_tokenizer_dir: str
    vision_snapshot_dir: str
    device: str = "cuda:0"
    torch_dtype: str = "float16"
    max_tokens_avibe: int = 256
    max_tokens_avision: int = 200
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.1


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8085
    debug: bool = False
    workers: int = 1
    max_content_length: int = 16 * 1024 * 1024  # 16MB


@dataclass
class SecurityConfig:
    """Security configuration"""
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 100
    allowed_origins: list = None
    max_prompt_length: int = 2000
    allowed_image_extensions: set = None
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]
        if self.allowed_image_extensions is None:
            self.allowed_image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s [%(levelname)s] [%(request_id)s] %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
    log_file: Optional[str] = None


class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "production")
        
        # Model Configuration
        self.model = ModelConfig(
            vibe_model_dir=os.getenv(
                "VIBE_MODEL_DIR",
                "/mnt/data/avito/vibe/models"
            ),
            vibe_tokenizer_dir=os.getenv(
                "VIBE_TOKENIZER_DIR",
                "/mnt/data/avito/vibe/tokenizers"
            ),
            vision_snapshot_dir=os.getenv(
                "VISION_SNAPSHOT_DIR",
                "/mnt/data/avito/vision/models/models--AvitoTech--avision/snapshots/def8375a2aa67643348ffd93143691410576663f"
            ),
            device=os.getenv("CUDA_DEVICE", "cuda:0"),
            max_tokens_avibe=int(os.getenv("MAX_TOKENS_AVIBE", "256")),
            max_tokens_avision=int(os.getenv("MAX_TOKENS_AVISION", "200")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            top_p=float(os.getenv("TOP_P", "0.9")),
        )
        
        # Server Configuration
        self.server = ServerConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8085")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            workers=int(os.getenv("WORKERS", "1")),
        )
        
        # Security Configuration
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        self.security = SecurityConfig(
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "10")),
            rate_limit_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "100")),
            allowed_origins=allowed_origins,
            max_prompt_length=int(os.getenv("MAX_PROMPT_LENGTH", "2000")),
        )
        
        # Logging Configuration
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
        )
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


# Global config instance
config = Config()

