from logging import getLogger
from pathlib import Path
from warnings import catch_warnings, simplefilter

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.transforms import TransformedBbox
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from mpl_toolkits.axes_grid1.inset_locator import (BboxConnector, BboxPatch,
                                                   inset_axes)
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .drawables import Drawable
from .helpers import PlotN, PlotText, Text

logger = getLogger(__name__)


def _oriented_limits(limits: tuple[float, float], reference: tuple[float, float]) -> tuple[float, float]:
    """
    Orders `limits` to increase or decrease like `reference` does.

    Matplotlib inverts an Axes' limits (e.g. `imshow`'s default `origin="upper"`
    leaves the y-axis decreasing) to control which direction is "up" on screen;
    this keeps a newly-set pair of limits visually consistent with that.

    Args:
        limits (tuple[float, float]): The limits to order, in either direction.
        reference (tuple[float, float]): The existing limits whose direction to match.

    Returns:
        tuple[float, float]: `limits`, sorted to match `reference`'s direction.
    """
    low, high = min(limits), max(limits)
    return (low, high) if reference[0] <= reference[1] else (high, low)


# matplotlib's mark_inset corner codes (1=upper right, 2=upper left, 3=lower left,
# 4=lower right), as (is_right, is_upper) flags and back
_LOC_CORNERS = {1: (True, True), 2: (False, True), 3: (False, False), 4: (True, False)}
_CORNERS_LOC = {corner: loc for loc, corner in _LOC_CORNERS.items()}


def _reoriented_loc(loc: int, x_inverted: bool, y_inverted: bool) -> int:
    """
    Remaps a `mark_inset` corner code so it keeps pointing at the same visual corner
    when the Axes it refers to has an inverted x- and/or y-axis.

    `mark_inset`'s corner codes are defined in terms of an Axes' raw (x0,y0)-(x1,y1)
    limits, which only match their documented visual meaning (e.g. 1=upper right) when
    both axes increase left-to-right/bottom-to-top; an inverted axis flips that.

    Args:
        loc (int): The requested corner (1-4, matplotlib's convention).
        x_inverted (bool): Whether the Axes' x-axis decreases instead of increasing.
        y_inverted (bool): Whether the Axes' y-axis decreases instead of increasing.

    Returns:
        int: The corner code to pass to `mark_inset` to get the same visual corner.
    """
    is_right, is_upper = _LOC_CORNERS[loc]
    if x_inverted:
        is_right = not is_right
    if y_inverted:
        is_upper = not is_upper
    return _CORNERS_LOC[(is_right, is_upper)]


def _draw_zoom_indicator(parent_axes: Axes, inset_axes: Axes, loc1: int, loc2: int, x_inverted: bool, y_inverted: bool, **kwargs) -> None:
    """
    Draws a rectangle around an inset's region on its source subplot, connected to the
    inset panel by two lines.

    Behaves like `mpl_toolkits.axes_grid1.inset_locator.mark_inset`, except the two ends
    of each connector line can use different corner codes: `inset_axes`'s own on-screen
    box is never inverted, but the rectangle (`inset_axes.viewLim` transformed into the
    parent's data space) is, whenever `inset_axes`'s axes are — so only the rectangle's
    corner codes are remapped (via `_reoriented_loc`) to keep pointing at the same visual
    corner; `mark_inset` itself has no way to do this since it applies one corner code to
    both ends.

    Args:
        parent_axes (Axes): The source subplot to draw the rectangle on.
        inset_axes (Axes): The inset panel the rectangle is connected to.
        loc1 (int): The corner connected by the first line (matplotlib corner codes,
            1-4: upper right, upper left, lower left, lower right).
        loc2 (int): The corner connected by the second line.
        x_inverted (bool): Whether `inset_axes`'s x-axis decreases instead of increasing.
        y_inverted (bool): Whether `inset_axes`'s y-axis decreases instead of increasing.

    Keyword Arguments:
        Patch properties (e.g. `ec`, `fc`) for the rectangle and connector lines.
    """
    rect = TransformedBbox(inset_axes.viewLim, parent_axes.transData)
    kwargs.setdefault("fill", bool({"fc", "facecolor", "color"}.intersection(kwargs)))

    parent_axes.add_patch(BboxPatch(rect, **kwargs))

    for loc in (loc1, loc2):
        connector = BboxConnector(inset_axes.bbox, rect, loc1=loc, loc2=_reoriented_loc(loc, x_inverted, y_inverted), **kwargs)
        connector.set_clip_on(False)
        inset_axes.add_patch(connector)


