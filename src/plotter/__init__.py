"""
-----------------------------------------------------
PLOTTER
by Luca Marchetti

A small Python library for plotting beautiful graphs.
------------------------------------------------------
"""

import os
import pathlib
import importlib.metadata as im

# create necessary directories
parent_dir = pathlib.Path("./plotter")
try:
    # make directories
    os.mkdir(parent_dir)

    dirs = ("img", "log", "text", "utils", "utils/info")
    for dir in dirs:
        try:
            os.mkdir((destination := parent_dir.joinpath(dir)))
        except OSError as _:
            print(f"{destination} directory already exists.")

    # copy data-files into utils/ and utils/info/
    package_name = "plotter"
    data_dir = "data/"
    data_dir_info = "data/info/"
    destination = pathlib.Path(os.getcwd() + "/plotter/utils/")
    destination_info = pathlib.Path(os.getcwd() + "/plotter/utils/info")

    files = {f for f in im.files(package_name) if data_dir in str(f)}  # find all files
    files_info = {f for f in im.files(package_name) if data_dir_info in str(f)}  # find info files
    files -= files_info

    for f in files:
        f_destination = destination.joinpath(f.name)
        with open(f_destination, "wb") as d_file:
            d_file.write(f.read_binary())

    for f in files_info:
        f_destination = destination_info.joinpath(f.name)
        with open(f_destination, "wb") as d_file:
            d_file.write(f.read_binary())

    # text example in text folder
    text_file = [p for p in im.files(package_name) if "text_example.json" in str(p)][0]
    text_destination = pathlib.Path(os.getcwd() + "/plotter/text/text_example.json")
    with open(text_destination, "wb") as d_file:
        d_file.write(text_file.read_binary())
except OSError as _:
    print(f"{parent_dir} directory already exists.")


from .canvas import *
from .plot import *
from .scatter import *
from .histograms import *
from .images import *
