"""Tests for line plot utilities and rendering behavior."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

import plotter as plt


class TestLinePlot:
    """Tests for `LinePlot`."""

    def test_rejects_mismatched_dimensions(self) -> None:
        """x and y must have the same dimension."""
        with pytest.raises(ValueError, match="must have the same dimension"):
            plt.LinePlot(np.array([0.0, 1.0]), np.array([1.0]))


class TestFromY:
    """Tests for `LinePlot.from_y`."""

    def test_uses_an_implicit_index_range_for_x(self) -> None:
        """`from_y` should fill in x with an index range matching y's shape."""
        y = np.array([10.0, 20.0, 30.0])

        plot = plt.LinePlot.from_y(y)

        assert_allclose(plot.x, np.arange(len(y)))
        assert_allclose(plot.y, y)


class TestDraw:
    """Tests for `LinePlot.draw`."""

    def test_supports_inverted_axes(self, single_text_file, show_plots) -> None:
        """Drawing with `inverted=True` should swap the plotted x and y data."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 1.0, 4.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plot = plt.LinePlot(x, y)

            plot.draw(canvas, inverted=True)

            line = canvas.axes[0].lines[0]
            assert canvas.counters.line_plots[0] == 1
            assert_allclose(line.get_xdata(), y)  # type: ignore
            assert_allclose(line.get_ydata(), x)  # type: ignore
            assert line.get_label() == "line"

    def test_alpha_defaults_to_opaque_and_is_overridable(self, single_text_file, show_plots) -> None:
        """The line should be fully opaque unless an `alpha` kwarg is given."""
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 1.0, 4.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.LinePlot(x, y).draw(canvas)
            assert canvas.axes[0].lines[0].get_alpha() == 1.0

            plt.LinePlot(x, y).draw(canvas, label="more line", alpha=0.3)
            assert canvas.axes[0].lines[1].get_alpha() == pytest.approx(0.3)
