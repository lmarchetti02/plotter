import os
import importlib.metadata as im

# create necessary directories
parent_dir = "./plotter"
os.mkdir(parent_dir)

dirs = ("/img", "/log", "/text", "/info")
for d in dirs:
    try:
        os.mkdir((destination := parent_dir + d))
    except OSError as _:
        print(f"The {destination} directory already exists.")

# copy data-files to info/
package_name = "plotter"
data_dir = "utils"
destination = os.getcwd() + "/plotter/info/"

files = [f for f in im.files(package_name) if "utils/" in str(f)]  # find all files
for f in files:
    f_destination = destination + f.name
    with open(f_destination, "wb") as d_file:
        d_file.write(f.read_binary())
