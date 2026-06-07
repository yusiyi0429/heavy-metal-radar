import requests
from backend.fetchers.base import BaseFetcher


class ShowstartFetcher(BaseFetcher):
    platform = "showstart"

    def fetch_raw(self):
        results = []
        try:
            resp = requests.get(
                "https://wap.showstart.com/api/performances/recommend",
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                    "Accept": "application/json",
                },
                params={"page": 1, "pageSize": 50},
                timeout=15,
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            items = data.get("data", {}).get("list", data.get("data", []))
            if isinstance(items, dict):
                items = items.get("list", [])

            for item in items:
                results.append(
                    {
                        "showId": str(item.get("id", item.get("performanceId", ""))),
                        "title": item.get("title", item.get("name", "")),
                        "artist": item.get("artistName", item.get("artist", "")),
                        "city": item.get("cityName", item.get("city", "")),
                        "venue": item.get("siteName", item.get("venueName", "")),
                        "date": item.get("showTime", item.get("startTime", "")),
                        "status": self._map_status(item),
                        "url": f"https://www.showstart.com/event/{item.get('id', item.get('performanceId', ''))}",
                    }
                )
        except Exception:
            pass
        return results

    def _map_status(self, item):
        status = item.get("status", item.get("ticketStatus", ""))
        status_map = {
            "1": "on_sale",
            "2": "sold_out",
            "3": "upcoming",
            "on_sale": "on_sale",
            "sold_out": "sold_out",
        }
        return status_map.get(str(status), "upcoming")
