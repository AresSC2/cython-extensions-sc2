"""Live-game round trip: drive a real SC2 game, then prove every field of the
``Observation`` matches the live unit attributes it claims to encode.

Unlike the pickle-based tests (frozen start-of-game states), this spawns
armies for both players, wounds units, stims marines, orders moves/builds,
lands a ravager bile, and checks the encoder output tag-by-tag against values
read independently from the same game step. No timing assumptions: every
expectation is recomputed from live state with plain ``math``.

Requires a StarCraft II install plus the ``TorchesAIE`` map; skipped
otherwise (the probe below only checks for the install, it never launches
a game, so the default suite stays fast).
"""

import math

import numpy as np
import pytest
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.protocol import ProtocolError

from cython_extensions.features import (
    ABILITY_DICT,
    BUFF_DICT,
    ENTITY_CAT_DIM,
    ENTITY_NUM_DIM,
    MAX_ENTITIES,
    SCALAR_DIM,
    SCALAR_FEATURE_NAMES,
    SPATIAL_CHANNEL_NAMES,
    UNIT_TYPE_DICT,
    Features,
)

_LIVE_MAP = "TorchesAIE_v4"
_MAX_ITERS = 250


def _sc2_available() -> bool:
    """True when a game could actually launch (install + map present)."""
    try:
        maps.get(_LIVE_MAP)
        return True
    except BaseException:  # maps.get raises SystemExit without an install
        return False


requires_sc2 = pytest.mark.skipif(
    not _sc2_available(), reason="StarCraft II install + map required"
)


def _clip01(v: float) -> float:
    return min(max(float(v), 0.0), 1.0)


def _ratio(num: float, den: float) -> float:
    return _clip01(num / den) if den > 1e-6 else 0.0


def _log_norm(value: float, scale: float) -> float:
    return _clip01(math.log1p(max(value, 0.0)) / math.log1p(scale))


