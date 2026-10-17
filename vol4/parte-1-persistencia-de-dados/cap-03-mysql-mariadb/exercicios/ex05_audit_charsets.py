"""Exercício 5: auditar o conjunto de caracteres do banco (a armadilha do utf8)."""


def audit_charsets(conn, schema):
    """Devolve uma lista ORDENADA de tuplas ``(tabela, coluna, charset)`` de TODAS as colunas
    de texto do ``schema`` cujo conjunto de caracteres NÃO seja ``utf8mb4`` (consulte
    ``information_schema.COLUMNS``, coluna ``CHARACTER_SET_NAME``; colunas que não são texto
    têm ``NULL`` e são ignoradas). Use parâmetros ``%s``. Esquema inexistente: lista vazia."""
    raise NotImplementedError


def fix_statements(findings):
    """Para cada ``(tabela, coluna, charset)``, devolva ``ALTER TABLE `tabela` CONVERT TO
    CHARACTER SET utf8mb4`` UMA vez por tabela (sem repetir), na ordem de aparição.
    Nomes entre crases, dobrando crases internas."""
    raise NotImplementedError
