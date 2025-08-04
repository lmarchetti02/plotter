import logging
from numpy import ndarray
from typing import Optional, Callable

from .canvas import Canvas
from .functions import make_wider

logger = logging.getLogger(__name__)

__all__ = ["Plot"]


class Plot:
    """
    Class for creating a 1D function plot to be drawn on a canvas.

    Args:
        x (ndarray): The values of the independent variable.
        f (Callable[[ndarray], ndarray] | ndarray): The function that defines the plot,
            or an array of y-values.
        wider (tuple[float, float], optional): The percentages (left, right) to which
            the domain of the function `f` is to be widened. Defaults to `(0, 0)`.
        dens (int, optional): The density factor to be passed to `make_wider()`.
            Defaults to 2.

    Raises:
        ValueError: If x and f as an array do not have the same dimensions.
    """

    def __init__(
        self,
        x: ndarray,
        f: Callable[[ndarray], ndarray] | ndarray,
        wider: Optional[tuple[float, float]] = (0, 0),
        dens: Optional[int] = 2,
    ) -> None:
        logger.info("Created 'Plot' object")

        if isinstance(f, ndarray):
            if len(x) != len(f):
                raise ValueError("x-values and y-values must have the same dimension")

            self.__x = x
            self.__y = f
        else:
            self.__x = make_wider(x, wider[0], wider[1], dens)
            self.__y = f(self.__x)

    def draw(
        self,
        canvas: Canvas,
        plot_n: Optional[int] = 0,
        color: Optional[str] = "darkgreen",
        lw: Optional[float] = 1.5,
        style: Optional[str] = "-",
        inverted: Optional[bool] = False,
        label: Optional[str] = None,
    ) -> None:
        """
        Draws the plot on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the plot on.
            plot_n (int, optional): The index of the subplot. Defaults to 0.
            color (str, optional): The Matplotlib color of the plot. Defaults to "darkgreen".
            lw (float, optional): The line width. Defaults to 1.5.
            style (str, optional): The line style. Defaults to `"-"`.
            inverted (bool, optional): If `True`, plots the inverse function.
                Defaults to `False`.
            label (str, optional): The label for the plot in the legend.
                Defaults to `None`.
        """

        # exchange x and y
        if inverted:
            _ = self.__x
            self.__x = self.__y
            self.__y = _

        # label
        n = canvas.counter_plots[plot_n]
        try:
            self.__label = label if label else canvas.text.functions[plot_n][n]
        except IndexError as _:
            self.__label = None
            logger.warning(f"No label for the plot in the json file.")

        canvas.ax[plot_n].plot(
            self.__x,
            self.__y,
            color=color,
            zorder=1,
            lw=lw,
            ls=style,
            label=self.__label,
        )
        logger.debug(f"Plot {n} drawn")

        canvas.counter_plots[plot_n] += 1


if __name__ == "__main__":
    pass
