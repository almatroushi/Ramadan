"""
WordPress Publisher - ينشر المقالات تلقائياً على WordPress
"""

import base64
import logging
import aiohttp

logger = logging.getLogger(__name__)


class WordPressPublisher:
    """ينشر المقال على WordPress بدون تدخل"""

    def __init__(self, site_url: str, token: str):
        self.api_base = f"{site_url.rstrip('/')}/wp-json/wp/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_or_create_category(
        self,
        niche: str,
        session: aiohttp.ClientSession
    ) -> int:
        """يجيب أو يصنع تصنيف للنيش"""
        async with session.get(
            f"{self.api_base}/categories",
            headers=self.headers,
            params={"search": niche}
        ) as resp:
            cats = await resp.json()
            if cats:
                return cats[0]["id"]

        # إنشاء تصنيف جديد
        async with session.post(
            f"{self.api_base}/categories",
            headers=self.headers,
            json={"name": niche}
        ) as resp:
            data = await resp.json()
            return data["id"]

    async def publish_article(
        self,
        article: dict,
        session: aiohttp.ClientSession,
        status: str = "publish"
    ) -> dict:
        """ينشر المقال الكامل"""

        cat_id = await self.get_or_create_category(
            article.get("niche", "عام"),
            session
        )

        payload = {
            "title": article.get("seo_title") or article.get("title"),
            "content": article.get("content"),
            "status": status,
            "slug": article.get("slug", ""),
            "excerpt": article.get("meta_description", ""),
            "categories": [cat_id],
            "meta": {
                "_yoast_wpseo_title": article.get("seo_title", ""),
                "_yoast_wpseo_metadesc": article.get("meta_description", ""),
                "_yoast_wpseo_focuskw": article.get("focus_keyword", ""),
            }
        }

        async with session.post(
            f"{self.api_base}/posts",
            headers=self.headers,
            json=payload
        ) as resp:
            result = await resp.json()
            post_url = result.get("link", "")
            post_id = result.get("id")
            logger.info(f"Published: {post_url}")
            return {"post_id": post_id, "url": post_url, "status": status}


class NewsletterPublisher:
    """يرسل النشرة الأسبوعية عبر SendGrid"""

    def __init__(self, api_key: str, list_id: str, sender_email: str = "noreply@yourdomain.com"):
        self.api_key = api_key
        self.list_id = list_id
        self.sender_email = sender_email
        self.base_url = "https://api.sendgrid.com/v3"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def send_weekly_digest(
        self,
        articles: list[dict],
        session: aiohttp.ClientSession
    ) -> bool:
        """يجمع أفضل مقالات الأسبوع ويرسلها"""

        html_content = self._build_newsletter_html(articles)

        payload = {
            "personalizations": [{"to": [{"email": self.sender_email}]}],
            "from": {"email": self.sender_email, "name": "نشرتي الأسبوعية"},
            "subject": f"أفضل {len(articles)} مقالات هذا الأسبوع ✨",
            "content": [{"type": "text/html", "value": html_content}],
            "mail_settings": {"sandbox_mode": {"enable": False}},
        }

        async with session.post(
            f"{self.base_url}/mail/send",
            headers=self.headers,
            json=payload
        ) as resp:
            success = resp.status == 202
            logger.info(f"Newsletter sent: {success}")
            return success

    def _build_newsletter_html(self, articles: list[dict]) -> str:
        items = ""
        for a in articles:
            items += f"""
            <div style="margin-bottom:30px;border-bottom:1px solid #eee;padding-bottom:20px;">
              <h2 style="color:#333;font-size:20px;">{a.get('seo_title') or a.get('title')}</h2>
              <p style="color:#666;">{a.get('meta_description','')}</p>
              <a href="{a.get('url','#')}"
                 style="background:#FF6B35;color:white;padding:10px 20px;
                        text-decoration:none;border-radius:5px;display:inline-block;">
                اقرأ المقال كاملاً
              </a>
            </div>"""

        return f"""
        <html dir="rtl">
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
          <h1 style="color:#FF6B35;text-align:center;">🔥 أفضل مقالات الأسبوع</h1>
          {items}
          <p style="color:#999;font-size:12px;text-align:center;">
            <a href="{{{{unsubscribe}}}}">إلغاء الاشتراك</a>
          </p>
        </body>
        </html>"""
