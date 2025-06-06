from cython cimport boundscheck, wraparound

import numpy as np

from cython_extensions.geometry import cy_distance_to, cy_distance_to_squared
from cython_extensions.unit_data import UNIT_DATA

cimport numpy as cnp

UNIT_DATA_INT_KEYS = {k.value: v for k, v in UNIT_DATA.items()}


@boundscheck(False)
@wraparound(False)
cpdef (double, double) cy_center(object units):
    """Returns the central position of all units."""
    cdef:
        unsigned int i = 0
        double MAX_THRESHOLD = 600.0
        Py_ssize_t num_units = len(units)
        double sum_x, sum_y, x, y
        (double, double) position
        object unit

    sum_x = 0
    sum_y = 0

    for i in range(num_units):
        pos = units[i].position
        position = (pos.x, pos.y)
        sum_x += position[0]
        sum_y += position[1]
    x = sum_x / num_units
    y = sum_y / num_units
    # there are some very rare scenarios where we get a rather large
    # x or y, in this case just return what we have in `position`
    if x > MAX_THRESHOLD or y > MAX_THRESHOLD:
        return position
    return (x, y)


@boundscheck(False)
@wraparound(False)
cpdef object cy_closest_to((float, float) position, object units):
    """
    14.9 µs ± 159 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
    
    python-sc2 `units.closest_to` alternative:
    Closest to a Point2:
    301 µs ± 4.34 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
    Closest to a Unit
    115 µs ± 2.25 µs per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
    """
    cdef:
        object closest = units[0]
        double closest_dist = 999.9
        double dist = 0.0
        unsigned int len_units = len(units)
        (float, float) pos

    for i in range(len_units):
        unit = units[i]
        pos = unit.position
        dist = cy_distance_to_squared((pos[0], pos[1]), (position[0], position[1]))
        if dist < closest_dist:
            closest_dist = dist
            closest = unit

    return closest

@boundscheck(False)
@wraparound(False)
cpdef tuple cy_find_units_center_mass(units, double distance):
    cdef:
        unsigned int max_units_found = 0
        (double, double) center_position
        double distance_check = distance * distance
        list positions = [u.position for u in units]
        (double, double) pos_1, pos_2
        unsigned int units_found
        unsigned int num_units = len(positions)
        double dist_sq
        Py_ssize_t i, j

    for i in range(num_units):
        units_found = 0
        pos_1 = positions[i]
        for j in range(num_units):
            pos_2 = positions[j]
            dist_sq = cy_distance_to_squared(pos_1, pos_2)
            if dist_sq < distance_check:
                units_found += 1

        if units_found > max_units_found:
            max_units_found = units_found
            center_position = pos_1

    return center_position, max_units_found

@boundscheck(False)
@wraparound(False)
cpdef list cy_in_attack_range(object unit, object units, double bonus_distance = 0.0):
    if not unit.can_attack:
        return []

    cdef:
        unsigned int x, len_units, type_id_int
        double dist, air_range, ground_range, radius, other_u_radius
        (float, float) unit_pos, other_unit_pos
        bint other_unit_flying, can_shoot_air, can_shoot_ground
        list returned_units

    can_shoot_air = unit.can_attack_air
    can_shoot_ground = unit.can_attack_ground
    len_units = len(units)
    returned_units = []
    unit_pos = unit.position
    radius = unit.radius
    air_range = unit.air_range
    ground_range = unit.ground_range

    for x in range(len_units):
        u = units[x]
        # this is faster than getting the UnitTypeID
        type_id_int = u._proto.unit_type
        unit_data = UNIT_DATA_INT_KEYS.get(type_id_int, None)
        if unit_data:
            other_unit_flying = unit_data["flying"]
            other_unit_pos = u.position
            other_u_radius = u.radius
            dist = cy_distance_to(unit_pos, other_unit_pos)

            # type_id_int == 4 is colossus
            if can_shoot_air and (other_unit_flying or type_id_int == 4):
                if dist <= air_range + radius + other_u_radius + bonus_distance:
                    returned_units.append(u)
                    # already added, no need to attempt logic below
                    continue

            if can_shoot_ground and not other_unit_flying:
                if dist <= ground_range + radius + other_u_radius + bonus_distance:
                    returned_units.append(u)

    return returned_units

cpdef list cy_sorted_by_distance_to(object units, (float, float) position, bint reverse=False):
    cdef:
        unsigned int len_units = len(units)
        cnp.ndarray[cnp.npy_double, ndim=1] distances = np.empty(len_units)
        # TODO: couldn't get this to work, so no speedup for `indices` currently
        # cnp.ndarray[cnp.npy_double, ndim=1] indices = np.empty(len_units)
        unsigned int i, j

    for i in range(len_units):
        distances[i] = cy_distance_to_squared(units[i].position, position)

    indices = distances.argsort()

    return [units[j] for j in indices]
