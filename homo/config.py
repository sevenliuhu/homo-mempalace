"""
HOMO 配置管理 — DeepSeek 版记忆系统配置

配置优先级：环境变量 > 配置文件 > 默认值
"""

import json
import os
from pathlib import Path

HOMO_CONFIG_DIR = os.path.expanduser("~/.homo-mempalace")
HOMO_CONFIG_FILE = os.path.join(HOMO_CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "llm": "deepseek",
    "deepseek_api_key": "",
    "deepseek_api_base": "https://api.deepseek.com",
    "deepseek_model": "deepseek-chat",
    "embedding_model": "all-MiniLM-L6-v2",
    "palace_path": os.path.expanduser("~/.homo-mempalace/palace"),
    "use_local_llm": True,
    "ollama_base_url": "http://localhost:11434",
    "ollama_model": "deepseek-r1:7b",
    "language": "zh-CN",
    "auto_save": True,
    "auto_save_interval_min": 5,
}


class HomoConfig:
    """HOMO 配置管理器。"""

    def __init__(self, config_path=None):
        self.config_path = config_path or HOMO_CONFIG_FILE
        self._config = {}
        self._load()

    def _load(self):
        """加载配置文件。"""
        cfg = dict(DEFAULT_CONFIG)
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    file_cfg = json.load(f)
                cfg.update(file_cfg)
            except (json.JSONDecodeError, IOError):
                pass

        # 环境变量覆盖
        env_map = {
            "HOMO_LLM": "llm",
            "HOMO_DEEPSEEK_API_KEY": "deepseek_api_key",
            "HOMO_DEEPSEEK_API_BASE": "deepseek_api_base",
            "HOMO_DEEPSEEK_MODEL": "deepseek_model",
            "HOMO_PALACE_PATH": "palace_path",
            "HOMO_LANGUAGE": "language",
            "HOMO_OLLAMA_BASE_URL": "ollama_base_url",
            "HOMO_OLLAMA_MODEL": "ollama_model",
        }
        for env_key, config_key in env_map.items():
            val = os.environ.get(env_key)
            if val is not None:
                cfg[config_key] = val

        self._config = cfg

    def save(self):
        """保存当前配置到文件。"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        """获取配置项。"""
        return self._config.get(key, default)

    def set(self, key, value):
        """设置配置项并保存。"""
        self._config[key] = value
        self.save()

    def all(self):
        """返回所有配置（隐藏敏感字段）。"""
        cfg = dict(self._config)
        if cfg.get("deepseek_api_key"):
            cfg["deepseek_api_key"] = cfg["deepseek_api_key"][:8] + "..." + cfg["deepseek_api_key"][-4:]
        return cfg

    @property
    def palace_path(self):
        return self._config.get("palace_path", DEFAULT_CONFIG["palace_path"])

    @property
    def is_deepseek_api(self):
        return self._config.get("llm") == "deepseek" and bool(self._config.get("deepseek_api_key"))

    @property
    def is_local_llm(self):
        return self._config.get("use_local_llm", True)


# 全局单例
_config = None


def get_config():
    global _config
    if _config is None:
        _config = HomoConfig()
    return _config


def reset_config():
    global _config
    _config = None
