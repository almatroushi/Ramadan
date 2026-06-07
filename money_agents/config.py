import os
from dataclasses import dataclass, field

@dataclass
class Config:
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

    # نشر المحتوى
    wordpress_url: str = field(default_factory=lambda: os.getenv("WORDPRESS_URL", ""))
    wordpress_token: str = field(default_factory=lambda: os.getenv("WORDPRESS_TOKEN", ""))

    # تحقيق الدخل
    amazon_affiliate_tag: str = field(default_factory=lambda: os.getenv("AMAZON_AFFILIATE_TAG", ""))
    sendgrid_api_key: str = field(default_factory=lambda: os.getenv("SENDGRID_API_KEY", ""))
    newsletter_list_id: str = field(default_factory=lambda: os.getenv("NEWSLETTER_LIST_ID", ""))

    # الجدولة
    posts_per_day: int = 3
    newsletter_day: str = "friday"  # يوم إرسال النشرة الأسبوعية

    # النيش المستهدف - مربح وعليه طلب بالعربي
    niches: list = field(default_factory=lambda: [
        "تقنية وأجهزة",
        "استثمار وأسهم",
        "سفر وفنادق",
        "صحة ورياضة",
        "منتجات منزلية",
    ])

CONFIG = Config()
