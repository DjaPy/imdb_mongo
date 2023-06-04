from aiomisc import entrypoint

from src.base.mongo_service.service import MongoDBService
from src.const import MONGO_DB, FASTAPI_SERVICE
from src.rest_api.api.v1.router import imdb_router
from src.settings import settings
from src.base.fastapi_service import FastAPIService


fastapi_service = FastAPIService(settings=settings.http, context_name=FASTAPI_SERVICE, app_name=settings.app_name)
mongodb = MongoDBService(settings=settings.mongo_db, context_name=MONGO_DB)

if __name__ == '__main__':
    with entrypoint(
        fastapi_service,
        mongodb,
    ) as loop:
        fastapi_service.fastapi.include_router(imdb_router)
        loop.run_forever()
