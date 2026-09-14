"""Drawable objects: the `Drawable` base class and its concrete subclasses."""

from .drawable import Drawable  # noqa: F401

# The concrete subclasses (bars, raw_histograms, binned_histograms, images, lines, scatter)
# import `Canvas`
# at runtime, and `Canvas` itself imports `Drawable` from this package while loading.
# Re-exporting them here too, like the other package `__init__.py`s do, would make
# importing `Drawable` (from `Canvas`) eagerly import `Canvas` again before it has
# finished defining itself. Import the subclasses from their own submodules instead
# (`plotter.drawables.bars`, etc.) — `plotter/__init__.py` does this already.
