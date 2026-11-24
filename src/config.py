"""Configuration loader for InstaNote."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class InstagramConfig:
    app_id: str = ""
    app_secret: str = ""
    access_token: str = ""
    user_id: str = ""
    redirect_uri: str = "http://localhost:8080/callback"


@dataclass
class AIImageConfig:
    provider: str = "stable_diffusion"
    model: str = "stable-diffusion-xl-base-1.0"
    api_key: str = ""
    local_path: str = ""


@dataclass
class ResearchConfig:
    sources: list = field(default_factory=lambda: ["wikipedia", "manufacturer_website", "automotive_news", "specs_database"])
    timeout: int = 30


@dataclass
class AutomationConfig:
    daily_limit: int = 3
    schedule_enabled: bool = True
    schedule_times: list = field(default_factory=lambda: ["09:00", "14:00", "19:00"])
    min_interval_hours: int = 4


@dataclass
class ImageConfig:
    width: int = 1080
    height: int = 1350
    format: str = "PNG"
    quality: int = 95
    styles: list = field(default_factory=list)
    default_style: str = "Aesthetic Handwritten Illustrated Infographic"


@dataclass
class MusicConfig:
    categories: Dict[str, list] = field(default_factory=dict)


@dataclass
class DatabaseConfig:
    path: str = "data/instanote.db"


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/instanote.log"


@dataclass
class AdminConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    secret_key: str = "change-this-secret-key"


@dataclass
class Config:
    instagram: InstagramConfig = field(default_factory=InstagramConfig)
    ai_image: AIImageConfig = field(default_factory=AIImageConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    music: MusicConfig = field(default_factory=MusicConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    admin: AdminConfig = field(default_factory=AdminConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        # Try local config first, then default
        local_path = Path("config.local.yaml")
        default_path = Path("config.yaml")
        config_path = local_path if local_path.exists() else default_path

    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    config = Config()

    if 'instagram' in data:
        config.instagram = InstagramConfig(**data['instagram'])
    if 'ai_image' in data:
        config.ai_image = AIImageConfig(**data['ai_image'])
    if 'research' in data:
        config.research = ResearchConfig(**data['research'])
    if 'automation' in data:
        auto_data = data['automation']
        config.automation = AutomationConfig(
            daily_limit=auto_data.get('daily_limit', 3),
            schedule_enabled=auto_data.get('schedule', {}).get('enabled', True),
            schedule_times=auto_data.get('schedule', {}).get('times', ["09:00", "14:00", "19:00"]),
            min_interval_hours=auto_data.get('min_interval_hours', 4)
        )
    if 'image' in data:
        img_data = data['image']
        config.image = ImageConfig(
            width=img_data.get('width', 1080),
            height=img_data.get('height', 1350),
            format=img_data.get('format', 'PNG'),
            quality=img_data.get('quality', 95),
            styles=img_data.get('styles', []),
            default_style=img_data.get('default_style', "Aesthetic Handwritten Illustrated Infographic")
        )
    if 'music' in data:
        config.music = MusicConfig(categories=data['music'].get('categories', {}))
    if 'database' in data:
        config.database = DatabaseConfig(**data['database'])
    if 'logging' in data:
        config.logging = LoggingConfig(**data['logging'])
    if 'admin' in data:
        config.admin = AdminConfig(**data['admin'])

    # Override with environment variables
    _override_from_env(config)

    return config


def _override_from_env(config: Config) -> None:
    """Override config values from environment variables."""
    env_mapping = {
        'INSTAGRAM_APP_ID': ('instagram', 'app_id'),
        'INSTAGRAM_APP_SECRET': ('instagram', 'app_secret'),
        'INSTAGRAM_ACCESS_TOKEN': ('instagram', 'access_token'),
        'INSTAGRAM_USER_ID': ('instagram', 'user_id'),
        'AI_IMAGE_API_KEY': ('ai_image', 'api_key'),
        'AI_IMAGE_LOCAL_PATH': ('ai_image', 'local_path'),
        'DATABASE_PATH': ('database', 'path'),
        'ADMIN_SECRET_KEY': ('admin', 'secret_key'),
        'LOG_LEVEL': ('logging', 'level'),
    }

    for env_var, (section, key) in env_mapping.items():
        value = os.environ.get(env_var)
        if value:
            obj = getattr(config, section)
            setattr(obj, key, value)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance (lazy load)."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """Reload configuration from file."""
    global _config
    _config = load_config(config_path)
    return _config