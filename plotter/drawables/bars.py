from logging import getLogger
from typing import Any, ClassVar

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from ..canvas import Canvas, ZoomInset
from .drawable import Drawable
from ._error_bar_style import _ErrorBarStyle, _errors_match, _to_mpl_errors
from ..helpers import ErrorBars, NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BarChart(Drawable):
    """
    Class for creating a bar chart.

    Attributes:
        x (NArray1D[Any]): The array containing the x positions of the bars.
        heights (NArray1D[Any]): The array containing the heights of the bars.
        yerr (ErrorBars | None, optional): The uncertainty on the bar heights: a float
            (identical for every bar), an array of shape (N,) (symmetric, one per bar), or an
            array of shape (N, 2) (asymmetric, one (low, high) pair of error sizes per bar).

    Raises:
        ValueError: If x and heights do not have the same dimensions.
        ValueError: If yerr as an array is not of shape (N,) or (N, 2), with N the number of bars.
    """

    label_name: ClassVar[str] = "bar_charts"

    x: NArray1D[Any]
    heights: NArray1D[Any]
    yerr: ErrorBars | None = None

    def __post_init__(self) -> None:
        if len(self.x) != len(self.heights):
            raise ValueError("x-values and heights must have the same dimensions")

        if not _errors_match(self.yerr, len(self.heights)):
            raise ValueError("heights and yerr-values don't have the same dimensions (expected shape (N,) or (N, 2))")

    def draw(
        self,
        canvas: Canvas | ZoomInset,
        plot_n: int = 0,
        label: str | None = None,
        bar_labels: bool | dict[str, Any] = False,
        **kwargs,
    ) -> None:
        """
        Draws the bar chart on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the bar chart on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            label (str, optional): The label for the bar chart in the legend.
                Defaults to `None`.
            bar_labels (bool | dict[str, Any], optional): If truthy, writes a text label above
                each bar via `Axes.bar_label`. Pass `True` for the default behavior (each bar's
                height, formatted with matplotlib's `"%g"` format), or a dict of keyword arguments
                forwarded straight through to `Axes.bar_label` -- e.g. `{"labels": [...]}` for
                custom per-bar text, or `"fmt"`/`"label_type"`/`"padding"`/any `Text` styling
                kwarg. Defaults to `False`.

        Keyword Arguments:
            bottom (float | NArray1D[Any]): The y-coordinate(s) of each bar's base.
                Pass the previous series' (cumulative) heights to stack bar charts on
                top of each other -- see `plotter.helpers.useful_functions.stack_bottoms`
                for computing this across more than two series. Defaults to 0.
            width (float): The width of the bars. Defaults to 0.8.
            color (str): The Matplotlib color of the bars. Defaults to "steelblue".
            alpha (float): The transparency of the bars. Defaults to 0.9.
            err_color (str): The color of the error bars. Defaults to "black".
            err_width (float): The width of the error bars. Defaults to 1.5.
            err_capsize (float): The size of the error bar ticks. Defaults to 3.
            lw (float): The width of the bar edges. Defaults to 0.
            edgecolor (str): The color of the bar edges. Defaults to "midnightblue".
        """

        logger.info("Called 'BarChart.draw()'")

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            logger,
            "No label for the bar chart in the json file.",
        )

        err_style = _ErrorBarStyle.from_kwargs(kwargs, color="black", width=1.5, capsize=3.0)

        container = canvas.axes[plot_n].bar(
            self.x,
            self.heights,
            yerr=_to_mpl_errors(self.yerr),
            bottom=kwargs.get("bottom", 0),
            width=kwargs.get("width", 0.8),
            color=kwargs.get("color", "steelblue"),
            alpha=kwargs.get("alpha", 0.9),
            label=label,
            ecolor=err_style.color,
            capsize=err_style.capsize,
            error_kw={"elinewidth": err_style.width},
            linewidth=kwargs.get("lw", 0.0),
            edgecolor=kwargs.get("edgecolor", "midnightblue"),
            zorder=2,
        )
        logger.debug(f"BarChart {n} drawn")

        if bar_labels:
            canvas.axes[plot_n].bar_label(container, **(bar_labels if isinstance(bar_labels, dict) else {}))

        self._increment_counter(canvas, plot_n)
