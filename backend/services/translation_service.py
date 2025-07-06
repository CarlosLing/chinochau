"""
Service layer for translation operations.
"""
import pinyin
from fastapi.concurrency import run_in_threadpool

from chinochau.translate_google import translate_google


class TranslationService:
    """Service class for translation operations."""

    @staticmethod
    async def translate_text(chinese: str) -> str:
        """Return the English translation for a given Chinese text."""
        result = await translate_google(chinese)
        return result[0] if result else ""

    @staticmethod
    async def get_pinyin(chinese: str) -> str:
        """Return the pinyin for a given Chinese text."""
        result = await run_in_threadpool(pinyin.get, chinese)
        return result
