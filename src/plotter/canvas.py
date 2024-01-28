from .functions import denser, setup_logging
import numpy as np
import logging

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    logger.info("START")

    a = np.array([1, 2, 3, 5, 6])

    a = denser(a, 3)

    logger.info("END")


if __name__ == "__main__":
    pass
