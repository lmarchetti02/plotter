from dataclasses import dataclass


@dataclass(kw_only=True)
class _LineStyle:
    """
    Shared connecting-line styling knobs for `ScatterPlot`.

    Attributes:
        color (str): The Matplotlib color of the line.
        width (float): The line width.
        style (str): The Matplotlib line style.
        alpha (float): The opacity of the line.
    """

    color: str
    width: float
    style: str
    alpha: float

    @classmethod
    def from_kwargs(cls, kwargs: dict, *, color: str, width: float, style: str, alpha: float) -> "_LineStyle":
        """
        Builds a `_LineStyle` from a `draw()` kwargs dict.

        Reads the shared `line_color`/`line_width`/`line_style`/`line_alpha` keys, falling
        back to the given per-drawable defaults when they're absent.

        Args:
            kwargs (dict): The keyword arguments passed to `draw()`.
            color (str): The default line color.
            width (float): The default line width.
            style (str): The default line style.
            alpha (float): The default line opacity.

        Returns:
            _LineStyle: The resolved line styling.
        """
        return cls(
            color=kwargs.get("line_color", color),
            width=kwargs.get("line_width", width),
            style=kwargs.get("line_style", style),
            alpha=kwargs.get("line_alpha", alpha),
        )
