import json
from typing import Any

from db.redis import redis_client
from fastapi.encoders import jsonable_encoder


class RedisCache:
    async def get(self, key: str) -> Any | None:
        data = await redis_client.get(name=key)
        if not data:
            return None
        return json.loads(data)

    async def set(self, key: str, value: Any) -> None:
        data = json.dumps(jsonable_encoder(value))
        await redis_client.set(name=key, value=data)

    async def delete_one(self, keys: list[str] | str) -> None:
        await redis_client.delete(*keys)

    async def delete_all(self, key: list[str]) -> None:
        keys = await redis_client.keys(f"{key}*")
        if keys:
            await redis_client.delete(*keys)


cache = RedisCache()
