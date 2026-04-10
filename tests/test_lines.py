"""Tests for line plot utilities and rendering behavior."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

import plotter as plt


@pytest.mark.parametrize(
    ("left", "right", "density", "message"),
    [
        (-0.1, 0.1, 2, "percentages of widening"),
        (0.1, -0.1, 2, "percentages of widening"),
        (0.1, 0.1, 0, "density cannot take values less than 1"),
    ],
)
def test_make_wider_rejects_invalid_arguments(left: float, right: float, density: int, message: str) -> None:
    """The interval widening helper should validate both bounds and density."""
    data = np.array([1.0, 2.0, 3.0])

    with pytest.raises(ValueError, match=message):
        plt.LinePlot._make_wider(data, left, right, density)


@pytest.mark.parametrize(
    ("data", "left", "right", "density", "expected"),
    [
        (np.array([10.0, 20.0]), 0.1, 0.2, 1, np.array([9.0, 10.0, 20.0, 22.0])),
        (np.array([10.0, 20.0]), 0.0, 0.2, 1, np.array([10.0, 20.0, 22.0])),
        (np.array([10.0, 20.0]), 0.1, 0.0, 1, np.array([9.0, 10.0, 20.0])),
    ],
)
def test_make_wider_extends_the_domain_as_expected(
    data: np.ndarray,
    left: float,
    right: float,
    density: int,
    expected: np.ndarray,
) -> None:
    """The widening helper should prepend or append boundary points as requested."""
    result = plt.LinePlot._make_wider(data, left, right, density)
    assert_allclose(result, expected)


def test_make_denser_handles_trivial_and_interpolated_cases() -> None:
    """The densifier should keep trivial inputs and interpolate missing points otherwise."""
    repeated = np.array([1.0, 2.0, 2.0, 4.0])
    assert np.array_equal(plt.LinePlot._make_denser(repeated, 2), repeated)

    sparse = np.array([0.0, 2.0])
    assert_allclose(plt.LinePlot._make_denser(sparse, 2), np.array([0.0, 1.0, 2.0]))


def test_line_plot_rejects_mismatched_explicit_y_values() -> None:
    """When y-values are provided directly, they must match the x grid size."""
    with pytest.raises(ValueError, match="must have the same dimension"):
        plt.LinePlot(np.array([0.0, 1.0]), np.array([1.0]))


def test_line_plot_computes_y_values_from_callable_and_wider_domain() -> None:
    """Callable-based plots should evaluate the function on the widened x-grid."""
    plot = plt.LinePlot(np.array([0.0, 1.0]), lambda x: x**2, wider=(0.5, 0.5), dens=2)

    assert plot.y is not None
    assert plot.x[0] == pytest.approx(-0.5)
    assert plot.x[-1] == pytest.approx(1.5)
    assert_allclose(plot.y, plot.x**2)


def test_line_plot_draw_supports_inverted_axes(single_text_file) -> None:
    """Drawing with `inverted=True` should swap the plotted x and y data."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 1.0, 4.0])

    with plt.Canvas(str(single_text_file), show=False) as canvas:
        canvas.setup()
        plot = plt.LinePlot(x, y)

        plot.draw(canvas, inverted=True)

        line = canvas.axes[0].lines[0]
        assert canvas.counters.line_plots[0] == 1
        assert_allclose(line.get_xdata(), y)  # type: ignore
        assert_allclose(line.get_ydata(), x)  # type: ignore
        assert line.get_label() == "line"
