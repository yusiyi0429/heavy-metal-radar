import uuid
from datetime import datetime, timezone
from backend.db import get_shows, upsert_show


def _make_id():
    return uuid.uuid4().hex[:16]


class BaseFetcher:
    platform = "unknown"

    def fetch_raw(self):
        raise NotImplementedError

    def match_keywords(self, raw_list, keywords):
        if not keywords:
            return raw_list
        matched = []
        for item in raw_list:
            text = (item.get("title", "") + " " + item.get("artist", "")).lower()
            if any(kw.lower() in text for kw in keywords):
                matched.append(item)
        return matched

    def deduplicate(self, raw_list):
        existing, _ = get_shows()
        seen = {(s["platform"], s["showId"]) for s in existing}
        return [r for r in raw_list if (self.platform, r["showId"]) not in seen]

    def save_and_return_new(self, shows):
        new_shows = []
        for s in shows:
            s.setdefault("platform", self.platform)
            s.setdefault("_id", _make_id())
            s.setdefault("notified", False)
            s.setdefault("createdAt", datetime.now(timezone.utc).isoformat())
            is_new = upsert_show(s)
            if is_new:
                new_shows.append(s)
        return new_shows

    def run(self, keywords):
        raw = self.fetch_raw()
        if not raw:
            return []
        matched = self.match_keywords(raw, keywords)
        fresh = self.deduplicate(matched)
        return self.save_and_return_new(fresh)
