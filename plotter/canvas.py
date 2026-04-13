import logging
from pathlib import Path
from warnings import simplefilter

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .drawable import Drawable
from .helpers import Text

logger = logging.getLogger(__name__)


class _Counters:
    """
    Container class to store the counters of the `Canvas`.

    These counters keep track of the number of objects that have
    to be drawn on each subplot. This way, each time an object
    calls its `draw` function, the label corresponding to said
    object can be retrieved and drawn.
    """

    def __init__(self, values: dict[str, list[int]]) -> None:
        self._values = values

    def __getattr__(self, name: str) -> list[int]:
        """Returns the counters associated with a drawable family."""
        try:
            return self._values[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def is_empty(self) -> bool:
        """Checks if there is any label that should be displayed."""
        for value in self._values.values():
            if sum(value):  # at least a label
                return False

        return True

    @classmethod
    def initialize_counters(cls, n_plots: int) -> "_Counters":
        """Initializes an object filled with zeros."""
        values = {name: [0] * n_plots for name in Drawable.get_label_names()}
        return cls(values)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Canvas:
    """
    Class for creating an empty canvas (xy-plane).

    Attributes:
        text_file (str): The name of the JSON file containing the text to be
            added to the plot.
        rows_cols (tuple[int, int], optional): A tuple with the number of rows
            and columns of subplots. Defaults to (1, 1).
        figsize (tuple[int, int], optional): A tuple containing the dimensions of
            the canvas (width, height). Defaults to (12, 8).
        dpi (int, optional): The number of dots per inch (DPI) of the image.
            Defaults to 150.
        save (str, optional): The name of the file to save the plot to. The
            plots are stored in 'plotter/img/'. Defaults to an empty string.
        figure (Figure): The matplotlib Figure object.
        axes (list[Axes]): A list with the matplotlib Axes object corresponding
            to each subplot.

    Raises:
        ValueError: If the number of columns and/or the number of rows is negative.
    """

    # args
    text_file: str
    rows_cols: tuple[int, int] = (1, 1)
    figsize: tuple[int, int] = (12, 8)
    dpi: int = 150
    save: str = ""
    show: bool = True

    # public attributes
    figure: Figure = Field(init=False)
    axes: list[Axes] = Field(init=False)
    text: Text = Field(init=False)
    counters: _Counters = Field(init=False)

    # private attributes
    _n_plots: int = Field(init=False)
    _loc_legend: list[int] = Field(init=False)

    def __post_init__(self) -> None:
        """Initializes the necessary attributes."""

        n_rows, n_cols = self.rows_cols
        if n_rows < 0 or n_cols < 0:
            raise ValueError("The number of rows and/or columns cannt be negative.")
        self._n_plots = n_rows * n_cols

        # initialize counters
        self.counters = _Counters.initialize_counters(self._n_plots)

        # plot properties
        self.figure, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=self.figsize, dpi=self.dpi)
        if self._n_plots < 2:
            self.axes = [axes]
        else:
            self.axes = list(axes.flatten())

        # plot text
        self.text = Text(self._n_plots)
        self.text.read_json(self.text_file)

        # legend
        self._loc_legend = [0 for _ in range(self._n_plots)]

    def __enter__(self):
        """Defines what happens when the user enters a 'Canvas' context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Defines what happens when the user exits a 'Canvas' context."""
        logger.info("Exiting canvas context")

        if exc_type or exc_val or exc_tb:
            print("\nException type:", exc_type)
            print("\nException value:", exc_val)
            print("\nTraceback:", exc_tb)

            return

        self._legend()  # draw legend if it exists
        self._save()  # save plot to disk
        logger.info("Plot(s) finished")

        # show plot
        if not self.show:
            plt.close()
            return

        plt.show()

    def setup(self, plot_n: int | tuple[int, int] | str = "all", **kwargs) -> None:
        """
        Sets up the properties of the subplots.

        Args:
            plot_n (int, tuple[int, int], str, optional): The index or indices
                of the subplots to configure. Defaults to 'all'. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Keyword Arguments:
            xlim (tuple[float, float]): The limits for the x-axis.
            ylim (tuple[float, float]): The limits for the y-axis.
            xscale (str): The scale for the x-axis ('linear', 'log', 'symlog').
            yscale (str): The scale for the y-axis ('linear', 'log', 'symlog').
            nogrid (bool): If True, removes the grid from the plot.
            inverted (tuple[bool, bool]): A tuple to invert the x and y axes
              respectively (e.g., `(True, False)`).
            legend (int): Force the position of the legend to a specified one.
                See 'plotter/utils/info/legend.png'.

        Raises:
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.debug("Called 'Canvas.setup()'")

        # which plots to target
        if isinstance(plot_n, int):
            limits = (plot_n, plot_n + 1)
        elif isinstance(plot_n, str) and plot_n == "all":
            limits = (0, self._n_plots)
        elif isinstance(plot_n, tuple) and len(plot_n) == 2:
            limits = (plot_n[0], plot_n[1] + 1)
        else:
            raise ValueError(f"'{plot_n}' is not a valid value for 'plot_n'")

        # setup plots
        for plot_i in range(*limits):
            # grid
            no_grid = kwargs.get("nogrid", False)
            if not no_grid:
                self.axes[plot_i].grid(color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)

            # axis limits
            x_min, x_max = kwargs.get("xlim", (None, None))
            if x_min is not None and x_max is not None:
                self.axes[plot_i].set_xlim(left=x_min, right=x_max)

            y_min, y_max = kwargs.get("ylim", (None, None))
            if y_min is not None and y_max is not None:
                self.axes[plot_i].set_ylim(bottom=y_min, top=y_max)

            # invert axis
            invert_x, invert_y = kwargs.get("inverted", (False, False))
            if invert_x:
                self.axes[plot_i].invert_xaxis()
            if invert_y:
                self.axes[plot_i].invert_yaxis()

            # axis scales
            self.axes[plot_i].set_yscale(kwargs.get("yscale", "linear"))
            self.axes[plot_i].set_xscale(kwargs.get("xscale", "linear"))

            # legend
            self._loc_legend[plot_i] = kwargs.get("legend", 0)

            # axis labels
            self.axes[plot_i].set_xlabel(self.text[plot_i].x_label)
            self.axes[plot_i].set_ylabel(self.text[plot_i].y_label)

            # title
            self.axes[plot_i].set_title(self.text[plot_i].title, y=1)

    def draw_line(self, orientation: str, point: float = 0.0, plot_n: int = 0, **kwargs) -> None:
        """
        Draws horizontal and vertical lines on the canvas.

        Args:
            orientation (str): The orientation of the line. Use 'v' for vertical
                or 'h' for horizontal.
            point (float, optional): The coordinate of the line. Defaults to 0.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.

        Keyword Arguments:
            color (str): The color of the line. Defaults to 'black'.
            style (str): The style of the line (e.g., '-', '--', '-.', ':').
                Defaults to '-'.
            width (float): The width of the line. Defaults to 0.5.
            label (str): The label for the line in the legend. Defaults to None.

        Raises:
            ValueError: If the orientation is not 'v' or 'h'.
        """
        logger.debug("Called 'Canvas.draw_line()'")

        if orientation not in ("v", "h"):
            raise ValueError("Invalid line type")

        args = {
            "x" if orientation == "v" else "y": point,
            "color": kwargs.get("color", "black"),
            "linestyle": kwargs.get("linestyle", "-"),
            "lw": kwargs.get("lw", 0.5),
            "label": kwargs.get("label", None),
        }

        if orientation == "v":
            self.axes[plot_n].axvline(**args)
        else:
            self.axes[plot_n].axhline(**args)

    def turn_scientific(self, axis: str, plot_n: int = 0, limits: tuple[int, int] | int = (0, 0)) -> None:
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
                If only one int is passed, m=n is assumed.
                Defaults to (0, 0).

        Raises:
            ValueError: If the axis is not 'x', 'y', or 'both'.
        """
        logger.debug("Called 'Canvas.turn_scientific()'")

        if axis not in ("x", "y", "both"):
            raise ValueError(f"{axis} is not a valid axis.")

        if isinstance(limits, int):
            limits = (limits, limits)

        self.axes[plot_n].ticklabel_format(style="sci", axis=axis, scilimits=limits)

    def set_ticks(self, axis: str, positions: tuple[float, ...], labels: tuple[str, ...] | None = None, plot_n: int = 0) -> None:
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
        logger.debug("Called 'Canvas.set_ticks()'")

        if axis not in ("x", "y"):
            raise ValueError("Invalid axis type")

        if axis == "x":
            self.axes[plot_n].set_xticks(positions, labels=labels)
            return

        self.axes[plot_n].set_yticks(positions, labels=labels)

    def add_scalebar(self, size: int, label: str, plot_n: int = 0, **kwargs) -> None:
        """
        Adds a scalebar (and, thus, removes the axis labels).

        Args:
            size (int): The horizontal size (in coordinates of axis).
            label (str): The label.
            plot_n (int, optional): The index of the subplot. Defaults to 0.

        Keyword Arguments:
            location (str): Where to put the scalebar. Defaults to "upper right".
            color (str): The color. Defaults to "black".
            v_size (int): The vertical size. Defaults to None,
                which results in 1% of the height of the axis.
        """
        logger.info("Called 'Canvas.add_scalebar()")

        v_size = kwargs.get("v_size", None)
        if not v_size:
            _, height = self._get_axis_size(self.figure, self.axes[plot_n])
            v_size = int(0.01 * height)

        scalebar = AnchoredSizeBar(
            self.axes[plot_n].transData,
            size=size,
            label=label,
            loc=kwargs.get("location", "upper right"),
            color=kwargs.get("color", "black"),
            pad=0.5,
            size_vertical=v_size,
            frameon=False,
        )

        self.axes[plot_n].add_artist(scalebar)
        self.axes[plot_n].set_yticks([])
        self.axes[plot_n].set_xticks([])

    def _legend(self) -> None:
        """This function generates the plot legend."""
        logger.info("Called 'Canvas._legend()'")

        # promote UserWarning to error
        simplefilter("error", UserWarning)

        for i in range(self._n_plots):
            try:
                if not self.counters.is_empty():
                    self.axes[i].legend(loc=self._loc_legend[i], labelspacing=1)

                logger.debug(f"Legend added to subplot {i}.")
            except Exception as _:
                logger.warning(f"Subplot {i} has an empty legend.")

    def _save(self) -> None:
        """
        If specified by the user, this function saves
        the plot that has been generated to a file.
        """
        logger.info("Called 'Canvas._save()'")

        if self.save:
            file_path = (Path.cwd() / "img").joinpath(self.save)
            self.figure.savefig(file_path, bbox_inches="tight")
            logger.debug(f"Plot saved to {file_path}")
        else:
            logger.warning("Plot not saved to any file")

    @staticmethod
    def _get_axis_size(figure: Figure, axes: Axes) -> tuple[int, int]:
        """
        Obtains the size (px) of the axes of a subplot.

        Args:
            fig (Figure): The Figure (see matplotlib doc).
            ax (Axes): The plot area in question.

        Returns:
            tuple[int, int]: A tuple with (width, height).
        """
        logger.info("Called 'Canvas._get_axis_size()'")

        bbox = axes.get_window_extent().transformed(figure.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        width *= figure.dpi
        height *= figure.dpi

        return int(width), int(height)
