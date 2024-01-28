import os
import importlib.metadata as im
import pathlib

# create necessary directories
parent_dir = "./plotter"
try:
    os.mkdir(parent_dir)
except OSError as _:
    print(f"{parent_dir} directory already exists.")

dirs = ("/img", "/log", "/text", "/utils")
for d in dirs:
    try:
        os.mkdir((destination := parent_dir + d))
    except OSError as _:
        print(f"{destination} directory already exists.")

# copy data-files to info/
package_name = "plotter"
data_dir = "data/"
destination = pathlib.Path(os.getcwd() + "/plotter/utils/")

files = [f for f in im.files(package_name) if data_dir in str(f)]  # find all files
for f in files:
    f_destination = destination.joinpath(f.name)
    with open(f_destination, "wb") as d_file:
        d_file.write(f.read_binary())
