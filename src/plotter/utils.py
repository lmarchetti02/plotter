import os
import json
import pathlib
import numpy as np
import logging.config
import logging.handlers
from typing import Optional
import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)

__all__ = ["get_colors"]


def _make_denser(data: np.ndarray, density: int) -> np.ndarray:
    """
    Creates a "denser" numpy array by adding elements between existing ones.

    This function finds the minimum distance 'd' between consecutive elements.
    For each pair of consecutive elements, it inserts new points, with the number
    of points determined by the ratio of the pair's distance to `d`, multiplied
    by `density` and rounded to the nearest integer.

    Args:
        data (np.ndarray): The 1D numpy array to be made denser.
        density (int): A scaling factor for the number of elements to add
            between existing elements. A value of 1 returns the original array.

    Returns:
        np.ndarray: A new 1D numpy array with a higher density of elements.

    Example:
        >>> data = np.array([1, 1.2, 3])
        >>> _make_denser(data, 1)
        array([1. , 1.2, 3. ])
        >>> # A higher density value inserts more points
        >>> denser_data = _make_denser(data, 10)
        >>> print(len(denser_data))
        20
    """
    logger.info("Called 'denser()' function")

    # trivial case
    if density == 1:
        return data

    # find minimum distance
    minimum_dist = np.min(np.abs(data - np.append(data[1:], 0))[:-1])
    logger.debug(f"Minimum distance: {minimum_dist}")

    if minimum_dist == 0:
        logger.warning("There are at least two repeated consecutive elements")
        return data

    # make denser
    increment = 0
    result = np.array(data, copy=True, dtype=np.float64)
    for i in range(len(data) - 1):
        n_elements = np.uint(np.round(np.abs(data[i + 1] - data[i]) / minimum_dist, 0)) * density

        result = np.insert(
            result,
            i + increment + 1,
            np.linspace(data[i], data[i + 1], num=n_elements, endpoint=False)[1:],
        )

        increment += n_elements - 1

    logger.debug(f"Final array:\n{result}")

    return result


def make_wider(data: np.ndarray, left: float, right: float, density: int) -> np.ndarray:
    """
    Makes a 1D array wider by a specified percentage and increases its density.

    The function extends the array's range by a percentage of its total span,
    as specified by `left` and `right`. It then calls `_make_denser()` to
    interpolate new data points and increase the array's density.

    Args:
        data (np.ndarray): The 1D input array.
        left (float): The percentage to widen the array to the left (e.g., 0.2 for 20%).
        right (float): The percentage to widen the array to the right (e.g., 0.1 for 10%).
        density (int): The density factor to pass to the `_make_denser()` function.

    Returns:
        np.ndarray: The new, wider and denser array.

    Raises:
        ValueError: If `density` is less than 1.
        ValueError: If `left` or `right` are less than 0.

    Example:
        >>> data = np.array([1, 1.2, 3])
        >>> make_wider(data, 0.2, 0.1, 10)
        array([0.6, 0.7, 0.8, 0.9, 1. , 1.1, 1.2, ..., 2.9, 3. ])
    """

    logger.info("Called 'widen_interval()'")

    if density < 1:
        raise ValueError("The density cannot take values less than 1")

    if left < 0 or right < 0:
        raise ValueError("The percentages of widening cannot take values less than 0")

    logger.debug(f"Initial dataset:\n {data}")

    m = np.min(data)
    M = np.max(data)
    delta = M - m

    wider_data = np.array(data, copy=True, dtype=np.float64)
    if left != 0:
        wider_data = np.insert(wider_data, 0, m - left * delta)

    if right != 0:
        wider_data = wider_data[::-1]
        wider_data = np.insert(wider_data, 0, M + right * delta)
        wider_data = wider_data[::-1]

    logger.debug(f"Dataset to be made denser:\n {wider_data}")

    return _make_denser(wider_data, density)


def setup_logging() -> None:
    """
    Sets up the logging configuration for the library.

    This function reads a logging configuration from a JSON file and applies it
    to set up the loggers used throughout the module.
    """
    config_file = pathlib.Path(os.getcwd() + "/plotter/utils/log_config.json")

    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)


def get_colors(length: int, gradient: Optional[tuple[str, str]] = None) -> list[str]:
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
    COLORS = list(mcolors.TABLEAU_COLORS.keys())

    if gradient:
        cmap = mcolors.LinearSegmentedColormap.from_list("cmap", gradient, length)
        return cmap(np.linspace(0, 1, length))

    if length <= len(COLORS):
        return np.random.choice(COLORS, length, replace=False)
    else:
        return np.random.choice(COLORS, length, replace=True)


if __name__ == "__main__":
    pass
