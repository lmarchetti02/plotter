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

    def test_orientation_follows_position(self, single_text_file, show_plots) -> None:
        """A 'top'/'bottom' position should produce a horizontal colorbar (label on the x-axis)."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            image = make_image()
            image.draw(canvas)

            colorbar = plt.Colorbar(source=image)
            colorbar.draw(canvas, label="Value", position="bottom")

            assert canvas.figure.axes[1].get_xlabel() == "Value"
            assert canvas.figure.axes[1].get_ylabel() == ""

    def test_passes_cosmetic_kwargs_through_to_matplotlib_colorbar(self, single_text_file, show_plots) -> None:
        """Non-positional keyword arguments should reach the underlying `matplotlib.colorbar.Colorbar`."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            image = make_image()
            image.draw(canvas)

            colorbar = plt.Colorbar(source=image)
            colorbar.draw(canvas, extend="both")

            assert colorbar.mpl_colorbar is not None
            assert colorbar.mpl_colorbar.extend == "both"

    def test_rejects_an_invalid_position(self, single_text_file, show_plots) -> None:
        """An unsupported 'position' value should fail loudly."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            image = make_image()
            image.draw(canvas)

            colorbar = plt.Colorbar(source=image)
            with pytest.raises(ValueError, match="not a valid position"):
                colorbar.draw(canvas, position="north")


class TestPositioning:
    """Tests for how `Colorbar.draw` sizes and places the colorbar Axes."""

    @pytest.mark.parametrize("position", ["left", "right", "top", "bottom"])
    def test_attaches_with_the_requested_size_and_gap(self, single_text_file, show_plots, position: str) -> None:
        """The colorbar should match the target's own length and thickness, shrink the
        target by exactly thickness+padding, and never overlap its ticks/labels/title."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            image = make_image()
            image.draw(canvas)
            original = canvas.axes[0].get_position()

            colorbar = plt.Colorbar(source=image)
            colorbar.draw(canvas, position=position, size="10%", padding=0.2)

            shrunk_axes = canvas.axes[0]
            shrunk = shrunk_axes.get_position()
            cax_axes = canvas.figure.axes[1]
            cax = cax_axes.get_position()
            fig_width_in, fig_height_in = canvas.figure.get_size_inches()

            if position in ("left", "right"):
                thickness = 0.10 * original.width
                pad_frac = 0.2 / fig_width_in
                assert shrunk.height == pytest.approx(original.height)
                assert original.width - shrunk.width == pytest.approx(thickness + pad_frac)
                assert cax.width == pytest.approx(thickness)
                assert cax.height == pytest.approx(original.height)
                assert cax.y0 == pytest.approx(original.y0)
                if position == "right":
                    assert shrunk.x0 == pytest.approx(original.x0)
                    assert cax.x0 >= shrunk.x1
                else:
                    assert shrunk.x1 == pytest.approx(original.x1)
                    assert cax.x1 <= shrunk.x0
            else:
                thickness = 0.10 * original.height
                pad_frac = 0.2 / fig_height_in
                assert shrunk.width == pytest.approx(original.width)
                assert original.height - shrunk.height == pytest.approx(thickness + pad_frac)
                assert cax.height == pytest.approx(thickness)
                assert cax.width == pytest.approx(original.width)
                assert cax.x0 == pytest.approx(original.x0)
                if position == "top":
                    assert shrunk.y0 == pytest.approx(original.y0)
                    assert cax.y0 >= shrunk.y1
                else:
                    assert shrunk.y1 == pytest.approx(original.y1)
                    assert cax.y1 <= shrunk.y0

            # the colorbar should never overlap the target's full rendered footprint,
            # ticks/labels/title included -- separated along at least one axis
            shrunk_tight = shrunk_axes.get_tightbbox().transformed(canvas.figure.transFigure.inverted())
            separated = cax.x0 >= shrunk_tight.x1 or cax.x1 <= shrunk_tight.x0 or cax.y0 >= shrunk_tight.y1 or cax.y1 <= shrunk_tight.y0
            assert separated

    def test_sharing_a_row_only_shrinks_the_edge_subplot(self, text_file, show_plots) -> None:
        """A row-shared colorbar on the right should only shrink the row's rightmost subplot."""
        with plt.Canvas(str(text_file), (1, 2), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            image0 = make_image()
            image0.draw(canvas, plot_n=0)
            image1 = make_image()
            image1.draw(canvas, plot_n=1)

            original0 = canvas.axes[0].get_position()
            original1 = canvas.axes[1].get_position()

            colorbar = plt.Colorbar(source=image1)
            colorbar.draw(canvas, row=0)

            assert canvas.axes[0].get_position().bounds == pytest.approx(original0.bounds)
            assert canvas.axes[1].get_position().width < original1.width
            cax = canvas.figure.axes[2].get_position()
            assert cax.x1 == pytest.approx(original1.x1)

    def test_sharing_a_column_shrinks_every_subplot_in_it(self, text_file, show_plots) -> None:
        """A column-shared colorbar on the right should shrink every subplot in that column,
        since they all share its right edge."""
        with plt.Canvas(str(text_file), (2, 1), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            image0 = make_image()
            image0.draw(canvas, plot_n=0)
            image1 = make_image()
            image1.draw(canvas, plot_n=1)

            original0 = canvas.axes[0].get_position()
            original1 = canvas.axes[1].get_position()

            colorbar = plt.Colorbar(source=image0)
            colorbar.draw(canvas, col=0)

            assert canvas.axes[0].get_position().width < original0.width
            assert canvas.axes[1].get_position().width < original1.width
