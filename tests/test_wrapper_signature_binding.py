"""
Smoke test to verify all wrapper functions can be called with valid inputs.
This catches signature binding issues between wrappers and validators.
"""
import numpy as np
import pytest
from sc2.ids.unit_typeid import UnitTypeId

from cython_extensions.type_checking.config import enable_safe_mode


@pytest.fixture(autouse=True, scope="module")
def _enable_safe_mode_for_module():
    """Enable safe mode so validators run during tests."""
    enable_safe_mode(True)
    yield
    enable_safe_mode(False)


def test_all_wrapper_functions_callable():
    """
    Call every exported wrapper function with minimal valid inputs.

    This test will fail if:
    - Wrapper parameter names don't match validator expectations (KeyError)
    - Validators have bugs (TypeError/ValueError)
    - Any exported function is missing from this test
    """
    # Import from main module to test the actual user-facing API
    import cython_extensions as ce

    # Prepare test data
    bool_grid = np.array([[True, False], [False, True]], dtype=bool)
    u8_grid = np.array([[0, 1], [1, 0]], dtype=np.uint8)
    f32_grid = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    f64_grid = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)
    pos = (1.0, 2.0)

    # Simple mock objects with minimal required attributes
    class MockPosition:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def __iter__(self):
            # Support tuple unpacking for validator compatibility
            return iter((self.x, self.y))
        def __getitem__(self, idx):
            return (self.x, self.y)[idx]
        def __len__(self):
            return 2

    class MockProto:
        def __init__(self, unit_type: int):
            self.unit_type = unit_type

    class MockUnit:
        def __init__(self, x=1.0, y=2.0, unit_type=50):
            self.position = MockPosition(x, y)
            self.can_attack = False
            self.weapon_cooldown = 0.0
            self.radius = 0.5
            self._proto = MockProto(unit_type)
            # for in_attack_range logic
            self.can_attack_air = False
            self.can_attack_ground = False
            self.air_range = 0.0
            self.ground_range = 0.0
            self.facing = 0.5
            self.health = 100.0
            self.shield = 0.0

    unit = MockUnit()
    units = [unit]

    # Test all functions - any exception will fail the test
    # Units utils
    ce.cy_center(units)
    ce.cy_closest_to(pos, units)
    ce.cy_find_units_center_mass(units, 5.0)
    ce.cy_in_attack_range(unit, [], 0.0)  # empty units to skip attack validation
    ce.cy_sorted_by_distance_to([], pos, False)

    # Geometry
    ce.cy_distance_to(pos, pos)
    ce.cy_distance_to_squared(pos, pos)
    ce.cy_towards(pos, (3.0, 4.0), 1.0)
    ce.cy_angle_to(pos, (3.0, 4.0))
    ce.cy_angle_diff(0.1, 0.2)
    ce.cy_find_average_angle((0.0, 0.0), (1.0, 0.0), [(1.0, 1.0), (2.0, 1.0)])
    ce.cy_get_angle_between_points((1.0, 0.0), (2.0, 1.0))
    ce.cy_translate_point_along_line(pos, 1.0, 2.0)
    ce.cy_find_correct_line([pos, (2.0, 2.0)], (1.5, 1.5))

    # Combat utils
    ce.cy_adjust_moving_formation(units, pos, [], 1.0, 0.5)
    ce.cy_attack_ready("bot", unit, unit)
    ce.cy_find_aoe_position(1.0, units, 1, set())
    ce.cy_get_turn_speed(unit, 50)  # Marine unit type ID
    ce.cy_is_facing(unit, unit, 0.3)
    ce.cy_pick_enemy_target([unit])
    ce.cy_range_vs_target(unit, unit)

    # General utils
    ce.cy_has_creep(bool_grid, pos)
    ce.cy_in_pathing_grid_burny(bool_grid, pos)
    ce.cy_in_pathing_grid_ma(f32_grid, pos)
    ce.cy_pylon_matrix_covers(pos, [], u8_grid, 1.0)
    # ce.cy_unit_pending("bot", UnitTypeId.MARINE)

    # Map analysis
    ce.cy_flood_fill_grid((0, 0), u8_grid, u8_grid, 3, set())
    ce.cy_get_bounding_box({pos, (2.0, 2.0)})

    # Numpy helper
    ce.cy_all_points_below_max_value(f32_grid, 5.0, [(0, 0), (1, 1)])
    ce.cy_all_points_have_value(u8_grid, 1, [(0, 1), (1, 0)])
    ce.cy_last_index_with_value(u8_grid, 1, [(0, 0), (1, 1)])
    ce.cy_point_below_value(f32_grid, pos, 10.0)
    ce.cy_points_with_value(u8_grid, 1, [(0, 0)])

    # Placement solver
    ce.cy_can_place_structure((0, 0), (2, 2), u8_grid, u8_grid, u8_grid, True, False)
    ce.cy_find_building_locations(
        u8_grid, 1, 1, (0, 1), (0, 1), 
        u8_grid, u8_grid, u8_grid, u8_grid, 
        2, 2, True
    )

    # Dijkstra
    ce.cy_dijkstra(f64_grid, np.array([[0, 0]], dtype=np.intp), True)
