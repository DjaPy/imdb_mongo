from aiomisc import Service
from motor.motor_asyncio import AsyncIOMotorClient


class MongoService(Service):

    _mongo: AsyncIOMotorClient

    async def start(self) -> None:
        self._mongo = AsyncIOMotorClient()

    async def stor(self) -> None:
        ...