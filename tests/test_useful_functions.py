"""Tests for miscellaneous plotting helper functions."""

import numpy as np
import pytest
from matplotlib.colors import TABLEAU_COLORS

from plotter.helpers.useful_functions import get_colors, stack_bottoms


class TestGetColors:
    """Tests for `get_colors`."""

    def test_returns_the_requested_number_of_colors(self) -> None:
        """The returned list should have exactly `length` entries."""
        colors = get_colors(4)
        assert len(colors) == 4
        assert all(color in TABLEAU_COLORS for color in colors)

    def test_returns_unique_colors_when_within_the_tableau_palette(self) -> None:
        """Requesting no more colors than the palette holds should avoid repeats."""
        colors = get_colors(5)
        assert len(set(colors)) == len(colors)

    def test_allows_repeats_when_more_colors_are_requested_than_the_palette_holds(self) -> None:
        """Requesting more colors than the palette holds should still succeed, with repeats."""
        colors = get_colors(20)
        assert len(colors) == 20

    def test_builds_a_gradient_between_the_given_endpoints(self) -> None:
        """A gradient request should interpolate colors between the two given endpoints."""
        colors = get_colors(5, gradient=("#000000", "#ffffff"))

        assert len(colors) == 5
        assert colors[0] == pytest.approx((0.0, 0.0, 0.0, 1.0))
        assert colors[-1] == pytest.approx((1.0, 1.0, 1.0, 1.0))


class TestStackBottoms:
    """Tests for `stack_bottoms`."""

    def test_returns_zeros_for_the_first_series(self) -> None:
        """The first series in a stack always starts at zero."""
        bottoms = stack_bottoms([np.array([1.0, 2.0]), np.array([3.0, 4.0])])
        assert bottoms[0] == pytest.approx([0.0, 0.0])

    def test_accumulates_heights_across_series(self) -> None:
        """Each series' bottom should be the running sum of every series below it."""
        series_a = np.array([1.0, 2.0, 3.0])
        series_b = np.array([4.0, 1.0, 2.0])
        series_c = np.array([2.0, 3.0, 1.0])

        bottoms = stack_bottoms([series_a, series_b, series_c])

        assert bottoms[0] == pytest.approx([0.0, 0.0, 0.0])
        assert bottoms[1] == pytest.approx(series_a)
        assert bottoms[2] == pytest.approx(series_a + series_b)

    def test_single_series_returns_zeros(self) -> None:
        """A single-series stack has nothing to offset it, so its bottom is all zeros."""
        bottoms = stack_bottoms([np.array([1.0, 2.0])])
        assert len(bottoms) == 1
        assert bottoms[0] == pytest.approx([0.0, 0.0])

    def test_rejects_empty_input(self) -> None:
        """An empty list of series has nothing to stack."""
        with pytest.raises(ValueError, match="heights must contain at least one series"):
            stack_bottoms([])

    def test_rejects_mismatched_series_lengths(self) -> None:
        """All series in a stack must share the same length to align bar-by-bar."""
        with pytest.raises(ValueError, match="all series in heights must have the same length"):
            stack_bottoms([np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0])])
