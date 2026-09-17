"""Tests for scatter plot validation and drawing."""

import numpy as np
import pytest
from matplotlib.colors import to_rgba
from numpy.testing import assert_allclose

import plotter as plt


class TestScatterPlot:
    """Tests for `ScatterPlot`."""

    @pytest.mark.parametrize(
        ("x", "y", "xerr", "yerr", "expected_message"),
        [
            (np.array([0.0, 1.0]), np.array([1.0]), None, None, "x-values and y-values don't have the same dimensions"),
            (np.array([0.0, 1.0]), np.array([1.0, 2.0]), np.array([0.1]), None, "xy-values and xerr-values don't have the same dimensions"),
            (np.array([0.0, 1.0]), np.array([1.0, 2.0]), None, np.array([0.1]), "xy-values and yerr-values don't have the same dimensions"),
        ],
    )
    def test_rejects_mismatched_input_shapes(
        self,
        x: np.ndarray,
        y: np.ndarray,
        xerr: np.ndarray | None,
        yerr: np.ndarray | None,
        expected_message: str,
    ) -> None:
        """ScatterPlot should validate data and uncertainty array lengths eagerly."""
        with pytest.raises(ValueError, match=expected_message):
            plt.ScatterPlot(x, y, yerr=yerr, xerr=xerr)


class TestFromY:
    """Tests for `ScatterPlot.from_y`."""

    def test_uses_an_implicit_index_range_for_x(self) -> None:
        """`from_y` should fill in x with an index range matching y's shape."""
        y = np.array([10.0, 20.0, 30.0])

        scatter = plt.ScatterPlot.from_y(y)

        assert_allclose(scatter.x, np.arange(len(y)))
        assert_allclose(scatter.y, y)

    def test_forwards_keyword_arguments_to_the_constructor(self) -> None:
        """`from_y` should forward kwargs like `yerr` to `ScatterPlot`'s constructor."""
        y = np.array([10.0, 20.0, 30.0])
        yerr = np.array([1.0, 2.0, 1.0])

        scatter = plt.ScatterPlot.from_y(y, yerr=yerr)

        assert_allclose(scatter.yerr, yerr)


class TestDraw:
    """Tests for `ScatterPlot.draw`."""

    def test_uses_canvas_labels_and_updates_counters(self, single_text_file, show_plots) -> None:
        """Drawing a scatter plot without an explicit label should consume the canvas metadata."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            scatter = plt.ScatterPlot(x, y)

            scatter.draw(canvas)

            assert canvas.counters.scatter_plots[0] == 1
            assert len(canvas.axes[0].lines) == 1
            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["data"]

    def test_alpha_defaults_to_opaque_and_is_overridable(self, single_text_file, show_plots) -> None:
        """The scatter points should be fully opaque unless an `alpha` kwarg is given."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(canvas)
            assert canvas.axes[0].lines[0].get_alpha() == 1.0

            plt.ScatterPlot(x, y).draw(canvas, label="more data", alpha=0.4)
            assert canvas.axes[0].lines[1].get_alpha() == pytest.approx(0.4)

    def test_error_bar_styling_uses_the_same_kwarg_names_as_bar_chart(self, single_text_file, show_plots) -> None:
        """`err_color`/`err_width`/`err_capsize` style the error bars, matching `BarChart`'s own kwargs."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])
        yerr = np.array([0.1, 0.2, 0.1])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            scatter = plt.ScatterPlot(x, y, yerr=yerr)

            scatter.draw(canvas, err_color="red", err_width=3.0, err_capsize=7.0)

            container = canvas.axes[0].containers[0]
            barlinecol = container.lines[2][0]
            capline = container.lines[1][0]
            assert to_rgba(barlinecol.get_color()[0]) == to_rgba("red")
            assert barlinecol.get_linewidth()[0] == pytest.approx(3.0)
            assert capline.get_markersize() == pytest.approx(14.0)  # 2 * err_capsize

    def test_no_line_by_default(self, single_text_file, show_plots) -> None:
        """Without `line=True`, only the markers artist should be drawn."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(canvas)

            assert len(canvas.axes[0].lines) == 1

    def test_draws_a_connecting_line_when_requested(self, single_text_file, show_plots) -> None:
        """`line=True` should add a second `Line2D` connecting the points in order."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(canvas, line=True)

            assert len(canvas.axes[0].lines) == 2
            connecting_line = canvas.axes[0].lines[1]
            assert_allclose(connecting_line.get_xdata(), x)
            assert_allclose(connecting_line.get_ydata(), y)

    def test_line_width_and_style_have_their_own_defaults(self, single_text_file, show_plots) -> None:
        """The connecting line's width/style default to 1.5/"-", independent of the markers."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(canvas, line=True)

            connecting_line = canvas.axes[0].lines[1]
            assert connecting_line.get_linewidth() == pytest.approx(1.5)
            assert connecting_line.get_linestyle() == "-"

    def test_line_color_and_alpha_default_to_the_points_style(self, single_text_file, show_plots) -> None:
        """Without an explicit `line_color`/`line_alpha`, the line matches the points' own `color`/`alpha`."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(canvas, line=True)

            connecting_line = canvas.axes[0].lines[1]
            assert to_rgba(connecting_line.get_color()) == to_rgba("firebrick")
            assert connecting_line.get_alpha() == pytest.approx(1.0)

            plt.ScatterPlot(x, y).draw(canvas, label="more data", line=True, color="blue", alpha=0.3)

            connecting_line = canvas.axes[0].lines[3]
            assert to_rgba(connecting_line.get_color()) == to_rgba("blue")
            assert connecting_line.get_alpha() == pytest.approx(0.3)

    def test_line_styling_uses_dedicated_kwargs(self, single_text_file, show_plots) -> None:
        """`line_color`/`line_width`/`line_style`/`line_alpha` style the connecting line independently of the markers."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(
                canvas,
                line=True,
                line_color="blue",
                line_width=3.0,
                line_style="--",
                line_alpha=0.5,
            )

            connecting_line = canvas.axes[0].lines[1]
            assert to_rgba(connecting_line.get_color()) == to_rgba("blue")
            assert connecting_line.get_linewidth() == pytest.approx(3.0)
            assert connecting_line.get_linestyle() == "--"
            assert connecting_line.get_alpha() == pytest.approx(0.5)

    def test_line_is_excluded_from_the_legend(self, single_text_file, show_plots) -> None:
        """The connecting line should not add its own legend entry."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.5, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.ScatterPlot(x, y).draw(canvas, line=True)

            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["data"]
