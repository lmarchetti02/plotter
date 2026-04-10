"""Tests for scatter plot validation and drawing."""

import numpy as np
import pytest

import plotter as plt


@pytest.mark.parametrize(
    ("x", "y", "xerr", "yerr", "expected_message"),
    [
        (np.array([0.0, 1.0]), np.array([1.0]), None, None, "x-values and y-values don't have the same dimensions"),
        (np.array([0.0, 1.0]), np.array([1.0, 2.0]), np.array([0.1]), None, "xy-values and xerr-values don't have the same dimensions"),
        (np.array([0.0, 1.0]), np.array([1.0, 2.0]), None, np.array([0.1]), "xy-values and yerr-values don't have the same dimensions"),
    ],
)
def test_scatter_plot_rejects_mismatched_input_shapes(
    x: np.ndarray,
    y: np.ndarray,
    xerr: np.ndarray | None,
    yerr: np.ndarray | None,
    expected_message: str,
) -> None:
    """ScatterPlot should validate data and uncertainty array lengths eagerly."""
    with pytest.raises(ValueError, match=expected_message):
        plt.ScatterPlot(x, y, yerr=yerr, xerr=xerr)


def test_scatter_plot_draw_uses_canvas_labels_and_updates_counters(single_text_file) -> None:
    """Drawing a scatter plot without an explicit label should consume the canvas metadata."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, 1.5, 2.0])

    with plt.Canvas(str(single_text_file), show=False) as canvas:
        canvas.setup()
        scatter = plt.ScatterPlot(x, y)

        scatter.draw(canvas)

        assert canvas.counters.scatter_plots[0] == 1
        assert len(canvas.axes[0].lines) == 1
        _, labels = canvas.axes[0].get_legend_handles_labels()
        assert labels == ["data"]
