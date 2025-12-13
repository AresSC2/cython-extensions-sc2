from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_equal
from sc2.bot_ai import BotAI

from cython_extensions import cy_dijkstra

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


class TestDijkstraGeneric:

    def test_raises_on_nonpositive_entries(self):
        targets = np.array([[0, 0]])
        cost = np.ones((3, 3))
        cost[1, 1] = -1
        with pytest.raises(Exception):
            cy_dijkstra(cost, targets)

    def test_raises_on_target_out_of_bounds(self):
        cost = np.ones((3, 3))
        with pytest.raises(Exception):
            cy_dijkstra(cost, np.array([[1, -1]]))
        with pytest.raises(Exception):
            cy_dijkstra(cost, np.array([[-1, 1]]))
        with pytest.raises(Exception):
            cy_dijkstra(cost, np.array([[1, 3]]))
        with pytest.raises(Exception):
            cy_dijkstra(cost, np.array([[3, 1]]))

    def test_bounds(self):
        # make sure the algorithm does not go through walls or out of bounds
        cost = np.array([[1, np.inf, 1], [1, np.inf, 1], [1, np.inf, 1]])
        pathing = cy_dijkstra(cost, np.array([[1, 2]]))
        assert_equal(pathing.get_path((0, 0)), [(0, 0)])
        assert_equal(pathing.get_path((1, 0)), [(1, 0)])
        assert_equal(pathing.get_path((2, 0)), [(2, 0)])

    def test_find_valid_start(self):
        # test that the algorithm searches for valid starting point near the given coordinates
        # setup a rectangular map surrounded by unpathable border
        cost = np.pad(np.ones((3, 3)), 1, constant_values=np.inf)
        # find paths towards center
        pathing = cy_dijkstra(cost, np.array([[2, 2]]))
        # test that starting point will be rounded
        assert_equal(pathing.get_path((1.1, 1.3)), [(1, 1), (2, 2)])
        assert_equal(pathing.get_path((0.8, 0.7)), [(1, 1), (2, 2)])
        # test that invalid start snaps to the closest valid one
        assert_equal(pathing.get_path((0.1, 2)), [(1, 2), (2, 2)])
        assert_equal(pathing.get_path((-2.2, 6.9), max_distance=5), [(1, 3), (2, 2)])

    def test_dtypes(self):
        """test that the algorithm accepts different kinds of dtypes"""
        cost = np.ones((3, 3))
        targets = np.array([(1, 1)])
        cy_dijkstra(cost.astype(np.float32), targets.astype(np.int32))
        cy_dijkstra(cost.astype(np.float64), targets.astype(np.int64))
        cy_dijkstra(cost.astype(np.int32), targets.astype(int))


class TestDijkstra:

    def test_maze1(self):
        """test that simple maze can be solved and that diagonals are used."""
        x = np.inf
        cost = np.array([
            [1, x, 1, 1, 1],
            [1, 1, 2, x, 1],
        ])
        targets = np.array([[1, 4]])
        pathing = cy_dijkstra(cost, targets)
        assert_equal(pathing.get_path((0, 0)), [(0, 0), (1, 1), (0, 2), (0, 3), (1, 4)])

    def test_maze2(self):
        """test that obstacles are avoided correctly."""
        x = np.inf
        cost = np.array([
            [1, 1, 1, 2, 1],
            [1, x, x, x, 1],
            [1, x, x, x, 1],
            [1, x, x, x, 1],
            [1, 1, 1, 1, 1],
        ])
        targets = np.array([[4, 4]])
        pathing = cy_dijkstra(cost, targets)
        assert_equal(pathing.get_path((0, 0)), [(0, 0), (1, 0), (2, 0), (3, 0), (4, 1), (4, 2), (4, 3), (4, 4)])
        assert_equal(pathing.get_path((0, 2)), [(0, 2), (0, 3), (1, 4), (2, 4), (3, 4), (4, 4)])