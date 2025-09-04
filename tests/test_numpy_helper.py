from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI

from cython_extensions import (
    cy_all_points_below_max_value,
    cy_all_points_have_value,
    cy_last_index_with_value,
    cy_point_below_value,
    cy_points_with_value,
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
        # arrange - create test grid with various float values including infinity
        test_grid = np.array(
            [
                [0.5, 1.0, 2.5, np.inf],
                [0.0, 1.5, np.inf, 3.0],
                [np.inf, 0.8, 1.2, 0.3],
                [2.0, np.inf, 0.1, 1.0],
            ],
            dtype=np.float32,
        ).T

        # test with default safety limit of 1.0
        # positions with weight <= 1.0 or == inf should return True
        assert cy_point_below_value(test_grid, (0, 0)) == True  # weight = 0.5 <= 1.0
        assert cy_point_below_value(test_grid, (1, 0)) == True  # weight = 1.0 <= 1.0
        assert cy_point_below_value(test_grid, (2, 0)) == False  # weight = 2.5 > 1.0
        assert (
            cy_point_below_value(test_grid, (3, 0)) == True
        )  # weight = inf (special case)

        assert cy_point_below_value(test_grid, (0, 1)) == True  # weight = 0.0 <= 1.0
        assert cy_point_below_value(test_grid, (1, 1)) == False  # weight = 1.5 > 1.0
        assert (
            cy_point_below_value(test_grid, (2, 1)) == True
        )  # weight = inf (special case)
        assert cy_point_below_value(test_grid, (3, 1)) == False  # weight = 3.0 > 1.0

        assert (
            cy_point_below_value(test_grid, (0, 2)) == True
        )  # weight = inf (special case)
        assert cy_point_below_value(test_grid, (1, 2)) == True  # weight = 0.8 <= 1.0
        assert cy_point_below_value(test_grid, (2, 2)) == False  # weight = 1.2 > 1.0
        assert cy_point_below_value(test_grid, (3, 2)) == True  # weight = 0.3 <= 1.0

        assert cy_point_below_value(test_grid, (0, 3)) == False  # weight = 2.0 > 1.0
        assert (
            cy_point_below_value(test_grid, (1, 3)) == True
        )  # weight = inf (special case)
        assert cy_point_below_value(test_grid, (2, 3)) == True  # weight = 0.1 <= 1.0
        assert cy_point_below_value(test_grid, (3, 3)) == True  # weight = 1.0 <= 1.0

        # test with custom safety limit of 0.5
        assert cy_point_below_value(test_grid, (0, 0), 0.5) == True  # 0.5 <= 0.5
        assert cy_point_below_value(test_grid, (1, 0), 0.5) == False  # 1.0 > 0.5
        assert cy_point_below_value(test_grid, (1, 2), 0.5) == False  # 0.8 > 0.5
        assert cy_point_below_value(test_grid, (3, 2), 0.5) == True  # 0.3 <= 0.5
        assert cy_point_below_value(test_grid, (3, 0), 0.5) == True  # inf always True

        # test with custom safety limit of 2.0
        assert cy_point_below_value(test_grid, (2, 0), 2.0) == False  # 2.5 > 2.0
        assert cy_point_below_value(test_grid, (0, 3), 2.0) == True  # 2.0 <= 2.0
        assert cy_point_below_value(test_grid, (2, 2), 2.0) == True  # 1.2 <= 2.0
        assert cy_point_below_value(test_grid, (2, 1), 2.0) == True  # inf always True

        # test with float coordinates (should floor to integers)
        assert (
            cy_point_below_value(test_grid, (0.9, 0.8), 1.0) == True
        )  # floors to (0,0) -> 0.5 <= 1.0
        assert (
            cy_point_below_value(test_grid, (2.1, 0.7), 1.0) == False
        )  # floors to (2,0) -> 2.5 > 1.0
        assert (
            cy_point_below_value(test_grid, (3.9, 0.2), 1.0) == True
        )  # floors to (3,0) -> inf always True

    def test_cy_point_below_value_all_infinity(self, bot: BotAI, event_loop):
        # test grid with all infinity values
        test_grid = np.full((3, 3), np.inf, dtype=np.float32)

        # all positions should return True since infinity is treated as unsafe/below threshold
        for x in range(3):
            for y in range(3):
                assert cy_point_below_value(test_grid, (x, y), 1.0) == True
                assert cy_point_below_value(test_grid, (x, y), 0.1) == True
                assert cy_point_below_value(test_grid, (x, y), 10.0) == True

    def test_cy_points_with_value(self, bot: BotAI, event_loop):
        grid = np.array([[1, 2], [3, 1]], dtype=np.uint8)
        points = [(0, 0), (1, 1), (1, 0)]
        result = cy_points_with_value(grid, 1, points)
        assert (0, 0) in result and (1, 1) in result
