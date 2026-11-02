# `plotter.helpers.initialization`

## function `setup_workspace`

```python
setup_workspace(base_path: Path | str | None=None) -> None
```

Sets up the directories needed by the library.

Also configures plotter's own logger (`plotter`, and every `plotter.*` module logger)
from `plotter/utils/log_config.json`: DEBUG and above go to `plotter/log/plotter.log`,
ERROR and above to stderr. The root logger, and so the calling application's own
logging, is left untouched. Bundled files are only copied into the workspace when
missing, so a workspace created by an older plotter version keeps its old
`log_config.json` (which also reconfigured the root logger, silencing the
application's own logging below CRITICAL) until that file is deleted.


**Args:**

| Name | Type | Description |
| --- | --- | --- |
| `base_path` | pathlib.Path or str, optional | The directory into which to create the necessary directories. It defaults to CWD. |
| `NOTE` | - | It's better to leave the default value, as changing it would likely results in import errors later on. |
