import os
import pathlib
import src.plotter


def test_dir():
    assert pathlib.Path("./plotter").exists()

    dirs = ("img", "log", "text", "utils", "utils/info")
    for dir in dirs:
        assert pathlib.Path("./plotter").joinpath(dir).exists()


def test_info():
    with os.scandir(pathlib.Path("./plotter/utils/info")) as entries:
        assert any(entries)
