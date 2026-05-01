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
