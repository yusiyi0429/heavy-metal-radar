import json
import os
from datetime import datetime, timedelta, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
SEED_SHOWS = [
    {
        "_id": "seed001",
        "platform": "showstart",
        "showId": "999001",
        "title": "Arch Enemy 2026 北京专场",
        "artist": "Arch Enemy",
        "city": "北京",
        "venue": "疆进酒 OMNI SPACE",
        "date": "2026-08-15",
        "status": "on_sale",
        "url": "https://www.showstart.com/event/999001",
        "notified": False,
        "createdAt": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    },
    {
        "_id": "seed002",
        "platform": "damai",
        "showId": "999002",
        "title": "夜叉乐队 上海专场",
        "artist": "夜叉",
        "city": "上海",
        "venue": "MAO Livehouse",
        "date": "2026-09-10",
        "status": "upcoming",
        "url": "https://detail.damai.cn/item.htm?id=999002",
        "notified": False,
        "createdAt": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    },
    {
        "_id": "seed003",
        "platform": "showstart",
        "showId": "999003",
        "title": "郁乐队 新专辑巡演 广州站",
        "artist": "郁",
        "city": "广州",
        "venue": "SD Livehouse",
        "date": "2026-07-20",
        "status": "on_sale",
        "url": "https://www.showstart.com/event/999003",
        "notified": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    },
]

shows_path = os.path.join(DATA_DIR, "shows.json")
with open(shows_path, "w", encoding="utf-8") as f:
    json.dump(SEED_SHOWS, f, ensure_ascii=False, indent=2)

print(f"Seeded {len(SEED_SHOWS)} shows into {shows_path}")
