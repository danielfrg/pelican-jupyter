# Pelican plugin for Jupyter/IPython Notebooks

This plugin provides two modes to use Jupyter/IPython notebooks in [Pelican](https://getpelican.com):

1. As a new markup language so `.ipynb` files are recognized as a valid filetype for an article
2. As a liquid tag based on the [liquid tags plugin](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags) so notebooks can be
included in a regular post using Markdown (`.md`) files.

## Requirements

Python 2.7 and 3.4 are supported

The main objective is to run with the latest version of Jupyter/IPython
but there is a good chance the plugin will work correctly with older versions of Pelican and Jupyter/IPython.
The recommended version of libraries are:

- `pelican>=3.5`
- `jupyter>=1.0`
- `ipython>=4.0`
- `nbconvert>=4.0`
- `beautifulsoup4`


## Installation

Download this repo and put all the `.py` files it into an `ipynb` directory
in your `plugins` directory. The structure should look like this:

```
content
plugins
  ipynb
    __init__.py
    core.py
    ipynb.py
    liquid.py
    markup.py
    ... other files are optional ...
```

If you manage your site with git (github pages for example),
you can also define it as a submodule:

```sh
git submodule add git://github.com/danielfrg/pelican-ipynb.git plugins/ipynb
```

See below for additional settings in your `pelicanconf.py`, depending on the
mode you are using.

## Mode A: Markup Mode

Setup usage of the `markup` plugin in `pelicanconf.py`:

```python
MARKUP = ('md', 'ipynb')

PLUGIN_PATHS = ['./plugins']
PLUGINS = ['ipynb.markup']
```

### Option 1 (recommended): separate metadata file

Write the post using the Jupyter Notebook interface, using markdown, equations, etc.

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extension `.ipynb-meta`.
For example if you have `my_post.ipynb` create a `my_post.ipynb-meta`.

The `.ipynb-meta` should contain the metadata like a regular Markdown based article:

```
Title:
Slug:
Date:
Category:
Tags:
Author:
Summary:

```

Note the empty line at the end, you need that.

You can also specify to only include a subset of notebook cells with the
`Subcells` metadata item.
It should contain the index (starting at 0) of first and last cell to include
(use `None` for "unlimited").
For example, to skip the first two cells:

```
Subcells: [2, None]
```

### Option 2: metadata field in notebook

Open the `.ipynb` file in a text editor and look for the `metadata` tag should see.

```
{
    "metadata": {
        "name": "My notebook",
        "kernelspec": ...
        "version": ...
        ... { A_LOT_OF_OTHER_STUFF } ...
    },
{ A_LOT_OF_OTHER_STUFF }
```

Edit this the `metadata` tag to have the required markdown metadata:

```
{
 "metadata": {
        "name": "My notebook",
        "Title": "Notebook using internal metadata",
        "Date": "2100-12-31",
        "Category": "Category",
        "Tags": "tag1,tag2",
        "slug": "with-metadata",
        "Author": "Me"

        ... { A_LOT_OF_OTHER_STUFF } ...
    },
    { A_LOT_OF_OTHER_STUFF }
```

### Option 3: metadata cell in notebook

With this option, the metadata is extracted from the first cell of
the notebook (which should be a Markdown cell).
This avoid the burden of maintaining a separate file or manually editing the
json in the `.ipynb` file like the previous options.

First, enable the "metacell" mode globally in your config

```python
IPYNB_USE_METACELL = True
```

Now, you can put the metadata in the first notebook cell in Markdown mode,
like this:

```markdown
# How to install pip
- author: John Doe
- date: 2018-05-11
- category: pyhton
- tags: pip
```

## Mode B: Liquid Tags

Install the [liquid_tags plugin](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags).
Only the base `liquid_tags.py` and `mdx_liquid_tags.py` files are needed.

In the `pelicanconf.py`:

```python
MARKUP = ('md', )

PLUGIN_PATHS = ['./plugins']
PLUGINS = ['ipynb.liquid']
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

The only problem with the liquid tag mode is that it doesn't generate a summary for the article
automatically from the notebook so you have to write it in the `.md` file that includes
the notebook liquid tag.

So you end up writing two files, one `.md` with some text content
and the `.ipynb` with the code/plots/equations that makes it a little bit annoying but can
be useful in some cases.

You can use both modes at the same time but you are probably going to see a exception that
prevents conflicts, ignore it.

## Note on CSS

There might be some issues/conflicts regarding the CSS that the Jupyter Notebook requires and the pelican theme.

I do my best to make the plugin work with every theme but for obvious reasons I cannot guarantee that it will look good in any pelican theme.

I only try this plugin on the pelican theme for [my blog](https://github.com/danielfrg/danielfrg.github.io-source)
while trying to make it the most general and useful out of the box as possible, a difficult compromise sometimes.

Jupyter Notebook is based on bootstrap so you probably will need your theme to be based on that it if you want the html and css to render nicely.

I try to inject only the necessary CSS, removing Jupyter's bootstrap but fixes are needed in some cases,
if you find this issues I recommend looking at how my theme fixes them. You can suppress the inclusion of CSS entirely by setting
`IPYNB_IGNORE_CSS=True` in `pelicanconf.py`.


## Options

You can include an `#ignore` comment anywhere in a cell of the Jupyter notebook
to ignore it, removing it from the post content.

In `pelicanconf.py` you can set:

- `IPYNB_USE_META_SUMMARY`: boolean variable to use the summary provided in the `.ipynb-meta` file instead of creating it from the notebook.
- `IPYNB_STOP_SUMMARY_TAGS`: list of tuples with the html tag and attribute (python HTMLParser format)
when the summary creation should stop, this is useful to generate valid/shorter summaries.
`default = [('div', ('class', 'input')), ('div', ('class', 'output'))]`
- `IPYNB_EXTEND_STOP_SUMMARY_TAGS`: list of tuples to extend the default `IPYNB_STOP_SUMMARY_TAGS`
- `IGNORE_FILES = ['.ipynb_checkpoints']`: prevents pelican from trying to parse notebook checkpoint files
- `IPYNB_IGNORE_CSS = True`: do not include the notebook CSS in the generated output
- `IPYNB_PREPROCESSORS`: a list of nbconvert preprocessors to be used when generating the HTML output
- `IPYNB_EXPORT_TEMPLATE` (advanced): path to nbconvert export template (relative to project root).
  For example: create a custom template that extends from the `basic` template and adds some custom
  CSS and JavaScript:
  ```
  {%- extends 'basic.tpl' -%}

  {% block header %}
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
  <style type="text/css">
  div#notebook {
      border: 1px solid red;
  }
  </style>
  {%- endblock header %}
  ```
