"""Shared pytest fixtures for the plotter test suite."""

from json import dumps
from pathlib import Path

import pytest

import plotter as plt


@pytest.fixture
def sample_text_data() -> list[dict[str, object]]:
    """Provide representative subplot metadata for canvas and text tests."""
    return [
        {
            "title": "Test 1",
            "x_label": "$ x $",
            "y_label": "$ y $",
            "scatter_plots": ["data"],
            "line_plots": ["line"],
            "histograms": ["hist"],
            "histograms_2d": ["hist"],
            "images": ["img1", "img2"],
        },
        {
            "title": "Test 2",
            "x_label": "$ x $",
            "y_label": "$ y $",
            "scatter_plots": ["data1", "data2"],
            "line_plots": ["line"],
            "histograms": ["hist1", "hist2", "hist3"],
            "histograms_2d": [""],
            "images": [""],
        },
    ]


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated workspace and make it the current working directory."""
    plt.setup_workspace(tmp_path)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def text_file(workspace: Path, sample_text_data: list[dict[str, object]]) -> Path:
    """Write two-subplot metadata to a JSON file and return its path."""
    file_path = workspace / "plotter" / "text" / "labels.json"
    file_path.write_text(dumps(sample_text_data))
    return file_path


@pytest.fixture
def single_text_file(workspace: Path, sample_text_data: list[dict[str, object]]) -> Path:
    """Write one-subplot metadata to a JSON file and return its path."""
    file_path = workspace / "plotter" / "text" / "single_labels.json"
    file_path.write_text(dumps(sample_text_data[:1]))
    return file_path