def _configure_axes(axes: Axes, text: PlotText, **kwargs) -> None:
    """
    Applies grid, limits, scale, inversion, labels, and title to a single `Axes`.

    Args:
        axes (Axes): The Axes object to configure.
        text (PlotText): The title and axis labels to apply.

    Keyword Arguments:
        See `Canvas.setup`.
    """
    # grid
    no_grid = kwargs.get("nogrid", False)
    no_grid_x, no_grid_y = no_grid if isinstance(no_grid, tuple) else (no_grid, no_grid)
    if not no_grid_x:
        axes.grid(axis="x", color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)
    if not no_grid_y:
        axes.grid(axis="y", color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)

    # axis limits
    x_min, x_max = kwargs.get("xlim", (None, None))
    if x_min is not None and x_max is not None:
        axes.set_xlim(left=x_min, right=x_max)

    y_min, y_max = kwargs.get("ylim", (None, None))
    if y_min is not None and y_max is not None:
        axes.set_ylim(bottom=y_min, top=y_max)

    # invert axis
    invert_x, invert_y = kwargs.get("inverted", (False, False))
    if invert_x:
        axes.invert_xaxis()
    if invert_y:
        axes.invert_yaxis()

    # axis scales
    axes.set_yscale(kwargs.get("yscale", "linear"))
    axes.set_xscale(kwargs.get("xscale", "linear"))

    # axis labels
    axes.set_xlabel(text.x_label)
    axes.set_ylabel(text.y_label)

    # title
    axes.set_title(text.title, y=1)


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
class ZoomInset:
    """
    A single zoomed-in inset panel returned by `Canvas.add_zoom_inset`.

    Exposes the same `axes`/`counters`/`text`/`figure` surface as `Canvas`, so any
    `Drawable` can be drawn into it exactly like a real `Canvas` subplot (e.g.
    `some_drawable.draw(inset)`). Also exposes `setup` to configure its `Axes`.
    Other cosmetic `Canvas` helpers (`draw_line`, `draw_band`, `add_text`, ...) are not
    available on it — use `inset.axes[0]` directly for those.

    Attributes:
        axes (list[Axes]): A single-element list containing the inset `Axes`.
        figure (Figure): The parent `Canvas`'s Figure (the inset lives on it).
        text (Text): Blank title/axis-labels/label-lists for the panel — there is no
            JSON slot for an ad hoc inset.
        counters (_Counters): Fresh, zeroed counters scoped to this one panel.
    """

    axes: list[Axes]

    figure: Figure = Field(init=False)
    text: Text = Field(init=False)
    counters: _Counters = Field(init=False)

    def __post_init__(self) -> None:
        """Initializes the blank text and zeroed counters for the panel."""
        self.figure = self.axes[0].figure  # type: ignore
        self.text = Text(1)
        self.text.subplots_text = [PlotText.get_empy_text()]
        self.counters = _Counters.initialize_counters(1)

    def setup(self, **kwargs) -> None:
        """
        Sets up the properties of the panel's `Axes`.

        Keyword Arguments:
            xlim (tuple[float, float]): The limits for the x-axis.
            ylim (tuple[float, float]): The limits for the y-axis.
            xscale (str): The scale for the x-axis ('linear', 'log', 'symlog').
            yscale (str): The scale for the y-axis ('linear', 'log', 'symlog').
            nogrid (bool or tuple[bool, bool]): Controls grid removal.
                - `bool`: Removes the grid from both axes.
                - `tuple`: `(x, y)` to independently remove the grid from the
                    x and/or y axis (e.g., `(True, False)` removes only the x grid).
                Defaults to `False`.
            inverted (tuple[bool, bool]): A tuple to invert the x and y axes
              respectively (e.g., `(True, False)`).
        """
        logger.info("Called 'ZoomInset.setup()'")
        _configure_axes(self.axes[0], self.text[0], **kwargs)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Canvas:
    """
    Class for creating an empty canvas (xy-plane).

    Attributes:
        text_file (str): The name of the JSON file containing the text to be
            added to the plot.
        rows_cols (tuple[int, int], optional): A tuple with the number of rows
            and columns of subplots. Defaults to (1, 1).
        figsize (tuple[float, float], optional): A tuple containing the dimensions of
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
    figsize: tuple[float, float] = (12.0, 8.0)
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
    _ncols_legend: list[int] = Field(init=False)

    def __post_init__(self) -> None:
        """Initializes the necessary attributes."""

        n_rows, n_cols = self.rows_cols
        if n_rows < 1 or n_cols < 1:
            raise ValueError("The number of rows and columns must be at least 1.")
        self._n_plots = n_rows * n_cols

        # initialize counters
        self.counters = _Counters.initialize_counters(self._n_plots)

        # plot properties
        self.figure, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=self.figsize, dpi=self.dpi)
        # Canvas/Colorbar manage subplot positions explicitly (e.g. Colorbar.draw()'s
        # manual set_position() calls); a layout engine would silently re-run on every
        # render and undo that. plt.subplots() enables one automatically whenever
        # rcParams["figure.autolayout"] or ["figure.constrained_layout.use"] is True
        # (e.g. set by the user's own matplotlib config or another imported library),
        # regardless of any style plotter itself applies -- always disable it.
        self.figure.set_layout_engine("none")
        if self._n_plots < 2:
            self.axes = [axes]
        else:
            self.axes = list(axes.flatten())

        # plot text
        self.text = Text(self._n_plots)
        self.text.read_json(self.text_file)

        # legend
        self._loc_legend = [0 for _ in range(self._n_plots)]
        self._ncols_legend = [1 for _ in range(self._n_plots)]

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

            plt.close(self.figure)
            return

        self._legend()  # draw legend if it exists
        self._save()  # save plot to disk
        logger.info("Plot(s) finished")

        # show plot
        if not self.show:
            plt.close()
            return

        plt.show()

    def plot_indices(self, plot_n: PlotN | None = None, row: int | None = None, col: int | None = None) -> list[int]:
        """
        Resolves 'plot_n', 'row', or 'col' into the list of subplot indices they refer to.

        Exactly one of 'plot_n', 'row', 'col' must be given. `axes` is flattened
        row-major, so a row is a contiguous range of indices while a column is a
        stride of `n_cols`.

        Args:
            plot_n (PlotN, optional): The index or indices of the
                subplots. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).
            row (int, optional): A 0-based row index in the `rows_cols` grid;
                resolves to every subplot in that row.
            col (int, optional): A 0-based column index in the `rows_cols` grid;
                resolves to every subplot in that column.

        Returns:
            list[int]: The resolved, ordered subplot indices.

        Raises:
            ValueError: If zero, or more than one, of 'plot_n', 'row', 'col' is given.
            ValueError: If 'row' or 'col' is out of range for `rows_cols`.
            ValueError: If 'plot_n' is not a valid value.
        """
        n_rows, n_cols = self.rows_cols
        if sum(value is not None for value in (plot_n, row, col)) != 1:
            raise ValueError("Exactly one of 'plot_n', 'row', or 'col' must be given.")

        if row is not None:
            if not 0 <= row < n_rows:
                raise ValueError(f"'row' must be between 0 and {n_rows - 1}.")
            return list(range(row * n_cols, (row + 1) * n_cols))

        if col is not None:
            if not 0 <= col < n_cols:
                raise ValueError(f"'col' must be between 0 and {n_cols - 1}.")
            return list(range(col, self._n_plots, n_cols))

        if isinstance(plot_n, int):
            limits = (plot_n, plot_n + 1)
        elif isinstance(plot_n, str) and plot_n == "all":
            limits = (0, self._n_plots)
        elif isinstance(plot_n, tuple) and len(plot_n) == 2:
            limits = (plot_n[0], plot_n[1] + 1)
        else:
            raise ValueError(f"'{plot_n}' is not a valid value for 'plot_n'")

        return list(range(*limits))

    def setup(self, plot_n: PlotN = "all", **kwargs) -> None:
        """
        Sets up the properties of the subplots.

        Args:
            plot_n (PlotN, optional): The index or indices
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
            nogrid (bool or tuple[bool, bool]): Controls grid removal.
                - `bool`: Removes the grid from both axes.
                - `tuple`: `(x, y)` to independently remove the grid from the
                    x and/or y axis (e.g., `(True, False)` removes only the x grid).
                Defaults to `False`.
            inverted (tuple[bool, bool]): A tuple to invert the x and y axes
              respectively (e.g., `(True, False)`).
            legend (int): Force the position of the legend to a specified one.
                See 'plotter/utils/info/legend.png'.
            leg_ncols (int): The number of columns to arrange the legend entries into.
                Defaults to 1.

        Raises:
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.setup()'")

        for plot_i in self.plot_indices(plot_n):
            _configure_axes(self.axes[plot_i], self.text[plot_i], **kwargs)

            # legend
            self._loc_legend[plot_i] = kwargs.get("legend", 0)
            self._ncols_legend[plot_i] = kwargs.get("leg_ncols", 1)

    def draw_line(self, orientation: str, point: float = 0.0, plot_n: PlotN = 0, **kwargs) -> None:
        """
        Draws horizontal and vertical lines on the canvas.

        Args:
            orientation (str): The orientation of the line. Use 'v' for vertical
                or 'h' for horizontal.
            point (float, optional): The coordinate of the line. Defaults to 0.
            plot_n (PlotN, optional): The index or indices
                of the subplots to draw on. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Keyword Arguments:
            color (str): The color of the line. Defaults to 'black'.
            linestyle (str): The style of the line (e.g., '-', '--', '-.', ':').
                Defaults to '-'.
            lw (float): The width of the line. Defaults to 0.5.
            alpha (float): The opacity of the line. Defaults to 1.0.
            label (str): The label for the line in the legend. Defaults to None.
            zorder (float): The drawing order of the line. Defaults to 2.

        Raises:
            ValueError: If the orientation is not 'v' or 'h'.
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.draw_line()'")

        if orientation not in ("v", "h"):
            raise ValueError("Invalid line type")

        args = {
            "x" if orientation == "v" else "y": point,
            "color": kwargs.get("color", "black"),
            "linestyle": kwargs.get("linestyle", "-"),
            "lw": kwargs.get("lw", 0.5),
            "alpha": kwargs.get("alpha", 1.0),
            "label": kwargs.get("label", None),
            "zorder": kwargs.get("zorder", 2),
        }

        for plot_i in self.plot_indices(plot_n):
            if orientation == "v":
                self.axes[plot_i].axvline(**args)
            else:
                self.axes[plot_i].axhline(**args)

    def draw_band(self, orientation: str, low: float, high: float, plot_n: PlotN = 0, **kwargs) -> None:
        """
        Draws a shaded horizontal or vertical band on the canvas.

        Args:
            orientation (str): The orientation of the band. Use 'v' for a vertical
                band (spanning between two x-coordinates) or 'h' for a horizontal
                band (spanning between two y-coordinates).
            low (float): The lower edge of the band.
            high (float): The upper edge of the band.
            plot_n (PlotN, optional): The index or indices
                of the subplots to draw on. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Keyword Arguments:
            color (str): The color of the band. Defaults to 'black'.
            linestyle (str): The style of the band's border (e.g., '-', '--', '-.', ':').
                Defaults to '-'.
            lw (float): The width of the band's border. Defaults to 0.0 (no visible border).
            alpha (float): The opacity of the band. Defaults to 0.2.
            label (str): The label for the band in the legend. Defaults to None.

        Raises:
            ValueError: If the orientation is not 'v' or 'h'.
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.draw_band()'")

        if orientation not in ("v", "h"):
            raise ValueError("Invalid band type")

        args = {
            "color": kwargs.get("color", "black"),
            "linestyle": kwargs.get("linestyle", "-"),
            "lw": kwargs.get("lw", 0.0),
            "alpha": kwargs.get("alpha", 0.2),
            "label": kwargs.get("label", None),
        }

        for plot_i in self.plot_indices(plot_n):
            if orientation == "v":
                self.axes[plot_i].axvspan(low, high, **args)
            else:
                self.axes[plot_i].axhspan(low, high, **args)

    def add_text(
        self, text: str, position: tuple[float, float], plot_n: PlotN = 0, point: tuple[float, float] | None = None, **kwargs
    ) -> None:
        """
        Adds a text label to the canvas.

        Args:
            text (str): The text to display.
            position (tuple[float, float]): The position of the text in data
                coordinates.
            plot_n (PlotN, optional): The index or indices
                of the subplots to draw on. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).
            point (tuple[float, float] | None, optional): A point to annotate.
                When provided, an arrow is drawn from the text to this point.

        Keyword Arguments:
            color (str): The text color. Defaults to 'black'.
            fontsize (float): The font size. Defaults to Matplotlib's default.
            ha (str): Horizontal alignment. Defaults to 'center'.
            va (str): Vertical alignment. Defaults to 'center'.
            rotation (float): The text rotation in degrees. Defaults to 0.
            arrowprops (dict): Arrow styling passed to `Axes.annotate`.

        Raises:
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.add_text()'")

        text_kwargs = {
            "color": kwargs.get("color", "black"),
            "fontsize": kwargs.get("fontsize", None),
            "ha": kwargs.get("ha", "center"),
            "va": kwargs.get("va", "center"),
            "rotation": kwargs.get("rotation", 0),
        }
        text_kwargs = {key: value for key, value in text_kwargs.items() if value is not None}
        arrowprops = kwargs.get("arrowprops", {"arrowstyle": "->"})

        for plot_i in self.plot_indices(plot_n):
            if point is None:
                self.axes[plot_i].text(position[0], position[1], text, **text_kwargs)
                continue

            self.axes[plot_i].annotate(text, xy=point, xytext=position, arrowprops=arrowprops, **text_kwargs)

    def add_point(self, position: tuple[float, float], label: str | None = None, plot_n: PlotN = 0, **kwargs) -> None:
        """
        Draws a single point on the canvas, with an optional nearby label.

        Args:
            position (tuple[float, float]): The (x, y) position of the point, in data
                coordinates.
            label (str, optional): Text to draw next to the point, offset from it by
                `label_offset`. Defaults to None (no label).
            plot_n (PlotN, optional): The index or indices
                of the subplots to draw on. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Keyword Arguments:
            marker (str): The marker style. Defaults to 'o'.
            color (str): The marker color. Defaults to 'black'.
            markersize (float): The marker size. Defaults to Matplotlib's default.
            alpha (float): The marker opacity. Defaults to 1.0.
            label_offset (tuple[float, float]): The (x, y) offset of the label from
                the point, in points. Defaults to (10, 10).
            label_color (str): The label text color. Defaults to 'black'.
            label_fontsize (float): The label font size. Defaults to Matplotlib's default.
            label_ha (str): The label's horizontal alignment. Defaults to 'left'.
            label_va (str): The label's vertical alignment. Defaults to 'bottom'.
            label_arrow (bool or dict): If True, draws a default arrow (`{"arrowstyle":
                "->"}`) from the label to the point; a dict draws one styled with those
                `Axes.annotate` arrow properties instead. Defaults to False (no arrow).

        Raises:
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.add_point()'")

        label_kwargs = {key.removeprefix("label_"): value for key, value in kwargs.items() if key.startswith("label_")}

        marker_args = {
            "marker": kwargs.get("marker", "o"),
            "color": kwargs.get("color", "black"),
            "markersize": kwargs.get("markersize", None),
            "alpha": kwargs.get("alpha", 1.0),
            "linestyle": "none",
        }
        marker_args = {key: value for key, value in marker_args.items() if value is not None}

        text_args = {
            "color": label_kwargs.get("color", "black"),
            "fontsize": label_kwargs.get("fontsize", None),
            "ha": label_kwargs.get("ha", "left"),
            "va": label_kwargs.get("va", "bottom"),
        }
        text_args = {key: value for key, value in text_args.items() if value is not None}
        label_offset = label_kwargs.get("offset", (10, 10))

        arrow = label_kwargs.get("arrow", False)
        if arrow:
            text_args["arrowprops"] = arrow if isinstance(arrow, dict) else {"arrowstyle": "->"}

        for plot_i in self.plot_indices(plot_n):
            self.axes[plot_i].plot(*position, **marker_args)

            if label is not None:
                self.axes[plot_i].annotate(label, xy=position, xytext=label_offset, textcoords="offset points", **text_args)

    def turn_scientific(self, axis: str, plot_n: PlotN = 0, limits: tuple[int, int] | int = (0, 0)) -> None:
        """
        Sets the ticks of an axis to scientific notation.

        Args:
            axis (str): The axis to modify: 'x', 'y', or 'both'.
            plot_n (PlotN, optional): The index or indices
                of the subplots to consider. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).
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
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.turn_scientific()'")

        if axis not in ("x", "y", "both"):
            raise ValueError(f"{axis} is not a valid axis.")

        if isinstance(limits, int):
            limits = (limits, limits)

        for plot_i in self.plot_indices(plot_n):
            self.axes[plot_i].ticklabel_format(style="sci", axis=axis, scilimits=limits)

    def set_ticks(self, axis: str, positions: tuple[float, ...], labels: tuple[str, ...] | None = None, plot_n: PlotN = 0) -> None:
        """
        Modifies the ticks of an axis.

        Args:
            axis (str): The axis to modify: 'x' or 'y'.
            positions (tuple[float, ...]): A tuple with the positions of the ticks.
            labels (tuple[str, ...], optional): A tuple with the labels for the
                ticks. If None, the labels will be the same as the positions.
                Defaults to None.
            plot_n (PlotN, optional): The index or indices
                of the subplots to consider. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Raises:
            ValueError: If the axis is not 'x' or 'y'.
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.set_ticks()'")

        if axis not in ("x", "y"):
            raise ValueError("Invalid axis type")

        for plot_i in self.plot_indices(plot_n):
            if axis == "x":
                self.axes[plot_i].set_xticks(positions, labels=labels)
                continue

            self.axes[plot_i].set_yticks(positions, labels=labels)

    def remove_ticks(self, axis: str, plot_n: PlotN = 0) -> None:
        """
        Removes the ticks (and their labels) from an axis.

        Args:
            axis (str): The axis to clear: 'x', 'y', or 'both'.
            plot_n (PlotN, optional): The index or indices
                of the subplots to consider. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Raises:
            ValueError: If the axis is not 'x', 'y', or 'both'.
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.remove_ticks()'")

        if axis not in ("x", "y", "both"):
            raise ValueError(f"{axis} is not a valid axis.")

        for single_axis in ("x", "y") if axis == "both" else (axis,):
            self.set_ticks(single_axis, (), plot_n=plot_n)

    def add_scalebar(self, size: float, label: str, plot_n: PlotN = 0, **kwargs) -> None:
        """
        Adds a scalebar (and, thus, removes the axis labels).

        Args:
            size (float): The horizontal size (in coordinates of axis).
            label (str): The label (e.g., "1 cm", "10 μm").
            plot_n (PlotN, optional): The index or indices
                of the subplots to target. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Keyword Arguments:
            location (str, tuple[float, float]): Where to put the scalebar.
                Either a named matplotlib location (e.g. "upper right",
                the default) or an (x, y) position in axes fraction
                coordinates (0-1 each, independent of the data range), which
                centers the scalebar exactly at that point.
            color (str): The color. Defaults to "black".
            v_size (float): The vertical size. Defaults to None,
                which results in 1% of the height of the axis.

        Raises:
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.add_scalebar()'")

        location = kwargs.get("location", "upper right")

        for plot_i in self.plot_indices(plot_n):
            axis = self.axes[plot_i]

            # Calculate vertical size if not provided
            v_size = kwargs.get("v_size", None)
            if v_size is None:
                # Calculate v_size as 1% of the y-axis data range
                y_min, y_max = axis.get_ylim()
                y_range = abs(y_max - y_min)
                v_size = 0.01 * y_range

            if isinstance(location, str):
                loc, bbox_to_anchor, bbox_transform = location, None, None
            else:
                # An explicit (x, y) always anchors the box's center to that point.
                loc, bbox_to_anchor, bbox_transform = "center", location, axis.transAxes

            scalebar = AnchoredSizeBar(
                axis.transData,
                size=size,
                label=label,
                loc=loc,
                bbox_to_anchor=bbox_to_anchor,
                bbox_transform=bbox_transform,
                color=kwargs.get("color", "black"),
                pad=0.5,
                size_vertical=v_size,
                frameon=False,
            )

            axis.add_artist(scalebar)
            axis.set_yticks([])
            axis.set_xticks([])

    def _add_zoom_inset(self, xlim: tuple[float, float], ylim: tuple[float, float], plot_i: int, **kwargs) -> ZoomInset:
        """
        Adds a single zoomed-in inset panel for one subplot.

        See `add_zoom_inset` for the meaning of the arguments and keyword arguments.

        Args:
            xlim (tuple[float, float]): The x-axis limits of the region to zoom into.
            ylim (tuple[float, float]): The y-axis limits of the region to zoom into.
            plot_i (int): The index of the subplot to zoom into.

        Returns:
            ZoomInset: The panel to draw the zoomed-in content into.
        """
        source = self.axes[plot_i]
        axins = inset_axes(
            source,
            width=kwargs.get("width", "30%"),
            height=kwargs.get("height", "30%"),
            loc=kwargs.get("location", "upper right"),
        )
        x_inverted = source.get_xlim()[0] > source.get_xlim()[1]
        y_inverted = source.get_ylim()[0] > source.get_ylim()[1]

        axins.set_xlim(*_oriented_limits(xlim, source.get_xlim()))
        axins.set_ylim(*_oriented_limits(ylim, source.get_ylim()))

        if not kwargs.get("ticks", False):
            axins.set_xticks([])
            axins.set_yticks([])

        edgecolor = kwargs.get("edgecolor", "black")
        linewidth = kwargs.get("linewidth", 0.5)

        # outline of the inset panel itself, so it visually matches its own rectangle/lines
        for spine in axins.spines.values():
            spine.set_edgecolor(edgecolor)
            spine.set_linewidth(linewidth)

        _draw_zoom_indicator(
            source,
            axins,
            loc1=kwargs.get("loc1", 2),
            loc2=kwargs.get("loc2", 4),
            x_inverted=x_inverted,
            y_inverted=y_inverted,
            fc="none",
            ec=edgecolor,
            lw=linewidth,
        )

        return ZoomInset(axes=[axins])

    def add_zoom_inset(
        self, xlim: tuple[float, float], ylim: tuple[float, float], plot_n: PlotN = 0, **kwargs
    ) -> ZoomInset | list[ZoomInset]:
        """
        Adds a zoomed-in inset panel showing a region of one or more subplots.

        Each source subplot gets a rectangle around the requested region, connected
        to its own inset panel by two lines. Each panel starts empty: draw into it
        via `some_drawable.draw(panel)`, exactly like a real `Canvas` subplot.

        Args:
            xlim (tuple[float, float]): The x-axis limits of the region to zoom into, in
                either order — each panel matches whichever direction (increasing or
                decreasing) its own source subplot's x-axis already has (e.g. an image
                drawn with the default `origin="upper"` has a decreasing y-axis).
            ylim (tuple[float, float]): The y-axis limits of the region to zoom into,
                same ordering behavior as `xlim`.
            plot_n (PlotN, optional): The index or indices of the
                subplots to zoom into. Defaults to 0. Options:
                - int: The index of a single plot (e.g., 0, 1).
                - str: 'all' to target all plots.
                - tuple[int, int]: A range of plots to target, from
                    `inf` to `sup` (inclusive).

        Keyword Arguments:
            location (str): Where to place the inset panel. Defaults to "upper right".
            width (str or float): The width of the inset panel, as a percentage of the
                subplot (e.g. "30%") or an absolute size in inches. Defaults to "30%".
            height (str or float): The height of the inset panel, same format as `width`.
                Defaults to "30%".
            loc1 (int): The corner of the region rectangle connected to the inset panel
                by the first line (Matplotlib corner codes, 1-4: upper right, upper left,
                lower left, lower right). Always refers to the visual corner, regardless
                of whether the source subplot's axes are inverted. Defaults to 2.
            loc2 (int): The corner connected by the second line. Defaults to 4.
            edgecolor (str): The color of the region rectangle, connector lines, and the
                inset panel's own outline (its Axes spines) — all three always share this
                one color. Defaults to "black".
            linewidth (float): The line width of the region rectangle, connector lines,
                and the inset panel's own outline — all three always share this one width.
                Defaults to 0.5.
            ticks (bool): If True, keeps the tick marks and labels on the inset panel.
                Defaults to False, for a clean panel showing only the zoomed-in content.

        Returns:
            ZoomInset | list[ZoomInset]: The panel to draw the zoomed-in content into,
                when `plot_n` is a single int; otherwise, one panel per targeted
                subplot, in subplot order.

        Raises:
            ValueError: If 'plot_n' is not a valid value.
        """
        logger.info("Called 'Canvas.add_zoom_inset()'")

        insets = [self._add_zoom_inset(xlim, ylim, plot_i, **kwargs) for plot_i in self.plot_indices(plot_n)]
        return insets[0] if isinstance(plot_n, int) else insets

    def _legend(self) -> None:
        """This function generates the plot legend."""
        logger.info("Called 'Canvas._legend()'")

        with catch_warnings():
            # promote UserWarning to error, scoped to this block only, so an
            # unrelated UserWarning raised later (e.g. by savefig()) isn't affected
            simplefilter("error", UserWarning)

            for i in range(self._n_plots):
                try:
                    if not self.counters.is_empty():
                        self.axes[i].legend(loc=self._loc_legend[i], labelspacing=1, ncols=self._ncols_legend[i])

                    logger.debug(f"Legend added to subplot {i}.")
                except UserWarning:
                    logger.warning(f"Subplot {i} has an empty legend.")

    def _save(self) -> None:
        """
        If specified by the user, this function saves
        the plot that has been generated to a file.
        """
        logger.info("Called 'Canvas._save()'")

        if self.save:
            file_path = (Path.cwd() / "plotter/img").joinpath(self.save)
            if not self.save[-4:] == ".pgf":
                self.figure.savefig(file_path, bbox_inches="tight")
            else:
                self.figure.savefig(file_path)
            logger.debug(f"Plot saved to {file_path}")
        else:
            logger.warning("Plot not saved to any file")
