# `plotter.histograms`

## class `Hist(Drawable)`

Class for creating a 1D histogram.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `data` | NArray1D\[Any\] | The array containing the data to plot. |
| `nbins` | int or NArray1D\[Any\] or "auto", optional | The number of bins of the histogram or the array containing the edges of the bins. Defaults to "auto". When `nbins` is an array of bin edges, `Hist.draw()` uses `matplotlib.axes.Axes.stairs` instead of `matplotlib.axes.Axes.hist`. |
| `density` | bool, optional | If `True`, the histogram is normalized such that the integral over the range is 1. Defaults to `False`. |
| `cumulative` | bool, optional | If `True`, the cumulative histogram is plotted. Defaults to `False`. |
| `bin_vals` | NArray1D\[F64\] or None | The array with the values corresponding to each bin. It has shape (N_bins,). |
| `bins` | NArray1D\[F64\] or None | The array with the edges of each bin (flattened). It has shape (N_bins+1,). |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `data: NArray1D[Any]`
- `nbins: int | NArray1D[Any] | str`
- `density: bool`
- `cumulative: bool`
- `bin_vals: NArray1D[F64] | None`
- `bins: NArray1D[F64] | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the histogram on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas | The canvas object to draw the histogram on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `label` | str, optional | The label for the histogram in the legend. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `bin_ranges` | tuple\[float,float\] | The tuple with the left and right limits of the bins. Defaults to `None`, which means (data.min(), data.max()). |
| `color` | str | The Matplotlib color of the histogram. Defaults to "royalblue". |
| `alpha` | float | The transparency of the histogram. Defaults to 0.8. |
| `filled` | bool | If `True`, the histogram is filled. Defaults to `True`. |
| `ecolor` | str | The color of the histogram edges. Defaults to `"cornflowerblue"`. |
| `lw` | float | The width of the histogram edges. Defaults to 0 if filled is `True`, else to 1.5. |


## class `Hist2D(Drawable)`

Class for creating a 2D histogram.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `x` | NArray1D\[Any\] | The array containing the x values to plot. |
| `y` | NArray1D\[Any\] | The array containing the y values to plot. |
| `nbins` | int \| tuple \| list \| NArray2D | The number of bins for the histogram. It can be:<br>- an `int` for the same number of bins for both axes.<br>- a `tuple` or `list` of two ints for the number of bins for x and y respectively.<br>- a 2D array for the edges of the bins. |
| `density` | bool, optional | If `True`, the histogram is normalized such that the integral over the range is 1. Defaults to `False`. |
| `bin_vals` | NArray2D\[F64\] or None | The array with the values corresponding to each bin. It has shape (N_bins,). |
| `xbins` | NArray1D\[F64\] or None | The array with the edges of each x-bin (flattened). It has shape (N_bins_X+1,). |
| `ybins` | NArray1D\[F64\] or None | The array with the edges of each y-bin (flattened). It has shape (N_bins_Y+1,). |


**Defined attributes:**

- `label_name: ClassVar[str]`
- `x: NArray1D[Any]`
- `y: NArray1D[Any]`
- `nbins: int | tuple[int, int] | list[int] | NArray2D[Any]`
- `density: bool`
- `bin_vals: NArray2D[F64] | None`
- `xbins: NArray1D[F64] | None`
- `ybins: NArray1D[F64] | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas, plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the 2D histogram on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas | The canvas object to draw the histogram on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `label` | str, optional | The label for the colorbar. Defaults to `None`. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `bin_ranges` | tuple\[tuple\[float,float\],tuple\[float,float\]\] | The tuple with the left and right limits of the bins (in x and y). Defaults to `None`, which means ((x.min(),x.max()),(y.min(),y.max()). |
| `colormap` | str | The Matplotlib colormap to use for the histogram. Defaults to "plasma". |
| `alpha` | float | The transparency of the histogram. Defaults to 1. |
| `log` | tuple\[bool, float\] | A tuple controlling the scale. The first element is a boolean to indicate if the scale should be logarithmic. The second element is a float for the range of linearity in case of a 'symlog' scale. Defaults to `(False, 0)`. |
