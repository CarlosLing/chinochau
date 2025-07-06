"""
Translation API routes.
"""
from fastapi import APIRouter, Depends

from backend.auth import get_current_active_user
from backend.db import UserDB
from backend.models import TextInput
from backend.services.translation_service import TranslationService

router = APIRouter(tags=["translation"])


@router.post("/translate")
async def translate_api(
    data: TextInput, current_user: UserDB = Depends(get_current_active_user)
):
    """Return the English translation(s) for a given Chinese text."""
    result = await TranslationService.translate_text(data.chinese)
    return {"translation": result}


@router.post("/pinyin")
async def pinyin_api(
    data: TextInput, current_user: UserDB = Depends(get_current_active_user)
):
    """Return the pinyin for a given Chinese text."""
    result = await TranslationService.get_pinyin(data.chinese)
    return {"pinyin": result}
