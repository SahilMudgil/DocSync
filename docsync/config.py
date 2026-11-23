"""
Configuration loader for DocSync.
Reads config/default.yaml and merges environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_env_file():
    """Load key-value pairs from .env into os.environ if present."""
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()


def update_env_value(key: str, value: str) -> None:
    """Update or append a key-value pair in .env and os.environ."""
    os.environ[key] = value
    env_path = REPO_ROOT / ".env"
    lines = []
    found = False
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} "):
                lines.append(f"{key}={value}")
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f"{key}={value}")
    env_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


_load_env_file()


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load and return configuration dictionary from a YAML file."""
    if config_path is None:
        path = REPO_ROOT / "config" / "default.yaml"
    else:
        path = Path(config_path)

    if not path.exists():
        return {
            "project": {"name": "docsync"},
            "llm": {"provider": "fake", "model": "gemini-1.5-flash", "temperature": 0.0},
            "retrieval": {"top_k": 5, "rrf_k": 60, "use_sourcegraph": False},
            "analysis": {"ignore_paths": ["tests/", "venv/", ".git/"], "max_code_chars": 4000},
            "ci": {"fail_on_drift": False, "issue_min_confidence": 0.8},
        }

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    if os.getenv("DOCSYNC_LLM_PROVIDER"):
        cfg.setdefault("llm", {})["provider"] = os.getenv("DOCSYNC_LLM_PROVIDER")
    if os.getenv("DOCSYNC_LLM_MODEL"):
        cfg.setdefault("llm", {})["model"] = os.getenv("DOCSYNC_LLM_MODEL")

    return cfg


class Config:
    """Convenience wrapper for configuration dictionary."""

    @classmethod
    def from_env(cls, config_path: str = None) -> Dict[str, Any]:
        return load_config(config_path)
