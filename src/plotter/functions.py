import os
import json
import pathlib
import numpy as np
import logging.config
import logging.handlers

logger = logging.getLogger(__name__)


def _make_denser(data: np.ndarray, density: int) -> np.ndarray:
    """
    This functions takes a numpy array and an integer `ratio` as input, and outputs
    another numpy array with more elements, hence a "denser" one.

    In particular:
        - it finds the minimum distance 'd' between two consecutive elements;
        - for every pair of consecutive elements:
            - it divides the their distance by 'd', it multiplies the result
              by `density` and rounds it to the nearest integer;
            - the result is the number of elements it adds in between the
              pair of elements.

    Parameters
    ---
    data: numpy.ndarray
        The array that is to be made denser.
    density: int
        See above.

    Example
    ---
    >>> data = np.array([1, 1.2, 3])
    >>> print(_make_denser(data))
    [1.         1.1        1.2        1.30588235 1.41176471 1.51764706
    1.62352941 1.72941176 1.83529412 1.94117647 2.04705882 2.15294118
    2.25882353 2.36470588 2.47058824 2.57647059 2.68235294 2.78823529
    2.89411765 3.        ]
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
        n_elements = np.uint16(np.round(np.abs(data[i + 1] - data[i]) / minimum_dist, 0)) * density

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
    This function takes a 1D array and makes it longer by an amount specified
    by `left` and `right`.

    It also makes the input array denser, by make use of the internal
    function `_make_denser()`.

    Parameters
    ---
    data: numpy.ndarray
        The input array.
    left: float
        The percentage to which the array is to be widened
        to the left.
    right: float
        The percentage to which the array is to be widened
        to the right.
    density: int
        The `_make_denser()` density.

    Example
    ---
    >>> data = np.array([1, 1.2, 3])
    >>> print(make_wider(data, 0.2, 0.1))
    [0.6        0.7        0.8        0.9        1.         1.1
    1.2        1.30588235 1.41176471 1.51764706 1.62352941 1.72941176
    1.83529412 1.94117647 2.04705882 2.15294118 2.25882353 2.36470588
    2.47058824 2.57647059 2.68235294 2.78823529 2.89411765 3.        ]
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
    This functions sets up the loggers that will
    be used throughout the library.
    """
    config_file = pathlib.Path(os.getcwd() + "/plotter/utils/log_config.json")

    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)


if __name__ == "__main__":
    pass
