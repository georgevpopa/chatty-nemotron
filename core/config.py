"""Configuration manager — persistent settings in ~/.chatty-chronos/config.json."""
import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "provider": "nvidia",
    "model": "nvidia/llama-3.1-nemotron-70b-instruct",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "ollama_host": "http://localhost:11434",
    "llamacpp_host": "http://localhost:8080",
    "embedding_provider": "local",
    "embedding_model": "all-MiniLM-L6-v2",
    "streaming": True,
    "max_context_messages": 20,
    "local_server_enabled": False,
    "local_server_bin": "E:\\AI_Sandbox\\llama-b9672-bin-win-hip-radeon-x64\\llama-server.exe",
    "local_server_model": "",
    "local_server_port": 8080,
    "local_server_ngl": 99,
    "local_server_ctx": 16384,
    "local_server_parallel": 1,
    "local_server_reasoning_budget": 1024,
    "local_server_cache_ram": 512,
    "llamacpp_timeout": 600,
    "agent_max_iterations": 15,
    "local_server_env": {
        "HSA_OVERRIDE_GFX_VERSION": "11.0.2",
        "HIP_VISIBLE_DEVICES": "0"
    },
}


class Config:
    def __init__(self):
        self.dir = Path.home() / ".chatty-nemotron"
        self.dir.mkdir(exist_ok=True)
        self.path = self.dir / "config.json"
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path, "r") as f:
                saved = json.load(f)
            return {**DEFAULT_CONFIG, **saved}
        return dict(DEFAULT_CONFIG)

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()