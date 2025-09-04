from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI
from sc2.position import Point2
from sc2.units import Units

from cython_extensions import (
    cy_has_creep,
    cy_in_pathing_grid_burny,
    cy_in_pathing_grid_ma,
    cy_pylon_matrix_covers,
)

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

    def test_cy_has_creep(self, bot: BotAI, event_loop):
        # arrange - create a test creep grid
        creep_grid = bot.state.creep.data_numpy.copy()

        # ensure we have some creep for testing
        if not creep_grid.any():
            # create artificial creep data for testing
            creep_grid = np.zeros((50, 50), dtype=bool)
            creep_grid[10:15, 10:15] = True

        # find positions with and without creep
        creep_positions = np.where(creep_grid == True)
        if len(creep_positions[0]) > 0:
            has_creep_pos = (
                float(creep_positions[1][0]),
                float(creep_positions[0][0]),
            )  # note: x,y vs y,x
        else:
            # fallback if no creep found
            creep_grid[10, 10] = True
            has_creep_pos = (10.0, 10.0)

        no_creep_positions = np.where(creep_grid == False)
        no_creep_pos = (
            float(no_creep_positions[1][0]),
            float(no_creep_positions[0][0]),
        )

        # act & assert - test with exact coordinates
        assert cy_has_creep(creep_grid, has_creep_pos) == True
        assert cy_has_creep(creep_grid, no_creep_pos) == False

        # test with float coordinates that get rounded down
        if has_creep_pos[0] < creep_grid.shape[1] - 1:
            float_pos = (has_creep_pos[0] + 0.7, has_creep_pos[1] + 0.3)
            assert cy_has_creep(creep_grid, float_pos) == True

        # test with integer coordinates
        int_pos = (int(has_creep_pos[0]), int(has_creep_pos[1]))
        assert cy_has_creep(creep_grid, int_pos) == True

    def test_cy_has_creep_edge_cases(self, bot: BotAI, event_loop):
        # arrange - create small test grid for edge case testing
        test_grid = np.array([[1, 0], [0, 1]], dtype=bool)

        # act & assert - test corner positions
        assert cy_has_creep(test_grid, (0, 0)) == True  # top-left has creep
        assert cy_has_creep(test_grid, (1, 0)) == False  # top-right no creep
        assert cy_has_creep(test_grid, (0, 1)) == False  # bottom-left no creep
        assert cy_has_creep(test_grid, (1, 1)) == True  # bottom-right has creep

        # test with float coordinates
        assert cy_has_creep(test_grid, (0.9, 0.9)) == True  # rounds to (0,0)
        assert cy_has_creep(test_grid, (1.0, 1.0)) == True  # exact (1,1)

    def test_cy_in_pathing_grid_ma(self, bot: BotAI, event_loop):
        # arrange - create a test float32 grid for MapAnalyzer style grids
        # function uses grid[x, y] indexing
        test_grid = np.array(
            [
                [1.0, 0.5, 0.0, 2.0],
                [0.0, 1.0, 1.5, 0.8],
                [0.3, 3.0, 1.0, 0.0],
                [1.2, 0.9, 2.5, 1.0],
            ],
            dtype=np.float32,
        )

        # act & assert - test pathable positions (weight >= 1.0)
        # function uses grid[x, y] so position (x, y) maps to grid[x, y]
        assert cy_in_pathing_grid_ma(test_grid, (0, 0)) == True  # grid[0, 0] = 1.0
        assert cy_in_pathing_grid_ma(test_grid, (0, 1)) == False  # grid[0, 1] = 0.5
        assert cy_in_pathing_grid_ma(test_grid, (0, 2)) == False  # grid[0, 2] = 0.0
        assert cy_in_pathing_grid_ma(test_grid, (0, 3)) == True  # grid[0, 3] = 2.0

        assert cy_in_pathing_grid_ma(test_grid, (1, 0)) == False  # grid[1, 0] = 0.0
        assert cy_in_pathing_grid_ma(test_grid, (1, 1)) == True  # grid[1, 1] = 1.0
        assert cy_in_pathing_grid_ma(test_grid, (1, 2)) == True  # grid[1, 2] = 1.5
        assert cy_in_pathing_grid_ma(test_grid, (1, 3)) == False  # grid[1, 3] = 0.8

        assert cy_in_pathing_grid_ma(test_grid, (2, 0)) == False  # grid[2, 0] = 0.3
        assert cy_in_pathing_grid_ma(test_grid, (2, 1)) == True  # grid[2, 1] = 3.0
        assert cy_in_pathing_grid_ma(test_grid, (2, 2)) == True  # grid[2, 2] = 1.0
        assert cy_in_pathing_grid_ma(test_grid, (2, 3)) == False  # grid[2, 3] = 0.0

        assert cy_in_pathing_grid_ma(test_grid, (3, 0)) == True  # grid[3, 0] = 1.2
        assert cy_in_pathing_grid_ma(test_grid, (3, 1)) == False  # grid[3, 1] = 0.9
        assert cy_in_pathing_grid_ma(test_grid, (3, 2)) == True  # grid[3, 2] = 2.5
        assert cy_in_pathing_grid_ma(test_grid, (3, 3)) == True  # grid[3, 3] = 1.0

        # test with float coordinates (should round down)
        assert (
            cy_in_pathing_grid_ma(test_grid, (0.9, 0.8)) == True
        )  # rounds to (0,0) -> grid[0,0] = 1.0
        assert (
            cy_in_pathing_grid_ma(test_grid, (0.2, 1.7)) == False
        )  # rounds to (0,1) -> grid[0,1] = 0.5
        assert (
            cy_in_pathing_grid_ma(test_grid, (2.1, 1.9)) == True
        )  # rounds to (2,1) -> grid[2,1] = 3.0

    def test_cy_in_pathing_grid_ma_with_infinity(self, bot: BotAI, event_loop):
        # test infinity values - should return False since they're not pathable
        test_grid = np.array([[np.inf, 1.0], [2.0, np.inf]], dtype=np.float32)

        # Test infinity and normal values
        result_inf1 = cy_in_pathing_grid_ma(test_grid, (0, 0))  # grid[0, 0] = inf
        result_inf2 = cy_in_pathing_grid_ma(test_grid, (1, 1))  # grid[1, 1] = inf
        result_normal1 = cy_in_pathing_grid_ma(test_grid, (1, 0))  # grid[1, 0] = 1.0
        result_normal2 = cy_in_pathing_grid_ma(test_grid, (0, 1))  # grid[0, 1] = 2.0

        # Normal values >= 1.0 should return True
        assert result_normal1 == True  # 1.0 >= 1.0 and 1.0 != inf -> True
        assert result_normal2 == True  # 2.0 >= 1.0 and 2.0 != inf -> True

        # Infinity values should return False (not pathable)
        # With the fix using INFINITY from numpy.math, this should work correctly
        assert (
            result_inf1 == False
        )  # inf >= 1.0 is True, but inf != INFINITY is False -> False
        assert (
            result_inf2 == False
        )  # inf >= 1.0 is True, but inf != INFINITY is False -> False

    def test_cy_in_pathing_grid_burny(self, bot: BotAI, event_loop):
        # arrange - create a test boolean grid for burnysc2 style grids
        test_grid = np.array(
            [[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]], dtype=bool
        )

        # act & assert - test pathable positions (True values)
        assert cy_in_pathing_grid_burny(test_grid, (0, 0)) == True  # y=0, x=0
        assert cy_in_pathing_grid_burny(test_grid, (2, 0)) == True  # y=0, x=2
        assert cy_in_pathing_grid_burny(test_grid, (1, 1)) == True  # y=1, x=1
        assert cy_in_pathing_grid_burny(test_grid, (3, 1)) == True  # y=1, x=3
        assert cy_in_pathing_grid_burny(test_grid, (0, 2)) == True  # y=2, x=0
        assert cy_in_pathing_grid_burny(test_grid, (1, 2)) == True  # y=2, x=1
        assert cy_in_pathing_grid_burny(test_grid, (2, 3)) == True  # y=3, x=2
        assert cy_in_pathing_grid_burny(test_grid, (3, 3)) == True  # y=3, x=3

        # test non-pathable positions (False values)
        assert cy_in_pathing_grid_burny(test_grid, (1, 0)) == False  # y=0, x=1
        assert cy_in_pathing_grid_burny(test_grid, (3, 0)) == False  # y=0, x=3
        assert cy_in_pathing_grid_burny(test_grid, (0, 1)) == False  # y=1, x=0
        assert cy_in_pathing_grid_burny(test_grid, (2, 1)) == False  # y=1, x=2
        assert cy_in_pathing_grid_burny(test_grid, (2, 2)) == False  # y=2, x=2
        assert cy_in_pathing_grid_burny(test_grid, (3, 2)) == False  # y=2, x=3
        assert cy_in_pathing_grid_burny(test_grid, (0, 3)) == False  # y=3, x=0
        assert cy_in_pathing_grid_burny(test_grid, (1, 3)) == False  # y=3, x=1

        # test with float coordinates (should round down)
        assert (
            cy_in_pathing_grid_burny(test_grid, (0.9, 0.8)) == True
        )  # rounds to (0,0)
        assert (
            cy_in_pathing_grid_burny(test_grid, (1.7, 0.2)) == False
        )  # rounds to (1,0)
        assert (
            cy_in_pathing_grid_burny(test_grid, (2.1, 3.9)) == True
        )  # rounds to (2,3)

    def test_cy_in_pathing_grid_functions_with_real_data(self, bot: BotAI, event_loop):
        # test with actual game data from the bot
        pathing_grid = bot.game_info.pathing_grid.data_numpy

        # create a float32 version for ma function testing
        pathing_grid_float = pathing_grid.astype(np.float32)

        # get valid test positions with fallbacks
        start_pos = bot.workers.random.position
        map_center = bot.game_info.map_center

        # test burny function with transposed grid (x,y indexing)
        burny_result_start = cy_in_pathing_grid_burny(pathing_grid, start_pos)
        burny_result_center = cy_in_pathing_grid_burny(pathing_grid, map_center)

        # test ma function with transposed float grid
        ma_result_start = cy_in_pathing_grid_ma(pathing_grid_float.T, start_pos)
        ma_result_center = cy_in_pathing_grid_ma(pathing_grid_float.T, map_center)

        # both functions should give same results for simple 0/1 grids
        assert burny_result_start == ma_result_start
        assert burny_result_center == ma_result_center

        # check burnysc2's built-in function'
        assert burny_result_start == bot.in_pathing_grid(start_pos)
        assert burny_result_center == bot.in_pathing_grid(map_center)

        # results should match burnysc2's built-in function
        assert burny_result_start == bot.in_pathing_grid(start_pos)
        assert burny_result_center == bot.in_pathing_grid(map_center)
