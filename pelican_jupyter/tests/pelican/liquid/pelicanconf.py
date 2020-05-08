SITEURL = ""
SITENAME = "pelican-jupyter-test"
PATH = "content"
LOAD_CONTENT_CACHE = False
TIMEZONE = "UTC"
DEFAULT_LANG = "en"
THEME = "notmyidea"

# Plugin config
MARKUP = "md"

from pelican_jupyter import liquid as nb_liquid  # noqa


PLUGINS = [nb_liquid]

IGNORE_FILES = [".ipynb_checkpoints"]
