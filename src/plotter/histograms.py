import logging
from typing import Optional
from .canvas import Canvas
import numpy as np

logger = logging.getLogger(__name__)


# TODO: add documentation
class Hist:
    """
    Class used for creating a 1D histogram,
    which is then drawn in a canvas.

    Parameters
    ---
    data: numpy.ndarray
        The array containing the data to plot.
    nbins: int
        The number of bins of the histogram.
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
        nbins: Optional[int | str] = "auto",
        density: Optional[bool] = False,
        cumulative: Optional[bool] = False,
    ) -> None:
        logger.info("Created 'Hist' object")

        self.__data = data
        self.__nbins = nbins
        self.__density = density
        self.__cumulative = cumulative

        self.__bin_vals_counter = 0
        self.__bins_counter = 0
        self.bin_vals = None
        self.bins = None

    @property
    def bin_vals(self):
        """
        The `bin_vals` setter/getter.

        The data member `bin_vals` is an array containing
        the values corresponding to each bin of the histogram.

        It is possible to obtain it for further analysis,
        but not to modify its value.
        """

        logger.info("Called 'Hist.bin_vals' getter")

        return self._bin_vals

    @bin_vals.setter
    def bin_vals(self, value):
        logger.info("Called 'Hist.bin_vals' setter")

        if self.__bin_vals_counter < 2:
            logger.debug("First call => modified 'bin_vals'")

            self._bin_vals = value
            self.__bin_vals_counter += 1
            return

        logger.warning("User tried to modify 'Hist.bin_vals'")

        pass

    @property
    def bins(self):
        """
        The `bins` setter/getter.

        The data member `bins` is an array containing the
        edges of the bins. Therefore, its size is equal
        to the number of bins +1.

        It is possible to obtain it for further analysis,
        but not to modify its value.
        """

        logger.info("Called 'Hist.bins' getter")

        return self._bins

    @bins.setter
    def bins(self, value):
        logger.info("Called 'Hist.bins' setter")

        if self.__bins_counter < 2:
            logger.debug("First call => modified 'bins'")

            self._bins = value
            self.__bins_counter += 1
            return

        logger.warning("User tried to modify 'Hist.bins'")

        pass

    def draw(
        self,
        canvas: Canvas,
        range: Optional[tuple] = None,
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
        range: tuple
            The tuple with the left and right limits
            of the bins. It is set to `None` by default.
        color: str
            The matplotlib color of the histogram.
        alpha: float
            The transparency of the histogram.
        """

        logger.info("Called 'Hist.draw()'")

        canvas.counter_histograms += 1

        self.bin_vals, self.bins, _ = canvas.ax.hist(
            self.__data,
            bins=self.__nbins,
            range=range,
            density=self.__density,
            cumulative=self.__cumulative,
            histtype="stepfilled",
            color=color,
            alpha=alpha,
            label=canvas.text.histograms[canvas.counter_histograms - 1],
        )

        logger.debug(f"Hist {canvas.counter_histograms-1} drawn")
