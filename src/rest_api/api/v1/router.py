from fastapi import APIRouter

from src.rest_api.api.v1.titles import title_router

imdb_router = APIRouter(prefix='/api/v1/imdb', tags=['imdb'])
imdb_router.include_router(title_router)

