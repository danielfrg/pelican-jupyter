import ast
import json
import os
import re
import tempfile
from shutil import copyfile

from pelican import signals
from pelican.readers import BaseReader, HTMLReader, MarkdownReader

from .core import get_html_from_filepath, parse_css


try:
    # Py3k
    from html.parser import HTMLParser
except ImportError:
    # Py2.7
    from HTMLParser import HTMLParser


def register():
    """
    Register the new "ipynb" reader
    """

    def add_reader(arg):
        arg.settings["READERS"]["ipynb"] = IPythonNB

    signals.initialized.connect(add_reader)


class IPythonNB(BaseReader):
    """
    Extend the Pelican.BaseReader to `.ipynb` files can be recognized
    as a markup language:

    Setup:

    `pelicanconf.py`:
    ```
    MARKUP = ('md', 'ipynb')
    ```
    """

    enabled = True
    file_extensions = ["ipynb"]

    def read(self, filepath):
        metadata = {}
        metadata["jupyter_notebook"] = True
        start = 0
        end = None

        # Files
        filedir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        metadata_filename = os.path.splitext(filename)[0] + ".nbdata"
        metadata_filepath = os.path.join(filedir, metadata_filename)

        if os.path.exists(metadata_filepath):
            # Found and .nbdata file
            # Process it using Pelican MD Reader
            md_reader = MarkdownReader(self.settings)
            _content, metadata = md_reader.read(metadata_filepath)
        elif self.settings.get("IPYNB_MARKUP_USE_FIRST_CELL"):
            # No external .md file:
            # Load metadata from the first cell of the notebook file
            with open(filepath) as ipynb_file:
                nb_json = json.load(ipynb_file)

            metacell = "\n".join(nb_json["cells"][0]["source"])
            # Convert Markdown title and listings to standard metadata items
            metacell = re.sub(r"^#+\s+", "title: ", metacell, flags=re.MULTILINE)
            metacell = re.sub(r"^\s*[*+-]\s+", "", metacell, flags=re.MULTILINE)
            # Unfortunately we can not pass MarkdownReader an in-memory
            # string, so we have to work with a temporary file
            with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as metadata_file:
                md_reader = MarkdownReader(self.settings)
                metadata_file.write(metacell)
                metadata_file.flush()
                _content, metadata = md_reader.read(metadata_file.name)
            # Skip metacell
            start = 1
        else:
            raise Exception(
                "Error processing f{filepath}: "
                "Could not find metadata in: .nbdata file or in the first cell of the notebook."
                "If this notebook is used with liquid tags then you can safely ignore this error."
            )

        if "subcells" in metadata:
            start, end = ast.literal_eval(metadata["subcells"])

        preprocessors = self.settings.get("IPYNB_PREPROCESSORS", [])
        template = self.settings.get("IPYNB_EXPORT_TEMPLATE", None)
        content, info = get_html_from_filepath(
            filepath,
            start=start,
            end=end,
            preprocessors=preprocessors,
            template=template,
            colorscheme=self.settings.get("IPYNB_COLORSCHEME"),
        )

        # Generate summary: Do it before cleaning CSS
        keys = [k.lower() for k in metadata.keys()]
        use_meta_summary = self.settings.get("IPYNB_GENERATE_SUMMARY", True)
        if "summary" not in keys and use_meta_summary:
            parser = MyHTMLParser(self.settings, filename)
            content = "<body>{0}</body>".format(content)
            parser.feed(content)
            parser.close()
            # content = parser.body
            metadata["summary"] = parser.summary

        # Write/fix content
        fix_css = self.settings.get("IPYNB_FIX_CSS", True)
        ignore_css = self.settings.get("IPYNB_SKIP_CSS", False)
        content = parse_css(content, info, fix_css=fix_css, ignore_css=ignore_css)
        if self.settings.get("IPYNB_NB_SAVE_AS"):
            output_path = self.settings.get("OUTPUT_PATH")
            nb_output_fullpath = self.settings.get("IPYNB_NB_SAVE_AS").format(
                **metadata
            )
            nb_output_dir = os.path.join(
                output_path, os.path.dirname(nb_output_fullpath)
            )
            if not os.path.isdir(nb_output_dir):
                os.makedirs(nb_output_dir, exist_ok=True)
            copyfile(filepath, os.path.join(output_path, nb_output_fullpath))
            metadata["nb_path"] = nb_output_fullpath
        return content, metadata


class MyHTMLParser(HTMLReader._HTMLParser):
    """
    Custom Pelican `HTMLReader._HTMLParser` to create the summary of the content
    based on settings['SUMMARY_MAX_LENGTH'].

    Summary is stoped if founds any div containing ipython notebook code cells.
    This is needed in order to generate valid HTML for the summary,
    a simple string split will break the html generating errors on the theme.
    The downside is that the summary length is not exactly the specified, it stops at
    completed div/p/li/etc tags.
    """

    def __init__(self, settings, filename):
        HTMLReader._HTMLParser.__init__(self, settings, filename)
        self.settings = settings
        self.filename = filename
        self.wordcount = 0
        self.summary = None

        self.stop_tags = self.settings.get(
            "IPYNB_STOP_SUMMARY_TAGS",
            [
                ("div", ("class", "input")),
                ("div", ("class", "output")),
                ("h2", ("id", "Header-2")),
            ],
        )
        if "IPYNB_EXTEND_STOP_SUMMARY_TAGS" in self.settings.keys():
            self.stop_tags.extend(self.settings["IPYNB_EXTEND_STOP_SUMMARY_TAGS"])

    def handle_starttag(self, tag, attrs):
        HTMLReader._HTMLParser.handle_starttag(self, tag, attrs)

        if self.wordcount < self.settings["SUMMARY_MAX_LENGTH"]:
            mask = [
                stoptag[0] == tag and (stoptag[1] is None or stoptag[1] in attrs)
                for stoptag in self.stop_tags
            ]
            if any(mask):
                self.summary = self._data_buffer
                self.wordcount = self.settings["SUMMARY_MAX_LENGTH"]

    def handle_endtag(self, tag):
        HTMLReader._HTMLParser.handle_endtag(self, tag)

        if self.wordcount < self.settings["SUMMARY_MAX_LENGTH"]:
            self.wordcount = len(strip_tags(self._data_buffer).split(" "))
            if self.wordcount >= self.settings["SUMMARY_MAX_LENGTH"]:
                self.summary = self._data_buffer


def strip_tags(html):
    """
    Strip html tags from html content (str)
    Useful for summary creation
    """
    s = HTMLTagStripper()
    s.feed(html)
    return s.get_data()


class HTMLTagStripper(HTMLParser):
    """
    Custom HTML Parser to strip HTML tags
    Useful for summary creation
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, html):
        self.fed.append(html)

    def get_data(self):
        return "".join(self.fed)
