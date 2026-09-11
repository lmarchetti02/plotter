from logging import getLogger
from math import isclose
from typing import Literal

from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar as MplColorbar
from matplotlib.figure import Figure
from matplotlib.transforms import Bbox
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .canvas import Canvas, ZoomInset
from .histograms import Hist2D
from .images import Image

logger = getLogger(__name__)

_Position = Literal["left", "right", "top", "bottom"]


def _parse_fraction(value: str | float) -> float:
    """
    Parses a size/fraction value into a plain float in [0, 1].

    Args:
        value (str | float): Either a percentage string (e.g. "5%") or a bare
            float already expressed as a fraction (e.g. 0.05).

    Returns:
        float: The parsed fraction.

    Raises:
        ValueError: If `value` is a string that doesn't end in '%'.
    """
    if isinstance(value, str):
        if not value.endswith("%"):
            raise ValueError(f"'{value}' is not a valid size (expected e.g. '5%').")
        return float(value[:-1]) / 100
    return value


def _decoration_margin(ax: Axes, figure: Figure, position: _Position, plain: Bbox) -> float:
    """
    Measures how far `ax`'s ticks/axis-label/title on the `position` side (the
    decorations matplotlib draws just outside the Axes' own box, e.g. y-tick labels
    to its left) extend beyond `plain`, in figure-fraction units.

    Args:
        ax (Axes): The Axes to measure.
        figure (Figure): The parent Figure (for the figure-fraction transform).
        position (str): Which side to measure ('left', 'right', 'top', 'bottom').
        plain (Bbox): `ax`'s own position box (`ax.get_position()`), passed in to
            avoid recomputing it.

    Returns:
        float: The margin, in figure-fraction units, never negative.
    """
    tight = ax.get_tightbbox().transformed(figure.transFigure.inverted())
    if position == "left":
        return max(0.0, plain.x0 - tight.x0)
    if position == "right":
        return max(0.0, tight.x1 - plain.x1)
    if position == "top":
        return max(0.0, tight.y1 - plain.y1)
    return max(0.0, plain.y0 - tight.y0)


def _resize_others_to_match(axes: list[Axes], positions: list[Bbox], edge_axes: set[Axes], final_size: float, vertical: bool) -> None:
    """
    Centers every group Axes not in `edge_axes` on `final_size` along the cross
    dimension (height if `vertical`, width otherwise).

    A fixed-aspect edge Axes (e.g. `Image`'s default `aspect="equal"`) may end up
    shrinking that dimension too, as a side effect of `_make_colorbar_axes` shrinking
    its other dimension to make room for the colorbar; without this, the rest of the
    group would be left visually mismatched. Each resized Axes' own aspect settles in
    turn (via the same immediate, stable `set_position()` behavior noted in
    `_make_colorbar_axes`) -- if it shares the edge Axes' data aspect ratio, it
    converges to the exact same final box; if not, only this dimension is matched.

    Args:
        axes (list[Axes]): The full target group.
        positions (list[Bbox]): `axes`' original position boxes (`get_position()`,
            captured before any resizing), in the same order.
        edge_axes (set[Axes]): The subset already resized by `_make_colorbar_axes`;
            left untouched here.
        final_size (float): The edge Axes' actual final height/width, in figure-fraction
            units, to match.
        vertical (bool): `True` to match height (for a "left"/"right" colorbar),
            `False` to match width (for a "top"/"bottom" one).
    """
    for ax, p in zip(axes, positions):
        if ax in edge_axes:
            continue
        current = p.height if vertical else p.width
        if isclose(current, final_size, abs_tol=1e-9):
            continue
        ax.set_axes_locator(None)
        if vertical:
            new_y0 = p.y0 + (p.height - final_size) / 2
            ax.set_position([p.x0, new_y0, p.width, final_size])
        else:
            new_x0 = p.x0 + (p.width - final_size) / 2
            ax.set_position([new_x0, p.y0, final_size, p.height])


