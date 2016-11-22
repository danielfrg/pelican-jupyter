# Pelican plugin for Jupyter/IPython Notebooks

This plugin provides two modes to use Jupyter/IPython notebooks in pelican:

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
into your `plugins` directory. The structure should look like this:

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

See specific modes notes for settings in the `pelicanconf.py`:

If you host your site on git (i.e. github pages) you could use it as a submodule:

```
git submodule add git://github.com/danielfrg/pelican-ipynb.git plugins/ipynb
```

## Mode A: Markup Mode

In the `pelicanconf.py`:
```
MARKUP = ('md', 'ipynb')

PLUGIN_PATH = './plugins'
PLUGINS = ['ipynb.markup']
```

### Option 1 (recommended)

Write the post using the Jupyter Notebook interface, using markdown, equations, etc.

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extension `.ipynb-meta`.
For example if you have `my_post.ipynb` create a `my_post.ipynb-meta`.

The `.ipynb-meta` should have the markdown metadata (note the empty line at the end, you need that)
of a regular pelican article:

```
Title:
Slug:
Date:
Category:
Tags:
Author:
Summary:

```

### Option 2

Open the `.ipynb` file in a text editor and look for the `metadata` tag should see.

```
{
    "metadata": {
        "name": "My notebook"
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

## Mode B: Liquid Tags

Install the [liquid_tags plugin](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags).
Only the base `liquid_tags.py` and `mdx_liquid_tags.py` files are needed.

In the `pelicanconf.py`:
```
MARKUP = ('md', )

PLUGIN_PATH = './plugins'
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

On the `pelicanconf.py` you can set:

- `IPYNB_USE_META_SUMMARY`: boolean variable to use the summary provided in the `.ipynb-meta` file instead of creating it from the notebook.
- `IPYNB_STOP_SUMMARY_TAGS`: list of tuple with the html tag and attribute (python HTMLParser format)
when the summary creation should stop, this is usefull to generate valid/shorter summaries.
`default = [('div', ('class', 'input')), ('div', ('class', 'output'))]`
- `IPYNB_EXTEND_STOP_SUMMARY_TAGS`: list of tuples to extend the default `IPYNB_STOP_SUMMARY_TAGS`
- `IGNORE_FILES = ['.ipynb_checkpoints']`: prevents pelican from trying to parse notebook checkpoint files
- `IPYNB_IGNORE_CSS = True`: do not include the notebook CSS in the generated output
