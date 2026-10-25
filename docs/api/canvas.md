# `plotter.canvas`

## class `ZoomInset`

A single zoomed-in inset panel returned by `Canvas.add_zoom_inset`.

Exposes the same `axes`/`counters`/`text`/`figure` surface as `Canvas`, so any
`Drawable` can be drawn into it exactly like a real `Canvas` subplot (e.g.
`some_drawable.draw(inset)`). Also exposes `setup` to configure its `Axes` and
`draw_line` to add reference lines to it. Other cosmetic `Canvas` helpers
(`draw_band`, `add_text`, ...) are not available on it — use `inset.axes\[0\]`
directly for those.


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
| `nogrid` | bool or tuple\[bool, bool\] | Controls grid removal.<br>- `bool`: Removes the grid from both axes.<br>- `tuple`: `(x, y)` to independently remove the grid from the x and/or y axis (e.g., `(True, False)` removes only the x grid). Defaults to `False`. |
| `inverted` | tuple\[bool, bool\] | A tuple to invert the x and y axes respectively (e.g., `(True, False)`). |


#### `draw_line`

```python
draw_line(self, orientation: str, point: float=0.0, **kwargs) -> None
```

Draws a horizontal or vertical reference line on the panel.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `orientation` | str | The orientation of the line. Use 'v' for vertical or 'h' for horizontal. |
| `point` | float, optional | The coordinate of the line. Defaults to 0. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The color of the line. Defaults to 'black'. |
| `linestyle` | str | The style of the line (e.g., '-', '--', '-.', ':'). Defaults to '-'. |
| `lw` | float | The width of the line. Defaults to 0.5. |
| `alpha` | float | The opacity of the line. Defaults to 1.0. |
| `label` | str | The label for the line in the legend. Defaults to None. |
| `zorder` | float | The drawing order of the line. Defaults to 2. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the orientation is not 'v' or 'h'. |


## class `Canvas`

Class for creating an empty canvas (xy-plane).


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `text_file` | str, optional | The name of the JSON file containing the text to be added to the plot. Defaults to None, in which case no JSON file is read or created and every subplot starts with blank text -- use `set_title` to give the subplots a title. |
| `rows_cols` | tuple\[int, int\], optional | A tuple with the number of rows and columns of a regular grid of subplots, numbered row-major. Mutually exclusive with `layout`. Defaults to None, which means (1, 1) unless `layout` is given, in which case it is set to the shape of `layout`. |
| `figsize` | tuple\[float, float\], optional | A tuple containing the dimensions of the canvas (width, height). Defaults to (12, 8). |
| `dpi` | int, optional | The number of dots per inch (DPI) of the image. Defaults to 150. |
| `save` | str, optional | The name of the file to save the plot to. The plots are stored in 'plotter/img/'. Defaults to an empty string. |
| `suptitle` | str, optional | The title of the figure as a whole, displayed above the subplots' own titles. Defaults to an empty string, which adds no title. |
| `layout` | Layout, optional | A non-grid arrangement of subplots, as a mosaic of `plot_n` indices (one per cell, row-major): repeating an index makes that subplot span every cell it appears in, and `None` leaves a cell empty. E.g. `\[\[0, 2\], \[1, 2\]\]` stacks subplots 0 and 1 on the left, with subplot 2 spanning the full height on the right. The text file needs one entry per distinct subplot. Mutually exclusive with `rows_cols`. Defaults to None. |
| `width_ratios` | tuple\[float, ...\], optional | The relative widths of the columns, one per column. Defaults to None (equal widths). |
| `height_ratios` | tuple\[float, ...\], optional | The relative heights of the rows, one per row. Defaults to None (equal heights). |
| `sharex` | bool \| str, optional | Which subplots share their x-axis (limits, scale, and ticks): False for none, True for all of them, "row"/"col" for those whose span starts in the same row/column. The x tick labels of a sharing subplot with another one of its group below it are hidden. Defaults to False. |
| `sharey` | bool \| str, optional | Same as `sharex`, for the y-axis; the y tick labels are hidden when another subplot of the group is to the left. Defaults to False. |
| `figure` | Figure | The matplotlib Figure object. |
| `axes` | list\[Axes\] | A list with the matplotlib Axes object corresponding to each subplot. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If both `rows_cols` and `layout` are given. |
| ValueError | If the number of columns and/or the number of rows is not positive. |
| ValueError | If `layout` is empty, ragged, contains no subplot, or its subplot indices are not numbered consecutively from 0. |
| ValueError | If a subplot in `layout` does not span a rectangle of cells. |
| ValueError | If `width_ratios`/`height_ratios` don't have one entry per column/row. |


