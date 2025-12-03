"""
Sanity test
Use this to test your environment is setup
And that some cython functions are working
"""

from random import choice
import statistics

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2


import cProfile

from cython_extensions import (
    cy_angle_diff,
    cy_closest_to,
    cy_find_units_center_mass,
    cy_has_creep,
    cy_in_pathing_grid_burny,
    cy_is_facing,
    enable_safe_mode,
    cy_closer_than,
    cy_further_than,
    cy_structure_pending,
)
from cython_extensions.combat_utils import (
    cy_adjust_moving_formation,
    cy_find_aoe_position,
)
enable_safe_mode(False)


class BotTest(BotAI):
    def __init__(self):
        super().__init__()
        # enable_safe_mode(False)
        self.unit_fodder_values: dict[UnitTypeId, int] = {
            UnitTypeId.STALKER: 4,
            UnitTypeId.ZEALOT: 1,
            UnitTypeId.ADEPT: 2,
            UnitTypeId.PROBE: 3,
        }
        self.one_time_executed = False
        
        
        self.structures_to_track = [
            UnitTypeId.NEXUS,
            UnitTypeId.PYLON,
            UnitTypeId.GATEWAY,
            UnitTypeId.CYBERNETICSCORE,
            UnitTypeId.STARGATE,
            UnitTypeId.FLEETBEACON,
            UnitTypeId.TWILIGHTCOUNCIL,
            UnitTypeId.ROBOTICSFACILITY,
            UnitTypeId.ROBOTICSBAY,
            UnitTypeId.TEMPLARARCHIVE,
            UnitTypeId.DARKSHRINE,
            UnitTypeId.FORGE, 
            UnitTypeId.PHOTONCANNON,
            UnitTypeId.SHIELDBATTERY,
            UnitTypeId.ASSIMILATOR,
            
            
        ]

    async def on_start(self):
        self.client.game_step = 2
        # await self.client.debug_create_unit(
        #     [[UnitTypeId.MARINE, 2, self.start_location, 2]]
        # )
        # uncomment to test AOE
        # await self.client.debug_create_unit([[UnitTypeId.RAVAGER, 5, self.start_location, 1]])
        # await self.client.debug_create_unit([[UnitTypeId.MARINE, 20, self.main_base_ramp.top_center, 2]])
        await self.client.debug_all_resources()
        await self.client.debug_tech_tree()
        

    def detect_fodder_value(self, units) -> int:
        """
        Given a set of unit types, determine which units should be fodder.
        Returns the fodder value if it exists, otherwise -1
        @param unit_types:
        @param fodder_values:
        @return:
        """
        # establish how many fodder levels there are
        unit_type_fodder_values: set[int] = {
            self.unit_fodder_values[u.type_id]
            for u in units
            if u.type_id in self.unit_fodder_values
        }

        # if there's only one fodder level, no units are fodder
        if len(unit_type_fodder_values) > 1:
            return min(unit_type_fodder_values)
        else:
            return 0
        
    async def track_multiple_structures(bot, structures, interval=2.0):
        """
        Repeatedly track and print status of multiple structures using cy_structure_pending.
        """
        if bot.time % 7 ==0:
            print("==== STATUS UPDATE ====")
            for structure_type in structures:
                print(f"Tracking: {structure_type.name}")
                cy_structure_pending(bot, structure_type)
                print("----")


    async def on_step(self, iteration: int):
        
        if self.state.chat:
            for m in self.state.chat:
                msg_lower = m.message.lower()
                if msg_lower=="o":
                    await self.client.debug_fast_build()
                    print("Enabled/disabled fast build")
                    
        
        
        # pos = cy_find_aoe_position(3.0, [])
        # TEST AOE
        # for unit in self.units:
        #     if unit.type_id == UnitTypeId.RAVAGER:
        #         if self.enemy_units:
        #             abilities = await self.get_available_abilities(unit)
        #             if AbilityId.EFFECT_CORROSIVEBILE in abilities:
        #                 pos = cy_find_aoe_position(3.0, self.enemy_units)
        #                 if pos is not None:
        #                     unit(AbilityId.EFFECT_CORROSIVEBILE, Point2(pos))
        #                 else:
        #                     unit.attack(self.enemy_start_locations[0])
        #             else:
        #                 unit.attack(self.enemy_units.center)
        #         else:
        #             unit.attack(self.enemy_start_locations[0])

        # TEST FUNCTIONS
        # print(cy_is_facing(self.workers[0], self.workers[1]))
        # print(cy_angle_diff(300.0, 250.0))
        # print(cy_closest_to(self.start_location, self.workers))
        # pos = self.start_location.towards(self.game_info.map_center, 7.0)
        # print(cy_has_creep(self.state.creep.data_numpy, pos))
        # print(self.has_creep(pos))
        # print(cy_has_creep(self.state.creep.data_numpy, self.game_info.map_center))
        # print(self.has_creep(self.game_info.map_center))
        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # print(cy_in_pathing_grid_burny(self.game_info.pathing_grid.data_numpy.T, pos))
        # print(self.in_pathing_grid(pos))
        # print(
        #     cy_in_pathing_grid_burny(
        #         self.game_info.pathing_grid.data_numpy.T, self.start_location
        #     )
        # )
        # print(self.in_pathing_grid(self.start_location))
        # units=self.all_own_units
        # #units= [s for s in units]
        # base = self.townhalls[0]
        
        # units_A = [u for u in units]
        # position= (base.position.x, base.position.y)
        # #position = (base.position.x, base.position.y)
        # a=(len(cy_closer_than(units, 10.0, base.position)))
        # b=(len(cy_further_than(units_A, 10.0, position)))
        
        # #summe
                
        #self._abilities_count_and_build_progress
        # if self.one_time_executed==False:
        #     pr_cy = profile_func(cy_structure_pending, 100000, self, UnitTypeId.SUPPLYDEPOT)
        #     print("Profiling done 1")
        # pr_py = profile_func(self.already_pending, 100000, UnitTypeId.SUPPLYDEPOT)
        #     print("Profiling done 2")
        #     self.one_time_executed = True
        
        # ability = self.game_data.units[UnitTypeId.SUPPLYDEPOT.value].creation_ability.exact_id
        # # print(f"Ability for SUPPLYDEPOT: {ability}")
        # # print(F"self._abilities_count_and_build_progress: {self._abilities_count_and_build_progress[0][ability]}")
        
       # await self.track_multiple_structures(self, self.structures_to_track)


        # if iteration % 100 ==0:
        #     print("==== STATUS UPDATE ====")
        #     for x in self.structures_to_track:
        #         print(f"structure {x}: {cy_structure_pending(self, x)}")
        
        # string = "{
        #     4349231105: {
        #         'id': UnitTypeId.PYLON,
        #         'target': (145.0, 130.0),
        #         'time_order_commenced': 8.57,
        #         'building_purpose': <BuildingPurpose.NORMAL_BUILDING: 1>,
        #         'structure_order_complete': True
        #     }
        #     }"
        
        
        
        if iteration % 3 ==0:
            #print("--c ", cy_structure_pending(self, UnitTypeId.SUPPLYDEPOT))
            
            # for s in self.structures:
            #     if s.build_progress < 1.0:
            #         print(f"Building: {s.type_id} Progress: {s.build_progress}")
            
            
            # print(self._abilities_count_and_build_progress[0])
            print("OC: ", cy_structure_pending(self, UnitTypeId.ORBITALCOMMAND))
            print("PF: ", cy_structure_pending(self, UnitTypeId.PLANETARYFORTRESS))
            print("Hive: ", cy_structure_pending(self, UnitTypeId.HIVE))
            print("Lair: ", cy_structure_pending(self, UnitTypeId.LAIR))
            print("Barracks: ", cy_structure_pending(self, UnitTypeId.BARRACKSREACTOR))
            # worker = self.workers.first
            # print(worker.orders[0].ability.exact_id.value)
            
            # print(worker.orders[0].ability._proto.ability_id)
            
            # print(self.already_pending(UnitTypeId.ORBITALCOMMAND))
            # print(self.already_pending(UnitTypeId.PLANETARYFORTRESS))
            # print("barracks: ", cy_structure_pending(self, UnitTypeId.BARRACKS))
            # print("reactor barracks: ", cy_structure_pending(self, UnitTypeId.BARRACKSREACTOR))
            # print("techlab barracks: ", cy_structure_pending(self, UnitTypeId.BARRACKSTECHLAB))
            # print("barracks reactor ", cy_structure_pending(self, UnitTypeId.BARRACKSREACTOR))
            # print("barracks techlab ", cy_structure_pending(self, UnitTypeId.BARRACKSTECHLAB))
            # print("starport techlab ", cy_structure_pending(self, UnitTypeId.STARPORTTECHLAB))
            # print("starport reactor ", cy_structure_pending(self, UnitTypeId.STARPORTREACTOR))
            # print("factory techlab ", cy_structure_pending(self, UnitTypeId.FACTORYTECHLAB))
            
            #print(cy_structure_pending(self, UnitTypeId.STARPORTTECHLAB))
        
        
        #print(f"Pending Spawning Pools: {pending_spawning_pools}")
        #print(self.race.name=="Terran", self.race.name)
        
        # print(self.game_data.abilities[])
        #self._proto #TODO investigate maybe get access filtered data out of bot object instead of all orders
        
        # wo= [w for w in self.workers if not w.is_collecting]
        # print(f"Idle workers: {len(wo)}")
        # for w in self.workers:
        #     for x in range(len(w.orders)):
        #         print("----------------")
        #         order = w.orders[x]
        #         print(f"Order: {order.ability}")
        #         print("----------------")
            #print(f"Orders len {len(w.orders)}")
            #print(w.orders)
        
        
        

        
        # time_taken = timeit.timeit(
        #     stmt=lambda: cy_closer_than(self.units, self.townhalls[0].position, 10.0),
        #     number=10000,
        # )
        #print(f"Time taken for cy_closer_than: {time_taken} seconds")
        
        # print(len(cy_closer_than(self.units, 1, 15.0)))
        # TEST UNIT FORMATION (play on micro arena)
        # if not self.enemy_units:
        #     return
        # fodder_value: int = self.detect_fodder_value(self.units)
        # # if there's only one fodder level, no units are fodder
        # fodder_tags = []
        # units_that_need_to_move = dict()
        # if fodder_value > 0:
        #     for unit in self.units:
        #         if (
        #             unit.type_id in self.unit_fodder_values
        #             and self.unit_fodder_values[unit.type_id] == fodder_value
        #         ):
        #             fodder_tags.append(unit.tag)
        #
        #     units_that_need_to_move = cy_adjust_moving_formation(
        #         self.units,
        #         cy_find_units_center_mass(self.enemy_units, 5.0)[0],
        #         fodder_tags,
        #         1.0,
        #         0.25,
        #     )
        #
        # for unit in self.units:
        #     unit.position_tuple
        #     if (
        #         unit.tag in units_that_need_to_move
        #         and unit.distance_to(self.enemy_units.center) > 9.0
        #     ):
        #         unit.move(Point2(units_that_need_to_move[unit.tag]))
        #     else:
        #         unit.attack(self.enemy_units.center)


if __name__ == "__main__":
    random_map = choice(
        [
            #"InterloperAIE",
            # "Tier1MicroAIArena_v4",
            "TorchesAIE"
            
        ]
    )
    run_game(
        maps.get(random_map),
        [
            Bot(Race.Terran, BotTest()),
            Computer(Race.Protoss, Difficulty.Medium),
        ],
        realtime=True,
    )
