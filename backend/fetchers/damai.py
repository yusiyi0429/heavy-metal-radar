from backend.fetchers.base import BaseFetcher


class DamaiFetcher(BaseFetcher):
    """大麦暂不可用 — mtop 签名 + 滑块验证码成本过高。"""

    platform = "damai"

    def fetch_raw(self):
        return []

    def run(self, keywords):
        return []
