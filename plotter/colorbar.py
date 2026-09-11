from logging import getLogger

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .canvas import Canvas, ZoomInset
from .histograms import Hist2D
from .images import Image

logger = getLogger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Colorbar:
    """
    Class for drawing an explicit colorbar on a canvas, optionally shared across
    several subplots.

    Attributes:
        source (Image | Hist2D): The already-drawn drawable whose color mapping
            (mappable, colormap, normalization) the colorbar represents.
    """

    source: Image | Hist2D

    def draw(
        self,
        canvas: Canvas | ZoomInset,
        plot_n: int | tuple[int, int] | str | None = None,
        row: int | None = None,
        col: int | None = None,
        label: str | None = None,
        **kwargs,
    ) -> None:
        """
        Draws the colorbar, spanning one or more subplots.

        Args:
            canvas (Canvas | ZoomInset): The canvas (or zoom-inset panel) to draw the colorbar on.
            plot_n (int, tuple[int, int], str, optional): The index or indices of the
                subplots to attach the colorbar to. At most one of `plot_n`, `row`, `col`
                may be given; defaults to `0` when none are. See `Canvas.plot_indices`.
            row (int, optional): A row of the `canvas`'s grid to share the colorbar
                across. Not supported when `canvas` is a `ZoomInset`.
            col (int, optional): A column of the `canvas`'s grid to share the colorbar
                across. Not supported when `canvas` is a `ZoomInset`.
            label (str, optional): The colorbar's label. Defaults to `None`.

        Keyword Arguments:
            Passed straight through to `matplotlib.figure.Figure.colorbar`
            (e.g. `orientation`, `location`, `fraction`, `pad`, `shrink`, `aspect`).

        Raises:
            RuntimeError: If `source` has not been drawn yet.
            ValueError: If more than one of `plot_n`, `row`, `col` is given.
            ValueError: If `row`/`col` is given for a `ZoomInset`.
        """
        logger.info("Called 'Colorbar.draw()'")

        if self.source.mappable is None:
            raise RuntimeError("'source' has not been drawn yet -- call its 'draw()' before 'Colorbar.draw()'.")

        if isinstance(canvas, ZoomInset):
            if row is not None or col is not None:
                raise ValueError("'row'/'col' are not supported for a ZoomInset panel.")
            axes = canvas.axes
        else:
            if plot_n is None and row is None and col is None:
                plot_n = 0
            axes = [canvas.axes[i] for i in canvas.plot_indices(plot_n, row=row, col=col)]

        canvas.figure.colorbar(self.source.mappable, ax=axes, label=label, **kwargs)
