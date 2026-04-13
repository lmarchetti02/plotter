from importlib import resources
from json import dumps, load
from logging.config import dictConfig
from pathlib import Path

from matplotlib.style import use

from .text import PlotText


def setup_workspace(base_path: Path | str | None = None) -> None:
    """
    Sets up the directories needed by the library.

    Args:
        base_path (pathlib.Path or str, optional): The directory into which to
            create the necessary directories. It defaults to CWD.
            NOTE: It's better to leave the default value, as changing it would
            likely results in import errors later on.
    """
    # get plotter/ directory
    if base_path is None:
        base_path = Path.cwd()
    elif not isinstance(base_path, Path):
        base_path = Path(base_path or ".")

    parent_dir = base_path / "plotter"
    parent_dir.mkdir(parents=True, exist_ok=True)

    # create necessary directories
    dirs = ("img", "log", "text", "utils", "utils/info")
    for dir in dirs:
        destination = parent_dir / dir
        destination.mkdir(exist_ok=True)

    # define in and out directories
    data_dir = resources.files("plotter") / "data"
    info_dir = data_dir / "info"
    destination = parent_dir / "utils"
    destination_info = parent_dir / "utils/info"
    text_destination = parent_dir / "text/text_example.json"
    log_destination = parent_dir / "log/plotter.log"

    # retrieve package data
    data_files = (f for f in data_dir.iterdir() if f.name != ".DS_Store" and f.is_file())
    info_files = (f for f in info_dir.iterdir() if f.name != ".DS_Store" and f.is_file())

    # copy files to plotter/utils/
    for f in data_files:
        f_destination = destination / f.name
        f_destination.write_bytes(f.read_bytes())

    # copy files to plotter/utils/info/
    for f in info_files:
        f_destination = destination_info / f.name
        f_destination.write_bytes(f.read_bytes())

    # generate text_example.json from the drawable registry
    text_destination.write_text(dumps(PlotText.get_empty_json(), indent=2))

    # create log file
    log_destination.touch(exist_ok=True)

    # logging
    _setup_logging(parent_dir)

    # matplotlib style
    use(parent_dir / "utils/style.mplstyle")


def _setup_logging(plotter_dir: Path) -> None:
    """
    Sets up the logging configuration for the library.

    This function reads a logging configuration from a JSON file and applies it
    to set up the loggers used throughout the module.

    Args:
        plotter_dir (pathlib.Path): The path to the 'plotter' directory.
    """
    # load JSON file
    config_file = plotter_dir / "utils/log_config.json"
    with open(config_file) as f_in:
        config = load(f_in)

    # make log file path absolute to avoid logging not finding it
    log_file = config["handlers"]["file"]["filename"]
    config["handlers"]["file"]["filename"] = plotter_dir / log_file

    # configuration
    dictConfig(config)
