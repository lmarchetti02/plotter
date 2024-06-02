import logging
import numpy as np
from typing import Optional

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
        color: Optional[str] = "royalblue",
        alpha: Optional[float] = 0.8,
        filled: Optional[bool] = True,
        **kwargs,
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
        filled: bool
            Whether the histogram is to be filled or not.

        Extra Parameters
        ---
        ecolor: str
            The color of the edges of the histogram.
        lw: float
            The width of the edges.
        """

        logger.info("Called 'Hist.draw()'")

        self.__ecolor = kwargs.get("ecolor", "cornflowerblue")
        self.__lw = kwargs.get("lw", 0 if filled else 1.5)

        self.bin_vals, self.bins, _ = canvas.ax[plot_n].hist(
            self.__data,
            bins=self.__nbins,
            range=range,
            density=self.__density,
            cumulative=self.__cumulative,
            histtype="stepfilled" if filled else "step",
            color=color,
            alpha=alpha,
            label=canvas.text.histograms[plot_n][(n := canvas.counter_histograms[plot_n])],
            edgecolor=self.__ecolor,
            lw=self.__lw,
        )
        logger.debug(f"Hist {n} drawn")

        canvas.counter_histograms[plot_n] += 1
