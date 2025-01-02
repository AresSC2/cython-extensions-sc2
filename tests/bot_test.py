"""
Sanity test
Use this to test your environment is setup
And that some cython functions are working
"""

from random import choice

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2

from cython_extensions import (
    cy_angle_diff,
    cy_closest_to,
    cy_find_units_center_mass,
    cy_is_facing,
)
from cython_extensions.combat_utils import (
    cy_adjust_moving_formation,
    cy_find_aoe_position,
)


class BotTest(BotAI):
    def __init__(self):
        super().__init__()
        self.unit_fodder_values: dict[UnitTypeId, int] = {
            UnitTypeId.STALKER: 4,
            UnitTypeId.ZEALOT: 1,
            UnitTypeId.ADEPT: 2,
            UnitTypeId.PROBE: 3,
        }

    async def on_start(self):
        self.client.game_step = 2
        # uncomment to test AOE
        # await self.client.debug_create_unit([[UnitTypeId.RAVAGER, 5, self.start_location, 1]])
        # await self.client.debug_create_unit([[UnitTypeId.MARINE, 20, self.main_base_ramp.top_center, 2]])

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

    async def on_step(self, iteration: int):

        pass

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
            "GoldenAura513AIE",
            # "Tier1MicroAIArena_v4"
        ]
    )
    run_game(
        maps.get(random_map),
        [
            Bot(Race.Protoss, BotTest()),
            Computer(Race.Protoss, Difficulty.Medium),
        ],
        realtime=False,
    )
