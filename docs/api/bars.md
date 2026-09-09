# `plotter.bars`

## class `BarChart(Drawable)`

Class for creating a bar chart.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `x` | NArray1D\[Any\] | The array containing the x positions of the bars. |
| `heights` | NArray1D\[Any\] | The array containing the heights of the bars. |
| `yerr` | NArray1D\[Any\] \| float \| None, optional | The uncertainty on the bar heights. If a float is passed, all the errors are assumed identical. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If x and heights do not have the same dimensions. |
| ValueError | If yerr as an array does not have the same dimensions as heights. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `x: NArray1D[Any]`
- `heights: NArray1D[Any]`
- `yerr: NArray1D[Any] | float | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the bar chart on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the bar chart on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `label` | str, optional | The label for the bar chart in the legend. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `width` | float | The width of the bars. Defaults to 0.8. |
| `color` | str | The Matplotlib color of the bars. Defaults to "steelblue". |
| `alpha` | float | The transparency of the bars. Defaults to 0.9. |
| `ecolor` | str | The color of the error bars. Defaults to "black". |
| `capsize` | float | The size of the error bar ticks. Defaults to 3. |
| `lw` | float | The width of the bar edges. Defaults to 0. |
| `edgecolor` | str | The color of the bar edges. Defaults to "midnightblue". |
