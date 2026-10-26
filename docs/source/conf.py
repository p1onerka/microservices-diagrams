import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath("../.."))


class _IdentityDecorator:
    """Stand-in for @mcp.tool() so Sphinx can import the server without the mcp package."""

    def __call__(self, fn):
        return fn


class _FakeMCPServer:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self):
        return _IdentityDecorator()

    def run(self, *args, **kwargs):
        pass


# codeql_mcp imports mcp at module level. The package is not a docs dependency,
# and its decorator would hide the real functions from autodoc.
_mcp_server = MagicMock()
_mcp_server.MCPServer = _FakeMCPServer
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = _mcp_server
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "microservices-diagrams"
copyright = "2025, Ksenia Kotelnikova (p1onerka)"
author = "Ksenia Kotelnikova (p1onerka)"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_theme = 'alabaster'
# html_static_path = ['_static']
