import logging
import numpy as np
import matplotlib.colors as colors
from typing import Optional

from .canvas import Canvas

logger = logging.getLogger(__name__)


class Image:
    """
    Class used for creating an image,
    which is then drawn in a canvas.

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

    def __init__(self, data: np.ndarray) -> None:
        logger.info("Created 'Image' object")

        if data.ndim not in [2, 3]:
            raise ValueError("The image data has to be a 2D or 3D array.")

        if data.ndim == 3 and data.shape[2] not in [3, 4]:
            raise ValueError("The third axes must contain 3 (RGB) or 4 (RGBA) values.")

        if not np.all(np.isreal(data)):
            raise ValueError("The image data has to be real.")

        self.__data = data

    def draw(
        self,
        canvas: Canvas,
        plot_n: Optional[int] = 0,
        colormap: Optional[str] = "plasma",
        log: Optional[bool | tuple[bool, float]] = False,
        v_range: Optional[tuple[float, float]] = (None, None),
        aspect: Optional[str] = "equal",
        origin: Optional[str] = "upper",
        limits: Optional[list[float]] = None,
        cb_label: Optional[str] = None,
    ) -> None:
        """
        This function draws the image in the canvas
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
        colormap: str
            The matplotlib colormap of the histogram.
        log: tuple
            The tuple with:
            - a bool for indicating if the scale is to be
              set to logarithmic;
            - the range of linearity in case the desired scale
              is of type 'symlog'.
            Ignored if data is RGB(A)
        v_range: tuple[min,max]
            The minimum and maximum intensity values.
            Ignored if the data is RGB(A).
        aspect: str
            The aspect ration of the axis: `equal` for squared
            pixels, `auto` for squared image.
        origin: str
            Where to place the [0,0] element: `upper` for top left
            and `lower` for bottom left.
        limits: list[left,right,bottom,top]
            The limits of the x (rows) and y (cols) axes.
        cb_label: str
            The label of the colorbar relative to the image.
        """

        logger.info("Called 'Image.draw()'")

        # get normalization
        if log:
            v_range = (None, None)

            if type(log) == tuple:
                self.__normalization = colors.SymLogNorm(log[1])
            else:
                self.__normalization = colors.LogNorm()
        else:
            self.__normalization = colors.Normalize()

        self.__img = canvas.ax[plot_n].imshow(
            self.__data,
            cmap=colormap,
            norm=self.__normalization,
            vmin=v_range[0],
            vmax=v_range[1],
            aspect=aspect,
            origin=origin,
            extent=limits,
        )
        logger.debug(f"Image drawn")

        canvas.fig.colorbar(self.__img, label=cb_label)


if __name__ == "__main__":
    pass
