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

div.cell{width:100%;padding:5px 5px 5px 0;margin:0;outline:none}
div.prompt{min-width:11ex;padding:.4em;margin:0;font-family:monospace;text-align:right;line-height:1.21429em}
@media (max-width:480px){div.prompt{text-align:left}}div.inner_cell{display:-webkit-box;-webkit-box-orient:vertical;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:vertical;-moz-box-align:stretch;display:box;box-orient:vertical;box-align:stretch;display:flex;flex-direction:column;align-items:stretch;-webkit-box-flex:1;-moz-box-flex:1;box-flex:1;flex:1}
div.input_area{border:1px solid #cfcfcf;border-radius:4px;background:#f7f7f7;line-height:1.21429em}
div.prompt:empty{padding-top:0;padding-bottom:0}
div.input{page-break-inside:avoid;display:-webkit-box;-webkit-box-orient:horizontal;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:horizontal;-moz-box-align:stretch;display:box;box-orient:horizontal;box-align:stretch;display:flex;flex-direction:row;align-items:stretch}
@media (max-width:480px){div.input{display:-webkit-box;-webkit-box-orient:vertical;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:vertical;-moz-box-align:stretch;display:box;box-orient:vertical;box-align:stretch;display:flex;flex-direction:column;align-items:stretch}}div.input_prompt{color:#000080;border-top:1px solid transparent}
div.input_area>div.highlight{margin:.4em;border:none;padding:0;background-color:transparent}
div.input_area>div.highlight>pre{margin:0;border:none;padding:0;background-color:transparent}
.CodeMirror{line-height:1.21429em;height:auto;background:none;}
.CodeMirror-scroll{overflow-y:hidden;overflow-x:auto}
.CodeMirror-lines{padding:.4em}
.CodeMirror-linenumber{padding:0 8px 0 4px}
.CodeMirror-gutters{border-bottom-left-radius:4px;border-top-left-radius:4px}
.CodeMirror pre{padding:0;border:0;-webkit-border-radius:0;-moz-border-radius:0;border-radius:0}
pre code{display:block;padding:.5em}
.highlight-base,pre code,pre .subst,pre .tag .title,pre .lisp .title,pre .clojure .built_in,pre .nginx .title{color:#000}
.highlight-string,pre .string,pre .constant,pre .parent,pre .tag .value,pre .rules .value,pre .rules .value .number,pre .preprocessor,pre .ruby .symbol,pre .ruby .symbol .string,pre .aggregate,pre .template_tag,pre .django .variable,pre .smalltalk .class,pre .addition,pre .flow,pre .stream,pre .bash .variable,pre .apache .tag,pre .apache .cbracket,pre .tex .command,pre .tex .special,pre .erlang_repl .function_or_atom,pre .markdown .header{color:#ba2121}
.highlight-comment,pre .comment,pre .annotation,pre .template_comment,pre .diff .header,pre .chunk,pre .markdown .blockquote{color:#408080;font-style:italic}
.highlight-number,pre .number,pre .date,pre .regexp,pre .literal,pre .smalltalk .symbol,pre .smalltalk .char,pre .go .constant,pre .change,pre .markdown .bullet,pre .markdown .link_url{color:#080}
pre .label,pre .javadoc,pre .ruby .string,pre .decorator,pre .filter .argument,pre .localvars,pre .array,pre .attr_selector,pre .important,pre .pseudo,pre .pi,pre .doctype,pre .deletion,pre .envvar,pre .shebang,pre .apache .sqbracket,pre .nginx .built_in,pre .tex .formula,pre .erlang_repl .reserved,pre .prompt,pre .markdown .link_label,pre .vhdl .attribute,pre .clojure .attribute,pre .coffeescript .property{color:#88f}
.highlight-keyword,pre .keyword,pre .id,pre .phpdoc,pre .aggregate,pre .css .tag,pre .javadoctag,pre .phpdoc,pre .yardoctag,pre .smalltalk .class,pre .winutils,pre .bash .variable,pre .apache .tag,pre .go .typename,pre .tex .command,pre .markdown .strong,pre .request,pre .status{color:#008000;font-weight:bold}
.highlight-builtin,pre .built_in{color:#008000}
pre .markdown .emphasis{font-style:italic}
pre .nginx .built_in{font-weight:normal}
pre .coffeescript .javascript,pre .javascript .xml,pre .tex .formula,pre .xml .javascript,pre .xml .vbscript,pre .xml .css,pre .xml .cdata{opacity:.5}
.cm-s-ipython span.cm-variable{color:#000}
.cm-s-ipython span.cm-keyword{color:#008000;font-weight:bold}
.cm-s-ipython span.cm-number{color:#080}
.cm-s-ipython span.cm-comment{color:#408080;font-style:italic}
.cm-s-ipython span.cm-string{color:#ba2121}
.cm-s-ipython span.cm-builtin{color:#008000}
.cm-s-ipython span.cm-error{color:#f00}
.cm-s-ipython span.cm-operator{color:#a2f;font-weight:bold}
.cm-s-ipython span.cm-meta{color:#a2f}
.cm-s-ipython span.cm-tab{background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAMCAYAAAAkuj5RAAAAAXNSR0IArs4c6QAAAGFJREFUSMft1LsRQFAQheHPowAKoACx3IgEKtaEHujDjORSgWTH/ZOdnZOcM/sgk/kFFWY0qV8foQwS4MKBCS3qR6ixBJvElOobYAtivseIE120FaowJPN75GMu8j/LfMwNjh4HUpwg4LUAAAAASUVORK5CYII=);background-position:right;background-repeat:no-repeat}
div.output_wrapper{position:relative;display:-webkit-box;-webkit-box-orient:vertical;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:vertical;-moz-box-align:stretch;display:box;box-orient:vertical;box-align:stretch;display:flex;flex-direction:column;align-items:stretch}
div.output_scroll{height:24em;width:100%;overflow:auto;border-radius:4px;-webkit-box-shadow:inset 0 2px 8px rgba(0,0,0,0.8);-moz-box-shadow:inset 0 2px 8px rgba(0,0,0,0.8);box-shadow:inset 0 2px 8px rgba(0,0,0,0.8);display:block}
div.output_collapsed{margin:0;padding:0;display:-webkit-box;-webkit-box-orient:vertical;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:vertical;-moz-box-align:stretch;display:box;box-orient:vertical;box-align:stretch;display:flex;flex-direction:column;align-items:stretch}
div.out_prompt_overlay{height:100%;padding:0 .4em;position:absolute;border-radius:4px}
div.out_prompt_overlay:hover{-webkit-box-shadow:inset 0 0 1px #000;-moz-box-shadow:inset 0 0 1px #000;box-shadow:inset 0 0 1px #000;background:rgba(240,240,240,0.5)}
div.output_prompt{color:#8b0000}
div.output_area{padding:0;page-break-inside:avoid;display:-webkit-box;-webkit-box-orient:horizontal;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:horizontal;-moz-box-align:stretch;display:box;box-orient:horizontal;box-align:stretch;display:flex;flex-direction:row;align-items:stretch}div.output_area .MathJax_Display{text-align:left !important}
div.output_area .rendered_html table{margin-left:0;margin-right:0}
div.output_area .rendered_html img{margin-left:0;margin-right:0}
.output{display:-webkit-box;-webkit-box-orient:vertical;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:vertical;-moz-box-align:stretch;display:box;box-orient:vertical;box-align:stretch;display:flex;flex-direction:column;align-items:stretch}
@media (max-width:480px){div.output_area{display:-webkit-box;-webkit-box-orient:vertical;-webkit-box-align:stretch;display:-moz-box;-moz-box-orient:vertical;-moz-box-align:stretch;display:box;box-orient:vertical;box-align:stretch;display:flex;flex-direction:column;align-items:stretch}}div.output_area pre{margin:0;padding:0;border:0;vertical-align:baseline;color:#000;background-color:transparent;-webkit-border-radius:0;-moz-border-radius:0;border-radius:0}
div.output_subarea{padding:.4em .4em 0 .4em;-webkit-box-flex:1;-moz-box-flex:1;box-flex:1;flex:1}
div.output_text{text-align:left;color:#000;line-height:1.21429em}
div.output_stderr{background:#fdd;}
div.output_latex{text-align:left}
div.output_javascript:empty{padding:0}
.js-error{color:#8b0000}
div.raw_input_container{font-family:monospace;padding-top:5px}
span.raw_input_prompt{}
input.raw_input{font-family:inherit;font-size:inherit;color:inherit;width:auto;vertical-align:baseline;padding:0 .25em;margin:0 .25em}
input.raw_input:focus{box-shadow:none}
p.p-space{margin-bottom:10px}
.rendered_html{color:#000;}.rendered_html em{font-style:italic}
.rendered_html strong{font-weight:bold}
.rendered_html u{text-decoration:underline}
.rendered_html :link{text-decoration:underline}
.rendered_html :visited{text-decoration:underline}
.rendered_html h1{font-size:185.7%;margin:1.08em 0 0 0;font-weight:bold;line-height:1}
.rendered_html h2{font-size:157.1%;margin:1.27em 0 0 0;font-weight:bold;line-height:1}
.rendered_html h3{font-size:128.6%;margin:1.55em 0 0 0;font-weight:bold;line-height:1}
.rendered_html h4{font-size:100%;margin:2em 0 0 0;font-weight:bold;line-height:1}
.rendered_html h5{font-size:100%;margin:2em 0 0 0;font-weight:bold;line-height:1;font-style:italic}
.rendered_html h6{font-size:100%;margin:2em 0 0 0;font-weight:bold;line-height:1;font-style:italic}
.rendered_html h1:first-child{margin-top:.538em}
.rendered_html h2:first-child{margin-top:.636em}
.rendered_html h3:first-child{margin-top:.777em}
.rendered_html h4:first-child{margin-top:1em}
.rendered_html h5:first-child{margin-top:1em}
.rendered_html h6:first-child{margin-top:1em}
.rendered_html ul{list-style:disc;margin:0 2em}
.rendered_html ul ul{list-style:square;margin:0 2em}
.rendered_html ul ul ul{list-style:circle;margin:0 2em}
.rendered_html ol{list-style:decimal;margin:0 2em}
.rendered_html ol ol{list-style:upper-alpha;margin:0 2em}
.rendered_html ol ol ol{list-style:lower-alpha;margin:0 2em}
.rendered_html ol ol ol ol{list-style:lower-roman;margin:0 2em}
.rendered_html ol ol ol ol ol{list-style:decimal;margin:0 2em}
.rendered_html *+ul{margin-top:1em}
.rendered_html *+ol{margin-top:1em}
.rendered_html hr{color:#000;background-color:#000}
.rendered_html pre{margin:1em 2em}
.rendered_html pre,.rendered_html code{border:0;background-color:#fff;color:#000;font-size:100%;padding:0}
.rendered_html blockquote{margin:1em 2em}
.rendered_html table{margin-left:auto;margin-right:auto;border:1px solid #000;border-collapse:collapse}
.rendered_html tr,.rendered_html th,.rendered_html td{border:1px solid #000;border-collapse:collapse;margin:1em 2em}
.rendered_html td,.rendered_html th{text-align:left;vertical-align:middle;padding:4px}
.rendered_html th{font-weight:bold}
.rendered_html *+table{margin-top:1em}
.rendered_html p{text-align:justify}
.rendered_html *+p{margin-top:1em}
.rendered_html img{display:block;margin-left:auto;margin-right:auto}
.rendered_html *+img{margin-top:1em}
</style>
'''

CUSTOM_SCRIPT = '''
<script type="text/javascript">if (!document.getElementById('mathjaxscript_pelican_#%@#$@#')) {
    var mathjaxscript = document.createElement('script');
    mathjaxscript.id = 'mathjaxscript_pelican_#%@#$@#';
    mathjaxscript.type = 'text/javascript';
    mathjaxscript.src = '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML';
    mathjaxscript[(window.opera ? "innerHTML" : "text")] =
        "MathJax.Hub.Config({" +
        "    config: ['MMLorHTML.js']," +
        "    TeX: { extensions: ['AMSmath.js','AMSsymbols.js','noErrors.js','noUndefined.js'], equationNumbers: { autoNumber: 'AMS' } }," +
        "    jax: ['input/TeX','input/MathML','output/HTML-CSS']," +
        "    extensions: ['tex2jax.js','mml2jax.js','MathMenu.js','MathZoom.js']," +
        "    displayAlign: 'center'," +
        "    displayIndent: '0em'," +
        "    showMathMenu: true," +
        "    tex2jax: { " +
        "        inlineMath: [ ['$','$'] ], " +
        "        displayMath: [ ['$$','$$'] ]," +
        "        processEscapes: true," +
        "        preview: 'TeX'," +
        "    }, " +
        "    'HTML-CSS': { " +
        "        styles: { '.MathJax_Display, .MathJax .mo, .MathJax .mi, .MathJax .mn': {color: 'black ! important'} }" +
        "    } " +
        "}); ";
    (document.body || document.getElementsByTagName('head')[0]).appendChild(mathjaxscript);
}
</script>	
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
        body = parser.body.replace('\[', '$$').replace('\]','$$').replace('\(', '$').replace('\)','$')
        summary = parser.summary

        #metadata['summary'] = summary

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
        css = CUSTOM_CSS #+ css
        body = css + body + CUSTOM_SCRIPT
        return body, metadata


settings = {}


def add_reader(arg):
    global settings
    arg.settings['READERS']['ipynb'] = IPythonNB
    settings = arg.settings


def register():
    signals.initialized.connect(add_reader)
