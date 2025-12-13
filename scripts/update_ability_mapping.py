#!/usr/bin/env python3
"""
Script to rewrite `ability_mapping.pyx` entries so keys use `UnitTypeId.<NAME>.value`
and (when possible) the RHS uses `AbilityId.<NAME>.value`. If the ability name
cannot be resolved, the script leaves the numeric literal on the RHS.

The script updates lines like:
    mapping_array[18] = 319 #SupplyDepot
into:
    mapping_array[UnitTypeId.SUPPLYDEPOT.value] = AbilityId.SOME_ABILITY.value  # SupplyDepot

It prefers using the trailing comment to determine the UnitTypeId name. If that
is missing, it will try to resolve the unit name using `sc2.ids.unit_typeid.UnitTypeId(<key>)`.
It will also attempt to resolve the AbilityId name from the numeric ability id
via `sc2.ids.ability_id.AbilityId(<value>)` and use `AbilityId.<NAME>.value` on the RHS.

Run:
    python scripts/update_ability_mapping.py path/to/ability_mapping.pyx

If you omit the path it defaults to `cython_extensions/ability_mapping.pyx`.
"""

import re
import sys
from pathlib import Path
import datetime

try:
    from sc2.ids.unit_typeid import UnitTypeId
    from sc2.ids.ability_id import AbilityId
except Exception:
    UnitTypeId = None
    AbilityId = None

MAPPING_RE = re.compile(r"^(\s*)mapping_array\s*\[\s*(\d+)\s*\]\s*=\s*(\d+)(\s*#\s*(.*))?\s*$")

# Regex to match Struct_ABILITIES:
STRUCT_RE = re.compile(r"^STRUCT_ABILITIES\s*\[\s*(\d+)\s*\]\s*=\s*(\d+)(\s*#\s*(.*))?\s*$") 


# REGEX tto remove update header 
HEADER_RE = re.compile(r"^#\s*Rewritten mappings from UNIT_TYPE_ID_TO_ABILITY_MAP(?:,\s*Updated at .+)?\s*$")

STRUCT_HEADER_RE = re.compile(r"^#\s*(?:STRUCT_ABILITIES|STRUCT_ABILLITIES)")




