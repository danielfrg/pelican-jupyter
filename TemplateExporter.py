from __future__ import absolute_import, print_function, unicode_literals


import os
import json


from nbconvert.exporters import HTMLExporter


class TemplateExporter(HTMLExporter):
    """
    Custom Tempalte Exporter.

    Supply your custom html tempaltes to export the ipython notebook.
    """

    def __init__(self, article_filename, pelican_settings, *args, **kwargs):
        self.settings = pelican_settings 
        self.article_filename = article_filename 

        super(HTMLExporter, self).__init__(*args, **kwargs)

    @property
    def template_path(self):
        """
        Add any custom template paths defined in pelican_conf.py.
        """
        template_path = self.settings.get("IPYTHON_TEMPLATE_PATH", [])
        if template_path:
            return super(HTMLExporter, self).template_path + [template_path]
        else:
            return super(HTMLExporter, self).template_path

    def _template_file_default(self):
        """
        We can supply templates specific to each article or one template for all
        the ipython article.

        For article specific tempalte name the template file same as the article
        file name with extension ".tpl"

        """
        return self.get_template_file()

    def get_template_file(self):
        """
        Get the ipython template file to be used with the exporter.

        @param filename: Notebook filename with extension.
        @return template file name.
        """
        template_path = self.settings.get("IPYTHON_TEMPLATE_PATH", "")
        article_filename = os.path.basename(self.article_filename).split(".")[0]

        article_tpl_name = os.path.join(template_path, article_filename + ".tpl")
        article_default_tpl_name = os.path.join(template_path, "article.tpl")
        if os.path.exists(article_tpl_name):
            template_name = article_filename
        elif os.path.exists(article_default_tpl_name):
            template_name = "article"
        else:
            template_name = "basic" # Use the Ipython default one.

        return template_name
