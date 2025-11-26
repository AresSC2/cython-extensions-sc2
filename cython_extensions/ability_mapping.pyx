# cython: boundscheck=False, wraparound=False, cdivision=True
cimport cython



cdef int MAX_KEY = 4200
cdef int mapping_array[4200]

# only set the ones you need
mapping_array[18] = 318 #CommandCenter
mapping_array[19] = 319 #SupplyDepot
mapping_array[20] = 320 #Refinery
mapping_array[21] = 321 #Barracks
mapping_array[22] = 322 #EngineeringBay
mapping_array[23] = 323 #missileTurret
mapping_array[24] = 324 #Bunker


mapping_array[25] = 326 #SensorTower
mapping_array[26] = 327 #GhostAcademy
mapping_array[27] = 328 #Factory
mapping_array[28] = 329 #Starport

mapping_array[29] = 331 #Armory
mapping_array[30] = 333 #FusionCore

mapping_array[37] = 421 #TechLab Barracks
mapping_array[38] = 422 #Reactor Barracks
mapping_array[39] = 454 #TechLab Factory
mapping_array[40] = 455 #Reactor Factory
mapping_array[41] = 487 #TechLab Starport
mapping_array[42] = 488 #Reactor Starport

mapping_array[130] = 1450 #PlanetaryFortress
mapping_array[132] = 1516 #OrbitalCommand

mapping_array[59] = 880 #Nexus
mapping_array[60] = 881 #Pylon
mapping_array[61] = 882 #Assimilator
mapping_array[62] = 883 #Gateway
mapping_array[63] = 884 #Forge
mapping_array[64] = 885 #FleetBeacon
mapping_array[65] = 886 #TwilightCouncil
mapping_array[66] = 887 #PhotonCannon
mapping_array[67] = 889 #Stargate
mapping_array[68] = 890 #TemplarArchive
mapping_array[69] = 891 #DarkShrine
mapping_array[70] = 892 #RoboticsBay
mapping_array[71] = 893 #RoboticsFacility
mapping_array[72] = 894 #CyberneticsCore
mapping_array[1910] = 895 #ShieldBattery




mapping_array[86] = 1152 #Hatchery
mapping_array[87] = 1153 #CreepTumor
mapping_array[88] = 1154 #Extractor
mapping_array[89] = 1155 #SpawningPool
mapping_array[90] = 1156 #EvolutionChamber
mapping_array[91] = 1157 #HydraliskDen
mapping_array[92] = 1158 #Spire
mapping_array[93] = 1159 #UltraliskCavern
mapping_array[94] = 1160 #InfestationPit
mapping_array[95] = 1161 #NydusNetwork
mapping_array[96] = 1162 #BanelingNest

mapping_array[97] = 1165 #RoachWarren
mapping_array[98] = 1166 #SpineCrawler
mapping_array[99] = 1167 #SporeCrawler


@cython.cfunc
@cython.inline
cdef int _map_value(int key) nogil:
    if 0 <= key < MAX_KEY:
        return mapping_array[key]
    return -1


def map_value(int key):
    return _map_value(key)
