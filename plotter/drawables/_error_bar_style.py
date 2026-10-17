from dataclasses import dataclass

import numpy as np

from ..helpers import ErrorBars


@dataclass(kw_only=True)
class _ErrorBarStyle:
    """
    Shared error-bar styling knobs for `ScatterPlot` and `BarChart`.

    Attributes:
        color (str): The Matplotlib color of the error bars.
        width (float): The line width of the error bars.
        capsize (float): The size of the error bar ticks.
    """

    color: str
    width: float
    capsize: float

    @classmethod
    def from_kwargs(cls, kwargs: dict, *, color: str, width: float, capsize: float) -> "_ErrorBarStyle":
        """
        Builds an `_ErrorBarStyle` from a `draw()` kwargs dict.

        Reads the shared `err_color`/`err_width`/`err_capsize` keys, falling back to
        the given per-drawable defaults when they're absent.

        Args:
            kwargs (dict): The keyword arguments passed to `draw()`.
            color (str): The default error bar color.
            width (float): The default error bar line width.
            capsize (float): The default error bar tick size.

        Returns:
            _ErrorBarStyle: The resolved error bar styling.
        """
        return cls(
            color=kwargs.get("err_color", color),
            width=kwargs.get("err_width", width),
            capsize=kwargs.get("err_capsize", capsize),
        )


def _errors_match(err: ErrorBars | None, n_points: int) -> bool:
    """Whether `err` is a scalar/`None`, or an array of shape (N,) or (N, 2) with N = `n_points`."""
    if not isinstance(err, np.ndarray):
        return True
    return err.shape in ((n_points,), (n_points, 2))


def _to_mpl_errors(err: ErrorBars | None) -> ErrorBars | None:
    """Transposes (N, 2) asymmetric errors into the (2, N) layout matplotlib expects; anything else passes through."""
    if isinstance(err, np.ndarray) and err.ndim == 2:
        return err.T
    return err
