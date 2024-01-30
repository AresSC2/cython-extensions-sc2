from pathlib import Path

import pytest
from sc2.bot_ai import BotAI
from sc2.unit import Unit
from sc2.units import Units

from cython_extensions import cy_range_vs_target, cy_is_facing

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestCombatUtils:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_range_vs_target(self, bot: BotAI, event_loop):
        # arrange
        air_targets: list[Unit] = [u for u in bot.enemy_units if u.is_flying]
        ground_targets: list[Unit] = [u for u in bot.enemy_units if not u.is_flying]
        if len(air_targets) == 0 or len(ground_targets) == 0:
            assert False

        for unit in bot.units:
            if unit.ground_range < 3 and unit.air_range < 3:
                continue

            if unit.can_attack_air:
                # act
                range_vs_flying: float = cy_range_vs_target(unit, air_targets[0])
                # assert
                assert range_vs_flying == unit.air_range
            if unit.can_attack_ground:
                # act
                range_vs_ground: float = cy_range_vs_target(unit, ground_targets[0])
                # assert
                assert range_vs_ground == unit.ground_range

    def test_is_facing(self, bot: BotAI, event_loop):
        """
        TODO: Add tests where unit is facing another unit
        """
        # arrange
        townhall: Unit = bot.townhalls[0]
        workers: Units = bot.workers.closer_than(4.5, townhall)

        # act
        # by the time our pickle data is saved, workers are sent to mine
        # so they shouldn't be facing our townhall
        all_not_facing_townhall: bool = True
        for worker in workers:
            if cy_is_facing(worker, townhall):
                all_not_facing_townhall = False
                break

        # assert
        assert all_not_facing_townhall

