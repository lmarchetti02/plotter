import numpy as np

import plotter as plt


def test_scatter(tmp_path):
    text_file = str(tmp_path / "scatter")
    canvas = plt.Canvas(text_file)
    canvas.setup()

    dy, dx = 0.5, 0.1
    rng = np.random.default_rng(0)
    x = np.linspace(0, 10, 75)
    x += rng.normal(0, dx, len(x))
    y = rng.normal(x, dy)

    plt.ScatterPlot(x, y, dy, dx).draw(canvas, label="Scatter Plot")

    canvas.end()
