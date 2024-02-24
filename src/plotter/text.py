import json
import pathlib
import logging

logger = logging.getLogger(__name__)


class Text:
    """
    Class used for storing and accessing the
    text to be displayed in the canvas.

    Parameters
    ---
    text_file: str
        The name of the json file where the text belonging
        to the canvases is stored.
    n_plots: int
        The number of subplots in the canvas.
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

        logger.info("Called 'Text.__get_data()'")

        for i in range(self.__n_plots):
            self.title[i] = str(self.__data_dict[i]["title"])
            self.abscissa[i] = str(self.__data_dict[i]["abscissa"])
            self.ordinate[i] = str(self.__data_dict[i]["ordinate"])

            self.datasets[i] = self.__data_dict[i]["datasets"]
            for j in self.datasets:
                j = str(j)

            self.functions[i] = self.__data_dict[i]["functions"]
            for j in self.functions:
                j = str(j)

            self.histograms[i] = self.__data_dict[i]["histograms"]
            for j in self.histograms:
                j = str(j)

        logger.debug(f"Titles: {self.title}")
        logger.debug(f"Abscissas: {self.abscissa}")
        logger.debug(f"Ordinates: {self.ordinate}")
        logger.debug(f"Datasets: {self.datasets}")
        logger.debug(f"Functions: {self.functions}")
        logger.debug(f"Histograms: {self.histograms}")
