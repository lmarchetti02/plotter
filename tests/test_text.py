from json import dumps

from plotter.text import PlotText, Text

TEST_DATA = [
    {
        "title": "Test 1",
        "x_label": "$ x $",
        "y_label": "$ y $",
        "scatter_plots": ["data"],
        "line_plots": ["line"],
        "histograms": ["hist"],
        "images": ["img1", "img2"],
    },
    {
        "title": "Test 2",
        "x_label": "$ x $",
        "y_label": "$ y $",
        "scatter_plots": ["data1", "data2"],
        "line_plots": ["line"],
        "histograms": ["hist1", "hist2", "hist3"],
        "images": [""],
    },
]


def test_plot_text():
    empty_obj = PlotText.get_empy_text()
    assert empty_obj.title == ""
    assert empty_obj.x_label == ""
    assert empty_obj.y_label == ""
    assert empty_obj.scatter_plots == [""]
    assert empty_obj.line_plots == [""]
    assert empty_obj.histograms == [""]
    assert empty_obj.images == [""]


def test_text(tmp_path):
    test_file = tmp_path / "test_text.json"
    test_file.write_text(dumps(TEST_DATA))

    text1 = Text(len(TEST_DATA))
    text1.read_json(str(test_file))

    # check automatic .json extension
    text2 = Text(len(TEST_DATA))
    text2.read_json(str(test_file)[:-5])

    assert text1 == text2
    del text2
    text = text1

    # check __iter__
    for subplot_text in text:
        assert isinstance(subplot_text, PlotText)

    # check __getattr__
    for i in range(len(TEST_DATA)):
        assert isinstance(text[i], PlotText)


def test_file_not_found(tmp_path):
    # check FileNotFoundError
    new_file = tmp_path / "new_file.json"
    text_empty = Text(len(TEST_DATA))
    text_empty.read_json(str(new_file))

    assert new_file.exists()
    assert text_empty.subplots_text == [PlotText.get_empy_text() for _ in range(len(TEST_DATA))]


def test_corrupted_json(tmp_path):
    corrupted_data = TEST_DATA.copy()
    corrupted_data.append({})

    test_file = tmp_path / "test_text.json"
    test_file.write_text(dumps(corrupted_data))

    text = Text(len(corrupted_data))
    text.read_json(str(test_file))

    assert text.subplots_text == [PlotText.get_empy_text() for _ in range(len(corrupted_data))]
