# `plotter.drawables.scatter`

## class `ScatterPlot(Drawable)`

Class for creating a scatter plot with error bars.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `x` | NArray1D\[Any\] | The array containing the x values. |
| `y` | NArray1D\[Any\] | The array containing the y values. |
| `xerr` | ErrorBars, optional | The errors of the x values: a float (identical for every point), an array of shape (N,) (symmetric, one per point), or an array of shape (N, 2) (asymmetric, one (left, right) pair of error sizes per point). |
| `yerr` | ErrorBars, optional | The errors of the y values: a float (identical for every point), an array of shape (N,) (symmetric, one per point), or an array of shape (N, 2) (asymmetric, one (low, high) pair of error sizes per point). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If x and y values do not have the same dimensions. |
| ValueError | If y error values are not of shape (N,) or (N, 2), with N the number of points. |
| ValueError | If x error values are not of shape (N,) or (N, 2), with N the number of points. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `x: NArray1D[Any]`
- `y: NArray1D[Any]`
- `yerr: ErrorBars | None`
- `xerr: ErrorBars | None`

### Methods

#### `from_y`

```python
from_y(cls, y: NArray1D[Any], **kwargs) -> 'ScatterPlot'
```

Builds a `ScatterPlot` from just `y`-values, using an implicit index range for `x`.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `y` | NArray1D\[Any\] | The array containing the y values. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `` | - | Any keyword argument accepted by `ScatterPlot`'s constructor other than `x`/`y`. |

**Returns:**

| Type | Description |
| --- | --- |
| - | A scatter plot with `x = numpy.arange(len(y))`. |


#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the scatter plot on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to which the scatter plot is to be attached. |
| `plot_n` | int, optional | The index of the subplot. Defaults to 0. |
| `label` | str, optional | The label for the scatter plot in the legend. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The Matplotlib color of the points. Defaults to "firebrick". |
| `err_color` | str | The Matplotlib color of the error bars. Defaults to "black". |
| `marker` | str | The kind of Matplotlib marker to use. Defaults to `"o"`. |
| `ms` | float | The dimensions of the markers. Defaults to 4. |
| `err_width` | float | The width of the error bars. Defaults to 1. |
| `err_capsize` | float | The size of the ticks on the error bars. Defaults to 2. |
| `alpha` | float | The opacity of the points. Defaults to 1.0. |
| `line` | bool | If `True`, also draws a line connecting the points, in the order they're given. Defaults to `False`. |
| `line_color` | str | The Matplotlib color of the connecting line. Defaults to the points' own `color`. |
| `line_width` | float | The width of the connecting line. Defaults to 1.5. |
| `line_style` | str | The Matplotlib style of the connecting line. Defaults to `"-"`. |
| `line_alpha` | float | The opacity of the connecting line. Defaults to the points' own `alpha`. |
