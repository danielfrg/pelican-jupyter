import os
from pelican import signals
from pelican.readers import EXTENSIONS, Reader

try:
    import json
    import IPython
    from .nbconverter.html import ConverterHTML
    import markdown
except Exception as e:
    IPython = False
    raise e


class iPythonNB(Reader):
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

            for key, value in _metadata.iteritems():
                _metadata[key] = value[0]
        else:
            # Try to load metadata from inside ipython nb
            ipynb_file = open(filepath)
            _metadata = json.load(ipynb_file)['metadata']
        # Change unicode encoding to utf-8
        for key, value in _metadata.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            _metadata[key] = value

        metadata = {}
        for key, value in _metadata.iteritems():
            key = key.lower()
            metadata[key] = self.process_metadata(key, value)
        metadata['ipython'] = True

        # Converting ipython to html
        converter = ConverterHTML(filepath)
        converter.read()
        content = converter.main_body()  # Use the ipynb converter
        # change ipython css classes so it does not mess up the blog css
        content = '\n'.join(converter.main_body())
        # replace the highlight tags
        content = content.replace('class="highlight"', 'class="highlight-ipynb"')
        # specify <pre> tags
        content = content.replace('<pre', '<pre class="ipynb"')
        # create a special div for notebook
        content = '<div class="ipynb">' + content + "</div>"
        # Modify max-width for tables
        content = content.replace('max-width:1500px;', 'max-width:540px;')
        # h1,h2,...
        for h in '123456':
            content = content.replace('<h%s' % h, '<h%s class="ipynb"' % h)
        return content, metadata


def add_reader(arg):
    EXTENSIONS['ipynb'] = iPythonNB


def register():
    signals.initialized.connect(add_reader)