def _make_colorbar_axes(figure: Figure, axes: list[Axes], position: _Position, size: str | float, padding: float) -> Axes:
    """
    Carves out a new Axes for a colorbar next to a group of Axes.

    Shrinks whichever Axes in `axes` sit on the group's edge facing `position` (e.g.
    for a row of Axes and `position="right"`, only the rightmost one; for a column,
    all of them, since they share that edge) so the colorbar occupies space that
    used to belong to the group's own footprint, without overlapping any Axes
    outside the group. The colorbar itself is placed just outside those Axes' own
    ticks/axis-label/title on that side, so it doesn't overlap them either. Any other
    Axes in the group (e.g. the rest of a row, for a "left"/"right" colorbar) gets its
    cross dimension matched to the edge Axes' actual final size, via
    `_resize_others_to_match`, so the group stays visually uniform even when a
    fixed-aspect edge Axes had to shrink further than just the requested thickness.

    Args:
        figure (Figure): The parent Figure the Axes belong to.
        axes (list[Axes]): The target group (one or more Axes sharing part of an edge).
        position (str): Which side of the group's bounding box to attach the colorbar to.
        size (str | float): The colorbar's thickness -- a percentage string (e.g. "5%")
            or a bare fraction -- of the group's width ('left'/'right') or height
            ('top'/'bottom').
        padding (float): The gap between the group's Axes (and their ticks/labels) and
            the colorbar, in inches.

    Returns:
        Axes: The new Axes to draw the colorbar into.
    """
    size_frac = _parse_fraction(size)
    positions = [ax.get_position() for ax in axes]
    x0 = min(p.x0 for p in positions)
    y0 = min(p.y0 for p in positions)
    x1 = max(p.x1 for p in positions)
    y1 = max(p.y1 for p in positions)
    fig_width_in, fig_height_in = figure.get_size_inches()

    if position in ("left", "right"):
        thickness = size_frac * (x1 - x0)
        shrink = thickness + padding / fig_width_in
        edge = x1 if position == "right" else x0
        edge_axes = [(ax, p) for ax, p in zip(axes, positions) if isclose(p.x1 if position == "right" else p.x0, edge, abs_tol=1e-9)]

        for ax, _ in edge_axes:
            # a ZoomInset's Axes has a locator (from inset_axes()) that recomputes its
            # position on every render, overriding set_position() below -- clear it first
            ax.set_axes_locator(None)
        margin = max((_decoration_margin(ax, figure, position, p) for ax, p in edge_axes), default=0.0)

        for ax, p in edge_axes:
            new_x0 = p.x0 if position == "right" else p.x0 + shrink
            ax.set_position([new_x0, p.y0, p.width - shrink, p.height])

        # a fixed-aspect edge Axes (e.g. Image's default aspect="equal") may have just
        # shrunk its height too, to keep the data square within the narrower box --
        # propagate that to the rest of the group so it stays visually uniform, then
        # match the colorbar to the actual final size, not the pre-shrink one
        edge_ax_set = {ax for ax, _ in edge_axes}
        final_height = max(ax.get_position().height for ax in edge_ax_set)
        _resize_others_to_match(axes, positions, edge_ax_set, final_height, vertical=True)

        final_y0 = min(ax.get_position().y0 for ax in axes)
        final_y1 = max(ax.get_position().y1 for ax in axes)

        cax_x0 = edge + margin - thickness if position == "right" else edge - margin
        return figure.add_axes([cax_x0, final_y0, thickness, final_y1 - final_y0])

    thickness = size_frac * (y1 - y0)
    shrink = thickness + padding / fig_height_in
    edge = y1 if position == "top" else y0
    edge_axes = [(ax, p) for ax, p in zip(axes, positions) if isclose(p.y1 if position == "top" else p.y0, edge, abs_tol=1e-9)]

    for ax, _ in edge_axes:
        ax.set_axes_locator(None)
    margin = max((_decoration_margin(ax, figure, position, p) for ax, p in edge_axes), default=0.0)

    for ax, p in edge_axes:
        new_y0 = p.y0 if position == "top" else p.y0 + shrink
        ax.set_position([p.x0, new_y0, p.width, p.height - shrink])

    edge_ax_set = {ax for ax, _ in edge_axes}
    final_width = max(ax.get_position().width for ax in edge_ax_set)
    _resize_others_to_match(axes, positions, edge_ax_set, final_width, vertical=False)

    final_x0 = min(ax.get_position().x0 for ax in axes)
    final_x1 = max(ax.get_position().x1 for ax in axes)

    cax_y0 = edge + margin - thickness if position == "top" else edge - margin
    return figure.add_axes([final_x0, cax_y0, final_x1 - final_x0, thickness])


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Colorbar:
    """
    Class for drawing an explicit colorbar on a canvas, optionally shared across
    several subplots.

    Attributes:
        source (Image | Hist2D): The already-drawn drawable whose color mapping
            (mappable, colormap, normalization) the colorbar represents.
        mpl_colorbar (MplColorbar or None): The underlying `matplotlib.colorbar.Colorbar`
            artist, populated after `draw` runs, for advanced customization.
    """

    source: Image | Hist2D

    mpl_colorbar: MplColorbar | None = Field(init=False, default=None)

    def draw(
        self,
        canvas: Canvas | ZoomInset,
        plot_n: int | tuple[int, int] | str | None = None,
        row: int | None = None,
        col: int | None = None,
        label: str | None = None,
        position: _Position = "right",
        size: str | float = "5%",
        padding: float = 0.1,
        **kwargs,
    ) -> None:
        """
        Draws the colorbar, spanning one or more subplots.

        The colorbar always ends up positioned right next to the targeted subplot(s),
        with the requested spacing, and the same length as them (their full shared
        height for `position="left"/"right"`, or width for `"top"/"bottom"`) -- the
        targeted subplot(s) are shrunk just enough to make room for it within their
        own footprint, so it never overlaps a neighboring subplot outside the target.

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
            position (str, optional): Which side to attach the colorbar to -- "left",
                "right", "top", or "bottom". Defaults to "right".
            size (str | float, optional): The colorbar's thickness, as a percentage
                string (e.g. "5%") or bare fraction of the target(s)' own width
                (for "left"/"right") or height (for "top"/"bottom"). Defaults to "5%".
            padding (float, optional): The gap between the target(s) and the colorbar,
                in inches. Defaults to 0.1.

        Keyword Arguments:
            Passed straight through to `matplotlib.figure.Figure.colorbar` for cosmetic
            tweaks unrelated to placement (e.g. `ticks`, `format`, `extend`, `alpha`).

        Raises:
            RuntimeError: If `source` has not been drawn yet.
            ValueError: If `position` is not one of "left", "right", "top", "bottom".
            ValueError: If more than one of `plot_n`, `row`, `col` is given.
            ValueError: If `row`/`col` is given for a `ZoomInset`.
        """
        logger.info("Called 'Colorbar.draw()'")

        if self.source.mappable is None:
            raise RuntimeError("'source' has not been drawn yet -- call its 'draw()' before 'Colorbar.draw()'.")

        if position not in ("left", "right", "top", "bottom"):
            raise ValueError(f"'{position}' is not a valid position (expected 'left', 'right', 'top', or 'bottom').")

        if isinstance(canvas, ZoomInset):
            if row is not None or col is not None:
                raise ValueError("'row'/'col' are not supported for a ZoomInset panel.")
            axes = canvas.axes
        else:
            if plot_n is None and row is None and col is None:
                plot_n = 0
            axes = [canvas.axes[i] for i in canvas.plot_indices(plot_n, row=row, col=col)]

        orientation = "vertical" if position in ("left", "right") else "horizontal"
        cax = _make_colorbar_axes(canvas.figure, axes, position, size, padding)

        self.mpl_colorbar = canvas.figure.colorbar(self.source.mappable, cax=cax, label=label, orientation=orientation, **kwargs)
