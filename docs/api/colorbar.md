# `plotter.colorbar`

## class `Colorbar`

Class for drawing an explicit colorbar on a canvas, optionally shared across
several subplots.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `source` | Image \| Hist2D | The already-drawn drawable whose color mapping (mappable, colormap, normalization) the colorbar represents. |


**Defined attributes:**

- `source: Image | Hist2D`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int | tuple[int, int] | str | None=None, row: int | None=None, col: int | None=None, label: str | None=None, **kwargs) -> None
```

Draws the colorbar, spanning one or more subplots.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the colorbar on. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to attach the colorbar to. At most one of `plot_n`, `row`, `col` may be given; defaults to `0` when none are. See `Canvas.plot_indices`. |
| `row` | int, optional | A row of the `canvas`'s grid to share the colorbar across. Not supported when `canvas` is a `ZoomInset`. |
| `col` | int, optional | A column of the `canvas`'s grid to share the colorbar across. Not supported when `canvas` is a `ZoomInset`. |
| `label` | str, optional | The colorbar's label. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `` | - | Passed straight through to `matplotlib.figure.Figure.colorbar` (e.g. `orientation`, `location`, `fraction`, `pad`, `shrink`, `aspect`). |

**Raises:**

| Type | Description |
| --- | --- |
| RuntimeError | If `source` has not been drawn yet. |
| ValueError | If more than one of `plot_n`, `row`, `col` is given. |
| ValueError | If `row`/`col` is given for a `ZoomInset`. |
