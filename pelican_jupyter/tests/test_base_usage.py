import os
import subprocess

import pytest


@pytest.mark.parametrize(
    "dirname,expected_fname",
    [
        ("pelican/liquid", "with-liquid-tag.html"),
        ("pelican/markup-incell", "md-info-in-cell.html"),
        ("pelican/markup-nbdata", "nbdata-file.html"),
    ],
)
def test_can_render_notebook(dirname, expected_fname):
    import shutil

    this_dir = os.path.dirname(os.path.realpath(__file__))
    pelican_dir = os.path.join(this_dir, dirname)
    output_dir = os.path.join(pelican_dir, "output")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    run = subprocess.run(["pelican", "-q"], cwd=pelican_dir)
    assert run.returncode == 0

    rendered_nb_file = os.path.join(output_dir, expected_fname)
    assert os.path.exists(rendered_nb_file)
