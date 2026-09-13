import contextlib
from pathlib import Path

import numpy as np
import pytest
from sc2.bot_ai import BotAI
from sc2.data import Alliance
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2
from sc2.units import Units


@contextlib.contextmanager
def _proto_values(unit, **values):
    """Temporarily set proto fields, restoring afterwards.

    The ``bot`` fixture is class-scoped and shared, so every synthetic
    mutation must be unwound in a ``finally``.
    """
    proto = unit._proto
    old = {k: getattr(proto, k) for k in values}
    try:
        for k, v in values.items():
            setattr(proto, k, v)
        yield proto
    finally:
        for k, v in old.items():
            setattr(proto, k, v)


class _FakeEffect:
    """Minimal stand-in for sc2.game_state.EffectData."""

    def __init__(self, positions, radius, alliance):
        self.positions = set(positions)
        self.radius = radius
        self.alliance = alliance

    @property
    def is_enemy(self):
        return self.alliance == Alliance.Enemy

from cython_extensions.features import (
    ABILITY_DICT,
    BUFF_DICT,
    ENTITY_CAT_DIM,
    ENTITY_NUM_DIM,
    MAX_ENTITIES,
    NUM_ABILITIES,
    NUM_BUFFS,
    NUM_UNIT_TYPES,
    SCALAR_DIM,
    SCALAR_FEATURE_NAMES,
    SPATIAL_CHANNEL_NAMES,
    TARGET_SPATIAL_SIZE,
    UNIT_TYPE_DICT,
    Features,
)

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "pickle_data").iterdir()
    if map_path.suffix == ".xz"
]

