# `plotter.colorbar`

## function `_get_reservation`

```python
_get_reservation(ax: Axes, position: _Position) -> dict | None
```

Returns the colorbar margin reservation stamped on `ax` for `position`, if any.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `ax` | Axes | The Axes to check. |
| `position` | str | Which side's reservation to look up. |

**Returns:**

| Type | Description |
| --- | --- |
| dict or None | `{"edge", "shrink", "thickness", "caxes"}` (see `_stamp_reservation`) if `ax` was previously touched by a `Colorbar` reserving space on that side; `None` otherwise. |


## function `_stamp_reservation`

```python
_stamp_reservation(ax: Axes, position: _Position, edge: float, shrink: float, thickness: float, caxes: list[Axes]) -> None
```

Records a colorbar margin reservation on `ax`, so a later `Colorbar` targeting a
sibling row/column that shares this edge can detect it via `_get_reservation` and
reuse (or grow) the same margin instead of carving out a second one.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `ax` | Axes | The Axes to stamp. |
| `position` | str | Which side the margin is on. |
| `edge` | float | The margin's fixed outer boundary (figure-fraction; the side away from the grid, e.g. `cax.x1` for "right"), stable across however many colorbars end up sharing it. |
| `shrink` | float | The total space (thickness + padding, figure-fraction) this margin currently reserves from the grid's original size. |
| `thickness` | float | The margin's current colorbar thickness (figure-fraction). |
| `caxes` | list\[Axes\] | Every colorbar Axes currently sharing this margin, so a later, larger colorbar can grow all of them to match. |


## function `_grow_existing_cax`

```python
_grow_existing_cax(cax: Axes, position: _Position, new_thickness: float) -> None
```

Widens (or heightens) a previously-created colorbar Axes to `new_thickness`,
keeping its outer edge (the fixed side, away from the grid) in place -- so an
earlier, smaller colorbar sharing a margin with a new, larger one ends up the
same size, per `_make_colorbar_axes`' "reuse the shared margin" behavior.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `cax` | Axes | The existing colorbar Axes to grow. |
| `position` | str | Which side it's attached to. |
| `new_thickness` | float | Its new thickness, in figure-fraction units. |


## function `_parse_fraction`

```python
_parse_fraction(value: str | float) -> float
```

Parses a size/fraction value into a plain float in \[0, 1\].


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `value` | str \| float | Either a percentage string (e.g. "5%") or a bare float already expressed as a fraction (e.g. 0.05). |

**Returns:**

| Type | Description |
| --- | --- |
| - | The parsed fraction. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `value` is a string that doesn't end in '%'. |


## function `_decoration_margin`

```python
_decoration_margin(ax: Axes, figure: Figure, position: _Position, plain: Bbox) -> float
```

Measures how far `ax`'s ticks/axis-label/title on the `position` side (the
decorations matplotlib draws just outside the Axes' own box, e.g. y-tick labels
to its left) extend beyond `plain`, in figure-fraction units.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `ax` | Axes | The Axes to measure. |
| `figure` | Figure | The parent Figure (for the figure-fraction transform). |
| `position` | str | Which side to measure ('left', 'right', 'top', 'bottom'). |
| `plain` | Bbox | `ax`'s own position box (`ax.get_position()`), passed in to avoid recomputing it. |

**Returns:**

| Type | Description |
| --- | --- |
| - | The margin, in figure-fraction units, never negative. |


## function `_reanchor_secondary_dimension`

```python
_reanchor_secondary_dimension(ax: Axes, original_p: Bbox, position: _Position, vertical: bool) -> None
```

Re-anchors an Axes' *other* dimension after `_resize_others_to_match` matched its
primary one, in case a fixed-aspect Axes' own aspect settling adjusted it too.

