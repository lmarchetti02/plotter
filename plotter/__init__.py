"""
PLOTTER
by Luca Marchetti

A small Python library for plotting beautiful graphs.
"""

from .canvas import Canvas, ZoomInset  # noqa: F401
from .colorbar import Colorbar  # noqa: F401
from .drawables.bars import BarChart  # noqa: F401
from .drawables.drawable import Drawable  # noqa: F401
from .drawables.histograms import Hist, Hist2D  # noqa: F401
from .drawables.images import Image  # noqa: F401
from .drawables.lines import LinePlot  # noqa: F401
from .drawables.scatter import ScatterPlot  # noqa: F401
from .helpers import get_colors, setup_workspace  # noqa: F401
