"""
Core module that handles the conversion from notebook to HTML
Plus some utilities
"""
from __future__ import absolute_import, print_function, division

from nbconvert import filters
from traitlets.config import Config
from nbconvert.exporters import HTMLExporter
from bs4 import BeautifulSoup


def get_html_from_filepath(filepath):
    """Convert ipython notebook to html
    Return: html content of the converted notebook
    """
    config = Config({'CSSHTMLHeaderTransformer': {'enabled': True,
                     'highlight_class': '.highlight-ipynb'}})
    exporter = HTMLExporter(config=config, template_file='basic')
    exporter.register_filter('markdown2html', filters.markdown2html_pandoc)

    content, info = exporter.from_filename(filepath)

    soup = BeautifulSoup(content, "html.parser")
    for i in soup.findAll("div", {"class": "input"}):
        if i.findChildren()[1].find(text='#ignore') is not None:
            i.extract()
    content = soup.decode(formatter=None)

    return content, info
