from logging import getLogger

import numpy as np
from matplotlib.colors import TABLEAU_COLORS, LinearSegmentedColormap


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
    logger = getLogger(__name__)
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
