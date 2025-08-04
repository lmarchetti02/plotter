import logging
import numpy as np
from typing import Optional
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .canvas import Canvas

logger = logging.getLogger(__name__)

__all__ = ["Hist", "Hist2D"]


class Hist:
    """
    Class for creating a 1D histogram.

    Args:
        data (np.ndarray): The array containing the data to plot.
        nbins (int | str | np.ndarray, optional): The number of bins of the histogram
            or the array containing the edges of the bins. Defaults to "auto".
        density (bool, optional): If `True`, the histogram is normalized such that
            the integral over the range is 1. Defaults to `False`.
        cumulative (bool, optional): If `True`, the cumulative histogram is plotted.
            Defaults to `False`.
    """

    def __init__(
        self,
        data: np.ndarray,
        nbins: Optional[int | str | np.ndarray] = "auto",
        density: Optional[bool] = False,
        cumulative: Optional[bool] = False,
    ) -> None:
        logger.info("Created 'Hist' object")

        self.__data = data
        self.__nbins = nbins
        self.__density = density
        self.__cumulative = cumulative

        self.bin_vals = None
        self.bins = None

    @property
    def bin_vals(self):
        """
        An array containing the values corresponding to each bin of the histogram.
        """

        logger.info("Called 'Hist.bin_vals' getter")

        return self._bin_vals

    @bin_vals.setter
    def bin_vals(self, value):
        logger.info("Called 'Hist.bin_vals' setter")

        self._bin_vals = value

    @property
    def bins(self):
        """
        An array containing the edges of the bins.

        The size of this array is equal to the number of bins plus one.
        """

        logger.info("Called 'Hist.bins' getter")

        return self._bins

    @bins.setter
    def bins(self, value):
        logger.info("Called 'Hist.bins' setter")

        self._bins = value

    def draw(
        self,
        canvas: Canvas,
        plot_n: Optional[int] = 0,
        range: Optional[tuple | list | np.ndarray] = None,
        color: Optional[str] = "royalblue",
        alpha: Optional[float] = 0.8,
        filled: Optional[bool] = True,
        label: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Draws the histogram on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the histogram on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            range (array-like, optional): The array with the left and right limits
                of the bins. Defaults to `None`.
            color (str, optional): The Matplotlib color of the histogram.
                Defaults to "royalblue".
            alpha (float, optional): The transparency of the histogram.
                Defaults to 0.8.
            filled (bool, optional): If `True`, the histogram is filled.
                Defaults to `True`.
            label (str, optional): The label for the histogram in the legend.
                Defaults to `None`.
            **kwargs: Additional keyword arguments.
                ecolor (str): The color of the histogram edges.
                lw (float): The width of the histogram edges.
        """

        logger.info("Called 'Hist.draw()'")

        self.__ecolor = kwargs.get("ecolor", "cornflowerblue")
        self.__lw = kwargs.get("lw", 0 if filled else 1.5)

        # label
        n = canvas.counter_histograms[plot_n]
        try:
            self.__label = label if label else canvas.text.histograms[plot_n][n]
        except IndexError as _:
            self.__label = None
            logger.warning(f"No label for the histogram in the json file.")

        self.bin_vals, self.bins, _ = canvas.ax[plot_n].hist(
            self.__data,
            bins=self.__nbins,
            range=range,
            density=self.__density,
            cumulative=self.__cumulative,
            histtype="stepfilled" if filled else "step",
            color=color,
            alpha=alpha,
            label=self.__label,
            edgecolor=self.__ecolor,
            lw=self.__lw,
        )
        logger.debug(f"Hist {n} drawn")

        canvas.counter_histograms[plot_n] += 1


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
