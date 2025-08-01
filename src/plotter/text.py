import json
import pathlib
import logging

logger = logging.getLogger(__name__)

BLUEPRINT = {"title": "", "abscissa": "", "ordinate": "", "datasets": [""], "functions": [""], "histograms": [""]}


class Text:
    """
    Class for storing and accessing the text to be displayed on the canvas.

    Args:
        text_file (str): The name of the JSON file where the text for the canvases is stored.
        n_plots (int): The number of subplots in the canvas.
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

        # add json extension if necessary
        if text_file[-5:] != ".json":
            text_file += ".json"
            logger.debug("Appended json extension to text file.")
        file_path = pathlib.Path("./plotter/text").joinpath(text_file)

        try:
            with open(file_path, "r") as json_file:
                logger.debug(f"Opened '{file_path}'")
                self.__data_dict = json.load(json_file)
                self.__get_data()
        except FileNotFoundError as _:
            logger.debug(f"Creating {file_path}.")

            # create json file
            with open(file_path, "w") as json_file:
                json.dump([BLUEPRINT for _ in range(self.__n_plots)], json_file)

            # read newly created file
            with open(file_path, "r") as json_file:
                logger.debug(f"Opened '{file_path}'")
                self.__data_dict = json.load(json_file)
                self.__get_data()
        except json.JSONDecodeError as _:
            logger.error(f"Impossible to open {file_path}")

    def __get_data(self) -> None:
        """
        Pulls data from the JSON file and stores it in the class data members.
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


if __name__ == "__main__":
    pass
