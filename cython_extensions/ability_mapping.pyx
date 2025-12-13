# cython: boundscheck=False, wraparound=False, cdivision=True
cimport cython
from sc2.ids.ability_id import AbilityId
from libc.string cimport memset


cdef int MAX_KEY = 2200
cdef int mapping_array[2200]
cdef public int STRUCT_ABILITIES[1620] #changes nothing 


@cython.cfunc
@cython.inline
cpdef int map_value(int key) nogil:
    if 0 <= key < MAX_KEY:
        return mapping_array[key]
    return -1


# Rewritten mappings from UNIT_TYPE_ID_TO_ABILITY_MAP, Updated at 2025-12-13 14:26:03.974413
mapping_array[5] = 3682  # TECHLAB
mapping_array[18] = 318  # COMMANDCENTER
mapping_array[19] = 319  # SUPPLYDEPOT
mapping_array[20] = 320  # REFINERY
mapping_array[21] = 321  # BARRACKS
mapping_array[22] = 322  # ENGINEERINGBAY
mapping_array[23] = 323  # MISSILETURRET
mapping_array[24] = 324  # BUNKER
mapping_array[25] = 326  # SENSORTOWER
mapping_array[26] = 327  # GHOSTACADEMY
mapping_array[27] = 328  # FACTORY
mapping_array[28] = 329  # STARPORT
mapping_array[29] = 331  # ARMORY
mapping_array[30] = 333  # FUSIONCORE
mapping_array[37] = 421  # BARRACKSTECHLAB
mapping_array[38] = 422  # BARRACKSREACTOR
mapping_array[39] = 454  # FACTORYTECHLAB
mapping_array[40] = 455  # FACTORYREACTOR
mapping_array[41] = 487  # STARPORTTECHLAB
mapping_array[42] = 488  # STARPORTREACTOR
mapping_array[59] = 880  # NEXUS
mapping_array[60] = 881  # PYLON
mapping_array[61] = 882  # ASSIMILATOR
mapping_array[62] = 883  # GATEWAY
mapping_array[63] = 884  # FORGE
mapping_array[64] = 885  # FLEETBEACON
mapping_array[65] = 886  # TWILIGHTCOUNCIL
mapping_array[66] = 887  # PHOTONCANNON
mapping_array[67] = 889  # STARGATE
mapping_array[68] = 890  # TEMPLARARCHIVE
mapping_array[69] = 891  # DARKSHRINE
mapping_array[70] = 892  # ROBOTICSBAY
mapping_array[71] = 893  # ROBOTICSFACILITY
mapping_array[72] = 894  # CYBERNETICSCORE
mapping_array[86] = 1152  # HATCHERY
mapping_array[88] = 1154  # EXTRACTOR
mapping_array[89] = 1155  # SPAWNINGPOOL
mapping_array[90] = 1156  # EVOLUTIONCHAMBER
mapping_array[91] = 1157  # HYDRALISKDEN
mapping_array[92] = 1158  # SPIRE
mapping_array[93] = 1159  # ULTRALISKCAVERN
mapping_array[94] = 1160  # INFESTATIONPIT
mapping_array[95] = 1161  # NYDUSNETWORK
mapping_array[96] = 1162  # BANELINGNEST
mapping_array[97] = 1165  # ROACHWARREN
mapping_array[98] = 1166  # SPINECRAWLER
mapping_array[99] = 1167  # SPORECRAWLER
mapping_array[100] = 1216  # LAIR
mapping_array[101] = 1218  # HIVE
mapping_array[130] = 1450  # PLANETARYFORTRESS
mapping_array[132] = 1516  # ORBITALCOMMAND
mapping_array[1910] = 895  # SHIELDBATTERY
mapping_array[1943] = 320  # REFINERYRICH
mapping_array[1994] = 882  # ASSIMILATORRICH
mapping_array[1995] = 1154  # EXTRACTORRICH

# STRUCT_ABILLITIES
STRUCT_ABILITIES[318] = 2  # TERRANBUILD_COMMANDCENTER
STRUCT_ABILITIES[421] = 1  # BUILD_TECHLAB_BARRACKS
STRUCT_ABILITIES[422] = 1  # BUILD_REACTOR_BARRACKS
STRUCT_ABILITIES[454] = 1  # BUILD_TECHLAB_FACTORY
STRUCT_ABILITIES[455] = 1  # BUILD_REACTOR_FACTORY
STRUCT_ABILITIES[487] = 1  # BUILD_TECHLAB_STARPORT
STRUCT_ABILITIES[488] = 1  # BUILD_REACTOR_STARPORT
STRUCT_ABILITIES[1152] = 2  # ZERGBUILD_HATCHERY
STRUCT_ABILITIES[1216] = 2  # UPGRADETOLAIR_LAIR
STRUCT_ABILITIES[1218] = 1  # UPGRADETOHIVE_HIVE
STRUCT_ABILITIES[1450] = 1  # UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS
STRUCT_ABILITIES[1516] = 1  # UPGRADETOORBITAL_ORBITALCOMMAND
