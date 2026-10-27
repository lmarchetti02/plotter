from importlib import resources
from importlib.resources.abc import Traversable
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
    base_path = Path.cwd() if base_path is None else Path(base_path)

    parent_dir = base_path / "plotter"
    if not parent_dir.exists():
        print("Creating 'plotter' directory...")

    # create necessary directories -- mkdir(exist_ok=True) is a no-op if a directory
    # is already there, so a partially set up 'plotter/' (e.g. from an interrupted
    # previous run) self-heals instead of leaving something like utils/log_config.json
    # permanently missing and crashing _setup_logging() below
    dirs = ("img", "log", "text", "utils", "utils/info")
    for dir in dirs:
        (parent_dir / dir).mkdir(parents=True, exist_ok=True)

    # define in and out directories
    data_dir = resources.files("plotter") / "data"
    text_destination = parent_dir / "text/text_example.json"
    log_destination = parent_dir / "log/plotter.log"

    # copy package data to plotter/utils/ and plotter/utils/info/
    _copy_missing(data_dir, parent_dir / "utils")
    _copy_missing(data_dir / "info", parent_dir / "utils/info")

    # generate text_example.json from the drawable registry, unless already present
    if not text_destination.exists():
        text_destination.write_text(dumps(PlotText.get_empty_json(), indent=2))

    # create log file
    log_destination.touch(exist_ok=True)

    # logging
    _setup_logging(parent_dir)

    # matplotlib style
    use(parent_dir / "utils/style.mplstyle")


def _copy_missing(source_dir: Traversable, destination_dir: Path) -> None:
    """
    Copies every file of `source_dir` (but `.DS_Store`) into `destination_dir`, skipping
    files already there, so a user's customized copies are never overwritten.

    Args:
        source_dir (Traversable): The bundled package directory to copy from.
        destination_dir (pathlib.Path): The workspace directory to copy into.
    """
    for f in source_dir.iterdir():
        if f.name == ".DS_Store" or not f.is_file():
            continue
        f_destination = destination_dir / f.name
        if not f_destination.exists():
            f_destination.write_bytes(f.read_bytes())


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
