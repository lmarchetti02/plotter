"""Generate Zensical Markdown pages from Plotter docstrings."""

from __future__ import annotations

import ast
import inspect
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "plotter"
DOCS = ROOT / "docs"
API = DOCS / "api"

PUBLIC_MODULES = [
    "plotter.__init__",
    "plotter.canvas",
    "plotter.drawable",
    "plotter.scatter",
    "plotter.lines",
    "plotter.bars",
    "plotter.histograms",
    "plotter.images",
    "plotter.helpers.text",
    "plotter.helpers.initialization",
    "plotter.helpers.useful_functions",
    "plotter.helpers.constants",
]


@dataclass(frozen=True)
class Page:
    module: str
    path: Path
    title: str


def module_path(module: str) -> Path:
    parts = module.split(".")
    if parts[-1] == "__init__":
        return PACKAGE / "__init__.py"
    return ROOT.joinpath(*parts).with_suffix(".py")


def page_path(module: str) -> Path:
    short = module.removeprefix("plotter.")
    if short == "__init__":
        return API / "package.md"
    return API / f"{short.replace('.', '-')}.md"


def anchor(text: str) -> str:
    clean = text.lower().replace("`", "").replace(".", "")
    return "-".join(part for part in clean.replace("_", "-").split() if part)


def escape_markdown(text: str) -> str:
    return text.replace("|", r"\|").replace("[", r"\[").replace("]", r"\]")


def escape_table_cell(text: str) -> str:
    return escape_markdown(text).replace("\n", "<br>")


FIELD_RE = re.compile(r"^(?P<name>`?[\w*]+`?)\s*(?:\((?P<type>[^)]*)\))?:\s*(?P<description>.*)$")


def is_field_line(text: str) -> bool:
    return FIELD_RE.match(text.strip()) is not None


def render_field_table(section: str, rows: list[tuple[str, str, str]]) -> list[str]:
    heading = f"**{section}:**"
    if not rows:
        return [heading]

    if section in {"Returns", "Raises"}:
        rendered = [heading, "", "| Type | Description |", "| --- | --- |"]
        for name, type_, description in rows:
            type_value = name if section == "Raises" else type_
            rendered.append(f"| {escape_table_cell(type_value or '-')} | {escape_table_cell(description)} |")
        return rendered

    rendered = [heading, "", "| Name | Type | Description |", "| --- | --- | --- |"]
    for name, type_, description in rows:
        rendered.append(
            f"| `{escape_table_cell(name.strip('`'))}` | {escape_table_cell(type_ or '-')} | {escape_table_cell(description)} |"
        )
    return rendered


def parse_field_rows(section: str, section_lines: list[str]) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []

    for line in section_lines:
        stripped = line.strip()
        if not stripped:
            continue

        if section == "Returns" and ":" in stripped and not is_field_line(stripped):
            type_, description = stripped.split(":", maxsplit=1)
            rows.append(("", type_.strip(), description.strip()))
            continue

        match = FIELD_RE.match(stripped)
        if match:
            rows.append(
                (
                    match.group("name"),
                    match.group("type") or "",
                    match.group("description").strip(),
                )
            )
            continue

        if rows:
            name, type_, description = rows[-1]
            separator = "<br>" if stripped.startswith("- ") else " "
            rows[-1] = (name, type_, f"{description}{separator}{stripped}".strip())
            continue

        rows.append(("", "", stripped))

    return rows


def render_section(section: str | None, section_lines: list[str]) -> list[str]:
    if section is None:
        return [escape_markdown(line.strip()) if line.strip() else "" for line in section_lines]

    table_sections = {"Args", "Attributes", "Keyword Arguments", "Returns", "Raises"}
    if section in table_sections:
        return render_field_table(section, parse_field_rows(section, section_lines))

    rendered = [f"**{section}:**"]
    if section_lines:
        rendered.append("")
        rendered.extend(escape_markdown(line.strip()) if line.strip() else "" for line in section_lines)
    return rendered


