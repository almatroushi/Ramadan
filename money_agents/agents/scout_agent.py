"""
Scout Agent - يكتشف المواضيع الرائجة والفرص المربحة
"""

import json
import logging
import aiohttp
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


SCOUT_SYSTEM = """أنت Scout Agent - مهمتك الوحيدة هي اكتشاف الفرص المربحة للمحتوى العربي.

قواعدك:
1. ابحث دائماً عن مواضيع فيها "نية شراء" عالية (الناس جاهزة تصرف فلوس)
2. فضّل المواضيع التي فيها منتجات يمكن وضع روابط affiliate عليها
3. ركّز على الجمهور الخليجي (UAE, KSA, Kuwait) - قوة شرائية عالية
4. أعطِ نتائجك دائماً بصيغة JSON منظمة

صيغة المخرجات:
{
  "opportunities": [
    {
      "topic": "عنوان الموضوع",
      "niche": "التصنيف",
      "search_volume": "عالي/متوسط/منخفض",
      "buying_intent": "عالي/متوسط",
      "affiliate_potential": "نعم/لا",
      "suggested_title": "عنوان مقال مقترح",
      "keywords": ["كلمة1", "كلمة2"],
      "estimated_monthly_revenue": "X دولار"
    }
  ]
}"""


async def run_scout(niche: str, client: AsyncAnthropic) -> list[dict]:
    """
    يفحص نيش معين ويرجع قائمة فرص مرتبة
    """
    logger.info(f"Scout scanning niche: {niche}")

    response = await client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        system=SCOUT_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""ابحث عن أفضل 5 فرص محتوى مربحة الآن في نيش: {niche}

المعايير:
- الموضوع رائج الآن أو موسمي قادم
- يمكن ربطه بمنتجات على Amazon أو برامج affiliate
- الجمهور خليجي/عربي
- المنافسة المحتوى العربي فيها ضعيفة أو متوسطة

أعطني النتائج بصيغة JSON فقط بدون أي نص إضافي."""
        }]
    )

    text = response.content[0].text.strip()
    # استخراج JSON
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    data = json.loads(text)
    opportunities = data.get("opportunities", [])
    logger.info(f"Scout found {len(opportunities)} opportunities in {niche}")
    return opportunities
