__version__ = "0.1.0"

# bootstrap is the only module which
# can be loaded with default Python-machinery
# because the resulting extension is called `bootstrap`:
from . import bootstrap

# injecting our finders into sys.meta_path
# after that all other submodules can be loaded
bootstrap.bootstrap_cython_submodules()

from cython_extensions.combat_utils import (
    cy_get_turn_speed,
    cy_range_vs_target,
    cy_is_facing,
    cy_attack_ready,
    cy_pick_enemy_target
)

from cython_extensions.general_utils import (
    cy_add_neighbors_to_ignore,
    cy_get_neighbors8,
    cy_pylon_matrix_covers,
    cy_unit_pending
)

from cython_extensions.geometry import (
    cy_distance_to_squared,
    cy_distance_to,
    cy_angle_to,
    cy_angle_diff,
    cy_find_correct_line,
    cy_find_average_angle,
    cy_get_angle_between_points,
    cy_translate_point_along_line,
    cy_towards
)

from cython_extensions.map_analysis import (
    cy_get_bounding_box,
    cy_flood_fill_grid
)

from cython_extensions.numpy_helper import (
    cy_last_index_with_value,
    cy_point_below_value,
    cy_points_with_value,
    cy_all_points_below_max_value,
    cy_all_points_have_value
)

from cython_extensions.placement_solver import (
    can_place_structure,
    find_building_locations
)

from cython_extensions.units_utils import (
    cy_distance_to_squared,
    cy_closest_to,
    cy_center,
    cy_in_attack_range,
    cy_sorted_by_distance_to
)
