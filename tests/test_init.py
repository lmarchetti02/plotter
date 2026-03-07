import os


def test_tree(tmp_path):
    import plotter

    plotter.setup_workspace(tmp_path)
    plotter_dir = tmp_path / "plotter"

    assert plotter_dir.exists()

    dirs = ("img", "log", "text", "utils", "utils/info")
    for dir in dirs:
        assert plotter_dir.joinpath(dir).exists()

    with os.scandir(plotter_dir / "utils/info") as entries:
        assert any(entries)

    assert (plotter_dir / "log/plotter.log").exists()
    assert (plotter_dir / "text/text_example.json").exists()
    assert (plotter_dir / "utils/style.mplstyle").exists()
    assert (plotter_dir / "utils/log_config.json").exists()

    # repeated imports
    del plotter
    import plotter

    plotter.setup_workspace(tmp_path)
