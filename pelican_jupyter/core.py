"""
Core module that handles the conversion from notebook to HTML plus some utilities
"""
import os
import re
from copy import deepcopy

import jinja2
from nbconvert.exporters import HTMLExporter
from pygments.formatters import HtmlFormatter


try:
    # Jupyter
    from traitlets import Integer
except ImportError:
    # IPython < 4.0
    from IPython.utils.traitlets import Integer

try:
    # Jupyter
    from nbconvert.preprocessors import Preprocessor
except ImportError:
    # IPython < 4.0
    from IPython.nbconvert.preprocessors import Preprocessor

try:
    from nbconvert.filters.highlight import _pygments_highlight
except ImportError:
    # IPython < 2.0
    from nbconvert.filters.highlight import _pygment_highlight as _pygments_highlight

try:
    from nbconvert.nbconvertapp import NbConvertApp
except ImportError:
    from IPython.nbconvert.nbconvertapp import NbConvertApp

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


LATEX_CUSTOM_SCRIPT = """
<script type="text/javascript">if (!document.getElementById('mathjaxscript_pelican_#%@#$@#')) {
    var mathjaxscript = document.createElement('script');
    mathjaxscript.id = 'mathjaxscript_pelican_#%@#$@#';
    mathjaxscript.type = 'text/javascript';
    mathjaxscript.src = '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML';
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
        " linebreaks: { automatic: true, width: '95% container' }, " +
        "        styles: { '.MathJax_Display, .MathJax .mo, .MathJax .mi, .MathJax .mn': {color: 'black ! important'} }" +
        "    } " +
        "}); ";
    (document.body || document.getElementsByTagName('head')[0]).appendChild(mathjaxscript);
}
</script>
"""


def get_config():
    """Load and return the user's nbconvert configuration
    """
    app = NbConvertApp()
    app.load_config_file()
    return app.config


def get_html_from_filepath(
    filepath, start=0, end=None, preprocessors=[], template=None, colorscheme=None
):
    """Return the HTML from a Jupyter Notebook
    """
    template_file = "basic"
    extra_loaders = []
    if template:
        extra_loaders.append(jinja2.FileSystemLoader([os.path.dirname(template)]))
        template_file = os.path.basename(template)

    config = get_config()
    config.update(
        {
            "CSSHTMLHeaderTransformer": {
                "enabled": True,
                "highlight_class": ".highlight-ipynb",
            },
            "SubCell": {"enabled": True, "start": start, "end": end},
        }
    )

    if not colorscheme:
        colorscheme = "default"

    config.CSSHTMLHeaderPreprocessor.highlight_class = " .highlight pre "
    config.CSSHTMLHeaderPreprocessor.style = colorscheme
    config.LatexPreprocessor.style = colorscheme
    exporter = HTMLExporter(
        config=config,
        template_file=template_file,
        extra_loaders=extra_loaders,
        filters={"highlight2html": custom_highlighter},
        preprocessors=[SubCell] + preprocessors,
    )
    content, info = exporter.from_filename(filepath)

    return content, info


def parse_css(content, info, fix_css=True, ignore_css=False):
    """
    General fixes for the notebook generated html

    fix_css is to do a basic filter to remove extra CSS from the Jupyter CSS
    ignore_css is to not include at all the Jupyter CSS
    """

    def style_tag(styles):
        return '<style type="text/css">{0}</style>'.format(styles)

    def filter_css(style):
        """
        This is a little bit of a Hack.
        Jupyter returns a lot of CSS including its own bootstrap.
        We try to get only the Jupyter Notebook CSS without the extra stuff.
        """
        index = style.find("/*!\n*\n* IPython notebook\n*\n*/")
        if index > 0:
            style = style[index:]
        index = style.find("/*!\n*\n* IPython notebook webapp\n*\n*/")
        if index > 0:
            style = style[:index]

        style = re.sub(r"color\:\#0+(;)?", "", style)
        style = re.sub(
            r"\.rendered_html[a-z0-9,._ ]*\{[a-z0-9:;%.#\-\s\n]+\}", "", style
        )
        return style_tag(style)

    if ignore_css:
        content = content + LATEX_CUSTOM_SCRIPT
    else:
        if fix_css:
            jupyter_css = "\n".join(
                filter_css(style) for style in info["inlining"]["css"]
            )
        else:
            jupyter_css = "\n".join(
                style_tag(style) for style in info["inlining"]["css"]
            )
        content = jupyter_css + content + LATEX_CUSTOM_SCRIPT
    return content


def custom_highlighter(source, language="python", metadata=None):
    """
    Makes the syntax highlighting from pygments have prefix(`highlight-ipynb`)
    So it doesn't break the theme pygments

    This modifies both css prefixes and html tags

    Returns new html content
    """
    if not language:
        language = "python"

    formatter = HtmlFormatter(cssclass="highlight-ipynb")
    output = _pygments_highlight(source, formatter, language, metadata)
    output = output.replace("<pre>", '<pre class="ipynb">')
    return output


# ----------------------------------------------------------------------
# Create a preprocessor to slice notebook by cells


class SliceIndex(Integer):
    """An integer trait that accepts None"""

    default_value = None

    def validate(self, obj, value):
        if value is None:
            return value
        else:
            return super(SliceIndex, self).validate(obj, value)


class SubCell(Preprocessor):
    """A preprocessor to select a slice of the cells of a notebook"""

    start = SliceIndex(0, config=True, help="first cell of notebook")
    end = SliceIndex(None, config=True, help="last cell of notebook")

    def preprocess(self, nb, resources):
        nbc = deepcopy(nb)
        nbc.cells = nbc.cells[self.start : self.end]
        return nbc, resources
