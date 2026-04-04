from json import dumps
from pathlib import Path

import plotter as plt

TEST_DATA = [
    {
        "title": "Test 1",
        "x_label": "$ x $",
        "y_label": "$ y $",
        "scatter_plots": ["data"],
        "line_plots": ["line"],
        "histograms": ["hist"],
        "histograms_2d": ["hist"],
        "images": ["img1", "img2"],
    },
    {
        "title": "Test 2",
        "x_label": "$ x $",
        "y_label": "$ y $",
        "scatter_plots": ["data1", "data2"],
        "line_plots": ["line"],
        "histograms": ["hist1", "hist2", "hist3"],
        "histograms_2d": [""],
        "images": [""],
    },
]


def test_counters():
    counters = plt.canvas._Counters.initialize_counters(2)
    assert counters.is_empty()

    counters.histograms_2d[0] += 1
    counters.images[1] += 1
    assert not counters.is_empty()


def test_basic(tmp_path):
    plt.setup_workspace(tmp_path)

    text_file: Path = tmp_path / "plotter/labels.json"
    text_file.write_text(dumps(TEST_DATA))

    with plt.Canvas(str(text_file), (1, 2)) as canvas:
        canvas.setup("all")
