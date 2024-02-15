# Plotter

A data-analysis-oriented library for drawing beautiful plots.

## Description

This library makes heavy use of the `matplotlib` library, therefore it is necessary to have some
understanding of that library.

Shortly, _Plotter_ makes it easy to create beautiful `matplotlib` plots by generating instances of
matplotlib object with preset values. In other words, it gives the user a faster and easier way of
rendering plots of analyzed data.

## Installation

Follow the steps below to install _Plotter_ (Unix-like systems):

1. Clone the repository to a directory in your system.
2. Open the terminal and navigate to said folder.
3. Run the command
   ```bash
   python3 -m install
   ```
4. A _dist_ directory will be created, containing a .whl file.
5. To install the package run
   ```bash
   pip3 install /path/to/whl/file
   ```
6. If the installation was successful, _Plotter_ can be
   imported simply by
   ```python
   import plotter as p
   ```

__Note__: It is possible that the commands to use are `python` and `pip`, instead of, respectively, `python3` and `pip3`.

## Usage

Once imported, the library will create a tree of directories with the following structure:

``` 
plotter
├── img
├── log
├── text
└── utils
    ├── blueprint.txt
    ├── log_config.json
    ├── style.mplstyle
    └── text_example.json
```

These directories/files, which are not to be deleted, have the following purposes:

1. The _/img_ directory is the one where the plots are saved to.
2. The _/log_ directory is the one where the log files are stored.
3. The _/text_ directory is the one where the json files containing the plot text are to be stored.
4. The _/utils_ directory stores useful files, in particular:
   * _blueprint.txt_, which contains boilerplate code needed for a basic example;
   * *log_config.json*, which contains the logging configurations;
   * _style.mplstyle_, which contains the matplotlib configurations;
   * *text_example.json*, which is the blueprint for the json files to put in the _/text_ directory.

### Example

For a basic graph, try the following piece of code.

```python
import numpy as np
import plotter as p

# datasets to plot
x = np.linspace(-5, 5, num=50)
y = x**2
y_err = np.full(50, 0.5)
x_err = np.full(50, 0.2)

# function to plot
def f(x):
    return x**2

# create canvas
canvas = p.Canvas("prova.json")
canvas.setup()

# add scatter plot and 1D graph to canvas
p.ScatterPlot(x, y, y_err, x_err).draw(canvas)
p.Plot(x, f, (0.01, 0.01)).draw(canvas)

# render plot
canvas.end()
```

## Images

![example1](/src/plotter/data/info/example_1.png "Example 1")
![example2](/src/plotter/data/info/example_2.png "Example 2")

## License

See the [LICENCE](LICENCE) file for licence rights and limitations.
