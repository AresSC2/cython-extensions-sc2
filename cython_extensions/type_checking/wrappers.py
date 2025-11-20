"""
Complete safe wrapper functions for all Cython extensions.
Provides type validation when safe mode is enabled.
"""

import inspect
from functools import wraps
from typing import Callable, Optional, Union

from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

from cython_extensions.type_checking.config import is_safe_mode_enabled
from cython_extensions.type_checking.validators import (
    _validate_cy_all_points_below_max_value,
    _validate_cy_all_points_have_value,
    _validate_cy_angle_diff,
    _validate_cy_angle_to,
    _validate_cy_attack_ready,
    _validate_cy_can_place_structure,
    _validate_cy_center,
    _validate_cy_closest_to,
    _validate_cy_dijkstra,
    _validate_cy_distance_to,
    _validate_cy_distance_to_squared,
    _validate_cy_find_aoe_position,
    _validate_cy_find_average_angle,
    _validate_cy_find_building_locations,
    _validate_cy_find_units_center_mass,
    _validate_cy_flood_fill_grid,
    _validate_cy_get_angle_between_points,
    _validate_cy_get_bounding_box,
    _validate_cy_get_turn_speed,
    _validate_cy_has_creep,
    _validate_cy_in_attack_range,
    _validate_cy_in_pathing_grid_burny,
    _validate_cy_in_pathing_grid_ma,
    _validate_cy_is_facing,
    _validate_cy_last_index_with_value,
    _validate_cy_pick_enemy_target,
    _validate_cy_point_below_value,
    _validate_cy_points_with_value,
    _validate_cy_pylon_matrix_covers,
    _validate_cy_range_vs_target,
    _validate_cy_sorted_by_distance_to,
    _validate_cy_towards,
    _validate_cy_translate_point_along_line,
    _validate_cy_unit_pending,
)


