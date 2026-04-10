from logging import getLogger
from typing import Any, TypedDict

import matplotlib.colors as colors
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .canvas import Canvas
from .drawable import Drawable
from .helpers import NArray2D

logger = getLogger(__name__)


class ColorbarAttributes(TypedDict):
    position: str
    size: str
    padding: float


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Image(Drawable):
    """
    Class for creating an image to be drawn on a canvas.

    Attributes:
        data (np.ndarray): The 2D or 3D numpy array containing the image data.
            If 3D, the third dimension must contain 3 (RGB) or 4 (RGBA) values.

    Raises:
        ValueError: If the data is not a 2D or 3D array.
        ValueError: If the third dimension of a 3D array is not 3 or 4.
        ValueError: If the data is not real.
    """

    data: NArray2D[Any]

    def __post_init__(self) -> None:
        logger.info("Created 'Image' object")

        if self.data.ndim not in [2, 3]:
            raise ValueError("The image data has to be a 2D or 3D array.")

        if self.data.ndim == 3 and self.data.shape[2] not in [3, 4]:
            raise ValueError("The third axes must contain 3 (RGB) or 4 (RGBA) values.")

        if not np.all(np.isreal(self.data)):
            raise ValueError("The image data has to be real.")

    def draw(self, canvas: Canvas, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the image on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the image on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            label (str, optional): The label for the colorbar. Defaults to `None`.

        Keyword Arguments:
            colormap (str): The Matplotlib colormap to use. Defaults to "plasma".
            log (bool or tuple[bool, float]): Controls the scale of the colormap.
                - `bool`: `True` for logarithmic scale.
                - `tuple`: `(True, float)` for a 'symlog' scale with a linear range of `float`.
                This parameter is ignored if the data is RGB(A). Defaults to `False`.
            v_range (tuple[float, float]): The minimum and maximum intensity
                values. Ignored if the data is RGB(A). Defaults to `(None, None)`.
            aspect (str): The aspect ratio of the axes. `equal` for squared
                pixels, `auto` for a squared image. Defaults to "equal".
            origin (str): The placement of the [0,0] element of the data.
                `upper` for the top-left, `lower` for the bottom-left. Defaults to "upper".
            limits (list[float]): The limits of the x and y axes in the format
                `[left, right, bottom, top]`. Defaults to `None`.
            colorbar (dict): To style the colorbar. Defaults to `None`.
                - `"pos"` (str): where to put the colorbar (right, left, top, bottom)
                - `"size"` (str): % of size of axes
                - `"pad"` (float): padding between colorbar and image
        """

        logger.info("Called 'Image.draw()'")

        log = kwargs.get("log", False)
        v_range = kwargs.get("v_range", (None, None))
        # get normalization
        if log:
            v_range = (None, None)

            if isinstance(log, tuple):
                normalization = colors.SymLogNorm(log[1])
            else:
                normalization = colors.LogNorm()
        else:
            normalization = colors.Normalize()

        self._img = canvas.axes[plot_n].imshow(
            self.data,
            cmap=kwargs.get("colormap", "gray"),
            norm=normalization,
            vmin=v_range[0],
            vmax=v_range[1],
            aspect=kwargs.get("aspect", "equal"),
            origin=kwargs.get("origin", "upper"),
            extent=kwargs.get("limits", None),
        )
        logger.debug("Image drawn")

        self._cb_attributes = kwargs.get("colorbar", None)
        if self._cb_attributes is None:
            self._cb_attributes = ColorbarAttributes(position="right", size="5%", padding=0.1)

        n = canvas.counters.images[plot_n]
        try:
            self._label = label if label else canvas.text[plot_n].images[n]
        except IndexError as _:
            self._label = None
            logger.warning("No label for the plot in the json file.")

        if self._label:
            self._add_colorbar(canvas, plot_n)
        canvas.counters.images[plot_n] += 1

    def _add_colorbar(self, canvas: Canvas, plot_n: int) -> None:
        """
        Adds the colorbar to an image.

        Args:
            See `draw`.
        """
        logger.info("Called 'Image.add.colorbar()'")

        divider = make_axes_locatable(canvas.axes[plot_n])

        if self._cb_attributes is None:
            return

        orientation = "vertical"
        if self._cb_attributes["position"] in ("top", "bottom"):
            orientation = "horizontal"
        else:
            logger.warning("The position of the colorbar is incorrect.")

        cax = divider.append_axes(
            position=self._cb_attributes["position"],
            size=self._cb_attributes["size"],
            pad=self._cb_attributes["padding"],
        )
        canvas.figure.colorbar(self._img, cax=cax, label=self._label, orientation=orientation)
