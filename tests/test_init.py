"""Tests for package-level workspace initialization."""

from json import loads
from pathlib import Path

import pytest

from plotter.helpers.text import PlotText


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("img"),
        Path("log"),
        Path("text"),
        Path("utils"),
        Path("utils/info"),
        Path("log/plotter.log"),
        Path("text/text_example.json"),
        Path("utils/style.mplstyle"),
        Path("utils/log_config.json"),
    ],
)
def test_setup_workspace_creates_expected_directories_and_files(tmp_path: Path, relative_path: Path) -> None:
    """setup_workspace should materialize the full on-disk structure used by the package."""
    import plotter

    plotter.setup_workspace(tmp_path)

    assert (tmp_path / "plotter" / relative_path).exists()


def test_setup_workspace_is_idempotent_and_keeps_packaged_assets(tmp_path: Path) -> None:
    """Running setup_workspace repeatedly should succeed and preserve copied assets."""
    import plotter

    plotter.setup_workspace(tmp_path)

    # modify file
    style_path = tmp_path / "plotter/utils/style.mplstyle"
    with open(style_path, "a") as f:
        f.write("\ntest")

    plotter.setup_workspace(tmp_path)

    info_dir = tmp_path / "plotter" / "utils" / "info"
    assert any(info_dir.iterdir())

    # assert modification is kept
    with open(style_path, "r") as f:
        lines = f.readlines()
        assert lines[-1] == "test"


def test_setup_workspace_generates_text_example_from_the_drawable_registry(tmp_path: Path) -> None:
    """The generated example JSON should be derived from the registry-backed empty PlotText."""
    import plotter

    plotter.setup_workspace(tmp_path)

    text_example = tmp_path / "plotter" / "text" / "text_example.json"
    assert loads(text_example.read_text()) == PlotText.get_empty_json()
