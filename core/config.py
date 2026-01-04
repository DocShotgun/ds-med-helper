"""Configuration Loading and Saving"""

import yaml
from pathlib import Path


def load_config() -> dict:
    """Load configuration from config.yaml"""
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def save_config(config: dict) -> None:
    """Save configuration to config.yaml"""
    with open("config.yaml", 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
