import logging
from numpy import ndarray
from typing import Optional, Callable

from .canvas import Canvas
from .functions import make_wider

logger = logging.getLogger(__name__)


class Plot:
    """
    Class used for creating a 1D function
    plot, which is then drawn in a canvas.

    Parameters
    ---
    x: numpy.ndarray
        The values of the independent variable.
    f: numpy.ndarray
        The function that defines the plot.

    Optional Parameters
    ---
    wider: tuple
        The percentages (left, right) to which
        the domain of the function `f` is to be
        widened. See `make_wider()`.
    """

    def __init__(
        self,
        x: ndarray,
        f: Callable[[ndarray], ndarray] | ndarray,
        wider: Optional[tuple[float, float]] = (0, 0),
        dens: Optional[int] = 2,
    ) -> None:
        logger.info("Created 'Plot' object")

        self.__x = make_wider(x, wider[0], wider[1], dens if not isinstance(f, ndarray) else 1)
        self.__y = f(self.__x) if callable(f) else f

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
        This function draws the plot in the canvas
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
            default, so the graph is assigned to the
            first canvas if otherwise not specified.
        color: str
            The matplotlib color of the plot. It is
            set to `"darkgreen"` by default.
        lw: str
            The matplotlib line width of the plot. It is
            set to `1.5` by default.
        style: str
            The line style. It is set to solid (`"-"`) by default.
        inverted: bool
            Whether to plot f(x) or its inverse function.
            It is set to `False` by default.
        label: str
            The label to assign to the plot. Alternative to
            the json file definition.
        """

        # exchange x and y
        if inverted:
            _ = self.__x
            self.__x = self.__y
            self.__y = _

        # label
        n = canvas.counter_plots[plot_n]
        self.__label = label if label else canvas.text.functions[plot_n][n]

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
