"""Tests for image validation and rendering."""

import numpy as np
import pytest

import plotter as plt


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (np.zeros((2, 2, 2, 2)), "2D or 3D array"),
        (np.zeros((2, 2, 2)), "third axes must contain 3"),
        (np.array([[1 + 1j, 2 + 0j]]), "has to be real"),
    ],
)
def test_image_rejects_invalid_input(data: np.ndarray, message: str) -> None:
    """Image should validate dimensionality, channel count, and real-valued input."""
    with pytest.raises(ValueError, match=message):
        plt.Image(data)


def test_image_draw_can_add_a_labeled_colorbar(single_text_file) -> None:
    """A grayscale image with a label should create a matching colorbar."""
    img = np.zeros((50, 50))
    img[20:30, 20:30] = 1.0

    with plt.Canvas(str(single_text_file), show=False) as canvas:
        canvas.setup(nogrid=True)
        image = plt.Image(img)

        image.draw(canvas, label="Intensity", colorbar={"position": "right", "size": "5%", "padding": 0.1})

        assert canvas.counters.images[0] == 1
        assert len(canvas.figure.axes) == 2
        assert canvas.figure.axes[1].get_ylabel() == "Intensity"
