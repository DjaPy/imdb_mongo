from src.base.aiohttp_client.client import BaseClient
from src.imdb_client_service.config import IMDBClientSettings


class IMDBApiException(RuntimeError):
    ...


class ClientIMDBApi(BaseClient[IMDBClientSettings, IMDBApiException]):
    client_name = 'imdb_api'

    async def get_movies(self, page: int = 1) -> list[dict]:
        ...
