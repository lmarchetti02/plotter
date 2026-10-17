from typing import Annotated, Any, Literal, TypeVar

from numpy import float64, generic
from numpy.typing import NDArray

DType = TypeVar("DType", bound=generic)
NArray1D = Annotated[NDArray[DType], Literal[1]]
NArray2D = Annotated[NDArray[DType], Literal[2]]
NArray3D = Annotated[NDArray[DType], Literal[3]]

F64 = float64

# Error bars, as accepted by `ScatterPlot`'s `xerr`/`yerr` and `BarChart`'s `yerr`: one value
# shared by every point (float), one symmetric error per point (shape (N,)), or one asymmetric
# (low, high) pair of error sizes per point (shape (N, 2)), each extending below/above the point.
ErrorBars = float | NArray1D[Any] | NArray2D[Any]

# A single subplot index (e.g. 0), 'all', an inclusive (inf, sup) range of indices, or
# an explicit, possibly non-consecutive list of indices (e.g. [0, 2]), as accepted by
# `Canvas.plot_indices` and the methods built on top of it.
PlotN = int | tuple[int, int] | list[int] | Literal["all"]

# A subplot mosaic, as accepted by `Canvas`'s `layout`: a grid of `plot_n` indices, one per
# cell (row-major). Repeating an index makes that subplot span every cell it appears in (which
# must form a rectangle); `None` leaves a cell empty. E.g. [[0, 2], [1, 2]]: two subplots
# stacked on the left, one spanning the full height on the right.
Layout = list[list[int | None]]

# How the subplots of a `Canvas` share an axis (`sharex`/`sharey`): not at all (False), all
# together (True), or grouped by the row/column each subplot's span starts in.
Share = bool | Literal["row", "col"]
