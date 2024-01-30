import asyncio
import sys
from os.path import abspath, dirname

import pytest_asyncio

d = dirname(dirname(abspath(__file__)))
sys.path.append(f"{d}\\")
sys.path.append(f"{d}\\src")

from tests.load_bot_from_pickle import get_map_specific_bot


@pytest_asyncio.fixture(scope="class")
async def bot(request):
    map_path = request.param
    bot = get_map_specific_bot(map_path)
    yield bot


@pytest_asyncio.fixture(scope="class")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