Given `vertical=True` (height was just matched), a width side effect is possible;
given `vertical=False` (width was just matched), a height side effect is possible.
Either way, matplotlib's own aspect settling centers that side effect within the
Axes' *original* span, rather than anchoring it on the same side `position`
itself anchors on (e.g. "right": fixed x0) -- left alone, this Axes would end up
correctly *sized* but not correctly *aligned* with a sibling elsewhere in the
canvas that shares its column/row (see `_realign_grid_siblings`). Re-anchoring is
a pure translation (same width/height as just settled), so it doesn't trigger
any further aspect adjustment.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `ax` | Axes | The Axes just resized by `_resize_others_to_match`. |
| `original_p` | Bbox | Its position box before that resize. |
| `position` | str | The colorbar's position, as passed to `_make_colorbar_axes`. |
| `vertical` | bool | Matches `_resize_others_to_match`'s own `vertical` argument. |


## function `_resize_others_to_match`

```python
_resize_others_to_match(axes: list[Axes], positions: list[Bbox], edge_axes: set[Axes], final_size: float, position: _Position, vertical: bool) -> None
```

Centers every group Axes not in `edge_axes` on `final_size` along the cross
dimension (height if `vertical`, width otherwise).

A fixed-aspect edge Axes (e.g. `Image`'s default `aspect="equal"`) may end up
shrinking that dimension too, as a side effect of `_make_colorbar_axes` shrinking
its other dimension to make room for the colorbar; without this, the rest of the
group would be left visually mismatched. Each resized Axes' own aspect settles in
turn (via the same immediate, stable `set_position()` behavior noted in
`_make_colorbar_axes`) -- if it shares the edge Axes' data aspect ratio, it
converges to the exact same final box; if not, only this dimension is matched.
`_reanchor_secondary_dimension` then fixes up the *other* dimension, in case that
settling centered it instead of anchoring it like the edge Axes' own shrink did.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axes` | list\[Axes\] | The full target group. |
| `positions` | list\[Bbox\] | `axes`' original position boxes (`get_position()`, captured before any resizing), in the same order. |
| `edge_axes` | set\[Axes\] | The subset already resized by `_make_colorbar_axes`; left untouched here. |
| `final_size` | float | The edge Axes' actual final height/width, in figure-fraction units, to match. |
| `position` | str | The colorbar's position, as passed to `_make_colorbar_axes`. |
| `vertical` | bool | `True` to match height (for a "left"/"right" colorbar), `False` to match width (for a "top"/"bottom" one). |


## function `_realign_grid_siblings`

```python
_realign_grid_siblings(all_axes: list[Axes], all_positions: list[Bbox], target_axes: list[Axes], target_positions: list[Bbox], position: _Position) -> list[Axes]
```

Realigns the rest of the canvas's grid with the (already resized) target group, so
a colorbar attached to only one row/column doesn't leave it visually narrower or
shorter than the rest of the grid.

For each target Axes, finds every *other* Axes in `all_axes` that originally
shared its column ("left"/"right" `position`, i.e. same x0/x1) or row ("top"/
"bottom", i.e. same y0/y1), and matches its width (or height) to that target
Axes' actual final size, anchored on the same side `position` itself anchors on
(e.g. "right": fixed x0, matching x1 moves inward) so the whole column/row of the
grid stays exactly aligned, not just equal-sized. This is a no-op for any sibling
that already matches (e.g. a target group whose shrink didn't need to touch this
dimension in the first place), and finds no siblings at all for a `col=`/`row=`
target whose position is perpendicular to the group's own arrangement (e.g.
`col=` with a "left"/"right" colorbar: every Axes sharing a column is already
inside the target group, since a column *is* that set of Axes).


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `all_axes` | list\[Axes\] | Every Axes in the canvas's grid. |
| `all_positions` | list\[Bbox\] | `all_axes`' original position boxes (`get_position()`, captured before any resizing), in the same order. |
| `target_axes` | list\[Axes\] | The (already resized) target group passed to `_make_colorbar_axes`. |
| `target_positions` | list\[Bbox\] | `target_axes`' original position boxes, in the same order -- used to identify which column/row each one was in. |
| `position` | str | The colorbar's position, as passed to `_make_colorbar_axes`. |

**Returns:**

| Type | Description |
| --- | --- |
| list\[Axes\] | Every sibling Axes found (whether or not it needed resizing), so the caller can stamp them all with a margin reservation too. |


## function `_make_colorbar_axes`