**Defined attributes:**

- `text_file: str | None`
- `rows_cols: tuple[int, int] | None`
- `figsize: tuple[float, float]`
- `dpi: int`
- `save: str`
- `show: bool`
- `suptitle: str`
- `layout: Layout | None`
- `width_ratios: tuple[float, ...] | None`
- `height_ratios: tuple[float, ...] | None`
- `sharex: Share`
- `sharey: Share`
- `figure: Figure`
- `axes: list[Axes]`
- `text: Text`
- `counters: _Counters`
- `_n_plots: int`
- `_loc_legend: list[int]`
- `_ncols_legend: list[int]`
- `_no_legend: list[bool]`
- `_group_titles: dict[tuple[int, int], MplText]`

### Methods

#### `plot_indices`

```python
plot_indices(self, plot_n: PlotN | None=None, row: int | None=None, col: int | None=None) -> list[int]
```

Resolves 'plot_n', 'row', or 'col' into the list of subplot indices they refer to.

Exactly one of 'plot_n', 'row', 'col' must be given. A row/column resolves to
every subplot whose span includes it, so a subplot spanning several rows/columns
of a `layout` belongs to each of them. On a regular `rows_cols` grid (numbered
row-major), a row is a contiguous range of indices while a column is a stride
of `n_cols`.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `plot_n` | PlotN, optional | The index or indices of the subplots. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |
| `row` | int, optional | A 0-based row index in the `rows_cols` grid (or `layout`); resolves to every subplot spanning that row. |
| `col` | int, optional | A 0-based column index in the `rows_cols` grid (or `layout`); resolves to every subplot spanning that column. |

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
| ValueError | If 'plot_n' is a list containing duplicate indices. |


#### `setup`

```python
setup(self, plot_n: PlotN='all', **kwargs) -> None
```

Sets up the properties of the subplots.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `plot_n` | PlotN, optional | The index or indices of the subplots to configure. Defaults to 'all'. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `xlim` | tuple\[float, float\] | The limits for the x-axis. |
| `ylim` | tuple\[float, float\] | The limits for the y-axis. |
| `xscale` | str | The scale for the x-axis ('linear', 'log', 'symlog'). |
| `yscale` | str | The scale for the y-axis ('linear', 'log', 'symlog'). |
| `nogrid` | bool or tuple\[bool, bool\] | Controls grid removal.<br>- `bool`: Removes the grid from both axes.<br>- `tuple`: `(x, y)` to independently remove the grid from the x and/or y axis (e.g., `(True, False)` removes only the x grid). Defaults to `False`. |
| `inverted` | tuple\[bool, bool\] | A tuple to invert the x and y axes respectively (e.g., `(True, False)`). |
| `legend` | int | Force the position of the legend to a specified one. See 'plotter/utils/info/legend.png'. |
| `leg_ncols` | int | The number of columns to arrange the legend entries into. Defaults to 1. |
| `nolegend` | bool | Removes the legend from the subplot(s), even if they have labelled artists. Defaults to `False`. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


#### `set_title`

```python
set_title(self, title: str, plot_n: PlotN=0) -> None
```

Sets the title of one or more subplots.

Overrides the title coming from the JSON text file, if any, and is applied
right away, so it works both before and after `setup`. This is meant for a
canvas that needs no text beyond a title (e.g. one holding only `Image`
objects), which can then be built without a `text_file` at all.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `title` | str | The title to display. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to title. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


#### `set_group_title`

```python
set_group_title(self, title: str, cols: int | tuple[int, int], **kwargs) -> None
```

Sets a title shared by a group of adjacent columns, like a suptitle for part of the canvas.

