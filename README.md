# Pelican plugin for Jupyter/IPython Notebooks

This plugin provides two modes to use Jupyter/IPython notebooks in [Pelican](https://getpelican.com):

1. As a new markup language so `.ipynb` files are recognized as a valid filetype for an article
2. As a liquid tag based on the [liquid tags plugin](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags) so notebooks can be
included in a regular post using Markdown (`.md`) files.

## Requirements

Python 2.7 and 3.4 are supported.

The main objective is to run with the latest version of Jupyter/IPython
but there is a good chance the plugin will work correctly with older versions of Pelican and Jupyter/IPython.
The recommended version of libraries are:

- `pelican>=3.5`
- `jupyter>=1.0`
- `ipython>=4.0`
- `nbconvert>=4.0`
- `markdown>=2.6.1`

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

```
git submodule add git://github.com/danielfrg/pelican-ipynb.git plugins/ipynb
```

See below for additional settings in your `pelicanconf.py`, depending on the mode you are using.

## Mode A: Markup Mode

Setup usage of the `markup` plugin in `pelicanconf.py`:

```python
MARKUP = ('md', 'ipynb')

PLUGIN_PATHS = ['./plugins']
PLUGINS = ['ipynb.markup']
```

### Option 1: Separate MD metadata file

Place the `.ipynb` file in the content folder and create a new file with the
same name as the ipython notebook with extension `.nbdata`.
For example if you have `my_post.ipynb` create a `my_post.nbdata`.

The `.nbdata` should contain the metadata like a regular Markdown based article:

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

### Option 2: Metadata cell in notebook

With this option, the metadata is extracted from the first cell of
the notebook (which should be a Markdown cell), this cell is then ignored on the rendering of the notebook.
This avoid the burden of maintaining a separate file or manually editing the
json in the `.ipynb` file like the previous options.

First, enable the "metacell" mode globally in your config

```python
IPYNB_USE_METACELL = True
```

Now, you can put the metadata in the first notebook cell in Markdown mode, like this:

```markdown
- title: My notebook
- author: John Doe
- date: 2018-05-11
- category: pyhton
- tags: pip
```

### Option 3: metadata field in notebook

Open the `.ipynb` file in a text editor or using the Jupyter Notebook editor under "File"
and look for the `metadata` tag should see.

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

Edit this the `metadata` tag to have the required markdown fields:

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

## Mode B: Liquid tags

**Requires** to install the pelican [liquid_tags plugin](https://github.com/getpelican/pelican-plugins/tree/master/liquid_tags).
Only the base `liquid_tags.py` and `mdx_liquid_tags.py` files are required.

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

Personally I like Method A - Option 1 since I write the Notebooks first and then I just add
the metadata file and keeps the notebook clean.

The Liquid tag mode provide more flexibility to combine an existing notebook code or output with extra text on a Markdown.
You can also combine 2 or more notebooks in this mode.
The only problem with the liquid tag mode is that it doesn't generate a summary for the article
automatically from the notebook so you have to write it in the `.md` file that includes
the notebook liquid tag.

You can use both modes at the same time but you are probably going to see a exception that
prevents conflicts, ignore it.

## Note on CSS

If the notebooks look bad on your pelican theme this can help. There is some issues/conflicts regarding the CSS that the Jupyter Notebook requires and the pelican theme.

I do my best to make the plugin work with every theme but for obvious reasons I cannot guarantee that it will look good in any pelican theme.

I only try this plugin on the pelican theme for [my blog](https://github.com/danielfrg/danielfrg.com)
while trying to make it the most general and useful out of the box as possible, a difficult compromise sometimes.

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