UNIT_TYPE_ID_TO_ABILITY_MAP = {
    UnitTypeId.COMMANDCENTER: AbilityId.TERRANBUILD_COMMANDCENTER,
    UnitTypeId.SUPPLYDEPOT: AbilityId.TERRANBUILD_SUPPLYDEPOT,
    UnitTypeId.REFINERY: AbilityId.TERRANBUILD_REFINERY,
    UnitTypeId.BARRACKS: AbilityId.TERRANBUILD_BARRACKS,
    UnitTypeId.ENGINEERINGBAY: AbilityId.TERRANBUILD_ENGINEERINGBAY,
    UnitTypeId.MISSILETURRET: AbilityId.TERRANBUILD_MISSILETURRET,
    UnitTypeId.BUNKER: AbilityId.TERRANBUILD_BUNKER,
    UnitTypeId.SENSORTOWER: AbilityId.TERRANBUILD_SENSORTOWER,
    UnitTypeId.GHOSTACADEMY: AbilityId.TERRANBUILD_GHOSTACADEMY,
    UnitTypeId.FACTORY: AbilityId.TERRANBUILD_FACTORY,
    UnitTypeId.STARPORT: AbilityId.TERRANBUILD_STARPORT,
    UnitTypeId.ARMORY: AbilityId.TERRANBUILD_ARMORY,
    UnitTypeId.FUSIONCORE: AbilityId.TERRANBUILD_FUSIONCORE,
    UnitTypeId.BARRACKSTECHLAB: AbilityId.BUILD_TECHLAB_BARRACKS,
    UnitTypeId.FACTORYTECHLAB: AbilityId.BUILD_TECHLAB_FACTORY,
    UnitTypeId.STARPORTTECHLAB: AbilityId.BUILD_TECHLAB_STARPORT,
    UnitTypeId.BARRACKSREACTOR: AbilityId.BUILD_REACTOR_BARRACKS,
    UnitTypeId.FACTORYREACTOR: AbilityId.BUILD_REACTOR_FACTORY,
    UnitTypeId.STARPORTREACTOR: AbilityId.BUILD_REACTOR_STARPORT,
    UnitTypeId.PLANETARYFORTRESS: AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS,
    UnitTypeId.ORBITALCOMMAND: AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
    UnitTypeId.NEXUS: AbilityId.PROTOSSBUILD_NEXUS,
    UnitTypeId.PYLON: AbilityId.PROTOSSBUILD_PYLON,
    UnitTypeId.ASSIMILATOR: AbilityId.PROTOSSBUILD_ASSIMILATOR,
    UnitTypeId.GATEWAY: AbilityId.PROTOSSBUILD_GATEWAY,
    UnitTypeId.FORGE: AbilityId.PROTOSSBUILD_FORGE,
    UnitTypeId.TWILIGHTCOUNCIL: AbilityId.PROTOSSBUILD_TWILIGHTCOUNCIL,
    UnitTypeId.FLEETBEACON: AbilityId.PROTOSSBUILD_FLEETBEACON,
    UnitTypeId.PHOTONCANNON: AbilityId.PROTOSSBUILD_PHOTONCANNON,
    UnitTypeId.STARGATE: AbilityId.PROTOSSBUILD_STARGATE,
    UnitTypeId.TEMPLARARCHIVE: AbilityId.PROTOSSBUILD_TEMPLARARCHIVE,
    UnitTypeId.DARKSHRINE: AbilityId.PROTOSSBUILD_DARKSHRINE,
    UnitTypeId.ROBOTICSBAY: AbilityId.PROTOSSBUILD_ROBOTICSBAY,
    UnitTypeId.ROBOTICSFACILITY: AbilityId.PROTOSSBUILD_ROBOTICSFACILITY,
    UnitTypeId.CYBERNETICSCORE: AbilityId.PROTOSSBUILD_CYBERNETICSCORE,
    UnitTypeId.SHIELDBATTERY: AbilityId.BUILD_SHIELDBATTERY,
    UnitTypeId.HATCHERY: AbilityId.ZERGBUILD_HATCHERY,
    UnitTypeId.EXTRACTOR: AbilityId.ZERGBUILD_EXTRACTOR,
    UnitTypeId.SPAWNINGPOOL: AbilityId.ZERGBUILD_SPAWNINGPOOL,
    UnitTypeId.EVOLUTIONCHAMBER: AbilityId.ZERGBUILD_EVOLUTIONCHAMBER,
    UnitTypeId.ROACHWARREN: AbilityId.ZERGBUILD_ROACHWARREN,
    UnitTypeId.SPINECRAWLER: AbilityId.ZERGBUILD_SPINECRAWLER,
    UnitTypeId.SPORECRAWLER: AbilityId.ZERGBUILD_SPORECRAWLER,
    UnitTypeId.HYDRALISKDEN: AbilityId.ZERGBUILD_HYDRALISKDEN,
    UnitTypeId.SPIRE: AbilityId.ZERGBUILD_SPIRE,
    UnitTypeId.ULTRALISKCAVERN: AbilityId.ZERGBUILD_ULTRALISKCAVERN,
    UnitTypeId.INFESTATIONPIT: AbilityId.ZERGBUILD_INFESTATIONPIT,
    UnitTypeId.NYDUSNETWORK: AbilityId.ZERGBUILD_NYDUSNETWORK,
    UnitTypeId.BANELINGNEST: AbilityId.ZERGBUILD_BANELINGNEST,
    UnitTypeId.ASSIMILATORRICH: AbilityId.PROTOSSBUILD_ASSIMILATOR,
    UnitTypeId.EXTRACTORRICH: AbilityId.ZERGBUILD_EXTRACTOR,
    UnitTypeId.REFINERYRICH: AbilityId.TERRANBUILD_REFINERY,
    UnitTypeId.TECHLAB: AbilityId.BUILD_TECHLAB,
    UnitTypeId.LAIR: AbilityId.UPGRADETOLAIR_LAIR,
    UnitTypeId.HIVE: AbilityId.UPGRADETOHIVE_HIVE,
    UnitTypeId.PLANETARYFORTRESS: AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS,
    UnitTypeId.ORBITALCOMMAND: AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND,
}

STRUCT_ABILITIES= {}


STRUCT_ABILITIES[AbilityId.BUILD_REACTOR_STARPORT.value] = 1
STRUCT_ABILITIES[AbilityId.BUILD_TECHLAB_STARPORT.value] = 1
STRUCT_ABILITIES[AbilityId.BUILD_REACTOR_FACTORY.value] = 1
STRUCT_ABILITIES[AbilityId.BUILD_TECHLAB_FACTORY.value] = 1
STRUCT_ABILITIES[AbilityId.BUILD_REACTOR_BARRACKS.value] = 1
STRUCT_ABILITIES[AbilityId.BUILD_TECHLAB_BARRACKS.value] = 1
STRUCT_ABILITIES[AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS.value] = 1
STRUCT_ABILITIES[AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND.value] = 1
STRUCT_ABILITIES[AbilityId.TERRANBUILD_COMMANDCENTER.value] = 2  #used to identify CC in ability order tracker
STRUCT_ABILITIES[AbilityId.ZERGBUILD_HATCHERY.value] = 2
STRUCT_ABILITIES[AbilityId.UPGRADETOHIVE_HIVE.value] = 1
# Special case Lair. Since upgradetolair ability is used from transition from Hatchery to Lair, but also used to identify Lair structure, lair has a special role
# Therefore, we set it to 2 to identify it as a structure in the ability order tracker, but its also identified as an upgrade ability to lair.
#It should have both 2 and 1.

STRUCT_ABILITIES[AbilityId.UPGRADETOLAIR_LAIR.value] = 2 



