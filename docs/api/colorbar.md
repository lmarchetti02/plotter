# `plotter.colorbar`

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


## function `_make_colorbar_axes`

```python
_make_colorbar_axes(figure: Figure, axes: list[Axes], position: _Position, size: str | float, padding: float) -> Axes
```

Carves out a new Axes for a colorbar next to a group of Axes.

Shrinks whichever Axes in `axes` sit on the group's edge facing `position` (e.g.
for a row of Axes and `position="right"`, only the rightmost one; for a column,
all of them, since they share that edge) so the colorbar occupies space that
used to belong to the group's own footprint, without overlapping any Axes
outside the group. The colorbar itself is placed just outside those Axes' own
ticks/axis-label/title on that side, so it doesn't overlap them either.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `figure` | Figure | The parent Figure the Axes belong to. |
| `axes` | list\[Axes\] | The target group (one or more Axes sharing part of an edge). |
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
draw(self, canvas: Canvas | ZoomInset, plot_n: int | tuple[int, int] | str | None=None, row: int | None=None, col: int | None=None, label: str | None=None, position: _Position='right', size: str | float='5%', padding: float=0.1, **kwargs) -> None
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
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to attach the colorbar to. At most one of `plot_n`, `row`, `col` may be given; defaults to `0` when none are. See `Canvas.plot_indices`. |
| `row` | int, optional | A row of the `canvas`'s grid to share the colorbar across. Not supported when `canvas` is a `ZoomInset`. |
| `col` | int, optional | A column of the `canvas`'s grid to share the colorbar across. Not supported when `canvas` is a `ZoomInset`. |
| `label` | str, optional | The colorbar's label. Defaults to `None`. |
| `position` | str, optional | Which side to attach the colorbar to -- "left", "right", "top", or "bottom". Defaults to "right". |
| `size` | str \| float, optional | The colorbar's thickness, as a percentage string (e.g. "5%") or bare fraction of the target(s)' own width (for "left"/"right") or height (for "top"/"bottom"). Defaults to "5%". |
| `padding` | float, optional | The gap between the target(s) and the colorbar, in inches. Defaults to 0.1. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `` | - | Passed straight through to `matplotlib.figure.Figure.colorbar` for cosmetic tweaks unrelated to placement (e.g. `ticks`, `format`, `extend`, `alpha`). |

**Raises:**

| Type | Description |
| --- | --- |
| RuntimeError | If `source` has not been drawn yet. |
| ValueError | If `position` is not one of "left", "right", "top", "bottom". |
| ValueError | If more than one of `plot_n`, `row`, `col` is given. |
| ValueError | If `row`/`col` is given for a `ZoomInset`. |
