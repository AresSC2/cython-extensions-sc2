from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI

from cython_extensions import cy_dijkstra

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestDijkstra:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_pathing(self, bot: BotAI, event_loop):
        # arrange
        targets = np.array([u.position.rounded for u in bot.enemy_units], np.intp)
        cost = np.where(bot.game_info.pathing_grid.data_numpy.T == 1, 1.0, np.inf).astype(np.float64)
        pathing = cy_dijkstra(cost, targets)

        limit = 32
        for unit in bot.units:
            path = pathing.get_path(unit.position.rounded, limit)
            assert 0 < len(path) <= limit
            if len(path) == 1:
                assert pathing.dist[path[0]] == np.inf
            else:
                # integrate cost backwards
                path_backwards = path[::-1]
                dist_expected = pathing.dist[path_backwards[0]]
                for i, (p, q) in enumerate(zip(path_backwards[1:], path_backwards)):
                    dist_factor = np.linalg.norm(np.array(p) - np.array(q))
                    dist_expected += cost[p] * dist_factor
                    assert pathing.dist[p] == dist_expected

    def test_raises_on_nonpositive_entries(self, bot: BotAI, event_loop):
        targets = np.array([], np.intp)
        cost = np.zeros(bot.game_info.map_size, np.float64)
        with pytest.raises(Exception):
            cy_dijkstra(cost, targets)

    def test_raises_on_target_out_of_bounds(self, bot: BotAI, event_loop):
        cost = np.ones(bot.game_info.map_size, np.float64)
        with pytest.raises(Exception):
            cy_dijkstra(cost, np.array([[-1, -1]], np.intp))
        with pytest.raises(Exception):
            cy_dijkstra(cost, np.array([cost.shape], np.intp))
