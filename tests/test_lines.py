import numpy as np
import pytest
from numpy.testing import assert_allclose

import plotter as plt


@pytest.mark.parametrize(
    "left, right, density",
    [
        (-0.1, 0.1, 2),  # left negative
        (0.1, -0.1, 2),  # right negative
        (0.1, 0.1, 0),  # density <0
    ],
)
def test_make_wider_exceptions(left, right, density):
    data = np.array([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        plt.LinePlot._make_wider(data, left, right, density)


def test_make_wider_bounds():
    data = np.array([10.0, 20.0])

    result = plt.LinePlot._make_wider(data, 0.1, 0.2, 1)
    expected = np.array([9.0, 10.0, 20.0, 22.0])
    assert_allclose(result, expected)

    result = plt.LinePlot._make_wider(data, 0, 0.2, 1)
    expected = np.array([10.0, 20.0, 22.0])
    assert_allclose(result, expected)

    result = plt.LinePlot._make_wider(data, 0.1, 0, 1)
    expected = np.array([9.0, 10.0, 20.0])
    assert_allclose(result, expected)


def test_make_denser_trivial():
    data = np.array([1.0, 2.0, 2.0, 4.0])

    result = plt.LinePlot._make_denser(data, 2)
    assert np.array_equal(data, result)

    data = np.delete(data, 1)
    result = plt.LinePlot._make_denser(data, 1)
    assert np.array_equal(data, result)


def test_make_wider():
    data = np.array([0.0, 2.0])

    result = plt.LinePlot._make_denser(data, 2)
    expected = np.array([0.0, 1.0, 2.0])

    assert_allclose(result, expected)


def test_lines(tmp_path):
    text_file = str(tmp_path / "scatter")
    with plt.Canvas(text_file) as canvas:
        canvas.setup()

        x = np.linspace(0.0, 1.0, 5)

        colors = plt.get_colors(3)
        plt.LinePlot(x, lambda x: x).draw(canvas, label="$ f(x) = x $", color=colors[0])
        plt.LinePlot(x, lambda x: x**2, dens=4).draw(canvas, label="$ f(x) = x^2 $", color=colors[1])
        plt.LinePlot(x, lambda x: x**3, dens=6).draw(canvas, label="$ f(x) = x^3 $", color=colors[2])
