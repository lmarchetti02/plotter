"""Tests for 1D and 2D histograms drawn from raw sample data."""

import numpy as np
import pytest
from matplotlib.collections import QuadMesh

import plotter as plt


class TestRawHistDraw:
    """Tests for `RawHist.draw`."""

    def test_populates_bin_information_and_uses_canvas_label(self, single_text_file, show_plots) -> None:
        """A histogram draw call should store computed bins and increment the subplot counter."""
        rng = np.random.default_rng(0)
        data = rng.normal(5.0, 1.5, 1_000)

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            hist = plt.RawHist(data, nbins=15, density=True)

            hist.draw(canvas)

            assert hist.bins is not None
            assert hist.bin_vals is not None
            assert len(hist.bins) == 16
            assert len(hist.bin_vals) == 15
            assert canvas.counters.histograms[0] == 1
            assert canvas.axes[0].patches[0].get_label() == "hist"


class TestRawHist2DDraw:
    """Tests for `RawHist2D.draw`."""

    @pytest.mark.parametrize("log", [(False, 0.0), (True, 0.0), (True, 1.0)])
    def test_renders_for_supported_normalizations(self, single_text_file, log: tuple[bool, float], show_plots) -> None:
        """RawHist2D should render successfully for linear, log, and symlog normalization modes."""
        rng = np.random.default_rng(0)
        x = rng.normal(5.0, 1.5, 1_000)
        y = rng.normal(5.0, 2.5, 1_000)

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            hist = plt.RawHist2D(x, y, 20)

            hist.draw(canvas, log=log)

            assert hist.xbins is not None
            assert hist.ybins is not None
            assert hist.bin_vals is not None
            assert hist.bin_vals.shape == (20, 20)
            assert isinstance(hist.mappable, QuadMesh)
            assert len(canvas.figure.axes) == 1
