from typing import Annotated, Literal, TypeVar

from numpy import float64, generic
from numpy.typing import NDArray

DType = TypeVar("DType", bound=generic)
NArray1D = Annotated[NDArray[DType], Literal[1]]
NArray2D = Annotated[NDArray[DType], Literal[2]]
NArray3D = Annotated[NDArray[DType], Literal[3]]

F64 = float64

# A single subplot index (e.g. 0), 'all', an inclusive (inf, sup) range of indices, or
# an explicit, possibly non-consecutive list of indices (e.g. [0, 2]), as accepted by
# `Canvas.plot_indices` and the methods built on top of it.
PlotN = int | tuple[int, int] | list[int] | Literal["all"]
