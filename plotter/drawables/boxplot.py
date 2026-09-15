from logging import getLogger
from typing import Any, ClassVar

from matplotlib.colors import to_rgba
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from ..canvas import Canvas, ZoomInset
from ..helpers import NArray1D
from .drawable import Drawable

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
            edgecolor (str): The color of the box edges, whiskers, and caps. Unaffected by
                `alpha`. Defaults to "navy".
            alpha (float): The opacity of the box fill only -- baked directly into the
                facecolor, so it never dims the box edges, whiskers, or caps.
                Defaults to 0.6.
            lw (float): The width of the box edges, whiskers, caps, median line, and mean
                line. Defaults to 1.0.
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
            median_color (str): The color of the median line. Defaults to "firebrick".
            showmeans (bool): If `True`, shows the mean of each box. Defaults to `True`.
            meanline (bool): If `True` (and `showmeans` is `True`), draws the mean as a
                line spanning the box instead of a marker point. Defaults to `True`.
            mean_color (str): The color of the mean line. Defaults to "orange".
            showfliers (bool): If `True`, shows the outlier points beyond the whiskers.
                Defaults to `False`.
            tick_labels (list[str]): The tick label placed under each box.
                Defaults to `None` (numeric tick values).
            orientation (str): `"vertical"` or `"horizontal"`. Defaults to `"vertical"`.
            medianprops (dict): Style overrides for the median line, passed straight
                through to `Axes.boxplot` instead of `median_color`. Defaults to a solid
                line colored with `median_color`.
            meanprops (dict): Style overrides for the mean line, passed straight through
                to `Axes.boxplot` instead of `mean_color`. Defaults to a dashed line
                colored with `mean_color`.

        Note:
            The first `BoxPlot` drawn on a given subplot additionally labels its median
            and mean lines "Median"/"Mean" for the legend -- later groups on the same
            subplot skip this, since every group shares the same median/mean styling and
            one legend entry is enough. Any other keyword argument accepted by
            `Axes.boxplot` (e.g. `bootstrap`, `capwidths`, `flierprops`) is forwarded
            straight through.
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
        edgecolor = kwargs.get("edgecolor", "navy")
        alpha = kwargs.get("alpha", 0.6)
        lw = kwargs.get("lw", 1)
        median_color = kwargs.get("median_color", "firebrick")
        mean_color = kwargs.get("mean_color", "orange")

        # Patch-artist boxes take Patch properties ("edgecolor"/"facecolor"); Line2D-style
        # boxes (patch_artist=False) only understand Line2D properties ("color") and would
        # raise on "edgecolor"/"facecolor". Baking `alpha` into the facecolor itself (rather
        # than Patch's own `alpha`, which would scale the edge color too) keeps the edge
        # fully opaque.
        if patch_artist:
            boxprops = {"facecolor": to_rgba(color, alpha), "edgecolor": edgecolor, "linewidth": lw}
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
            showmeans=kwargs.get("showmeans", True),
            meanline=kwargs.get("meanline", True),
            showfliers=kwargs.get("showfliers", False),
            boxprops=boxprops,
            whiskerprops={"color": edgecolor, "linewidth": lw},
            capprops={"color": edgecolor, "linewidth": lw},
            medianprops=kwargs.get("medianprops", {"color": median_color, "linestyle": "-", "linewidth": lw}),
            meanprops=kwargs.get("meanprops", {"color": mean_color, "linestyle": "--", "linewidth": lw}),
            zorder=kwargs.get("zorder", 2),
        )

        # The group's own label always goes on the box artist itself, regardless of
        # patch_artist -- matplotlib's own `label=` kwarg on `boxplot()` would otherwise
        # tie it to the median line instead when patch_artist=False, colliding with the
        # "Median" legend entry below.
        if label is not None:
            self.bxp["boxes"][0].set_label(label)

        # Every group shares the same median/mean styling, so only the first group drawn
        # on this subplot gets a legend entry for them -- avoids duplicate "Median"/"Mean"
        # entries when several BoxPlot groups are drawn on the same subplot.
        if n == 0:
            self.bxp["medians"][0].set_label("Median")
            if self.bxp["means"]:
                self.bxp["means"][0].set_label("Mean")

        logger.debug(f"BoxPlot {n} drawn")

        getattr(canvas.counters, self.label_name)[plot_n] += 1