The title is centered above the subplots lying entirely within those columns, between
the figure's suptitle (if any) and the subplots' own titles. Its final position is
only settled when the canvas is exited, once the layout (e.g. any `Colorbar`) is final.
Calling this again with the same columns replaces that group's title.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `title` | str | The title to display. |
| `cols` | int \| tuple\[int, int\] | The 0-based column of the `rows_cols` grid (or `layout`) to title, or a range of columns from `first` to `last` (inclusive). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `fontsize` | float \| str | The font size of the title. Defaults to the suptitle's, `rcParams\["figure.titlesize"\]`. Any other keyword argument is passed on to `matplotlib.figure.Figure.text` (e.g. `fontweight`, `color`). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'cols' is out of range for `rows_cols`, or its first column comes after its last. |
| ValueError | If 'cols' overlaps the columns of another group title. |
| ValueError | If a subplot in the top row spans columns both inside and outside 'cols'. |
| ValueError | If no subplot lies entirely within 'cols'. |


#### `draw_line`

```python
draw_line(self, orientation: str, point: float=0.0, plot_n: PlotN=0, **kwargs) -> None
```

Draws horizontal and vertical lines on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `orientation` | str | The orientation of the line. Use 'v' for vertical or 'h' for horizontal. |
| `point` | float, optional | The coordinate of the line. Defaults to 0. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to draw on. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The color of the line. Defaults to 'black'. |
| `linestyle` | str | The style of the line (e.g., '-', '--', '-.', ':'). Defaults to '-'. |
| `lw` | float | The width of the line. Defaults to 0.5. |
| `alpha` | float | The opacity of the line. Defaults to 1.0. |
| `label` | str | The label for the line in the legend. Defaults to None. |
| `zorder` | float | The drawing order of the line. Defaults to 2. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the orientation is not 'v' or 'h'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `draw_band`

```python
draw_band(self, orientation: str, low: float, high: float, plot_n: PlotN=0, **kwargs) -> None
```

Draws a shaded horizontal or vertical band on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `orientation` | str | The orientation of the band. Use 'v' for a vertical band (spanning between two x-coordinates) or 'h' for a horizontal band (spanning between two y-coordinates). |
| `low` | float | The lower edge of the band. |
| `high` | float | The upper edge of the band. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to draw on. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The color of the band. Defaults to 'black'. |
| `linestyle` | str | The style of the band's border (e.g., '-', '--', '-.', ':'). Defaults to '-'. |
| `lw` | float | The width of the band's border. Defaults to 0.0 (no visible border). |
| `alpha` | float | The opacity of the band. Defaults to 0.2. |
| `label` | str | The label for the band in the legend. Defaults to None. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the orientation is not 'v' or 'h'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `add_text`

```python
add_text(self, text: str, position: tuple[float, float], plot_n: PlotN=0, point: tuple[float, float] | None=None, **kwargs) -> None
```

Adds a text label to the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `text` | str | The text to display. |
| `position` | tuple\[float, float\] | The position of the text in data coordinates. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to draw on. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |
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


#### `add_point`

```python
add_point(self, position: tuple[float, float], label: str | None=None, plot_n: PlotN=0, **kwargs) -> None
```

Draws a single point on the canvas, with an optional nearby label.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `position` | tuple\[float, float\] | The (x, y) position of the point, in data coordinates. |
| `label` | str, optional | Text to draw next to the point, offset from it by `label_offset`. Defaults to None (no label). |
| `plot_n` | PlotN, optional | The index or indices of the subplots to draw on. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `marker` | str | The marker style. Defaults to 'o'. |
| `color` | str | The marker color. Defaults to 'black'. |
| `markersize` | float | The marker size. Defaults to Matplotlib's default. |
| `alpha` | float | The marker opacity. Defaults to 1.0. |
| `label_offset` | tuple\[float, float\] | The (x, y) offset of the label from the point, in points. Defaults to (10, 10). |
| `label_color` | str | The label text color. Defaults to 'black'. |
| `label_fontsize` | float | The label font size. Defaults to Matplotlib's default. |
| `label_ha` | str | The label's horizontal alignment. Defaults to 'left'. |
| `label_va` | str | The label's vertical alignment. Defaults to 'bottom'. |
| `label_arrow` | bool or dict | If True, draws a default arrow (`{"arrowstyle": "->"}`) from the label to the point; a dict draws one styled with those `Axes.annotate` arrow properties instead. Defaults to False (no arrow). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |


