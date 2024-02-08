import logging
from typing import Optional
from .canvas import Canvas
import numpy as np

logger = logging.getLogger(__name__)


# TODO: add documentation
class Hist:
    """ """

    def __init__(
        self,
        data: np.ndarray,
        nbins: Optional[int] = "auto",
        density: Optional[bool] = False,
        cumulative: Optional[bool] = False,
    ) -> None:
        logger.info("Created 'Hist' object")

        self.__data = data
        self.__nbins = nbins
        self.__density = density
        self.__cumulative = cumulative

        self.bin_n = None
        self.bins = None

    def draw(self, canvas: Canvas, color: Optional[str] = "cornflowerblue", alpha: Optional[float] = 1) -> None:

        logger.info("Called 'Hist.draw()'")

        canvas.counter_histograms += 1

        self.bin_n, self.bins, _ = canvas.ax.hist(
            self.__data,
            bins=self.__nbins,
            density=self.__density,
            cumulative=self.__cumulative,
            histtype="stepfilled",
            color=color,
            alpha=alpha,
            label=canvas.text.histograms[canvas.counter_histograms - 1],
        )

        logger.debug(f"Hist {canvas.counter_histograms-1} drawn")