def safe_wrapper(validation_func: Optional[Callable] = None):
    """
    Decorator to create safe wrappers that conditionally apply validation.

    Args:
        validation_func: Function to validate arguments before calling the original
    """

    def decorator(original_func):
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            if is_safe_mode_enabled() and validation_func:
                try:
                    # Get parameter names for better error messages
                    sig = inspect.signature(original_func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    validation_func(bound_args.arguments)
                except (TypeError, ValueError, KeyError) as e:
                    # Enhance error message with function name if not already present
                    # KeyError indicates validator expects different parameter names than wrapper signature
                    func_name = original_func.__name__
                    error_msg = str(e)

                    # Check if function name is already in the error message
                    if not error_msg.startswith(func_name):
                        enhanced_msg = f"{func_name}: {error_msg}"
                        raise type(e)(enhanced_msg) from e
                    else:
                        raise
            return original_func(*args, **kwargs)

        return wrapper

    return decorator


# Combat utils
from cython_extensions.combat_utils import (
    cy_adjust_moving_formation as _cy_adjust_moving_formation,
)
from cython_extensions.combat_utils import cy_attack_ready as _cy_attack_ready
from cython_extensions.combat_utils import cy_find_aoe_position as _cy_find_aoe_position
from cython_extensions.combat_utils import cy_get_turn_speed as _cy_get_turn_speed
from cython_extensions.combat_utils import cy_is_facing as _cy_is_facing
from cython_extensions.combat_utils import cy_pick_enemy_target as _cy_pick_enemy_target
from cython_extensions.combat_utils import cy_range_vs_target as _cy_range_vs_target

# Dijkstra
from cython_extensions.dijkstra import cy_dijkstra as _cy_dijkstra

# General utils
from cython_extensions.general_utils import cy_has_creep as _cy_has_creep
from cython_extensions.general_utils import (
    cy_in_pathing_grid_burny as _cy_in_pathing_grid_burny,
)
from cython_extensions.general_utils import (
    cy_in_pathing_grid_ma as _cy_in_pathing_grid_ma,
)
from cython_extensions.general_utils import (
    cy_pylon_matrix_covers as _cy_pylon_matrix_covers,
)
from cython_extensions.general_utils import cy_unit_pending as _cy_unit_pending

# Geometry
from cython_extensions.geometry import cy_angle_diff as _cy_angle_diff
from cython_extensions.geometry import cy_angle_to as _cy_angle_to
from cython_extensions.geometry import cy_distance_to as _cy_distance_to
from cython_extensions.geometry import cy_distance_to_squared as _cy_distance_to_squared
from cython_extensions.geometry import cy_find_average_angle as _cy_find_average_angle
from cython_extensions.geometry import cy_find_correct_line as _cy_find_correct_line
from cython_extensions.geometry import (
    cy_get_angle_between_points as _cy_get_angle_between_points,
)
from cython_extensions.geometry import cy_towards as _cy_towards
from cython_extensions.geometry import (
    cy_translate_point_along_line as _cy_translate_point_along_line,
)

# Map analysis
from cython_extensions.map_analysis import cy_flood_fill_grid as _cy_flood_fill_grid
from cython_extensions.map_analysis import cy_get_bounding_box as _cy_get_bounding_box

# Numpy helper
from cython_extensions.numpy_helper import (
    cy_all_points_below_max_value as _cy_all_points_below_max_value,
)
from cython_extensions.numpy_helper import (
    cy_all_points_have_value as _cy_all_points_have_value,
)
from cython_extensions.numpy_helper import (
    cy_last_index_with_value as _cy_last_index_with_value,
)
from cython_extensions.numpy_helper import cy_point_below_value as _cy_point_below_value
from cython_extensions.numpy_helper import cy_points_with_value as _cy_points_with_value

# Placement solver
from cython_extensions.placement_solver import (
    cy_can_place_structure as _cy_can_place_structure,
)
from cython_extensions.placement_solver import (
    cy_find_building_locations as _cy_find_building_locations,
)

# Import all original Cython functions
# Units utils
from cython_extensions.units_utils import cy_center as _cy_center
from cython_extensions.units_utils import cy_closest_to as _cy_closest_to
from cython_extensions.units_utils import (
    cy_find_units_center_mass as _cy_find_units_center_mass,
)
from cython_extensions.units_utils import cy_in_attack_range as _cy_in_attack_range
from cython_extensions.units_utils import (
    cy_sorted_by_distance_to as _cy_sorted_by_distance_to,
)

# ============================================================================
# UNITS UTILS WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_center)
def cy_center(units: Union[Units, list[Unit]]) -> tuple[float, float]:
    """Given some units, find the center point.


    Example:
    ```py
    from ares.cython_functions.units_utils import cy_center

    centroid: Tuple[float, float] = cy_center(self.workers)

    # centroid_point2 = Point2(centroid)
    ```

    ```
    54.2 µs ± 137 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

    `python-sc2`'s `units.center` alternative:
    107 µs ± 255 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
    ```

    Parameters:
        units: Units we want to check

    Returns:
        Centroid of all units positions

    """
    return _cy_center(units)


@safe_wrapper(_validate_cy_closest_to)
def cy_closest_to(
    position: Union[Point2, tuple[float, float]], units: Union[Units, list[Unit]]
) -> Unit:
    """Iterate through `units` to find closest to `position`.

    Example:
    ```py
    from cython_functions import cy_closest_to
    from sc2.unit import Unit

    closest_unit: Unit = cy_closest_to(self.start_location, self.workers)
    ```

    ```
    14.3 µs ± 135 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

    python-sc2's `units.closest_to()` alternative:
    98.9 µs ± 240 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

    If using python-sc2's `units.closest_to(Point2):
    200 µs ± 1.02 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
    ```

    Parameters:
        position: Position to measure distance from.
        units: Collection of units we want to check.

    Returns:
        Unit closest to `position`.

    """
    return _cy_closest_to(position, units)


@safe_wrapper(_validate_cy_find_units_center_mass)
def cy_find_units_center_mass(
    units: Union[Units, list[Unit]], distance: float
) -> tuple[tuple[float, float], int]:
    """Given some units, find the center mass

    Example:
    ```py
    from cython_functions import cy_find_units_center_mass
    from sc2.position import Point2

    center_mass: Point2
    num_units: int
    center_mass, num_units = cy_find_units_center_mass(self.units, 10.0)
    ```

    ```
    47.8 ms ± 674 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

    python alternative:
    322 ms ± 5.2 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    ```

    Parameters:
        units: Collection of units we want to check.
        distance: The distance to check from the center mass.

    Returns:
        The center mass, and how many units are within `distance` of the center mass.
    """
    return _cy_find_units_center_mass(units, float(distance))


@safe_wrapper(_validate_cy_in_attack_range)
def cy_in_attack_range(
    unit: Unit, units: Union[Units, list[Unit]], bonus_distance: float = 0.0
) -> list[Unit]:
    """Find all units that unit can shoot at.

    Doesn't check if the unit weapon is ready. See:
    `cython_functions.attack_ready`

    Example:
    ```py
    from cython_functions import cy_in_attack_range
    from sc2.unit import Unit

    in_attack_range: list[Unit] = cy_in_attack_range(self.workers[0], self.enemy_units)
    ```

    ```
    7.28 µs ± 26.3 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

    python-sc2's `units.in_attack_range_of(unit)` alternative:
    30.4 µs ± 271 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
    ```

    Parameters:
        unit: The unit to measure distance from.
        units: Collection of units we want to check.
        bonus_distance: Additional distance to consider.

    Returns:
        Units that are in attack range of `unit`.

    """
    return _cy_in_attack_range(unit, units, float(bonus_distance))


@safe_wrapper(_validate_cy_sorted_by_distance_to)
def cy_sorted_by_distance_to(
    units: Union[Units, list[Unit]], position: Point2, reverse: bool = False
) -> list[Unit]:
    """Sort units by distance to `position`

    Example:
    ```py
    from cython_functions import cy_sorted_by_distance_to
    from sc2.unit import Unit

    sorted_by_distance: list[Unit] = cy_sorted_by_distance_to(
        self.workers, self.start_location
    )
    ```

    ```
    33.7 µs ± 190 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)

    python-sc2's `units.sorted_by_distance_to(position)` alternative:
    246 µs ± 830 ns per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
    ```

    Parameters:
        units: Units we want to sort.
        position: Sort by distance to this position.
        reverse: Not currently used.

    Returns:
        Units sorted by distance to position.

    """
    return _cy_sorted_by_distance_to(units, position, reverse)


# ============================================================================
# GEOMETRY WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_distance_to)
def cy_distance_to(
    p1: Union[Point2, tuple[float, float]], p2: Union[Point2, tuple[float, float]]
) -> float:
    """Check distance between two Point2 positions.

    Example:
    ```py
    from cython_functions import cy_distance_to

    dist: float = cy_distance_to(
        self.start_location, self.game_info.map_center
    )
    ```
    ```
    cy_distance_to(Point2, Point2)
    157 ns ± 2.69 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)

    cy_distance_to(unit1.position, unit2.position)
    219 ns ± 10.5 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    Python alternative:

    Point1.distance_to(Point2)
    386 ns ± 2.71 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    unit1.distance_to(unit2)
    583 ns ± 7.89 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)
    ```

    Args:
        p1: First point.
        p2: Measure to this point.

    Returns:
        distance: Distance in tiles.


    """
    return _cy_distance_to(p1, p2)


@safe_wrapper(_validate_cy_distance_to_squared)
def cy_distance_to_squared(
    p1: Union[Point2, tuple[float, float]], p2: Union[Point2, tuple[float, float]]
) -> float:
    """Similar to `cy_distance_to` but without a square root operation.
    Use this for ~1.3x speedup

    Example:
    ```python
    from cython_functions import cy_distance_to_squared

    dist: float = cy_distance_to_squared(
        self.start_location, self.game_info.map_center
    )
    ```

    Args:
        p1: First point.
        p2: Measure to this point.

    Returns:
        distance: Distance in tiles, squared.
    """
    return _cy_distance_to_squared(p1, p2)


@safe_wrapper(_validate_cy_towards)
def cy_towards(
    start_pos: Point2, target_pos: Point2, distance: float
) -> tuple[float, float]:
    """Get position from start_pos towards target_pos based on distance.

    Example:
    ```py
    from cython_functions import cy_towards

    new_pos: Tuple[float, float] = cy_towards(
        self.start_location,
        self.game_info.map_center,
        12.0
    )
    ```

    Note: For performance reasons this returns the point2 as a tuple, if a
    python-sc2 Point2 is required it's up to the user to convert it.

    Example:
    ```py
    new_pos: Point2 = Point2(
        cy_towards(
            self.start_location, self.enemy_start_locations, 10.0
        )
    )
    ```

    Though for best performance it is recommended to simply work with the tuple if possible:
    ```py
    new_pos: tuple[float, float] = cy_towards(
        self.start_location, self.enemy_start_locations, 10.0
    )
    ```

    ```
    191 ns ± 0.855 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)

    Python-sc2's `start_pos.towards(target_pos, distance)` alternative:
    2.73 µs ± 18.9 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    ```


    Args:
        start_pos: Start from this 2D position.
        target_pos: Go towards this 2D position.
        distance: How far we go towards target_pos.

    Returns:
        The new position as a tuple of x and y coordinates.
    """
    return _cy_towards(start_pos, target_pos, float(distance))


@safe_wrapper(_validate_cy_angle_to)
def cy_angle_to(from_pos, to_pos):
    """Type-safe wrapper for cy_angle_to."""
    return _cy_angle_to(from_pos, to_pos)


@safe_wrapper(_validate_cy_angle_diff)
def cy_angle_diff(a: float, b: float) -> float:
    """Absolute angle difference between 2 angles

    Args:
        a: First angle.
        b: Second angle.

    Returns:
        angle_difference: Difference between the two angles.
    """
    return _cy_angle_diff(float(a), float(b))


@safe_wrapper(_validate_cy_find_average_angle)
def cy_find_average_angle(
    start_point: Union[Point2, tuple[float, float]],
    reference_point: Union[Point2, tuple[float, float]],
    points: list[Point2],
) -> float:
    """Find the average angle between the points and the reference point.

    Given a starting point, a reference point, and a list of points, find the average
    angle between the vectors from the starting point to the reference point and the
    starting point to the points.

    Example:
    ```py
    from cython_extensions import cy_find_average_angle

    angle: float = cy_get_angle_between_points(
        self.start_location,
        self.game_info.map_center,
        [w.position for w in self.workers]
    )
    ```

    Args:
        start_point: Origin for the vectors to the other given points.
        reference_point: Vector forming one leg of the angle.
        points: Points to calculate the angle between relative
            to the reference point.

    Returns:
        Average angle in radians between the reference
        point and the given points.

    """
    return _cy_find_average_angle(start_point, reference_point, points)


@safe_wrapper(_validate_cy_get_angle_between_points)
def cy_get_angle_between_points(
    point_a: Union[Point2, tuple[float, float]],
    point_b: Union[Point2, tuple[float, float]],
) -> float:
    """Get the angle between two points as if they were vectors from the origin.

    Example:
    ```py
    from cython_functions import cy_get_angle_between_points

    angle: float = cy_get_angle_between_points(
        self.start_location, self.game_info.map_center
    )
    ```

    Args:
        point_a: First point.
        point_b: Measure to this point.

    Returns:
        The angle between the two points.
    """
    return _cy_get_angle_between_points(point_a, point_b)


@safe_wrapper(_validate_cy_translate_point_along_line)
def cy_translate_point_along_line(
    point: Union[Point2, tuple[float, float]], a_value: float, distance: float
) -> tuple[float, float]:
    """
    Translates a point along a line defined by a slope value.

    This function moves a given point along a line in a direction
    determined by the slope `a_value`, by a specified `distance`.
    The new point after translation is returned.

    Args:
        point: The point to be translated, given as either a `Point2`
        object or a tuple of `(x, y)` coordinates.
        a_value: The slope of the line along which the point will be moved.
        distance: The distance to move the point along the line.

    Returns:
        A tuple representing the new position of the point
        after translation.
    """
    return _cy_translate_point_along_line(point, a_value, float(distance))


# Pass-through functions that don't need validation yet
cy_find_correct_line = _cy_find_correct_line


# ============================================================================
# COMBAT UTILS WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_attack_ready)
def cy_attack_ready(bot, unit, target):
    """Type-safe wrapper for cy_attack_ready."""
    return _cy_attack_ready(bot, unit, target)


@safe_wrapper(_validate_cy_is_facing)
def cy_is_facing(unit, other_unit, angle_error: float = 0.3):
    """Type-safe wrapper for cy_is_facing."""
    return _cy_is_facing(unit, other_unit, angle_error)


@safe_wrapper(_validate_cy_range_vs_target)
def cy_range_vs_target(unit, target):
    """Type-safe wrapper for cy_range_vs_target."""
    return _cy_range_vs_target(unit, target)


@safe_wrapper(_validate_cy_pick_enemy_target)
def cy_pick_enemy_target(enemies):
    """Type-safe wrapper for cy_pick_enemy_target."""
    return _cy_pick_enemy_target(enemies)


@safe_wrapper(_validate_cy_find_aoe_position)
def cy_find_aoe_position(effect_radius, targets, min_units: int = 1, bonus_tags=None):
    """Type-safe wrapper for cy_find_aoe_position."""
    return _cy_find_aoe_position(effect_radius, targets, min_units, bonus_tags)


@safe_wrapper(_validate_cy_get_turn_speed)
def cy_get_turn_speed(unit, unit_type_int):
    """Type-safe wrapper for cy_get_turn_speed."""
    return _cy_get_turn_speed(unit, unit_type_int)


# Pass-through functions that don't need validation yet
cy_adjust_moving_formation = _cy_adjust_moving_formation


# ============================================================================
# GENERAL UTILS WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_has_creep)
def cy_has_creep(creep_numpy_grid, position):
    """Type-safe wrapper for cy_has_creep."""
    return _cy_has_creep(creep_numpy_grid, position)


@safe_wrapper(_validate_cy_in_pathing_grid_burny)
def cy_in_pathing_grid_burny(pathing_numpy_grid, position):
    """Type-safe wrapper for cy_in_pathing_grid_burny."""
    return _cy_in_pathing_grid_burny(pathing_numpy_grid, position)


@safe_wrapper(_validate_cy_in_pathing_grid_ma)
def cy_in_pathing_grid_ma(pathing_numpy_grid, position):
    """Type-safe wrapper for cy_in_pathing_grid_ma."""
    return _cy_in_pathing_grid_ma(pathing_numpy_grid, position)


@safe_wrapper(_validate_cy_unit_pending)
def cy_unit_pending(bot, unit_type):
    """Type-safe wrapper for cy_unit_pending."""
    return _cy_unit_pending(bot, unit_type)


@safe_wrapper(_validate_cy_pylon_matrix_covers)
def cy_pylon_matrix_covers(position, pylons, height_grid, pylon_build_progress=1.0):
    """Type-safe wrapper for cy_pylon_matrix_covers."""
    return _cy_pylon_matrix_covers(position, pylons, height_grid, pylon_build_progress)


# ============================================================================
# MAP ANALYSIS WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_flood_fill_grid)
def cy_flood_fill_grid(
    start_point, terrain_grid, pathing_grid, max_distance, cutoff_points
):
    """Type-safe wrapper for cy_flood_fill_grid."""
    return _cy_flood_fill_grid(
        start_point, terrain_grid, pathing_grid, max_distance, cutoff_points
    )


@safe_wrapper(_validate_cy_get_bounding_box)
def cy_get_bounding_box(coordinates):
    """Type-safe wrapper for cy_get_bounding_box."""
    return _cy_get_bounding_box(coordinates)


# ============================================================================
# NUMPY HELPER WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_all_points_below_max_value)
def cy_all_points_below_max_value(grid, max_value, points_to_check):
    """Type-safe wrapper for cy_all_points_below_max_value."""
    return _cy_all_points_below_max_value(grid, max_value, points_to_check)


@safe_wrapper(_validate_cy_all_points_have_value)
def cy_all_points_have_value(grid, value, points):
    """Type-safe wrapper for cy_all_points_have_value."""
    return _cy_all_points_have_value(grid, value, points)


@safe_wrapper(_validate_cy_point_below_value)
def cy_point_below_value(grid, position, weight_safety_limit=1.0):
    """Type-safe wrapper for cy_point_below_value."""
    return _cy_point_below_value(grid, position, weight_safety_limit)


@safe_wrapper(_validate_cy_points_with_value)
def cy_points_with_value(grid, value, points):
    """Type-safe wrapper for cy_points_with_value."""
    return _cy_points_with_value(grid, value, points)


@safe_wrapper(_validate_cy_last_index_with_value)
def cy_last_index_with_value(grid, value, points):
    """Type-safe wrapper for cy_last_index_with_value."""
    return _cy_last_index_with_value(grid, value, points)


# ============================================================================
# PLACEMENT SOLVER WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_can_place_structure)
def cy_can_place_structure(
    building_origin,
    building_size,
    creep_grid,
    placement_grid,
    pathing_grid,
    avoid_creep=True,
    include_addon=False,
    skip_creep_check=False,
):
    """Type-safe wrapper for cy_can_place_structure."""
    return _cy_can_place_structure(
        building_origin,
        building_size,
        creep_grid,
        placement_grid,
        pathing_grid,
        avoid_creep,
        include_addon,
        skip_creep_check,
    )


@safe_wrapper(_validate_cy_find_building_locations)
def cy_find_building_locations(
    kernel,
    x_stride,
    y_stride,
    x_bounds,
    y_bounds,
    creep_grid,
    placement_grid,
    pathing_grid,
    points_to_avoid_grid,
    building_width,
    building_height,
    avoid_creep=True,
):
    """Type-safe wrapper for cy_find_building_locations."""
    return _cy_find_building_locations(
        kernel,
        x_stride,
        y_stride,
        x_bounds,
        y_bounds,
        creep_grid,
        placement_grid,
        pathing_grid,
        points_to_avoid_grid,
        building_width,
        building_height,
        avoid_creep,
    )


# ============================================================================
# DIJKSTRA WRAPPERS
# ============================================================================


@safe_wrapper(_validate_cy_dijkstra)
def cy_dijkstra(cost, targets, checks_enabled=True):
    """Type-safe wrapper for cy_dijkstra."""
    return _cy_dijkstra(cost, targets, checks_enabled)


# ============================================================================
# EXPORT ALL FUNCTIONS
# ============================================================================

__all__ = [
    # Units utils
    "cy_center",
    "cy_closest_to",
    "cy_find_units_center_mass",
    "cy_in_attack_range",
    "cy_sorted_by_distance_to",
    # Geometry
    "cy_distance_to",
    "cy_distance_to_squared",
    "cy_towards",
    "cy_angle_to",
    "cy_angle_diff",
    "cy_find_average_angle",
    "cy_find_correct_line",
    "cy_get_angle_between_points",
    "cy_translate_point_along_line",
    # Combat utils
    "cy_adjust_moving_formation",
    "cy_attack_ready",
    "cy_find_aoe_position",
    "cy_get_turn_speed",
    "cy_is_facing",
    "cy_pick_enemy_target",
    "cy_range_vs_target",
    # General utils
    "cy_has_creep",
    "cy_in_pathing_grid_burny",
    "cy_in_pathing_grid_ma",
    "cy_pylon_matrix_covers",
    "cy_unit_pending",
    # Map analysis
    "cy_flood_fill_grid",
    "cy_get_bounding_box",
    # Numpy helper
    "cy_all_points_below_max_value",
    "cy_all_points_have_value",
    "cy_last_index_with_value",
    "cy_point_below_value",
    "cy_points_with_value",
    # Placement solver
    "cy_can_place_structure",
    "cy_find_building_locations",
    # Dijkstra
    "cy_dijkstra",
]
