import numpy as np

import plotter as plt


def test_hist(tmp_path):
    text_file = str(tmp_path / "hist")
    canvas = plt.Canvas(text_file)
    canvas.setup()

    rng = np.random.default_rng(0)
    x = rng.normal(5.0, 1.5, 1_000)

    hist = plt.Hist(x)
    hist.draw(canvas, label="Histogram")

    assert hist.bins is not None
    assert hist.bin_vals is not None

    canvas.end()


def test_hist2d(tmp_path):
    text_file = str(tmp_path / "hist")
    canvas = plt.Canvas(text_file)
    canvas.setup()

    rng = np.random.default_rng(0)
    x = rng.normal(5.0, 1.5, 1_000)
    y = rng.normal(5.0, 2.5, 1_000)

    hist = plt.Hist2D(x, y, 20)
    hist.draw(canvas, label="2D Histogram")

    assert hist.xbins is not None
    assert hist.ybins is not None
    assert hist.bin_vals is not None

    canvas.end()
