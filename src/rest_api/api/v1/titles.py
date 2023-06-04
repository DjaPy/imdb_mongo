from aiomisc import get_context
from fastapi import APIRouter
from odmantic import AIOEngine

from src.collections import Title
from src.const import MONGO_DB
from src.rest_api.api.v1.response_schema import TitleResponseSchema, TitlesResponseSchema


title_router = APIRouter(prefix='/titles', tags=['titles'])


@title_router.get(
    path='/',
    response_model=TitlesResponseSchema,
    description='Получение списка произведений',
    summary='Получение списка произведений',
)
async def get_titles() -> TitlesResponseSchema:
    engine: AIOEngine = await get_context()[MONGO_DB]
    titles = await engine.find(Title, Title.title != "Starcraft", limit=100)
    return TitlesResponseSchema(titles=[TitleResponseSchema(**title.dict()) for title in titles])

