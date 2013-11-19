import os
from pelican import signals

try:
    from pelican.readers import BaseReader  # new Pelican API
except ImportError:
    from pelican.readers import Reader as BaseReader

try:
    from pelican.readers import EXTENSIONS  # old Pelican API
except ImportError:
    EXTENSIONS = None

try:
    import json
    import markdown

    from IPython.config import Config
    from IPython.nbconvert.exporters import HTMLExporter

    from IPython.nbconvert.filters.highlight import _pygment_highlight
    from pygments.formatters import HtmlFormatter
except Exception as e:
    IPython = False
    raise e


CUSTOM_CSS = '''
<style type="text/css">
div.input_area {
    border: none;
    background: none;
}

pre.ipynb {
    padding: 3px 9.5px;
}

@media print{*{text-shadow:none !important;color:#000 !important;background:transparent !important;box-shadow:none !important;} a,a:visited{text-decoration:underline;} a[href]:after{content:" (" attr(href) ")";} abbr[title]:after{content:" (" attr(title) ")";} .ir a:after,a[href^="javascript:"]:after,a[href^="#"]:after{content:"";} pre,blockquote{border:1px solid #999;page-break-inside:avoid;} thead{display:table-header-group;} tr,img{page-break-inside:avoid;} img{max-width:100% !important;} @page {margin:0.5cm;}p,h2,h3{orphans:3;widows:3;} h2,h3{page-break-after:avoid;}}

.cell.border-box-sizing.code_cell.vbox {
  max-width: 750px;
  margin: 0 auto;
}

pre {
    font-size: 1em;
}

/* Forcing DataFrame table styles */
table.dataframe {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 20px;
}

table.dataframe th, td {
    padding: 4px;
    text-align: left;
}

.anchor-link {
    display: none;
}

.anchor-link:hover {
    display: blockquote;
}

</style>
'''


def custom_highlighter(source, language='ipython'):
    formatter = HtmlFormatter(cssclass='highlight-ipynb')
    output = _pygment_highlight(source, formatter, language)
    output = output.replace('<pre>', '<pre class="ipynb">')
    return output


class iPythonNB(BaseReader):
    enabled = True
    file_extensions = ['ipynb']

    def read(self, filepath):
        filedir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        _metadata = {}
        # See if metadata file exists metadata
        metadata_filename = filename.split('.')[0] + '.ipynb-meta'
        metadata_filepath = os.path.join(filedir, metadata_filename)
        if os.path.exists(metadata_filepath):
            with open(metadata_filepath, 'r') as metadata_file:
                content = metadata_file.read()
                metadata_file = open(metadata_filepath)
                md = markdown.Markdown(extensions=['meta'])
                md.convert(content)
                _metadata = md.Meta

            for key, value in _metadata.items():
                _metadata[key] = value[0]
        else:
            # Try to load metadata from inside ipython nb
            ipynb_file = open(filepath)
            _metadata = json.load(ipynb_file)['metadata']

        metadata = {}
        for key, value in _metadata.items():
            key = key.lower()
            metadata[key] = self.process_metadata(key, value)
        metadata['ipython'] = True

        # Converting ipythonnb to html
        config = Config({'CSSHTMLHeaderTransformer': {'enabled': True, 'highlight_class': '.highlight-ipynb'}})
        exporter = HTMLExporter(config=config, template_file='basic', filters={'highlight2html': custom_highlighter})
        body, info = exporter.from_filename(filepath)

        def filter_tags(s):
            l = s.split('\n')
            exclude = ['a', '.rendered_html', '@media']
            l = [i for i in l if len(list(filter(i.startswith, exclude))) == 0]
            ans = '\n'.join(l)
            return STYLE_TAG.format(ans)

        STYLE_TAG = '<style type=\"text/css\">{0}</style>'
        css = '\n'.join(filter_tags(css) for css in info['inlining']['css'])
        css = css + CUSTOM_CSS
        body = css + body
        return body, metadata


def add_reader(arg):
    if EXTENSIONS is None:  # new pelican API:
        arg.settings['READERS']['ipynb'] = iPythonNB
    else:
        EXTENSIONS['ipynb'] = iPythonNB


def register():
    signals.initialized.connect(add_reader)
