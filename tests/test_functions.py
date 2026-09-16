"""Tests for function plot utilities and rendering behavior."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

import plotter as plt


class TestMakeWider:
    """Tests for `FunctionPlot._make_wider`."""

    @pytest.mark.parametrize(
        ("left", "right", "density", "message"),
        [
            (-0.1, 0.1, 2, "percentages of widening"),
            (0.1, -0.1, 2, "percentages of widening"),
            (0.1, 0.1, 0, "density cannot take values less than 1"),
        ],
    )
    def test_rejects_invalid_arguments(self, left: float, right: float, density: int, message: str) -> None:
        """The interval widening helper should validate both bounds and density."""
        data = np.array([1.0, 2.0, 3.0])

        with pytest.raises(ValueError, match=message):
            plt.FunctionPlot._make_wider(data, left, right, density)

    @pytest.mark.parametrize(
        ("data", "left", "right", "density", "expected"),
        [
            (np.array([10.0, 20.0]), 0.1, 0.2, 1, np.array([9.0, 10.0, 20.0, 22.0])),
            (np.array([10.0, 20.0]), 0.0, 0.2, 1, np.array([10.0, 20.0, 22.0])),
            (np.array([10.0, 20.0]), 0.1, 0.0, 1, np.array([9.0, 10.0, 20.0])),
        ],
    )
    def test_extends_the_domain_as_expected(
        self,
        data: np.ndarray,
        left: float,
        right: float,
        density: int,
        expected: np.ndarray,
    ) -> None:
        """The widening helper should prepend or append boundary points as requested."""
        result = plt.FunctionPlot._make_wider(data, left, right, density)
        assert_allclose(result, expected)


class TestMakeDenser:
    """Tests for `FunctionPlot._make_denser`."""

    def test_handles_trivial_and_interpolated_cases(self) -> None:
        """The densifier should keep trivial inputs and interpolate missing points otherwise."""
        repeated = np.array([1.0, 2.0, 2.0, 4.0])
        assert np.array_equal(plt.FunctionPlot._make_denser(repeated, 2), repeated)

        sparse = np.array([0.0, 2.0])
        assert_allclose(plt.FunctionPlot._make_denser(sparse, 2), np.array([0.0, 1.0, 2.0]))


class TestFunctionPlot:
    """Tests for `FunctionPlot`."""

    def test_computes_y_values_from_callable_and_wider_domain(self) -> None:
        """Callable-based plots should evaluate the function on the widened x-grid."""
        plot = plt.FunctionPlot(np.array([0.0, 1.0]), lambda x: x**2, wider=(0.5, 0.5), dens=2)

        assert plot.y is not None
        assert plot.x[0] == pytest.approx(-0.5)
        assert plot.x[-1] == pytest.approx(1.5)
        assert_allclose(plot.y, plot.x**2)


class TestDraw:
    """Tests for `FunctionPlot.draw`."""

    def test_evaluates_and_plots_the_function(self, single_text_file, show_plots) -> None:
        """Drawing should plot `f` evaluated on `x`, sharing the `line_plots` label family."""
        x = np.array([0.0, 1.0, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.FunctionPlot(x, np.sin).draw(canvas)

            line = canvas.axes[0].lines[0]
            assert canvas.counters.line_plots[0] == 1
            assert_allclose(line.get_xdata(), x)  # type: ignore
            assert_allclose(line.get_ydata(), np.sin(x))  # type: ignore
            assert line.get_label() == "line"
