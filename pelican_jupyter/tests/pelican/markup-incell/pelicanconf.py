SITEURL = ""
SITENAME = "pelican-jupyter-test"
PATH = "content"
LOAD_CONTENT_CACHE = False
TIMEZONE = "UTC"
DEFAULT_LANG = "en"
THEME = "notmyidea"

# Plugin config
MARKUP = ("md", "ipynb")

from pelican_jupyter import markup as nb_markup  # noqa


PLUGINS = [nb_markup]
IPYNB_MARKUP_USE_FIRST_CELL = True

IGNORE_FILES = [".ipynb_checkpoints"]
