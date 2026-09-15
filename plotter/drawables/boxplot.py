from logging import getLogger
from typing import Any, ClassVar

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from ..canvas import Canvas, ZoomInset
from .drawable import Drawable
from ..helpers import NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BoxPlot(Drawable):
    """
    Class for creating a group of box-and-whisker plots.

    Attributes:
        data (list[NArray1D[Any]]): One array of raw samples per box.
        positions (NArray1D[Any] or None, optional): The x-position of each box.
            Defaults to `None`, which lets Matplotlib place the boxes at `1, 2, ..., N`.
        bxp (dict[str, list[Any]] or None): The dictionary of Matplotlib artists
            (keys: `"boxes"`, `"medians"`, `"whiskers"`, `"caps"`, `"fliers"`, `"means"`)
            returned by `Axes.boxplot`, populated after `draw()` runs, for further
            per-artist styling.

    Raises:
        ValueError: If `data` is empty.
        ValueError: If `positions` is given and does not have the same length as `data`.
    """

    label_name: ClassVar[str] = "box_plots"

    data: list[NArray1D[Any]]
    positions: NArray1D[Any] | None = None

    bxp: dict[str, list[Any]] | None = Field(init=False, default=None)

    def __post_init__(self) -> None:
        if len(self.data) == 0:
            raise ValueError("data must contain at least one group")

        if self.positions is not None and len(self.positions) != len(self.data):
            raise ValueError("positions and data must have the same length")

    def draw(self, canvas: Canvas | ZoomInset, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the group of boxes on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the boxes on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            label (str, optional): The single legend label for the whole group of boxes.
                Defaults to `None`.

        Keyword Arguments:
            color (str): The Matplotlib facecolor of the boxes, when `patch_artist` is `True`.
                Defaults to "steelblue".
            edgecolor (str): The color of the box edges, whiskers, and caps.
                Defaults to "midnightblue".
            alpha (float): The opacity of the boxes. Defaults to 0.9.
            lw (float): The width of the box edges, whiskers, caps, and median line.
                Defaults to 1.0.
            zorder (float): The drawing order of the boxes. Defaults to 2.
            patch_artist (bool): If `True`, boxes are drawn as filled `Patch` artists using
                `color`/`edgecolor`/`alpha`/`lw`; if `False`, boxes are drawn as unfilled
                `Line2D` rectangles styled with `edgecolor`/`lw` only (`color`/`alpha` are
                ignored, since there is no fill). Defaults to `True`.
            notch (bool): If `True`, draws a notch around the median of each box.
                Defaults to `False`.
            whis (float or tuple[float, float]): The whisker reach. See `Axes.boxplot`.
                Defaults to 1.5.
            widths (float or NArray1D[Any]): The width(s) of the boxes.
                Defaults to Matplotlib's own computed default.
            showmeans (bool): If `True`, shows the arithmetic mean of each box.
                Defaults to `False`.
            showfliers (bool): If `True`, shows the outlier points beyond the whiskers.
                Defaults to `True`.
            tick_labels (list[str]): The tick label placed under each box.
                Defaults to `None` (numeric tick values).
            orientation (str): `"vertical"` or `"horizontal"`. Defaults to `"vertical"`.
            medianprops (dict): Style overrides for the median line, passed straight through
                to `Axes.boxplot`. Defaults to a plain black line.

        Note:
            Any other keyword argument accepted by `Axes.boxplot` (e.g. `bootstrap`,
            `capwidths`, `flierprops`, `meanprops`) is forwarded straight through.
        """

        logger.info("Called 'BoxPlot.draw()'")

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            self.label_name,
            logger,
            "No label for the box plot in the json file.",
        )

        patch_artist = kwargs.get("patch_artist", True)
        color = kwargs.get("color", "steelblue")
        edgecolor = kwargs.get("edgecolor", "midnightblue")
        alpha = kwargs.get("alpha", 0.9)
        lw = kwargs.get("lw", 1.0)

        # Patch-artist boxes take Patch properties ("edgecolor"/"facecolor"); Line2D-style
        # boxes (patch_artist=False) only understand Line2D properties ("color") and would
        # raise on "edgecolor"/"facecolor".
        if patch_artist:
            boxprops = {"facecolor": color, "edgecolor": edgecolor, "alpha": alpha, "linewidth": lw}
        else:
            boxprops = {"color": edgecolor, "linewidth": lw}

        self.bxp = canvas.axes[plot_n].boxplot(
            self.data,
            positions=self.positions,
            tick_labels=kwargs.get("tick_labels", None),
            widths=kwargs.get("widths", None),
            orientation=kwargs.get("orientation", "vertical"),
            patch_artist=patch_artist,
            notch=kwargs.get("notch", False),
            whis=kwargs.get("whis", 1.5),
            showmeans=kwargs.get("showmeans", False),
            showfliers=kwargs.get("showfliers", True),
            boxprops=boxprops,
            whiskerprops={"color": edgecolor, "linewidth": lw},
            capprops={"color": edgecolor, "linewidth": lw},
            medianprops=kwargs.get("medianprops", {"color": "black", "linewidth": lw}),
            zorder=kwargs.get("zorder", 2),
            label=label,
        )
        logger.debug(f"BoxPlot {n} drawn")

        getattr(canvas.counters, self.label_name)[plot_n] += 1
