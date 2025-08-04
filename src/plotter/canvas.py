import json
import logging
import pathlib
import numpy as np
from typing import Optional
import matplotlib.pyplot as plt

from .functions import setup_logging

plt.style.use(pathlib.Path("./plotter/utils/style.mplstyle"))
logging.getLogger("matplotlib").setLevel(logging.CRITICAL)  # remove matplotlib logger
logging.getLogger("PIL").setLevel(logging.CRITICAL)  # remove PIL logger

logger = logging.getLogger(__name__)


__all__ = ["Canvas"]


class _Text:
    """
    Class for storing and accessing the text to be displayed on the canvas.

    Args:
        text_file (str): The name of the JSON file where the text for the canvases is stored.
        n_plots (int): The number of subplots in the canvas.
    """

    BLUEPRINT = {
        "title": "",
        "abscissa": "",
        "ordinate": "",
        "datasets": [""],
        "functions": [""],
        "histograms": [""],
    }

    def __init__(self, text_file: str, n_plots: int) -> None:

        logger.info("'Text' object created")

        self.__n_plots = n_plots

        self.title = ["" for _ in range(self.__n_plots)]
        self.abscissa = ["" for _ in range(self.__n_plots)]
        self.ordinate = ["" for _ in range(self.__n_plots)]
        self.datasets = [[] for _ in range(self.__n_plots)]
        self.functions = [[] for _ in range(self.__n_plots)]
        self.histograms = [[] for _ in range(self.__n_plots)]

        # add json extension if necessary
        if text_file[-5:] != ".json":
            text_file += ".json"
            logger.debug("Appended json extension to text file.")
        file_path = pathlib.Path("./plotter/text").joinpath(text_file)

        try:
            with open(file_path, "r") as json_file:
                logger.debug(f"Opened '{file_path}'")
                self.__data_dict = json.load(json_file)
                self.__get_data()
        except FileNotFoundError as _:
            logger.debug(f"Creating {file_path}.")

            # create json file
            with open(file_path, "w") as json_file:
                json.dump([_Text.BLUEPRINT for _ in range(self.__n_plots)], json_file)

            # read newly created file
            with open(file_path, "r") as json_file:
                logger.debug(f"Opened '{file_path}'")
                self.__data_dict = json.load(json_file)
                self.__get_data()
        except json.JSONDecodeError as _:
            logger.error(f"Impossible to open {file_path}")

    def __get_data(self) -> None:
        """
        Pulls data from the JSON file and stores it in the class data members.
        """

        logger.info("Called 'Text.__get_data()'")

        for i in range(self.__n_plots):
            self.title[i] = str(self.__data_dict[i]["title"])
            self.abscissa[i] = str(self.__data_dict[i]["abscissa"])
            self.ordinate[i] = str(self.__data_dict[i]["ordinate"])

            self.datasets[i] = self.__data_dict[i]["datasets"]
            for j in self.datasets:
                j = str(j)

            self.functions[i] = self.__data_dict[i]["functions"]
            for j in self.functions:
                j = str(j)

            self.histograms[i] = self.__data_dict[i]["histograms"]
            for j in self.histograms:
                j = str(j)

        logger.debug(f"Titles: {self.title}")
        logger.debug(f"Abscissas: {self.abscissa}")
        logger.debug(f"Ordinates: {self.ordinate}")
        logger.debug(f"Datasets: {self.datasets}")
        logger.debug(f"Functions: {self.functions}")
        logger.debug(f"Histograms: {self.histograms}")


