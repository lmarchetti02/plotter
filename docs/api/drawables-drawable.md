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
draw(self, canvas: 'Canvas | ZoomInset', plot_n: int=0, label: str | None=None, **kwargs) -> None
```

Draws the object on the canvas.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) to draw on. |
| `plot_n` | int, optional | The index of the subplot to draw on. Defaults to 0. |
| `label` | str, optional | The label associated with the drawn object. Defaults to `None`. |
