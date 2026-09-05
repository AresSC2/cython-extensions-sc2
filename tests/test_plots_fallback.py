"""Plots degrade to warn + None when matplotlib is absent.

Runs in every environment (no matplotlib import here); the real backend is
blocked via monkeypatched ``sys.modules``.
"""

import sys

import numpy as np
import pytest

from cython_extensions import plots


def _block_matplotlib(monkeypatch):
    monkeypatch.setitem(sys.modules, "matplotlib", None)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", None)


@pytest.mark.parametrize(
    "call",
    [
        lambda: plots.plot_spatial(np.zeros((2, 4, 4), np.float32)),
        lambda: plots.plot_entities(
            (
                np.zeros((3, 20), np.float32),
                np.zeros((3, 17), np.int64),
                np.zeros(3, np.float32),
                np.zeros((3, 2), np.float32),
            )
        ),
        lambda: plots.plot_scalar(np.zeros(47, np.float32)),
        lambda: plots.plot_observation(np.zeros((2, 4, 4), np.float32)),
    ],
    ids=["spatial", "entities", "scalar", "observation"],
)
def test_plot_without_matplotlib_warns_and_returns_none(monkeypatch, call):
    _block_matplotlib(monkeypatch)
    with pytest.warns(UserWarning, match="matplotlib"):
        assert call() is None
