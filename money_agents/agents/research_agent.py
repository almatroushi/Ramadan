"""
Research Agent - يبحث ويجمع المعلومات لكل موضوع
"""

import json
import logging
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

RESEARCH_SYSTEM = """أنت Research Agent - خبير في البحث وجمع المعلومات الدقيقة.

مهمتك:
1. جمع كل المعلومات اللازمة لكتابة مقال شامل ومفيد
2. تحديد أفضل المنتجات المرتبطة بالموضوع (مع أسعار تقريبية)
3. إيجاد زاوية فريدة تميز المحتوى عن المنافسين
4. تحضير outline كامل للمقال

دائماً أعطِ مخرجاتك بصيغة JSON."""

RESEARCH_SCHEMA = {
    "topic": "عنوان الموضوع",
    "main_angle": "الزاوية المميزة للمقال",
    "key_points": ["نقطة 1", "نقطة 2"],
    "products_to_mention": [
        {"name": "اسم المنتج", "price_aed": 0, "amazon_search": "كلمات البحث على أمازون"}
    ],
    "article_outline": ["قسم 1", "قسم 2"],
    "seo_keywords": ["كلمة1", "كلمة2"],
    "meta_description": "وصف الـ meta للسيو",
    "target_word_count": 1500
}


async def run_research(opportunity: dict, client: AsyncAnthropic) -> dict:
    """
    يأخذ فرصة من Scout ويجمع بحثاً شاملاً
    """
    topic = opportunity.get("topic", "")
    niche = opportunity.get("niche", "")
    logger.info(f"Research starting for: {topic}")

    response = await client.messages.create(
        model="claude-opus-4-8",
        max_tokens=3000,
        system=RESEARCH_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""ابحث بعمق في هذا الموضوع وحضّر كل ما يحتاجه الكاتب:

الموضوع: {topic}
النيش: {niche}
الكلمات المفتاحية المقترحة: {', '.join(opportunity.get('keywords', []))}

أريد:
1. أفضل زاوية لتناول الموضوع (تكون مفيدة ومميزة)
2. قائمة منتجات حقيقية يمكن ذكرها مع أسعارها بالدرهم الإماراتي
3. Outline كامل للمقال (1500-2000 كلمة)
4. كلمات مفتاحية SEO للسوق الخليجي
5. Meta description جاهزة

أعطني الإجابة بصيغة JSON فقط بنفس هيكل هذا المثال:
{json.dumps(RESEARCH_SCHEMA, ensure_ascii=False, indent=2)}"""
        }]
    )

    text = response.content[0].text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    research = json.loads(text)
    research["original_opportunity"] = opportunity
    logger.info(f"Research complete for: {topic}")
    return research
