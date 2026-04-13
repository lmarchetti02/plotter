"""Tests for text loading and fallback behavior."""

from json import dumps
from pathlib import Path

import pytest

from plotter.drawable import Drawable
from plotter.helpers.text import PlotText, Text


def test_plot_text_empty_factory_returns_a_complete_placeholder() -> None:
    """The empty PlotText factory should populate every supported label collection."""
    empty_text = PlotText.get_empy_text()

    assert empty_text.title == ""
    assert empty_text.x_label == ""
    assert empty_text.y_label == ""
    for name in Drawable.get_label_names():
        assert getattr(empty_text, name) == [""]


def test_text_reads_json_with_or_without_extension(
    workspace: Path,
    text_file: Path,
    sample_text_data: list[dict[str, object]],
) -> None:
    """Text.read_json should parse the same file whether or not `.json` is given."""
    relative_path = Path("labels")

    text_from_stem = Text(len(sample_text_data))
    text_from_stem.read_json(str(relative_path))

    text_from_full_name = Text(len(sample_text_data))
    text_from_full_name.read_json(str(text_file))

    assert text_from_stem == text_from_full_name
    assert list(text_from_stem) == text_from_stem.subplots_text
    assert text_from_stem[0] == PlotText(**sample_text_data[0])  # type: ignore
    assert text_from_stem[1] == PlotText(**sample_text_data[1])  # type: ignore


def test_text_creates_a_default_file_when_json_is_missing(workspace: Path) -> None:
    """Missing text files should be created automatically with empty placeholder content."""
    missing_file = workspace / "plotter" / "text" / "new_labels.json"

    text = Text(2)
    text.read_json(str(missing_file))

    expected = [PlotText.get_empy_text(), PlotText.get_empy_text()]
    assert missing_file.exists()
    assert text.subplots_text == expected
    assert missing_file.read_text() == dumps([subplot.to_dict() for subplot in expected])


@pytest.mark.parametrize(
    "payload",
    [
        '[{"title": "missing required fields"}]',
        '{"not": "a list"}',
    ],
)
def test_text_falls_back_to_empty_text_for_unparseable_json(workspace: Path, payload: str) -> None:
    """Invalid JSON structures should not crash text loading and should clear labels."""
    corrupted_file = workspace / "plotter" / "text" / "corrupted.json"
    corrupted_file.write_text(payload)

    text = Text(2)
    text.read_json(str(corrupted_file))

    assert text.subplots_text == [PlotText.get_empy_text(), PlotText.get_empy_text()]


def test_text_raises_when_json_contains_the_wrong_number_of_subplots(
    workspace: Path,
    sample_text_data: list[dict[str, object]],
) -> None:
    """A mismatch between canvas size and JSON entries should raise a ValueError."""
    mismatch_file = workspace / "plotter" / "text" / "mismatch.json"
    mismatch_file.write_text(dumps(sample_text_data[:1]))

    text = Text(2)

    with pytest.raises(ValueError, match="Incorrect number of plots"):
        text.read_json(str(mismatch_file))
