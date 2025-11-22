from pathlib import Path

import pytest
from sc2.bot_ai import BotAI
from sc2.unit import Unit

from cython_extensions import (
    cy_center,
    cy_closer_than,
    cy_closest_to,
    cy_find_units_center_mass,
    cy_further_than,
    cy_in_attack_range,
    cy_sorted_by_distance_to,
)

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "combat_data").iterdir()
    if map_path.suffix == ".xz"
]


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestUnitsUtils:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_cy_center(self, bot: BotAI, event_loop):
        """Test cy_center function returns correct centroid of units."""
        # Test with workers
        workers = bot.workers
        if len(workers) == 0:
            pytest.skip("No workers available for testing")

        # Compare with python-sc2's center
        cy_result = cy_center(workers)
        sc2_result = workers.center

        # Results should be very close
        assert abs(cy_result[0] - sc2_result.x) < 0.001
        assert abs(cy_result[1] - sc2_result.y) < 0.001

        # Test with list[Unit] instead of Units
        workers_list = list(workers)
        cy_result_list = cy_center(workers_list)
        assert abs(cy_result_list[0] - cy_result[0]) < 0.001
        assert abs(cy_result_list[1] - cy_result[1]) < 0.001

        # Test with single unit
        single_unit = [workers[0]]
        cy_result_single = cy_center(single_unit)
        unit_pos = workers[0].position
        assert abs(cy_result_single[0] - unit_pos.x) < 0.001
        assert abs(cy_result_single[1] - unit_pos.y) < 0.001

    def test_cy_closest_to(self, bot: BotAI, event_loop):
        """Test cy_closest_to function finds the correct closest unit."""
        units = bot.units
        if len(units) == 0:
            pytest.skip("No units available for testing")

        test_position = bot.game_info.map_center

        # Compare with python-sc2's closest_to
        cy_result = cy_closest_to(test_position, units)
        sc2_result = units.closest_to(test_position)

        # Should be the same unit
        assert cy_result.tag == sc2_result.tag

        # Test with list[Unit] instead of Units
        units_list = list(units)
        cy_result_list = cy_closest_to(test_position, units_list)
        assert cy_result_list.tag == cy_result.tag

        # Test with different position format
        cy_result_alt = cy_closest_to(test_position, units)
        assert cy_result_alt.tag == cy_result.tag

    def test_cy_find_units_center_mass(self, bot: BotAI, event_loop):
        """Test cy_find_units_center_mass function finds correct center mass."""
        units = bot.units
        if len(units) == 0:
            pytest.skip("No units available for testing")

        distance = 10.0
        center_pos, num_units = cy_find_units_center_mass(units, distance)

        # Check return types
        assert isinstance(center_pos, tuple)
        assert len(center_pos) == 2
        assert isinstance(center_pos[0], float)
        assert isinstance(center_pos[1], float)
        assert isinstance(num_units, int)
        assert num_units > 0
        assert num_units <= len(units)

        # Test with different distance values
        center_pos_small, num_units_small = cy_find_units_center_mass(units, 1.0)
        center_pos_large, num_units_large = cy_find_units_center_mass(units, 50.0)

        # Larger distance should include more or equal units
        assert num_units_large >= num_units_small

    def test_cy_in_attack_range(self, bot: BotAI, event_loop):
        """Test cy_in_attack_range function correctly identifies units in attack range."""
        # Find a unit that can attack
        attacking_unit = None
        for unit in bot.units:
            if unit.can_attack:
                attacking_unit = unit
                break

        if attacking_unit is None:
            pytest.skip("No units capable of attacking found")

        target_units = bot.enemy_units if bot.enemy_units else bot.units
        if len(target_units) == 0:
            pytest.skip("No target units available for testing")

        # Test basic functionality
        in_range = cy_in_attack_range(attacking_unit, target_units)
        assert isinstance(in_range, list)

        # All returned units should be Unit objects
        for unit in in_range:
            assert isinstance(unit, Unit)

        # Test with bonus distance
        in_range_bonus = cy_in_attack_range(attacking_unit, target_units, 5.0)
        assert len(in_range_bonus) >= len(in_range)

        # Test with list[Unit] instead of Units
        target_list = list(target_units)
        in_range_list = cy_in_attack_range(attacking_unit, target_list)
        assert len(in_range_list) == len(in_range)

        # Test with non-attacking unit
        non_attacking_unit = None
        for unit in bot.units:
            if not unit.can_attack:
                non_attacking_unit = unit
                break

        if non_attacking_unit:
            empty_result = cy_in_attack_range(non_attacking_unit, target_units)
            assert empty_result == []

    def test_cy_sorted_by_distance_to(self, bot: BotAI, event_loop):
        """Test cy_sorted_by_distance_to function correctly sorts units by distance."""
        units = bot.units
        if len(units) < 2:
            pytest.skip("Need at least 2 units for sorting test")

        test_position = bot.game_info.map_center

        # Test sorting
        sorted_units = cy_sorted_by_distance_to(units, test_position)

        # Should return same number of units
        assert len(sorted_units) == len(units)

        # All should be Unit objects
        for unit in sorted_units:
            assert isinstance(unit, Unit)

        # Should be sorted by distance (closest first)
        for i in range(len(sorted_units) - 1):
            dist1 = sorted_units[i].distance_to(test_position)
            dist2 = sorted_units[i + 1].distance_to(test_position)
            assert dist1 <= dist2

        # Test with list[Unit] instead of Units
        units_list = list(units)
        sorted_list = cy_sorted_by_distance_to(units_list, test_position)
        assert len(sorted_list) == len(sorted_units)
        assert sorted_list[0].tag == sorted_units[0].tag

    def test_cy_closer_than(self, bot: BotAI, event_loop):
        """Test cy_closer_than function correctly filters units by distance."""
        units = bot.units
        if len(units) == 0:
            pytest.skip("No units available for testing")

        test_position = bot.game_info.map_center
        max_distance = 15.0

        # Test filtering
        close_units = cy_closer_than(units, max_distance, test_position)

        # Should return list of units
        assert isinstance(close_units, list)
        for unit in close_units:
            assert isinstance(unit, Unit)

        # All returned units should be within max_distance
        for unit in close_units:
            assert unit.distance_to(test_position) <= max_distance

        # Compare with python-sc2's closer_than
        sc2_close = units.closer_than(max_distance, test_position)
        assert len(close_units) == len(sc2_close)

        # Test with different distances
        close_units_small = cy_closer_than(units, 5.0, test_position)
        close_units_large = cy_closer_than(units, 50.0, test_position)
        assert len(close_units_large) >= len(close_units_small)

        # Test with list[Unit] instead of Units
        units_list = list(units)
        close_units_list = cy_closer_than(units_list, max_distance, test_position)
        assert len(close_units_list) == len(close_units)

    def test_cy_further_than(self, bot: BotAI, event_loop):
        """Test cy_further_than function correctly filters units by distance."""
        units = bot.units
        if len(units) == 0:
            pytest.skip("No units available for testing")

        test_position = bot.game_info.map_center
        min_distance = 10.0

        # Test filtering
        far_units = cy_further_than(units, min_distance, test_position)

        # Should return list of units
        assert isinstance(far_units, list)
        for unit in far_units:
            assert isinstance(unit, Unit)

        # All returned units should be further than min_distance
        for unit in far_units:
            assert unit.distance_to(test_position) >= min_distance

        # Compare with python-sc2's further_than
        sc2_far = units.further_than(min_distance, test_position)
        assert len(far_units) == len(sc2_far)

        # Test with different distances
        far_units_small = cy_further_than(units, 5.0, test_position)
        far_units_large = cy_further_than(units, 50.0, test_position)
        assert len(far_units_large) <= len(far_units_small)

        # Test with list[Unit] instead of Units
        units_list = list(units)
        far_units_list = cy_further_than(units_list, min_distance, test_position)
        assert len(far_units_list) == len(far_units)
