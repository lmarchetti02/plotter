from logging import getLogger
from typing import Any, Callable, ClassVar

import numpy as np
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .canvas import Canvas
from .drawable import Drawable
from .helpers import NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class LinePlot(Drawable):
    """
    Class for creating a 1D function plot to be drawn on a canvas.

    Attributes:
        x (NArray1D[Any]): The values of the independent variable.
        f (Callable[[NArray1D[Any]], NArray1D[Any]] | NArray1D[Any]): The function that
            defines the plot, or an array of y-values.
        wider (tuple[float, float], optional): The percentages (left, right) to which
            the domain of the function `f` is to be widened. Defaults to `(0, 0)`.
        dens (int, optional): The density factor to be passed to `make_wider()`.
            Defaults to 1.

    Raises:
        ValueError: If x and f as an array do not have the same dimensions.
    """

    label_name: ClassVar[str] = "line_plots"

    x: NArray1D[Any]
    f: Callable[[NArray1D[Any]], NArray1D[Any]] | NArray1D[Any]
    wider: tuple[float, float] = (0, 0)
    dens: int = 1

    y: NArray1D[Any] | None = Field(init=True, default=None)

    def __post_init__(self) -> None:
        """Makes x-grid denser if necessary."""

        if isinstance(self.f, np.ndarray):
            if len(self.x) != len(self.f):
                raise ValueError("x-values and y-values must have the same dimension")
            self.y = self.f
        else:
            self.x = self._make_wider(self.x, *self.wider, self.dens)
            self.y = self.f(self.x)

    def draw(self, canvas: Canvas, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the plot on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the plot on.
            plot_n (int, optional): The index of the subplot. Defaults to 0.
            label (str, optional): The label for the plot in the legend.
                Defaults to `None`.

        Keyword Arguments:
            color (str): The Matplotlib color of the plot. Defaults to "darkgreen".
            lw (float): The line width. Defaults to 1.5.
            style (str): The line style. Defaults to `"-"`.
            inverted (bool): If `True`, plots the inverse function.
                Defaults to `False`.
        """

        # exchange x and y
        if kwargs.get("inverted", False):
            self.x, self.y = self.y, self.x

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            self.label_name,
            logger,
            "No label for the plot in the json file.",
        )

        canvas.axes[plot_n].plot(
            self.x,
            self.y,
            color=kwargs.get("color", "darkgreen"),
            zorder=1,
            lw=kwargs.get("lw", 1.5),
            ls=kwargs.get("style", "-"),
            label=label,
        )
        logger.debug(f"Plot {n} drawn")

        getattr(canvas.counters, self.label_name)[plot_n] += 1

    @staticmethod
    def _make_wider(data: NArray1D[Any], left: float, right: float, density: int) -> NArray1D[Any]:
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
        """
        logger.info("Called 'widen_interval()'")

        if density < 1:
            raise ValueError("The density cannot take values less than 1")

        if left < 0 or right < 0:
            raise ValueError("The percentages of widening cannot take values less than 0")

        data_min = np.min(data)
        data_max = np.max(data)
        delta = data_max - data_min

        wider_data = np.array(data, copy=True, dtype=np.float64)
        if left != 0:
            wider_data = np.insert(wider_data, 0, data_min - left * delta)

        if right != 0:
            wider_data = wider_data[::-1]
            wider_data = np.insert(wider_data, 0, data_max + right * delta)
            wider_data = wider_data[::-1]

        return LinePlot._make_denser(wider_data, density)

    @staticmethod
    def _make_denser(data: NArray1D[Any], density: int) -> NArray1D[Any]:
        """
        Creates a "denser" numpy array by adding elements between existing ones.

        This function finds the minimum distance 'd' between consecutive elements.
        For each pair of consecutive elements, it inserts new points, with the number
        of points determined by the ratio of the pair's distance to `d`, multiplied
        by `density` and rounded to the nearest integer.

        Args:
            data (NArray1D[Any]): The 1D numpy array to be made denser.
            density (int): A scaling factor for the number of elements to add
                between existing elements. A value of 1 returns the original array.

        Returns:
            NArray1D[Any]: A new 1D numpy array with a higher density of elements.
        """
        logger.info("Called 'denser()' function")

        # trivial case
        if density == 1:
            return data

        if not np.allclose(np.sort(data), data):
            logger.warning("The data to be made denser is not sorted; sorting...")
            data = np.sort(data)

        # find minimum distance
        distances = np.diff(data)
        minimum_dist = np.min(np.abs(distances))
        logger.debug(f"Minimum distance: {minimum_dist}")

        if minimum_dist == 0:
            logger.warning("There are at least two repeated consecutive elements")
            return data

        # create final array
        n_elements_to_add = np.round(np.abs(distances) / minimum_dist).astype(np.uint) * density - 1
        final_size = data.size + np.sum(n_elements_to_add)
        result = np.zeros(final_size, dtype=data.dtype)

        # add original data to final array
        insert_indices = np.astype(np.cumsum(n_elements_to_add) + np.arange(len(data) - 1) + 1, np.uint)
        result[0] = data[0]
        result[insert_indices] = data[1:]

        # add interpolated data to final array
        current_index = 0
        for i in range(len(data) - 1):
            num_new_points = n_elements_to_add[i]
            start = data[i]
            stop = data[i + 1]

            start_index = current_index + 1
            stop_index = start_index + num_new_points

            result[start_index:stop_index] = np.linspace(start, stop, num=num_new_points + 2)[1:-1]

            current_index = stop_index

        logger.debug(f"Final array of size {len(result)}")

        return result
