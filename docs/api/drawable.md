# `plotter.drawable`

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


#### `get_label`

```python
_get_label(canvas: 'Canvas | ZoomInset', plot_n: int, label: str | None, name: str, logger: Logger, msg: str) -> tuple[int, str | None]
```

Retrieves the label associated with the drawable.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `canvas` | Canvas \| ZoomInset | The canvas (or zoom-inset panel) the drawable is attached to. |
| `plot_n` | int | The index of the subplot. |
| `label` | str \| None | An explicit user-provided label. |
| `name` | str | The name of the drawable. |
| `logger` | Logger | The logger to use for warnings. |
| `msg` | str | The warning to emit when no label can be found. |

**Returns:**

| Type | Description |
| --- | --- |
| tuple\[int, str \| None\] | The current drawable index and the resolved label. |


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
