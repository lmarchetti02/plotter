from logging import getLogger
from typing import Any, ClassVar

import numpy as np
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from ..canvas import Canvas, ZoomInset
from .drawable import Drawable
from ._error_bar_style import _ErrorBarStyle
from ._line_style import _LineStyle
from ..helpers import NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class ScatterPlot(Drawable):
    """
    Class for creating a scatter plot with error bars.

    Attributes:
        x (NArray1D[Any]): The array containing the x values.
        y (NArray1D[Any]): The array containing the y values.
        xerr (NArray1D[Any] or float, optional): The array containing the errors of the x values.
            If a float is passed, all the errors are assumed identical.
        yerr (NArray1D[Any] or float, optional): The array containing the errors of the y values.
            If a float is passed, all the errors are assumed identical.

    Raises:
        ValueError: If x and y values do not have the same dimensions.
        ValueError: If y error values do not have the same dimensions as the y values.
        ValueError: If x error values do not have the same dimensions as the x values.
    """

    label_name: ClassVar[str] = "scatter_plots"

    x: NArray1D[Any]
    y: NArray1D[Any]
    yerr: NArray1D[Any] | float | None = Field(default=None, kw_only=True)
    xerr: NArray1D[Any] | float | None = Field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        # xy values
        if len(self.x) != len(self.y):
            raise ValueError("x-values and y-values don't have the same dimensions")

        # y errors
        if isinstance(self.yerr, np.ndarray) and len(self.y) != len(self.yerr):
            raise ValueError("xy-values and yerr-values don't have the same dimensions")

        # x errors
        if isinstance(self.xerr, np.ndarray) and len(self.x) != len(self.xerr):
            raise ValueError("xy-values and xerr-values don't have the same dimensions")

    @classmethod
    def from_y(cls, y: NArray1D[Any], **kwargs) -> "ScatterPlot":
        """
        Builds a `ScatterPlot` from just `y`-values, using an implicit index range for `x`.

        Args:
            y (NArray1D[Any]): The array containing the y values.

        Keyword Arguments:
            Any keyword argument accepted by `ScatterPlot`'s constructor other than `x`/`y`.

        Returns:
            ScatterPlot: A scatter plot with `x = numpy.arange(len(y))`.
        """

        return cls(np.arange(len(y)), y, **kwargs)

    def draw(self, canvas: Canvas | ZoomInset, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the scatter plot on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to which
                the scatter plot is to be attached.
            plot_n (int, optional): The index of the subplot. Defaults to 0.
            label (str, optional): The label for the scatter plot in the legend.
                Defaults to `None`.

        Keyword Arguments:
            color (str): The Matplotlib color of the points. Defaults to "firebrick".
            err_color (str): The Matplotlib color of the error bars. Defaults to "black".
            marker (str): The kind of Matplotlib marker to use. Defaults to `"o"`.
            ms (float): The dimensions of the markers. Defaults to 4.
            err_width (float): The width of the error bars. Defaults to 1.
            err_capsize (float): The size of the ticks on the error bars. Defaults to 2.
            alpha (float): The opacity of the points. Defaults to 1.0.
            line (bool): If `True`, also draws a line connecting the points, in the order
                they're given. Defaults to `False`.
            line_color (str): The Matplotlib color of the connecting line. Defaults to the
                points' own `color`.
            line_width (float): The width of the connecting line. Defaults to 1.5.
            line_style (str): The Matplotlib style of the connecting line. Defaults to `"-"`.
            line_alpha (float): The opacity of the connecting line. Defaults to the points'
                own `alpha`.
        """

        logger.info("Called 'ScatterPlot.draw()'")

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            self.label_name,
            logger,
            "No label for the scatter plot in the json file.",
        )

        err_style = _ErrorBarStyle.from_kwargs(kwargs, color="black", width=1.0, capsize=2.0)
        marker_color = kwargs.get("color", "firebrick")
        marker_alpha = kwargs.get("alpha", 1.0)

        canvas.axes[plot_n].errorbar(
            x=self.x,
            y=self.y,
            yerr=self.yerr,
            xerr=self.xerr,
            marker=kwargs.get("marker", "o"),
            color=marker_color,
            ecolor=err_style.color,
            ms=kwargs.get("ms", 4.0),
            elinewidth=err_style.width,
            zorder=2,  # layer
            ls="none",  # line size (none for disconnected dots)
            capsize=err_style.capsize,
            alpha=marker_alpha,
            label=label,
        )

        if kwargs.get("line", False):
            line_style = _LineStyle.from_kwargs(kwargs, color=marker_color, width=1.5, style="-", alpha=marker_alpha)
            canvas.axes[plot_n].plot(
                self.x,
                self.y,
                color=line_style.color,
                lw=line_style.width,
                ls=line_style.style,
                alpha=line_style.alpha,
                zorder=1,  # behind the markers (zorder=2)
            )

        logger.debug(f"ScatterPlot {n} drawn")

        getattr(canvas.counters, self.label_name)[plot_n] += 1
