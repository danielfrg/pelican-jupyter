# Pelican plugin for blogging with IPython Notebooks

## Requirements

- `pelican==3.3`
- `ipython==1.1.0`

Also some libraries are used by `IPython.nbconvert`:
- `Sphinx==1.1.3`
- [pandoc](http://johnmacfarlane.net/pandoc/)

I recommend Python 3 because all the libraries already support it and is the main target of this plugin, python 2.7 should work in any case.

## Installation

Put the plugin (`__init__.py` and `ipythonnb.py`) inside `pelican_project/plugins/ipythonnb` folder.

Then in the `pelicanconf.py`:
```
MARKUP = ('md', 'ipynb')

PLUGIN_PATH = './plugins'
PLUGINS = ['ipythonnb', 'other_plugins']
```

If you host your site on github pages (or just git) you could use it as a submodule:

```
git submodule add git://github.com/danielfrg/pelican-ipythonnb.git plugins/ipythonnb
```

## How to use it

### Option 1 (recommended)

Write the post using the IPython notebook interface, using markdown, equations, etc.

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extension `.ipynb-meta`. So you should have:
`my_post.ipynb` and `my_post.ipynb-meta`

The `ipynb-meta` should have the regular markdown metadata:
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
