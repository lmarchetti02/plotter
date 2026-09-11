"""Tests for explicit colorbar drawing."""

import numpy as np
import pytest

import plotter as plt


def make_image(fill: float = 1.0) -> plt.Image:
    """Build a small grayscale test image."""
    data = np.zeros((10, 10))
    data[2:5, 2:5] = fill
    return plt.Image(data)


def make_hist2d() -> plt.Hist2D:
    """Build a small 2D histogram for test use."""
    rng = np.random.default_rng(0)
    x = rng.normal(5.0, 1.5, 500)
    y = rng.normal(5.0, 2.5, 500)
    return plt.Hist2D(x, y, 10)


class TestDraw:
    """Tests for `Colorbar.draw`."""

    def test_creates_a_colorbar_for_an_image_source(self, single_text_file, show_plots) -> None:
        """A Colorbar attached to a single subplot should add one labeled Axes."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            image = make_image()
            image.draw(canvas)

            colorbar = plt.Colorbar(source=image)
            colorbar.draw(canvas, label="Intensity")

            assert len(canvas.figure.axes) == 2
            assert canvas.figure.axes[1].get_ylabel() == "Intensity"

    def test_creates_a_colorbar_for_a_hist2d_source(self, single_text_file, show_plots) -> None:
        """A Colorbar should also work when its source is a Hist2D."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            hist = make_hist2d()
            hist.draw(canvas)

            colorbar = plt.Colorbar(source=hist)
            colorbar.draw(canvas, label="Density")

            assert len(canvas.figure.axes) == 2
            assert canvas.figure.axes[1].get_ylabel() == "Density"

    def test_shares_a_colorbar_across_a_row(self, text_file, show_plots) -> None:
        """A single Colorbar drawn with row= should span all subplots in that row, not one per subplot."""
        with plt.Canvas(str(text_file), (1, 2), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            image0 = make_image()
            image0.draw(canvas, plot_n=0, colormap="gray")
            image1 = make_image()
            image1.draw(canvas, plot_n=1, colormap="gray")

            colorbar = plt.Colorbar(source=image0)
            colorbar.draw(canvas, row=0)

            assert len(canvas.figure.axes) == 3

    def test_shares_a_colorbar_across_a_column(self, text_file, show_plots) -> None:
        """A single Colorbar drawn with col= should span all subplots in that column."""
        with plt.Canvas(str(text_file), (2, 1), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            image0 = make_image()
            image0.draw(canvas, plot_n=0, colormap="gray")
            image1 = make_image()
            image1.draw(canvas, plot_n=1, colormap="gray")

            colorbar = plt.Colorbar(source=image0)
            colorbar.draw(canvas, col=0)

            assert len(canvas.figure.axes) == 3

    def test_raises_when_source_has_not_been_drawn(self, single_text_file, show_plots) -> None:
        """Attaching a Colorbar to an undrawn source should fail loudly rather than error deep in matplotlib."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            colorbar = plt.Colorbar(source=make_image())

            with pytest.raises(RuntimeError, match="has not been drawn"):
                colorbar.draw(canvas)

    def test_rejects_row_and_col_given_together(self, text_file, show_plots) -> None:
        """Ambiguous targeting should fail loudly."""
        with plt.Canvas(str(text_file), (1, 2), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            image = make_image()
            image.draw(canvas, plot_n=0)

            colorbar = plt.Colorbar(source=image)
            with pytest.raises(ValueError, match="Exactly one of"):
                colorbar.draw(canvas, row=0, col=0)

    def test_works_with_a_zoom_inset(self, single_text_file, show_plots) -> None:
        """A Colorbar should be attachable to a ZoomInset's single Axes."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            inset = canvas.add_zoom_inset(xlim=(2, 5), ylim=(2, 5))
            inset_image = make_image()
            inset_image.draw(inset)

            colorbar = plt.Colorbar(source=inset_image)
            colorbar.draw(inset)

            assert len(canvas.figure.axes) == 3

    def test_rejects_row_or_col_for_a_zoom_inset(self, single_text_file, show_plots) -> None:
        """A ZoomInset has only one Axes, so row/col targeting doesn't apply."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            inset = canvas.add_zoom_inset(xlim=(2, 5), ylim=(2, 5))
            inset_image = make_image()
            inset_image.draw(inset)

            colorbar = plt.Colorbar(source=inset_image)
            with pytest.raises(ValueError, match="not supported for a ZoomInset"):
                colorbar.draw(inset, row=0)

    def test_passes_kwargs_through_to_matplotlib_colorbar(self, single_text_file, show_plots) -> None:
        """Extra keyword arguments should reach `Figure.colorbar` unchanged."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            image = make_image()
            image.draw(canvas)

            colorbar = plt.Colorbar(source=image)
            colorbar.draw(canvas, label="Value", orientation="horizontal")

            assert canvas.figure.axes[1].get_xlabel() == "Value"
            assert canvas.figure.axes[1].get_ylabel() == ""