assert MAPS, "expected pickle maps under tests/pickle_data"


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestFeatures:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_observation_shapes_and_dtypes(self, bot: BotAI, event_loop):
        obs = Features(bot).build_observation()
        h, w = TARGET_SPATIAL_SIZE
        assert obs.entity_features.shape == (1, MAX_ENTITIES, ENTITY_NUM_DIM)
        assert obs.entity_categorical.shape == (1, MAX_ENTITIES, ENTITY_CAT_DIM)
        assert obs.entity_mask.shape == (1, MAX_ENTITIES)
        assert obs.entity_positions.shape == (1, MAX_ENTITIES, 2)
        assert obs.spatial.shape == (1, len(SPATIAL_CHANNEL_NAMES), h, w)
        assert obs.scalar.shape == (1, SCALAR_DIM)
        assert obs.entity_features.dtype == np.float32
        assert obs.entity_categorical.dtype == np.int64
        assert obs.entity_mask.dtype == np.float32
        assert obs.spatial.dtype == np.float32
        assert obs.scalar.dtype == np.float32
        assert len(SCALAR_FEATURE_NAMES) == SCALAR_DIM == obs.scalar.shape[1]

    def test_mask_tags_positions_consistent(self, bot: BotAI, event_loop):
        obs = Features(bot).build_observation()
        mask = obs.entity_mask[0]
        n = int(mask.sum())
        assert n == len(bot.all_units)
        assert len(obs.unit_tags) == n
        assert set(mask.tolist()) <= {0.0, 1.0}
        # padded rows are exact zeros
        assert (obs.entity_features[0, n:] == 0.0).all()
        assert (obs.entity_categorical[0, n:] == 0).all()
        assert (obs.entity_positions[0, n:] == 0.0).all()
        # tags line up with real rows
        assert len(set(obs.unit_tags)) == n  # tags unique per game

    def test_numeric_ranges(self, bot: BotAI, event_loop):
        obs = Features(bot).build_observation()
        n = int(obs.entity_mask[0].sum())
        num = obs.entity_features[0, :n]
        assert np.isfinite(num).all()
        assert num.min() >= 0.0 and num.max() <= 1.0
        assert np.isfinite(obs.spatial).all()
        assert obs.spatial.min() >= 0.0 and obs.spatial.max() <= 1.0
        assert np.isfinite(obs.scalar).all()
        assert obs.scalar.min() >= 0.0 and obs.scalar.max() <= 1.0
        cats = obs.entity_categorical[0, :n]
        assert (cats[:, 0] < NUM_UNIT_TYPES).all()
        assert set(np.unique(cats[:, 1]).tolist()) <= {0, 1, 2, 3}
        assert (cats[:, 4] < NUM_ABILITIES).all()
        assert (cats[:, 6] < NUM_BUFFS).all() and (cats[:, 7] < NUM_BUFFS).all()

    def test_deterministic_under_input_permutation(self, bot: BotAI, event_loop):
        feats = Features(bot)
        units = bot.all_units
        reversed_units = Units(list(reversed(list(units))), bot)
        a = feats._encode_entities(units, MAX_ENTITIES, True)
        b = feats._encode_entities(reversed_units, MAX_ENTITIES, True)
        for x, y in zip(a[:4], b[:4]):  # feats, cats, pos, mask
            np.testing.assert_array_equal(np.asarray(x), np.asarray(y))
        assert a[4] == b[4]

    def test_known_values_spot_check(self, bot: BotAI, event_loop):
        feats = Features(bot)
        ent, cats, pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        by_tag = {tag: i for i, tag in enumerate(tags)}
        # townhall at full hp -> hp ratio 1.0, harvester slots present
        townhall = bot.townhalls[0]
        row = by_tag[int(townhall.tag)]
        assert ent[row, 4] == pytest.approx(1.0)  # EN_HP
        assert cats[row, 1] == 0  # own alliance
        assert cats[row, 0] > 0  # known unit type
        # collecting worker exposes its gather order ability
        worker = bot.workers[0]
        wrow = by_tag[int(worker.tag)]
        assert cats[wrow, 4] == ABILITY_DICT[AbilityId.HARVEST_GATHER.value]
        # mineral field carries raw mineral contents
        mineral = next(
            u for u in bot.all_units if u._proto.mineral_contents > 0
        )
        mrow = by_tag[int(mineral.tag)]
        assert cats[mrow, 1] == 2
        assert ent[mrow, 13] > 0.0  # EN_MINERALS

    def test_scalar_spot_check(self, bot: BotAI, event_loop):
        feats = Features(bot)
        scalar = feats._encode_scalar()
        by_name = dict(zip(SCALAR_FEATURE_NAMES, scalar.tolist()))
        assert by_name["minerals"] == pytest.approx(
            float(np.log1p(bot.minerals) / np.log1p(20000.0))
        )
        assert by_name["supply_used"] == pytest.approx(bot.supply_used / 200.0)
        # race one-hots are exclusive
        assert sum(by_name[f"race_self_{r}"] for r in ("terran", "zerg", "protoss", "random")) == 1.0
        assert sum(by_name[f"race_enemy_{r}"] for r in ("terran", "zerg", "protoss", "random")) == 1.0
        # start-state pickles: terran player vs zerg enemy
        assert by_name["race_self_terran"] == 1.0
        assert by_name["race_enemy_zerg"] == 1.0

    def test_spatial_playable_and_presence(self, bot: BotAI, event_loop):
        feats = Features(bot)
        _ent, _cats, pos, mask, _tags, aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        spatial, _n_effects = feats._encode_spatial(
            entity_positions=pos, entity_mask=mask, entity_aux=aux
        )
        playable = spatial[3]
        assert playable.max() == 1.0
        outside = playable < 0.5
        assert (spatial[:, outside] == 0.0).all()
        rel = dict(zip(SPATIAL_CHANNEL_NAMES, spatial))
        assert rel["rel_self"].max() == 1.0  # own units exist
        assert rel["rel_neutral"].max() == 1.0  # minerals exist
        assert rel["density_self"].max() > 0.0

    def test_spatial_target_size_override(self, bot: BotAI, event_loop):
        obs = Features(bot).build_observation(target_spatial_size=(64, 64))
        assert obs.spatial.shape == (1, len(SPATIAL_CHANNEL_NAMES), 64, 64)
        assert np.isfinite(obs.spatial).all()

    def test_no_effects_by_default(self, bot: BotAI, event_loop):
        # Start-state pickles contain no persistent effects.
        feats = Features(bot)
        _ent, _cats, pos, mask, _tags, aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        spatial, n_effects = feats._encode_spatial(
            entity_positions=pos, entity_mask=mask, entity_aux=aux
        )
        chans = dict(zip(SPATIAL_CHANNEL_NAMES, spatial))
        assert n_effects == 0
        assert chans["effects"].max() == 0.0
        scalar = feats._encode_scalar()
        by_name = dict(zip(SCALAR_FEATURE_NAMES, scalar.tolist()))
        assert by_name["effect_count"] == 0.0

    def test_effects_plane_and_scalar(self, bot: BotAI, event_loop):
        feats = Features(bot)
        old_effects = bot.state.effects
        # Drop a hostile storm on the townhall and a friendly shield on a
        # worker; both sit on playable ground. Effects endanger both sides,
        # so both land on the single danger plane.
        storm_xy = bot.townhalls[0].position
        shield_xy = bot.workers[0].position
        bot.state.effects = {
            _FakeEffect(
                [Point2((storm_xy.x, storm_xy.y))],
                1.5,
                Alliance.Enemy,
            ),
            _FakeEffect(
                [Point2((shield_xy.x, shield_xy.y))],
                2.0,
                Alliance.Self,
            ),
        }
        try:
            obs = feats.build_observation()
        finally:
            bot.state.effects = old_effects
        chan = dict(zip(SPATIAL_CHANNEL_NAMES, np.asarray(obs.spatial[0])))["effects"]
        assert chan.max() > 0.0
        # Both effect centres are marked.
        w, h = float(feats.map_width), float(feats.map_height)
        for xy in (storm_xy, shield_xy):
            gx = min(int(xy.x * 128 / w), 127)
            gy = min(int(xy.y * 128 / h), 127)
            assert chan[gy, gx] > 0.0
        by_name = dict(zip(SCALAR_FEATURE_NAMES, np.asarray(obs.scalar[0]).tolist()))
        assert by_name["effect_count"] == pytest.approx(
            float(np.log1p(2) / np.log1p(8))
        )

    def test_buff_id_and_scalar_duration(self, bot: BotAI, event_loop):
        # The raw API exposes buff_duration_remain as a single scalar (not a
        # list): slot 0 carries it, slot 1 stays 0. Inject into a live proto
        # and restore afterwards (bot fixture is class-scoped).
        from sc2.ids.buff_id import BuffId

        feats = Features(bot)
        unit = bot.workers[0]
        proto = unit._proto
        old_ids = list(proto.buff_ids)
        old_remain = int(proto.buff_duration_remain)  # int32 field: keep int
        proto.buff_ids.append(BuffId.STIMPACK.value)
        proto.buff_duration_remain = 30  # int32 game loops, not seconds
        try:
            ent, cats, _pos, mask, tags, _aux = feats._encode_entities(
                bot.all_units, MAX_ENTITIES, True
            )
        finally:
            del proto.buff_ids[:]
            proto.buff_ids.extend(old_ids)
            proto.buff_duration_remain = old_remain
        row = tags.index(int(unit.tag))
        assert mask[row] == 1.0
        assert cats[row, 6] == BUFF_DICT[BuffId.STIMPACK.value]  # EC_BUFF0
        assert cats[row, 7] == 0  # EC_BUFF1 empty
        assert ent[row, 16] == pytest.approx(30 / 60.0)  # EN_BUFF_DUR0
        assert ent[row, 17] == 0.0  # EN_BUFF_DUR1 has no duration source

    # -- synthetic branch coverage: start-state pickles never contain these --
    # Each test mutates live protos / state and restores them afterwards.

    def test_enemy_alliance_paths(self, bot: BotAI, event_loop):
        feats = Features(bot)
        foes = [bot.workers[0], bot.workers[1], bot.townhalls[0]]
        ally = bot.workers[2]
        saved = [(u._proto, int(u._proto.alliance)) for u in foes + [ally]]
        try:
            for u in foes:
                u._proto.alliance = 4
            ally._proto.alliance = 2
            obs = feats.build_observation()
        finally:
            for proto, v in saved:
                proto.alliance = v
        n = int(obs.entity_mask[0].sum())
        cats = obs.entity_categorical[0, :n]
        assert set(cats[:, 1].tolist()) == {0, 1, 2, 3}
        chans = dict(zip(SPATIAL_CHANNEL_NAMES, np.asarray(obs.spatial[0])))
        assert chans["rel_enemy"].max() == 1.0
        assert chans["rel_ally"].max() == 1.0
        assert chans["density_enemy"].max() > 0.0
        assert chans["hp_enemy"].max() > 0.0
        w, h = float(feats.map_width), float(feats.map_height)
        by_tag = {t: i for i, t in enumerate(obs.unit_tags)}
        for u in foes:
            assert cats[by_tag[int(u.tag)], 1] == 3
            gx = min(max(int(u.position.x / (w - 1) * 128), 0), 127)
            gy = min(max(int(u.position.y / (h - 1) * 128), 0), 127)
            assert chans["rel_enemy"][gy, gx] == 1.0

    def test_status_flag_paths(self, bot: BotAI, event_loop):
        feats = Features(bot)
        u = bot.workers[0]
        with _proto_values(
            u,
            is_flying=True,
            is_burrowed=True,
            is_hallucination=True,
            is_selected=True,
            is_powered=True,
            weapon_cooldown=25.0,
            cargo_space_taken=2,
            cargo_space_max=8,
            attack_upgrade_level=2,
            armor_upgrade_level=1,
            shield_upgrade_level=3,
            engaged_target_tag=12345,
            cloak=2,
        ):
            ent, cats, pos, mask, tags, aux = feats._encode_entities(
                bot.all_units, MAX_ENTITIES, True
            )
            spatial, _ = feats._encode_spatial(
                entity_positions=pos, entity_mask=mask, entity_aux=aux
            )
        row = tags.index(int(u.tag))
        assert cats[row, 8] == 1  # flying
        assert cats[row, 9] == 1  # burrowed
        assert cats[row, 10] == 1  # hallucination
        assert cats[row, 12] == 1  # powered
        assert cats[row, 13] == 1  # selected
        assert cats[row, 3] == 2  # cloak
        assert ent[row, 11] == pytest.approx(0.5)  # weapon cd 25/50
        assert ent[row, 8] == pytest.approx(0.25)  # cargo taken 2/8
        assert ent[row, 9] == pytest.approx(1.0)  # cargo max 8/8
        assert (cats[row, 14], cats[row, 15], cats[row, 16]) == (2, 1, 3)
        assert ent[row, 20] == 1.0  # engaged
        sel = dict(zip(SPATIAL_CHANNEL_NAMES, spatial))["selected"]
        w, h = float(feats.map_width), float(feats.map_height)
        gx = min(max(int(u.position.x / (w - 1) * 128), 0), 127)
        gy = min(max(int(u.position.y / (h - 1) * 128), 0), 127)
        assert sel[gy, gx] > 0.0

    def test_scalar_upgrades_alerts(self, bot: BotAI, event_loop):
        import math

        from sc2.data import Alert
        from sc2.ids.upgrade_id import UpgradeId

        feats = Features(bot)
        up_a, up_b = (
            UpgradeId.TERRANINFANTRYWEAPONSLEVEL1,
            UpgradeId.TERRANINFANTRYARMORSLEVEL1,
        )
        old_up, old_al = bot.state.upgrades, bot.state.alerts
        bot.state.upgrades = {up_a, up_b}
        bot.state.alerts = [Alert.BuildingComplete, Alert.BuildingUnderAttack]
        try:
            scalar = feats._encode_scalar()
        finally:
            bot.state.upgrades, bot.state.alerts = old_up, old_al
        by_name = dict(zip(SCALAR_FEATURE_NAMES, scalar.tolist()))
        assert by_name["upgrades_count"] == pytest.approx(
            math.log1p(2) / math.log1p(64)
        )
        buckets = [up_a.value % 8, up_b.value % 8]
        assert buckets[0] != buckets[1]
        for b in range(8):
            exp = math.log1p(1) / math.log1p(16) if b in buckets else 0.0
            assert by_name[f"upgrade_hash_{b}"] == pytest.approx(exp)
        assert by_name["alerts_count"] == pytest.approx(
            math.log1p(2) / math.log1p(8)
        )
        assert by_name["alert_severity"] == pytest.approx(
            min(max(a.value for a in (Alert.BuildingComplete, Alert.BuildingUnderAttack)) / 25.0, 1.0)
        )

    def test_power_plane(self, bot: BotAI, event_loop):
        feats = Features(bot)
        pm = bot.state.psionic_matrix
        old = pm.sources
        hall = bot.townhalls[0]
        from sc2.power_source import PowerSource

        pm.sources = [PowerSource(hall.position, 7.0, hall.tag)]
        try:
            obs = feats.build_observation()
        finally:
            pm.sources = old
        plane = dict(zip(SPATIAL_CHANNEL_NAMES, np.asarray(obs.spatial[0])))["power"]
        w, h = float(feats.map_width), float(feats.map_height)
        gx = min(max(int(hall.position.x * 128 / w), 0), 127)
        gy = min(max(int(hall.position.y * 128 / h), 0), 127)
        assert plane[gy, gx] == 1.0
        assert plane.max() == 1.0

    def test_truncation_deterministic(self, bot: BotAI, event_loop):
        feats = Features(bot)
        rep = MAX_ENTITIES // len(bot.all_units) + 2
        big = Units(list(bot.all_units) * rep, bot)
        assert len(big) > MAX_ENTITIES
        ent, cats, pos, mask, tags, aux = feats._encode_entities(
            big, MAX_ENTITIES, True
        )
        assert int(mask.sum()) == MAX_ENTITIES
        order = cats[:, 1].tolist()
        assert order == sorted(order)  # alliance groups, own units first
        rev = Units(list(reversed(list(big))), bot)
        ent2, cats2, *_ = feats._encode_entities(rev, MAX_ENTITIES, True)
        np.testing.assert_array_equal(ent, ent2)
        np.testing.assert_array_equal(cats, cats2)

    def test_spawn_plane_marked(self, bot: BotAI, event_loop):
        obs = Features(bot).build_observation()
        plane = dict(zip(SPATIAL_CHANNEL_NAMES, np.asarray(obs.spatial[0])))["spawn"]
        assert plane.max() == 1.0

    def test_vespene_contents(self, bot: BotAI, event_loop):
        geyser = next(
            (u for u in bot.all_units if u._proto.vespene_contents > 0), None
        )
        if geyser is None:
            pytest.skip("no vespene geyser on this map")
        feats = Features(bot)
        ent, _cats, _pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        row = tags.index(int(geyser.tag))
        assert mask[row] == 1.0
        assert ent[row, 14] > 0.0  # EN_VESPENE

    def test_full_entity_recompute(self, bot: BotAI, event_loop):
        """Recompute all entity columns from raw protos (no encoder
        helpers) and diff against the encoder output, for every unit."""
        import math

        from cython_extensions.features import ENTITY_CAT_DIM, ENTITY_NUM_DIM

        feats = Features(bot)
        w = float(feats.map_width)
        h = float(feats.map_height)
        dx = w - 1.0 if w > 1.0 else 1.0
        dy = h - 1.0 if h > 1.0 else 1.0

        def clip01(v):
            return min(max(float(v), 0.0), 1.0)

        def ratio(a, b):
            return clip01(a / b) if b > 1e-6 else 0.0

        def lognorm(v, s):
            return clip01(math.log1p(max(v, 0.0)) / math.log1p(s))

        def initial_resource(raw_type, mineral_c, vespene_c):
            if mineral_c > 0.0:
                if raw_type in (147, 483, 666, 797, 885, 887):
                    return 750.0
                if raw_type == 1996:
                    return 450.0
                if raw_type == 1998:
                    return 900.0
                return 1800.0
            if vespene_c > 0.0:
                return 2250.0
            return 0.0

        ent, cats, _pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        assert ent.shape[1] == ENTITY_NUM_DIM
        assert cats.shape[1] == ENTITY_CAT_DIM
        n = int(mask.sum())
        assert n == len(bot.all_units)
        tag_to_type = {int(u.tag): int(u._proto.unit_type) for u in bot.all_units}
        passenger_tags: set[int] = set()
        for u in bot.all_units:
            try:
                for passenger in u._proto.passengers:
                    passenger_tags.add(int(passenger.tag))
            except Exception:
                continue
        for u in bot.all_units:
            row = tags.index(int(u.tag))
            p = u._proto
            raw_type = int(p.unit_type)
            facing = float(p.facing) % (2 * math.pi)
            exp_num = [0.0] * ENTITY_NUM_DIM
            exp_num[0] = clip01(p.pos.x / dx)
            exp_num[1] = clip01(p.pos.y / dy)
            exp_num[2] = clip01(math.sin(facing) * 0.5 + 0.5)
            exp_num[3] = clip01(math.cos(facing) * 0.5 + 0.5)
            exp_num[4] = ratio(p.health, p.health_max)
            exp_num[5] = ratio(p.shield, p.shield_max)
            exp_num[6] = ratio(p.energy, p.energy_max)
            exp_num[7] = lognorm(p.radius, 4.0)
            exp_num[8] = clip01(p.cargo_space_taken / 8.0)
            exp_num[9] = clip01(p.cargo_space_max / 8.0)
            exp_num[10] = clip01(p.build_progress)
            exp_num[11] = clip01(p.weapon_cooldown / 50.0)
            exp_num[12] = lognorm(float(u.movement_speed), 8.0)
            exp_num[13] = lognorm(p.mineral_contents, 2500.0)
            exp_num[14] = lognorm(p.vespene_contents, 2500.0)
            exp_num[15] = ratio(p.assigned_harvesters, p.ideal_harvesters)
            exp_num[20] = 1.0 if int(p.engaged_target_tag) != 0 else 0.0
            exp_num[21] = clip01(
                float(u.orders[0].progress) if u.orders else 0.0
            )
            init = initial_resource(
                raw_type, float(p.mineral_contents), float(p.vespene_contents)
            )
            mined = (
                max(
                    0.0,
                    init
                    - (float(p.mineral_contents) + float(p.vespene_contents)),
                )
                if init > 0.0
                else 0.0
            )
            exp_num[22] = lognorm(mined, 2500.0)
            exp_num[23] = lognorm(float(p.detect_range), 16.0)
            exp_num[24] = clip01(float(p.pos.z) / 16.0)
            exp_cat = [0] * ENTITY_CAT_DIM
            exp_cat[0] = UNIT_TYPE_DICT.get(int(p.unit_type), 0)
            exp_cat[1] = int(u.alliance) - 1
            exp_cat[2] = int(p.display_type)
            exp_cat[3] = int(p.cloak)
            exp_cat[8] = 1 if p.is_flying else 0
            exp_cat[9] = 1 if p.is_burrowed else 0
            exp_cat[10] = 1 if p.is_hallucination else 0
            exp_cat[11] = 1 if p.is_active else 0
            exp_cat[12] = 1 if p.is_powered else 0
            exp_cat[13] = 1 if p.is_selected else 0
            exp_cat[14] = int(p.attack_upgrade_level)
            exp_cat[15] = int(p.armor_upgrade_level)
            exp_cat[16] = int(p.shield_upgrade_level)
            exp_cat[17] = min(len(u.orders), 8)
            exp_cat[18] = 1 if p.is_on_screen else 0
            exp_cat[19] = 1 if p.is_blip else 0
            exp_cat[20] = 1 if int(u.tag) in passenger_tags else 0
            addon_tag = int(p.add_on_tag)
            if addon_tag != 0:
                if addon_tag in tag_to_type:
                    exp_cat[21] = UNIT_TYPE_DICT.get(tag_to_type[addon_tag], 1)
                else:
                    exp_cat[21] = 1
            engaged_tag = int(p.engaged_target_tag)
            if engaged_tag != 0:
                ttype = tag_to_type.get(engaged_tag)
                exp_cat[22] = (
                    UNIT_TYPE_DICT.get(ttype, 0) if ttype is not None else 0
                )
            exp_cat[23] = min(max(int(p.owner), 0), 15)
            live_buffs = [int(b) for b in p.buff_ids]
            if live_buffs:
                exp_cat[6] = BUFF_DICT.get(live_buffs[0], 0)
                exp_num[16] = clip01(float(p.buff_duration_remain) / 60.0)
                if len(live_buffs) > 1:
                    exp_cat[7] = BUFF_DICT.get(live_buffs[1], 0)
            if u.orders:
                first = u.orders[0]
                ab = getattr(getattr(first, "ability", None), "id", None)
                ab = getattr(ab, "value", ab)
                try:
                    exp_cat[4] = ABILITY_DICT.get(int(ab), 0)
                except Exception:
                    exp_cat[4] = 0
                tgt = getattr(first, "target_unit_tag", None)
                if tgt is None:
                    tgt = getattr(first, "target", None)
                if isinstance(tgt, bool):
                    pass
                elif isinstance(tgt, int):
                    ttype = tag_to_type.get(int(tgt))
                    exp_cat[5] = UNIT_TYPE_DICT.get(ttype, 0) if ttype is not None else 0
                elif tgt is not None and hasattr(tgt, "x"):
                    exp_num[18] = clip01(float(tgt.x) / dx)
                    exp_num[19] = clip01(float(tgt.y) / dy)
            np.testing.assert_allclose(
                ent[row], exp_num, rtol=1e-5, atol=1e-6, err_msg=u.name
            )
            np.testing.assert_array_equal(cats[row], exp_cat, err_msg=u.name)

    def test_static_spatial_matches_source_grids(self, bot: BotAI, event_loop):
        """Static planes at native res must equal the source grids (catches
        transposition / scaling bugs that valid-looking output would hide)."""
        feats = Features(bot)
        h, w = int(feats.map_height), int(feats.map_width)
        _ent, _cats, pos, mask, _tags, aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        spatial, _ = feats._encode_spatial(
            entity_positions=pos,
            entity_mask=mask,
            entity_aux=aux,
            target_spatial_size=(h, w),
        )
        assert spatial.shape == (len(SPATIAL_CHANNEL_NAMES), h, w)
        chans = dict(zip(SPATIAL_CHANNEL_NAMES, spatial))
        playable = chans["playable"]
        assert playable.max() == 1.0
        height = np.asarray(bot.game_info.terrain_height.data_numpy, dtype=np.float32)
        if height.shape != (h, w):
            height = height.T
        height = (height - height.min()) / max(height.max() - height.min(), 1e-6)
        np.testing.assert_allclose(chans["height"], height * playable, atol=1e-6)
        for name, attr in (("pathable", "pathing_grid"), ("placement", "placement_grid")):
            raw = np.asarray(
                getattr(bot.game_info, attr).data_numpy, dtype=np.float32
            )
            if raw.shape != (h, w):
                raw = raw.T
            np.testing.assert_allclose(
                chans[name], np.clip(raw, 0.0, 1.0) * playable, atol=1e-6
            )
        vis = np.asarray(bot.state.visibility.data_numpy, dtype=np.float32)
        if vis.shape != (h, w):
            vis = vis.T
        np.testing.assert_allclose(
            chans["visibility"], np.nan_to_num(vis) / 2.0 * playable, atol=1e-6
        )
        creep = np.asarray(bot.state.creep.data_numpy, dtype=np.float32)
        if creep.shape != (h, w):
            creep = creep.T
        np.testing.assert_allclose(
            chans["creep"], np.clip(np.nan_to_num(creep), 0.0, 1.0) * playable, atol=1e-6
        )

    def test_order_unit_target(self, bot: BotAI, event_loop):
        feats = Features(bot)
        worker = next((u for u in bot.workers if u.orders), None)
        if worker is None:
            pytest.skip("no ordered worker on this map")
        first = worker.orders[0]
        tgt = getattr(first, "target_unit_tag", None)
        if tgt is None:
            tgt = getattr(first, "target", None)
        assert isinstance(tgt, int)
        target_unit = next(u for u in bot.all_units if int(u.tag) == int(tgt))
        expected = UNIT_TYPE_DICT.get(int(target_unit._proto.unit_type), 0)
        assert expected > 0
        _ent, cats, _pos, _mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        row = tags.index(int(worker.tag))
        assert cats[row, 5] == expected  # EC_ORDER_TARGET_UNIT

    @staticmethod
    def _scatter_add(values, gx, gy, h, w):
        """Summing scatter into cells (same convention as features.pyx)."""
        flat = np.zeros(h * w, dtype=np.float32)
        np.add.at(flat, gy * w + gx, values)
        return flat.reshape(h, w)

    def test_hp_mass_matches_cell_sums(self, bot: BotAI, event_loop):
        """Encoder hp_self plane must equal independently accumulated hp mass
        (up to its log-norm) on every playable cell."""
        feats = Features(bot)
        _ent, cats, pos, mask, _tags, aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        spatial, _ = feats._encode_spatial(
            entity_positions=pos, entity_mask=mask, entity_aux=aux
        )
        chans = dict(zip(SPATIAL_CHANNEL_NAMES, spatial))
        valid = (mask > 0.5) & np.isin(cats[:, 1], [0, 1])
        gx = np.clip((pos[valid, 0] * 128).astype(np.int64), 0, 127)
        gy = np.clip((pos[valid, 1] * 128).astype(np.int64), 0, 127)
        expected = np.log1p(
            self._scatter_add(aux[valid, 0], gx, gy, 128, 128)
        ) / np.log1p(4000.0)
        playable = chans["playable"] > 0.5
        np.testing.assert_allclose(
            chans["hp_self"][playable], expected[playable], rtol=1e-5, atol=1e-5
        )

    def test_density_matches_counts(self, bot: BotAI, event_loop):
        """Encoder density_self plane must equal independently accumulated
        unit counts (up to its log-norm) on every playable cell."""
        feats = Features(bot)
        _ent, cats, pos, mask, _tags, aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        spatial, _ = feats._encode_spatial(
            entity_positions=pos, entity_mask=mask, entity_aux=aux
        )
        chans = dict(zip(SPATIAL_CHANNEL_NAMES, spatial))
        valid = (mask > 0.5) & np.isin(cats[:, 1], [0, 1])
        n = int(valid.sum())
        gx = np.clip((pos[valid, 0] * 128).astype(np.int64), 0, 127)
        gy = np.clip((pos[valid, 1] * 128).astype(np.int64), 0, 127)
        expected = np.log1p(
            self._scatter_add(np.ones(n, dtype=np.float32), gx, gy, 128, 128)
        ) / np.log1p(32.0)
        playable = chans["playable"] > 0.5
        np.testing.assert_allclose(
            chans["density_self"][playable], expected[playable], rtol=1e-5, atol=1e-5
        )

    def test_layout_dimensions(self, bot: BotAI, event_loop):
        """Entity/scalar widths match the layout constants; all real rows
        are finite and padded rows are exact zeros."""
        from cython_extensions.features import ENTITY_CAT_DIM, ENTITY_NUM_DIM

        feats = Features(bot)
        ent, cats, _pos, mask, _tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        n = int(mask.sum())
        assert ent.shape == (MAX_ENTITIES, ENTITY_NUM_DIM)
        assert cats.shape == (MAX_ENTITIES, ENTITY_CAT_DIM)
        assert np.isfinite(ent[:n]).all()
        assert (ent[n:] == 0.0).all()
        assert (cats[n:] == 0).all()

    def test_facing_sincos_consistent(self, bot: BotAI, event_loop):
        """Sin/cos pair must sit on the unit circle and match raw facing."""
        import math

        feats = Features(bot)
        ent, _cats, _pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        n = int(mask.sum())
        s, c = ent[:n, 2], ent[:n, 3]
        np.testing.assert_allclose(
            (2 * s - 1) ** 2 + (2 * c - 1) ** 2,
            np.ones(n, dtype=np.float32),
            rtol=1e-5,
            atol=1e-5,
        )
        for u in bot.all_units:
            row = tags.index(int(u.tag))
            facing = float(u._proto.facing) % (2 * math.pi)
            assert s[row] == pytest.approx(math.sin(facing) * 0.5 + 0.5, abs=1e-6)
            assert c[row] == pytest.approx(math.cos(facing) * 0.5 + 0.5, abs=1e-6)

    def test_screen_blip_owner_ranges(self, bot: BotAI, event_loop):
        """New mask/owner categoricals are bounded and match raw protos."""
        feats = Features(bot)
        _ent, cats, _pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        n = int(mask.sum())
        on_screen, blip, in_cargo = cats[:n, 18], cats[:n, 19], cats[:n, 20]
        assert set(np.unique(on_screen).tolist()) <= {0, 1}
        assert set(np.unique(blip).tolist()) <= {0, 1}
        assert set(np.unique(in_cargo).tolist()) <= {0, 1}
        assert cats[:n, 23].min() >= 0 and cats[:n, 23].max() <= 15
        # Start-state pickles: own visible units on screen, no blips/cargo.
        assert on_screen.max() == 1
        assert blip.max() == 0
        assert in_cargo.max() == 0
        for u in bot.all_units:
            row = tags.index(int(u.tag))
            assert cats[row, 18] == (1 if u._proto.is_on_screen else 0)
            assert cats[row, 23] == min(max(int(u._proto.owner), 0), 15)

    def test_order_length_and_progress(self, bot: BotAI, event_loop):
        """Queue length matches len(orders); progress matches first order."""
        feats = Features(bot)
        ent, cats, _pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        n = int(mask.sum())
        assert cats[:n, 17].min() >= 0 and cats[:n, 17].max() <= 8
        assert ent[:n, 21].min() >= 0.0 and ent[:n, 21].max() <= 1.0
        worker = bot.workers[0]
        row = tags.index(int(worker.tag))
        assert cats[row, 17] == min(len(worker.orders), 8)
        if worker.orders:
            assert ent[row, 21] == pytest.approx(
                min(max(float(worker.orders[0].progress), 0.0), 1.0)
            )

    def test_mined_only_on_resources(self, bot: BotAI, event_loop):
        """Mined column is zero for non-resources and bounded everywhere."""
        feats = Features(bot)
        ent, cats, _pos, mask, tags, _aux = feats._encode_entities(
            bot.all_units, MAX_ENTITIES, True
        )
        n = int(mask.sum())
        assert ent[:n, 22].min() >= 0.0 and ent[:n, 22].max() <= 1.0
        # Fresh start-state fields are full -> nothing mined yet.
        assert ent[:n, 22].max() == 0.0
        for u in bot.all_units:
            row = tags.index(int(u.tag))
            if (
                u._proto.mineral_contents == 0
                and u._proto.vespene_contents == 0
            ):
                assert ent[row, 22] == 0.0

    def test_scalar_killed_split_lost_spent(self, bot: BotAI, event_loop):
        """Split killed units/structures + lost/spent match score details."""
        import math

        feats = Features(bot)
        scalar = feats._encode_scalar()
        by_name = dict(zip(SCALAR_FEATURE_NAMES, scalar.tolist()))
        score = bot.state.score
        assert by_name["killed_units"] == pytest.approx(
            min(max(math.log1p(float(score.killed_value_units)) / math.log1p(10000.0), 0.0), 1.0)
        )
        assert by_name["killed_structures"] == pytest.approx(
            min(max(math.log1p(float(score.killed_value_structures)) / math.log1p(10000.0), 0.0), 1.0)
        )
        lost = sum(
            float(getattr(score, f"lost_minerals_{c}", 0.0))
            + float(getattr(score, f"lost_vespene_{c}", 0.0))
            for c in ("none", "army", "economy", "technology", "upgrade")
        )
        spent = float(getattr(score, "spent_minerals", 0.0)) + float(
            getattr(score, "spent_vespene", 0.0)
        )
        assert by_name["lost_value"] == pytest.approx(
            min(max(math.log1p(max(lost, 0.0)) / math.log1p(50000.0), 0.0), 1.0)
        )
        assert by_name["spent_value"] == pytest.approx(
            min(max(math.log1p(max(spent, 0.0)) / math.log1p(50000.0), 0.0), 1.0)
        )
