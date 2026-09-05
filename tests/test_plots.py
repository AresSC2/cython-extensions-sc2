from pathlib import Path

import pytest

matplotlib = pytest.importorskip(
    "matplotlib", reason="plots need the dev-only matplotlib dependency"
)
matplotlib.use("Agg")
from sc2.bot_ai import BotAI

from cython_extensions.features import Features
from cython_extensions.plots import (
    plot_entities,
    plot_observation,
    plot_scalar,
    plot_spatial,
)

pytest_plugins = ("pytest_asyncio",)

MAPS: list[Path] = [
    map_path
    for map_path in (Path(__file__).parent / "pickle_data").iterdir()
    if map_path.suffix == ".xz"
]

assert MAPS, "expected pickle maps under tests/pickle_data"


@pytest.mark.parametrize("bot", MAPS, indirect=True)
class TestPlots:
    scenarios = [(map_path.name, {"map_path": map_path}) for map_path in MAPS]

    def test_plot_spatial_saves(self, bot: BotAI, event_loop, tmp_path):
        obs = Features(bot).build_observation()
        out = tmp_path / "spatial.png"
        fig = plot_spatial(obs, save_path=str(out))
        assert out.stat().st_size > 0
        assert fig is not None

    def test_plot_spatial_channel_subset(self, bot: BotAI, event_loop, tmp_path):
        obs = Features(bot).build_observation()
        out = tmp_path / "subset.png"
        plot_spatial(obs, channels=["height", "density_self", 10], save_path=str(out))
        assert out.stat().st_size > 0

    def test_plot_entities_saves(self, bot: BotAI, event_loop, tmp_path):
        obs = Features(bot).build_observation()
        out = tmp_path / "entities.png"
        ax = plot_entities(obs, save_path=str(out))
        assert out.stat().st_size > 0
        assert ax is not None

    def test_plot_scalar_saves(self, bot: BotAI, event_loop, tmp_path):
        obs = Features(bot).build_observation()
        out = tmp_path / "scalar.png"
        ax = plot_scalar(obs, save_path=str(out))
        assert out.stat().st_size > 0
        assert ax is not None

    def test_plot_observation_saves(self, bot: BotAI, event_loop, tmp_path):
        obs = Features(bot).build_observation()
        out = tmp_path / "observation.png"
        fig = plot_observation(obs, save_path=str(out))
        assert out.stat().st_size > 0
        assert fig is not None
