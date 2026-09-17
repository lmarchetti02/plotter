"""Tests for canvas setup and drawing helpers."""

from pathlib import Path
from unittest.mock import patch
from warnings import warn

import matplotlib
import numpy as np
import pytest
from matplotlib.colors import to_rgb
from matplotlib.layout_engine import PlaceHolderLayoutEngine
from matplotlib.offsetbox import AnchoredOffsetbox

import plotter as plt


class TestReorientedLoc:
    """Tests for `_reoriented_loc`."""

    @pytest.mark.parametrize(
        "loc, x_inverted, y_inverted, expected",
        [
            (1, False, False, 1),  # no inversion: unchanged
            (1, True, False, 2),  # upper right, x inverted -> upper left
            (1, False, True, 4),  # upper right, y inverted -> lower right
            (1, True, True, 3),  # upper right, both inverted -> lower left
            (3, True, False, 4),  # lower left, x inverted -> lower right
        ],
    )
    def test_remaps_to_keep_the_same_visual_corner(self, loc: int, x_inverted: bool, y_inverted: bool, expected: int) -> None:
        """The remapped code should always point at the same visual corner."""
        assert plt.canvas._reoriented_loc(loc, x_inverted, y_inverted) == expected


class TestCounters:
    """Tests for `_Counters`."""

    def test_initializes_with_one_slot_per_subplot(self) -> None:
        """Counters should start empty and track each drawable family independently."""
        counters = plt.canvas._Counters.initialize_counters(2)

        for name in plt.Drawable.get_label_names():
            assert getattr(counters, name) == [0, 0]

        assert counters.is_empty()

        counters.histograms[0] += 1
        counters.scatter_plots[1] += 1

        assert not counters.is_empty()


class TestCanvas:
    """Tests for `Canvas`."""

    def test_accepts_fractional_figsize(self, single_text_file: Path) -> None:
        """Canvas should accept non-integer figure dimensions."""
        with plt.Canvas(str(single_text_file), figsize=(12.5, 8.25), show=False) as canvas:
            assert tuple(canvas.figure.get_size_inches()) == pytest.approx((12.5, 8.25), abs=0.01)

    def test_saves_requested_figure(self, workspace: Path, single_text_file: Path) -> None:
        """Exiting the canvas context should save the figure when a filename is provided."""
        image_dir = workspace / "plotter/img"
        image_dir.mkdir(exist_ok=True)
        output_file = image_dir / "figure.png"

        with plt.Canvas(str(single_text_file), save="figure.png", show=False) as canvas:
            canvas.setup()

        assert output_file.exists()

    def test_exiting_does_not_leak_the_promoted_warnings_filter(self, single_text_file: Path) -> None:
        """`_legend` promotes UserWarning to an error to detect empty legends; that must not
        outlive the `with` block, or an unrelated later UserWarning (e.g. from `savefig`)
        would incorrectly raise instead of just being emitted."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

        warn("unrelated warning raised after the canvas context has exited", UserWarning)

    @pytest.mark.parametrize("rows_cols", [(0, 1), (1, 0), (-1, 1), (1, -1)])
    def test_rejects_non_positive_rows_or_columns(self, single_text_file: Path, rows_cols: tuple[int, int]) -> None:
        """Zero or negative rows/columns should fail loudly instead of reaching `plt.subplots`."""
        with pytest.raises(ValueError, match="must be at least 1"):
            plt.Canvas(str(single_text_file), rows_cols=rows_cols, show=False)

    def test_disables_any_active_layout_engine(self, single_text_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A layout engine (auto-enabled by plt.subplots() whenever the caller's own
        rcParams -- unrelated to plotter's own style -- has figure.autolayout or
        figure.constrained_layout.use set) would silently re-run on every render and
        undo Colorbar's manual axes repositioning; Canvas must disable it regardless."""
        monkeypatch.setitem(matplotlib.rcParams, "figure.autolayout", True)

        with plt.Canvas(str(single_text_file), show=False) as canvas:
            assert isinstance(canvas.figure.get_layout_engine(), PlaceHolderLayoutEngine)


