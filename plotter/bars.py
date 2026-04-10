from logging import getLogger
from typing import Any

import numpy as np
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .canvas import Canvas
from .drawable import Drawable
from .helpers import NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BarChart(Drawable):
    """
    Class for creating a bar chart.

    Attributes:
        x (NArray1D[Any]): The array containing the x positions of the bars.
        heights (NArray1D[Any]): The array containing the heights of the bars.
        yerr (NArray1D[Any] | float | None, optional): The uncertainty on the
            bar heights. If a float is passed, all the errors are assumed identical.

    Raises:
        ValueError: If x and heights do not have the same dimensions.
        ValueError: If yerr as an array does not have the same dimensions as heights.
    """

    x: NArray1D[Any]
    heights: NArray1D[Any]
    yerr: NArray1D[Any] | float | None = None

    def __post_init__(self) -> None:
        if len(self.x) != len(self.heights):
            raise ValueError("x-values and heights must have the same dimensions")

        if isinstance(self.yerr, np.ndarray) and len(self.heights) != len(self.yerr):
            raise ValueError("heights and yerr-values don't have the same dimensions")

    def draw(self, canvas: Canvas, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the bar chart on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw the bar chart on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            label (str, optional): The label for the bar chart in the legend.
                Defaults to `None`.

        Keyword Arguments:
            width (float): The width of the bars. Defaults to 0.8.
            color (str): The Matplotlib color of the bars. Defaults to "steelblue".
            alpha (float): The transparency of the bars. Defaults to 0.9.
            ecolor (str): The color of the error bars. Defaults to "black".
            capsize (float): The size of the error bar ticks. Defaults to 3.
            lw (float): The width of the bar edges. Defaults to 0.
            edgecolor (str): The color of the bar edges. Defaults to "midnightblue".
        """

        logger.info("Called 'BarChart.draw()'")

        n = canvas.counters.bar_charts[plot_n]
        try:
            label = label if label else canvas.text[plot_n].bar_charts[n]
        except IndexError as _:
            label = None
            logger.warning("No label for the bar chart in the json file.")

        canvas.axes[plot_n].bar(
            self.x,
            self.heights,
            yerr=self.yerr,
            width=kwargs.get("width", 0.8),
            color=kwargs.get("color", "steelblue"),
            alpha=kwargs.get("alpha", 0.9),
            label=label,
            ecolor=kwargs.get("ecolor", "black"),
            capsize=kwargs.get("capsize", 3.0),
            linewidth=kwargs.get("lw", 0.0),
            edgecolor=kwargs.get("edgecolor", "midnightblue"),
            zorder=2,
        )
        logger.debug(f"BarChart {n} drawn")

        canvas.counters.bar_charts[plot_n] += 1
