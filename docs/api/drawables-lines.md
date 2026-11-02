# `plotter.drawables.lines`

## class `LinePlot(Drawable)`

Class for creating a line plot from raw (x, y) data to be drawn on a canvas.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `x` | NArray1D\[Any\] | The values of the independent variable. |
| `y` | NArray1D\[Any\] | The values of the dependent variable. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If x and y do not have the same dimensions. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `draw_kwargs: ClassVar[frozenset[str]]`
- `x: NArray1D[Any]`
- `y: NArray1D[Any]`

### Methods

#### `from_y`

```python
from_y(cls, y: NArray1D[Any], **kwargs) -> 'LinePlot'
```

Builds a `LinePlot` from just `y`-values, using an implicit index range for `x`.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `y` | NArray1D\[Any\] | The values of the dependent variable. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `` | - | Any keyword argument accepted by `LinePlot`'s constructor other than `x`/`y`. |

**Returns:**

| Type | Description |
| --- | --- |
| - | A line plot with `x = numpy.arange(len(y))`. |


#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the plot on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the plot on. |
| `plot_n` | int, optional | The index of the subplot. Defaults to 0. |
| `label` | str, optional | The label for the plot in the legend. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The Matplotlib color of the plot. Defaults to "darkgreen". |
| `lw` | float | The line width. Defaults to 1.5. |
| `style` | str | The line style. Defaults to `"-"`. |
| `alpha` | float | The opacity of the line. Defaults to 1.0. |
| `inverted` | bool | If `True`, plots the inverse function. Defaults to `False`. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `plot_n` is out of range for `canvas`. |
| TypeError | If a keyword argument not listed above is given. |
