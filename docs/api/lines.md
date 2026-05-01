# `plotter.lines`

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

#### `post_init`

```python
__post_init__(self) -> None
```

Makes x-grid denser if necessary.


#### `draw`

```python
draw(self, canvas: Canvas, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the plot on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas | The canvas object to draw the plot on. |
| `plot_n` | int, optional | The index of the subplot. Defaults to 0. |
| `label` | str, optional | The label for the plot in the legend. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The Matplotlib color of the plot. Defaults to "darkgreen". |
| `lw` | float | The line width. Defaults to 1.5. |
| `style` | str | The line style. Defaults to `"-"`. |
| `inverted` | bool | If `True`, plots the inverse function. Defaults to `False`. |


#### `make_wider`

```python
_make_wider(data: NArray1D[Any], left: float, right: float, density: int) -> NArray1D[Any]
```

Makes a 1D array wider by a specified percentage and increases its density.

The function extends the array's range by a percentage of its total span,
as specified by `left` and `right`. It then calls `_make_denser()` to
interpolate new data points and increase the array's density.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `data` | np.ndarray | The 1D input array. |
| `left` | float | The percentage to widen the array to the left (e.g., 0.2 for 20%). |
| `right` | float | The percentage to widen the array to the right (e.g., 0.1 for 10%). |
| `density` | int | The density factor to pass to the `_make_denser()` function. |

**Returns:**

| Type | Description |
| --- | --- |
| np.ndarray | The new, wider and denser array. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `density` is less than 1. |
| ValueError | If `left` or `right` are less than 0. |


#### `make_denser`

```python
_make_denser(data: NArray1D[Any], density: int) -> NArray1D[Any]
```

Creates a "denser" numpy array by adding elements between existing ones.

This function finds the minimum distance 'd' between consecutive elements.
For each pair of consecutive elements, it inserts new points, with the number
of points determined by the ratio of the pair's distance to `d`, multiplied
by `density` and rounded to the nearest integer.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `data` | NArray1D\[Any\] | The 1D numpy array to be made denser. |
| `density` | int | A scaling factor for the number of elements to add between existing elements. A value of 1 returns the original array. |

**Returns:**

| Type | Description |
| --- | --- |
| NArray1D\[Any\] | A new 1D numpy array with a higher density of elements. |
