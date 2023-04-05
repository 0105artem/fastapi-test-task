import asyncio
from time import monotonic

from fastapi import APIRouter

from app.api.models import schemas

router = APIRouter()

lock = asyncio.Lock()


async def work() -> None:
    await asyncio.sleep(3)


@router.get("/test", response_model=schemas.TestResponse)
async def handler() -> schemas.TestResponse:
    ts1 = monotonic()

    async with lock:
        await work()

    ts2 = monotonic()
    return schemas.TestResponse(elapsed=ts2 - ts1)