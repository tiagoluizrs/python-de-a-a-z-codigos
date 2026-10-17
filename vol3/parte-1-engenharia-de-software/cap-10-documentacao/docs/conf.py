"""Configuração do Sphinx."""
project = "shapes"
author = "Autor do livro"
release = "0.1.0"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode", "sphinx.ext.doctest"]
html_theme = "alabaster"
language = "pt_BR"
autodoc_member_order = "bysource"
