# `plotter.scatter`

## class `ScatterPlot(Drawable)`

Class for creating a scatter plot with error bars.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `x` | NArray1D\[Any\] | The array containing the x values. |
| `y` | NArray1D\[Any\] | The array containing the y values. |
| `xerr` | NArray1D\[Any\] or float, optional | The array containing the errors of the x values. If a float is passed, all the errors are assumed identical. |
| `yerr` | NArray1D\[Any\] or float, optional | The array containing the errors of the y values. If a float is passed, all the errors are assumed identical. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If x and y values do not have the same dimensions. |
| ValueError | If y error values do not have the same dimensions as the y values. |
| ValueError | If x error values do not have the same dimensions as the x values. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `x: NArray1D[Any]`
- `y: NArray1D[Any]`
- `yerr: NArray1D[Any] | float | None`
- `xerr: NArray1D[Any] | float | None`

### Methods

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
| `err_color` | str | The Matplotlib color of the error bars. Defaults to "firebrick". |
| `marker` | str | The kind of Matplotlib marker to use. Defaults to `"o"`. |
| `ms` | float | The dimensions of the markers. Defaults to 4. |
| `err_width` | float | The width of the error bars. Defaults to 1. |
| `ticks_size` | float | The size of the ticks on the error bars. Defaults to 2. |
