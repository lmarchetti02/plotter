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
        self.__n_plots = self.__rows * self.__cols

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

        # legend
        self.__loc_legend = [0] * self.__n_plots

    def setup(self, plot_n: Optional[int | tuple[int, int] | str] = 0, **kwargs) -> None:
        """
        This functions sets up the properties of the
        subplots created.

        Optional Parameters
        ---
        plot_n: int, tuple, str
            The indexes of the subplots (0,1,...,n-1)
            to target for the setup. It defaults to `0`.

            Options:
                - int: the number of the plot
                - str: 'all' to target all plots
                - tuple[inf,sup]: to target all plots in [inf,sup]

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
        inverted: tuple
            The tuple with the info on whether to invert the axis.
            The first element corresponds to the x-axis, the second
            to the y-axis.
        legend: int
            Force the position of the legend to a specified one.
        """
        # which plots to target
        if plot_n and not isinstance(plot_n, int):
            if plot_n == "all":
                limits = (0, self.__n_plots)
            elif isinstance(plot_n, tuple) and len(plot_n) == 2:
                limits = (plot_n[0], plot_n[1] + 1)
            else:
                raise ValueError(f"'{plot_n}' is not a valid value for 'plot_n'")
        else:
            limits = (plot_n, plot_n + 1)

        # setup plots
        for plot_i in range(*limits):
            # grid
            self.no_grid = kwargs.get("nogrid", False)
            if not self.no_grid:
                self.ax[plot_i].grid(color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)

            # axis limits
            if "xlim" in kwargs.keys():
                self.ax[plot_i].set_xlim(kwargs["xlim"][0], kwargs["xlim"][1])

            if "ylim" in kwargs.keys():
                self.ax[plot_i].set_ylim(kwargs["ylim"][0], kwargs["ylim"][1])

            # invert axis
            if "inverted" in kwargs.keys():
                if kwargs["inverted"][0]:
                    self.ax[plot_i].invert_xaxis()
                if kwargs["inverted"][1]:
                    self.ax[plot_i].invert_yaxis()

            # axis scales
            if "yscale" in kwargs.keys():
                self.ax[plot_i].set_yscale(kwargs["yscale"])

            if "xscale" in kwargs.keys():
                self.ax[plot_i].set_xscale(kwargs["xscale"])

            # legend
            if "legend" in kwargs.keys():
                self.__loc_legend[plot_i] = kwargs["legend"]

            # axis labels
            self.ax[plot_i].set_xlabel(self.text.abscissa[plot_i])
            self.ax[plot_i].set_ylabel(self.text.ordinate[plot_i])

            # title
            self.ax[plot_i].set_title(self.text.title[plot_i], y=1)

    def draw_line(
        self,
        orientation: str,
        point: Optional[float] = 0,
        plot_n: Optional[int] = 0,
        color: Optional[str] = "black",
        style: Optional[str] = "-",
        width: Optional[float] = 0.5,
        label: Optional[str] = None,
    ) -> None:
        """
        This function draws horizontal and vertical lines
        on the canvas.

        Parameters
        ---
        orientation: str
            `"v"` for vertical lines, `"h"` for horizontal lines

        Optional Parameters
        ---
        point: float
            The coordinate of the line. Set to 0 by default.
        plot_n: int
            The number of the canvas to consider. Set to 0
            by default.
        color: str
            The color of the line. Set to 'black' by default.
        style: str
            The style of the line. See info directory. Set to
            '-' (solid) by default.
        width: float
            The width of the line. Set to 0.5 by default.
        label: str
            The name to give to the line in the legend. Set to
            `None` by default.
        """

        if orientation not in ("v", "h"):
            raise ValueError("Invalid line type")

        if orientation == "v":
            self.ax[plot_n].axvline(x=point, color=color, linestyle=style, lw=width, label=label)
            return

        self.ax[plot_n].axhline(y=point, color=color, linestyle=style, lw=width, label=label)

    def turn_scientific(
        self, axis: str, plot_n: Optional[int] = 0, limits: Optional[tuple[int, int] | int] = (0, 0)
    ) -> None:
        """
        Function for setting the ticks of the axis to
        scientific notation.

        Parameters
        ---
        axis: str
            The axis to consider: 'x', 'y', or 'both'.

        Optional parameters
        ---
        plot_n: int
            The number of the canvas to consider. Set to 0
            by default.
        limits: tuple or int
            Use `(m,n)` for scientific notation outside
            10^m-10^n. Use `0` to include all numbers.
            Use `m` to fix the order of magnitude to 10^m.
        """

        if axis not in ("x", "y", "both"):
            raise ValueError(f"{axis} is not a valid axis.")

        if type(limits) == int:
            limits = (limits, limits)

        self.ax[plot_n].ticklabel_format(style="sci", axis=axis, scilimits=(limits[0], limits[1]))

    def set_ticks(
        self,
        axis: str,
        positions: tuple[float, ...],
        labels: tuple[str, ...] = None,
        plot_n: int = 0,
    ) -> None:
        """
        This function modifies the ticks of the axis.

        Parameters
        ---
        axis: str
            `"x"` for x axis, `"y"` for y axis.
        positions: tuple
            A tuple with the positions of the ticks.

        Optional Parameters
        ---
        labels: tuple
            A tuple with the labels of the ticks. Set to 0
            by default, which means labels=positions.
        plot_n: int
            The number of the canvas to consider. Set to 0
            by default.
        """

        if axis not in ("x", "y"):
            raise ValueError("Invalid axis type")

        if axis == "x":
            self.ax[plot_n].set_xticks(positions, labels=labels)
            return

        self.ax[plot_n].set_yticks(positions, labels=labels)

    def __legend(self) -> None:
        """
        This function generates the plot legend.
        """

        logger.info("Called 'Canvas.__legend()'")

        for i in range(self.__n_plots):
            legend = self.ax[i].legend(loc=self.__loc_legend[i], labelspacing=1)

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
            self.fig.savefig(file_path, bbox_inches="tight")
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
