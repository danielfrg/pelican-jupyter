import os
import re

from .core import get_html_from_filepath, parse_css
from .vendor.liquid_tags import register  # noqa
from .vendor.liquid_tags.mdx_liquid_tags import LiquidTags


SYNTAX = "{% notebook ~/absolute/path/to/notebook.ipynb [cells[start:end]] %}"
FORMAT = re.compile(
    r"""
^(\s+)?                                                # whitespace
(?P<src>\S+)                                           # source path
(\s+)?                                                 # whitespace
((cells\[)(?P<start>-?[0-9]*):(?P<end>-?[0-9]*)(\]))?  # optional cells
(\s+)?$                                                # whitespace
""",
    re.VERBOSE,
)


@LiquidTags.register("notebook")
def notebook(preprocessor, tag, markup):
    match = FORMAT.search(markup)
    if match:
        argdict = match.groupdict()
        src = argdict["src"]
        start = argdict["start"]
        end = argdict["end"]
    else:
        raise ValueError(
            "Error processing input, " "expected syntax: {0}".format(SYNTAX)
        )

    start = int(start) if start else 0
    end = int(end) if end else None

    nb_path = os.path.join("content", src)
    preprocessors = preprocessor.configs.getConfig("IPYNB_PREPROCESSORS", [])
    template = preprocessor.configs.getConfig("IPYNB_EXPORT_TEMPLATE", None)
    content, info = get_html_from_filepath(
        nb_path, start=start, end=end, preprocessors=preprocessors, template=template
    )

    # Fix CSS
    fix_css = preprocessor.configs.getConfig("IPYNB_FIX_CSS", True)
    ignore_css = preprocessor.configs.getConfig("IPYNB_SKIP_CSS", False)
    content = parse_css(content, info, fix_css=fix_css, ignore_css=ignore_css)

    # TODO: add bleach parsing for safe html
    # https://github.com/Python-Markdown/markdown/commit/7f63b20b819b83afef0ddadc2e210ddce32a2be3
    content = preprocessor.configs.htmlStash.store(content)
    return content
