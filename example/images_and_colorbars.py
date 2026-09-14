"""Runnable example of RawHist2D/BinnedHist2D/Image, explicit Colorbars, and a zoom inset.

Unlike ScatterPlot/LinePlot/BarChart/RawHist/BinnedHist, `RawHist2D`, `BinnedHist2D`, and
`Image` don't take a `label` and aren't driven by the JSON text file's label lists -- their
color mapping is instead exposed through a `Colorbar`, drawn explicitly. This also
shows `Canvas.add_zoom_inset`, which returns a panel that any `Drawable` can
be drawn into just like a real subplot.

Run from anywhere:

    uv run python example/images_and_colorbars.py

The rendered figure is saved to
`example/output/plotter/img/images_and_colorbars.png`.
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

    text = [
        {"title": "2D histogram", "x_label": "$x$", "y_label": "$y$"},
        {"title": "Synthetic image", "x_label": "x (px)", "y_label": "y (px)"},
        {"title": "Pre-binned 2D histogram", "x_label": "$x$", "y_label": "$y$"},
    ]
    Path("plotter/text/images_and_colorbars.json").write_text(dumps(text))

    rng = np.random.default_rng(0)

    # correlated 2D data for the histogram
    x = rng.normal(size=5000)
    y = x + rng.normal(scale=0.5, size=5000)

    # a synthetic image with a bright blob, to zoom into
    size = 200
    xx, yy = np.meshgrid(np.linspace(-3, 3, size), np.linspace(-3, 3, size))
    image_data = np.exp(-(xx**2 + yy**2)) + 0.05 * rng.normal(size=(size, size))

    # already-binned counterpart to the first subplot's histogram, computed ahead of
    # time (e.g. loaded from a file) rather than binned from raw samples at draw time
    bin_vals, xbins, ybins = np.histogram2d(x, y, bins=40)

    with p.Canvas(
        "images_and_colorbars.json", rows_cols=(1, 3), figsize=(20.0, 6.0), save="images_and_colorbars.png", show=False
    ) as canvas:
        # extra room between subplots for each one's colorbar label
        canvas.figure.subplots_adjust(wspace=0.6)
        canvas.setup(nogrid=True)

        hist2d = p.RawHist2D(x, y, nbins=40)
        hist2d.draw(canvas, plot_n=0)
        p.Colorbar(source=hist2d).draw(canvas, plot_n=0, label="count")

        image = p.Image(image_data)
        image.draw(canvas, plot_n=1)
        p.Colorbar(source=image).draw(canvas, plot_n=1, label="intensity")

        inset = canvas.add_zoom_inset((80, 120), (80, 120), plot_n=1, location="lower left")
        image.draw(inset)

        binned_hist2d = p.BinnedHist2D(bin_vals, xbins, ybins)
        binned_hist2d.draw(canvas, plot_n=2)
        p.Colorbar(source=binned_hist2d).draw(canvas, plot_n=2, label="count")


if __name__ == "__main__":
    main()
