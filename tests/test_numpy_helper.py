from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI

from cython_extensions import (
    cy_all_points_have_value,
    cy_last_index_with_value,
    cy_point_below_value,
    cy_points_with_value,
    cy_all_points_below_max_value,
)

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestNumpyHelper:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_cy_all_points_below_max_value(self, bot: BotAI, event_loop):
        grid = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        points = [(0, 0), (1, 1)]
        assert cy_all_points_below_max_value(grid, 5.0, points)
        assert not cy_all_points_below_max_value(grid, 3.0, points)

    def test_cy_all_points_have_value(self, bot: BotAI, event_loop):
        grid = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        points = [(0, 0), (1, 1)]
        assert not cy_all_points_have_value(grid, 1, points)
        assert cy_all_points_have_value(grid, 4, [(1, 1)])

    def test_cy_last_index_with_value(self, bot: BotAI, event_loop):
        grid = np.array([[1, 1], [1, 0]], dtype=np.uint8)
        points = [(0, 0), (0, 1), (1, 0), (1, 1)]
        assert cy_last_index_with_value(grid, 1, points) == 2

    def test_cy_point_below_value(self, bot: BotAI, event_loop):
        grid = np.array([[0.5, 1.5], [2.0, 0.3]], dtype=np.float32)
        assert cy_point_below_value(grid, (0, 0), 1.0)
        assert not cy_point_below_value(grid, (0, 1), 1.0)

    def test_cy_points_with_value(self, bot: BotAI, event_loop):
        grid = np.array([[1, 2], [3, 1]], dtype=np.uint8)
        points = [(0, 0), (1, 1), (1, 0)]
        result = cy_points_with_value(grid, 1, points)
        assert (0, 0) in result and (1, 1) in result
