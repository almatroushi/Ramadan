"""
Writer Agent - يكتب محتوى عربي عالي الجودة يحقق مبيعات
"""

import logging
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

WRITER_SYSTEM = """أنت كاتب محتوى عربي محترف متخصص في المحتوى التسويقي والمربح.

أسلوبك:
- لغة عربية فصحى مريحة، بسيطة وواضحة (مش معقدة)
- تكتب بطريقة تقنع القارئ بالشراء بشكل طبيعي (مش مباشر)
- تبدأ بعنوان يشد الانتباه وتنهي بـ CTA واضح
- تذكر المنتجات بشكل مفيد وموضوعي (مش إعلان مباشر)
- تحافظ على SEO بدون حشو للكلمات

بنية المقال الدائمة:
1. مقدمة تثير فضول القارئ (150 كلمة)
2. صلب الموضوع مع نقاط واضحة
3. توصيات منتجات بصورة طبيعية
4. خلاصة + CTA للشراء أو الاشتراك"""


async def run_writer(research: dict, affiliate_tag: str, client: AsyncAnthropic) -> dict:
    """
    يكتب مقالاً كاملاً جاهزاً للنشر
    """
    topic = research.get("topic", "")
    products = research.get("products_to_mention", [])
    outline = research.get("article_outline", [])
    keywords = research.get("seo_keywords", [])

    logger.info(f"Writer starting: {topic}")

    # بناء جمل المنتجات مع روابط Amazon affiliate
    product_notes = ""
    if products:
        product_notes = "\n\nالمنتجات للذكر في المقال:\n"
        for p in products:
            search_url = f"https://www.amazon.ae/s?k={p.get('amazon_search', '').replace(' ', '+')}&tag={affiliate_tag}"
            product_notes += f"- {p['name']} (حوالي {p.get('price_aed', '')} درهم) | رابط: {search_url}\n"

    response = await client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4000,
        system=WRITER_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""اكتب مقالاً شاملاً بناءً على هذا البحث:

الموضوع: {topic}
الزاوية: {research.get('main_angle', '')}
الكلمات المفتاحية: {', '.join(keywords)}
Outline المطلوب: {' | '.join(outline)}
{product_notes}

المتطلبات:
- طول المقال: {research.get('target_word_count', 1500)} كلمة تقريباً
- أضف روابط المنتجات بشكل طبيعي ضمن النص (ليس كقائمة منفصلة)
- أول فقرة تحتوي الكلمة المفتاحية الرئيسية
- استخدم headings H2 و H3 بصيغة Markdown
- اختم بـ CTA طبيعي

اكتب المقال كاملاً الآن:"""
        }]
    )

    article_content = response.content[0].text.strip()

    result = {
        "title": research.get("original_opportunity", {}).get("suggested_title", topic),
        "content": article_content,
        "meta_description": research.get("meta_description", ""),
        "seo_keywords": keywords,
        "niche": research.get("original_opportunity", {}).get("niche", ""),
        "word_count": len(article_content.split()),
    }

    logger.info(f"Writer done: {result['word_count']} words for '{topic}'")
    return result
