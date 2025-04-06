from pathlib import Path

import numpy as np
from numpy.testing import assert_equal
import pytest
from sc2.bot_ai import BotAI

from cython_extensions import cy_dijkstra

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


class TestDijkstraFailcases:

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
        cost = np.array([[1, np.inf, 1],
                         [1, np.inf, 1],
                         [1, np.inf, 1]])
        pathing = cy_dijkstra(cost, np.array([[1, 2]]))
        distance_expected = np.array([[np.inf, np.inf, 2],
                                      [np.inf, np.inf, 1],
                                      [np.inf, np.inf, 2]])
        assert_equal(pathing.distance, distance_expected)


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestDijkstra:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_pathing(self, bot: BotAI, event_loop):
        targets = np.array([u.position.rounded for u in bot.enemy_units], np.intp)
        cost = np.where(bot.game_info.pathing_grid.data_numpy.T == 1, 1.0, np.inf).astype(np.float64)
        pathing = cy_dijkstra(cost, targets)

        limit = 32
        for unit in bot.units:
            p = unit.position.rounded
            path = pathing.get_path(p, limit)
            assert 1 <= len(path) <= limit
            if len(path) == 1:
                assert pathing.distance[path[0]] == np.inf
            else:
                # test that the distance was calculated correctly along the path
                path_backwards = path[::-1]
                dist_expected = pathing.distance[path_backwards[0]]
                for i, (p, q) in enumerate(zip(path_backwards[1:], path_backwards)):
                    dist_factor = np.linalg.norm(np.array(p) - np.array(q))
                    dist_expected += cost[p] * dist_factor
                    assert pathing.distance[p] == dist_expected
