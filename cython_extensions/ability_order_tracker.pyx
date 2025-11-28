# cython: boundscheck=False, wraparound=False, cdivision=True
"""
Optimized Cython implementation for tracking ability counts and build progress.
Replaces the Python _abilities_count_and_build_progress method for maximum speed.
"""

from sc2.data import Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId




cpdef dict cy_abilities_count_and_build_progress(object bot):
    """
    Fast Cython implementation to count abilities in progress.
    
    Returns a dict mapping AbilityId -> count (int).
    This replaces bot._abilities_count_and_build_progress[0] for counting.
    
    Args:
        bot: BotAI instance with units, structures, race, and game_data
        
    Returns:
        dict[AbilityId, int]: Counter of ability exact_ids currently active
    """
    cdef:
        dict abilities_amount = {}
        object unit
        object order
        object creation_ability
        Py_ssize_t i, j, len_units, len_orders
        object units_list
        object structures_list
        object all_units
        int current_count
        bint is_terran = bot.race == Race.Terran
        object local_get = abilities_amount.get
        
    # Combine units and structures into a single list once to avoid repeated concatenation
    units_list = bot.units
    structures_list = bot.structures
    
    # Process all units and structures
    len_units = len(units_list)
    for i in range(len_units):
        unit = units_list[i]
        
        # Count orders for this unit
        len_orders = len(unit.orders)
        for j in range(len_orders):
            order = unit.orders[j]
            creation_ability = order.ability.exact_id
            # Fast increment: read current count, add 1, store back
            current_count = <int> local_get(creation_ability, 0)
            abilities_amount[creation_ability] = current_count + 1
        
        # Count units/structures not yet ready (in production/construction)
        # Skip Terran structures (SCV building counts would double-count)
        if not unit.is_ready and (not is_terran or not unit.is_structure):
            # Check if this unit type needs special handling
            if unit.type_id in CREATION_ABILITY_FIX:
                if unit.type_id == UnitTypeId.ARCHON:
                    # Archon morphs from 2 units, count as 2
                    creation_ability = AbilityId.ARCHON_WARP_TARGET
                    current_count = <int> local_get(creation_ability, 0)
                    abilities_amount[creation_ability] = current_count + 2
                else:
                    # Other special cases (e.g., rich geysers)
                    creation_ability = CREATION_ABILITY_FIX[unit.type_id]
                    current_count = <int> local_get(creation_ability, 0)
                    abilities_amount[creation_ability] = current_count + 1
            else:
                # Standard case: lookup creation ability from game data
                try:
                    creation_ability = bot.game_data.units[unit.type_id.value].creation_ability.exact_id
                    current_count = <int> local_get(creation_ability, 0)
                    abilities_amount[creation_ability] = current_count + 1
                except Exception:
                    # Skip units without valid creation ability
                    pass
    
    # Process structures
    len_units = len(structures_list)
    for i in range(len_units):
        unit = structures_list[i]
        
        # Count orders
        len_orders = len(unit.orders)
        for j in range(len_orders):
            order = unit.orders[j]
            creation_ability = order.ability.exact_id
            current_count = <int> local_get(creation_ability, 0)
            abilities_amount[creation_ability] = current_count + 1
        
        # Count structures not yet ready (skip Terran structures being built)
        if not unit.is_ready and (not is_terran or not unit.is_structure):
            if unit.type_id in CREATION_ABILITY_FIX:
                if unit.type_id == UnitTypeId.ARCHON:
                    creation_ability = AbilityId.ARCHON_WARP_TARGET
                    current_count = <int> local_get(creation_ability, 0)
                    abilities_amount[creation_ability] = current_count + 2
                else:
                    creation_ability = CREATION_ABILITY_FIX[unit.type_id]
                    current_count = <int> local_get(creation_ability, 0)
                    abilities_amount[creation_ability] = current_count + 1
            else:
                try:
                    creation_ability = bot.game_data.units[unit.type_id.value].creation_ability.exact_id
                    current_count = <int> local_get(creation_ability, 0)
                    abilities_amount[creation_ability] = current_count + 1
                except Exception:
                    pass
    
    return abilities_amount

#TEMPORRARY placing it here until we cythonize the tracker file, does not work yet
@cache_per_game_loop
def _abilities_count_structures(bot):
    """Cache for the already_pending function, includes protoss units warping in,
    all units in production and all structures, and all morphs"""
    abilities_amount: Counter[AbilityId] = Counter()

    for worker in bot.workers:
        for order in worker.orders:
            abilities_amount[order.ability.exact_id] += 1
    if bot.race == Race.Terran:
        return abilities_amount

    for structure in bot.structures:
        if structure.build_progress < 1.0:
            # If an SCV is constructing a building, already_pending would count this structure twice
            # (once from the SCV order, and once from "not structure.is_ready")
            type_id = structure.type_id
            if type_id in UNIT_TYPE_ID_TO_ABILITY_MAP:
                creation_ability: AbilityId = UNIT_TYPE_ID_TO_ABILITY_MAP[type_id]
                abilities_amount[creation_ability] += 1

    return abilities_amount



def cache_per_game_loop(func):
    """Decorator to cache a method's result until bot.state.game_loop changes."""
    cache_name = f"_{func.__name__}_cache"
    loop_name = f"_{func.__name__}_loop"

    def wrapper(bot, *args, **kwargs):
        current_loop = bot.state.game_loop
        if getattr(bot, loop_name, object()) == current_loop:
            return getattr(bot, cache_name)
        result = func(bot, *args, **kwargs)
        setattr(bot, cache_name, result)
        setattr(bot, loop_name, current_loop)
        return result
    return wrapper


# Willl edit general_utils.pyx to use this cythonized function later