from src.base.aiohttp_client.config import ClientSettings


class IMDBClientSettings(ClientSettings):
    api_key: str