#### `turn_scientific`

```python
turn_scientific(self, axis: str, plot_n: PlotN=0, limits: tuple[int, int] | int=(0, 0)) -> None
```

Sets the ticks of an axis to scientific notation.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to modify: 'x', 'y', or 'both'. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to consider. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |
| `limits` | tuple\[int, int\] or int, optional | Controls the scientific notation.<br>- `(m, n)`: Scientific notation is used for numbers outside 10^m to 10^n.<br>- `0`: Scientific notation is used for all numbers.<br>- `m`: Fixes the order of magnitude to 10^m. If only one int is passed, m=n is assumed. Defaults to (0, 0). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x', 'y', or 'both'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `set_ticks`

```python
set_ticks(self, axis: str, positions: tuple[float, ...], labels: tuple[str, ...] | None=None, plot_n: PlotN=0) -> None
```

Modifies the ticks of an axis.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to modify: 'x' or 'y'. |
| `positions` | tuple\[float, ...\] | A tuple with the positions of the ticks. |
| `labels` | tuple\[str, ...\], optional | A tuple with the labels for the ticks. If None, the labels will be the same as the positions. Defaults to None. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to consider. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x' or 'y'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `remove_ticks`

```python
remove_ticks(self, axis: str, plot_n: PlotN=0) -> None
```

Removes the ticks (and their labels) from an axis.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `axis` | str | The axis to clear: 'x', 'y', or 'both'. |
| `plot_n` | PlotN, optional | The index or indices of the subplots to consider. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the axis is not 'x', 'y', or 'both'. |
| ValueError | If 'plot_n' is not a valid value. |


#### `add_scalebar`

```python
add_scalebar(self, size: float, label: str, plot_n: PlotN=0, **kwargs) -> None
```

Adds a scalebar (and, thus, removes the axis labels).


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `size` | float | The horizontal size (in coordinates of axis). |
| `label` | str | The label (e.g., "1 cm", "10 μm"). |
| `plot_n` | PlotN, optional | The index or indices of the subplots to target. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

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
add_zoom_inset(self, xlim: tuple[float, float], ylim: tuple[float, float], plot_n: PlotN=0, **kwargs) -> ZoomInset | list[ZoomInset]
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
| `plot_n` | PlotN, optional | The index or indices of the subplots to zoom into. Defaults to 0. Options:<br>- int: The index of a single plot (e.g., 0, 1).<br>- str: 'all' to target all plots.<br>- tuple\[int, int\]: A range of plots to target, from `inf` to `sup` (inclusive).<br>- list\[int\]: An explicit, non-consecutive set of plot indices to target (e.g. \[0, 2\]). |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `location` | str | Where to place the inset panel. Defaults to "upper right". |
| `width` | str or float | The width of the inset panel, as a percentage of the subplot (e.g. "30%") or an absolute size in inches. Defaults to "30%". |
| `height` | str or float | The height of the inset panel, same format as `width`. Defaults to "30%". |
| `loc1` | int | The corner of the region rectangle connected to the inset panel by the first line (Matplotlib corner codes, 1-4: upper right, upper left, lower left, lower right). Always refers to the visual corner, regardless of whether the source subplot's axes are inverted. Defaults to 2. |
| `loc2` | int | The corner connected by the second line. Defaults to 4. |
| `edgecolor` | str | The color of the region rectangle, connector lines, and the inset panel's own outline (its Axes spines) — all three always share this one color. Defaults to "black". |
| `linewidth` | float | The line width of the region rectangle, connector lines, and the inset panel's own outline — all three always share this one width. Defaults to 0.5. |
| `ticks` | bool | If True, keeps the tick marks and labels on the inset panel. Defaults to False, for a clean panel showing only the zoomed-in content. |

**Returns:**

| Type | Description |
| --- | --- |
| ZoomInset \| list\[ZoomInset\] | The panel to draw the zoomed-in content into, when `plot_n` is a single int; otherwise, one panel per targeted subplot, in subplot order. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If 'plot_n' is not a valid value. |
