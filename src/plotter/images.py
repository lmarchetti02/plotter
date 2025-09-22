import logging
import numpy as np
from typing import Optional
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .canvas import Canvas

logger = logging.getLogger(__name__)

__all__ = ["Image"]


class Image:
    """
    Class for creating an image to be drawn on a canvas.

    Args:
        data (np.ndarray): The 2D or 3D numpy array containing the image data.
            If 3D, the third dimension must contain 3 (RGB) or 4 (RGBA) values.

    Raises:
        ValueError: If the data is not a 2D or 3D array.
        ValueError: If the third dimension of a 3D array is not 3 or 4.
        ValueError: If the data is not real.
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
        label: Optional[str] = None,
    ) -> None:
        """
        Draws the image on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the image on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            colormap (str, optional): The Matplotlib colormap to use. Defaults to "plasma".
            log (bool or tuple[bool, float], optional): Controls the scale of the colormap.
                - `bool`: `True` for logarithmic scale.
                - `tuple`: `(True, float)` for a 'symlog' scale with a linear range of `float`.
                This parameter is ignored if the data is RGB(A). Defaults to `False`.
            v_range (tuple[float, float], optional): The minimum and maximum intensity
                values. Ignored if the data is RGB(A). Defaults to `(None, None)`.
            aspect (str, optional): The aspect ratio of the axes. `equal` for squared
                pixels, `auto` for a squared image. Defaults to "equal".
            origin (str, optional): The placement of the [0,0] element of the data.
                `upper` for the top-left, `lower` for the bottom-left. Defaults to "upper".
            limits (list[float], optional): The limits of the x and y axes in the format
                `[left, right, bottom, top]`. Defaults to `None`.
            cb_label (str, optional): The label for the colorbar. Defaults to `None`.
        """

        logger.info("Called 'Image.draw()'")

        # get normalization
        if log:
            v_range = (None, None)

            if isinstance(log, tuple):
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

        self.add_colorbar(canvas, plot_n, label)
        canvas.counter_images[plot_n] += 1

    def add_colorbar(self, canvas: Canvas, plot_n: int, label: str) -> None:
        """
        Adds the colorbar to an image.

        Args:
            See `self.draw`.
        """
        logger.info("Called 'Image.add.colorbar()'")

        n = canvas.counter_images[plot_n]
        try:
            self.__label = label if label else canvas.text.images[plot_n][n]
        except IndexError as _:
            self.__label = None
            logger.warning(f"No label for the plot in the json file.")

        if not self.__label:
            return

        divider = make_axes_locatable(canvas.ax[plot_n])
        cax = divider.append_axes("right", size="5%", pad=0.1)
        canvas.fig.colorbar(self.__img, cax=cax, label=self.__label)


if __name__ == "__main__":
    pass
