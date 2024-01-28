import numpy as np


def denser(data: np.ndarray, ratio: int) -> np.ndarray:
    """
    This functions takes a numpy array and an integer `ratio` as input, and outputs
    another numpy array with more elements, hence a "denser" one.

    In particular:
        - it finds the minimum distance 'd' between two consecutive elements;
        - for every pair of consecutive elements:
            - it divides 'd' by `ratio` and rounds it to the nearest integer;
            - the result is the number of elements it adds in between the
              pair of elements.

    Parameters
    ---
    data: numpy.ndarray
        The array that is to be made denser.
    ratio: int
        See above.

    Example
    ---
    >>> data = np.array([1, 1.2, 3])
    >>> print(denser(data))
    [1.         1.1        1.2        1.30588235 1.41176471 1.51764706
    1.62352941 1.72941176 1.83529412 1.94117647 2.04705882 2.15294118
    2.25882353 2.36470588 2.47058824 2.57647059 2.68235294 2.78823529
    2.89411765 3.        ]
    """
    # find minimum distance
    minimum_dist = np.min(np.abs(data - np.append(data[1:], 0))[:-1])

    if minimum_dist == 0:
        return data

    # make denser
    increment = 0
    result = np.array(data, copy=True, dtype=np.float64)
    for i in range(len(data) - 1):
        n_elements = np.uint16(np.round(np.abs(data[i + 1] - data[i]) / minimum_dist, 0)) * ratio

        result = np.insert(
            result,
            i + increment + 1,
            np.linspace(data[i], data[i + 1], num=n_elements, endpoint=False)[1:],
        )

        increment += n_elements - 1

    return result
