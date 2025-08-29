# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

# Add the current directory to the Python path so local extensions can be found
sys.path.insert(0, os.path.abspath("."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "experiment_control_protocol"
copyright = "2023-2025, LECO maintainers"
author = "LECO maintainers"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinx_rtd_theme",
    "sphinx_data_viewer",
    "sphinx_ext.leco_json_viewer",
]

myst_enable_extensions = [
    "colon_fence",
]
myst_heading_anchors = 5

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".venv",
    "venv",
    "env",
    "ENV",
    "env.bak",
    "venv.bak",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = []
