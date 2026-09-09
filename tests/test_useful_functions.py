"""Tests for miscellaneous plotting helper functions."""

import pytest
from matplotlib.colors import TABLEAU_COLORS

from plotter.helpers.useful_functions import get_colors


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
