"""Tests for canvas setup and drawing helpers."""

from pathlib import Path

import pytest

import plotter as plt


def test_counters_initialize_with_one_slot_per_subplot() -> None:
    """Counters should start empty and track each drawable family independently."""
    counters = plt.canvas._Counters.initialize_counters(2)

    for name in plt.Drawable.get_label_names():
        assert getattr(counters, name) == [0, 0]

    assert counters.is_empty()

    counters.histograms_2d[0] += 1
    counters.images[1] += 1

    assert not counters.is_empty()


def test_canvas_setup_applies_axes_configuration(text_file: Path) -> None:
    """Canvas.setup should apply labels, limits, scales, and legend settings."""
    with plt.Canvas(str(text_file), (1, 2), show=False) as canvas:
        canvas.setup(
            plot_n=1,
            xlim=(0.0, 5.0),
            ylim=(-1.0, 3.0),
            xscale="log",
            yscale="symlog",
            inverted=(True, False),
            legend=3,
        )

        axis = canvas.axes[1]
        assert axis.get_xlim() == pytest.approx((5.0, 0.0))
        assert axis.get_ylim() == pytest.approx((-1.0, 3.0))
        assert axis.get_xscale() == "log"
        assert axis.get_yscale() == "symlog"
        assert axis.get_xlabel() == "$ x $"
        assert axis.get_ylabel() == "$ y $"
        assert axis.get_title() == "Test 2"
        assert canvas._loc_legend[1] == 3


@pytest.mark.parametrize("orientation", ["v", "h"])
def test_canvas_draw_line_adds_a_single_reference_line(single_text_file: Path, orientation: str, show_plots) -> None:
    """Canvas.draw_line should add exactly one line for either supported orientation."""
    with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
        canvas.setup()
        before = len(canvas.axes[0].lines)

        canvas.draw_line(orientation, point=1.5, plot_n=0, color="red", linestyle="--", lw=2.0)

        line = canvas.axes[0].lines[-1]
        assert len(canvas.axes[0].lines) == before + 1
        assert line.get_color() == "red"
        assert line.get_linestyle() == "--"
        assert line.get_linewidth() == pytest.approx(2.0)


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expected_message"),
    [
        ("draw_line", {"orientation": "diagonal"}, "Invalid line type"),
        ("turn_scientific", {"axis": "z"}, "is not a valid axis"),
        ("set_ticks", {"axis": "z", "positions": (0.0, 1.0)}, "Invalid axis type"),
    ],
)
def test_canvas_rejects_invalid_axis_arguments(
    single_text_file: Path,
    method_name: str,
    kwargs: dict[str, object],
    expected_message: str,
) -> None:
    """Canvas helper methods should fail loudly on unsupported axis values."""
    with plt.Canvas(str(single_text_file), show=False) as canvas:
        canvas.setup()
        method = getattr(canvas, method_name)

        with pytest.raises(ValueError, match=expected_message):
            method(**kwargs)


def test_canvas_can_customize_ticks_and_scalebar(single_text_file: Path, show_plots) -> None:
    """Tick helpers and scalebars should update the selected subplot in place."""
    with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
        canvas.setup()
        canvas.set_ticks("x", (0.0, 1.0), labels=("left", "right"))
        canvas.set_ticks("y", (1.0, 2.0))
        canvas.add_scalebar(size=0.5, label="5 um")

        axis = canvas.axes[0]
        assert list(axis.get_xticks()) == []
        assert list(axis.get_yticks()) == []
        assert len(axis.artists) == 1


def test_canvas_saves_requested_figure(workspace: Path, single_text_file: Path) -> None:
    """Exiting the canvas context should save the figure when a filename is provided."""
    image_dir = workspace / "img"
    image_dir.mkdir(exist_ok=True)
    output_file = image_dir / "figure.png"

    with plt.Canvas(str(single_text_file), save="figure.png", show=False) as canvas:
        canvas.setup()

    assert output_file.exists()
