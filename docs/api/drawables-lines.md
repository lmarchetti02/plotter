# `plotter.drawables.lines`

## class `LinePlot(Drawable)`

Class for creating a 1D function plot to be drawn on a canvas.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `x` | NArray1D\[Any\] | The values of the independent variable. |
| `f` | Callable\[\[NArray1D\[Any\]\], NArray1D\[Any\]\] \| NArray1D\[Any\] | The function that defines the plot, or an array of y-values. |
| `wider` | tuple\[float, float\], optional | The percentages (left, right) to which the domain of the function `f` is to be widened. Defaults to `(0, 0)`. |
| `dens` | int, optional | The density factor to be passed to `make_wider()`. Defaults to 1. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If x and f as an array do not have the same dimensions. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `x: NArray1D[Any]`
- `f: Callable[[NArray1D[Any]], NArray1D[Any]] | NArray1D[Any]`
- `wider: tuple[float, float]`
- `dens: int`
- `y: NArray1D[Any] | None`

### Methods

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
