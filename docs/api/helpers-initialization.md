# `plotter.helpers.initialization`

## function `setup_workspace`

```python
setup_workspace(base_path: Path | str | None=None) -> None
```

Sets up the directories needed by the library.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `base_path` | pathlib.Path or str, optional | The directory into which to create the necessary directories. It defaults to CWD. |
| `NOTE` | - | It's better to leave the default value, as changing it would likely results in import errors later on. |


## function `_setup_logging`

```python
_setup_logging(plotter_dir: Path) -> None
```

Sets up the logging configuration for the library.

This function reads a logging configuration from a JSON file and applies it
to set up the loggers used throughout the module.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `plotter_dir` | pathlib.Path | The path to the 'plotter' directory. |
