import yaml
from pathlib import Path
from .models import AppConfig

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> AppConfig:
    """Load config from YAML file. Returns default config if file doesn't exist."""
    if not CONFIG_PATH.exists():
        return AppConfig()
    with open(CONFIG_PATH) as f:
        data = yaml.safe_load(f) or {}
    return AppConfig(**data)


def save_config(config: AppConfig):
    """Save config to YAML file."""
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(
            config.model_dump(),
            f,
            default_flow_style=False,
            sort_keys=False,
        )