class Canvas:
    """
    Class for creating a canvas (xy-plane) to plot datasets and graphs.

    Args:
        text_file (str): The name of the JSON file containing the text to be
            added to the plot.
        rows_cols (tuple[int, int], optional): A tuple with the number of rows
            and columns of subplots. Defaults to (1, 1).
        fs (tuple[int, int], optional): A tuple containing the dimensions of
            the canvas (width, height). Defaults to (12, 8).
        dpi (int, optional): The number of dots per inch (DPI) of the image.
            Defaults to 150.
        save (str, optional): The name of the file to save the plot to. The
            plots are stored in 'plotter/img/'. Defaults to an empty string.
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

        self.__init_counters = [0 for _ in range(self.__n_plots)]
        self.counter_scatter_plots = self.__init_counters.copy()
        self.counter_plots = self.__init_counters.copy()
        self.counter_histograms = self.__init_counters.copy()

        # plot properties
        self.fig, self.ax = plt.subplots(nrows=rows_cols[0], ncols=rows_cols[1], figsize=(fs[0], fs[1]), dpi=dpi)
        if self.__n_plots < 2:
            self.ax = np.array([self.ax, None])
        else:
            self.ax = self.ax.flatten()

        # plot text
        self.text = _Text(text_file, self.__n_plots)

        # save plot
        self.__save_plot = save

        # legend
        self.__loc_legend = [0] * self.__n_plots

    def setup(self, plot_n: Optional[int | tuple[int, int] | str] = 0, **kwargs) -> None:
        """
        Sets up the properties of the subplots.

        Args:
            plot_n (int, tuple[int, int], str, optional): The index or indices
                of the subplots to configure. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).
            **kwargs: Additional keyword arguments to configure the plots.
                - xlim (tuple[float, float]): The limits for the x-axis.
                - ylim (tuple[float, float]): The limits for the y-axis.
                - xscale (str): The scale for the x-axis ('linear', 'log', 'symlog').
                - yscale (str): The scale for the y-axis ('linear', 'log', 'symlog').
                - nogrid (bool): If True, removes the grid from the plot.
                - inverted (tuple[bool, bool]): A tuple to invert the x and y axes
                    respectively (e.g., `(True, False)`).
                - legend (int): Force the position of the legend to a specified one.

        Raises:
            ValueError: If 'plot_n' is not a valid value.
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
        Draws horizontal and vertical lines on the canvas.

        Args:
            orientation (str): The orientation of the line. Use 'v' for vertical
                or 'h' for horizontal.
            point (float, optional): The coordinate of the line. Defaults to 0.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            color (str, optional): The color of the line. Defaults to 'black'.
            style (str, optional): The style of the line (e.g., '-', '--', '-.', ':').
                Defaults to '-'.
            width (float, optional): The width of the line. Defaults to 0.5.
            label (str, optional): The label for the line in the legend. Defaults to None.

        Raises:
            ValueError: If the orientation is not 'v' or 'h'.
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
        Sets the ticks of an axis to scientific notation.

        Args:
            axis (str): The axis to modify: 'x', 'y', or 'both'.
            plot_n (int, optional): The index of the subplot to consider.
                Defaults to 0.
            limits (tuple[int, int] or int, optional): Controls the scientific
                notation.
                - `(m, n)`: Scientific notation is used for numbers outside
                  10^m to 10^n.
                - `0`: Scientific notation is used for all numbers.
                - `m`: Fixes the order of magnitude to 10^m.
                Defaults to (0, 0).

        Raises:
            ValueError: If the axis is not 'x', 'y', or 'both'.
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
        Modifies the ticks of an axis.

        Args:
            axis (str): The axis to modify: 'x' or 'y'.
            positions (tuple[float, ...]): A tuple with the positions of the ticks.
            labels (tuple[str, ...], optional): A tuple with the labels for the
                ticks. If None, the labels will be the same as the positions.
                Defaults to None.
            plot_n (int, optional): The index of the subplot to consider.
                Defaults to 0.

        Raises:
            ValueError: If the axis is not 'x' or 'y'.
        """

        if axis not in ("x", "y"):
            raise ValueError("Invalid axis type")

        if axis == "x":
            self.ax[plot_n].set_xticks(positions, labels=labels)
            return

        self.ax[plot_n].set_yticks(positions, labels=labels)

    def __legend(self) -> None:
        """This function generates the plot legend."""

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
        Finalizes and renders the plot.

        This method should be called at the end of the plotting process, as any
        commands after it will not affect the plot.

        Args:
            show (bool, optional): Whether to display the plot. Defaults to True.
        """

        logger.info("Called 'Canvas.end()'")

        # if only Hist2D, no legend
        if self.__init_counters not in (self.counter_histograms, self.counter_plots, self.counter_scatter_plots):
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