class TestAutoLayout:
    """Tests for `Canvas._auto_layout`."""

    def test_runs_tight_layout_once_when_no_colorbar_was_used(self, single_text_file: Path) -> None:
        """A canvas without a Colorbar should get one automatic tight_layout() pass on exit,
        so titles/axis labels don't overlap between subplots."""
        canvas = plt.Canvas(str(single_text_file), show=False)
        figure_type = type(canvas.figure)

        with patch.object(figure_type, "tight_layout", autospec=True) as tight_layout_mock:
            with canvas:
                canvas.setup()

        tight_layout_mock.assert_called_once()

    def test_skips_tight_layout_when_a_colorbar_was_used(self, single_text_file: Path) -> None:
        """tight_layout() recomputes every subplot's position from the gridspec uniformly,
        which would undo a Colorbar's manual shrink/realignment -- it must not run at all
        once a Colorbar has touched the canvas."""
        canvas = plt.Canvas(str(single_text_file), show=False)
        figure_type = type(canvas.figure)

        with patch.object(figure_type, "tight_layout", autospec=True) as tight_layout_mock:
            with canvas:
                canvas.setup()
                image = plt.Image(np.zeros((10, 10)))
                image.draw(canvas)

                colorbar = plt.Colorbar(source=image)
                colorbar.draw(canvas)

                shrunk_position = canvas.axes[0].get_position()

        tight_layout_mock.assert_not_called()
        assert canvas.axes[0].get_position().bounds == pytest.approx(shrunk_position.bounds)

    def test_suppresses_the_incompatible_axes_warning_for_zoom_insets(
        self, single_text_file: Path, recwarn: pytest.WarningsRecorder
    ) -> None:
        """tight_layout() always warns about a ZoomInset panel's Axes (no subplotspec) even
        though it correctly leaves them untouched -- that specific warning should not reach
        the caller."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()
            canvas.add_zoom_inset((0.0, 1.0), (0.0, 1.0))

        assert not any("not compatible with tight_layout" in str(w.message) for w in recwarn.list)


class TestPlotIndices:
    """Tests for `Canvas.plot_indices`."""

    @pytest.mark.parametrize(
        "plot_n, expected",
        [
            (1, [1]),
            ("all", [0, 1, 2]),
            ((0, 1), [0, 1]),
            ((1, 2), [1, 2]),
            ([0, 2], [0, 2]),
            ([2, 0], [0, 2]),
        ],
    )
    def test_resolves_to_the_expected_subplot_indices(
        self, workspace: Path, plot_n: int | tuple[int, int] | list[int] | str, expected: list[int]
    ) -> None:
        """Each supported 'plot_n' form should resolve to its documented indices."""
        with plt.Canvas("plot_indices_labels", (1, 3), show=False) as canvas:
            assert canvas.plot_indices(plot_n) == expected

    def test_rejects_duplicate_indices_in_a_list(self, workspace: Path) -> None:
        """A list 'plot_n' with repeated indices almost certainly signals a mistake."""
        with plt.Canvas("plot_indices_labels_duplicate", (1, 3), show=False) as canvas:
            with pytest.raises(ValueError, match="duplicate"):
                canvas.plot_indices([0, 1, 0])

    def test_rejects_an_invalid_value(self, workspace: Path) -> None:
        """An unsupported 'plot_n' value should fail loudly."""
        with plt.Canvas("plot_indices_labels_invalid", (1, 3), show=False) as canvas:
            with pytest.raises(ValueError, match="not a valid value"):
                canvas.plot_indices("first")

    @pytest.mark.parametrize(
        "row, col, expected",
        [
            (0, None, [0, 1, 2]),
            (1, None, [3, 4, 5]),
            (None, 0, [0, 3]),
            (None, 1, [1, 4]),
            (None, 2, [2, 5]),
        ],
    )
    def test_resolves_row_and_col_against_the_grid(
        self, workspace: Path, row: int | None, col: int | None, expected: list[int]
    ) -> None:
        """'row'/'col' should resolve against the (row-major flattened) `rows_cols` grid."""
        with plt.Canvas("plot_indices_row_col_labels", (2, 3), show=False) as canvas:
            assert canvas.plot_indices(row=row, col=col) == expected

    def test_rejects_more_than_one_of_plot_n_row_col(self, workspace: Path) -> None:
        """Ambiguous targeting (more than one of 'plot_n'/'row'/'col') should fail loudly."""
        with plt.Canvas("plot_indices_ambiguous_labels", (2, 3), show=False) as canvas:
            with pytest.raises(ValueError, match="Exactly one of"):
                canvas.plot_indices(plot_n=0, row=0)

    def test_rejects_none_of_plot_n_row_col(self, workspace: Path) -> None:
        """Targeting nothing at all should fail loudly rather than silently pick a default."""
        with plt.Canvas("plot_indices_none_labels", (2, 3), show=False) as canvas:
            with pytest.raises(ValueError, match="Exactly one of"):
                canvas.plot_indices()

    @pytest.mark.parametrize("row, col", [(2, None), (-1, None), (None, 3), (None, -1)])
    def test_rejects_an_out_of_range_row_or_col(self, workspace: Path, row: int | None, col: int | None) -> None:
        """A 'row'/'col' outside the `rows_cols` grid should fail loudly."""
        with plt.Canvas("plot_indices_out_of_range_labels", (2, 3), show=False) as canvas:
            with pytest.raises(ValueError, match="must be between"):
                canvas.plot_indices(row=row, col=col)


class TestSetup:
    """Tests for `Canvas.setup`."""

    def test_applies_axes_configuration(self, text_file: Path) -> None:
        """Canvas.setup should apply labels, limits, scales, and legend settings."""
        with plt.Canvas(str(text_file), (1, 2), show=False) as canvas:
            canvas.setup(
                plot_n=1,
                xlim=(1.0, 5.0),  # log-scaled below, so the lower bound must stay positive
                ylim=(-1.0, 3.0),
                xscale="log",
                yscale="symlog",
                inverted=(True, False),
                legend=3,
                leg_ncols=2,
            )

            axis = canvas.axes[1]
            assert axis.get_xlim() == pytest.approx((5.0, 1.0))
            assert axis.get_ylim() == pytest.approx((-1.0, 3.0))
            assert axis.get_xscale() == "log"
            assert axis.get_yscale() == "symlog"
            assert axis.get_xlabel() == "$ x $"
            assert axis.get_ylabel() == "$ y $"
            assert axis.get_title() == "Test 2"
            assert canvas._loc_legend[1] == 3
            assert canvas._ncols_legend[1] == 2

    def test_leg_ncols_defaults_to_one(self, text_file: Path) -> None:
        """Without an explicit 'leg_ncols', the legend should default to a single column."""
        with plt.Canvas(str(text_file), (1, 2), show=False) as canvas:
            canvas.setup(plot_n=1, legend=3)

            assert canvas._ncols_legend[1] == 1

    def test_applies_to_all_subplots_by_default(self, text_file: Path) -> None:
        """The default plot_n='all' should configure every subplot."""
        with plt.Canvas(str(text_file), (1, 2), show=False) as canvas:
            canvas.setup(xlim=(0.0, 5.0))

            assert canvas.axes[0].get_xlim() == pytest.approx((0.0, 5.0))
            assert canvas.axes[1].get_xlim() == pytest.approx((0.0, 5.0))

    def test_applies_to_a_range_of_subplots(self, workspace: Path) -> None:
        """A tuple plot_n should configure only the requested inclusive range."""
        with plt.Canvas("setup_range_labels", (1, 3), show=False) as canvas:
            canvas.setup(plot_n=(0, 1), xlim=(0.0, 5.0))

            assert canvas.axes[0].get_xlim() == pytest.approx((0.0, 5.0))
            assert canvas.axes[1].get_xlim() == pytest.approx((0.0, 5.0))
            assert canvas.axes[2].get_xlim() != pytest.approx((0.0, 5.0))

    def test_grid_is_shown_by_default(self, single_text_file: Path) -> None:
        """With no 'nogrid' kwarg, both axes should show a grid."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            axis = canvas.axes[0]
            assert all(line.get_visible() for line in axis.get_xgridlines())
            assert all(line.get_visible() for line in axis.get_ygridlines())

    def test_nogrid_bool_removes_grid_from_both_axes(self, single_text_file: Path) -> None:
        """A bool 'nogrid=True' should remove the grid from both axes."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup(nogrid=True)

            axis = canvas.axes[0]
            assert not any(line.get_visible() for line in axis.get_xgridlines())
            assert not any(line.get_visible() for line in axis.get_ygridlines())

    @pytest.mark.parametrize(
        ("nogrid", "x_visible", "y_visible"),
        [((True, False), False, True), ((False, True), True, False)],
    )
    def test_nogrid_tuple_removes_grid_from_one_axis(
        self, single_text_file: Path, nogrid: tuple[bool, bool], x_visible: bool, y_visible: bool
    ) -> None:
        """A `tuple[bool, bool]` 'nogrid' should independently control the x and y grid."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup(nogrid=nogrid)

            axis = canvas.axes[0]
            assert all(line.get_visible() == x_visible for line in axis.get_xgridlines())
            assert all(line.get_visible() == y_visible for line in axis.get_ygridlines())


