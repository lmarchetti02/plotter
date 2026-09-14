"""Tests for 1D and 2D histograms drawn from pre-computed bin values."""

import numpy as np
import pytest
from matplotlib.collections import QuadMesh
from unittest.mock import patch

import plotter as plt


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


class TestBinnedHist2DDraw:
    """Tests for `BinnedHist2D.draw`."""

    def test_draws_pre_binned_values_via_pcolormesh(self, single_text_file, show_plots) -> None:
        """A pre-binned 2D histogram should draw the given grid as-is via pcolormesh."""
        bin_vals = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        xbins = np.array([0.0, 1.0, 2.0, 3.0])
        ybins = np.array([0.0, 1.0, 2.0])

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            hist = plt.BinnedHist2D(bin_vals, xbins, ybins)

            hist.draw(canvas)

            assert isinstance(hist.mappable, QuadMesh)
            assert len(canvas.figure.axes) == 1

    def test_rejects_mismatched_bin_vals_shape(self) -> None:
        """`bin_vals` must have shape (len(xbins) - 1, len(ybins) - 1)."""
        bin_vals = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        xbins = np.array([0.0, 1.0, 2.0, 3.0])
        ybins = np.array([0.0, 1.0, 2.0, 3.0])

        with pytest.raises(ValueError, match="must have shape"):
            plt.BinnedHist2D(bin_vals, xbins, ybins)
