SITEURL = ''
SITENAME = u'pelican-jupyter-test'
PATH = 'content-markup-incell'
LOAD_CONTENT_CACHE = False
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
THEME = "notmyidea"

# Plugin config
MARKUP = ('md', 'ipynb')

from pelican_jupyter import markup as nb_markup
PLUGINS = [nb_markup]
IPYNB_USE_METACELL = True

IGNORE_FILES = [".ipynb_checkpoints"]
