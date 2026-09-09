"""Tests for canvas setup and drawing helpers."""

from pathlib import Path
from warnings import warn

import numpy as np
import pytest

import plotter as plt


class TestCounters:
    """Tests for `_Counters`."""

    def test_initializes_with_one_slot_per_subplot(self) -> None:
        """Counters should start empty and track each drawable family independently."""
        counters = plt.canvas._Counters.initialize_counters(2)

        for name in plt.Drawable.get_label_names():
            assert getattr(counters, name) == [0, 0]

        assert counters.is_empty()

        counters.histograms_2d[0] += 1
        counters.images[1] += 1

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


class TestSetup:
    """Tests for `Canvas.setup`."""

    def test_applies_axes_configuration(self, text_file: Path) -> None:
        """Canvas.setup should apply labels, limits, scales, and legend settings."""
        with plt.Canvas(str(text_file), (1, 2), show=False) as canvas:
            canvas.setup(
                plot_n=1,
                xlim=(0.0, 5.0),
                ylim=(-1.0, 3.0),
                xscale="log",
                yscale="symlog",
                inverted=(True, False),
                legend=3,
            )

            axis = canvas.axes[1]
            assert axis.get_xlim() == pytest.approx((5.0, 0.0))
            assert axis.get_ylim() == pytest.approx((-1.0, 3.0))
            assert axis.get_xscale() == "log"
            assert axis.get_yscale() == "symlog"
            assert axis.get_xlabel() == "$ x $"
            assert axis.get_ylabel() == "$ y $"
            assert axis.get_title() == "Test 2"
            assert canvas._loc_legend[1] == 3


class TestDrawLine:
    """Tests for `Canvas.draw_line`."""

    @pytest.mark.parametrize("orientation", ["v", "h"])
    def test_adds_a_single_reference_line(self, single_text_file: Path, orientation: str, show_plots) -> None:
        """Canvas.draw_line should add exactly one line for either supported orientation."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            before = len(canvas.axes[0].lines)

            canvas.draw_line(orientation, point=1.5, plot_n=0, color="red", linestyle="--", lw=2.0)

            line = canvas.axes[0].lines[-1]
            assert len(canvas.axes[0].lines) == before + 1
            assert line.get_color() == "red"
            assert line.get_linestyle() == "--"
            assert line.get_linewidth() == pytest.approx(2.0)

    def test_rejects_invalid_orientation(self, single_text_file: Path) -> None:
        """draw_line should fail loudly on an unsupported orientation."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="Invalid line type"):
                canvas.draw_line("diagonal")


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


class TestTurnScientific:
    """Tests for `Canvas.turn_scientific`."""

    def test_rejects_invalid_axis(self, single_text_file: Path) -> None:
        """turn_scientific should fail loudly on an unsupported axis value."""
        with plt.Canvas(str(single_text_file), show=False) as canvas:
            canvas.setup()

            with pytest.raises(ValueError, match="is not a valid axis"):
                canvas.turn_scientific("z")


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
            plt.LinePlot(x=np.array([1.0, 1.5, 2.0]), f=np.array([0.1, 0.5, 0.9])).draw(inset)

            assert len(inset.axes[0].lines) == 1


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
