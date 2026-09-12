"""Runnable example of the core Canvas / Drawable workflow.

Draws a row of three subplots -- a ScatterPlot with an overlaid LinePlot fit, a
BarChart, and a Hist -- driven by a JSON text file for the titles/axis labels/
legend labels, mirroring how a real project would use the library.

Run from anywhere:

    uv run python example/basic_plot.py

The rendered figure is saved to `example/output/plotter/img/basic_plot.png`.
"""

import os
from json import dumps
from pathlib import Path

import numpy as np

import plotter as p

# `setup_workspace()` (and everything else in the library that reads/writes
# 'plotter/...') always resolves paths relative to the current working
# directory. Running in a dedicated 'output' subdirectory keeps the generated
# 'plotter/' workspace out of this script's own directory -- which matters
# because a plain 'plotter/' directory sitting next to this script, without an
# '__init__.py', would otherwise shadow the real 'plotter' package on `import`.
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def model(x: np.ndarray) -> np.ndarray:
    """The function `ScatterPlot`'s noisy data is generated around."""
    return x**2


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    os.chdir(OUTPUT_DIR)

    p.setup_workspace()

    text = [
        {
            "title": "Data vs. model",
            "x_label": "$x$",
            "y_label": "$y$",
            "scatter_plots": ["measured"],
            "line_plots": [r"$f(x) = x^2$"],
        },
        {
            "title": "Counts per category",
            "x_label": "category",
            "y_label": "count",
            "bar_charts": ["counts"],
        },
        {
            "title": "Residual distribution",
            "x_label": "residual",
            "y_label": "density",
            "histograms": ["residuals"],
        },
    ]
    Path("plotter/text/basic_plot.json").write_text(dumps(text))

    rng = np.random.default_rng(0)
    x = np.linspace(-5, 5, num=50)
    residuals = rng.normal(scale=1.5, size=x.size)
    y = model(x) + residuals

    categories = np.array([0.0, 1.0, 2.0, 3.0])
    heights = np.array([2.0, 5.0, 3.0, 4.0])

    with p.Canvas("basic_plot.json", rows_cols=(1, 3), save="basic_plot.png", show=False) as canvas:
        canvas.setup()

        p.ScatterPlot(x, y, yerr=1.5).draw(canvas, plot_n=0)
        p.LinePlot(x, model).draw(canvas, plot_n=0)

        p.BarChart(categories, heights).draw(canvas, plot_n=1)

        p.Hist(residuals, nbins=12, density=True).draw(canvas, plot_n=2)


if __name__ == "__main__":
    main()