def normalize_unitname(name: str) -> str:
    # convert comment like "SupplyDepot" or "Supply Depot" to SUPPLYDEPOT
    s = name.strip()
    s = s.replace(" ", "_")
    s = s.replace("-", "_")
    return s.upper()


def try_resolve_unit_name_from_key(key: int):
    if UnitTypeId is None:
        return None
    try:
        return UnitTypeId(key).name
    except Exception:
        return None


def try_resolve_ability_name_from_value(val: int):
    if AbilityId is None:
        return None
    try:
        return AbilityId(val).name
    except Exception:
        return None


def transform_line(line: str):
    m = MAPPING_RE.match(line)
    if not m:
        return line
    indent, key_s, val_s, _, comment = m.groups()
    key = int(key_s)
    val = int(val_s)

    # Determine unit name
    unit_name = None
    if comment:
        # comment could be like "SupplyDepot" or "CommandCenter"
        # prefer the comment if it looks like a valid Python identifier
        cleaned = comment.strip()
        if cleaned and re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', cleaned.replace(' ', '_')):
            unit_name = cleaned.replace(' ', '_').upper()
    if unit_name is None:
        resolved = try_resolve_unit_name_from_key(key)
        if resolved:
            unit_name = resolved
    # Prefer to use the explicit UNIT_TYPE_ID_TO_ABILITY_MAP defined in this
    # script. Resolve the UnitTypeId enum for the key/comment and look up the
    # RHS ability from the mapping when available.
    ability_name = None
    lhs = f"mapping_array[{key}]"
    rhs = str(val)
    comment_text = f"  # {key}"

    unit_enum = None
    if unit_name is not None and UnitTypeId is not None:
        unit_enum = getattr(UnitTypeId, unit_name, None)
    if unit_enum is None and UnitTypeId is not None:
        # try resolving by numeric key
        try:
            unit_enum = UnitTypeId(key)
        except Exception:
            unit_enum = None

    if unit_enum is not None:
        # Use numeric values for the generated mapping entries. This produces
        # lines like: mapping_array[45] = 78  # BARRACKS
        lhs = f"mapping_array[{unit_enum.value}]"
        comment_text = f"  # {unit_enum.name}"
        if unit_enum in UNIT_TYPE_ID_TO_ABILITY_MAP:
            ability_enum = UNIT_TYPE_ID_TO_ABILITY_MAP[unit_enum]
            if ability_enum is not None:
                rhs = str(ability_enum.value)
        else:
            # Fallback: try to resolve ability numeric value from given literal
            rhs = str(val)

    return f"{indent}{lhs} = {rhs}{comment_text}\n"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "cython_extensions" / "ability_mapping.pyx"
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf8")
    out_lines = []

    # Preserve all non-mapping lines; skip any existing mapping_array[...] lines
    for line in text.splitlines(True):
        if MAPPING_RE.match(line):
            continue
        if STRUCT_RE.match(line):
            continue
        if HEADER_RE.match(line):
            continue
        if STRUCT_HEADER_RE.match(line):
            continue
        out_lines.append(line)

    # Generate mapping lines from UNIT_TYPE_ID_TO_ABILITY_MAP (authoritative)
    entries = []
    for unit_enum, ability_enum in UNIT_TYPE_ID_TO_ABILITY_MAP.items():
        try:
            uval = int(unit_enum.value)
        except Exception:
            # skip entries we can't resolve
            continue
        try:
            aval = int(ability_enum.value) if ability_enum is not None else -1
        except Exception:
            aval = -1
        uname = getattr(unit_enum, 'name', str(unit_enum))
        entries.append((uval, aval, uname))

    # Sort entries by unit id for stable output
    entries.sort()

    mapping_lines = [f"mapping_array[{uval}] = {aval}  # {uname}\n" for uval, aval, uname in entries]

    # Backup and overwrite with regenerated mappings. Place backup in `scripts/`.
    scripts_dir = Path(__file__).parent
    backup = scripts_dir / (path.name + ".bak")
    backup.write_text(text, encoding="utf8")

    new_text = ''.join(out_lines)
    new_text += "\n# Rewritten mappings from UNIT_TYPE_ID_TO_ABILITY_MAP, Updated at {}\n".format(datetime.datetime.now())
    new_text += ''.join(mapping_lines)
    # Append STRUCT_ABILITIES block generated from this script's STRUCT_ABILITIES dict
    try:
        struct_items = sorted(((int(k), int(v)) for k, v in STRUCT_ABILITIES.items()))
    except Exception:
        struct_items = []

    if struct_items:
        new_text += "\n# STRUCT_ABILLITIES\n"
        for aid, flag in struct_items:
            try:
                ability_name = AbilityId(aid).name
            except Exception:
                ability_name = None
            if ability_name:
                new_text += f"STRUCT_ABILITIES[{aid}] = {flag}  # {ability_name}\n"
            else:
                new_text += f"STRUCT_ABILITIES[{aid}] = {flag}\n"

    path.write_text(new_text, encoding="utf8")
    print(f"Updated {path}; original backed up to {backup}")


if __name__ == '__main__':
    main()
