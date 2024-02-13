import logging
import pathlib
import json

logger = logging.getLogger(__name__)


class Text:
    """
    Class used for storing and accessing the
    text to be displayed in the canvas.

    Parameters
    ---
    """

    def __init__(self, text_file: str, n_plots: int) -> None:

        logger.info("'Text' object created")

        self.__n_plots = n_plots

        self.title = ["" for _ in range(self.__n_plots)]
        self.abscissa = ["" for _ in range(self.__n_plots)]
        self.ordinate = ["" for _ in range(self.__n_plots)]
        self.datasets = [[] for _ in range(self.__n_plots)]
        self.functions = [[] for _ in range(self.__n_plots)]
        self.histograms = [[] for _ in range(self.__n_plots)]

        file_path = pathlib.Path("./plotter/text").joinpath(text_file)
        try:
            with open(file_path) as json_file:
                logger.debug(f"Opened '{file_path}'")
                self.__data_dict = json.load(json_file)
                self.__get_data()
        except FileNotFoundError as _:
            logger.error(f"Impossible to open '{file_path}'")

    def __get_data(self) -> None:
        """
        This function pulls the data out of the
        json file and stores it into the data members
        of the class.
        """

        for i in range(self.__n_plots):
            self.title[i] = str(self.__data_dict["title"])
            self.abscissa[i] = str(self.__data_dict["abscissa"])
            self.ordinate[i] = str(self.__data_dict["ordinate"])

            self.datasets[i] = self.__data_dict["datasets"]
            for j in self.datasets:
                j = str(j)

            self.functions[i] = self.__data_dict["functions"]
            for j in self.functions:
                j = str(j)

            self.histograms[i] = self.__data_dict["histograms"]
            for j in self.histograms:
                j = str(j)