```python
_make_colorbar_axes(figure: Figure, axes: list[Axes], all_axes: list[Axes], position: _Position, size: str | float, padding: float) -> Axes
```

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
The rest of the canvas's grid is then realigned to match too, via
`_realign_grid_siblings`, so a colorbar on only one row/column doesn't leave it
narrower/shorter than the rest of the grid.

If the edge Axes already carries a margin reservation on this side (stamped by an
earlier `Colorbar` targeting a sibling row/column that shares it, via
`_get_reservation`/`_stamp_reservation`), that margin is reused instead of
carving out a second one: only the extra space this call needs *beyond* what's
already reserved is taken (zero, if this call's own thickness+padding doesn't
exceed it), and any previously-created colorbar sharing the margin is grown to
match if this call needs more. Without this, two colorbars on different rows of
the same columns (or columns of the same rows) would compound: each one's
`_realign_grid_siblings` step would shrink the other's row/column again, on top of
what the first one already reserved.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `figure` | Figure | The parent Figure the Axes belong to. |
| `axes` | list\[Axes\] | The target group (one or more Axes sharing part of an edge). |
| `all_axes` | list\[Axes\] | Every Axes in the canvas's grid (a superset of `axes`), for `_realign_grid_siblings`. |
| `position` | str | Which side of the group's bounding box to attach the colorbar to. |
| `size` | str \| float | The colorbar's thickness -- a percentage string (e.g. "5%") or a bare fraction -- of the group's width ('left'/'right') or height ('top'/'bottom'). |
| `padding` | float | The gap between the group's Axes (and their ticks/labels) and the colorbar, in inches. |

**Returns:**

| Type | Description |
| --- | --- |
| - | The new Axes to draw the colorbar into. |


## class `Colorbar`

Class for drawing an explicit colorbar on a canvas, optionally shared across
several subplots.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `source` | Image \| Hist2D | The already-drawn drawable whose color mapping (mappable, colormap, normalization) the colorbar represents. |
| `mpl_colorbar` | MplColorbar or None | The underlying `matplotlib.colorbar.Colorbar` artist, populated after `draw` runs, for advanced customization. |


**Defined attributes:**

- `source: Image | Hist2D`
- `mpl_colorbar: MplColorbar | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: PlotN | None=None, row: int | None=None, col: int | None=None, label: str | None=None, **kwargs) -> None
```

Draws the colorbar, spanning one or more subplots.

The colorbar always ends up positioned right next to the targeted subplot(s),
with the requested spacing, and the same length as them (their full shared
height for `position="left"/"right"`, or width for `"top"/"bottom"`) -- the
targeted subplot(s) are shrunk just enough to make room for it within their
own footprint, so it never overlaps a neighboring subplot outside the target.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the colorbar on. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to attach the colorbar to. At most one of `plot_n`, `row`, `col` may be given; defaults to `0` when none are. See `Canvas.plot_indices`. |
| `row` | int, optional | A row of the `canvas`'s grid to share the colorbar across. Not supported when `canvas` is a `ZoomInset`. |
| `col` | int, optional | A column of the `canvas`'s grid to share the colorbar across. Not supported when `canvas` is a `ZoomInset`. |
| `label` | str, optional | The colorbar's label. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `position` | str | Which side to attach the colorbar to -- "left", "right", "top", or "bottom". Defaults to "right". |
| `size` | str \| float | The colorbar's thickness, as a percentage string (e.g. "5%") or bare fraction of the target(s)' own width (for "left"/"right") or height (for "top"/"bottom"). Defaults to "5%". |
| `padding` | float | The gap between the target(s) and the colorbar, in inches. Defaults to 0.1. |
| `**kwargs` | - | Anything else is passed straight through to `matplotlib.figure.Figure.colorbar` for cosmetic tweaks unrelated to placement (e.g. `ticks`, `format`, `extend`, `alpha`). |

**Raises:**

| Type | Description |
| --- | --- |
| RuntimeError | If `source` has not been drawn yet. |
| ValueError | If `position` is not one of "left", "right", "top", "bottom". |
| ValueError | If more than one of `plot_n`, `row`, `col` is given. |
| ValueError | If `row`/`col` is given for a `ZoomInset`. |
