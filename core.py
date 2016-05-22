"""
Core module that handles the conversion from notebook to HTML
Plus some utilities
"""
from __future__ import absolute_import, print_function, division

import re
from nbconvert import filters
from traitlets.config import Config
from nbconvert.exporters import HTMLExporter
from nbconvert.filters.highlight import _pygments_highlight
from bs4 import BeautifulSoup
from pygments.formatters import HtmlFormatter


def get_html_from_filepath(filepath):
    """Convert ipython notebook to html
    Return: html content of the converted notebook
    """
    config = Config({'CSSHTMLHeaderTransformer': {'enabled': True,
                     'highlight_class': '.highlight-ipynb'}})
    exporter = HTMLExporter(config=config, template_file='basic',
                            filters={'highlight2html': custom_highlighter})
    exporter.register_filter('markdown2html', filters.markdown2html_pandoc)

    content, info = exporter.from_filename(filepath)

    soup = BeautifulSoup(content, "html.parser")
    for i in soup.findAll("div", {"class": "input"}):
        if i.findChildren()[1].find(text='#ignore') is not None:
            i.extract()
    content = soup.decode(formatter=None)

    return content, info


def fix_css(content, info):
    """
    General fixes for the notebook generated html
    """
    def filter_css(style_text):
        """
        HACK: IPython returns a lot of CSS including its own bootstrap.
        Get only the IPython Notebook CSS styles.
        """
        index = style_text.find('/*!\n*\n* IPython notebook\n*\n*/')
        if index > 0:
            style_text = style_text[index:]
        index = style_text.find('/*!\n*\n* IPython notebook webapp\n*\n*/')
        if index > 0:
            style_text = style_text[:index]

        style_text = re.sub(r'color:#0+(;)?', '', style_text)
        style_text = re.sub(r'\.rendered_html[a-z0-9,._ ]*\{[a-z0-9:;%.#\-\s\n]+\}', '', style_text)
        return '<style type=\"text/css\">{0}</style>'.format(style_text)

    ipython_css = '\n'.join(filter_css(css_style) for css_style in info['inlining']['css'])
    content = ipython_css + content
    return content


def custom_highlighter(source, language='python', metadata=None):
    """
    Makes the syntax highlighting from pygments have prefix(`highlight-ipynb`)
    So it doesn't break the theme pygments

    This modifies both css prefixes and html tags

    Returns new html content
    """
    if not language:
        language = 'python'

    formatter = HtmlFormatter(cssclass='highlight-ipynb')
    output = _pygments_highlight(source, formatter, language, metadata)
    output = output.replace('<pre>', '<pre class="ipynb">')
    return output
