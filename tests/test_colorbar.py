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
        """The colorbar should shrink the target by exactly thickness+padding in the
        attachment direction, match its actual final length in the other direction
        (an aspect="equal" Image, like the one used here, may itself shrink further to
        keep its data square within the narrower/shorter box), and never overlap its
        ticks/labels/title."""
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
                assert original.width - shrunk.width == pytest.approx(thickness + pad_frac)
                assert cax.width == pytest.approx(thickness)
                assert cax.height == pytest.approx(shrunk.height)
                assert cax.y0 == pytest.approx(shrunk.y0)
                if position == "right":
                    assert shrunk.x0 == pytest.approx(original.x0)
                    assert cax.x0 >= shrunk.x1
                else:
                    assert shrunk.x1 == pytest.approx(original.x1)
                    assert cax.x1 <= shrunk.x0
            else:
                thickness = 0.10 * original.height
                pad_frac = 0.2 / fig_height_in
                assert original.height - shrunk.height == pytest.approx(thickness + pad_frac)
                assert cax.height == pytest.approx(thickness)
                assert cax.width == pytest.approx(shrunk.width)
                assert cax.x0 == pytest.approx(shrunk.x0)
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

    def test_sharing_a_row_keeps_same_aspect_subplots_uniform(self, text_file, show_plots) -> None:
        """A row-shared colorbar on the right shrinks the row's rightmost subplot for its
        own space; since both images here share the same (square) data aspect ratio, the
        other subplot should be resized to match it too, rather than being left taller."""
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

            final0 = canvas.axes[0].get_position()
            final1 = canvas.axes[1].get_position()

            assert final1.width < original1.width
            assert final0.width < original0.width
            assert final0.height == pytest.approx(final1.height)
            assert final0.width == pytest.approx(final1.width)
            cax = canvas.figure.axes[2].get_position()
            assert cax.height == pytest.approx(final1.height)
            assert cax.x1 == pytest.approx(original1.x1)

    def test_sharing_a_row_does_not_resize_others_without_a_shape_mismatch(self, text_file, show_plots) -> None:
        """When nothing forces a cross-dimension change (e.g. an aspect='auto' Hist2D),
        the rest of the row should be left exactly as it was."""
        with plt.Canvas(str(text_file), (1, 2), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            hist0 = make_hist2d()
            hist0.draw(canvas, plot_n=0)
            hist1 = make_hist2d()
            hist1.draw(canvas, plot_n=1)

            original0 = canvas.axes[0].get_position()

            colorbar = plt.Colorbar(source=hist1)
            colorbar.draw(canvas, row=0)

            assert canvas.axes[0].get_position().bounds == pytest.approx(original0.bounds)

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

    def test_geometry_is_stable_across_repeated_renders(self, text_file, show_plots) -> None:
        """Re-rendering the figure multiple times (e.g. once for savefig, once for
        show()) must not keep shrinking an aspect="equal" target -- regression test
        for a real bug where a since-removed adjustable="datalim" override caused the
        shrunk Axes' data limits to drift further apart on every subsequent render."""
        with plt.Canvas(str(text_file), (1, 2), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            image0 = make_image()
            image0.draw(canvas, plot_n=0)
            image1 = make_image()
            image1.draw(canvas, plot_n=1)

            colorbar = plt.Colorbar(source=image1)
            colorbar.draw(canvas, row=0)

            after_draw = canvas.axes[1].get_position().bounds
            xlim_after_draw = canvas.axes[1].get_xlim()
            ylim_after_draw = canvas.axes[1].get_ylim()

            for _ in range(3):
                canvas.figure.canvas.draw()
                assert canvas.axes[1].get_position().bounds == pytest.approx(after_draw)
                assert canvas.axes[1].get_xlim() == pytest.approx(xlim_after_draw)
                assert canvas.axes[1].get_ylim() == pytest.approx(ylim_after_draw)


class TestGridRealignment:
    """Tests for how `Colorbar.draw` realigns the rest of the canvas's grid."""

    def test_realigns_other_rows_to_match_a_row_colorbar(self, workspace, show_plots) -> None:
        """A colorbar on only one row of a 2x2 grid should shrink the untouched row's
        columns to match, not leave it wider than the row with the colorbar."""
        with plt.Canvas("grid_row_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            original = [ax.get_position() for ax in canvas.axes]

            colorbar = plt.Colorbar(source=images[3])
            colorbar.draw(canvas, row=1)

            final = [ax.get_position() for ax in canvas.axes]

            # row 1 (the colorbar's own row) shrank, as before
            assert final[2].width < original[2].width
            assert final[3].width < original[3].width
            # row 0 (untouched by the colorbar itself) should now match row 1's columns,
            # aligned on the same (left) edge, not just equal-width
            assert final[0].width == pytest.approx(final[2].width)
            assert final[0].x0 == pytest.approx(final[2].x0)
            assert final[1].width == pytest.approx(final[3].width)
            assert final[1].x0 == pytest.approx(final[3].x0)
            # row 0's own aspect="equal" images may need their height reduced too, to
            # stay square at the new narrower width -- centered within their original
            # vertical span, same convention used elsewhere for an unanchored dimension
            assert final[0].height <= original[0].height
            assert final[0].y0 + final[0].height / 2 == pytest.approx(original[0].y0 + original[0].height / 2)
            assert final[1].height <= original[1].height
            assert final[1].y0 + final[1].height / 2 == pytest.approx(original[1].y0 + original[1].height / 2)

    def test_realigns_other_columns_to_match_a_column_colorbar(self, workspace, show_plots) -> None:
        """A 'top' colorbar on only one column of a 2x2 grid should shrink the other
        column's rows to match, row by row, not leave them taller than column 1."""
        with plt.Canvas("grid_col_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            original = [ax.get_position() for ax in canvas.axes]

            colorbar = plt.Colorbar(source=images[1])
            colorbar.draw(canvas, col=1, position="top")

            final = [ax.get_position() for ax in canvas.axes]

            # column 1 (the colorbar's own column) shrank in height, as before
            assert final[1].height < original[1].height
            # column 0's row 0 (untouched by the colorbar itself) should now match
            # column 1's row 0 height, since they're in the same row -- aligned on the
            # same (top) edge, not just equal-height
            assert final[0].height == pytest.approx(final[1].height)
            assert final[0].y0 == pytest.approx(final[1].y0)
            # column 1's row 1 (index 3) may itself need a small height adjustment to
            # stay square at its (within-group) width-matched width -- whatever it
            # ends up at, column 0's row 1 (index 2) should still match it exactly,
            # aligned on the same edge
            assert final[2].height == pytest.approx(final[3].height)
            assert final[2].y0 == pytest.approx(final[3].y0)

    def test_does_not_realign_other_columns_for_a_column_colorbar(self, workspace, show_plots) -> None:
        """A 'right' colorbar on a whole column has no columns left to realign --
        every Axes sharing that column is already inside the target group."""
        with plt.Canvas("grid_col_only_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            original1 = canvas.axes[1].get_position()
            original3 = canvas.axes[3].get_position()

            colorbar = plt.Colorbar(source=images[0])
            colorbar.draw(canvas, col=0)

            assert canvas.axes[1].get_position().bounds == pytest.approx(original1.bounds)
            assert canvas.axes[3].get_position().bounds == pytest.approx(original3.bounds)

    def test_realigns_only_the_shared_column_for_a_single_subplot_target(self, workspace, show_plots) -> None:
        """A colorbar on a single subplot should only realign the rest of its own
        column, leaving the other column untouched."""
        with plt.Canvas("grid_single_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            original0 = canvas.axes[0].get_position()
            original1 = canvas.axes[1].get_position()
            original3 = canvas.axes[3].get_position()

            colorbar = plt.Colorbar(source=images[2])
            colorbar.draw(canvas, plot_n=2)

            # column 0 (subplots 0 and 2): subplot 0 realigns to match subplot 2
            assert canvas.axes[0].get_position().width < original0.width
            assert canvas.axes[0].get_position().width == pytest.approx(canvas.axes[2].get_position().width)
            # column 1 (subplots 1 and 3): untouched
            assert canvas.axes[1].get_position().bounds == pytest.approx(original1.bounds)
            assert canvas.axes[3].get_position().bounds == pytest.approx(original3.bounds)


class TestSharedMarginReuse:
    """Tests for how `Colorbar.draw` shares a margin between colorbars on different
    rows/columns of the same grid, instead of compounding their shrinks."""

    def test_two_same_size_colorbars_on_different_rows_do_not_compound(self, workspace, show_plots) -> None:
        """Regression test: a second Colorbar on a sibling row used to shrink the grid
        a second time, since its own grid-realignment step treated the first
        colorbar's already-adjusted columns as the 'original' size to shrink from."""
        with plt.Canvas("shared_margin_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            colorbar_row0 = plt.Colorbar(source=images[1])
            colorbar_row0.draw(canvas, row=0)

            after_first = [ax.get_position().bounds for ax in canvas.axes]

            colorbar_row1 = plt.Colorbar(source=images[3])
            colorbar_row1.draw(canvas, row=1)

            after_second = [ax.get_position().bounds for ax in canvas.axes]

            # nothing should have moved again -- the second colorbar reused the
            # margin the first one already reserved
            for before, after in zip(after_first, after_second):
                assert after == pytest.approx(before)

            # both colorbars share the exact same horizontal strip
            cax0 = colorbar_row0.mpl_colorbar.ax.get_position()
            cax1 = colorbar_row1.mpl_colorbar.ax.get_position()
            assert cax0.x0 == pytest.approx(cax1.x0)
            assert cax0.x1 == pytest.approx(cax1.x1)
            # but each covers only its own row's height
            assert cax0.y0 == pytest.approx(canvas.axes[1].get_position().y0)
            assert cax1.y0 == pytest.approx(canvas.axes[3].get_position().y0)

    def test_a_larger_second_colorbar_grows_the_shared_margin(self, workspace, show_plots) -> None:
        """If a second colorbar on a sibling row needs more room than the first one
        reserved, the shared margin (and the first colorbar) should grow to fit it,
        rather than the two colorbars ending up different widths."""
        with plt.Canvas("grow_margin_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            colorbar_row0 = plt.Colorbar(source=images[1])
            colorbar_row0.draw(canvas, row=0, size="2%")

            narrow_col1_width = canvas.axes[1].get_position().width

            colorbar_row1 = plt.Colorbar(source=images[3])
            colorbar_row1.draw(canvas, row=1, size="8%")

            # row 0 should have shrunk further to match row 1's larger requirement
            assert canvas.axes[1].get_position().width < narrow_col1_width
            assert canvas.axes[1].get_position().width == pytest.approx(canvas.axes[3].get_position().width)

            # the first colorbar should have grown to the same, larger thickness
            cax0 = colorbar_row0.mpl_colorbar.ax.get_position()
            cax1 = colorbar_row1.mpl_colorbar.ax.get_position()
            assert cax0.width == pytest.approx(cax1.width)
            assert cax0.x0 == pytest.approx(cax1.x0)
            assert cax0.x1 == pytest.approx(cax1.x1)

    def test_two_same_size_colorbars_on_different_columns_do_not_compound(self, workspace, show_plots) -> None:
        """Same as the row case, but for two 'top' colorbars on different columns."""
        with plt.Canvas("shared_margin_col_labels", (2, 2), figsize=(8.0, 8.0), show=show_plots) as canvas:
            canvas.setup(plot_n="all")
            images = [make_image() for _ in range(4)]
            for i, image in enumerate(images):
                image.draw(canvas, plot_n=i)

            colorbar_col0 = plt.Colorbar(source=images[0])
            colorbar_col0.draw(canvas, col=0, position="top")

            after_first = [ax.get_position().bounds for ax in canvas.axes]

            colorbar_col1 = plt.Colorbar(source=images[1])
            colorbar_col1.draw(canvas, col=1, position="top")

            after_second = [ax.get_position().bounds for ax in canvas.axes]

            for before, after in zip(after_first, after_second):
                assert after == pytest.approx(before)

            cax0 = colorbar_col0.mpl_colorbar.ax.get_position()
            cax1 = colorbar_col1.mpl_colorbar.ax.get_position()
            assert cax0.y0 == pytest.approx(cax1.y0)
            assert cax0.y1 == pytest.approx(cax1.y1)
