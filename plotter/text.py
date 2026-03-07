from dataclasses import asdict, dataclass, field
from json import JSONDecodeError, dumps, load
from logging import getLogger
from pathlib import Path
from typing import Iterator, Self

logger = getLogger(__name__)


@dataclass(frozen=True)
class PlotText:
    """
    Container class to store the al the information on the
    text that has to be displayed in a subplot of a `Canvas`.

    Attributes:
        title (str): The title of the plot.
        x_label (str): The label of the x-axis.
        y_label (str): The label of the y-axis.
        scatter_plots (list[str]): The labels of the scatter plots.
        line_plots (list[str]): The labels of the line plots.
        histograms (list[str]): The labels of the histograms.
        images (list[str]): The label of the images.
    """

    title: str
    x_label: str
    y_label: str
    scatter_plots: list[str]
    line_plots: list[str]
    histograms: list[str]
    images: list[str]

    @classmethod
    def get_empy_text(cls) -> Self:
        """
        Creates an empty object to use as blueprint to dump
        into a JSON file.

        Returns:
            PlotText: The empty object.
        """

        empty_obj = cls(
            title="",
            x_label="",
            y_label="",
            scatter_plots=[""],
            line_plots=[""],
            histograms=[""],
            images=[""],
        )

        return empty_obj


@dataclass
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

    n_plots: int
    subplots_text: list[PlotText] = field(init=False, default_factory=list)

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
            file_path.write_text(dumps([asdict(text) for text in self.subplots_text]))

        except (JSONDecodeError, TypeError) as _:
            logger.warning(f"Could not parse JSON file {file_path}. Canvas will not display any text.")
            self.subplots_text = [PlotText.get_empy_text() for _ in range(self.n_plots)]
