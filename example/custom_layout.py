"""Runnable example of a non-grid `Canvas` layout, with shared axes.

`layout=` arranges the subplots as a mosaic of `plot_n` indices: repeating an index makes
that subplot span several cells. Here, subplots 0 and 1 are stacked in the left column
(sharing their x-axis, so only the bottom one keeps its tick labels), while subplot 2
spans the full height of a wider right column, with a `Colorbar` next to it.

Run from anywhere:

    uv run python example/custom_layout.py

The rendered figure is saved to
`example/output/plotter/img/custom_layout.png`.
"""

import os
from json import dumps
from pathlib import Path

import numpy as np

import plotter as p

# See basic_plot.py for why the workspace lives in a dedicated subdirectory
# rather than next to this script.
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    os.chdir(OUTPUT_DIR)

    p.setup_workspace()

    # one entry per distinct subplot (3), not per cell of the mosaic (4)
    text = [
        {
            "title": "Signal",
            "x_label": "",
            "y_label": "amplitude",
            "scatter_plots": ["measured"],
            "line_plots": ["model"],
        },
        {
            "title": "Residuals",
            "x_label": "time (s)",
            "y_label": "residual",
            "scatter_plots": ["measured - model"],
        },
        {"title": "Residual vs. amplitude", "x_label": "amplitude", "y_label": "residual"},
    ]
    Path("plotter/text/custom_layout.json").write_text(dumps(text))

    rng = np.random.default_rng(0)
    time_s = np.linspace(0.0, 10.0, num=200)
    model = np.sin(time_s)
    signal = model + rng.normal(scale=0.2, size=time_s.size)
    residuals = signal - model

    # many more samples for a well-populated 2D histogram
    amplitude = rng.uniform(-1.0, 1.0, size=20000)
    amplitude_residuals = rng.normal(scale=0.1 + 0.2 * np.abs(amplitude))

    with p.Canvas(
        "custom_layout.json",
        layout=[[0, 2], [1, 2]],
        width_ratios=(1.0, 1.2),
        sharex="col",
        figsize=(14.0, 7.0),
        save="custom_layout.png",
        show=False,
    ) as canvas:
        canvas.setup(plot_n=(0, 1))
        canvas.setup(plot_n=2, nogrid=True)

        p.ScatterPlot(time_s, signal).draw(canvas, plot_n=0)
        p.LinePlot(time_s, model).draw(canvas, plot_n=0)
        p.ScatterPlot(time_s, residuals).draw(canvas, plot_n=1)
        canvas.draw_line("h", 0.0, plot_n=1)

        hist2d = p.RawHist2D(amplitude, amplitude_residuals, nbins=50)
        hist2d.draw(canvas, plot_n=2)
        p.Colorbar(source=hist2d).draw(canvas, plot_n=2, label="count")


if __name__ == "__main__":
    main()