def signature(name: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    result = f"{name}({args})"
    if node.returns is not None:
        result += f" -> {ast.unparse(node.returns)}"
    return result


def display_name(name: str) -> str:
    return name.strip("_") or name


def class_bases(node: ast.ClassDef) -> str:
    if not node.bases:
        return node.name
    return f"{node.name}({', '.join(ast.unparse(base) for base in node.bases)})"


def format_docstring(docstring: str | None) -> str:
    if not docstring:
        return "_No docstring available._\n"

    lines = inspect.cleandoc(docstring).splitlines()
    result: list[str] = []
    sections = {"Args", "Attributes", "Returns", "Raises", "Keyword Arguments", "Note"}
    current_section: str | None = None
    section_lines: list[str] = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        section = stripped[:-1] if stripped.endswith(":") else ""
        if section in sections:
            result.extend(render_section(current_section, section_lines))
            result.append("")
            current_section = section
            section_lines = []
            continue

        section_lines.append(line)

    result.extend(render_section(current_section, section_lines))
    return "\n".join(result).strip() + "\n"


def iter_documented_members(tree: ast.Module) -> list[ast.AST]:
    members: list[ast.AST] = []
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
            members.append(node)
    return members


def iter_documented_methods(node: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        item
        for item in node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and ast.get_docstring(item)
    ]


def iter_documented_attributes(node: ast.ClassDef) -> list[str]:
    attrs: list[str] = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            attrs.append(f"`{item.target.id}: {ast.unparse(item.annotation)}`")
    return attrs


def page_for(module: str) -> Page:
    path = module_path(module)
    title = "plotter" if module.endswith("__init__") else module
    return Page(module=module, path=path, title=title)


def render_page(page: Page) -> str:
    tree = ast.parse(page.path.read_text(), filename=str(page.path))
    parts = [f"# `{page.title}`", ""]

    module_doc = ast.get_docstring(tree)
    if module_doc:
        parts.extend([format_docstring(module_doc), ""])

    for member in iter_documented_members(tree):
        if isinstance(member, ast.ClassDef):
            parts.extend([f"## class `{class_bases(member)}`", "", format_docstring(ast.get_docstring(member)), ""])
            attrs = iter_documented_attributes(member)
            if attrs:
                parts.extend(["**Defined attributes:**", ""])
                parts.extend(f"- {attr}" for attr in attrs)
                parts.append("")

            methods = iter_documented_methods(member)
            if methods:
                parts.extend(["### Methods", ""])
                for method in methods:
                    parts.extend(
                        [
                            f"#### `{display_name(method.name)}`",
                            "",
                            "```python",
                            signature(method.name, method),
                            "```",
                            "",
                            format_docstring(ast.get_docstring(method)),
                            "",
                        ]
                    )
            continue

        parts.extend(
            [
                f"## function `{member.name}`",
                "",
                "```python",
                signature(member.name, member),
                "```",
                "",
                format_docstring(ast.get_docstring(member)),
                "",
            ]
        )

    return "\n".join(parts).rstrip() + "\n"


def write_static_docs(pages: list[Page]) -> None:
    DOCS.mkdir(exist_ok=True)
    API.mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(exist_ok=True)

    shutil.copy2(PACKAGE / "data/info/example_1.png", DOCS / "assets/example_1.png")
    shutil.copy2(PACKAGE / "data/info/example_2.png", DOCS / "assets/example_2.png")

    (DOCS / "index.md").write_text(
        """# Plotter Documentation

Plotter is a small Python library for drawing beautiful plots on top of Matplotlib.
This site turns the package docstrings into a browsable reference, so users can
quickly discover the canvas lifecycle, drawable objects, text-file conventions,
and helper functions.

![Two Plotter examples](assets/example_1.png)

## Start Here

The library is centered on a `Canvas` context manager. Create one canvas, configure
its subplots, draw one or more drawable objects, and let the context manager save,
show, or close the Matplotlib figure.

```python
import numpy as np
import plotter as p

x = np.linspace(-5, 5, num=50)
y = x**2

with p.Canvas("example.json", rows_cols=(1, 1), show=False) as canvas:
    canvas.setup(0)
    p.ScatterPlot(x, y).draw(canvas, label="data")
    p.LinePlot(x, lambda values: values**2).draw(canvas, label="model")
```

## What To Read

- [Quickstart](quickstart.md): setup, workspace layout, and the main plotting flow.
- [API Reference](api/index.md): every module, class, method, and function with a docstring.
- [Canvas](api/canvas.md): figure lifecycle, subplot setup, legends, ticks, guide lines, and scale bars.
- [Drawables](api/scatter.md): scatter plots, line plots, bar charts, histograms, and images.
""",
    )

    (DOCS / "quickstart.md").write_text(
        """# Quickstart

## Install

From the project root:

```bash
pip install .
```

## Create A Workspace

Call `plotter.setup_workspace()` in the directory where you want Plotter to place
runtime assets. It creates folders for generated images, logs, text files, and
bundled helper resources.

```python
import plotter as p

p.setup_workspace()
```

## Add Plot Text

Canvas text comes from JSON files in `plotter/text`. Each subplot entry can define
axis labels, a title, and drawable labels:

```json
[
  {
    "title": "Example",
    "x_label": "x",
    "y_label": "y",
    "scatter_plots": ["data"],
    "line_plots": ["model"],
    "bar_charts": [""],
    "histograms": [""],
    "histograms_2d": [""],
    "images": [""]
  }
]
```

## Draw

```python
import numpy as np
import plotter as p

x = np.linspace(0, 10, 100)

with p.Canvas("example.json", show=False, save="example.png") as canvas:
    canvas.setup(xlim=(0, 10), ylim=(-1.2, 1.2))
    p.LinePlot(x, np.sin).draw(canvas, color="darkgreen", label="sin(x)")
    canvas.draw_line("h", point=0, style="--")
```

![Plotter example](assets/example_2.png)
""",
    )

    links = "\n".join(f"- [`{page.title}`]({page_path(page.module).name})" for page in pages)
    (API / "index.md").write_text(
        f"""# API Reference

These pages are generated from the docstrings in `plotter/`. Run:

```bash
uv run python tools/generate_api_docs.py
```

Then rebuild the static site:

```bash
uv run zensical build
```

## Modules

{links}
""",
    )


def main() -> None:
    pages = [page_for(module) for module in PUBLIC_MODULES]
    write_static_docs(pages)
    for page in pages:
        page_path(page.module).write_text(render_page(page))


if __name__ == "__main__":
    main()
