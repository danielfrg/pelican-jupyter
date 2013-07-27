# Pelican plugin for blogging with iPython Notebooks

## Installation

Download plugin files: `plugin/*` including the `plugin/nbconverter` directory
and put those files in `pelican_project/plugins/`

Then in the `pelicanconf.py`:
```
PLUGIN_PATH = './plugins'
PLUGINS = ['ipythonnb', ...]
MARKUP = ('md', 'ipynb')
```

## Add the CSS to the theme

Download the `ipython.css` file from the `assets` directory and place it in your
theme static folder. Then include the CSS on the theme template:

```
{% if article.ipython %}
    <link rel="stylesheet" href="/theme/css/ipython.css">
{% endif %}
```

## How to blog

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