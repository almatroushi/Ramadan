"""
Revenue Tracker - يتابع الأرباح ويحسّن الاستراتيجية
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "revenue.json"


class RevenueTracker:
    """يتتبع الأرباح ويقترح تحسينات تلقائية"""

    def __init__(self):
        DATA_FILE.parent.mkdir(exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if DATA_FILE.exists():
            return json.loads(DATA_FILE.read_text())
        return {"articles": [], "total_revenue_usd": 0, "monthly": {}}

    def _save(self):
        DATA_FILE.write_text(json.dumps(self._data, ensure_ascii=False, indent=2))

    def record_article(self, article: dict, post_url: str):
        """يسجل مقال منشور جديد"""
        record = {
            "title": article.get("seo_title") or article.get("title"),
            "url": post_url,
            "niche": article.get("niche"),
            "published_at": datetime.now().isoformat(),
            "clicks": 0,
            "affiliate_revenue_usd": 0,
            "ad_revenue_usd": 0,
        }
        self._data["articles"].append(record)
        self._save()
        logger.info(f"Recorded: {record['title']}")

    def update_revenue(self, article_url: str, affiliate: float = 0, ads: float = 0):
        """يحدّث إيرادات مقال موجود"""
        for a in self._data["articles"]:
            if a["url"] == article_url:
                a["affiliate_revenue_usd"] += affiliate
                a["ad_revenue_usd"] += ads
                break

        month = date.today().strftime("%Y-%m")
        self._data["monthly"].setdefault(month, {"affiliate": 0, "ads": 0})
        self._data["monthly"][month]["affiliate"] += affiliate
        self._data["monthly"][month]["ads"] += ads
        self._data["total_revenue_usd"] += affiliate + ads
        self._save()

    def get_summary(self) -> dict:
        month = date.today().strftime("%Y-%m")
        monthly = self._data["monthly"].get(month, {"affiliate": 0, "ads": 0})
        top_articles = sorted(
            self._data["articles"],
            key=lambda x: x["affiliate_revenue_usd"] + x["ad_revenue_usd"],
            reverse=True
        )[:5]

        return {
            "total_articles": len(self._data["articles"]),
            "total_revenue_usd": self._data["total_revenue_usd"],
            "this_month_affiliate": monthly["affiliate"],
            "this_month_ads": monthly["ads"],
            "this_month_total": monthly["affiliate"] + monthly["ads"],
            "top_articles": [
                {
                    "title": a["title"],
                    "revenue": a["affiliate_revenue_usd"] + a["ad_revenue_usd"]
                }
                for a in top_articles
            ]
        }


async def run_strategy_optimizer(tracker: RevenueTracker, client: AsyncAnthropic) -> str:
    """
    Strategy Agent - يحلل الأداء ويقترح تحسينات للأسبوع القادم
    """
    summary = tracker.get_summary()

    response = await client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""أنت مستشار تسويق رقمي محترف. حلّل هذا الأداء واقترح استراتيجية الأسبوع القادم:

الإحصائيات:
{json.dumps(summary, ensure_ascii=False, indent=2)}

أريد:
1. تحليل قصير للأداء (2-3 جمل)
2. أي أنواع المحتوى تحقق أعلى دخل
3. 3 توصيات محددة للأسبوع القادم
4. النيش الذي يجب التركيز عليه

الجواب بالعربية، مباشر وعملي."""
        }]
    )

    return response.content[0].text
