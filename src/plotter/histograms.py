import logging
import numpy as np
from typing import Optional
import matplotlib.colors as colors

from .canvas import Canvas

logger = logging.getLogger(__name__)


class Hist:
    """
    Class used for creating a 1D histogram,
    which is then drawn in a canvas.

    Parameters
    ---
    data: numpy.ndarray
        The array containing the data to plot.
    nbins: int
        The number of bins of the histogram or
        the array containing the edges of the bins.
        See matplotlib documentation. It is set to
        `"auto"` by default.
    density: bool
        Whether to normalize the histogram. It is
        set to `False` by default.
    cumulative: bool
        Whether to plot the cumulative histogram
        or not. It is set to `False` by default.
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
        The `bin_vals` setter/getter.

        The data member `bin_vals` is an array containing
        the values corresponding to each bin of the histogram.
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
        The `bins` setter/getter.

        The data member `bins` is an array containing the
        edges of the bins. Therefore, its size is equal
        to the number of bins +1.
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
        color: Optional[str] = "cornflowerblue",
        alpha: Optional[float] = 1,
    ) -> None:
        """
        This function draws the histogram in the canvas
        to which it belongs.

        Parameters
        ---
        canvas: Canvas
            The canvas object to which the histogram
            is to be attached.

        Optional Parameters
        ---
        plot_n: int
            The index of the subplot. It is set to 0 by
            default, so the histogram is assigned to the
            first canvas if otherwise not specified.
        range: array-like shape(1,2)
            The array with the left and right limits
            of the bins. It is set to `None` by default.
        color: str
            The matplotlib color of the histogram.
        alpha: float
            The transparency of the histogram.
        """

        logger.info("Called 'Hist.draw()'")

        self.bin_vals, self.bins, _ = canvas.ax[plot_n].hist(
            self.__data,
            bins=self.__nbins,
            range=range,
            density=self.__density,
            cumulative=self.__cumulative,
            histtype="stepfilled",
            color=color,
            alpha=alpha,
            label=canvas.text.histograms[plot_n][(n := canvas.counter_histograms[plot_n])],
        )
        logger.debug(f"Hist {n} drawn")

        canvas.counter_histograms[plot_n] += 1


class Hist2D:
    """
    Class used for creating a 1D histogram,
    which is then drawn in a canvas.

    Parameters
    ---
    x: numpy.ndarray
        The array containing the x values to plot.
    y: numpy.ndarray
        The array containing the y values to plot.
    nbins: int
        Ether:
        - an int corresponding to the number of bins
            of both axis;
        - a tuple or a list with two int, corresponding
            to the number of bin per axis;
        - a 2D array containing the edges of the bins.
    density: bool
        Whether to normalize the histogram. It is
        set to `False` by default.
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
        The `bin_vals` getter/setter.

        The data member `bin_vals` is an array containing the values
        corresponding to each bin.

        It is a array of n arrays of m elements, where 'n' is the number
        of bin along x and 'm' the number of bins along y.
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
        The `xbins` getter/setter.

        The data member `xbins` is an array containing the edges of
        the bins along the x axis. Therefore, its size is equal to
        the number of bins along x +1.
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
        The `ybins` getter/setter.

        The data member `ybins` is an array containing the edges of
        the bins along the y axis. Therefore, its size is equal to
        the number of bins along y +1.
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
    ) -> None:
        """
        This function draws the histogram in the canvas
        to which it belongs.

        Parameters
        ---
        canvas: Canvas
            The canvas object to which the histogram
            is to be attached.

        Optional Parameters
        ---
        plot_n: int
            The index of the subplot. It is set to 0 by
            default, so the histogram is assigned to the
            first canvas if otherwise not specified.
        range: array-like shape(2,2)
            The tuple with the left and right limits
            of the bins (in x and y). It is set to `None` by default.
        colormap: str
            The matplotlib colormap of the histogram.
        alpha: float
            The transparency of the histogram.
        log: tuple
            The tuple with:
            - a bool for indicating if the scale is to be
              set to logarithmic;
            - the range of linearity in case the desired scale
              is of type 'symlog'.
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

        canvas.fig.colorbar(self.__patches)


if __name__ == "__main__":
    pass
