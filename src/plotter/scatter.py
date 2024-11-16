import logging
import numpy as np
from typing import Optional

from .canvas import Canvas

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

    Optional Parameters
    ---
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
        plot_n: Optional[int] = 0,
        color: Optional[str] = "firebrick",
        err_color: Optional[str] = "black",
        marker: Optional[str] = "o",
        ms: Optional[float] = 4,
        err_width: Optional[float] = 1,
        ticks_size: Optional[float] = 2,
        label: Optional[str] = None,
    ) -> None:
        """
        This function draws the scatter plot in the canvas
        to which it belongs.

        Parameters
        ---
        canvas: Canvas
            The canvas object to which the scatter plot
            is to be attached.

        Optional Parameters
        ---
        plot_n: int
            The index of the subplot. It is set to 0 by
            default, so the scatter plot is assigned to the
            first canvas if otherwise not specified.
        color: str
            The matplotlib color of the points. It is
            set to `"firebrick"` by default.
        err_color: str
            The matplotlib color of the error bars. It is
            set to `"firebrick"` by default.
        marker: str
            The kind of matplotlib marker to use. It is set
            to `"o"` by default (filled circular dots).
        ms: float
            The dimensions of the markers. It is set to `4`
            by default.
        err_witdth: float
            The width of the error bars. It is set to `1`
            by default.
        ticks_size: float
            The size of the ticks on the error bars. It is
            set to `2` by default.
        label: str
            The label to assign to the scatter plot. Alternative
            to the json file definition.
        """

        logger.info("Called 'ScatterPlot.draw()'")

        # label
        n = canvas.counter_scatter_plots[plot_n]
        self.__label = label if label else canvas.text.datasets[plot_n][n]

        canvas.ax[plot_n].errorbar(
            self.__x,
            self.__y,
            yerr=self.__yerr,
            xerr=self.__xerr,
            marker=marker,
            color=color,
            ecolor=err_color,
            ms=ms,
            elinewidth=err_width,
            zorder=2,  # layer
            ls="none",  # line size (none for disconnected dots)
            capsize=ticks_size,  # error bars ticks
            label=self.__label,
        )
        logger.debug(f"ScatterPlot {n} drawn")

        canvas.counter_scatter_plots[plot_n] += 1


if __name__ == "__main__":
    pass
