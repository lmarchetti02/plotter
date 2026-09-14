# `plotter.helpers.text`

## class `PlotText`

Container class to store the information on the
text that has to be displayed in a subplot of a `Canvas`.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `title` | str | The title of the plot. |
| `x_label` | str | The label of the x-axis. |
| `y_label` | str | The label of the y-axis. |


### Methods

#### `to_dict`

```python
to_dict(self) -> dict[str, str | list[str]]
```

Converts the object to a JSON-serializable dictionary.


#### `get_empy_text`

```python
get_empy_text(cls) -> Self
```

Creates an empty object to use as blueprint to dump
into a JSON file.


**Returns:**

| Type | Description |
| --- | --- |
| - | The empty object. |


#### `get_empty_json`

```python
get_empty_json(cls, n_plots: int=1) -> list[dict[str, str | list[str]]]
```

Builds the default JSON payload for one or more empty subplots.


## class `Text`

Class for storing and accessing the text to be displayed on the canvas.


**Attributes:**

| Name | Type | Description |
| --- | --- | --- |
| `n_plots` | int | The number of subplots in the canvas. |
| `subplots_text` | list\[PlotText\] | A list of `PlotText` objects that store the information on the text to display on each subplot of the canvas to which `Text` belongs. |

**Raises:**

| Type | Description |
| --- | --- |
| ValueError | If the number of subplots in the JSON file does not match the number of subplot in the `Canvas` object. |


### Methods

#### `read_json`

```python
read_json(self, text_file: str) -> None
```

Parses data from the JSON file and stores it in the class attributes.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `text_file` | str | The name of the JSON file where the information about the text to display on the calnvas is stored. |
| `Note` | - | The extension .json can be omitted. |
