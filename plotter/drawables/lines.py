from logging import getLogger
from typing import Any, ClassVar

import numpy as np
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from ..canvas import Canvas, ZoomInset
from .drawable import Drawable
from ..helpers import NArray1D

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class LinePlot(Drawable):
    """
    Class for creating a line plot from raw (x, y) data to be drawn on a canvas.

    Attributes:
        x (NArray1D[Any]): The values of the independent variable.
        y (NArray1D[Any]): The values of the dependent variable.

    Raises:
        ValueError: If x and y do not have the same dimensions.
    """

    label_name: ClassVar[str] = "line_plots"

    x: NArray1D[Any]
    y: NArray1D[Any]

    def __post_init__(self) -> None:
        """Validates that x and y have matching dimensions."""

        if len(self.x) != len(self.y):
            raise ValueError("x-values and y-values must have the same dimension")

    @classmethod
    def from_y(cls, y: NArray1D[Any], **kwargs) -> "LinePlot":
        """
        Builds a `LinePlot` from just `y`-values, using an implicit index range for `x`.

        Args:
            y (NArray1D[Any]): The values of the dependent variable.

        Keyword Arguments:
            Any keyword argument accepted by `LinePlot`'s constructor other than `x`/`y`.

        Returns:
            LinePlot: A line plot with `x = numpy.arange(len(y))`.
        """

        return cls(np.arange(len(y)), y, **kwargs)

    def draw(self, canvas: Canvas | ZoomInset, plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the plot on the canvas.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the plot on.
            plot_n (int, optional): The index of the subplot. Defaults to 0.
            label (str, optional): The label for the plot in the legend.
                Defaults to `None`.

        Keyword Arguments:
            color (str): The Matplotlib color of the plot. Defaults to "darkgreen".
            lw (float): The line width. Defaults to 1.5.
            style (str): The line style. Defaults to `"-"`.
            alpha (float): The opacity of the line. Defaults to 1.0.
            inverted (bool): If `True`, plots the inverse function.
                Defaults to `False`.
        """

        logger.info("Called 'LinePlot.draw()'")

        # exchange x and y
        if kwargs.get("inverted", False):
            self.x, self.y = self.y, self.x

        n, label = self._get_label(
            canvas,
            plot_n,
            label,
            self.label_name,
            logger,
            "No label for the plot in the json file.",
        )

        canvas.axes[plot_n].plot(
            self.x,
            self.y,
            color=kwargs.get("color", "darkgreen"),
            zorder=1,
            lw=kwargs.get("lw", 1.5),
            ls=kwargs.get("style", "-"),
            alpha=kwargs.get("alpha", 1.0),
            label=label,
        )
        logger.debug(f"Plot {n} drawn")

        getattr(canvas.counters, self.label_name)[plot_n] += 1
