"""Tests for package-level workspace initialization."""

from pathlib import Path

import pytest


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
    plotter.setup_workspace(tmp_path)

    info_dir = tmp_path / "plotter" / "utils" / "info"
    assert any(info_dir.iterdir())
