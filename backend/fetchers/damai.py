import requests
from backend.fetchers.base import BaseFetcher


class DamaiFetcher(BaseFetcher):
    platform = "damai"

    def fetch_raw(self):
        results = []
        try:
            resp = requests.get(
                "https://search.damai.cn/searchajax.html",
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                    "Accept": "application/json",
                },
                params={"keyword": "演唱会", "currPage": 1, "pageSize": 50},
                timeout=15,
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            items = (
                data.get("pageData", {})
                .get("resultData", {})
                .get("itemList", data.get("pageData", []))
            )
            if isinstance(items, dict):
                items = items.get("itemList", [])

            for item in items:
                item_id = str(item.get("itemId", item.get("projectId", "")))
                results.append(
                    {
                        "showId": item_id,
                        "title": item.get("name", item.get("title", "")),
                        "artist": item.get("performerName", item.get("artistName", "")),
                        "city": item.get("cityname", item.get("cityName", "")),
                        "venue": item.get("venue", item.get("venueName", item.get("addr", ""))),
                        "date": item.get("showtime", item.get("showTime", "")),
                        "status": self._map_status(item),
                        "url": f"https://detail.damai.cn/item.htm?id={item_id}",
                    }
                )
        except Exception:
            pass
        return results

    def _map_status(self, item):
        status = item.get("saleStatus", item.get("status", ""))
        status_map = {
            "1": "on_sale",
            "2": "sold_out",
            "3": "upcoming",
            "on_sale": "on_sale",
            "sold_out": "sold_out",
            "presale": "upcoming",
        }
        return status_map.get(str(status), "upcoming")
