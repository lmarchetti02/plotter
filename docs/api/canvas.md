# `plotter.canvas`

## function `_oriented_limits`

```python
_oriented_limits(limits: tuple[float, float], reference: tuple[float, float]) -> tuple[float, float]
```

Orders `limits` to increase or decrease like `reference` does.

Matplotlib inverts an Axes' limits (e.g. `imshow`'s default `origin="upper"`
leaves the y-axis decreasing) to control which direction is "up" on screen;
this keeps a newly-set pair of limits visually consistent with that.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `limits` | tuple\[float, float\] | The limits to order, in either direction. |
| `reference` | tuple\[float, float\] | The existing limits whose direction to match. |

**Returns:**

| Type | Description |
| --- | --- |
| tuple\[float, float\] | `limits`, sorted to match `reference`'s direction. |


## function `_reoriented_loc`

```python
_reoriented_loc(loc: int, x_inverted: bool, y_inverted: bool) -> int
```

Remaps a `mark_inset` corner code so it keeps pointing at the same visual corner
when the Axes it refers to has an inverted x- and/or y-axis.

`mark_inset`'s corner codes are defined in terms of an Axes' raw (x0,y0)-(x1,y1)
limits, which only match their documented visual meaning (e.g. 1=upper right) when
both axes increase left-to-right/bottom-to-top; an inverted axis flips that.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `loc` | int | The requested corner (1-4, matplotlib's convention). |
| `x_inverted` | bool | Whether the Axes' x-axis decreases instead of increasing. |
| `y_inverted` | bool | Whether the Axes' y-axis decreases instead of increasing. |

**Returns:**

| Type | Description |
| --- | --- |
| - | The corner code to pass to `mark_inset` to get the same visual corner. |


## function `_draw_zoom_indicator`

```python
_draw_zoom_indicator(parent_axes: Axes, inset_axes: Axes, loc1: int, loc2: int, x_inverted: bool, y_inverted: bool, **kwargs) -> None
```

Draws a rectangle around an inset's region on its source subplot, connected to the
inset panel by two lines.

Behaves like `mpl_toolkits.axes_grid1.inset_locator.mark_inset`, except the two ends
of each connector line can use different corner codes: `inset_axes`'s own on-screen
box is never inverted, but the rectangle (`inset_axes.viewLim` transformed into the
parent's data space) is, whenever `inset_axes`'s axes are — so only the rectangle's
corner codes are remapped (via `_reoriented_loc`) to keep pointing at the same visual
corner; `mark_inset` itself has no way to do this since it applies one corner code to
both ends.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `parent_axes` | Axes | The source subplot to draw the rectangle on. |
| `inset_axes` | Axes | The inset panel the rectangle is connected to. |
| `loc1` | int | The corner connected by the first line (matplotlib corner codes, 1-4: upper right, upper left, lower left, lower right). |
| `loc2` | int | The corner connected by the second line. |
| `x_inverted` | bool | Whether `inset_axes`'s x-axis decreases instead of increasing. |
| `y_inverted` | bool | Whether `inset_axes`'s y-axis decreases instead of increasing. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `` | - | Patch properties (e.g. `ec`, `fc`) for the rectangle and connector lines. |


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


#### `plot_indices`

```python
plot_indices(self, plot_n: int | tuple[int, int] | str | None=None, row: int | None=None, col: int | None=None) -> list[int]
```

Resolves 'plot_n', 'row', or 'col' into the list of subplot indices they refer to.

Exactly one of 'plot_n', 'row', 'col' must be given. `axes` is flattened
row-major, so a row is a contiguous range of indices while a column is a
stride of `n_cols`.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |
| `row` | int, optional | A 0-based row index in the `rows_cols` grid; resolves to every subplot in that row. |
| `col` | int, optional | A 0-based column index in the `rows_cols` grid; resolves to every subplot in that column. |

**Returns:**

| Type | Description |
| --- | --- |
| list\[int\] | The resolved, ordered subplot indices. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If zero, or more than one, of 'plot_n', 'row', 'col' is given. |
| ValueError | If 'row' or 'col' is out of range for `rows_cols`. |
| ValueError | If 'plot_n' is not a valid value. |


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
draw_line(self, orientation: str, point: float=0.0, plot_n: int | tuple[int, int] | str=0, **kwargs) -> None
```

Draws horizontal and vertical lines on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `orientation` | str | The orientation of the line. Use 'v' for vertical or 'h' for horizontal. |
| `point` | float, optional | The coordinate of the line. Defaults to 0. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to draw on. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |

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
| ValueError | If 'plot_n' is not a valid value. |


#### `add_text`

```python
add_text(self, text: str, position: tuple[float, float], plot_n: int | tuple[int, int] | str=0, point: tuple[float, float] | None=None, **kwargs) -> None
```

Adds a text label to the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `text` | str | The text to display. |
| `position` | tuple\[float, float\] | The position of the text in data coordinates. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to draw on. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |
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

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


#### `turn_scientific`

```python
turn_scientific(self, axis: str, plot_n: int | tuple[int, int] | str=0, limits: tuple[int, int] | int=(0, 0)) -> None
```

Sets the ticks of an axis to scientific notation.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to modify: 'x', 'y', or 'both'. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to consider. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |
| `limits` | tuple\[int, int\] or int, optional | Controls the scientific notation.<br>- `(m, n)`: Scientific notation is used for numbers outside 10^m to 10^n.<br>- `0`: Scientific notation is used for all numbers.<br>- `m`: Fixes the order of magnitude to 10^m. If only one int is passed, m=n is assumed. Defaults to (0, 0). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x', 'y', or 'both'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `set_ticks`

```python
set_ticks(self, axis: str, positions: tuple[float, ...], labels: tuple[str, ...] | None=None, plot_n: int | tuple[int, int] | str=0) -> None
```

Modifies the ticks of an axis.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to modify: 'x' or 'y'. |
| `positions` | tuple\[float, ...\] | A tuple with the positions of the ticks. |
| `labels` | tuple\[str, ...\], optional | A tuple with the labels for the ticks. If None, the labels will be the same as the positions. Defaults to None. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to consider. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x' or 'y'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `remove_ticks`

```python
remove_ticks(self, axis: str, plot_n: int | tuple[int, int] | str=0) -> None
```

Removes the ticks (and their labels) from an axis.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to clear: 'x', 'y', or 'both'. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to consider. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x', 'y', or 'both'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `add_scalebar`

```python
add_scalebar(self, size: float, label: str, plot_n: int | tuple[int, int] | str=0, **kwargs) -> None
```

Adds a scalebar (and, thus, removes the axis labels).


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `size` | float | The horizontal size (in coordinates of axis). |
| `label` | str | The label (e.g., "1 cm", "10 μm"). |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to target. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `location` | str, tuple\[float, float\] | Where to put the scalebar. Either a named matplotlib location (e.g. "upper right", the default) or an (x, y) position in axes fraction coordinates (0-1 each, independent of the data range), which centers the scalebar exactly at that point. |
| `color` | str | The color. Defaults to "black". |
| `v_size` | float | The vertical size. Defaults to None, which results in 1% of the height of the axis. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


#### `add_zoom_inset`

```python
_add_zoom_inset(self, xlim: tuple[float, float], ylim: tuple[float, float], plot_i: int, **kwargs) -> ZoomInset
```

Adds a single zoomed-in inset panel for one subplot.

See `add_zoom_inset` for the meaning of the arguments and keyword arguments.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `xlim` | tuple\[float, float\] | The x-axis limits of the region to zoom into. |
| `ylim` | tuple\[float, float\] | The y-axis limits of the region to zoom into. |
| `plot_i` | int | The index of the subplot to zoom into. |

**Returns:**

| Type | Description |
| --- | --- |
| - | The panel to draw the zoomed-in content into. |


#### `add_zoom_inset`

```python
add_zoom_inset(self, xlim: tuple[float, float], ylim: tuple[float, float], plot_n: int | tuple[int, int] | str=0, **kwargs) -> ZoomInset | list[ZoomInset]
```

Adds a zoomed-in inset panel showing a region of one or more subplots.

Each source subplot gets a rectangle around the requested region, connected
to its own inset panel by two lines. Each panel starts empty: draw into it
via `some_drawable.draw(panel)`, exactly like a real `Canvas` subplot.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `xlim` | tuple\[float, float\] | The x-axis limits of the region to zoom into, in either order — each panel matches whichever direction (increasing or decreasing) its own source subplot's x-axis already has (e.g. an image drawn with the default `origin="upper"` has a decreasing y-axis). |
| `ylim` | tuple\[float, float\] | The y-axis limits of the region to zoom into, same ordering behavior as `xlim`. |
| `plot_n` | int, tuple\[int, int\], str, optional | The index or indices of the subplots to zoom into. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `location` | str | Where to place the inset panel. Defaults to "upper right". |
| `width` | str or float | The width of the inset panel, as a percentage of the subplot (e.g. "30%") or an absolute size in inches. Defaults to "30%". |
| `height` | str or float | The height of the inset panel, same format as `width`. Defaults to "30%". |
| `loc1` | int | The corner of the region rectangle connected to the inset panel by the first line (Matplotlib corner codes, 1-4: upper right, upper left, lower left, lower right). Always refers to the visual corner, regardless of whether the source subplot's axes are inverted. Defaults to 2. |
| `loc2` | int | The corner connected by the second line. Defaults to 4. |
| `edgecolor` | str | The color of the region rectangle and connector lines. Defaults to "0.5". |
| `ticks` | bool | If True, keeps the tick marks and labels on the inset panel. Defaults to False, for a clean panel showing only the zoomed-in content. |

**Returns:**

| Type | Description |
| --- | --- |
| ZoomInset \| list\[ZoomInset\] | The panel to draw the zoomed-in content into, when `plot_n` is a single int; otherwise, one panel per targeted subplot, in subplot order. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


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
