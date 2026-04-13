from json import JSONDecodeError, dumps, load
from logging import getLogger
from pathlib import Path
from typing import Iterator, Self

from ..drawable import Drawable

logger = getLogger(__name__)


class PlotText:
    """
    Container class to store the information on the
    text that has to be displayed in a subplot of a `Canvas`.

    Attributes:
        title (str): The title of the plot.
        x_label (str): The label of the x-axis.
        y_label (str): The label of the y-axis.
    """

    def __init__(self, title: str, x_label: str, y_label: str, **kwargs) -> None:
        unexpected_keys = set(kwargs) - set(Drawable.get_label_names())
        if unexpected_keys:
            unexpected_key = sorted(unexpected_keys)[0]
            raise TypeError(f"Unexpected keyword argument: '{unexpected_key}'")

        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self._labels = {name: list(kwargs.get(name, [""])) for name in Drawable.get_label_names()}

    def __getattr__(self, name: str) -> list[str]:
        """Returns the labels associated with a drawable family."""
        try:
            return self._labels[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __eq__(self, other: object) -> bool:
        """Compares two `PlotText` objects."""
        if not isinstance(other, PlotText):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def to_dict(self) -> dict[str, str | list[str]]:
        """Converts the object to a JSON-serializable dictionary."""
        return {
            "title": self.title,
            "x_label": self.x_label,
            "y_label": self.y_label,
            **self._labels,
        }

    @classmethod
    def get_empy_text(cls) -> Self:
        """
        Creates an empty object to use as blueprint to dump
        into a JSON file.

        Returns:
            PlotText: The empty object.
        """

        return cls(title="", x_label="", y_label="")

    @classmethod
    def get_empty_json(cls, n_plots: int = 1) -> list[dict[str, str | list[str]]]:
        """Builds the default JSON payload for one or more empty subplots."""
        return [cls.get_empy_text().to_dict() for _ in range(n_plots)]


class Text:
    """
    Class for storing and accessing the text to be displayed on the canvas.

    Attributes:
        n_plots (int): The number of subplots in the canvas.
        subplots_text (list[PlotText]): A list of `PlotText` objects that
            store the information on the text to display on each subplot of
            the canvas to which `Text` belongs.

    Raises:
        ValueError: If the number of subplots in the JSON file does not match
            the number of subplot in the `Canvas` object.
    """

    def __init__(self, n_plots: int) -> None:
        self.n_plots = n_plots
        self.subplots_text: list[PlotText] = []

    def __eq__(self, other: object) -> bool:
        """Compares two `Text` objects."""
        if not isinstance(other, Text):
            return NotImplemented
        return self.n_plots == other.n_plots and self.subplots_text == other.subplots_text

    def __getitem__(self, plot_n: int) -> PlotText:
        """Returns the text of the selected subplot."""
        return self.subplots_text[plot_n]

    def __iter__(self) -> Iterator[PlotText]:
        """Allows to iterate over the `PlotText` objects."""
        return iter(self.subplots_text)

    def read_json(self, text_file: str) -> None:
        """
        Parses data from the JSON file and stores it in the class attributes.

        Args:
            text_file (str): The name of the JSON file where the information about
                the text to display on the calnvas is stored.
                Note: The extension .json can be omitted.
        """
        logger.info("Called 'Text.read_json'")

        # add json extension if necessary
        if text_file[-5:] != ".json":
            text_file += ".json"
            logger.debug("Appended json extension to text file.")

        # get file path
        file_path = (Path.cwd() / "plotter/text").joinpath(text_file)

        try:
            # load json file
            with open(file_path, "r") as json_file:
                self.subplots_text = [PlotText(**data) for data in load(json_file)]

                if len(self.subplots_text) != self.n_plots:
                    raise ValueError("Incorrect number of plots contained in the JSON file.")

        except FileNotFoundError as _:
            logger.warning(f"JSON file not found. Creating {file_path}.")

            self.subplots_text = [PlotText.get_empy_text() for _ in range(self.n_plots)]
            file_path.write_text(dumps([text.to_dict() for text in self.subplots_text]))

        except (JSONDecodeError, TypeError) as _:
            logger.warning(f"Could not parse JSON file {file_path}. Canvas will not display any text.")
            self.subplots_text = [PlotText.get_empy_text() for _ in range(self.n_plots)]
