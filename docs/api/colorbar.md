# `plotter.colorbar`

## class `Colorbar`

Class for drawing an explicit colorbar on a canvas, optionally shared across
several subplots.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `source` | Image \| RawHist2D \| BinnedHist2D | The already-drawn drawable whose color mapping (mappable, colormap, normalization) the colorbar represents. |
| `mpl_colorbar` | MplColorbar or None | The underlying `matplotlib.colorbar.Colorbar` artist, populated after `draw` runs, for advanced customization. |


**Defined attributes:**

- `source: Image | RawHist2D | BinnedHist2D`
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
| `plot_n` | PlotN, optional | The index or indices of the subplots to attach the colorbar to. At most one of `plot_n`, `row`, `col` may be given; defaults to `0` when none are. See `Canvas.plot_indices`. A `list\[int\]` must resolve to consecutive indices -- the colorbar's placement geometry has no meaning for a gapped target. |
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
| ValueError | If `plot_n` is a list that does not resolve to consecutive indices. |
