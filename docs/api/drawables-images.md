# `plotter.drawables.images`

## class `Image(Drawable)`

Class for creating an image to be drawn on a canvas.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `data` | NArray2D\[Any\] \| NArray3D\[Any\] | The 2D or 3D numpy array containing the image data. If 3D, the third dimension must contain 3 (RGB) or 4 (RGBA) values. |
| `mappable` | AxesImage or None | The image artist returned by `imshow`, populated after `draw` runs. Pass it (via this `Image`) as a `Colorbar`'s `source`. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the data is not a 2D or 3D array. |
| ValueError | If the third dimension of a 3D array is not 3 or 4. |
| ValueError | If the data is not real. |


**Defined attributes:**

- `data: NArray2D[Any] | NArray3D[Any]`
- `mappable: AxesImage | None`

### Methods

#### `draw`

```python
draw(self, canvas: Canvas | ZoomInset, plot_n: int=0, **kwargs) -> None
```

Draws the image on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw the image on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |

**Keyword Arguments:**

| Name | Type | Description |
| --- | --- | --- |
| `colormap` | str | The Matplotlib colormap to use. Defaults to "gray". |
| `log` | bool or tuple\[bool, float\] | Controls the scale of the colormap.<br>- `bool`: `True` for logarithmic scale.<br>- `tuple`: `(True, float)` for a 'symlog' scale with a linear range of `float`. This parameter is ignored if the data is RGB(A). Defaults to `False`. |
| `v_range` | tuple\[float, float\] | The minimum and maximum intensity values. Ignored if the data is RGB(A). Defaults to `(None, None)`. |
| `aspect` | str | The aspect ratio of the axes. `equal` for squared pixels, `auto` for a squared image. Defaults to "equal". |
| `origin` | str | The placement of the \[0,0\] element of the data. `upper` for the top-left, `lower` for the bottom-left. Defaults to "upper". |
| `limits` | list\[float\] | The limits of the x and y axes in the format `\[left, right, bottom, top\]`. Defaults to `None`. When drawing into a `ZoomInset` with `limits` left as `None`, `data` is instead expected to be the same full-resolution array shown on the source subplot: it gets automatically cropped and placed to match the panel's requested region. |
