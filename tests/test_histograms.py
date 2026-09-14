"""Tests for 1D and 2D histogram drawing."""

import numpy as np
import pytest
from matplotlib.collections import QuadMesh
from unittest.mock import patch

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


class TestBinnedHistDraw:
    """Tests for `BinnedHist.draw`."""

    def test_draws_pre_binned_values_via_stairs(self, single_text_file, show_plots) -> None:
        """A pre-binned histogram should draw through stairs, using the given values as-is."""
        bin_vals = np.array([2.0, 4.0, 3.0])
        bins = np.array([0.0, 1.0, 2.0, 3.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            hist = plt.BinnedHist(bin_vals, bins)

            axes_type = type(canvas.axes[0])
            with patch.object(axes_type, "hist", autospec=True) as hist_mock, patch.object(
                axes_type, "stairs", autospec=True
            ) as stairs_mock:
                hist.draw(canvas)

            hist_mock.assert_not_called()
            stairs_mock.assert_called_once()

            args, kwargs = stairs_mock.call_args
            assert args[1] is bin_vals
            assert np.array_equal(args[2], bins)
            assert kwargs["fill"] is True
            assert kwargs["label"] == "hist"
            assert hist.bin_vals is bin_vals
            assert hist.bins is bins
            assert canvas.counters.histograms[0] == 1

    def test_rejects_mismatched_bin_vals_and_bins_lengths(self) -> None:
        """`bin_vals` must have exactly one fewer element than `bins`."""
        with pytest.raises(ValueError, match="one fewer element"):
            plt.BinnedHist(np.array([2.0, 4.0, 3.0]), np.array([0.0, 1.0, 2.0]))


class TestHist2DDraw:
    """Tests for `Hist2D.draw`."""

    @pytest.mark.parametrize("log", [(False, 0.0), (True, 0.0), (True, 1.0)])
    def test_renders_for_supported_normalizations(self, single_text_file, log: tuple[bool, float], show_plots) -> None:
        """Hist2D should render successfully for linear, log, and symlog normalization modes."""
        rng = np.random.default_rng(0)
        x = rng.normal(5.0, 1.5, 1_000)
        y = rng.normal(5.0, 2.5, 1_000)

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            hist = plt.Hist2D(x, y, 20)

            hist.draw(canvas, log=log)

            assert hist.xbins is not None
            assert hist.ybins is not None
            assert hist.bin_vals is not None
            assert hist.bin_vals.shape == (20, 20)
            assert isinstance(hist.mappable, QuadMesh)
            assert len(canvas.figure.axes) == 1