class TestDrawLine:
    """Tests for `Canvas.draw_line`."""

    @pytest.mark.parametrize("orientation", ["v", "h"])
    def test_adds_a_single_reference_line(self, single_text_file: Path, orientation: str, show_plots) -> None:
        """Canvas.draw_line should add exactly one line for either supported orientation."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            before = len(canvas.axes[0].lines)

            canvas.draw_line(
                orientation, point=1.5, plot_n=0, color="red", linestyle="--", lw=2.0, alpha=0.5, zorder=5
            )

            line = canvas.axes[0].lines[-1]
            assert len(canvas.axes[0].lines) == before + 1
            assert line.get_color() == "red"
            assert line.get_linestyle() == "--"
            assert line.get_linewidth() == pytest.approx(2.0)
            assert line.get_alpha() == pytest.approx(0.5)
            assert line.get_zorder() == pytest.approx(5)

    @pytest.mark.parametrize("orientation", ["v", "h"])
    def test_zorder_defaults_to_two(self, single_text_file: Path, orientation: str, show_plots) -> None:
        """Without an explicit `zorder`, the reference line should default to 2."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.draw_line(orientation, point=1.5, plot_n=0)

            assert canvas.axes[0].lines[-1].get_zorder() == pytest.approx(2)

    def test_rejects_invalid_orientation(self, single_text_file: Path) -> None:
        """draw_line should fail loudly on an unsupported orientation."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="Invalid line type"):
                canvas.draw_line("diagonal")

    def test_can_draw_on_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should add the line to every subplot."""
        with plt.Canvas("draw_line_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.draw_line("h", point=1.5, plot_n="all", color="red")

            assert all(axis.lines[-1].get_color() == "red" for axis in canvas.axes)


class TestDrawBand:
    """Tests for `Canvas.draw_band`."""

    @pytest.mark.parametrize("orientation", ["v", "h"])
    def test_adds_a_single_shaded_band(self, single_text_file: Path, orientation: str, show_plots) -> None:
        """Canvas.draw_band should add exactly one shaded region for either supported orientation."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            before = len(canvas.axes[0].patches)

            canvas.draw_band(orientation, low=1.0, high=2.0, plot_n=0, color="red", linestyle="--", lw=2.0, alpha=0.3)

            band = canvas.axes[0].patches[-1]
            assert len(canvas.axes[0].patches) == before + 1
            assert to_rgb(band.get_facecolor()) == to_rgb("red")
            assert band.get_linewidth() == pytest.approx(2.0)
            assert band.get_alpha() == pytest.approx(0.3)

            bbox = band.get_bbox()
            extent = (bbox.x0, bbox.x1) if orientation == "v" else (bbox.y0, bbox.y1)
            assert extent == pytest.approx((1.0, 2.0))

    def test_rejects_invalid_orientation(self, single_text_file: Path) -> None:
        """draw_band should fail loudly on an unsupported orientation."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="Invalid band type"):
                canvas.draw_band("diagonal", low=0.0, high=1.0)

    def test_can_draw_on_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should add the band to every subplot."""
        with plt.Canvas("draw_band_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.draw_band("h", low=1.0, high=2.0, plot_n="all", color="red")

            assert all(to_rgb(axis.patches[-1].get_facecolor()) == to_rgb("red") for axis in canvas.axes)


class TestAddText:
    """Tests for `Canvas.add_text`."""

    def test_places_a_label_without_an_arrow(self, single_text_file: Path, show_plots) -> None:
        """Canvas.add_text should add a plain text artist at the requested position."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            before = len(canvas.axes[0].texts)

            canvas.add_text("Note", position=(0.25, 0.75), plot_n=0, color="green", fontsize=14)

            annotation = canvas.axes[0].texts[-1]
            assert len(canvas.axes[0].texts) == before + 1
            assert annotation.get_text() == "Note"
            assert annotation.get_position() == pytest.approx((0.25, 0.75))
            assert annotation.get_color() == "green"
            assert annotation.get_fontsize() == pytest.approx(14)
            assert getattr(annotation, "arrow_patch", None) is None

    def test_can_annotate_a_point_with_an_arrow(self, single_text_file: Path, show_plots) -> None:
        """Canvas.add_text should support arrowed annotations to a user-specified point."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_text(
                "Target",
                position=(0.2, 0.8),
                point=(0.75, 0.25),
                plot_n=0,
                arrowprops={"arrowstyle": "->", "color": "red"},
            )

            annotation = canvas.axes[0].texts[-1]
            assert annotation.get_text() == "Target"
            assert annotation.get_position() == pytest.approx((0.2, 0.8))
            assert annotation.xy == pytest.approx((0.75, 0.25))
            assert annotation.arrow_patch is not None
            assert annotation.arrow_patch.get_edgecolor()[:3] == pytest.approx((1.0, 0.0, 0.0))

    def test_can_add_text_to_a_range_of_subplots(self, workspace: Path) -> None:
        """A tuple plot_n should add the text to only the requested inclusive range."""
        with plt.Canvas("add_text_range_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.add_text("Note", position=(0.25, 0.75), plot_n=(0, 1))

            assert [t.get_text() for t in canvas.axes[0].texts] == ["Note"]
            assert [t.get_text() for t in canvas.axes[1].texts] == ["Note"]
            assert len(canvas.axes[2].texts) == 0


class TestAddPoint:
    """Tests for `Canvas.add_point`."""

    def test_draws_a_single_marker(self, single_text_file: Path, show_plots) -> None:
        """Canvas.add_point should add exactly one marker with the requested styling."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            before = len(canvas.axes[0].lines)

            canvas.add_point((1.0, 2.0), plot_n=0, marker="x", color="red", markersize=12.0, alpha=0.5)

            marker = canvas.axes[0].lines[-1]
            assert len(canvas.axes[0].lines) == before + 1
            assert marker.get_data() == pytest.approx(([1.0], [2.0]))
            assert marker.get_marker() == "x"
            assert marker.get_color() == "red"
            assert marker.get_markersize() == pytest.approx(12.0)
            assert marker.get_alpha() == pytest.approx(0.5)
            assert marker.get_linestyle() == "None"

    def test_omits_the_label_by_default(self, single_text_file: Path) -> None:
        """Without a 'label', no text artist should be added."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()
            before = len(canvas.axes[0].texts)

            canvas.add_point((1.0, 2.0), plot_n=0)

            assert len(canvas.axes[0].texts) == before

    def test_adds_an_offset_label_when_requested(self, single_text_file: Path, show_plots) -> None:
        """A 'label' should be drawn as an annotation offset from the point, with its own styling."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_point(
                (1.0, 2.0), label="P1", plot_n=0, label_color="blue", label_fontsize=14, label_ha="right", label_va="top"
            )

            annotation = canvas.axes[0].texts[-1]
            assert annotation.get_text() == "P1"
            assert annotation.xy == pytest.approx((1.0, 2.0))
            assert annotation.xyann == pytest.approx((10, 10))
            assert annotation.get_color() == "blue"
            assert annotation.get_fontsize() == pytest.approx(14)
            assert annotation.get_ha() == "right"
            assert annotation.get_va() == "top"

    def test_can_customize_the_label_offset(self, single_text_file: Path, show_plots) -> None:
        """label_offset should override the default (10, 10) points offset."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_point((1.0, 2.0), label="P1", plot_n=0, label_offset=(-20, 5))

            annotation = canvas.axes[0].texts[-1]
            assert annotation.xyann == pytest.approx((-20, 5))

    def test_omits_the_arrow_by_default(self, single_text_file: Path) -> None:
        """Without 'label_arrow', the label should have no connector arrow."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            canvas.add_point((1.0, 2.0), label="P1", plot_n=0)

            assert canvas.axes[0].texts[-1].arrow_patch is None

    def test_adds_a_default_arrow_when_requested(self, single_text_file: Path, show_plots) -> None:
        """label_arrow=True should draw a default '->' arrow from the label to the point."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_point((1.0, 2.0), label="P1", plot_n=0, label_arrow=True)

            assert canvas.axes[0].texts[-1].arrow_patch is not None

    def test_can_customize_the_arrow_style(self, single_text_file: Path, show_plots) -> None:
        """label_arrow accepts a dict of arrowprops to style the connector arrow."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_point((1.0, 2.0), label="P1", plot_n=0, label_arrow={"arrowstyle": "-|>", "color": "red"})

            arrow_patch = canvas.axes[0].texts[-1].arrow_patch
            assert arrow_patch is not None
            assert arrow_patch.get_edgecolor()[:3] == pytest.approx((1.0, 0.0, 0.0))

    def test_can_draw_on_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should add the point to every subplot."""
        with plt.Canvas("add_point_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.add_point((1.0, 2.0), plot_n="all", color="red")

            assert all(axis.lines[-1].get_color() == "red" for axis in canvas.axes)


class TestTurnScientific:
    """Tests for `Canvas.turn_scientific`."""

    def test_rejects_invalid_axis(self, single_text_file: Path) -> None:
        """turn_scientific should fail loudly on an unsupported axis value."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="is not a valid axis"):
                canvas.turn_scientific("z")

    def test_can_apply_to_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should switch every subplot's axis to scientific notation."""
        with plt.Canvas("turn_scientific_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.turn_scientific("y", plot_n="all")

            assert all(axis.yaxis.get_major_formatter()._scientific for axis in canvas.axes)


class TestSetTicks:
    """Tests for `Canvas.set_ticks`."""

    def test_updates_positions_and_labels(self, single_text_file: Path, show_plots) -> None:
        """set_ticks should update both the tick positions and their labels."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.set_ticks("x", (0.0, 1.0), labels=("left", "right"))
            canvas.set_ticks("y", (1.0, 2.0))

            axis = canvas.axes[0]
            assert list(axis.get_xticks()) == [0.0, 1.0]
            assert [label.get_text() for label in axis.get_xticklabels()] == ["left", "right"]
            assert list(axis.get_yticks()) == [1.0, 2.0]

    def test_rejects_invalid_axis(self, single_text_file: Path) -> None:
        """set_ticks should fail loudly on an unsupported axis value."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="Invalid axis type"):
                canvas.set_ticks("z", (0.0, 1.0))

    def test_can_update_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should update the ticks of every subplot."""
        with plt.Canvas("set_ticks_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.set_ticks("x", (0.0, 1.0), labels=("left", "right"), plot_n="all")

            for axis in canvas.axes:
                assert list(axis.get_xticks()) == [0.0, 1.0]
                assert [label.get_text() for label in axis.get_xticklabels()] == ["left", "right"]


class TestRemoveTicks:
    """Tests for `Canvas.remove_ticks`."""

    def test_clears_positions_and_labels(self, single_text_file: Path, show_plots) -> None:
        """remove_ticks should clear both the tick positions and their labels."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.set_ticks("x", (0.0, 1.0), labels=("left", "right"))
            canvas.remove_ticks("x")

            axis = canvas.axes[0]
            assert list(axis.get_xticks()) == []
            assert axis.get_xticklabels() == []

    def test_both_clears_x_and_y(self, single_text_file: Path) -> None:
        """axis='both' should clear ticks on both axes at once."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            canvas.remove_ticks("both")

            axis = canvas.axes[0]
            assert list(axis.get_xticks()) == []
            assert list(axis.get_yticks()) == []

    def test_rejects_invalid_axis(self, single_text_file: Path) -> None:
        """remove_ticks should fail loudly on an unsupported axis value."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="is not a valid axis"):
                canvas.remove_ticks("z")

    def test_can_clear_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should clear the ticks of every subplot."""
        with plt.Canvas("remove_ticks_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.remove_ticks("both", plot_n="all")

            for axis in canvas.axes:
                assert list(axis.get_xticks()) == []
                assert list(axis.get_yticks()) == []


class TestAddScalebar:
    """Tests for `Canvas.add_scalebar`."""

    def test_adds_a_scalebar_and_clears_the_ticks(self, single_text_file: Path, show_plots) -> None:
        """Adding a scalebar should remove the axis ticks and add one artist."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_scalebar(size=0.5, label="5 um")

            axis = canvas.axes[0]
            assert list(axis.get_xticks()) == []
            assert list(axis.get_yticks()) == []
            assert len(axis.artists) == 1

    def test_can_add_a_scalebar_to_every_subplot_at_once(self, workspace: Path) -> None:
        """plot_n='all' should add a scalebar to every subplot."""
        with plt.Canvas("add_scalebar_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            canvas.add_scalebar(size=0.5, label="5 um", plot_n="all")

            assert all(len(axis.artists) == 1 for axis in canvas.axes)

    def test_can_place_the_scalebar_at_a_precise_axes_fraction_position(self, single_text_file: Path, show_plots) -> None:
        """A location tuple should center the scalebar on that axes-fraction point, rather than a named corner."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            canvas.add_scalebar(size=0.5, label="5 um", location=(0.3, 0.7))

            axis = canvas.axes[0]
            scalebar = axis.artists[0]
            canvas.figure.canvas.draw()

            assert scalebar.loc == AnchoredOffsetbox.codes["center"]
            anchor_bbox = scalebar.get_bbox_to_anchor()
            expected_x, expected_y = axis.transAxes.transform((0.3, 0.7))
            assert (anchor_bbox.x0, anchor_bbox.y0) == pytest.approx((expected_x, expected_y))


class TestAddZoomInset:
    """Tests for `Canvas.add_zoom_inset`."""

    def test_returns_a_zoom_inset_with_the_requested_view(self, single_text_file: Path, show_plots) -> None:
        """add_zoom_inset should return a panel showing the requested region on its own Axes."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            assert isinstance(inset, plt.ZoomInset)
            assert inset.axes[0] is not canvas.axes[0]
            assert inset.figure is canvas.figure
            assert inset.axes[0].get_xlim() == pytest.approx((1.0, 2.0))
            assert inset.axes[0].get_ylim() == pytest.approx((0.0, 1.0))

    def test_matches_the_source_axes_inverted_direction(self, single_text_file: Path, show_plots) -> None:
        """If the source subplot's axis is inverted (e.g. an image's y-axis), the inset's
        requested limits should be applied in that same direction, not the literal order
        passed in, so the zoomed content isn't mirrored."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup(inverted=(True, False))  # x inverted, y left as-is

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            assert inset.axes[0].get_xlim() == pytest.approx((2.0, 1.0))
            assert inset.axes[0].get_ylim() == pytest.approx((0.0, 1.0))

    def test_keeps_loc1_loc2_pointing_at_the_same_visual_corner_when_inverted(self, single_text_file: Path, show_plots) -> None:
        """loc1/loc2 should still reference the same visual corner even on an inverted axis,
        on both ends of each connector line: the inset panel's own on-screen box is never
        inverted (so its end keeps the original code), only the rectangle on the source
        subplot is (so its end gets remapped)."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup(inverted=(True, False))  # x inverted, y left as-is

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0), loc1=1, loc2=3)

            connectors = [p for p in inset.axes[0].patches if isinstance(p, plt.canvas.BboxConnector)]
            assert len(connectors) == 2
            assert {c.loc1 for c in connectors} == {1, 3}  # inset panel side: unchanged
            assert {c.loc2 for c in connectors} == {2, 4}  # rectangle side: remapped (x inverted)

    def test_hides_ticks_by_default(self, single_text_file: Path, show_plots) -> None:
        """The inset panel should show no tick marks or labels unless requested."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            assert list(inset.axes[0].get_xticks()) == []
            assert list(inset.axes[0].get_yticks()) == []

    def test_keeps_ticks_when_requested(self, single_text_file: Path, show_plots) -> None:
        """Passing ticks=True should keep the inset panel's tick marks and labels."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0), ticks=True)

            assert list(inset.axes[0].get_xticks()) != []
            assert list(inset.axes[0].get_yticks()) != []

    def test_draws_an_indicator_on_the_source_axes(self, single_text_file: Path, show_plots) -> None:
        """add_zoom_inset should mark the zoomed region on the source subplot."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            axis = canvas.axes[0]
            before = len(axis.patches)

            canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            assert len(axis.patches) > before

    def test_a_drawable_can_be_drawn_into_the_returned_panel(self, single_text_file: Path, show_plots) -> None:
        """The panel should accept Drawable objects exactly like a real Canvas subplot."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))
            plt.LinePlot(x=np.array([1.0, 1.5, 2.0]), y=np.array([0.1, 0.5, 0.9])).draw(inset)

            assert len(inset.axes[0].lines) == 1

    def test_applies_matching_default_color_and_width_to_rectangle_lines_and_outline(
        self, single_text_file: Path, show_plots
    ) -> None:
        """With no edgecolor/linewidth given, the rectangle, connector lines, and the
        inset panel's own outline (its Axes spines) should all share the same defaults."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            axis = canvas.axes[0]

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            rect = next(p for p in axis.patches if isinstance(p, plt.canvas.BboxPatch))
            connectors = [p for p in inset.axes[0].patches if isinstance(p, plt.canvas.BboxConnector)]
            spines = inset.axes[0].spines.values()

            assert rect.get_edgecolor()[:3] == pytest.approx(to_rgb("black"))
            assert rect.get_linewidth() == pytest.approx(0.5)
            for connector in connectors:
                assert connector.get_edgecolor()[:3] == pytest.approx(to_rgb("black"))
                assert connector.get_linewidth() == pytest.approx(0.5)
            for spine in spines:
                assert spine.get_edgecolor()[:3] == pytest.approx(to_rgb("black"))
                assert spine.get_linewidth() == pytest.approx(0.5)

    def test_applies_matching_custom_color_and_width_to_rectangle_lines_and_outline(
        self, single_text_file: Path, show_plots
    ) -> None:
        """Passing edgecolor/linewidth should restyle the rectangle, connector lines, and
        the inset panel's own outline identically."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            axis = canvas.axes[0]

            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0), edgecolor="red", linewidth=2.5)

            rect = next(p for p in axis.patches if isinstance(p, plt.canvas.BboxPatch))
            connectors = [p for p in inset.axes[0].patches if isinstance(p, plt.canvas.BboxConnector)]
            spines = inset.axes[0].spines.values()

            assert rect.get_edgecolor()[:3] == pytest.approx(to_rgb("red"))
            assert rect.get_linewidth() == pytest.approx(2.5)
            for connector in connectors:
                assert connector.get_edgecolor()[:3] == pytest.approx(to_rgb("red"))
                assert connector.get_linewidth() == pytest.approx(2.5)
            for spine in spines:
                assert spine.get_edgecolor()[:3] == pytest.approx(to_rgb("red"))
                assert spine.get_linewidth() == pytest.approx(2.5)

    def test_returns_one_panel_per_subplot_when_targeting_multiple(self, workspace: Path) -> None:
        """plot_n='all' should add an inset to every subplot and return one panel each."""
        with plt.Canvas("add_zoom_inset_all_labels", (1, 3), show=False) as canvas:
            canvas.setup()

            insets = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0), plot_n="all")

            assert isinstance(insets, list)
            assert len(insets) == 3
            assert all(isinstance(inset, plt.ZoomInset) for inset in insets)
            assert len({id(inset.axes[0]) for inset in insets}) == 3


