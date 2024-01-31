import logging
from typing import Optional
from .canvas import Canvas
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ScatterPlot:
    """
    Class used for creating a scatter plot with
    error bars, which is then drawn in a canvas.

    Parameters
    ---
    x: numpy.ndarray
        The array containing the x values.
    y: numpy.ndarray
        The array containing the y values.
    xerr: numpy.ndarray
        The array containing the errors in
        the x values.
    yerr: numpy.ndarray
        The array containing the errors in
        the y values.
    """

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        yerr: Optional[np.ndarray] = None,
        xerr: Optional[np.ndarray] = None,
    ) -> None:
        logger.info("Created 'ScatterPlot' object")

        # xy values
        if len(x) != len(y):
            raise ValueError("x-values and y-values don't have the same dimensions")
        self.__x = x
        self.__y = y

        # y errors
        if yerr is not None and len(y) != len(yerr):
            raise ValueError("xy-values and yerr-values don't have the same dimensions")
        self.__yerr = yerr

        # x errors
        if xerr is not None and len(x) != len(xerr):
            raise ValueError("xy-values and xerr-values don't have the same dimensions")
        self.__xerr = xerr

    def draw(
        self,
        canvas: Canvas,
        color: Optional[str] = "firebrick",
        marker: Optional[str] = "o",
        ms: Optional[float] = 4,
    ) -> None:
        """
        This function draws the scatter plot in the canvas
        to which it belongs.

        Parameters
        ---
        canvas: Canvas
            The canvas object to which the scatter plot
            is to be attached.
        color: str
            The matplotlib color of the scatter plot. It is
            set to `"firebrick"` by default.
        marker: str
            The kind of matplotlib marker to use. It is set
            to `"o"` by default (filled circular dots).
        ms: float
            The dimensions of the markers. It is set to `4`
            by default.
        """

        logger.info("Called 'ScatterPlot.draw()'")

        self.__color = color
        self.__marker = marker
        self.__ms = ms

        canvas.counter_scatter_plots += 1

        canvas.ax.errorbar(
            self.__x,
            self.__y,
            yerr=self.__yerr,
            xerr=self.__xerr,
            marker=self.__marker,
            color=self.__color,
            ms=self.__ms,  # marker size
            zorder=2,  # layer
            ls="none",  # line size (none for disconnected dots)
            capsize=2,  # error bars ticks
            label=canvas.text.datasets[canvas.counter_scatter_plots - 1],
        )
        logger.debug(f"ScatterPlot {canvas.counter_scatter_plots-1} drawn")


if __name__ == "__main__":
    pass
