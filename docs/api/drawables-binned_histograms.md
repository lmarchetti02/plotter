# `plotter.drawables.binned_histograms`

## class `BinnedHist(Drawable)`

Class for creating a 1D histogram from already pre-computed bin values.

Unlike `RawHist`, `bin_vals` and `bins` are the values to display directly, drawn as-is via
`matplotlib.axes.Axes.stairs` -- no binning of raw samples takes place.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `bin_vals` | NArray1D\[Any\] | The array with the value of each bin. It has shape (N_bins,). |
| `bins` | NArray1D\[Any\] | The array with the edges of each bin (flattened). It has shape (N_bins+1,). |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `len(bin_vals)` doesn't equal `len(bins) - 1`. |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `bin_vals: NArray1D[Any]`
- `bins: NArray1D[Any]`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the histogram on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the histogram on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `label` | str, optional | The label for the histogram in the legend. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `color` | str | The Matplotlib color of the histogram. Defaults to "royalblue". |
| `alpha` | float | The transparency of the histogram. Defaults to 0.8. |
| `filled` | bool | If `True`, the histogram is filled. Defaults to `True`. |
| `edgecolor` | str | The color of the histogram edges. Defaults to `"cornflowerblue"`. |
| `lw` | float | The width of the histogram edges. Defaults to 0 if filled is `True`, else to 1.5. |


## class `BinnedHist2D(Drawable)`

Class for creating a 2D histogram from already pre-computed bin values.

Unlike `RawHist2D`, `bin_vals`, `xbins`, and `ybins` are the values to display directly,
drawn as-is via `matplotlib.axes.Axes.pcolormesh` (the same call `Axes.hist2d` delegates to
internally) -- no binning of raw samples takes place.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `bin_vals` | NArray2D\[Any\] | The array with the value of each cell. It has shape (N_bins_X, N_bins_Y), matching `numpy.histogram2d`'s own convention. |
| `xbins` | NArray1D\[Any\] | The array with the edges of each x-bin (flattened). It has shape (N_bins_X+1,). |
| `ybins` | NArray1D\[Any\] | The array with the edges of each y-bin (flattened). It has shape (N_bins_Y+1,). |
| `mappable` | QuadMesh or None | The mesh artist returned by `pcolormesh`, populated after `draw` runs. Pass it (via this `BinnedHist2D`) as a `Colorbar`'s `source`. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `bin_vals.shape` doesn't equal `(len(xbins) - 1, len(ybins) - 1)`. |


**Defined attributes:**

- `bin_vals: NArray2D[Any]`
- `xbins: NArray1D[Any]`
- `ybins: NArray1D[Any]`
- `mappable: QuadMesh | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, **kwargs) -> None
```

Draws the 2D histogram on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the histogram on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `colormap` | str | The Matplotlib colormap to use for the histogram. Defaults to "plasma". |
| `alpha` | float | The transparency of the histogram. Defaults to 1. |
| `log` | tuple\[bool, float\] | A tuple controlling the scale. The first element is a boolean to indicate if the scale should be logarithmic. The second element is a float for the range of linearity in case of a 'symlog' scale. Defaults to `(False, 0)`. |
