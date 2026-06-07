from flask import Flask, request, jsonify
from backend.db import get_config, set_config, get_shows, mark_notified, reset_shows
from backend.fetchers import ShowstartFetcher, DamaiFetcher
from backend.notifier.wecom_bot import notify_new_shows

app = Flask(__name__)


def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.after_request
def after_request(response):
    return _cors(response)


@app.route("/api/health")
def health():
    return jsonify({"ok": True, "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()})


@app.route("/api/config", methods=["GET", "PUT"])
def config():
    if request.method == "GET":
        return jsonify(get_config())
    updates = request.get_json(silent=True) or {}
    allowed = {"keywords", "cities", "enable_push", "push_type", "webhook_url"}
    filtered = {k: v for k, v in updates.items() if k in allowed}
    cfg = set_config(filtered)
    return jsonify(cfg)


@app.route("/api/shows")
def list_shows():
    city = request.args.get("city")
    keyword = request.args.get("keyword")
    status = request.args.get("status")
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", 0, type=int)
    shows, total = get_shows(city=city, keyword=keyword, status=status, limit=limit, offset=offset)
    return jsonify({"shows": shows, "total": total})


@app.route("/api/fetch", methods=["POST"])
def fetch():
    cfg = get_config()
    keywords = cfg.get("keywords", [])
    cities = cfg.get("cities", [])

    ss = ShowstartFetcher()
    ss_new = ss.run(keywords)
    if cities:
        ss_new = [s for s in ss_new if s.get("city") in cities]

    dm = DamaiFetcher()
    dm_new = dm.run(keywords)
    if cities:
        dm_new = [s for s in dm_new if s.get("city") in cities]

    return jsonify(
        {
            "new_count": len(ss_new) + len(dm_new),
            "platforms": {"showstart": len(ss_new), "damai": len(dm_new)},
        }
    )


@app.route("/api/notify", methods=["POST"])
def notify():
    cfg = get_config()
    if not cfg.get("enable_push"):
        return jsonify({"notified_count": 0, "message": "推送已关闭"})
    shows, _ = get_shows()
    unnotified = [s for s in shows if not s.get("notified")]
    count = notify_new_shows(unnotified, cfg.get("webhook_url", ""))
    if count > 0:
        mark_notified([s["_id"] for s in unnotified[:count]])
    return jsonify({"notified_count": count})


@app.route("/api/reset", methods=["POST"])
def reset():
    reset_shows()
    return jsonify({"ok": True})


if __name__ == "__main__":
    import os
    from datetime import datetime, timezone
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="127.0.0.1", port=5001, debug=debug)
