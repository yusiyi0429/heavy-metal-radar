import time
import logging
import schedule
from backend.db import get_config
from backend.fetchers import ShowstartFetcher, DamaiFetcher
from backend.notifier.wecom_bot import notify_new_shows

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_all():
    cfg = get_config()
    keywords = cfg.get("keywords", [])
    cities = cfg.get("cities", [])
    webhook_url = cfg.get("webhook_url", "")

    logger.info("开始抓取...")
    ss = ShowstartFetcher()
    ss_new = ss.run(keywords)
    if cities:
        ss_new = [s for s in ss_new if s.get("city") in cities]

    dm = DamaiFetcher()
    dm_new = dm.run(keywords)
    if cities:
        dm_new = [s for s in dm_new if s.get("city") in cities]

    all_new = ss_new + dm_new
    logger.info(f"发现 {len(all_new)} 场新演出 (秀动:{len(ss_new)}, 大麦:{len(dm_new)})")

    if all_new and cfg.get("enable_push"):
        unnotified = [s for s in all_new if not s.get("notified")]
        count = notify_new_shows(unnotified, webhook_url)
        logger.info(f"已推送 {count} 条通知")


if __name__ == "__main__":
    interval_hours = 6
    schedule.every(interval_hours).hours.do(run_all)
    logger.info(f"调度器启动，每 {interval_hours} 小时执行一次")
    run_all()
    while True:
        schedule.run_pending()
        time.sleep(60)
