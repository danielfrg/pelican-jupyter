from pelican import signals
from pelican.readers import _EXTENSIONS, Reader
 
try:
    import json
    import IPython
    from datetime import datetime
    from nbconverter.html import ConverterHTML
except:
    IPython = False
 
class iPythonNB(Reader):
    enabled = True
    file_extensions = ['ipynb']

    def read(self, filename):
        text = open(filename)
        converter = ConverterHTML(filename)
        converter.read()

        metadata_uni = json.load(text)['metadata']
        metadata2 = {}
        # Change unicode encoding to utf-8
        for key, value in metadata_uni.iteritems():
          if isinstance(key, unicode):
            key = key.encode('utf-8')
          if isinstance(value, unicode):
            value = value.encode('utf-8')
          metadata2[key] = value

        metadata = {}
        for key, value in metadata2.iteritems():
            key = key.lower()
            metadata[key] = self.process_metadata(key, value)
        metadata['ipython'] = True

        content = converter.main_body() # Use the ipynb converter
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
    _EXTENSIONS['ipynb'] = iPythonNB
 
 
def register():
    signals.initialized.connect(add_reader)