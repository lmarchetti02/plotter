# `plotter.drawables.drawable`

## class `Drawable(ABC)`

Abstract base class for objects that can be drawn on a canvas.


**Defined attributes:**

- `label_name: ClassVar[str]`

### Methods

#### `get_label_names`

```python
get_label_names() -> tuple[str, ...]
```

Returns the names of all supported drawable label groups.


#### `draw`

```python
draw(self, canvas: 'Canvas | ZoomInset', plot_n: int=0, **kwargs) -> None
```

Draws the object on the canvas.

Not every concrete drawable accepts the same keyword arguments -- see each
subclass's own docstring. In particular, drawables that participate in label
bookkeeping (see `Drawable.get_label_names`) additionally accept a `label`
keyword argument; `Image`, `RawHist2D`, and `BinnedHist2D` do not.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
