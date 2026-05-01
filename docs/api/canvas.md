# `plotter.canvas`

## class `_Counters`

Container class to store the counters of the `Canvas`.

These counters keep track of the number of objects that have
to be drawn on each subplot. This way, each time an object
calls its `draw` function, the label corresponding to said
object can be retrieved and drawn.


### Methods

#### `getattr`

```python
__getattr__(self, name: str) -> list[int]
```

Returns the counters associated with a drawable family.


#### `is_empty`

```python
is_empty(self) -> bool
```

Checks if there is any label that should be displayed.


#### `initialize_counters`

```python
initialize_counters(cls, n_plots: int) -> '_Counters'
```

Initializes an object filled with zeros.


## class `Canvas`

Class for creating an empty canvas (xy-plane).


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `text_file` | str | The name of the JSON file containing the text to be added to the plot. |
| `rows_cols` | tuple\[int, int\], optional | A tuple with the number of rows and columns of subplots. Defaults to (1, 1). |
| `figsize` | tuple\[int, int\], optional | A tuple containing the dimensions of the canvas (width, height). Defaults to (12, 8). |
| `dpi` | int, optional | The number of dots per inch (DPI) of the image. Defaults to 150. |
| `save` | str, optional | The name of the file to save the plot to. The plots are stored in 'plotter/img/'. Defaults to an empty string. |
| `figure` | Figure | The matplotlib Figure object. |
| `axes` | list\[Axes\] | A list with the matplotlib Axes object corresponding to each subplot. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the number of columns and/or the number of rows is negative. |


**Defined attributes:**

- `text_file: str`
- `rows_cols: tuple[int, int]`
- `figsize: tuple[int, int]`
- `dpi: int`
- `save: str`
- `show: bool`
- `figure: Figure`
- `axes: list[Axes]`
- `text: Text`
- `counters: _Counters`
- `_n_plots: int`
- `_loc_legend: list[int]`

### Methods

#### `post_init`

```python
__post_init__(self) -> None
```

Initializes the necessary attributes.


#### `enter`

```python
__enter__(self)
```

Defines what happens when the user enters a 'Canvas' context.


#### `exit`

```python
__exit__(self, exc_type, exc_val, exc_tb)
```

Defines what happens when the user exits a 'Canvas' context.


#### `setup`

```python
setup(self, plot_n: int | tuple[int, int] | str='all', **kwargs) -> None
```

Sets up the properties of the subplots.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to configure. Defaults to 'all'. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `xlim` | tuple\[float, float\] | The limits for the x-axis. |
| `ylim` | tuple\[float, float\] | The limits for the y-axis. |
| `xscale` | str | The scale for the x-axis ('linear', 'log', 'symlog'). |
| `yscale` | str | The scale for the y-axis ('linear', 'log', 'symlog'). |
| `nogrid` | bool | If True, removes the grid from the plot. |
| `inverted` | tuple\[bool, bool\] | A tuple to invert the x and y axes respectively (e.g., `(True, False)`). |
| `legend` | int | Force the position of the legend to a specified one. See 'plotter/utils/info/legend.png'. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


#### `draw_line`

```python
draw_line(self, orientation: str, point: float=0.0, plot_n: int=0, **kwargs) -> None
```

Draws horizontal and vertical lines on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `orientation` | str | The orientation of the line. Use 'v' for vertical or 'h' for horizontal. |
| `point` | float, optional | The coordinate of the line. Defaults to 0. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The color of the line. Defaults to 'black'. |
| `style` | str | The style of the line (e.g., '-', '--', '-.', ':'). Defaults to '-'. |
| `width` | float | The width of the line. Defaults to 0.5. |
| `label` | str | The label for the line in the legend. Defaults to None. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the orientation is not 'v' or 'h'. |


#### `turn_scientific`

```python
turn_scientific(self, axis: str, plot_n: int=0, limits: tuple[int, int] | int=(0, 0)) -> None
```

Sets the ticks of an axis to scientific notation.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to modify: 'x', 'y', or 'both'. |
| `plot_n` | int, optional | The index of the subplot to consider. Defaults to 0. |
| `limits` | tuple\[int, int\] or int, optional | Controls the scientific notation.<br>- `(m, n)`: Scientific notation is used for numbers outside 10^m to 10^n.<br>- `0`: Scientific notation is used for all numbers.<br>- `m`: Fixes the order of magnitude to 10^m. If only one int is passed, m=n is assumed. Defaults to (0, 0). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x', 'y', or 'both'. |


#### `set_ticks`

```python
set_ticks(self, axis: str, positions: tuple[float, ...], labels: tuple[str, ...] | None=None, plot_n: int=0) -> None
```

Modifies the ticks of an axis.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to modify: 'x' or 'y'. |
| `positions` | tuple\[float, ...\] | A tuple with the positions of the ticks. |
| `labels` | tuple\[str, ...\], optional | A tuple with the labels for the ticks. If None, the labels will be the same as the positions. Defaults to None. |
| `plot_n` | int, optional | The index of the subplot to consider. Defaults to 0. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x' or 'y'. |


#### `add_scalebar`

```python
add_scalebar(self, size: float, label: str, plot_n: int=0, **kwargs) -> None
```

Adds a scalebar (and, thus, removes the axis labels).


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `size` | float | The horizontal size (in coordinates of axis). |
| `label` | str | The label (e.g., "1 cm", "10 μm"). |
| `plot_n` | int, optional | The index of the subplot. Defaults to 0. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `location` | str | Where to put the scalebar. Defaults to "upper right". |
| `color` | str | The color. Defaults to "black". |
| `v_size` | float | The vertical size. Defaults to None, which results in 1% of the height of the axis. |


#### `legend`

```python
_legend(self) -> None
```

This function generates the plot legend.


#### `save`

```python
_save(self) -> None
```

If specified by the user, this function saves
the plot that has been generated to a file.
