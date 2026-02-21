"""Main entry point for fast-aiogentic Telegram bot."""

import asyncio
import logging
from pathlib import Path

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.types import BotCommand
from aiogram.types import BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

from fast_aiogentic.agent_bridge import AgentBridge
from fast_aiogentic.config import get_settings
from fast_aiogentic.handlers import register_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent


class FastAiogenticBot:
    """Main bot class managing lifecycle."""

    def __init__(self) -> None:
        self.bot = Bot(token=get_settings().telegram_bot_token)
        self.dp = Dispatcher()
        self.agent_bridge: AgentBridge | None = None

    async def setup(self) -> None:
        """Initialize bot components."""
        logger.info("Initializing fast-aiogentic bot...")

        self.agent_bridge = AgentBridge(
            config_path=PROJECT_ROOT / "fastagent.config.yaml",
            prompt_path=PROJECT_ROOT / "prompts" / "SYSTEM_PROMPT.md",
            server_names=["context7"],
            bot=self.bot,
        )
        await self.agent_bridge.initialize()

        register_handlers(self.dp, self.agent_bridge)

        await self.bot.delete_my_commands(scope=BotCommandScopeDefault())
        await self.bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="help", description="Show help"),
            ],
            scope=BotCommandScopeDefault(),
        )
        logger.info("Bot setup complete")

    async def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up...")
        if self.agent_bridge:
            for chat_id in list(self.agent_bridge._sessions):
                try:
                    await self.agent_bridge.end_persistent_session(chat_id)
                except (RuntimeError, OSError) as e:
                    logger.warning("Error ending session %d: %s", chat_id, e)
        await self.bot.session.close()

    async def run_webhook(self) -> None:
        """Run bot in webhook mode with aiohttp."""
        await self.setup()
        cfg = get_settings()

        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.bot.set_webhook(
            url=cfg.webhook_url,
            secret_token=cfg.webhook_secret or None,
            drop_pending_updates=True,
        )

        app = web.Application()

        async def health_handler(_request: web.Request) -> web.Response:
            return web.json_response({"status": "healthy"})

        app.router.add_get(cfg.health_path, health_handler)

        webhook_handler = SimpleRequestHandler(
            dispatcher=self.dp,
            bot=self.bot,
            secret_token=cfg.webhook_secret or None,
        )
        webhook_handler.register(app, path=cfg.webhook_path)
        setup_application(app, self.dp, bot=self.bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, cfg.webhook_host, cfg.webhook_port)
        await site.start()

        logger.info("Webhook mode running on %s:%d", cfg.webhook_host, cfg.webhook_port)

        try:
            await asyncio.Event().wait()
        finally:
            await self.cleanup()

    async def run_polling(self) -> None:
        """Run bot in polling mode (development)."""
        await self.setup()
        await self.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Polling mode started")
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        finally:
            await self.cleanup()


async def main() -> None:
    """Entry point."""
    bot = FastAiogenticBot()
    if get_settings().webhook_enabled:
        await bot.run_webhook()
    else:
        await bot.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
