from logging import getLogger
from typing import Any

import numpy as np
from matplotlib.colors import TABLEAU_COLORS, LinearSegmentedColormap

from .constants import NArray1D

logger = getLogger(__name__)


def get_colors(length: int, gradient: tuple[str, str] | None = None) -> list[str]:
    """
    Generate a list of colors for the plots.

    Args:
        length (int): The length of the list.
        gradient (tuple[str, str], optional): The initial and final colors of the
            gradient (see plotter/utils/info for a list of available colors).
            Defaults to None, which results in a list of random colors.

    Returns:
        list[str]: The list of colors.
    """
    logger.info("Called 'get_colors' function.")

    colors = list(TABLEAU_COLORS.keys())
    rng = np.random.default_rng()

    if gradient:
        cmap = LinearSegmentedColormap.from_list("cmap", gradient, length)
        return cmap(np.linspace(0, 1, length)).tolist()

    if length <= len(colors):
        return rng.choice(colors, length, replace=False).tolist()
    else:
        return rng.choice(colors, length, replace=True).tolist()


def stack_bottoms(heights: list[NArray1D[Any]]) -> list[NArray1D[Any]]:
    """
    Computes the cumulative starting offset ("bottom") for each series in a stack of bar charts.

    Args:
        heights (list[NArray1D[Any]]): One array of bar heights per series, in
            stacking order (bottom to top). All arrays must have the same length.

    Raises:
        ValueError: If `heights` is empty.
        ValueError: If the arrays in `heights` don't all have the same length.

    Returns:
        list[NArray1D[Any]]: One array of cumulative offsets per series, the same
            shape as `heights`, suitable for `BarChart.draw`'s `bottom` keyword
            argument -- the first entry is all zeros, and each subsequent entry is
            the running total of every series stacked below it.
    """
    logger.info("Called 'stack_bottoms' function.")

    if not heights:
        raise ValueError("heights must contain at least one series")

    if len({len(series) for series in heights}) > 1:
        raise ValueError("all series in heights must have the same length")

    cumulative = np.cumsum(heights, axis=0)
    return [np.zeros_like(heights[0]), *cumulative[:-1]]
