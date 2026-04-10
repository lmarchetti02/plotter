"""Tests for bar chart validation and drawing."""

import numpy as np
import pytest

import plotter as plt


@pytest.mark.parametrize(
    ("x", "heights", "yerr", "message"),
    [
        (
            np.array([0.0, 1.0]),
            np.array([1.0]),
            None,
            "x-values and heights must have the same dimensions",
        ),
        (
            np.array([0.0, 1.0]),
            np.array([1.0, 2.0]),
            np.array([0.1]),
            "heights and yerr-values don't have the same dimensions",
        ),
    ],
)
def test_bar_chart_rejects_mismatched_input_shapes(
    x: np.ndarray,
    heights: np.ndarray,
    yerr: np.ndarray | None,
    message: str,
) -> None:
    """BarChart should validate bar positions, heights, and error values."""
    with pytest.raises(ValueError, match=message):
        plt.BarChart(x, heights, yerr=yerr)


def test_bar_chart_draw_uses_canvas_labels_and_updates_counters(single_text_file) -> None:
    """Drawing a bar chart should use JSON labels when no explicit label is passed."""
    x = np.array([0.0, 1.0, 2.0])
    heights = np.array([1.0, 3.0, 2.0])
    yerr = np.array([0.2, 0.1, 0.3])

    with plt.Canvas(str(single_text_file), show=False) as canvas:
        canvas.setup()
        bars = plt.BarChart(x, heights, yerr=yerr)

        bars.draw(canvas)

        assert canvas.counters.bar_charts[0] == 1
        assert len(canvas.axes[0].patches) == 3
        assert canvas.axes[0].patches[0].get_height() == pytest.approx(1.0)
        _, labels = canvas.axes[0].get_legend_handles_labels()
        assert labels == ["bars"]


def test_bar_chart_draw_respects_styling_arguments(single_text_file) -> None:
    """BarChart should forward width and edge styling to matplotlib."""
    x = np.array([0.0, 1.0])
    heights = np.array([2.0, 4.0])

    with plt.Canvas(str(single_text_file), show=True) as canvas:
        canvas.setup()
        bars = plt.BarChart(x, heights)

        bars.draw(canvas, width=0.4, lw=1.5, edgecolor="black")

        patch = canvas.axes[0].patches[0]
        assert patch.get_width() == pytest.approx(0.4)
        assert patch.get_linewidth() == pytest.approx(1.5)
