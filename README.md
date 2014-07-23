# Pelican plugin for blogging with IPython Notebooks

## Requirements

Python 2.7 and 3.4 are supported

- `pelican==3.4`
- `ipython==2.1`

Libraries needed by `IPython.nbconvert`:
- [pandoc](http://johnmacfarlane.net/pandoc/)

For advanced options:
- `beautifulsoup==4.3.2`

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

The `ipynb-meta` should have the regular markdown metadata (note the empty line at the end, you need that):

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
        "name": "Super IPython NB"
    },
{ A_LOT_OF_OTHER_STUFF }
```

Add the metadata in the `metadata` field like this:

```
{
 "metadata": {
        "name": "Super IPython NB",
        "Title": "Blogging with IPython notebooks in pelican",
        "Date": "2013-2-16",
        "Category": "Category",
        "Tags": "tag2, tag2",
        "slug": "slug-slug-slug",
        "Author": "Me"
    },
    { A_LOT_OF_OTHER_STUFF }
```

## Options

You can include an `#ignore` comment anywhere in a cell of the ipython notebook
to ignore it, removing it from the post content.

On the `pelicanconf.py` you can use:

- `IPYNB_STOP_SUMMARY_TAGS`: list of tuple with the html tag and attribute (python HTMLParser format)
when the summary creation should stop, this is usefull to generate valid/shorter summaries.
`default = [('div', ('class', 'input')), ('div', ('class', 'output'))]`
- `IPYNB_EXTEND_STOP_SUMMARY_TAGS`: list of tuples to extend the default `IPYNB_STOP_SUMMARY_TAGS`
## TODO

Toggable cells: javascript code is easy but I am not sure about the how the UI should look.
