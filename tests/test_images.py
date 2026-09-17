"""Tests for image validation and rendering."""

import numpy as np
import pytest
from matplotlib.image import AxesImage

import plotter as plt


class TestImage:
    """Tests for `Image`."""

    @pytest.mark.parametrize(
        ("data", "message"),
        [
            (np.zeros((2, 2, 2, 2)), "2D or 3D array"),
            (np.zeros((2, 2, 2)), "third axes must contain 3"),
            (np.array([[1 + 1j, 2 + 0j]]), "has to be real"),
        ],
    )
    def test_rejects_invalid_input(self, data: np.ndarray, message: str) -> None:
        """Image should validate dimensionality, channel count, and real-valued input."""
        with pytest.raises(ValueError, match=message):
            plt.Image(data)


class TestDraw:
    """Tests for `Image.draw`."""

    def test_exposes_its_mappable_without_creating_a_colorbar(self, single_text_file, show_plots) -> None:
        """Drawing an image should expose its AxesImage as `mappable` and never draw a colorbar implicitly."""
        img = np.zeros((50, 50))
        img[20:30, 20:30] = 1.0

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup(nogrid=True)
            image = plt.Image(img)

            image.draw(canvas)

            assert isinstance(image.mappable, AxesImage)
            assert len(canvas.figure.axes) == 1

    def test_applies_an_explicit_v_range(self, single_text_file, show_plots) -> None:
        """An explicit v_range should clip the color scale without erroring."""
        img = np.linspace(0.0, 10.0, 100).reshape(10, 10)

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup(nogrid=True)
            image = plt.Image(img)

            image.draw(canvas, v_range=(2.0, 8.0))

            assert image.mappable.norm.vmin == pytest.approx(2.0)
            assert image.mappable.norm.vmax == pytest.approx(8.0)

    @pytest.mark.parametrize(
        "log",
        [True, (True, 1.0)],
        ids=["log", "symlog"],
    )
    def test_applies_an_explicit_v_range_under_log_scales(self, single_text_file, show_plots, log: bool | tuple[bool, float]) -> None:
        """An explicit v_range should still clip the color scale when combined with `log` or `symlog`."""
        img = np.linspace(0.1, 10.0, 100).reshape(10, 10)

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup(nogrid=True)
            image = plt.Image(img)

            image.draw(canvas, log=log, v_range=(2.0, 8.0))

            assert image.mappable.norm.vmin == pytest.approx(2.0)
            assert image.mappable.norm.vmax == pytest.approx(8.0)

    @pytest.mark.parametrize("channels", [None, 3, 4], ids=["grayscale", "rgb", "rgba"])
    def test_auto_crops_full_resolution_data_into_a_zoom_inset(self, single_text_file, show_plots, channels: int | None) -> None:
        """Drawing the same full-resolution array into a ZoomInset should crop it to the
        panel's requested region and place it at matching axis limits, with no `limits=`
        needed -- for grayscale, RGB, and RGBA data alike (the channel axis, if any,
        must be carried through the crop untouched)."""
        shape = (10, 10) if channels is None else (10, 10, channels)
        data = np.arange(np.prod(shape)).reshape(shape) / np.prod(shape)

        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            inset = canvas.add_zoom_inset(xlim=(2, 5), ylim=(1, 4))

            plt.Image(data).draw(inset)

            drawn = inset.axes[0].images[0]
            assert np.array_equal(drawn.get_array(), data[1:4, 2:5])
            assert drawn.get_extent() == pytest.approx((2.0, 5.0, 1.0, 4.0))

    def test_explicit_limits_bypass_auto_crop_in_a_zoom_inset(self, single_text_file, show_plots) -> None:
        """Passing limits= explicitly should draw the given data as-is, without auto-cropping."""
        with plt.Canvas(str(single_text_file), show=show_plots) as canvas:
            canvas.setup()
            inset = canvas.add_zoom_inset(xlim=(2, 5), ylim=(1, 4))

            pre_cropped = np.ones((3, 3))
            plt.Image(pre_cropped).draw(inset, limits=[2, 5, 1, 4])

            drawn = inset.axes[0].images[0]
            assert np.array_equal(drawn.get_array(), pre_cropped)
            assert drawn.get_extent() == pytest.approx((2.0, 5.0, 1.0, 4.0))
