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

from cython_extensions import cy_is_facing, cy_angle_diff, cy_closest_to


class BotTest(BotAI):
    def __init__(self):
        super().__init__()

    async def on_step(self, iteration: int):
        # print(cy_is_facing(self.workers[0], self.workers[1]))
        # print(cy_angle_diff(300.0, 250.0))
        print(cy_closest_to(self.start_location, self.workers))


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
