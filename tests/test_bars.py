"""Tests for bar chart validation and drawing."""

import numpy as np
import pytest
from matplotlib.colors import to_rgba

import plotter as plt


class TestBarChart:
    """Tests for `BarChart`."""

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
    def test_rejects_mismatched_input_shapes(
        self,
        x: np.ndarray,
        heights: np.ndarray,
        yerr: np.ndarray | None,
        message: str,
    ) -> None:
        """BarChart should validate bar positions, heights, and error values."""
        with pytest.raises(ValueError, match=message):
            plt.BarChart(x, heights, yerr=yerr)


class TestDraw:
    """Tests for `BarChart.draw`."""

    def test_uses_canvas_labels_and_updates_counters(self, single_text_file, show_plots) -> None:
        """Drawing a bar chart should use JSON labels when no explicit label is passed."""
        x = np.array([0.0, 1.0, 2.0])
        heights = np.array([1.0, 3.0, 2.0])
        yerr = np.array([0.2, 0.1, 0.3])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights, yerr=yerr)

            bars.draw(canvas)

            assert canvas.counters.bar_charts[0] == 1
            assert len(canvas.axes[0].patches) == 3
            assert canvas.axes[0].patches[0].get_height() == pytest.approx(1.0)  # type: ignore
            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["bars"]

    def test_respects_styling_arguments(self, single_text_file, show_plots) -> None:
        """BarChart should forward width and edge styling to matplotlib."""
        x = np.array([0.0, 1.0])
        heights = np.array([2.0, 4.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights)

            bars.draw(canvas, width=0.4, lw=1.5, edgecolor="black")

            patch = canvas.axes[0].patches[0]
            assert patch.get_width() == pytest.approx(0.4)  # type: ignore
            assert patch.get_linewidth() == pytest.approx(1.5)

    def test_bottom_offsets_the_bars(self, single_text_file, show_plots) -> None:
        """`bottom` should be forwarded to `Axes.bar`, offsetting each bar's base."""
        x = np.array([0.0, 1.0])
        heights = np.array([2.0, 4.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights)

            bars.draw(canvas, bottom=1.5)

            for patch in canvas.axes[0].patches:
                assert patch.get_y() == pytest.approx(1.5)  # type: ignore

    def test_stacking_two_bar_charts_on_the_same_subplot(self, single_text_file, show_plots) -> None:
        """Drawing a second `BarChart` with `bottom` set to the first's heights should stack them."""
        x = np.array([0.0, 1.0, 2.0])
        bottom_heights = np.array([1.0, 3.0, 2.0])
        top_heights = np.array([2.0, 1.0, 4.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            plt.BarChart(x, bottom_heights).draw(canvas, label="bottom series")
            plt.BarChart(x, top_heights).draw(canvas, bottom=bottom_heights, label="top series")

            assert canvas.counters.bar_charts[0] == 2

            bottom_patches = canvas.axes[0].patches[:3]
            top_patches = canvas.axes[0].patches[3:]
            for bottom_patch, top_patch in zip(bottom_patches, top_patches):
                assert top_patch.get_y() == pytest.approx(bottom_patch.get_height())  # type: ignore

            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["bottom series", "top series"]

    def test_error_bar_styling_uses_the_same_kwarg_names_as_scatter_plot(self, single_text_file, show_plots) -> None:
        """`err_color`/`err_width`/`err_capsize` style the error bars, matching `ScatterPlot`'s own kwargs."""
        x = np.array([0.0, 1.0, 2.0])
        heights = np.array([1.0, 3.0, 2.0])
        yerr = np.array([0.2, 0.1, 0.3])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights, yerr=yerr)

            bars.draw(canvas, err_color="red", err_width=3.0, err_capsize=7.0)

            container = canvas.axes[0].containers[0]
            barlinecol = container.lines[2][0]
            capline = container.lines[1][0]
            assert to_rgba(barlinecol.get_color()[0]) == to_rgba("red")
            assert barlinecol.get_linewidth()[0] == pytest.approx(3.0)
            assert capline.get_markersize() == pytest.approx(14.0)  # 2 * err_capsize

    def test_bar_labels_defaults_to_no_text(self, single_text_file, show_plots) -> None:
        """By default, no text is written on top of the bars."""
        x = np.array([0.0, 1.0, 2.0])
        heights = np.array([1.0, 3.0, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights)

            bars.draw(canvas)

            assert len(canvas.axes[0].texts) == 0

    def test_bar_labels_true_shows_formatted_heights(self, single_text_file, show_plots) -> None:
        """`bar_labels=True` writes each bar's height above it, using matplotlib's default format."""
        x = np.array([0.0, 1.0, 2.0])
        heights = np.array([1.0, 3.0, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights)

            bars.draw(canvas, bar_labels=True)

            texts = [text.get_text() for text in canvas.axes[0].texts]
            assert texts == ["1", "3", "2"]

    def test_bar_labels_dict_passes_through_to_bar_label(self, single_text_file, show_plots) -> None:
        """A `bar_labels` dict is forwarded straight through to `Axes.bar_label`, e.g. for custom text."""
        x = np.array([0.0, 1.0, 2.0])
        heights = np.array([1.0, 3.0, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            bars = plt.BarChart(x, heights)

            bars.draw(canvas, bar_labels={"labels": ["a", "b", "c"]})

            texts = [text.get_text() for text in canvas.axes[0].texts]
            assert texts == ["a", "b", "c"]
