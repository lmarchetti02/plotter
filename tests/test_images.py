import numpy as np

import plotter as plt


def test_hist2d(tmp_path):
    text_file = str(tmp_path / "hist")
    with plt.Canvas(text_file) as canvas:
        canvas.setup(nogrid=True)

        img = np.zeros((500, 500))
        img[200:300, 200:300] = 1

        plt.Image(img).draw(canvas, label="Image")
