from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# avoid importing Canvas at runtime
if TYPE_CHECKING:
    from .canvas import Canvas


class Drawable(ABC):
    """Abstract base class for objects that can be drawn on a canvas."""

    @abstractmethod
    def draw(self, canvas: "Canvas", plot_n: int = 0, label: str | None = None, **kwargs) -> None:
        """
        Draws the object on the canvas.

        Args:
            canvas (Canvas): The canvas object to draw on.
            plot_n (int, optional): The index of the subplot to draw on.
                Defaults to 0.
            label (str, optional): The label associated with the drawn object.
                Defaults to `None`.
        """
