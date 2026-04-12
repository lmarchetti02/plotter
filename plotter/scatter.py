from logging import getLogger
from typing import Any

import numpy as np
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .canvas import Canvas
from .drawable import Drawable
from .helpers import NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ScatterPlot(Drawable):
    """
    Class for creating a scatter plot with error bars.

    Attributes:
        x (NArray1D[Any]): The array containing the x values.
        y (NArray1D[Any]): The array containing the y values.
        xerr (NArray1D[Any] or float, optional): The array containing the errors of the x values.
            If a float is passed, all the errors are assumed identical.
        yerr (NArray1D[Any] or float, optional): The array containing the errors of the y values.
            If a float is passed, all the errors are assumed identical.

    Raises:
        ValueError: If x and y values do not have the same dimensions.
        ValueError: If x or y error values do not have the same dimensions as their corresponding data arrays.
    """

    x: NArray1D[Any]
    y: NArray1D[Any]
    yerr: NArray1D[Any] | float | None = None
    xerr: NArray1D[Any] | float | None = None

    def __post_init__(self) -> None:
        # xy values
        if len(self.x) != len(self.y):
            raise ValueError("x-values and y-values don't have the same dimensions")

        # y errors
        if isinstance(self.yerr, np.ndarray) and len(self.y) != len(self.yerr):
            raise ValueError("xy-values and yerr-values don't have the same dimensions")

        # x errors
        if isinstance(self.xerr, np.ndarray) and len(self.x) != len(self.xerr):
            raise ValueError("xy-values and xerr-values don't have the same dimensions")

    def draw(self, canvas: Canvas, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the scatter plot on the canvas.

        Args:
            canvas (Canvas): The canvas object to which the scatter plot
                is to be attached.
            plot_n (int, optional): The index of the subplot. Defaults to 0.
            label (str, optional): The label for the scatter plot in the legend.
                Defaults to `None`.

        Keyword Arguments:
            color (str): The Matplotlib color of the points. Defaults to "firebrick".
            err_color (str): The Matplotlib color of the error bars. Defaults to "firebrick".
            marker (str): The kind of Matplotlib marker to use. Defaults to `"o"`.
            ms (float): The dimensions of the markers. Defaults to 4.
            err_width (float): The width of the error bars. Defaults to 1.
            ticks_size (float): The size of the ticks on the error bars. Defaults to 2.
        """

        logger.info("Called 'ScatterPlot.draw()'")

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            "scatter_plots",
            logger,
            "No label for the scatter plot in the json file.",
        )

        canvas.axes[plot_n].errorbar(
            x=self.x,
            y=self.y,
            yerr=self.yerr,
            xerr=self.xerr,
            marker=kwargs.get("marker", "o"),
            color=kwargs.get("color", "firebrick"),
            ecolor=kwargs.get("err_color", "black"),
            ms=kwargs.get("ms", 4.0),
            elinewidth=kwargs.get("err_width", 1.0),
            zorder=2,  # layer
            ls="none",  # line size (none for disconnected dots)
            capsize=kwargs.get("ticks_size", 2.0),  # error bars ticks
            label=label,
        )
        logger.debug(f"ScatterPlot {n} drawn")

        canvas.counters.scatter_plots[plot_n] += 1
