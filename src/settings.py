from pydantic import BaseSettings

from src.base.fastapi_service import FastAPISettings
from src.base.mongo_service.config import MongoDBSettings
from src.imdb_client_service.config import IMDBClientSettings


class Settings(BaseSettings):
    mongo_db: MongoDBSettings
    imdb_api: IMDBClientSettings
    http: FastAPISettings = FastAPISettings()
    app_name: str = 'imdb_mongo'

    class Config:
        env_file = '.env.example', '.env'
        env_nested_delimiter = '__'


settings = Settings()