class TestZoomInsetSetup:
    """Tests for `ZoomInset.setup`."""

    def test_applies_axes_configuration(self, single_text_file: Path, show_plots) -> None:
        """ZoomInset.setup should apply limits and scales to the panel's own Axes."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            inset.setup(
                xlim=(0.0, 5.0),
                ylim=(-1.0, 3.0),
                xscale="log",
                yscale="symlog",
                inverted=(True, False),
            )

            axis = inset.axes[0]
            assert axis.get_xlim() == pytest.approx((5.0, 0.0))
            assert axis.get_ylim() == pytest.approx((-1.0, 3.0))
            assert axis.get_xscale() == "log"
            assert axis.get_yscale() == "symlog"


class TestZoomInsetDrawLine:
    """Tests for `ZoomInset.draw_line`."""

    @pytest.mark.parametrize("orientation", ["v", "h"])
    def test_adds_a_single_reference_line(self, single_text_file: Path, orientation: str, show_plots) -> None:
        """ZoomInset.draw_line should add exactly one line for either supported orientation."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))
            before = len(inset.axes[0].lines)

            inset.draw_line(orientation, point=1.5, color="red", linestyle="--", lw=2.0, alpha=0.5, zorder=5)

            line = inset.axes[0].lines[-1]
            assert len(inset.axes[0].lines) == before + 1
            assert line.get_color() == "red"
            assert line.get_linestyle() == "--"
            assert line.get_linewidth() == pytest.approx(2.0)
            assert line.get_alpha() == pytest.approx(0.5)
            assert line.get_zorder() == pytest.approx(5)

    @pytest.mark.parametrize("orientation", ["v", "h"])
    def test_zorder_defaults_to_two(self, single_text_file: Path, orientation: str, show_plots) -> None:
        """Without an explicit `zorder`, the reference line should default to 2."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            inset.draw_line(orientation, point=1.5)

            assert inset.axes[0].lines[-1].get_zorder() == pytest.approx(2)

    def test_rejects_invalid_orientation(self, single_text_file: Path, show_plots) -> None:
        """draw_line should fail loudly on an unsupported orientation."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            inset = canvas.add_zoom_inset(xlim=(1.0, 2.0), ylim=(0.0, 1.0))

            with pytest.raises(ValueError, match="Invalid line type"):
                inset.draw_line("diagonal")
