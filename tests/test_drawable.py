"""Tests for the shared Drawable base class."""

import numpy as np
import pytest

import plotter as plt


def make_drawables() -> tuple[plt.Drawable, ...]:
    """Build one small instance of every concrete drawable."""
    x = np.array([0.0, 1.0])
    y = np.array([1.0, 2.0])
    image = np.array([[1.0, 2.0], [3.0, 4.0]])

    return (
        plt.ScatterPlot(x, y),
        plt.LinePlot(x, y),
        plt.FunctionPlot(x, np.sin),
        plt.BarChart(x, y),
        plt.BoxPlot([x, y]),
        plt.RawHist(x),
        plt.BinnedHist(np.array([1.0]), np.array([0.0, 1.0])),
        plt.RawHist2D(x, y, 2),
        plt.BinnedHist2D(np.array([[1.0]]), np.array([0.0, 1.0]), np.array([0.0, 1.0])),
        plt.Image(image),
    )


class TestDrawable:
    """Tests for `Drawable`."""

    def test_is_exported_at_package_level(self) -> None:
        """The Drawable base class should be part of the public package API."""
        assert plt.Drawable is not None

    def test_all_supported_plot_types_are_drawables(self) -> None:
        """Every concrete drawable object should inherit from the shared base class."""
        assert all(isinstance(drawable, plt.Drawable) for drawable in make_drawables())


class TestDraw:
    """Tests for `Drawable.draw`, across every concrete drawable."""

    @pytest.mark.parametrize("drawable", make_drawables(), ids=lambda drawable: type(drawable).__name__)
    def test_rejects_unknown_keyword_arguments(self, workspace, drawable: plt.Drawable) -> None:
        """A misspelled or unsupported kwarg should raise, naming it, before anything is drawn."""
        with plt.Canvas(show=False) as canvas:
            with pytest.raises(TypeError, match=r"unexpected keyword argument\(s\) \['colour'\]"):
                drawable.draw(canvas, colour="red")

            assert not canvas.axes[0].has_data()

    @pytest.mark.parametrize("drawable", make_drawables(), ids=lambda drawable: type(drawable).__name__)
    @pytest.mark.parametrize("plot_n", [2, -1, True])
    def test_rejects_an_out_of_range_plot_n(self, workspace, drawable: plt.Drawable, plot_n: int) -> None:
        """'plot_n' must index an existing subplot: no IndexError later, no counting from the end."""
        with plt.Canvas(rows_cols=(1, 2), show=False) as canvas:
            with pytest.raises(ValueError, match="'plot_n' must be an integer between 0 and 1"):
                drawable.draw(canvas, plot_n=plot_n)

            assert not any(axes.has_data() for axes in canvas.axes)


class TestGetLabelNames:
    """Tests for `Drawable.get_label_names`."""

    def test_lists_all_supported_label_groups(self) -> None:
        """The shared drawable registry should define every supported label collection once."""
        assert plt.Drawable.get_label_names() == (
            "scatter_plots",
            "line_plots",
            "bar_charts",
            "box_plots",
            "histograms",
        )
