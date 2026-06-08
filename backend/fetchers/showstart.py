import json
import logging
import subprocess
import os

import requests
from backend.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)

CITY_CODE_MAP = {
    "北京": "10", "上海": "21", "广州": "20", "深圳": "755", "成都": "28",
    "杭州": "571", "武汉": "27", "南京": "25", "西安": "29", "重庆": "23",
    "长沙": "731", "天津": "22", "沈阳": "24", "郑州": "371", "济南": "531",
    "青岛": "532", "大连": "411", "厦门": "592", "福州": "591", "苏州": "512",
    "合肥": "551", "昆明": "871", "贵阳": "851", "南宁": "771", "太原": "351",
    "长春": "431", "哈尔滨": "451", "石家庄": "311", "呼和浩特": "471", "银川": "951",
    "兰州": "931", "西宁": "971", "乌鲁木齐": "991", "拉萨": "891", "海口": "898",
    "南昌": "791", "无锡": "510", "宁波": "574", "温州": "577", "常州": "519",
    "珠海": "756", "东莞": "769", "佛山": "757", "中山": "760", "惠州": "752",
    "保定": "312", "廊坊": "316", "包头": "472", "鄂尔多斯": "477", "锦州": "416",
    "烟台": "535", "潍坊": "536", "洛阳": "379", "南通": "513", "扬州": "514",
    "徐州": "516", "日照": "633", "淄博": "533", "临沂": "539", "济宁": "537",
    "金华": "579", "绍兴": "575", "台州": "576", "嘉兴": "573", "湖州": "572",
    "芜湖": "553", "镇江": "511", "泰州": "523", "桂林": "773", "汕头": "754",
    "柳州": "772", "三亚": "899", "秦皇岛": "335", "运城": "359", "岳阳": "730",
    "株洲": "733", "湘潭": "732", "荆州": "716", "宜昌": "717", "襄阳": "710",
    "九江": "792", "赣州": "797", "遵义": "852", "大理": "872", "丽江": "888",
    "泉州": "595", "漳州": "596", "威海": "631", "盐城": "515", "延边": "433",
    "吉林": "432", "丹东": "415", "大庆": "459", "马鞍山": "555", "安庆": "556",
}

BASE_URL = "https://www.showstart.com/event/list"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

_EXTRACTOR = os.path.join(os.path.dirname(__file__), "_nuxt_extract.js")


class ShowstartFetcher(BaseFetcher):
    platform = "showstart"

    DEFAULT_STYLES = ["12", "24", "25"]  # 金属, 极端金属, 核

    def fetch_by_style(self, city_code: str = "", style: str = "12") -> list:
        """Fetch shows filtered by city and style (showStyle)."""
        params = {"pageSize": 200}
        if city_code:
            params["cityCode"] = city_code
        if style:
            params["showStyle"] = style
        try:
            resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return self._extract(resp.text)
        except Exception:
            logger.warning(
                "Showstart fetch failed (city=%s, style=%s)", city_code, style, exc_info=True
            )
        return []

    def _extract(self, html):
        try:
            proc = subprocess.run(
                ["node", _EXTRACTOR],
                input=html,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if proc.stderr:
                logger.warning("NUXT extract stderr: %s", proc.stderr.strip())
            return json.loads(proc.stdout.strip())
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            logger.warning("Showstart NUXT extraction failed", exc_info=True)
        return []

    def run(self, styles=None, cities=None):
        """Fetch by style + city, no keyword matching needed."""
        if styles is None:
            styles = self.DEFAULT_STYLES

        all_raw = []
        for style in styles:
            if cities:
                for city in cities:
                    code = CITY_CODE_MAP.get(city, "")
                    all_raw.extend(self.fetch_by_style(code, style))
            else:
                all_raw.extend(self.fetch_by_style("", style))

        if not all_raw:
            return []

        # Deduplicate across styles (a show can belong to multiple styles)
        seen_ids = set()
        deduped = []
        for s in all_raw:
            sid = s.get("showId")
            if sid not in seen_ids:
                seen_ids.add(sid)
                deduped.append(s)

        # City post-filter for cities without a known code
        if cities:
            deduped = [s for s in deduped if s.get("city") in cities]

        fresh = self.deduplicate(deduped)
        return self.save_and_return_new(fresh)
