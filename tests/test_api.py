import asyncio
from asyncio import AbstractEventLoop

import pytest
import httpx

from main import app
from app.core.config import env


@pytest.fixture(scope='session')
def event_loop() -> AbstractEventLoop:
    """
    Fixture for creating and closing brand-new event loop for testing session.
    With it, each running test will use only one event loop.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_hello():
    url = f"http://{env.HOSTNAME}:{env.PORT}/"

    async with httpx.AsyncClient(app=app) as client:
        resp = await client.get(url)

    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello World!"


@pytest.mark.asyncio
@pytest.mark.parametrize("num_requests", [2, 4, 8])
async def test_concurrent_requests(num_requests: int, event_loop: AbstractEventLoop) -> None:
    """
    Sends several concurrent GET requests to /test endpoint. Test will pass if
    the response time between requests at least 3 seconds.
    :param num_requests: Number of concurrent sent requests.
    """
    url = f"http://{env.HOSTNAME}:{env.PORT}/test"

    async with httpx.AsyncClient(app=app) as client:
        tasks = [asyncio.ensure_future(client.get(url), loop=event_loop) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 200

    for i in range(len(responses)-1):
        time_i = responses[i].json()['elapsed']
        time_j = responses[i+1].json()['elapsed']
        assert time_j - time_i >= 3
