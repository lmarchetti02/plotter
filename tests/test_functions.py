import numpy as np
import pytest
import pathlib

from plotter.utils import make_wider
from plotter.utils import _make_denser
from plotter.utils import setup_logging

data = np.array([0, 1, 2])
repeating = np.array([0, 1, 1, 3])


def test_setup_logging():
    setup_logging()
    assert pathlib.Path("./plotter/log/plotter.log").exists()


def test_make_wider():
    assert make_wider(data, 0.1, 0.1, 1).tolist() == [-0.2, 0, 1, 2, 2.2]
    assert make_wider(data, 0, 0.1, 1).tolist() == [0, 1, 2, 2.2]
    assert make_wider(data, 0.1, 0, 1).tolist() == [-0.2, 0, 1, 2]
    assert make_wider(data, 0, 0, 1).tolist() == data.tolist()

    with pytest.raises(ValueError):
        make_wider(data, -1, 0.1, 1)
        make_wider(data, 0.1, -2, 1)
        make_wider(data, 0, 0, -1)


def test_make_denser():
    assert _make_denser(data, 1).tolist() == data.tolist()
    assert _make_denser(repeating, 1).tolist() == repeating.tolist()
    assert _make_denser(data, 2).tolist() == [0, 0.5, 1, 1.5, 2]
