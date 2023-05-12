from pydantic import BaseModel, MongoDsn, Field


class MongoDBSettings(BaseModel):

    dsn: MongoDsn = Field(
        description='Строка подключения к базе данных',
        example='mongodb://localhost:27017',
    )