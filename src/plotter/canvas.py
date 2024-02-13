from .functions import setup_logging
import logging
import matplotlib.pyplot as plt
import pathlib
from typing import Optional
from .text import Text

plt.style.use(pathlib.Path("./plotter/utils/style.mplstyle"))
logging.getLogger("matplotlib").setLevel(logging.CRITICAL)  # remove matplotlib logger
logging.getLogger("PIL").setLevel(logging.CRITICAL)  # remove PIL logger

logger = logging.getLogger(__name__)


class Canvas:
    """
    Class used for creating a canvas (xy-plane) where to plot
    datasets, graphs,...

    Parameters
    ---
    text: str
        The name of the json file in which the text to be added
        to the plot is stored.
    fs: tuple
        The tuple containing the dimensions of the canvas.
        Set to `(12,8)` by default.
    dpi: int
        The number of 'dots per inches' of the image (see matplotlib
        documentation). Set to `150` by default.

    Optional Parameters
    ---
    xlim: tuple
        The tuple containing the limits of the abscissa axis.
    ylim: tuple
        The tuple containing the limits of the ordinate axis.
    xscale: str
        The abscissa axis scale. It can be: 'linear' (default),
        'log' o 'symlog'.
    yscale: str
        The ordinate axis scale. It can be: 'linear' (default),
        'log' o 'symlog'.
    save: str
        The name of the file in which to store the plot. The
        plots are stored in 'plotter/img/'.
    nogrid: bool
        `True` if the grid is to be removed, `False` otherwise.
    """

    def __init__(
        self,
        text_file: str,
        fs: Optional[tuple[int, int]] = (12, 8),
        dpi: Optional[int] = 150,
        **kwargs,
    ) -> None:
        # logging
        setup_logging()

        logger.info("Created 'Canvas' object")

        self.counter_scatter_plots = 0
        self.counter_plots = 0
        self.counter_histograms = 0

        # plot properties
        self.fig, self.ax = plt.subplots(figsize=(fs[0], fs[1]), dpi=dpi)
        self.__kwargs = kwargs

        # plot text
        self.text = Text(text_file)

        # grid
        self.no_grid = kwargs.get("nogrid", False)
        if not self.no_grid:
            self.ax.grid(color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)

        # axis limits
        if "xlim" in self.__kwargs.keys():
            self.ax.set_xlim(self.__kwargs["xlim"][0], self.__kwargs["xlim"][1])

        if "ylim" in self.__kwargs.keys():
            self.ax.set_ylim(self.__kwargs["ylim"][0], self.__kwargs["ylim"][1])

        # axis scales
        if "yscale" in self.__kwargs.keys():
            self.ax.set_yscale(self.__kwargs["yscale"])

        if "xscale" in self.__kwargs.keys():
            self.ax.set_xscale(self.__kwargs["xscale"])

        # axis labels
        self.ax.set_xlabel(self.text.abscissa)
        self.ax.set_ylabel(self.text.ordinate)

        # title
        self.ax.set_title(self.text.title, y=1)

    def __legend(self) -> None:
        """
        This function generates the plot legend.
        """

        logger.info("Called 'Canvas.__legend()'")

        try:
            self.ax.legend(loc=0)
            plt.legend(labelspacing=1)

            logger.debug("Legend added.")
        # TODO: change thus exception
        except Exception:
            self.logger.exception("Impossible to show the legend.")

    def __save(self) -> None:
        """
        If specified by the user, this function saves
        the plot that has been generated to a file.
        """

        logger.info("Called 'Canvas.__save()'")

        if "save" in self.__kwargs.keys():
            file_path = pathlib.Path("./plotter/img").joinpath(self.__kwargs["save"])
            self.fig.savefig(file_path)
            logger.debug(f"Plot saved to {file_path}")
        else:
            logger.warning("Plot not saved to any file")

    def end(self, show: Optional[bool] = True) -> None:
        """
        This functions finished the plots and renders it.

        It is meant to be called at the end of everything, as
        anything after it will not affect the plot.

        Parameters
        ---
        show: bool
            Whether to actually show the plot. True by default.
        """

        logger.info("Called 'Canvas.end()'")

        # if only Hist2D, no legend
        if self.counter_histograms != 0 or self.counter_plots != 0 or self.counter_scatter_plots != 0:
            self.__legend()

        self.__save()
        logger.info("Plot finished")

        # show plot
        if not show:
            plt.close()
            return

        plt.show()


if __name__ == "__main__":
    pass
