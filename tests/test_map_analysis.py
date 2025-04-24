from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI
from sc2.position import Point2

from cython_extensions import (
    cy_all_points_have_value,
    cy_last_index_with_value,
    cy_point_below_value,
    cy_points_with_value,
    cy_all_points_below_max_value,
    cy_flood_fill_grid,
    cy_get_bounding_box,
)

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestMapAnalysis:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_cy_flood_fill_grid(self, bot: BotAI, event_loop):
        terrain = np.ones((5, 5), dtype=np.uint8)
        pathing = np.ones((5, 5), dtype=np.uint8)
        start = (2, 2)
        result = cy_flood_fill_grid(start, terrain, pathing, 2, set())
        assert isinstance(result, set)
        assert (2, 2) in result

    def test_cy_get_bounding_box(self, bot: BotAI, event_loop):
        points = {Point2((1, 2)), Point2((3, 4)), Point2((2, 3))}
        (xmin, xmax), (ymin, ymax) = cy_get_bounding_box(points)
        assert xmin == 1 and xmax == 3
        assert ymin == 2 and ymax == 4
