from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from cython_extensions import cy_pylon_matrix_covers

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestGeneralUtils:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_pylon_matrix_covers(self, bot: BotAI, event_loop):
        # arrange
        # pretend our townhalls are a pylon
        # cy_pylon_matrix_covers function will still work with it
        pylons: Units = bot.townhalls
        height_grid: np.ndarray = bot.game_info.terrain_height.data_numpy

        covers_position: Point2 = pylons[0].position
        doesnt_cover: Point2 = bot.game_info.map_center

        # act
        assert cy_pylon_matrix_covers(covers_position, pylons, height_grid)
        assert not cy_pylon_matrix_covers(doesnt_cover, pylons, height_grid)
