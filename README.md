# pelican-jupyter: Pelican plugin for Jupyter Notebooks

[![PyPI](https://badge.fury.io/py/pelican-jupyter.svg)](https://pypi.org/project/pelican-jupyter/)
[![Testing](https://github.com/danielfrg/pelican-jupyter/workflows/test/badge.svg)](https://github.com/danielfrg/pelican-jupyter/actions)
[![Coverage Status](https://codecov.io/gh/danielfrg/pelican-jupyter/branch/master/graph/badge.svg)](https://codecov.io/gh/danielfrg/pelican-jupyter?branch=master)
[![License](http://img.shields.io/:license-Apache%202-blue.svg)](https://github.com/danielfrg/pelican-jupyter/blob/master/LICENSE.txt)

## Installation

```
pip install pelican-jupyter
```

### Pelican and Jupyter versions

The main focus is to run with the latest versions of the packages but there is a good chance the plugin will work correctly with older versions of Pelican and Jupyter/.
The recommended version of libraries are:

- `pelican>=4`
- `notebook>=6`
- `nbconvert>=5`

## Usage

This plugin provides two modes to use Jupyter notebooks in [Pelican](https://getpelican.com):

1. As a new markup language so `.ipynb` files are recognized as a valid filetype for an article
2. As a liquid tag based on the [liquid tags plugin](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags) so notebooks can be
included in a regular post using Markdown (`.md`) files.

### Mode A: Markup Mode

On your `pelicanconf.py`:

```python
MARKUP = ("md", "ipynb")

from pelican_jupyter import markup as nb_markup
PLUGINS = [nb_markup]

IGNORE_FILES = [".ipynb_checkpoints"]
```

With this mode you need to pass the MD metadata to the plugins with one of this two options:

#### Option 1: `.nbdata` metadata file

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extension `.nbdata`.
For example if you have `my_post.ipynb` create `my_post.nbdata`.

The `.nbdata` should contain the metadata like a regular Markdown based article (note the empty line at the end, you need it):

```
Title:
Slug:
Date:
Category:
Tags:
Author:
Summary:

```

You can specify to only include a subset of notebook cells with the
`Subcells` metadata item.
It should contain the index (starting at 0) of first and last cell to include
(use `None` for open range).
For example, to skip the first two cells:

```
Subcells: [2, None]
```

### Option 2: Metadata cell in notebook

With this option, the metadata is extracted from the first cell of
the notebook (which should be a Markdown cell), this cell is then ignored when the notebook is rendered.

On your `pelicanconf.py`:

```python
MARKUP = ("md", "ipynb")

from pelican_jupyter import markup as nb_markup
PLUGINS = [nb_markup]
IPYNB_MARKUP_USE_FIRST_CELL = True

IGNORE_FILES = [".ipynb_checkpoints"]
```

Now, you can put the metadata in the first notebook cell in Markdown mode, like this:

```markdown
- title: My notebook
- author: John Doe
- date: 2018-05-11
- category: pyhton
- tags: pip
```

## Mode B: Liquid tags

On your `pelicanconf.py`:

```python
MARKUP = ('md', )

from pelican_jupyter import liquid as nb_liquid
PLUGINS = [nb_liquid]

IGNORE_FILES = [".ipynb_checkpoints"]
```

After this you can use a liquid tag to include a notebook in any regular markdown article,
for example `mypost.md`:

```
Title:
Slug:
Date:
Category:
Tags:
Author:
Summary:

{% notebook path/from/content/dir/to/notebook.ipynb %}
```

## Recommend mode?

Personally I like Method A - Option 1 since I write the Notebooks first and then I just add
the metadata file and keeps the notebook clean.

The Liquid tag mode provide more flexibility to combine an existing notebook code or output with extra text on a Markdown.
You can also combine 2 or more notebooks in this mode.
The only problem with the liquid tag mode is that it doesn't generate a summary for the article
automatically from the notebook so you have to write it in the source `.md` file that includes the notebook.s

You can use both modes at the same time but you are probably going to see a exception that
prevents conflicts, ignore it.

## Note on CSS

If the notebooks look bad on your pelican theme this can help.

There is some issues/conflicts regarding the CSS that the Jupyter Notebook requires and the pelican themes.

I do my best to make the plugin work with every theme but for obvious reasons I cannot guarantee that it will look good in any pelican theme.

Jupyter Notebook is based on bootstrap so you probably will need your theme to be based on that it if you want the html and css to render nicely.

I try to inject only the necessary CSS by removing Jupyter's bootstrap code and only injecting the extra CSS code.
In some cases but fixes are needed, I recommend looking at how [my theme](https://github.com/danielfrg/danielfrg.com) fixes them.

You can suppress the inclusion of any Notebook CSS entirely by setting `IPYNB_SKIP_CSS=True`, this allows more flexibility on the pelican theme.

The `IPYNB_EXPORT_TEMPLATE` option is another great way of extending the output natively using Jupyter nbconvert.

## Settings

**Note:** If you are using the Liquid mode you need to set the variables like this inside the `pelicanconf.py`.

```
LIQUID_CONFIGS = (("IPYNB_EXPORT_TEMPLATE", "notebook.tpl", ""), )
```

If you are using the Markup mode then just add this variables to your `pelicanconf.py`.

| Setting | Description |
|---|---|
| `IPYNB_FIX_CSS = True` | [markup and liquid] Do not apply any of the plugins "fixes" to the Jupyter CSS use all the default Jupyter CSS. |
| `IPYNB_SKIP_CSS = False` | [markup and liquid] Do not include (at all) the notebook CSS in the generated output. This is usefull if you want to include it yourself in the theme. |
| `IPYNB_PREPROCESSORS` | [markup and liquid] A list of nbconvert preprocessors to be used when generating the HTML output. |
| `IPYNB_EXPORT_TEMPLATE` | [markup and liquid] Path to nbconvert export template (relative to project root). For example: Create a custom template that extends from the `basic` template and adds some custom CSS and JavaScript, more info here [docs](http://nbconvert.readthedocs.io/en/latest/customizing.html) and [example here](https://github.com/jupyter/nbconvert/blob/master/nbconvert/templates/html/basic.tpl). |
| `IPYNB_STOP_SUMMARY_TAGS = [('div', ('class', 'input')), ('div', ('class', 'output')), ('h2', ('id', 'Header-2'))]` | [markup only] List of tuples with the html tag and attribute (python HTMLParser format) that are used to stop the summary creation, this is useful to generate valid/shorter summaries. |
| `IPYNB_GENERATE_SUMMARY = True` | [markup only] Create a summary based on the notebook content. Every notebook can still use the s`Summary` from the metadata to overwrite this. |
| `IPYNB_EXTEND_STOP_SUMMARY_TAGS` | [markup only] List of tuples to extend the default `IPYNB_STOP_SUMMARY_TAGS`. |
| `IPYNB_NB_SAVE_AS` | [markup only] If you want to make the original notebook available set this variable in a  is similar way to the default pelican `ARTICLE_SAVE_AS` setting. This will also add a metadata field `nb_path` which can be used in the theme. e.g. `blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/notebook.ipynb` |
| `IPYNB_COLORSCHEME` | [markup only] Change the pygments colorscheme used for syntax highlighting |
| `IGNORE_FILES = ['.ipynb_checkpoints']` | [Pelican setting useful for markup] Prevents pelican from trying to parse notebook checkpoint files. |

Example template for `IPYNB_EXPORT_TEMPLATE`:

```
{%- extends 'basic.tpl' -%}

{% block header %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>

<style type="text/css">
div.code_cell {
    border: 2px solid red;
}
</style>
{%- endblock header %}
```
