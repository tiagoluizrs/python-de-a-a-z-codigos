"""Exercício 1: ler uma docstring no estilo Google."""


def parse_google_docstring(text):
    """Interpreta ``text`` (uma docstring já limpa, como ``inspect.getdoc``) e
    devolve um dict com:

    * ``"summary"``: a primeira linha;
    * ``"description"``: o texto entre o resumo e a primeira seção (sem as linhas
      em branco das pontas; ``""`` se não houver);
    * ``"args"``: ``{nome: descrição}`` da seção ``Args:`` (cada argumento é uma
      linha ``nome: texto`` ou ``nome (tipo): texto``, com recuo; linhas
      seguintes MAIS recuadas continuam a descrição, unidas por um espaço);
      o dict também guarda o tipo em ``"arg_types"``: ``{nome: tipo}`` só para
      os que declararam ``(tipo)``;
    * ``"returns"``: o texto da seção ``Returns:`` (linhas unidas por espaço) ou ``""``;
    * ``"raises"``: ``{ExceçãoNome: descrição}`` da seção ``Raises:``;
    * ``"example"``: o texto da seção ``Example:`` ou ``Examples:`` (com o recuo
      removido, linhas preservadas) ou ``""``.

    Seções são linhas como ``Args:`` sem recuo. Seções ausentes dão vazio
    (``{}`` ou ``""``)."""
    raise NotImplementedError
