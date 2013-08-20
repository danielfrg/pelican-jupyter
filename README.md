# Pelican plugin for blogging with iPython Notebooks

## Requirements

Mainly: pelican==3.2.2 and ipython==1.0.0

Also this libraries are used by the IPython.nbconvert:
Sphinx==1.1.3 and [pandoc](http://johnmacfarlane.net/pandoc/)

I test this under Python 3, Python 2 in theory works but I do not test it.

I recommend using Python 3 because all the libraries already support it.

## Installation

Put the plugin (`ipythonnb.py`) inside the `pelican_project/plugins/` folder.

Then in the `pelicanconf.py`:
```
MARKUP = ('md', 'ipynb')

PLUGIN_PATH = './plugins'
PLUGINS = ['ipythonnb', 'other_plugins']
```

## How to blog

### Option 1 (recomended)

Write the post using the iPython notebook interface, using markdown, equations, etc.

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extention `.ipynb-meta`. So you should have:
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

### Option 2

Open the `.ipynb` file in a text editor and should see.

```
{
    "metadata": {
        "name": "Super iPython NB"
    },
{ A_LOT_OF_OTHER_STUFF }
```

Add the metadata in the `metadata` json tag:

```
{
 "metadata": {
        "name": "Super iPython NB",
        "Title": "Blogging with iPython notebooks in pelican",
        "Date": "2013-2-16",
        "Category": "Category",
        "Tags": "tag2, tag2",
        "slug": "slug-slug-slug",
        "Author": "Me"
    },
    { A_LOT_OF_OTHER_STUFF }
```