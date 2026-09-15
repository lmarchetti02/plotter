# `plotter.drawables.boxplot`

## class `BoxPlot(Drawable)`

Class for creating a group of box-and-whisker plots.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `data` | list\[NArray1D\[Any\]\] | One array of raw samples per box. |
| `positions` | NArray1D\[Any\] or None, optional | The x-position of each box. Defaults to `None`, which lets Matplotlib place the boxes at `1, 2, ..., N`. |
| `bxp` | dict\[str, list\[Any\]\] or None | The dictionary of Matplotlib artists (keys: `"boxes"`, `"medians"`, `"whiskers"`, `"caps"`, `"fliers"`, `"means"`) returned by `Axes.boxplot`, populated after `draw()` runs, for further per-artist styling. When `patch_artist` is `True`, also carries a `"box_edges"` key: one extra, edge-only `Patch` per box, layered in front of the median/mean lines (see `draw`'s `zorder` keyword argument). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `data` is empty. |
| ValueError | If `positions` is given and does not have the same length as `data`. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `data: list[NArray1D[Any]]`
- `positions: NArray1D[Any] | None`
- `bxp: dict[str, list[Any]] | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the group of boxes on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the boxes on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `label` | str, optional | The single legend label for the whole group of boxes. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The Matplotlib facecolor of the boxes, when `patch_artist` is `True`. Defaults to "steelblue". |
| `edgecolor` | str | The color of the box edges, whiskers, and caps. Unaffected by `alpha`. Defaults to "navy". |
| `alpha` | float | The opacity of the box fill only -- baked directly into the facecolor, so it never dims the box edges, whiskers, or caps. Defaults to 0.6. |
| `lw` | float | The width of the box edges, whiskers, caps, median line, and mean line. Defaults to 1.0. |
| `zorder` | float | The drawing order of the box edges, whiskers, and caps -- the topmost layer. The median and mean lines draw one step behind this, and the box fill two steps behind, so (from back to front) the fill sits behind the summary lines, which sit behind the box's own border. This keeps the lines fully saturated (nothing translucent drawn over them) while the border still visually "closes over" them at the box edges. Defaults to 2. |
| `patch_artist` | bool | If `True`, boxes are drawn as filled `Patch` artists using `color`/`edgecolor`/`alpha`/`lw`; if `False`, boxes are drawn as unfilled `Line2D` rectangles styled with `edgecolor`/`lw` only (`color`/`alpha` are ignored, since there is no fill). Defaults to `True`. |
| `notch` | bool | If `True`, draws a notch around the median of each box. Defaults to `False`. |
| `whis` | float or tuple\[float, float\] | The whisker reach. See `Axes.boxplot`. Defaults to 1.5. |
| `widths` | float or NArray1D\[Any\] | The width(s) of the boxes. Defaults to Matplotlib's own computed default. |
| `median_color` | str | The color of the median line. Defaults to "firebrick". |
| `showmeans` | bool | If `True`, shows the mean of each box. Defaults to `True`. |
| `meanline` | bool | If `True` (and `showmeans` is `True`), draws the mean as a line spanning the box instead of a marker point. Defaults to `True`. |
| `mean_color` | str | The color of the mean line. Defaults to "orange". |
| `showfliers` | bool | If `True`, shows the outlier points beyond the whiskers. Defaults to `False`. |
| `tick_labels` | list\[str\] | The tick label placed under each box. Defaults to `None` (numeric tick values). |
| `orientation` | str | `"vertical"` or `"horizontal"`. Defaults to `"vertical"`. |
| `medianprops` | dict | Style overrides for the median line, passed straight through to `Axes.boxplot` instead of `median_color`/`zorder`. Defaults to a solid line colored with `median_color`, one `zorder` step behind the box. |
| `meanprops` | dict | Style overrides for the mean line, passed straight through to `Axes.boxplot` instead of `mean_color`/`zorder`. Defaults to a dashed line colored with `mean_color`, one `zorder` step behind the box. |

**Note:**

The first `BoxPlot` drawn on a given subplot additionally labels its median
and mean lines "Median"/"Mean" for the legend -- later groups on the same
subplot skip this, since every group shares the same median/mean styling and
one legend entry is enough. Any other keyword argument accepted by
`Axes.boxplot` (e.g. `bootstrap`, `capwidths`, `flierprops`) is forwarded
straight through.
