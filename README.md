# Pelican plugin for blogging with Jupyter/IPython Notebooks

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


## CSS

There might be some issues/conflicts regarding the CSS that the Jupyter Notebook requires and the pelican theme.

I do my best to make the plugin work with every theme but for obvious reasons I cannot guarantee that it will look good in any pelican theme.

I only try this plugin on the pelican theme for [my blog](https://github.com/danielfrg/danielfrg.github.io-source)
while trying to make it the most general and useful out of the box as possible, a difficult compromise sometimes.

Jupyter Notebook is based on bootstrap so you probably will need your theme to be based on that it if you want the html and css to render nicely.

I try to inject only the necessary CSS, removing Jupyter's bootstrap but fixes are needed in some cases,
if you find this issues I recommend looking at how my theme fixes them.

## Installation

Put the plugin (`__init__.py` and `ipynb.py`) inside the `pelican_project/plugins/ipynb` directory.

Then in the `pelicanconf.py`:
```
MARKUP = ('md', 'ipynb')

PLUGIN_PATH = './plugins'
PLUGINS = ['ipynb']
```

If you host your site on github pages (or just git) you could use it as a submodule:

```
git submodule add git://github.com/danielfrg/pelican-ipynb.git plugins/ipynb
```

## How to use it

### Option 1 (recommended)

Write the post using the IPython notebook interface, using markdown, equations, etc.

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extension `.ipynb-meta`. So you should have:
`my_post.ipynb` and `my_post.ipynb-meta`

The `.ipynb-meta` should have the regular markdown metadata (note the empty line at the end, you need that):

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

Open the `.ipynb` file in a text editor and should see.

```
{
    "metadata": {
        "name": "My notebook"
        ... { A_LOT_OF_OTHER_STUFF } ...
    },
{ A_LOT_OF_OTHER_STUFF }
```

Add the metadata in the `metadata` field like this:

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

## Options

You can include an `#ignore` comment anywhere in a cell of the Jupyter notebook
to ignore it, removing it from the post content.

On the `pelicanconf.py` you can set:

- `IPYNB_USE_META_SUMMARY`: boolean variable to use the summary provided in the `.ipynb-meta` file instead of creating it from the notebook.
- `IPYNB_STOP_SUMMARY_TAGS`: list of tuple with the html tag and attribute (python HTMLParser format)
when the summary creation should stop, this is usefull to generate valid/shorter summaries.
`default = [('div', ('class', 'input')), ('div', ('class', 'output'))]`
- `IPYNB_EXTEND_STOP_SUMMARY_TAGS`: list of tuples to extend the default `IPYNB_STOP_SUMMARY_TAGS`
