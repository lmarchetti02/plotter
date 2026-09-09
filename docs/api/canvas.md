# `plotter.canvas`

## function `_configure_axes`

```python
_configure_axes(axes: Axes, text: PlotText, **kwargs) -> None
```

Applies grid, limits, scale, inversion, labels, and title to a single `Axes`.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axes` | Axes | The Axes object to configure. |
| `text` | PlotText | The title and axis labels to apply. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `` | - | See `Canvas.setup`. |


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


## class `ZoomInset`

A single zoomed-in inset panel returned by `Canvas.add_zoom_inset`.

Exposes the same `axes`/`counters`/`text`/`figure` surface as `Canvas`, so any
`Drawable` can be drawn into it exactly like a real `Canvas` subplot (e.g.
`some_drawable.draw(inset)`). Also exposes `setup` to configure its `Axes`.
Other cosmetic `Canvas` helpers (`draw_line`, `add_text`, ...) are not available
on it — use `inset.axes\[0\]` directly for those.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `axes` | list\[Axes\] | A single-element list containing the inset `Axes`. |
| `figure` | Figure | The parent `Canvas`'s Figure (the inset lives on it). |
| `text` | Text | Blank title/axis-labels/label-lists for the panel — there is no JSON slot for an ad hoc inset. |
| `counters` | _Counters | Fresh, zeroed counters scoped to this one panel. |


**Defined attributes:**

- `axes: list[Axes]`
- `figure: Figure`
- `text: Text`
- `counters: _Counters`

### Methods

#### `post_init`

```python
__post_init__(self) -> None
```

Initializes the blank text and zeroed counters for the panel.


#### `setup`

```python
setup(self, **kwargs) -> None
```

Sets up the properties of the panel's `Axes`.


**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `xlim` | tuple\[float, float\] | The limits for the x-axis. |
| `ylim` | tuple\[float, float\] | The limits for the y-axis. |
| `xscale` | str | The scale for the x-axis ('linear', 'log', 'symlog'). |
| `yscale` | str | The scale for the y-axis ('linear', 'log', 'symlog'). |
| `nogrid` | bool | If True, removes the grid from the plot. |
| `inverted` | tuple\[bool, bool\] | A tuple to invert the x and y axes respectively (e.g., `(True, False)`). |


## class `Canvas`

Class for creating an empty canvas (xy-plane).


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `text_file` | str | The name of the JSON file containing the text to be added to the plot. |
| `rows_cols` | tuple\[int, int\], optional | A tuple with the number of rows and columns of subplots. Defaults to (1, 1). |
| `figsize` | tuple\[float, float\], optional | A tuple containing the dimensions of the canvas (width, height). Defaults to (12, 8). |
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
- `figsize: tuple[float, float]`
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


#### `add_text`

```python
add_text(self, text: str, position: tuple[float, float], plot_n: int=0, point: tuple[float, float] | None=None, **kwargs) -> None
```

Adds a text label to the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `text` | str | The text to display. |
| `position` | tuple\[float, float\] | The position of the text in data coordinates. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `point` | tuple\[float, float\] \| None, optional | A point to annotate. When provided, an arrow is drawn from the text to this point. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The text color. Defaults to 'black'. |
| `fontsize` | float | The font size. Defaults to Matplotlib's default. |
| `ha` | str | Horizontal alignment. Defaults to 'center'. |
| `va` | str | Vertical alignment. Defaults to 'center'. |
| `rotation` | float | The text rotation in degrees. Defaults to 0. |
| `arrowprops` | dict | Arrow styling passed to `Axes.annotate`. |


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


#### `add_zoom_inset`

```python
add_zoom_inset(self, xlim: tuple[float, float], ylim: tuple[float, float], plot_n: int=0, **kwargs) -> ZoomInset
```

Adds a zoomed-in inset panel showing a region of a subplot.

The source subplot gets a rectangle around the requested region, connected
to the inset panel by two lines. The panel itself starts empty: draw into
it via `some_drawable.draw(panel)`, exactly like a real `Canvas` subplot.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `xlim` | tuple\[float, float\] | The x-axis limits of the region to zoom into. |
| `ylim` | tuple\[float, float\] | The y-axis limits of the region to zoom into. |
| `plot_n` | int, optional | The index of the subplot to zoom into. Defaults to 0. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `location` | str | Where to place the inset panel. Defaults to "upper right". |
| `width` | str or float | The width of the inset panel, as a percentage of the subplot (e.g. "30%") or an absolute size in inches. Defaults to "30%". |
| `height` | str or float | The height of the inset panel, same format as `width`. Defaults to "30%". |
| `loc1` | int | The corner of the region rectangle connected to the inset panel by the first line (Matplotlib corner codes, 1-4). Defaults to 2. |
| `loc2` | int | The corner connected by the second line. Defaults to 4. |
| `edgecolor` | str | The color of the region rectangle and connector lines. Defaults to "0.5". |
| `ticks` | bool | If True, keeps the tick marks and labels on the inset panel. Defaults to False, for a clean panel showing only the zoomed-in content. |

**Returns:**

| Type | Description |
| --- | --- |
| - | The panel to draw the zoomed-in content into. |


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
