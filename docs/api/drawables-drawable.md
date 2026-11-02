# `plotter.drawables.drawable`

## class `Drawable(ABC)`

Abstract base class for objects that can be drawn on a canvas.


**Defined attributes:**

- `label_name: ClassVar[str]`
- `draw_kwargs: ClassVar[frozenset[str]]`

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
keyword argument; `Image`, `RawHist2D`, and `BinnedHist2D` do not. Each subclass
lists the keyword arguments it accepts in `draw_kwargs`, and its `draw()` raises
on any other one instead of silently ignoring it.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If `plot_n` is not an index of `canvas.axes`. |
| TypeError | If a keyword argument not listed in `draw_kwargs` is given. |
