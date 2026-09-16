import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/tkinter-github")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "token": "",
    "ssh_key_path": "",
    "theme": "dark",
    "username": "",
    "cache_dir": os.path.expanduser("~/.cache/tkinter-github"),
    "last_repo": "",
}


def ensure_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DEFAULT_CONFIG["cache_dir"], exist_ok=True)


def load_config():
    ensure_dirs()
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        merged = DEFAULT_CONFIG.copy()
        merged.update(cfg)
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg):
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
