# Examples

Runnable scripts showing how to use Plotter in practice, as a companion to the
[Quickstart](../docs/quickstart.md) and the [API reference](../docs/api/index.md).

- `basic_plot.py`: the core `Canvas` / `Drawable` workflow -- `ScatterPlot`, `LinePlot`,
  `BarChart`, `RawHist`, and `BinnedHist`, with titles and legend labels driven by a JSON
  text file.
- `images_and_colorbars.py`: `Hist2D` and `Image`, an explicit `Colorbar` for each, and a
  zoom inset via `Canvas.add_zoom_inset`.

## Running

Install the project first (from the repository root):

```bash
uv sync --group dev
```

Then run a script, from anywhere:

```bash
uv run python example/basic_plot.py
uv run python example/images_and_colorbars.py
```

Each script calls `plotter.setup_workspace()`, which creates a `plotter/` directory in
the current working directory for its runtime assets (images, logs, text files). To keep
that generated directory from colliding with the library's own `plotter/` package -- a
plain directory named `plotter` sitting next to one of these scripts would shadow the
real package on `import plotter` -- each script `chdir`s into its own `example/output/`
subdirectory first. `example/output/` is created on first run and is gitignored; delete
it freely to start over.

Each script saves its rendered figure to `example/output/plotter/img/<script_name>.png`;
set `show=True` on the `Canvas` call to also open it in a window instead.
