"""Configuration loader for InstaNote.

Order of precedence (highest first):
  1. Environment variables / .env file
  2. config.local.yaml  (written by the Settings page, git-ignored)
  3. config.yaml        (defaults committed to git)
"""
import os
import secrets
import yaml
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field, fields

try:  # python-dotenv is optional at runtime
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


@dataclass
class InstagramConfig:
    app_id: str = ""
    app_secret: str = ""
    access_token: str = ""
    user_id: str = ""
    redirect_uri: str = "http://localhost:8080/callback"
    public_base_url: str = ""          # e.g. https://instanote.onrender.com (needed by Instagram API)
    graph_api_version: str = "v23.0"


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
    max_retries: int = 3
    cache_ttl: int = 3600


@dataclass
class AutomationConfig:
    daily_limit: int = 3
    min_interval_hours: int = 4
    timezone: str = "UTC"
    post_times: list = field(default_factory=lambda: ["09:00", "14:00", "19:00"])
    enabled: bool = True
    randomize_category: bool = False
    randomize_style: bool = False
    skip_posted: bool = True
    auto_post: bool = False            # False = only generate images, True = also publish to Instagram

    # backwards-compatible aliases used by older code
    @property
    def schedule_times(self) -> list:
        return self.post_times

    @property
    def schedule_enabled(self) -> bool:
        return self.enabled


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
    categories: Dict[str, str] = field(default_factory=dict)


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
    secret_key: str = ""               # session signing key (auto-generated when empty)
    password: str = ""                 # admin login password (auto-generated when empty)


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


def _build(cls, data: Optional[dict]):
    """Build a dataclass from a dict, silently ignoring unknown keys and None values."""
    data = data or {}
    allowed = {f.name for f in fields(cls)}
    clean = {k: v for k, v in data.items() if k in allowed and v is not None}
    return cls(**clean)


def _read_yaml(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML (+ local overrides) and environment variables."""
    if config_path:
        data = _read_yaml(Path(config_path))
    else:
        data = _merge(_read_yaml(BASE_DIR / "config.yaml"), _read_yaml(BASE_DIR / "config.local.yaml"))

    # old config format: automation.schedule_times / automation.schedule.times
    auto = dict(data.get("automation") or {})
    if "post_times" not in auto:
        if "schedule_times" in auto:
            auto["post_times"] = auto["schedule_times"]
        elif isinstance(auto.get("schedule"), dict) and "times" in auto["schedule"]:
            auto["post_times"] = auto["schedule"]["times"]
    if "enabled" not in auto and "schedule_enabled" in auto:
        auto["enabled"] = auto["schedule_enabled"]

    config = Config(
        instagram=_build(InstagramConfig, data.get("instagram")),
        ai_image=_build(AIImageConfig, data.get("ai_image")),
        research=_build(ResearchConfig, data.get("research")),
        automation=_build(AutomationConfig, auto),
        image=_build(ImageConfig, data.get("image")),
        music=MusicConfig(categories=(data.get("music") or {}).get("categories", {})),
        database=_build(DatabaseConfig, data.get("database")),
        logging=_build(LoggingConfig, data.get("logging")),
        admin=_build(AdminConfig, data.get("admin")),
    )

    _override_from_env(config)
    _ensure_admin_secrets(config)
    return config


def _override_from_env(config: Config) -> None:
    """Override config values from environment variables."""
    env_mapping = {
        "INSTAGRAM_APP_ID": ("instagram", "app_id"),
        "INSTAGRAM_APP_SECRET": ("instagram", "app_secret"),
        "INSTAGRAM_ACCESS_TOKEN": ("instagram", "access_token"),
        "INSTAGRAM_USER_ID": ("instagram", "user_id"),
        "PUBLIC_BASE_URL": ("instagram", "public_base_url"),
        "GRAPH_API_VERSION": ("instagram", "graph_api_version"),
        "AI_IMAGE_API_KEY": ("ai_image", "api_key"),
        "AI_IMAGE_LOCAL_PATH": ("ai_image", "local_path"),
        "DATABASE_PATH": ("database", "path"),
        "DB_PATH": ("database", "path"),
        "SECRET_KEY": ("admin", "secret_key"),
        "ADMIN_SECRET_KEY": ("admin", "secret_key"),
        "ADMIN_PASSWORD": ("admin", "password"),
        "LOG_LEVEL": ("logging", "level"),
        "LOG_FILE": ("logging", "file"),
    }
    for env_var, (section, key) in env_mapping.items():
        value = os.environ.get(env_var)
        if value:
            setattr(getattr(config, section), key, value)

    auto_post = os.environ.get("AUTO_POST")
    if auto_post is not None:
        config.automation.auto_post = auto_post.strip().lower() in ("1", "true", "yes", "on")

    port = os.environ.get("PORT")  # Render / Railway / Heroku provide this
    if port and port.isdigit():
        config.admin.port = int(port)


def _persisted_secret(filename: str, nbytes: int = 24) -> str:
    """Return a random secret that is generated once and stored in data/ (git-ignored)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    if path.exists():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            return value
    value = secrets.token_urlsafe(nbytes)
    path.write_text(value, encoding="utf-8")
    return value


def _ensure_admin_secrets(config: Config) -> None:
    """Never run with a guessable default key/password."""
    if not config.admin.secret_key or config.admin.secret_key == "change-this-secret-key":
        config.admin.secret_key = _persisted_secret(".secret_key", 32)
    if not config.admin.password:
        config.admin.password = _persisted_secret(".admin_password", 9)
        config.admin.password_generated = True  # type: ignore[attr-defined]


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


def project_path(relative: str) -> Path:
    """Resolve a project-relative path (data/, logs/, output/ ...) to an absolute one."""
    p = Path(relative)
    return p if p.is_absolute() else BASE_DIR / p
