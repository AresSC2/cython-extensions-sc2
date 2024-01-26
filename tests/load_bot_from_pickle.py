import lzma
import pickle
from pathlib import Path
from typing import Any

from sc2.bot_ai import BotAI
from sc2.client import Client
from sc2.game_data import GameData
from sc2.game_info import GameInfo
from sc2.game_state import GameState

MAPS: list[Path] = [
    map_path for map_path in (Path(__file__).parent / "pickle_data").iterdir() if map_path.suffix == ".xz"
]

def build_bot_object_from_pickle_data(raw_game_data, raw_game_info, raw_observation) -> BotAI:
    # Build fresh bot object, and load the pickled data into the bot object
    bot = BotAI()
    game_data = GameData(raw_game_data.data)
    game_info = GameInfo(raw_game_info.game_info)
    game_state = GameState(raw_observation)
    bot._initialize_variables()
    client = Client(True)
    bot._prepare_start(client=client, player_id=1, game_info=game_info, game_data=game_data)
    bot._prepare_step(state=game_state, proto_game_info=raw_game_info)
    return bot

def load_map_pickle_data(map_path: Path) -> tuple[Any, Any, Any]:
    with lzma.open(str(map_path), "rb") as f:
        raw_game_data, raw_game_info, raw_observation = pickle.load(f)
        return raw_game_data, raw_game_info, raw_observation

def get_map_specific_bot(map_path: Path) -> BotAI:
    data = load_map_pickle_data(map_path)
    return build_bot_object_from_pickle_data(*data)
