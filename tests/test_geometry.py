from pathlib import Path

import pytest
from sc2.bot_ai import BotAI
from sc2.position import Point2
from sc2.unit import Unit

from cython_extensions import (
    cy_angle_to,
    cy_distance_to,
    cy_distance_to_squared,
    cy_towards,
)

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestGeometry:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_angle_to(self, bot: BotAI, event_loop):
        from_pos: Point2 = Point2((0.0, 0.0))
        to_pos: Point2 = Point2((25.0, 25.0))
        angle_radians: float = (
            0.7853981633974483096156608458198757210492923498437764552437361480
        )

        assert cy_angle_to(from_pos, to_pos) == pytest.approx(angle_radians)

    def test_cy_distance_to(self, bot: BotAI, event_loop):
        # we just test this calculates same as burnysc2
        center: Point2 = bot.game_info.map_center
        enemy_spawn: Point2 = bot.enemy_start_locations[0]
        unit_one: Unit = bot.units[0]
        unit_two: Unit = bot.units[-1]
        enemy_one: Unit = bot.enemy_units[0]
        enemy_two: Unit = bot.enemy_units[-1]

        assert cy_distance_to(unit_one.position, center) == unit_one.distance_to(center)
        assert cy_distance_to(
            unit_one.position, unit_two.position
        ) == unit_one.distance_to(unit_two)
        assert cy_distance_to(
            unit_one.position, enemy_one.position
        ) == unit_one.distance_to(enemy_one)
        assert cy_distance_to(
            unit_one.position, enemy_two.position
        ) == unit_one.distance_to(enemy_two)
        assert cy_distance_to(center, enemy_spawn) == center.distance_to(enemy_spawn)

    def test_cy_distance_to_squared(self, bot: BotAI, event_loop):
        # we just test this calculates same as burnysc2
        center: Point2 = bot.game_info.map_center
        enemy_spawn: Point2 = bot.enemy_start_locations[0]
        unit_one: Unit = bot.units[0]
        unit_two: Unit = bot.units[-1]
        enemy_one: Unit = bot.enemy_units[0]
        enemy_two: Unit = bot.enemy_units[-1]

        assert cy_distance_to_squared(
            unit_one.position, center
        ) == unit_one.distance_to_squared(center)
        assert cy_distance_to_squared(
            unit_one.position, unit_two.position
        ) == unit_one.distance_to_squared(unit_two)
        assert cy_distance_to_squared(
            unit_one.position, enemy_one.position
        ) == unit_one.distance_to_squared(enemy_one)
        assert cy_distance_to_squared(
            unit_one.position, enemy_two.position
        ) == unit_one.distance_to_squared(enemy_two)
        assert cy_distance_to_squared(center, enemy_spawn) == center._distance_squared(
            enemy_spawn
        )

    def test_cy_towards(self, bot: BotAI, event_loop):
        # we just test this calculates same as burnysc2
        center: Point2 = bot.game_info.map_center
        enemy_spawn: Point2 = bot.enemy_start_locations[0]
        unit_one: Unit = bot.units[0]
        unit_two: Unit = bot.units[-1]
        enemy_one: Unit = bot.enemy_units[0]
        enemy_two: Unit = bot.enemy_units[-1]

        assert cy_towards(center, unit_one.position, 10.0) == center.towards(
            unit_one.position, 10.0
        )
        assert cy_towards(
            unit_two.position, enemy_spawn, 15.0
        ) == unit_two.position.towards(enemy_spawn, 15.0)
        assert cy_towards(
            enemy_one.position, enemy_two.position, -17.5
        ) == enemy_one.position.towards(enemy_two.position, -17.5)
