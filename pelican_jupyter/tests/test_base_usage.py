import os
import subprocess

import pytest


@pytest.mark.parametrize(
    "filename,expected_fname",
    [
        # ("pelicanconf_liquid.py", "with-liquid-tag.html"),
        ("pelicanconf_markup_incell.py", "md-info-in-cell.html"),
        # ("pelicanconf_markup_nbdata.py", "nbdata-file.html"),
    ],
)
def test_can_render_notebook(filename, expected_fname):
    import shutil

    this_dir = os.path.dirname(os.path.realpath(__file__))
    pelican_dir = os.path.join(this_dir, "pelican")
    output_dir = os.path.join(pelican_dir, "output")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    run = subprocess.run(["pelican", "-q", "-s", filename], cwd=pelican_dir)
    assert run.returncode == 0

    rendered_nb_file = os.path.join(output_dir, expected_fname)
    assert os.path.exists(rendered_nb_file)
