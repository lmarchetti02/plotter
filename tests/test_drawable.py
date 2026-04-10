import numpy as np

import plotter as plt


def test_drawable_export():
    assert plt.Drawable is not None


def test_drawable_inheritance():
    x = np.array([0.0, 1.0])
    y = np.array([1.0, 2.0])
    image = np.array([[1.0, 2.0], [3.0, 4.0]])

    drawables = (
        plt.ScatterPlot(x, y),
        plt.LinePlot(x, y),
        plt.Hist(x),
        plt.Hist2D(x, y, 2),
        plt.Image(image),
    )

    for drawable in drawables:
        assert isinstance(drawable, plt.Drawable)
