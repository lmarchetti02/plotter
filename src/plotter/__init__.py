import os
import importlib

# create necessary directories
try:
    os.mkdir("./img")
except FileExistsError as _:
    print("The '/img' directory already exists.")

try:
    os.mkdir("./log")
except FileExistsError as _:
    print("The '/log' directory already exists.")

try:
    os.mkdir("./text")
except FileExistsError as _:
    print("The '/text' directory already exists.")

try:
    os.mkdir("./info")
except FileExistsError as _:
    print("The '/text' directory already exists.")
