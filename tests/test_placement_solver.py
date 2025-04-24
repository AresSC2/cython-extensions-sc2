from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI

from cython_extensions import cy_can_place_structure, cy_find_building_locations

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestPlacementSolver:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_cy_can_place_structure(self, bot: BotAI, event_loop):
        grid = np.ones((4, 4), dtype=np.uint8)
        creep_grid = np.zeros((4, 4), dtype=np.uint8)
        assert cy_can_place_structure((0, 0), (2, 2), creep_grid, grid, grid)
        grid[0, 0] = 0
        assert not cy_can_place_structure((0, 0), (2, 2), creep_grid, grid, grid)

    def test_cy_find_building_locations(self, bot: BotAI, event_loop):
        kernel = np.ones((2, 2), dtype=np.uint8)
        grid = np.ones((4, 4), dtype=np.uint8)
        creep_grid = np.zeros((4, 4), dtype=np.uint8)
        # locations = cy_find_building_locations(
        #     kernel, 1, 1, (0, 2), (0, 2), creep_grid, grid, grid, creep_grid, True
        # )
        locations = cy_find_building_locations(
            kernel=kernel,
            x_stride=1,
            y_stride=1,
            x_bounds=(0, 2),
            y_bounds=(0, 2),
            creep_grid=creep_grid,
            placement_grid=grid,
            pathing_grid=grid,
            points_to_avoid_grid=creep_grid,
            building_width=2,
            building_height=2,
            avoid_creep=True,
        )
        assert isinstance(locations, list)
        assert all(isinstance(loc, tuple) for loc in locations)
