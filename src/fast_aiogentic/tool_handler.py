"""Telegram tool execution handler for real-time progress indicators.

Implements fast-agent's ToolExecutionHandler protocol to show tool execution
progress in Telegram messages.
"""

import logging
import uuid
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from telegramify_markdown import markdownify

logger = logging.getLogger(__name__)

TOOL_EMOJIS: dict[str, str] = {
    "resolve-library-id": "\U0001f50d",
    "get-library-docs": "\U0001f4da",
    "query-docs": "\U0001f4da",
}


class TelegramToolHandler:
    """Tool execution handler that updates Telegram status messages.

    Shows real-time tool execution progress by editing a status message
    as tools start and complete.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.current_context: tuple[int, int] | None = None
        self.tool_history: list[tuple[str, str, str]] = []

    def set_context(self, chat_id: int, message_id: int) -> None:
        """Set the context for tool tracking."""
        self.current_context = (chat_id, message_id)
        self.tool_history = []

    def _get_emoji(self, tool_name: str) -> str:
        return TOOL_EMOJIS.get(tool_name, "\u2699\ufe0f")

    def _format_arguments(self, arguments: dict | None, max_length: int = 100) -> str:
        if not arguments:
            return ""
        parts = []
        for key, value in arguments.items():
            if value is None:
                continue
            val_str = value if isinstance(value, str) else str(value)
            parts.append(f"{key}={val_str}")
        if not parts:
            return ""
        args_str = ", ".join(parts)
        if len(args_str) > max_length:
            args_str = args_str[:max_length] + "..."
        return f" ({args_str})"

    async def on_tool_start(
        self,
        tool_name: str,
        server_name: str,
        arguments: dict | None,
        tool_use_id: str | None = None,
    ) -> str:
        """Called when tool execution starts."""
        tool_call_id = str(uuid.uuid4())

        if not self.current_context:
            return tool_call_id

        chat_id, msg_id = self.current_context
        emoji = self._get_emoji(tool_name)
        args_preview = self._format_arguments(arguments)
        self.tool_history.append((emoji, tool_name, args_preview))

        text = f"{emoji} {tool_name}{args_preview} running..."
        try:
            await self.bot.edit_message_text(
                markdownify(text),
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="MarkdownV2",
            )
        except TelegramAPIError as e:
            logger.warning("Failed to update status for tool start: %s", e)

        return tool_call_id

    async def on_tool_progress(
        self,
        tool_call_id: str,
        progress: int | float | None,
        total: int | float | None,
        message: str | None = None,
    ) -> None:
        """Called during tool execution with progress updates."""

    async def on_tool_complete(
        self,
        tool_call_id: str,
        success: bool,
        content: list[Any] | None,
        error: str | None = None,
    ) -> None:
        """Called when tool execution completes."""
        if not self.current_context:
            return

        chat_id, msg_id = self.current_context

        if success:
            tool_count = len(self.tool_history)
            if tool_count == 0:
                text = "\u2705 Tools complete"
            else:
                tools_lines = [f"{emoji} {name}{args}" for emoji, name, args in self.tool_history]
                tools_text = "\n".join(tools_lines)
                text = f"\u2705 Tools complete ({tool_count} calls)\n\n{tools_text}"
        else:
            error_msg = error[:100] if error else "Unknown error"
            text = f"\u26a0\ufe0f Tool failed: {error_msg}"

        try:
            await self.bot.edit_message_text(
                markdownify(text),
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode="MarkdownV2",
            )
        except TelegramAPIError as e:
            logger.warning("Failed to update status for tool complete: %s", e)
