"""AgentBridge for fast-agent + Telegram integration.

Manages agent lifecycle with long-lived run() contexts for the application lifetime.
Per-session conversation history via FastAgent's built-in history management.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING
from typing import Any

from fast_agent import FastAgent

from fast_aiogentic.config import get_settings
from fast_aiogentic.tool_handler import TelegramToolHandler

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from contextlib import AbstractAsyncContextManager
    from pathlib import Path

    from aiogram import Bot

logger = logging.getLogger(__name__)


class AgentSession:
    """Persistent agent session for a chat."""

    def __init__(self, chat_id: int, agent_instance: Any) -> None:  # noqa: ANN401
        self.chat_id = chat_id
        self.agent_instance = agent_instance
        self.lock = asyncio.Lock()


class AgentBridge:
    """Bridge between Telegram bot and fast-agent.

    Provides:
    - Persistent sessions per chat (conversation history)
    - Callback-based streaming -> async generator conversion
    - Tool execution tracking in Telegram messages
    - Proper async context manager lifecycle
    """

    def __init__(
        self,
        config_path: Path,
        prompt_path: Path,
        server_names: list[str] | None = None,
        bot: Bot | None = None,
    ) -> None:
        self.config_path = config_path
        self.prompt_path = prompt_path
        self.server_names = server_names or ["context7"]
        self.bot = bot
        self.agent: FastAgent | None = None
        self.tool_handler: TelegramToolHandler | None = None
        self.is_initialized = False
        self._sessions: dict[int, AgentSession] = {}
        self._context_managers: dict[int, AbstractAsyncContextManager[Any]] = {}

    async def initialize(self) -> None:
        """Initialize fast-agent from YAML config."""
        # CRITICAL: Set env var BEFORE FastAgent init for YAML substitution
        if not os.getenv("OPENROUTER_API_KEY"):
            os.environ["OPENROUTER_API_KEY"] = get_settings().openrouter_api_key

        self.agent = FastAgent(
            name="fast-aiogentic",
            config_path=str(self.config_path),
            parse_cli_args=False,
            quiet=True,
        )

        @self.agent.agent(
            instruction=self.prompt_path,
            servers=self.server_names,
        )
        async def assistant() -> None:
            pass

        if self.bot:
            self.tool_handler = TelegramToolHandler(self.bot)

        self.is_initialized = True
        logger.info("AgentBridge initialized")

    async def start_persistent_session(self, chat_id: int) -> None:
        """Start persistent session for a chat.

        Keeps agent.run() context alive to maintain conversation history.
        """
        if chat_id in self._sessions:
            return

        if self.agent is None:
            msg = "AgentBridge not initialized"
            raise RuntimeError(msg)

        cm = self.agent.run()
        agent_instance = await cm.__aenter__()

        # Enable auto-tool-execution
        if hasattr(agent_instance, "_context") and agent_instance._context:
            agent_instance._context.shell_runtime = True

        # Inject tool handler
        if self.tool_handler:
            try:
                first_key = next(iter(agent_instance._agents.keys()))
                agent_obj = agent_instance._agents[first_key]
                if hasattr(agent_obj, "_aggregator"):
                    agent_obj._aggregator._tool_handler = self.tool_handler
                    logger.info("Tool handler injected for chat %d", chat_id)
            except (KeyError, AttributeError, StopIteration):
                logger.warning("Failed to inject tool handler for chat %d", chat_id)

        self._context_managers[chat_id] = cm
        self._sessions[chat_id] = AgentSession(chat_id, agent_instance)

    async def end_persistent_session(self, chat_id: int) -> None:
        """End persistent session for a chat."""
        if chat_id not in self._sessions:
            return
        cm = self._context_managers[chat_id]
        await cm.__aexit__(None, None, None)
        del self._sessions[chat_id]
        del self._context_managers[chat_id]

    async def stream_in_session(
        self,
        chat_id: int,
        message: str,
        status_message_id: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream response from agent within persistent session."""
        if chat_id not in self._sessions:
            msg = f"No active session for chat {chat_id}"
            raise ValueError(msg)

        session = self._sessions[chat_id]

        if self.tool_handler and status_message_id:
            self.tool_handler.set_context(chat_id, status_message_id)

        async with session.lock:
            chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()
            _background_tasks: set[asyncio.Task[None]] = set()

            def stream_callback(chunk: str) -> None:
                task = asyncio.create_task(chunk_queue.put(chunk))
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)

            first_key = next(iter(session.agent_instance._agents.keys()))
            agent = session.agent_instance._agents[first_key]
            remove_listener = agent.llm.add_stream_listener(stream_callback)

            try:
                response_task = asyncio.create_task(session.agent_instance.send(message))

                while True:
                    try:
                        chunk = await asyncio.wait_for(chunk_queue.get(), timeout=0.1)
                        if chunk is None:
                            break
                        yield chunk
                    except TimeoutError:
                        if response_task.done():
                            while not chunk_queue.empty():
                                chunk = await chunk_queue.get()
                                if chunk is not None:
                                    yield chunk
                            break

                await response_task
            finally:
                remove_listener()
                await chunk_queue.put(None)
