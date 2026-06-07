"""
Master Orchestrator - العقل المسؤول عن كل شيء
يشغّل جميع الأجنتات بالتسلسل الصحيح 24/7
"""

import asyncio
import logging
import random
from datetime import datetime, time as dtime
from anthropic import AsyncAnthropic
import aiohttp

from config import CONFIG
from agents.scout_agent import run_scout
from agents.research_agent import run_research
from agents.writer_agent import run_writer
from agents.seo_agent import run_seo
from publishers.wordpress_publisher import WordPressPublisher, NewsletterPublisher
from monetization.revenue_tracker import RevenueTracker, run_strategy_optimizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("money_machine.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger("Orchestrator")


class MoneyMachineOrchestrator:
    """
    الأوركسترا الرئيسية - تدير كل شيء تلقائياً

    Pipeline لكل مقال:
    Scout → Research → Writer → SEO → Publisher → Revenue Tracker

    يشتغل ويكرر هذا {posts_per_day} مرات يومياً
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=CONFIG.anthropic_api_key)
        self.wp = WordPressPublisher(CONFIG.wordpress_url, CONFIG.wordpress_token)
        self.newsletter = NewsletterPublisher(
            CONFIG.sendgrid_api_key,
            CONFIG.newsletter_list_id
        )
        self.tracker = RevenueTracker()
        self.published_today: list[dict] = []

    async def produce_one_article(self, session: aiohttp.ClientSession) -> dict | None:
        """ينتج مقالاً واحداً كاملاً من الصفر للنشر"""

        # 1. Scout: اختر نيش عشوائي وابحث عن فرصة
        niche = random.choice(CONFIG.niches)
        logger.info(f"=== Starting pipeline | Niche: {niche} ===")

        try:
            opportunities = await run_scout(niche, self.client)
            if not opportunities:
                logger.warning("Scout found no opportunities, skipping")
                return None

            opportunity = opportunities[0]  # أفضل فرصة
            logger.info(f"Selected: {opportunity.get('topic')}")

            # 2. Research: ابحث بعمق
            research = await run_research(opportunity, self.client)

            # 3. Writer: اكتب المقال
            article = await run_writer(research, CONFIG.amazon_affiliate_tag, self.client)

            # 4. SEO: حسّن للبحث
            optimized = await run_seo(article, self.client)

            # 5. Publish: انشر
            if CONFIG.wordpress_url and CONFIG.wordpress_token:
                result = await self.wp.publish_article(optimized, session)
                post_url = result.get("url", "")
                self.tracker.record_article(optimized, post_url)
                optimized["url"] = post_url
                logger.info(f"Published at: {post_url}")
            else:
                logger.warning("WordPress not configured - article saved to log only")

            self.published_today.append(optimized)
            return optimized

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return None

    async def daily_run(self):
        """الروتين اليومي الكامل"""
        logger.info(f"=== Daily Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
        summary = self.tracker.get_summary()
        logger.info(f"Revenue so far: ${summary['total_revenue_usd']:.2f} total | "
                    f"${summary['this_month_total']:.2f} this month")

        async with aiohttp.ClientSession() as session:
            # نشر X مقال في اليوم مع فواصل زمنية طبيعية
            for i in range(CONFIG.posts_per_day):
                logger.info(f"Article {i+1}/{CONFIG.posts_per_day}")
                await self.produce_one_article(session)

                # انتظر بين المقالات (يبدو طبيعياً لجوجل)
                if i < CONFIG.posts_per_day - 1:
                    wait = random.randint(1800, 3600)  # 30-60 دقيقة
                    logger.info(f"Waiting {wait//60} minutes before next article...")
                    await asyncio.sleep(wait)

            # إرسال النشرة الأسبوعية كل جمعة
            if datetime.now().strftime("%A").lower() == CONFIG.newsletter_day:
                if self.published_today:
                    logger.info("Sending weekly newsletter...")
                    await self.newsletter.send_weekly_digest(self.published_today, session)

        # تحليل الأداء وتوصيات
        if self.published_today:
            strategy = await run_strategy_optimizer(self.tracker, self.client)
            logger.info(f"\n📊 Strategy Report:\n{strategy}\n")

        self.published_today.clear()
        logger.info("=== Daily Run Complete ===")

    async def run_forever(self):
        """يشتغل إلى الأبد - هذا هو المسؤول الوحيد"""
        logger.info("🚀 Money Machine started - Running autonomously 24/7")
        logger.info(f"Plan: {CONFIG.posts_per_day} articles/day | Niches: {CONFIG.niches}")

        while True:
            try:
                await self.daily_run()
            except Exception as e:
                logger.error(f"Daily run failed: {e}", exc_info=True)

            # انتظر حتى الغداء التالي (نشر في الوقت المناسب للقراء الخليجيين)
            now = datetime.now()
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now.hour >= 9:
                next_run = next_run.replace(day=now.day + 1)

            wait_seconds = (next_run - now).total_seconds()
            logger.info(f"Next run in {wait_seconds/3600:.1f} hours ({next_run.strftime('%Y-%m-%d %H:%M')})")
            await asyncio.sleep(wait_seconds)


async def main():
    machine = MoneyMachineOrchestrator()
    await machine.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
