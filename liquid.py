import os
import re

from liquid_tags.mdx_liquid_tags import LiquidTags

from .core import get_html_from_filepath, fix_css


SYNTAX = "{% notebook ~/absolute/path/to/notebook.ipynb %}"
FORMAT = re.compile(r"""^(\s+)?(?P<src>\S+)(\s+)?((cells\[)(?P<start>-?[0-9]*):(?P<end>-?[0-9]*)(\]))?(\s+)?((language\[)(?P<language>-?[a-z0-9\+\-]*)(\]))?(\s+)?$""")


@LiquidTags.register('notebook')
def notebook(preprocessor, tag, markup):
    match = FORMAT.search(markup)
    if match:
        argdict = match.groupdict()
        src = argdict['src']
        start = argdict['start']
        end = argdict['end']
        language = argdict['language']
    else:
        raise ValueError("Error processing input, "
                         "expected syntax: {0}".format(SYNTAX))

    # nb_dir =  preprocessor.configs.getConfig('NOTEBOOK_DIR')
    nb_path = os.path.join('content', src)
    content, info = get_html_from_filepath(nb_path)
    content = fix_css(content, info)
    content = preprocessor.configs.htmlStash.store(content, safe=True)
    return content


# ---------------------------------------------------
# This import allows notebook tag to be a Pelican plugin
from liquid_tags import register  # noqa
