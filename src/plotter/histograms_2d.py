import logging
import numpy as np
from typing import Optional
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .canvas import Canvas

logger = logging.getLogger(__name__)


class Hist2D:
    """
    Class for creating a 2D histogram.

    Args:
        x (np.ndarray): The array containing the x values to plot.
        y (np.ndarray): The array containing the y values to plot.
        nbins (int | np.ndarray | tuple | list): The number of bins for the
            histogram. It can be:
                - an `int` for the same number of bins for both axes.
                - a `tuple` or `list` of two ints for the number of bins
                  for x and y respectively.
                - a 2D `np.ndarray` for the edges of the bins.
        density (bool, optional): If `True`, the histogram is normalized
            such that the integral over the range is 1. Defaults to `False`.
    """

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        nbins: int | np.ndarray | tuple | list,
        density: Optional[bool] = False,
    ) -> None:
        logger.info("Created 'Hist2D' object")

        self.__x = x
        self.__y = y
        self.__nbins = nbins
        self.__density = density

        self.bin_vals = None
        self.xbins = None
        self.ybins = None

    @property
    def bin_vals(self):
        """
        An array containing the values corresponding to each bin.

        This is a 2D array where the first dimension corresponds to the number of
        bins along the x-axis and the second dimension corresponds to the number
        of bins along the y-axis.
        """
        logger.info("Called 'Hist2D.bin_vals' getter")

        return self._bin_vals

    @bin_vals.setter
    def bin_vals(self, value):
        logger.info("Called 'Hist2D.bin_vals' setter")

        self._bin_vals = value

    @property
    def xbins(self):
        """
        An array containing the edges of the bins along the x-axis.

        The size of this array is equal to the number of bins along the x-axis plus one.
        """
        logger.info("Called 'Hist2D.xbins' getter")

        return self._xbins

    @xbins.setter
    def xbins(self, value):
        logger.info("Called 'Hist2D.xbins' setter")

        self._xbins = value

    @property
    def ybins(self):
        """
        An array containing the edges of the bins along the y-axis.

        The size of this array is equal to the number of bins along the y-axis plus one.
        """
        logger.info("Called 'Hist2D.ybins' getter")

        return self._ybins

    @ybins.setter
    def ybins(self, value):
        logger.info("Called 'Hist2D.ybins' setter")

        self._ybins = value

    def draw(
        self,
        canvas: Canvas,
        plot_n: Optional[int] = 0,
        range: Optional[tuple | list | np.ndarray] = None,
        colormap: Optional[str] = "plasma",
        alpha: Optional[float] = 1,
        log: Optional[tuple[bool, float]] = (False, 0),
        cb_label: Optional[str] = None,
    ) -> None:
        """
        Draws the 2D histogram on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the histogram on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            range (array-like, optional): The tuple with the left and right limits
                of the bins (in x and y). Defaults to `None`.
            colormap (str, optional): The Matplotlib colormap to use for the histogram.
                Defaults to "plasma".
            alpha (float, optional): The transparency of the histogram. Defaults to 1.
            log (tuple[bool, float], optional): A tuple controlling the scale.
                The first element is a boolean to indicate if the scale should be
                logarithmic. The second element is a float for the range of
                linearity in case of a 'symlog' scale. Defaults to `(False, 0)`.
            cb_label (str, optional): The label for the colorbar. Defaults to None.
        """

        logger.info("Called 'Hist.draw()'")

        # get normalization
        if log[0]:
            if log[1]:
                self.__normalization = colors.SymLogNorm(log[1])
            else:
                self.__normalization = colors.LogNorm()
        else:
            self.__normalization = colors.Normalize()

        self.bin_vals, self.xbins, self.ybins, self.__patches = canvas.ax[plot_n].hist2d(
            self.__x,
            self.__y,
            bins=self.__nbins,
            range=range,
            density=self.__density,
            cmap=colormap,
            alpha=alpha,
            norm=self.__normalization,
        )
        logger.debug(f"2D Hist drawn")

        # make colorbar that fits the histogram
        divider = make_axes_locatable(canvas.ax[plot_n])
        cax = divider.append_axes("right", size="5%", pad=0.1)
        canvas.fig.colorbar(self.__patches, cax=cax, label=cb_label)


if __name__ == "__main__":
    pass
