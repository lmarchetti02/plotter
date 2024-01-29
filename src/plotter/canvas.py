from .functions import denser, setup_logging
import numpy as np
import logging
import matplotlib.pyplot as plt
import pathlib
from typing import Optional
from .text import Text

plt.style.use(pathlib.Path("./plotter/utils/style.mplstyle"))

logger = logging.getLogger(__name__)


class Canvas:
    """
    Inizializza un piano cartesiano su cui è possibile disegnare dataset e
    funzioni.

    Parametri
    ---
    text: str
        Nome del file .txt in cui è memorizzato il testo da mostrare
        nel grafico.
    fs: tuple
        Tupla contenente le dimensioni dell'immagine. Se non viene
        specificata, `fs=(12,8)`.
    dpi: int
        'Dots per inches' dell'immagine (vedi documentazione matplotlib).
        Se non viene specificata, `dpi=150`.

    Parametri opzionali
    ---
    xlim: list
        Lista con limite sx e dx dell'asse delle ascisse.
    ylim: list
        Lista con limite inf e sup dell'asse delle ordinate.
    yscale: str
        Scala dell'asse delle ordinate. Può essere: 'linear' (default),
        'log' o 'symlog'.
    xscale: str
        Scala dell'asse delle ascisse. Può essere: 'linear' (default),
        'log' o 'symlog'.
    save: str
        Se passata come parametro, l'immagine creata viene salvata nella
        cartella ~/img con il nome indicato da tale parametro.
    log_file: str
        Specifica dove si vuole salvare il log della libreria.


    """

    def __init__(
        self,
        text_file: str,
        fs: Optional[tuple[int, int]] = (12, 8),
        dpi: Optional[int] = 150,
        **kwargs,
    ) -> None:
        setup_logging()

        logger.info("Creato oggetto Canvas")

        self.counter_scatter_plots = 0
        self.counter_graphs = 0

        # def proprietà grafico
        self.fig, self.ax = plt.subplots(figsize=(fs[0], fs[1]), dpi=dpi)
        self.kwargs = kwargs

        # testo
        self.text = Text(text_file)

        # griglia
        self.ax.grid(color="darkgray", alpha=0.5, linestyle="dashed", lw=0.5)

        # limiti assi
        if "xlim" in self.kwargs.keys():
            self.ax.set_xlim(self.kwargs["xlim"][0], self.kwargs["xlim"][1])

        if "ylim" in self.kwargs.keys():
            self.ax.set_ylim(self.kwargs["ylim"][0], self.kwargs["ylim"][1])

        # scala assi
        if "yscale" in self.kwargs.keys():
            self.ax.set_yscale(self.kwargs["yscale"])

        if "xscale" in self.kwargs.keys():
            self.ax.set_xscale(self.kwargs["xscale"])

        try:
            # nome assi
            self.ax.set_xlabel(self.text.get_ascisse())
            self.ax.set_ylabel(self.text.get_ordinate())

            # titolo
            plt.title(self.text.get_titolo(), y=1)

            logger.debug("Testo del canvas inserito.")
        except Exception:
            logger.exception("Errore nell'ottenimento del testo relativo al canvas.")

    def __legenda(self) -> None:
        """
        Quando chiamata, questa funzione mostra la legenda nel grafico.
        Fa parte del mainloop dell'oggetto `Canvas`.
        """
        try:
            self.ax.legend(loc=0)
            plt.legend(labelspacing=1)

            logger.debug("Mostrata la legenda.")
        except Exception:
            logger.exception("Errore nel mostrare la legenda.")

    def __save(self) -> None:
        """
        Se l'utente lo vuole, questa funzione salva l'immagine
        nella cartella 'img'.

        Fa parte del mainloop dell'oggetto `Canvas`.
        """

        if "save" in self.kwargs.keys():
            self.fig.savefig(f"img/{self.kwargs['save']}")
            logger.debug("File salvato.")
        else:
            logger.warning("File non salvato.")

    def mainloop(self, show: Optional[bool] = True) -> None:
        """
        Funzione necessaria per renderizzare il grafico voluto. Ciò
        che viene dopo questa funzione non modifica in alcun modo il
        grafico.
        """

        self.__legenda()
        self.__save()
        logger.info("Fine disegno")

        # mostra il grafico s
        if show:
            plt.show()
        elif not show:
            plt.close()


if __name__ == "__main__":
    pass
