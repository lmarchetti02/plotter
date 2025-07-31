import logging
import numpy as np
from typing import Optional

from .canvas import Canvas

logger = logging.getLogger(__name__)


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
        self.__label = label if label else canvas.text.histograms[plot_n][n]

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
