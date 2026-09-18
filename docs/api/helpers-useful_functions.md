# `plotter.helpers.useful_functions`

## function `get_colors`

```python
get_colors(length: int, gradient: tuple[str, str] | None=None) -> list[str]
```

Generate a list of colors for the plots.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `length` | int | The length of the list. |
| `gradient` | tuple\[str, str\], optional | The initial and final colors of the gradient (see plotter/utils/info for a list of available colors). Defaults to None, which results in a list of random colors. |

**Returns:**

| Type | Description |
| --- | --- |
| list\[str\] | The list of colors. |


## function `stack_bottoms`

```python
stack_bottoms(heights: list[NArray1D[Any]]) -> list[NArray1D[Any]]
```

Computes the cumulative starting offset ("bottom") for each series in a stack of bar charts.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `heights` | list\[NArray1D\[Any\]\] | One array of bar heights per series, in stacking order (bottom to top). All arrays must have the same length. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `heights` is empty. |
| ValueError | If the arrays in `heights` don't all have the same length. |

**Returns:**

| Type | Description |
| --- | --- |
| list\[NArray1D\[Any\]\] | One array of cumulative offsets per series, the same shape as `heights`, suitable for `BarChart.draw`'s `bottom` keyword argument -- the first entry is all zeros, and each subsequent entry is the running total of every series stacked below it. |
