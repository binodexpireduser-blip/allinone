import json
import os

CONFIG_FILE = "config.json"

def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {"default_channels": ["#chatwithworld"]}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {"default_channels": ["#chatwithworld"]}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
