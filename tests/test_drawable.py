"""Tests for the shared Drawable base class."""

import numpy as np

import plotter as plt


def test_drawable_is_exported_at_package_level() -> None:
    """The Drawable base class should be part of the public package API."""
    assert plt.Drawable is not None


def test_all_supported_plot_types_are_drawables() -> None:
    """Every concrete drawable object should inherit from the shared base class."""
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

    assert all(isinstance(drawable, plt.Drawable) for drawable in drawables)
