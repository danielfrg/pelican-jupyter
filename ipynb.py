# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import logging

import markdown

try:
    # Py3k
    from html.parser import HTMLParser
except ImportError:
    # Py2.7
    from HTMLParser import HTMLParser

from pelican import signals
from pelican.readers import MarkdownReader, HTMLReader, BaseReader

import IPython
from IPython.config import Config
from IPython.nbconvert.exporters import HTMLExporter

try:
    from IPython.nbconvert.filters.highlight import _pygment_highlight
except ImportError:
    # IPython < 2.0
    from IPython.nbconvert.filters.highlight import _pygments_highlight

try:
    from bs4 import BeautifulSoup
except:
    BeautifulSoup = None

from pygments.formatters import HtmlFormatter


logger = logging.getLogger(__name__)


# Utility to strip HTML tags for summary creation
class MLStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# Fix CSS

CUSTOM_CSS = '''
<style type="text/css">

/* General text, input and output cells */
div.cell {
    border: none;
}

.inner_cell {
    width: 100%
}

.text_cell .prompt {
    display: none;
}

div.cell {
    margin: 0;
    padding: 0;
}

div.input_area {
    border: none;
    background: none;
    margin-left: 6px;
}

div.output_subarea {
    padding: 0;
}

pre.ipynb {
    padding: 5px 5px 5px 10px;
}

/* DataFrame */
table.dataframe {
    font-family: Arial, sans-serif;
    font-size: 13px;
    line-height: 20px;
}

table.dataframe th, td {
    padding: 4px;
    text-align: left;
}

</style>
'''


def custom_highlighter(source, language='ipython', metadata=None):
    """
    Makes the syntax highlighting from pygments have prefix(`highlight-ipynb`)
    So it does not break the theme pygments

    It modifies both the css and html
    """
    if not language:
        language = 'ipython'

    formatter = HtmlFormatter(cssclass='highlight-ipynb')
    output = _pygments_highlight(source, formatter, language, metadata)
    output = output.replace('<pre>', '<pre class="ipynb">')
    return output


class MyHTMLParser(HTMLReader._HTMLParser):
    """
    Extends Pelican HTMLReader._HTMLParser by including the summary of the content
    based on settings['SUMMARY_MAX_LENGTH'].
    Also stops the summary if founds any div containing ipython notebook code cells

    This is needed in order to generate valid HTML for the summary, because a simple split
    breaks the html generating errors on the theme.
    The downside is that the summary length is not exactly the specified, it includes
    complete div/p/li/etc tags.
    """
    def __init__(self, settings, filename):
        HTMLReader._HTMLParser.__init__(self, settings, filename)
        self.wordcount = 0
        self.summary = None

        self.stop_tags = [('div', ('class', 'input')), ('div', ('class', 'output'))]
        if 'IPYNB_STOP_SUMMARY_TAGS' in self.settings.keys():
            self.stop_tags = self.settings['IPYNB_STOP_SUMMARY_TAGS']
        if 'IPYNB_EXTEND_STOP_SUMMARY_TAGS' in self.settings.keys():
            self.stop_tags.extend(self.settings['IPYNB_EXTEND_STOP_SUMMARY_TAGS'])


    def handle_starttag(self, tag, attrs):
        HTMLReader._HTMLParser.handle_starttag(self, tag, attrs)

        if self.wordcount < self.settings['SUMMARY_MAX_LENGTH']:
            mask = [stoptag[0] == tag and (stoptag[1] is None or stoptag[1] in attrs) for stoptag in self.stop_tags]
            if any(mask):
                self.summary = self._data_buffer
                self.wordcount = self.settings['SUMMARY_MAX_LENGTH']

    def handle_endtag(self, tag):
        HTMLReader._HTMLParser.handle_endtag(self, tag)

        if self.wordcount < self.settings['SUMMARY_MAX_LENGTH']:
            self.wordcount = len(strip_tags(self._data_buffer).split(' '))
            if self.wordcount >= self.settings['SUMMARY_MAX_LENGTH']:
                self.summary = self._data_buffer


class IPythonNB(BaseReader):
    enabled = True
    file_extensions = ['ipynb']

    def read(self, filepath):
        metadata = {}

        # Files
        filedir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        metadata_filename = filename.split('.')[0] + '.ipynb-meta'
        metadata_filepath = os.path.join(filedir, metadata_filename)

        # Load metadata
        if os.path.exists(metadata_filepath):
            # Metadata is on a external file, process using Pelican MD Reader
            md_reader = MarkdownReader(self.settings)
            _content, metadata = md_reader.read(metadata_filepath)
        else:
            # Load metadata from ipython notebook file
            ipynb_file = open(filepath)
            metadata = json.load(ipynb_file)['metadata']

            # Fix metadata to pelican standards
            for key, value in metadata.items():
                del metadata[key]
                key = key.lower()
                metadata[key] = self.process_metadata(key, value)
        metadata['ipython'] = True

        # Convert ipython notebook to html
        config = Config({'CSSHTMLHeaderTransformer': {'enabled': True,
                         'highlight_class': '.highlight-ipynb'}})
        exporter = HTMLExporter(config=config, template_file='basic',
                                filters={'highlight2html': custom_highlighter})

        content, info = exporter.from_filename(filepath)

        if BeautifulSoup:
            soup = BeautifulSoup(content)
            for i in soup.findAll("div", {"class" : "input"}):
                if i.findChildren()[1].find(text='#ignore') is not None:
                    i.extract()
        else:
            soup = content

        # Process using Pelican HTMLReader
        content = '<body>{0}</body>'.format(soup)  # So Pelican HTMLReader works
        parser = MyHTMLParser(self.settings, filename)
        parser.feed(content)
        parser.close()
        body = parser.body
        summary = parser.summary

        metadata['summary'] = summary

        # Remove some CSS styles, so it doesn't break the themes.
        def filter_tags(style_text):
            style_list = style_text.split('\n')
            exclude = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'ol', 'li',
                       '.rendered_html', '@media', '.navbar', 'nav.navbar', '.navbar-text',
                       'code', 'pre', 'div.text_cell_render']
            style_list = [i for i in style_list if len(list(filter(i.startswith, exclude))) == 0]
            ans = '\n'.join(style_list)
            return '<style type=\"text/css\">{0}</style>'.format(ans)

        css = '\n'.join(filter_tags(css) for css in info['inlining']['css'])
        css = CUSTOM_CSS + css
        body = css + body

        return body, metadata


settings = {}


def add_reader(arg):
    global settings
    arg.settings['READERS']['ipynb'] = IPythonNB
    settings = arg.settings


def register():
    signals.initialized.connect(add_reader)
