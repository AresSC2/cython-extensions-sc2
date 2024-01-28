"""
Sanity test
Use this to test your environment is setup
And that some cython functions are working
"""

from random import choice

from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2 import maps
from sc2.player import Bot, Computer

from cython_extensions import cy_is_facing


class BotTest(BotAI):
    def __init__(self):
        super().__init__()

    async def on_step(self, iteration: int):
        print(cy_is_facing(self.workers[0], self.workers[1]))


if __name__ == "__main__":
    random_map = choice(
        [
            "GresvanAIE",
        ]
    )
    run_game(
        maps.get(random_map),
        [
            Bot(Race.Random, BotTest()),
            Computer(Race.Protoss, Difficulty.Medium),
        ],
        realtime=False,
    )
