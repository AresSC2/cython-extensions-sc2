from typing import Dict

from sc2.ids.unit_typeid import UnitTypeId as UnitID


cdef struct TurnRateData:
    float turn_rate

# movement turn rate
TURN_RATE: Dict[UnitID, TurnRateData] = {
    UnitID.BALL: 720.0,
    UnitID.COLOSSUS: float('inf'),
    UnitID.INFESTORTERRAN: 999.8437,
    UnitID.BANELING: 999.8437,
    UnitID.MOTHERSHIP: float('inf'),
    UnitID.CHANGELING: 999.8437,
    UnitID.CHANGELINGZEALOT: 999.8437,
    UnitID.CHANGELINGMARINESHIELD: 999.8437,
    UnitID.CHANGELINGMARINE: 999.8437,
    UnitID.CHANGELINGZERGLINGWINGS: 999.8437,
    UnitID.CHANGELINGZERGLING: 999.8437,
    UnitID.SIEGETANK: 360.0,
    UnitID.SIEGETANKSIEGED: 360.0,
    UnitID.VIKINGASSAULT: 720.0,
    UnitID.VIKINGFIGHTER: 999.8437,
    UnitID.COMMANDCENTERFLYING: 720.0,
    UnitID.FACTORYFLYING: 720.0,
    UnitID.STARPORTFLYING: 720.0,
    UnitID.SCV: 999.8437,
    UnitID.BARRACKSFLYING: 720.0,
    UnitID.MARINE: 999.8437,
    UnitID.REAPER: 999.8437,
    UnitID.GHOST: 999.8437,
    UnitID.MARAUDER: 999.8437,
    UnitID.THOR: 360.0,
    UnitID.HELLION: 720.0,
    UnitID.MEDIVAC: 999.8437,
    UnitID.BANSHEE: 1499.9414,
    UnitID.RAVEN: 999.8437,
    UnitID.BATTLECRUISER: 720.0,
    UnitID.ZEALOT: 999.8437,
    UnitID.STALKER: 999.8437,
    UnitID.HIGHTEMPLAR: 999.8437,
    UnitID.DARKTEMPLAR: 999.8437,
    UnitID.SENTRY: 999.8437,
    UnitID.PHOENIX: 1499.9414,
    UnitID.CARRIER: 720.0,
    UnitID.VOIDRAY: 999.8437,
    UnitID.WARPPRISM: 720.0,
    UnitID.OBSERVER: 720.0,
    UnitID.IMMORTAL: float('inf'),
    UnitID.PROBE: 999.8437,
    UnitID.INTERCEPTOR: 999.8437,
    UnitID.DRONE: 999.8437,
    UnitID.ZERGLING: 999.8437,
    UnitID.OVERLORD: 999.8437,
    UnitID.HYDRALISK: 999.8437,
    UnitID.MUTALISK: 1499.9414,
    UnitID.ULTRALISK: 360.0,
    UnitID.ROACH: 999.8437,
    UnitID.INFESTOR: 999.8437,
    UnitID.CORRUPTOR: 999.8437,
    UnitID.BROODLORD: 720.0,
    UnitID.REDSTONELAVACRITTER: 494.4726,
    UnitID.REDSTONELAVACRITTERINJURED: 494.4726,
    UnitID.QUEEN: 999.8437,
    UnitID.INFESTORBURROWED: 999.8437,
    UnitID.OVERSEER: 999.8437,
    UnitID.ORBITALCOMMANDFLYING: 720.0,
    UnitID.SPINECRAWLERUPROOTED: float('inf'),
    UnitID.SPORECRAWLERUPROOTED: float('inf'),
    UnitID.ARCHON: 999.8437,
    UnitID.BROODLINGESCORT: 720.0,
    UnitID.GHOSTALTERNATE: 999.8437,
    UnitID.GHOSTNOVA: 999.8437,
    UnitID.URSADON: 494.4726,
    UnitID.LARVA: 720.0,
    UnitID.MULE: 999.8437,
    UnitID.BROODLING: 999.8437,
    UnitID.ADEPT: 999.8437,
    UnitID.LYOTE: 494.4726,
    UnitID.CARRIONBIRD: 494.4726,
    UnitID.KARAKMALE: 494.4726,
    UnitID.KARAKFEMALE: 494.4726,
    UnitID.URSADAKFEMALEEXOTIC: 494.4726,
    UnitID.URSADAKMALE: 494.4726,
    UnitID.URSADAKFEMALE: 494.4726,
    UnitID.URSADAKCALF: 494.4726,
    UnitID.URSADAKMALEEXOTIC: 494.4726,
    UnitID.UTILITYBOT: 494.4726,
    UnitID.COMMENTATORBOT1: 494.4726,
    UnitID.COMMENTATORBOT2: 494.4726,
    UnitID.COMMENTATORBOT3: 494.4726,
    UnitID.COMMENTATORBOT4: 494.4726,
    UnitID.SCANTIPEDE: 494.4726,
    UnitID.DOG: 360.0,
    UnitID.SHEEP: 494.4726,
    UnitID.COW: 249.961,
    UnitID.AUTOTESTATTACKTARGETGROUND: 494.4726,
    UnitID.AUTOTESTATTACKTARGETAIR: 720.0,
    UnitID.AUTOTESTATTACKER: 719.2968,
    UnitID.SCOPETEST: 999.8437,
    UnitID.HELLIONTANK: 720.0,
    UnitID.MOTHERSHIPCORE: float('inf'),
    UnitID.LOCUSTMP: 720.0,
    UnitID.SWARMHOSTMP: 360.0,
    UnitID.ORACLE: 999.8437,
    UnitID.TEMPEST: 720.0,
    UnitID.WARHOUND: 360.0,
    UnitID.WIDOWMINE: 720.0,
    UnitID.VIPER: 999.8437,
    UnitID.LURKERMP: 999.8437,
    UnitID.LURKERMPBURROWED: 999.8437,
    UnitID.THORNLIZARD: 494.4726,
    UnitID.CLEANINGBOT: 494.4726,
    UnitID.PROTOSSSNAKESEGMENTDEMO: 999.8437,
    UnitID.TESTZERG: 720.0,
    UnitID.ARTOSILOPE: 494.4726,
    UnitID.ANTEPLOTT: 494.4726,
    UnitID.LABBOT: 494.4726,
    UnitID.CRABEETLE: 494.4726,
    UnitID.RAVAGER: 999.8437,
    UnitID.LIBERATOR: 1499.9414,
    UnitID.THORAP: 360.0,
    UnitID.CYCLONE: 360.0,
    UnitID.LOCUSTMPFLYING: 720.0,
    UnitID.DISRUPTOR: float('inf'),
    UnitID.VOIDMPIMMORTALREVIVECORPSE: 720.0,
    UnitID.GUARDIANMP: 720.0,
    UnitID.DEVOURERMP: 539.4726,
    UnitID.DEFILERMP: 999.8437,
    UnitID.DISRUPTORPHASED: float('inf'),
    UnitID.ADEPTPHASESHIFT: 999.8437,
    UnitID.HERCPLACEMENT: 999.8437,
    UnitID.HERC: 999.8437,
    UnitID.MOOPY: 999.8437,
    UnitID.REPLICANT: float('inf'),
    UnitID.SEEKERMISSILE: 999.8437,
    UnitID.FLYOVERUNIT: 999.8437,
    UnitID.CORSAIRMP: 1499.9414,
    UnitID.SCOUTMP: 539.4726,
    UnitID.ARBITERMP: 539.4726,
    UnitID.SCOURGEMP: 1499.9414,
    UnitID.QUEENMP: 799.9804,
    UnitID.REPTILECRATE: 494.4726,
    UnitID.SLAYNSWARMHOSTSPAWNFLYER: 494.4726,
    UnitID.SLAYNELEMENTAL: 99.8437,
    UnitID.URSULA: 494.4726,
    UnitID.OVERLORDTRANSPORT: 999.8437,
    UnitID.BYPASSARMORDRONE: 720.0,
}
