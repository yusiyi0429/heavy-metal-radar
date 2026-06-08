import json
import os
import threading

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
SHOWS_PATH = os.path.join(DATA_DIR, "shows.json")

_lock = threading.RLock()


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_config():
    defaults = {
        "keywords": [],
        "cities": [],
        "enable_push": True,
        "push_type": "wecom_bot",
        "webhook_url": "",
    }
    with _lock:
        cfg = _read_json(CONFIG_PATH, defaults)
        for k, v in defaults.items():
            if k not in cfg:
                cfg[k] = v
        return cfg


def set_config(updates: dict):
    with _lock:
        cfg = get_config()
        for k in ("keywords", "cities", "enable_push", "push_type", "webhook_url"):
            if k in updates:
                cfg[k] = updates[k]
        _write_json(CONFIG_PATH, cfg)
        return cfg


def get_shows(city=None, keyword=None, status=None, limit=None, offset=0):
    with _lock:
        shows = _read_json(SHOWS_PATH, [])

    if city:
        shows = [s for s in shows if s.get("city") == city]
    if keyword:
        kw = keyword.lower()
        shows = [
            s
            for s in shows
            if kw in s.get("title", "").lower() or kw in s.get("artist", "").lower()
        ]
    if status:
        shows = [s for s in shows if s.get("status") == status]

    shows.sort(key=lambda s: s.get("createdAt", ""), reverse=True)
    total = len(shows)
    if limit is not None:
        shows = shows[offset : offset + limit]
    return shows, total


def upsert_show(show: dict):
    with _lock:
        shows = _read_json(SHOWS_PATH, [])
        for i, existing in enumerate(shows):
            if (
                existing.get("platform") == show.get("platform")
                and existing.get("showId") == show.get("showId")
            ):
                shows[i] = {**existing, **show}
                _write_json(SHOWS_PATH, shows)
                return False
        shows.append(show)
        _write_json(SHOWS_PATH, shows)
        return True


def mark_notified(show_ids: list[str]):
    with _lock:
        shows = _read_json(SHOWS_PATH, [])
        for s in shows:
            if s["_id"] in show_ids:
                s["notified"] = True
        _write_json(SHOWS_PATH, shows)


def reset_shows():
    with _lock:
        _write_json(SHOWS_PATH, [])
