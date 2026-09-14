from abc import ABC, abstractmethod
from logging import Logger
from typing import TYPE_CHECKING, ClassVar

# avoid importing Canvas at runtime
if TYPE_CHECKING:
    from ..canvas import Canvas, ZoomInset


DRAWABLE_LABEL_NAMES = (
    "scatter_plots",
    "line_plots",
    "bar_charts",
    "histograms",
)


class Drawable(ABC):
    """Abstract base class for objects that can be drawn on a canvas."""

    label_name: ClassVar[str]

    @staticmethod
    def get_label_names() -> tuple[str, ...]:
        """Returns the names of all supported drawable label groups."""
        return DRAWABLE_LABEL_NAMES

    @staticmethod
    def _get_label(canvas: "Canvas | ZoomInset", plot_n: int, label: str | None, name: str, logger: Logger, msg: str) -> tuple[int, str | None]:
        """
        Retrieves the label associated with the drawable.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) the drawable is attached to.
            plot_n (int): The index of the subplot.
            label (str | None): An explicit user-provided label.
            name (str): The name of the drawable.
            logger (Logger): The logger to use for warnings.
            msg (str): The warning to emit when no label can be found.

        Returns:
            tuple[int, str | None]: The current drawable index and the resolved label.
        """

        n = getattr(canvas.counters, name)[plot_n]
        try:
            resolved_label = label if label else getattr(canvas.text[plot_n], name)[n]
        except IndexError as _:
            resolved_label = None
            logger.warning(msg)

        return n, resolved_label

    @abstractmethod
    def draw(self, canvas: "Canvas | ZoomInset", plot_n: int = 0, **kwargs) -> None:
        """
        Draws the object on the canvas.

        Not every concrete drawable accepts the same keyword arguments -- see each
        subclass's own docstring. In particular, drawables that participate in label
        bookkeeping (see `Drawable.get_label_names`) additionally accept a `label`
        keyword argument; `Image`, `RawHist2D`, and `BinnedHist2D` do not.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
        """
