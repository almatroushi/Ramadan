"""
SEO Agent - يحسّن المحتوى للظهور في جوجل ويضيف schema markup
"""

import json
import logging
import re
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

SEO_SYSTEM = """أنت خبير SEO متخصص في المحتوى العربي وتحسين محركات البحث للسوق الخليجي.

مهمتك تحسين المقالات لـ:
1. الظهور في الصفحة الأولى جوجل للكلمات المفتاحية المستهدفة
2. زيادة نسبة النقر (CTR) من نتائج البحث
3. تحسين وقت البقاء على الصفحة

تعطي دائماً JSON منظم مع المقال المحسّن."""


async def run_seo(article: dict, client: AsyncAnthropic) -> dict:
    """
    يأخذ المقال ويحسّنه للـ SEO
    """
    logger.info(f"SEO optimizing: {article['title']}")

    response = await client.messages.create(
        model="claude-opus-4-8",
        max_tokens=5000,
        system=SEO_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""حسّن هذا المقال للـ SEO وأعده بصيغة JSON:

العنوان الحالي: {article['title']}
الكلمات المفتاحية: {', '.join(article.get('seo_keywords', []))}
Meta Description: {article.get('meta_description', '')}

المقال:
{article['content'][:3000]}...

أريد JSON بهذا الهيكل:
{{
  "seo_title": "عنوان محسّن (50-60 حرف)",
  "slug": "url-friendly-slug-arabic-or-english",
  "meta_description": "وصف محسّن (150-160 حرف)",
  "focus_keyword": "الكلمة المفتاحية الرئيسية",
  "secondary_keywords": ["كلمة1", "كلمة2"],
  "content_improvements": ["تحسين1", "تحسين2"],
  "internal_link_suggestions": ["موضوع مقال مرتبط 1", "موضوع مقال مرتبط 2"],
  "schema_type": "Article",
  "estimated_ranking_time": "X أسابيع"
}}"""
        }]
    )

    text = response.content[0].text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    seo_data = json.loads(text)

    # دمج كل شيء
    optimized = {**article, **seo_data}
    logger.info(f"SEO done: slug={seo_data.get('slug')}")
    return optimized
