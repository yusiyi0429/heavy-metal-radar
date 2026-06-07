import requests


def send_show_notification(show, webhook_url):
    if not webhook_url or webhook_url == "YOUR_WECOM_WEBHOOK_KEY_HERE":
        return False

    status_label = {"on_sale": "售票中", "upcoming": "即将开票", "sold_out": "已售罄"}
    status = status_label.get(show.get("status", ""), show.get("status", ""))

    emoji_map = {"showstart": "🎸", "damai": "🎫"}
    emoji = emoji_map.get(show.get("platform", ""), "🎵")

    content = (
        f"## {emoji} 新演出发现！\n"
        f"> **艺人**：{show.get('artist', show.get('title', '未知'))}\n"
        f"> **演出**：{show.get('title', '')}\n"
        f"> **城市**：{show.get('city', '未知')}\n"
        f"> **场地**：{show.get('venue', '未知')}\n"
        f"> **日期**：{show.get('date', '未知')}\n"
        f"> **状态**：{status}\n"
        f"> **平台**：{show.get('platform', '')}\n"
        f"\n"
        f"[点击购票]({show.get('url', '')})"
    )

    try:
        resp = requests.post(
            webhook_url,
            json={
                "msgtype": "markdown",
                "markdown": {"content": content},
            },
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("errcode") == 0
    except Exception:
        return False


def notify_new_shows(shows, webhook_url):
    if not shows:
        return 0
    notified = 0
    for s in shows:
        if not s.get("notified") and not s.get("notified_at"):
            ok = send_show_notification(s, webhook_url)
            if ok:
                notified += 1
    return notified
