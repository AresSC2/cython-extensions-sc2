# cython: boundscheck=False, wraparound=False, cdivision=True
"""
Optimized Cython implementation for tracking ability counts and build progress.
Replaces the Python _abilities_count_and_build_progress method for maximum speed.
"""

from sc2.data import Race

from cython_extensions.ability_mapping cimport map_value
from cython_extensions.ability_mapping cimport STRUCT_ABILITIES
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.data import Race
from cython cimport boundscheck, wraparound
from libc.stdlib cimport malloc, free
from libc.string cimport memset



#TEMPORARRY placing it here until we cythonize the tracker file, does not work yet
cdef struct AbilityCount:
    int ability_id
    int count

# Disable Python checks for speed
@boundscheck(False)
@wraparound(False)
cpdef AbilityCount[:] abilities_count_structures(object bot):
    """
    Build a C array indexed by ability_id that stores counts.
    Returns: memoryview of AbilityCount (size = 2200)
    """

    cdef int MAX_ABILITIES = 2200
    cdef AbilityCount* arr = <AbilityCount*> malloc(MAX_ABILITIES * sizeof(AbilityCount))

    # ... fill arr ...

    memset(arr, 0, MAX_ABILITIES * sizeof(AbilityCount))

    cdef object unit
    cdef object order
    cdef int aid
    # special ability ids that should always be counted if seen

    cdef object structures = bot.structures
    cdef object workers = bot.workers


    # Workers orders → ability_id count

    #FUTURE exclude this for ares?
    for unit in workers:
        for order in unit.orders:
            aid = <int> order.ability._proto.ability_id #FUTURE add mapping table for order.ability?
            if 0 <= aid < MAX_ABILITIES:
                arr[aid].count += 1


    race = bot.race
    # Structures → build progress < 1.0 → increment creation ability
    if race == Race.Protoss:
        for unit in structures:
            if <double> unit.build_progress < 1.0:
                aid = <int> map_value(unit.type_id.value)
                if aid!=-1:
                    arr[aid].count += 1

    elif race == Race.Zerg:
        for unit in structures:
            aid = <int> map_value(unit.type_id.value)
            if <double> unit.build_progress < 1.0:
                if aid!=-1:
                    arr[aid].count += 1
            elif STRUCT_ABILITIES[aid]==2:  #identify Lair, Hive in the same way as others to save time
             # Lair and Hive
                for order in unit.orders:
                    aid = <int> order.ability._proto.ability_id
                    if STRUCT_ABILITIES[aid]:
                        arr[aid].count += 1
    
    #for terran, count PF, OC, Reactor, Tech Lab too
    else:
        for unit in structures:
            aid = <int> map_value(unit.type_id.value)
            if <double> unit.build_progress < 1.0:
                if STRUCT_ABILITIES[aid]:
                    arr[aid].count += 1
            elif STRUCT_ABILITIES[aid]==2:  #identify Commandcenter, but in the same way as others to save time
             # Command Center for OC and PF
                for order in unit.orders:
                    aid = <int> order.ability._proto.ability_id
                    if STRUCT_ABILITIES[aid]:
                        arr[aid].count += 1
        
    # Return as Python-usable memoryview
    return <AbilityCount[:MAX_ABILITIES]> arr


def cache_per_game_loop(func):
    cache_name = f"_{func.__name__}_cache"
    loop_name = f"_{func.__name__}_loop"
    def wrapper(bot, *args, **kwargs):
        current_loop = bot.state.game_loop
        if getattr(bot, loop_name, None) == current_loop:
            return getattr(bot, cache_name)
        result = func(bot, *args, **kwargs)
        setattr(bot, cache_name, result)
        setattr(bot, loop_name, current_loop)
        return result
    return wrapper

@cache_per_game_loop
def cy_abilities_count_structures(bot):
    return abilities_count_structures(bot)
