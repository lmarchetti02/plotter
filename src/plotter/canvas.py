import logging
import pathlib
import numpy as np
from typing import Optional
import matplotlib.pyplot as plt

from .text import Text
from .functions import setup_logging

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
    text_file: str
        The name of the json file in which the text to be added
        to the plot is stored.

    Optional Parameters
    ---
    rows_cols: tuple
        The tuple with the number of rows and columns
        of subplots '(rows, cols)'.
    fs: tuple
        The tuple containing the dimensions of the canvas.
        Set to `(12,8)` by default.
    dpi: int
        The number of 'dots per inches' of the image (see matplotlib
        documentation). Set to `150` by default.
    save: str
        The name of the file in which to store the plot. The
        plots are stored in 'plotter/img/'.
    """

    def __init__(
        self,
        text_file: str,
        rows_cols: Optional[tuple[int, int]] = (1, 1),
        fs: Optional[tuple[int, int]] = (12, 8),
        dpi: Optional[int] = 150,
        save: Optional[str] = "",
    ) -> None:
        # logging
        setup_logging()

        logger.info("Created 'Canvas' object")

        self.__rows = rows_cols[0]
        self.__cols = rows_cols[1]
        self.__n_plots = self.__get_n_plots()

        self.counter_scatter_plots = [0 for _ in range(self.__rows + self.__cols)]
        self.counter_plots = [0 for _ in range(self.__rows + self.__cols)]
        self.counter_histograms = [0 for _ in range(self.__rows + self.__cols)]

        # plot properties
        self.fig, self.ax = plt.subplots(nrows=rows_cols[0], ncols=rows_cols[1], figsize=(fs[0], fs[1]), dpi=dpi)
        if self.__n_plots < 2:
            self.ax = np.array([self.ax, None])
        else:
            self.ax = self.ax.flatten()

        # plot text
        self.text = Text(text_file, self.__n_plots)

        # save plot
        self.__save_plot = save

    def setup(self, plot_n: Optional[int] = 0, **kwargs) -> None:
        """
        This functions sets up the properties of the
        subplots created.

        Optional Parameters
        ---
        plot_n: int
            The index of the subplot (0,1,...,n-1).
            It is set to `0` by default.

        Extra Parameters
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
        nogrid: bool
            `True` if the grid is to be removed, `False` otherwise.
        """

        # grid
        self.no_grid = kwargs.get("nogrid", False)
        if not self.no_grid:
            self.ax[plot_n].grid(color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)

        # axis limits
        if "xlim" in kwargs.keys():
            self.ax[plot_n].set_xlim(kwargs["xlim"][0], kwargs["xlim"][1])

        if "ylim" in kwargs.keys():
            self.ax[plot_n].set_ylim(kwargs["ylim"][0], kwargs["ylim"][1])

        # axis scales
        if "yscale" in kwargs.keys():
            self.ax[plot_n].set_yscale(kwargs["yscale"])

        if "xscale" in kwargs.keys():
            self.ax[plot_n].set_xscale(kwargs["xscale"])

        # axis labels
        self.ax[plot_n].set_xlabel(self.text.abscissa[plot_n])
        self.ax[plot_n].set_ylabel(self.text.ordinate[plot_n])

        # title
        self.ax[plot_n].set_title(self.text.title[plot_n], y=1)

    def __get_n_plots(self) -> int:
        """
        This function obtains the number of subplots
        of the canvas.
        """

        _n_plots = 0
        if self.__rows == 1:
            _n_plots = self.__cols
        elif self.__cols == 1:
            _n_plots = self.__rows
        else:
            _n_plots = self.__rows + self.__cols

        return _n_plots

    def __legend(self) -> None:
        """
        This function generates the plot legend.
        """

        logger.info("Called 'Canvas.__legend()'")

        for i in range(self.__n_plots):
            legend = self.ax[i].legend(loc=0, labelspacing=1)

            if not legend.get_texts():
                legend.remove()
                logger.warning("Empty legend.")

            logger.debug("Legend added.")

    def __save(self) -> None:
        """
        If specified by the user, this function saves
        the plot that has been generated to a file.
        """

        logger.info("Called 'Canvas.__save()'")

        if self.__save_plot:
            file_path = pathlib.Path("./plotter/img").joinpath(self.__save_plot)
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
