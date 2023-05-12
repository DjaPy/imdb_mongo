from pydantic import BaseSettings

from src.base.mongo_service.config import MongoDBSettings


class Settings(BaseSettings):
    mongo_db: MongoDBSettings

    class Config:
        env_file = '.env.example', '.env'
        env_nested_delimiter = '__'