class _AuditBot(BotAI):
    """Sets up a deterministic skirmish, audits the encoder, leaves."""

    def __init__(self) -> None:
        super().__init__()
        self.failures: list[str] = []
        self.audited = False
        self._setup_done = False
        self._stim_tag: int | None = None
        self._mover_tag: int | None = None
        self._move_target = None
        self._bile_at = None

    def check(self, cond: bool, msg: str) -> None:
        if not cond:
            self.failures.append(msg)

    async def on_start(self) -> None:
        self.client.game_step = 2
        await self.client.debug_show_map()
        await self.client.debug_all_resources()
        await self.client.debug_tech_tree()  # lift tech requirements ...
        await self.client.debug_upgrade()  # ... then research stimpack etc.
        await self.client.debug_cooldown()  # free recasts (bile retries)
        sl = self.start_location
        await self.client.debug_create_unit(
            [
                [UnitTypeId.MARINE, 3, sl, 1],
                [UnitTypeId.MARAUDER, 1, sl, 1],
                [UnitTypeId.HIGHTEMPLAR, 1, sl, 1],
                [UnitTypeId.RAVAGER, 1, sl, 1],
                [UnitTypeId.SCV, 2, sl, 1],
            ]
        )
        await self.client.debug_create_unit(
            [
                [UnitTypeId.ZEALOT, 2, self.enemy_start_locations[0], 2],
                [UnitTypeId.STALKER, 1, self.enemy_start_locations[0], 2],
            ]
        )

    async def _setup(self) -> None:
        """One-off orders once spawned units are visible."""
        marines = self.units(UnitTypeId.MARINE)
        hts = self.units(UnitTypeId.HIGHTEMPLAR)
        ravagers = self.units(UnitTypeId.RAVAGER)
        scvs = self.workers
        if not (len(marines) >= 3 and hts and ravagers and scvs):
            return
        # Deterministic attribute control (no combat timing involved).
        await self.client.debug_set_unit_value([marines[0].tag], 2, 20.0)  # Life
        await self.client.debug_set_unit_value([hts[0].tag], 1, 150.0)  # Energy
        marines[1](AbilityId.EFFECT_STIM_MARINE)  # self-buff, ~11 s duration
        self._stim_tag = marines[1].tag
        # Point order for order-target checks.
        self._move_target = self.game_info.map_center.towards(self.start_location, 10)
        marines[2].move(self._move_target)
        self._mover_tag = marines[2].tag
        # Construction in progress for build_progress coverage.
        depot_at = await self.find_placement(
            UnitTypeId.SUPPLYDEPOT, near=self.start_location, max_distance=20
        )
        if depot_at is not None:
            scvs[0].build(UnitTypeId.SUPPLYDEPOT, depot_at)
        # Bile goes on empty ground: a real persistent effect without
        # endangering our own audit subjects. Ordered repeatedly below
        # because the spawn point can be out of bile range.
        self._bile_at = self.start_location.towards(self.game_info.map_center, 10)
        self._setup_done = True

    async def _upkeep(self) -> None:
        """Keep scripted conditions true until the audit runs."""
        ravagers = self.units(UnitTypeId.RAVAGER)
        if ravagers and not self.state.effects:
            ravagers[0].move(self._bile_at)
            if ravagers[0].distance_to(self._bile_at) < 7:
                ravagers[0](AbilityId.EFFECT_CORROSIVEBILE, self._bile_at)
        if self._stim_tag is not None:
            stimmer = self.units.find_by_tag(self._stim_tag)
            if stimmer is not None and stimmer.health > 25:
                try:
                    remain = float(stimmer._proto.buff_duration_remain)
                except Exception:
                    remain = 0.0
                if not stimmer.buffs or remain < 30:  # refresh an expiring stim
                    stimmer(AbilityId.EFFECT_STIM_MARINE)

    async def on_step(self, iteration: int) -> None:
        if not self._setup_done:
            await self._setup()
            return
        await self._upkeep()
        bile_seen = len(self.state.effects) > 0
        if (bile_seen and iteration > 15) or iteration >= _MAX_ITERS:
            self._audit()
            self.audited = True
            await self.client.leave()

    # ------------------------------------------------------------------
    # Audit: every expectation recomputed from live state, independently
    # of the encoder (plain math, documented scales).
    # ------------------------------------------------------------------
    def _audit(self) -> None:
        obs = Features(self).build_observation()
        w = float(self.game_info.map_size[0])
        h = float(self.game_info.map_size[1])
        dx = w - 1.0 if w > 1.0 else 1.0
        dy = h - 1.0 if h > 1.0 else 1.0

        ent = np.asarray(obs.entity_features[0])
        cats = np.asarray(obs.entity_categorical[0])
        mask = np.asarray(obs.entity_mask[0])
        pos = np.asarray(obs.entity_positions[0])
        n = int(mask.sum())
        self.check(
            n == len(self.all_units), f"mask count {n} != units {len(self.all_units)}"
        )
        self.check(
            set(obs.unit_tags) == {u.tag for u in self.all_units}, "tag set mismatch"
        )
        by_tag = {tag: i for i, tag in enumerate(obs.unit_tags)}

        for u in self.all_units:
            row = by_tag.get(u.tag)
            self.check(row is not None, f"missing row for tag {u.tag} ({u.name})")
            if row is None:
                continue
            p = u._proto
            f = ent[row]
            c = cats[row]
            self.check(abs(f[0] - p.pos.x / dx) < 1e-4, f"{u.name} x")
            self.check(abs(f[1] - p.pos.y / dy) < 1e-4, f"{u.name} y")
            self.check(
                abs(f[2] - (float(p.facing) % (2 * math.pi)) / (2 * math.pi)) < 1e-4,
                f"{u.name} facing",
            )
            self.check(
                abs(f[3] - _ratio(p.health, p.health_max)) < 1e-4, f"{u.name} hp"
            )
            self.check(
                abs(f[4] - _ratio(p.shield, p.shield_max)) < 1e-4, f"{u.name} shield"
            )
            self.check(
                abs(f[5] - _ratio(p.energy, p.energy_max)) < 1e-4, f"{u.name} energy"
            )
            self.check(abs(f[6] - _log_norm(p.radius, 4.0)) < 1e-4, f"{u.name} radius")
            self.check(
                abs(f[7] - _clip01(p.cargo_space_taken / 8.0)) < 1e-4,
                f"{u.name} cargo taken",
            )
            self.check(
                abs(f[8] - _clip01(p.cargo_space_max / 8.0)) < 1e-4,
                f"{u.name} cargo max",
            )
            self.check(
                abs(f[9] - _clip01(p.build_progress)) < 1e-4, f"{u.name} build progress"
            )
            self.check(
                abs(f[10] - _clip01(p.weapon_cooldown / 50.0)) < 1e-4,
                f"{u.name} weapon cd",
            )
            try:
                speed = float(u.movement_speed)
            except Exception:
                speed = 0.0
            self.check(abs(f[11] - _log_norm(speed, 8.0)) < 1e-4, f"{u.name} speed")
            self.check(
                abs(f[12] - _log_norm(p.mineral_contents, 2500.0)) < 1e-4,
                f"{u.name} minerals",
            )
            self.check(
                abs(f[13] - _log_norm(p.vespene_contents, 2500.0)) < 1e-4,
                f"{u.name} vespene",
            )
            self.check(
                abs(f[14] - _ratio(p.assigned_harvesters, p.ideal_harvesters)) < 1e-4,
                f"{u.name} harvesters",
            )
            self.check(
                abs(f[19] - (1.0 if int(p.engaged_target_tag) != 0 else 0.0)) < 1e-4,
                f"{u.name} engaged",
            )
            self.check(
                c[0] == UNIT_TYPE_DICT.get(int(p.unit_type), 0), f"{u.name} type"
            )
            self.check(c[1] == int(u.alliance) - 1, f"{u.name} alliance")
            for col, attr in ((2, "display_type"), (3, "cloak")):
                self.check(c[col] == int(getattr(p, attr)), f"{u.name} {attr}")
            for col, attr in (
                (8, "is_flying"),
                (9, "is_burrowed"),
                (10, "is_hallucination"),
                (11, "is_active"),
                (12, "is_powered"),
                (13, "is_selected"),
            ):
                self.check(c[col] == (1 if getattr(p, attr) else 0), f"{u.name} {attr}")
            for col, attr in (
                (14, "attack_upgrade_level"),
                (15, "armor_upgrade_level"),
                (16, "shield_upgrade_level"),
            ):
                self.check(c[col] == int(getattr(p, attr)), f"{u.name} {attr}")
            # Buffs: first two ids; the raw API exposes a single
            # buff_duration_remain scalar in game loops, so only slot 0
            # has a duration (scaled by 60 loops, as in the encoder).
            live_buffs = [int(b) for b in p.buff_ids]
            try:
                live_rem0 = float(p.buff_duration_remain)
            except Exception:
                live_rem0 = 0.0
            for slot, col, dcol in ((0, 6, 15), (1, 7, 16)):
                exp_id = (
                    BUFF_DICT.get(live_buffs[slot], 0) if slot < len(live_buffs) else 0
                )
                exp_dur = _clip01(live_rem0 / 60.0) if slot == 0 and live_buffs else 0.0
                self.check(c[col] == exp_id, f"{u.name} buff{slot}")
                self.check(
                    abs(f[dcol] - exp_dur) < 2e-2, f"{u.name} buff{slot} duration"
                )
            # Position mirror used by the model-side scatter.
            self.check(
                abs(pos[row, 0] - f[0]) < 1e-6 and abs(pos[row, 1] - f[1]) < 1e-6,
                f"{u.name} positions mirror",
            )

        # Scripted scenarios with exact expectations.
        wounded = next(
            (u for u in self.units if u.tag in by_tag and u.health < u.health_max), None
        )
        self.check(wounded is not None, "expected a wounded marine (debug life set)")
        if self._stim_tag in by_tag:
            srow = by_tag[self._stim_tag]
            stimmer = self.units.find_by_tag(self._stim_tag)
            live_ids = [int(b) for b in stimmer._proto.buff_ids] if stimmer else []
            try:
                live_rem = (
                    float(stimmer._proto.buff_duration_remain) if stimmer else 0.0
                )
            except Exception:
                live_rem = 0.0
            self.check(int(cats[srow, 6]) != 0, f"stim buff recorded (live={live_ids})")
            # The game does not always report a duration (live stim shows
            # remain == 0 while active); encoder==API is already asserted
            # exactly per unit above, so only demand flow-through when the
            # game actually provides a value.
            if live_rem > 0:
                self.check(
                    float(ent[srow, 15]) > 0.0,
                    f"stim duration recorded (remain={live_rem})",
                )
        if self._mover_tag in by_tag:
            mrow = by_tag[self._mover_tag]
            self.check(int(cats[mrow, 4]) != 0, "move order ability recorded")
            self.check(
                abs(float(ent[mrow, 17]) - self._move_target.x / dx) < 2e-2,
                "move order target x",
            )
            self.check(
                abs(float(ent[mrow, 18]) - self._move_target.y / dy) < 2e-2,
                "move order target y",
            )

        # Spatial: independently regroup live units per target cell.
        chans = dict(zip(SPATIAL_CHANNEL_NAMES, np.asarray(obs.spatial[0])))
        tw = th = 128
        for u in self.all_units:
            gx = min(max(int(u.position.x / dx * tw), 0), tw - 1)
            gy = min(max(int(u.position.y / dy * th), 0), th - 1)
            ally = int(u.alliance) - 1
            rel = ["rel_self", "rel_ally", "rel_neutral", "rel_enemy"][ally]
            if chans["playable"][gy, gx] > 0.5:
                self.check(chans[rel][gy, gx] == 1.0, f"{u.name} presence on {rel}")
        own = [u for u in self.all_units if int(u.alliance) in (1, 2)]
        if own:
            cell_mass: dict[tuple[int, int], float] = {}
            for u in own:
                key = (
                    min(max(int(u.position.x / dx * tw), 0), tw - 1),
                    min(max(int(u.position.y / dy * th), 0), th - 1),
                )
                cell_mass[key] = cell_mass.get(key, 0.0) + u.health + u.shield
            (kx, ky), mass = max(cell_mass.items(), key=lambda kv: kv[1])
            if chans["playable"][ky, kx] > 0.5 and mass > 0:
                self.check(
                    abs(chans["hp_self"][ky, kx] - _log_norm(mass, 4000.0)) < 1e-4,
                    "hp_self mass recompute",
                )
        # Effects landed (bile was ordered onto empty ground).
        self.check(len(self.state.effects) > 0, "bile effect visible in state")
        self.check(chans["effects"].max() > 0.0, "effects plane marks bile")

        # Scalar spot checks recomputed from live state.
        scalar = dict(zip(SCALAR_FEATURE_NAMES, np.asarray(obs.scalar[0]).tolist()))
        self.check(
            abs(scalar["minerals"] - _log_norm(self.minerals, 20000.0)) < 1e-6,
            "scalar minerals",
        )
        self.check(
            abs(scalar["supply_used"] - min(self.supply_used / 200.0, 1.0)) < 1e-6,
            "scalar supply",
        )
        self.check(
            abs(scalar["game_loop"] - min(self.state.game_loop / 45000.0, 1.0)) < 1e-6,
            "scalar game_loop",
        )
        self.check(
            abs(
                scalar["effect_count"]
                - _clip01(math.log1p(len(self.state.effects)) / math.log1p(8))
            )
            < 1e-6,
            "scalar effect_count",
        )
        self.check(ent.shape == (MAX_ENTITIES, ENTITY_NUM_DIM), "entity width")
        self.check(cats.shape == (MAX_ENTITIES, ENTITY_CAT_DIM), "categorical width")
        self.check(len(scalar) == SCALAR_DIM, "scalar width")


def _run_audit_game() -> _AuditBot:
    bot = _AuditBot()
    try:
        run_game(
            maps.get(_LIVE_MAP),
            [Bot(Race.Terran, bot), Computer(Race.Zerg, Difficulty.Easy)],
            realtime=False,
        )
    except ProtocolError:
        pass  # raised by client.leave() after a successful audit
    return bot


@requires_sc2
def test_live_observation_matches_game_state():
    bot = _run_audit_game()
    assert bot.audited, "audit never ran (setup units missing or game ended early)"
    assert bot.failures == [], "observation mismatches:\n- " + "\n- ".join(bot.failures)


if __name__ == "__main__":
    _bot = _run_audit_game()
    assert _bot.audited, "audit never ran (setup units missing or game ended early)"
    assert _bot.failures == [], "observation mismatches:\n- " + "\n- ".join(
        _bot.failures
    )
