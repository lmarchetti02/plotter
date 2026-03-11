from typing import Annotated, Literal, TypeVar

from numpy import generic
from numpy.typing import NDArray

DType = TypeVar("DType", bound=generic)
NArray1D = Annotated[NDArray[DType], Literal[1]]
NArray2D = Annotated[NDArray[DType], Literal[2]]
NArray3D = Annotated[NDArray[DType], Literal[3]]
