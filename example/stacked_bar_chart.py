"""Runnable example of stacking BarCharts with `stack_bottoms`.

`BarChart.draw()` has no dedicated "stacked" mode -- stacking is just drawing several
`BarChart`s on the same subplot, each one's `bottom` set to the running cumulative
total of the series stacked below it. `stack_bottoms` computes that running total so
the call site doesn't have to track it by hand.

Run from anywhere:

    uv run python example/stacked_bar_chart.py

The rendered figure is saved to `example/output/plotter/img/stacked_bar_chart.png`.
"""

import os
from json import dumps
from pathlib import Path

import numpy as np

import plotter as p

# See basic_plot.py for why the workspace lives in a dedicated subdirectory
# rather than next to this script.
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    os.chdir(OUTPUT_DIR)

    p.setup_workspace()

    text = [
        {
            "title": "Quarterly revenue by product line",
            "x_label": "quarter",
            "y_label": "revenue (k USD)",
            "bar_charts": ["hardware", "software", "services"],
        }
    ]
    Path("plotter/text/stacked_bar_chart.json").write_text(dumps(text))

    quarters = np.array([0.0, 1.0, 2.0, 3.0])
    hardware = np.array([3.0, 4.0, 3.5, 5.0])
    software = np.array([2.0, 2.5, 3.0, 3.5])
    services = np.array([1.0, 1.5, 2.0, 2.5])

    series = [hardware, software, services]
    colors = ["steelblue", "darkorange", "firebrick"]
    bottoms = p.stack_bottoms(series)

    with p.Canvas("stacked_bar_chart.json", figsize=(8.0, 6.0), save="stacked_bar_chart.png", show=False) as canvas:
        canvas.setup()

        for heights, bottom, color in zip(series, bottoms, colors):
            p.BarChart(quarters, heights).draw(canvas, bottom=bottom, color=color)


if __name__ == "__main__":
    main()
