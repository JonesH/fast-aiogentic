"""Telegram message handlers for fast-aiogentic bot."""

import asyncio
import contextlib
import logging

from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from telegramify_markdown import markdownify

from fast_aiogentic.agent_bridge import AgentBridge
from fast_aiogentic.text_utils import split_for_telegram

logger = logging.getLogger(__name__)


async def continuous_typing_indicator(bot, chat_id: int, interval: float = 4.0) -> None:
    """Send typing indicator continuously until cancelled.

    Uses 4s interval (not 5) to stay within Telegram's 5s expiry window.
    """
    while True:
        await bot.send_chat_action(chat_id, "typing")
        await asyncio.sleep(interval)


def register_handlers(dp, agent_bridge: AgentBridge) -> None:
    """Register all handlers with dispatcher."""
    router = Router()

    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        text = (
            "Hey! I'm **fast-aiogentic** \u2014 your AI assistant powered by fast-agent.\n\n"
            "Send me any question and I'll use my tools to find the answer.\n\n"
            "**Commands:**\n"
            "/start \u2014 This message\n"
            "/help \u2014 Usage info"
        )
        await message.answer(markdownify(text), parse_mode="MarkdownV2")

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        text = (
            "**How to use:**\n\n"
            "Just send me a message and I'll respond using my AI agent.\n"
            "I can look up documentation, answer questions, and help with code.\n\n"
            "**Tips:**\n"
            "- Be specific about what library or topic\n"
            "- I'll show you which tools I'm using in real-time\n"
            "- Conversation history is maintained per chat"
        )
        await message.answer(markdownify(text), parse_mode="MarkdownV2")

    @router.message(F.text)
    async def handle_message(message: Message) -> None:
        """Handle regular text messages with agent responses."""
        chat_id = message.chat.id
        message_text = message.text or ""

        await agent_bridge.start_persistent_session(chat_id)

        typing_task = asyncio.create_task(continuous_typing_indicator(message.bot, chat_id, interval=4.0))

        status_message = await message.answer(markdownify("\U0001f504 Processing..."), parse_mode="MarkdownV2")

        full_response = ""
        try:
            async for chunk in agent_bridge.stream_in_session(
                chat_id, message_text, status_message_id=status_message.message_id
            ):
                full_response += chunk

            if full_response.strip():
                escaped_response = markdownify(full_response)
                chunks = split_for_telegram(escaped_response)
                for chunk in chunks:
                    await message.answer(chunk, parse_mode="MarkdownV2")
                with contextlib.suppress(Exception):
                    await status_message.delete()
            else:
                error_text = "\u274c No response generated. Try again!"
                await status_message.edit_text(markdownify(error_text), parse_mode="MarkdownV2")

        except Exception as e:
            logger.exception("Error during message handling: %s", type(e).__name__)
            error_text = f"\u274c Error: {type(e).__name__}: {e!s}"
            try:
                await status_message.edit_text(markdownify(error_text), parse_mode="MarkdownV2")
            except (RuntimeError, ValueError, OSError, ConnectionError):
                with contextlib.suppress(RuntimeError, ValueError, OSError, ConnectionError):
                    await message.answer(markdownify(error_text), parse_mode="MarkdownV2")
        finally:
            typing_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await typing_task

    dp.include_router(router)
