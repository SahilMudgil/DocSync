"""
Configuration loader for DocSync.
Reads config/default.yaml and merges environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml


def _load_env_file():
    """Load key-value pairs from .env into os.environ if present."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env_file()


def load_config(config_path: str = "config/default.yaml") -> Dict[str, Any]:
    """Load and return configuration dictionary from a YAML file."""
    path = Path(config_path)
    if not path.exists():
        # Fallback to defaults
        return {
            "project": {"name": "docsync"},
            "llm": {"provider": "fake", "model": "gemini-1.5-flash", "temperature": 0.0},
            "retrieval": {"top_k": 5, "rrf_k": 60, "use_sourcegraph": False},
            "analysis": {"ignore_paths": ["tests/", "venv/", ".git/"], "max_code_chars": 4000},
            "ci": {"fail_on_drift": False, "issue_min_confidence": 0.8},
        }

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Override model / provider from environment if set
    if os.getenv("DOCSYNC_LLM_PROVIDER"):
        cfg.setdefault("llm", {})["provider"] = os.getenv("DOCSYNC_LLM_PROVIDER")
    if os.getenv("DOCSYNC_LLM_MODEL"):
        cfg.setdefault("llm", {})["model"] = os.getenv("DOCSYNC_LLM_MODEL")

    return cfg
