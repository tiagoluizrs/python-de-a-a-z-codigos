"""Exercício 1: validar a tabela [project] de um pyproject.toml."""
import re


def validate_project(project, files_exist=lambda path: True):
    """Devolve a lista ORDENADA de códigos de problema de ``project`` (o dict da
    tabela ``[project]``). ``files_exist(caminho)`` diz se um arquivo existe.

    Códigos:

    * ``"no-name"``; ``"bad-name"`` se ``name`` não casar com
      ``^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$``;
    * ``"no-version"``: sem ``version`` E ``"version"`` não está em
      ``dynamic``; ``"bad-version"``: ``version`` fora de
      ``^\\d+(\\.\\d+)*((a|b|rc)\\d+)?(\\.post\\d+)?(\\.dev\\d+)?$``;
    * ``"no-requires-python"``; ``"bad-requires-python"`` se não for uma lista de
      cláusulas separadas por vírgula, cada uma ``(~=|==|!=|<=|>=|<|>)`` seguido de
      número com pontos (``>=3.10,<4``; espaços toleráveis);
    * ``"no-description"``;
    * ``"no-readme"`` (chave ausente) ou ``"missing-readme-file"`` (``readme`` é
      um texto e ``files_exist`` recusa; se for dict, use ``readme["file"]``);
    * ``"no-license"``: sem ``license`` e sem ``license-files``;
      ``"license-table"``: ``license`` é um dict (forma antiga, obsoleta pela
      PEP 639: use um texto SPDX como ``"MIT"``);
    * ``"bad-script"``: algum valor de ``scripts`` fora de ``^[\\w.]+:[\\w.]+$``."""
    raise NotImplementedError
