# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Tracer'
copyright = '2021, Alberto Rodriguez'
author = 'Alberto Rodriguez'

# The full version, including alpha/beta/rc tags
release = '1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add source directory
#
#
import os
import sys

todo_include_todos = True

default_imports = []
delimiter_chars = ["=", ">", "<"]
with open(os.path.join("..", "..", "requirements.txt")) as requirements_file:
    requirements_spec = requirements_file.read()
    for r_line in requirements_spec.splitlines():
        delimiters_indices = list(filter(lambda index: index > -1,
                                         [r_line.find("="), r_line.find(">"), r_line.find("<")]))
        default_imports.append(r_line[:min(delimiters_indices)])
autodoc_mock_imports = default_imports
sys.path.append(os.path.abspath(os.path.join("..", "..", "src")))
