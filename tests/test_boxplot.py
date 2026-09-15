"""Tests for box plot validation and drawing."""

import numpy as np
import pytest
from matplotlib.colors import to_rgba

import plotter as plt


class TestBoxPlot:
    """Tests for `BoxPlot`."""

    def test_rejects_empty_data(self) -> None:
        """BoxPlot should reject an empty group of boxes."""
        with pytest.raises(ValueError, match="data must contain at least one group"):
            plt.BoxPlot([])

    def test_rejects_mismatched_positions_length(self) -> None:
        """BoxPlot should validate that positions and data have the same length."""
        data = [np.array([1.0, 2.0, 3.0]), np.array([2.0, 3.0])]
        with pytest.raises(ValueError, match="positions and data must have the same length"):
            plt.BoxPlot(data, positions=np.array([0.0]))


class TestDraw:
    """Tests for `BoxPlot.draw`."""

    def test_uses_canvas_labels_and_updates_counters(self, single_text_file, show_plots) -> None:
        """Drawing a box plot without an explicit label should consume the canvas metadata."""
        data = [np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([2.0, 3.0, 4.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas)

            assert canvas.counters.box_plots[0] == 1
            assert len(boxes.bxp["boxes"]) == 2
            # The first (and only) group on this subplot also picks up the automatic
            # "Median"/"Mean" legend entries, alongside its own JSON label.
            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["boxes", "Median", "Mean"]

    def test_respects_styling_arguments(self, single_text_file, show_plots) -> None:
        """BoxPlot should forward color and edge styling to matplotlib's patch artists."""
        data = [np.array([1.0, 2.0, 3.0]), np.array([2.0, 3.0, 4.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas, color="red", edgecolor="black", alpha=0.5, lw=2.0)

            box_patch = boxes.bxp["boxes"][0]
            # `alpha` is baked into the facecolor only, so the edge stays fully opaque.
            assert to_rgba(box_patch.get_facecolor()) == to_rgba("red", alpha=0.5)
            assert to_rgba(box_patch.get_edgecolor()) == to_rgba("black")
            assert box_patch.get_linewidth() == pytest.approx(2.0)

    def test_tick_labels_passthrough_sets_xtick_text(self, single_text_file, show_plots) -> None:
        """`tick_labels` should set the per-box category text under each box."""
        data = [np.array([1.0, 2.0]), np.array([3.0, 4.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas, tick_labels=["A", "B"])

            texts = [text.get_text() for text in canvas.axes[0].get_xticklabels()]
            assert texts == ["A", "B"]

    def test_positions_default_to_matplotlibs_own_numbering(self, single_text_file, show_plots) -> None:
        """Without an explicit `positions`, boxes fall back to matplotlib's own 1..N placement."""
        data = [np.array([1.0, 2.0]), np.array([3.0, 4.0]), np.array([5.0, 6.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas)

            xticks = canvas.axes[0].get_xticks()
            assert list(xticks) == [1.0, 2.0, 3.0]

    def test_patch_artist_false_falls_back_to_line_boxes(self, single_text_file, show_plots) -> None:
        """`patch_artist=False` should draw unfilled Line2D boxes instead of crashing."""
        data = [np.array([1.0, 2.0, 3.0]), np.array([2.0, 3.0, 4.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas, patch_artist=False, edgecolor="green")

            box_line = boxes.bxp["boxes"][0]
            assert type(box_line).__name__ == "Line2D"
            assert to_rgba(box_line.get_color()) == to_rgba("green")

    def test_group_label_stays_on_the_box_even_without_a_patch(self, single_text_file, show_plots) -> None:
        """The group's own label should attach to the box artist, not the median line,
        even when `patch_artist=False` puts matplotlib's own median/box heuristic aside."""
        data = [np.array([1.0, 2.0, 3.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas, patch_artist=False, label="boxes")

            assert boxes.bxp["boxes"][0].get_label() == "boxes"
            assert boxes.bxp["medians"][0].get_label() == "Median"

    def test_median_and_mean_lines_default_to_firebrick_solid_and_orange_dashed(self, single_text_file, show_plots) -> None:
        """The mean line is shown by default, alongside the median, with distinct styling."""
        data = [np.array([1.0, 2.0, 3.0, 4.0, 5.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas)

            median_line = boxes.bxp["medians"][0]
            mean_line = boxes.bxp["means"][0]
            assert to_rgba(median_line.get_color()) == to_rgba("firebrick")
            assert median_line.get_linestyle() == "-"
            assert to_rgba(mean_line.get_color()) == to_rgba("orange")
            assert mean_line.get_linestyle() == "--"

    def test_median_and_mean_colors_are_overridable(self, single_text_file, show_plots) -> None:
        """`median_color`/`mean_color` should override the default line colors."""
        data = [np.array([1.0, 2.0, 3.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas, median_color="black", mean_color="purple")

            assert to_rgba(boxes.bxp["medians"][0].get_color()) == to_rgba("black")
            assert to_rgba(boxes.bxp["means"][0].get_color()) == to_rgba("purple")

    def test_only_the_first_group_on_a_subplot_gets_median_and_mean_legend_entries(self, single_text_file, show_plots) -> None:
        """Drawing several groups on the same subplot shouldn't duplicate the "Median"/"Mean" entries."""
        data = [np.array([1.0, 2.0, 3.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            plt.BoxPlot(data, positions=np.array([0.0])).draw(canvas, label="first")
            plt.BoxPlot(data, positions=np.array([1.0])).draw(canvas, label="second")

            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["first", "Median", "Mean", "second"]

    def test_showmeans_false_omits_the_mean_legend_entry(self, single_text_file, show_plots) -> None:
        """Disabling `showmeans` should skip the automatic "Mean" legend entry."""
        data = [np.array([1.0, 2.0, 3.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas, showmeans=False)

            assert boxes.bxp["means"] == []
            _, labels = canvas.axes[0].get_legend_handles_labels()
            assert labels == ["boxes", "Median"]

    def test_bxp_exposes_every_artist_family(self, single_text_file, show_plots) -> None:
        """`bxp` should hold the full artist dict returned by `Axes.boxplot` for further styling."""
        data = [np.array([1.0, 2.0, 3.0])]

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            boxes = plt.BoxPlot(data)

            boxes.draw(canvas)

            assert set(boxes.bxp.keys()) == {"boxes", "medians", "whiskers", "caps", "fliers", "means"}
