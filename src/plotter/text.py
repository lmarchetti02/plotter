import logging
import pathlib
import json

logger = logging.getLogger(__name__)


class Text:
    """
    Class used for storing and accessing the
    text to be displayed in the canvas.
    """

    def __init__(self, text_file: str) -> None:
        """
        The class constructor.

        It opens the json file where the text to be shown
        is stored and saves it into its data members.
        """
        logger.info("'Text' object created")

        self.title = "p"
        self.abscissa = ""
        self.ordinate = ""
        self.datasets = []
        self.functions = []

        file_path = pathlib.Path("./plotter/text").joinpath(text_file)
        try:
            with open(file_path) as json_file:
                logger.debug(f"Opened '{file_path}'")
                self.data_dict = json.load(json_file)
                self.__get_data()
        except FileNotFoundError as _:
            logger.error(f"Impossible to open '{file_path}'")

    def __get_data(self) -> None:
        self.title = self.data_dict["title"]
        self.abscissa = self.data_dict["abscissa"]
        self.ordinate = self.data_dict["ordinate"]
        self.datasets = self.data_dict["datasets"]
        self.functions = self.data_dict["functions"]
