import logging
import numpy as np
from typing import Optional

from .canvas import Canvas

logger = logging.getLogger(__name__)

__all__ = ["ScatterPlot"]


class ScatterPlot:
    """
    Class for creating a scatter plot with error bars.

    Args:
        x (np.ndarray): The array containing the x values.
        y (np.ndarray): The array containing the y values.
        xerr (np.ndarray, optional): The array containing the errors in the x values.
        yerr (np.ndarray, optional): The array containing the errors in the y values.

    Raises:
        ValueError: If x and y values do not have the same dimensions.
        ValueError: If x or y error values do not have the same dimensions as their corresponding data arrays.
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
        Draws the scatter plot on the canvas.

        Args:
            canvas (Canvas): The canvas object to which the scatter plot
                is to be attached.
            plot_n (int, optional): The index of the subplot. Defaults to 0.
            color (str, optional): The Matplotlib color of the points. Defaults to "firebrick".
            err_color (str, optional): The Matplotlib color of the error bars. Defaults to "firebrick".
            marker (str, optional): The kind of Matplotlib marker to use. Defaults to `"o"`.
            ms (float, optional): The dimensions of the markers. Defaults to 4.
            err_width (float, optional): The width of the error bars. Defaults to 1.
            ticks_size (float, optional): The size of the ticks on the error bars. Defaults to 2.
            label (str, optional): The label for the scatter plot in the legend.
                Defaults to `None`.
        """

        logger.info("Called 'ScatterPlot.draw()'")

        # label
        n = canvas.counter_scatter_plots[plot_n]
        try:
            self.__label = label if label else canvas.text.datasets[plot_n][n]
        except IndexError as _:
            self.__label = None
            logger.warning(f"No label for the scatter plot in the json file.")

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
