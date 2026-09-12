from logging import getLogger
from typing import Any

import matplotlib.colors as colors
import numpy as np
from matplotlib.axes import Axes
from matplotlib.image import AxesImage
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .canvas import Canvas, ZoomInset
from .drawable import Drawable
from .helpers import NArray2D, NArray3D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Image(Drawable):
    """
    Class for creating an image to be drawn on a canvas.

    Attributes:
        data (NArray2D[Any] | NArray3D[Any]): The 2D or 3D numpy array containing the
            image data. If 3D, the third dimension must contain 3 (RGB) or 4 (RGBA) values.
        mappable (AxesImage or None): The image artist returned by `imshow`, populated
            after `draw` runs. Pass it (via this `Image`) as a `Colorbar`'s `source`.

    Raises:
        ValueError: If the data is not a 2D or 3D array.
        ValueError: If the third dimension of a 3D array is not 3 or 4.
        ValueError: If the data is not real.
    """

    data: NArray2D[Any] | NArray3D[Any]

    mappable: AxesImage | None = Field(init=False, default=None)

    def __post_init__(self) -> None:
        logger.info("Created 'Image' object")

        if self.data.ndim not in [2, 3]:
            raise ValueError("The image data has to be a 2D or 3D array.")

        if self.data.ndim == 3 and self.data.shape[2] not in [3, 4]:
            raise ValueError("The third axes must contain 3 (RGB) or 4 (RGBA) values.")

        if not np.all(np.isreal(self.data)):
            raise ValueError("The image data has to be real.")

    def draw(self, canvas: Canvas | ZoomInset, plot_n: int = 0, **kwargs) -> None:
        """
        Draws the image on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the image on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.

        Keyword Arguments:
            colormap (str): The Matplotlib colormap to use. Defaults to "gray".
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
                `[left, right, bottom, top]`. Defaults to `None`. When drawing into a
                `ZoomInset` with `limits` left as `None`, `data` is instead expected to
                be the same full-resolution array shown on the source subplot: it gets
                automatically cropped and placed to match the panel's requested region.
        """

        logger.info("Called 'Image.draw()'")

        log = kwargs.get("log", False)
        v_range = kwargs.get("v_range", (None, None))
        # get normalization -- vmin/vmax must be set on the norm itself: matplotlib
        # rejects passing a Normalize instance together with vmin/vmax to imshow()
        if log:
            if isinstance(log, tuple):
                normalization = colors.SymLogNorm(log[1])
            else:
                normalization = colors.LogNorm()
        else:
            normalization = colors.Normalize(vmin=v_range[0], vmax=v_range[1])

        data = self.data
        extent = kwargs.get("limits", None)
        if isinstance(canvas, ZoomInset) and extent is None:
            data, extent = self._crop_to_view(data, canvas.axes[plot_n])

        self.mappable = canvas.axes[plot_n].imshow(
            data,
            cmap=kwargs.get("colormap", "gray"),
            norm=normalization,
            aspect=kwargs.get("aspect", "equal"),
            origin=kwargs.get("origin", "upper"),
            extent=extent,
        )
        logger.debug("Image drawn")

    @staticmethod
    def _crop_to_view(
        data: NArray2D[Any] | NArray3D[Any], axes: Axes
    ) -> tuple[NArray2D[Any] | NArray3D[Any], tuple[float, float, float, float]]:
        """
        Crops image data to an Axes' current view window.

        Only ever slices the first two axes (rows, columns): a 3D array's channel
        axis (RGB or RGBA) is left untouched and carried through unchanged.

        Args:
            data (NArray2D[Any] | NArray3D[Any]): The full-resolution image data to crop.
            axes (Axes): The Axes whose current `xlim`/`ylim` define the region to keep.

        Returns:
            tuple[NArray2D[Any] | NArray3D[Any], tuple[float, float, float, float]]: The
                cropped data, and the `extent` (left, right, bottom, top) to draw it at
                so it exactly matches `axes`' current view, orientation included.
        """
        x0, x1 = axes.get_xlim()
        y0, y1 = axes.get_ylim()

        col_lo, col_hi = sorted((round(x0), round(x1)))
        row_lo, row_hi = sorted((round(y0), round(y1)))

        col_lo, row_lo = max(0, col_lo), max(0, row_lo)
        col_hi, row_hi = min(data.shape[1], col_hi), min(data.shape[0], row_hi)

        return data[row_lo:row_hi, col_lo:col_hi], (x0, x1, y0, y1)
