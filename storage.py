import json
import os
import threading

import config

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")

_lock = threading.Lock()


def _default_data():
    return {
        "default_channels": [config.DEFAULT_CHANNEL],
        "disabled_channels": []
    }


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def _save_json(path, data):
    with _lock:
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)


def get_channels():
    data = _load_json(CHANNELS_FILE, _default_data())
    # make sure keys always exist even if file was hand-edited
    data.setdefault("default_channels", [config.DEFAULT_CHANNEL])
    data.setdefault("disabled_channels", [])
    return data


def save_channels(data):
    _save_json(CHANNELS_FILE, data)


def add_default_channel(channel):
    data = get_channels()
    existing = [c.lower() for c in data["default_channels"]]
    if channel.lower() not in existing:
        data["default_channels"].append(channel)
        save_channels(data)
        return True
    return False


def remove_default_channel(channel):
    if channel.lower() == config.DEFAULT_CHANNEL.lower():
        return "protected"
    data = get_channels()
    before = len(data["default_channels"])
    data["default_channels"] = [
        c for c in data["default_channels"] if c.lower() != channel.lower()
    ]
    if len(data["default_channels"]) < before:
        save_channels(data)
        return True
    return False


def is_channel_disabled(channel):
    data = get_channels()
    return channel.lower() in [c.lower() for c in data["disabled_channels"]]


def set_channel_enabled(channel, enabled):
    data = get_channels()
    disabled_lower = [c.lower() for c in data["disabled_channels"]]
    ch_lower = channel.lower()
    if enabled:
        if ch_lower in disabled_lower:
            data["disabled_channels"] = [
                c for c in data["disabled_channels"] if c.lower() != ch_lower
            ]
            save_channels(data)
    else:
        if ch_lower not in disabled_lower:
            data["disabled_channels"].append(channel)
            save_channels(data)
