from logging import getLogger
from typing import Any, ClassVar

from matplotlib.collections import QuadMesh
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from ..canvas import Canvas, ZoomInset
from .drawable import Drawable
from ..helpers import F64, NArray1D, NArray2D
from ._normalization import resolve_log_normalization

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class RawHist(Drawable):
    """
    Class for creating a 1D histogram from raw sample data.

    Attributes:
        data (NArray1D[Any]): The array containing the raw data to bin and plot.
        nbins (int or NArray1D[Any] or "auto", optional): The number of bins of the histogram,
            or the array containing the edges of the bins (matplotlib's own convention for
            `Axes.hist`'s `bins` argument). Defaults to "auto".
        density (bool, optional): If `True`, the histogram is normalized such that
            the integral over the range is 1. Defaults to `False`.
        cumulative (bool, optional): If `True`, the cumulative histogram is plotted.
            Defaults to `False`.
        bin_vals (NArray1D[F64] or None): The array with the values corresponding to each bin.
            It has shape (N_bins,).
        bins (NArray1D[F64] or None): The array with the edges of each bin (flattened).
            It has shape (N_bins+1,).
    """

    label_name: ClassVar[str] = "histograms"

    data: NArray1D[Any]
    nbins: int | NArray1D[Any] | str = "auto"
    density: bool = False
    cumulative: bool = False

    bin_vals: NArray1D[F64] | None = Field(init=False, default=None)
    bins: NArray1D[F64] | None = Field(init=False, default=None)

    def draw(self, canvas: Canvas | ZoomInset, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the histogram on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the histogram on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            label (str, optional): The label for the histogram in the legend.
                Defaults to `None`.

        Keyword Arguments:
            bin_ranges (tuple[float,float]): The tuple with the left and right limits
                of the bins. Defaults to `None`, which means (data.min(), data.max()).
            color (str): The Matplotlib color of the histogram.
                Defaults to "royalblue".
            alpha (float): The transparency of the histogram.
                Defaults to 0.8.
            filled (bool): If `True`, the histogram is filled.
                Defaults to `True`.
            ecolor (str): The color of the histogram edges. Defaults to `"cornflowerblue"`.
            lw (float): The width of the histogram edges. Defaults to 0 if filled is `True`,
                else to 1.5.
        """

        logger.info("Called 'RawHist.draw()'")

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            self.label_name,
            logger,
            "No label for the histogram in the json file.",
        )

        filled = kwargs.get("filled", True)

        self.bin_vals, self.bins, _ = canvas.axes[plot_n].hist(  # type: ignore
            self.data,
            bins=self.nbins,  # type: ignore
            range=kwargs.get("bin_ranges", None),
            density=self.density,
            cumulative=self.cumulative,
            histtype="stepfilled" if filled else "step",
            color=kwargs.get("color", "royalblue"),
            alpha=kwargs.get("alpha", 0.8),
            label=label,
            edgecolor=kwargs.get("ecolor", "cornflowerblue"),
            lw=kwargs.get("lw", 0 if filled else 1.5),
        )
        logger.debug(f"RawHist {n} drawn")

        getattr(canvas.counters, self.label_name)[plot_n] += 1


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class RawHist2D(Drawable):
    """
    Class for creating a 2D histogram from raw sample data.

    Attributes:
        x (NArray1D[Any]): The array containing the x values to plot.
        y (NArray1D[Any]): The array containing the y values to plot.
        nbins (int | tuple | list | NArray2D): The number of bins for the
            histogram. It can be:
                - an `int` for the same number of bins for both axes.
                - a `tuple` or `list` of two ints for the number of bins
                  for x and y respectively.
                - a 2D array for the edges of the bins.
        density (bool, optional): If `True`, the histogram is normalized
            such that the integral over the range is 1. Defaults to `False`.
        bin_vals (NArray2D[F64] or None): The array with the values corresponding to each bin.
            It has shape (N_bins,).
        xbins (NArray1D[F64] or None): The array with the edges of each x-bin (flattened).
            It has shape (N_bins_X+1,).
        ybins (NArray1D[F64] or None): The array with the edges of each y-bin (flattened).
            It has shape (N_bins_Y+1,).
        mappable (QuadMesh or None): The mesh artist returned by `hist2d`, populated
            after `draw` runs. Pass it (via this `RawHist2D`) as a `Colorbar`'s `source`.
    """

    x: NArray1D[Any]
    y: NArray1D[Any]
    nbins: int | tuple[int, int] | list[int] | NArray2D[Any]
    density: bool = False

    bin_vals: NArray2D[F64] | None = Field(init=False, default=None)
    xbins: NArray1D[F64] | None = Field(init=False, default=None)
    ybins: NArray1D[F64] | None = Field(init=False, default=None)
    mappable: QuadMesh | None = Field(init=False, default=None)

    def draw(self, canvas: Canvas | ZoomInset, plot_n: int = 0, **kwargs) -> None:
        """
        Draws the 2D histogram on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the histogram on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.

        Keyword Arguments:
            bin_ranges (tuple[tuple[float,float],tuple[float,float]]): The tuple with the left
                and right limits of the bins (in x and y). Defaults to `None`, which means
                ((x.min(),x.max()),(y.min(),y.max()).
            colormap (str): The Matplotlib colormap to use for the histogram.
                Defaults to "plasma".
            alpha (float): The transparency of the histogram. Defaults to 1.
            log (tuple[bool, float]): A tuple controlling the scale.
                The first element is a boolean to indicate if the scale should be
                logarithmic. The second element is a float for the range of
                linearity in case of a 'symlog' scale. Defaults to `(False, 0)`.
        """

        logger.info("Called 'RawHist2D.draw()'")

        normalization = resolve_log_normalization(kwargs.get("log", (False, 0.0)))

        self.bin_vals, self.xbins, self.ybins, self.mappable = canvas.axes[plot_n].hist2d(
            self.x,
            self.y,
            bins=self.nbins,
            range=kwargs.get("bin_ranges", None),
            density=self.density,
            cmap=kwargs.get("colormap", "plasma"),
            alpha=kwargs.get("alpha", 1),
            norm=normalization,
        )
        logger.debug("2D RawHist drawn")
