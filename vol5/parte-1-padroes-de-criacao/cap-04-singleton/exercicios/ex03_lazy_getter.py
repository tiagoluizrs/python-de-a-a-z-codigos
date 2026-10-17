"""Exercício 3: o "singleton" em forma de função: um valor criado sob demanda, uma única vez, com segurança para threads."""


def make_getter(loader):
    """Devolve ``get()``, que chama ``loader()`` na primeira vez e guarda o resultado; as próximas chamadas devolvem o valor guardado.

    * seguro com threads: com 8 threads chamando ao mesmo tempo, ``loader`` roda exatamente UMA vez (``threading.Lock`` com dupla verificação);
    * se ``loader`` levantar uma exceção, ela sobe e NADA fica guardado (a próxima chamada tenta de novo);
    * ``get.is_loaded()`` diz se já há um valor guardado (sem carregar);
    * ``get.cache_clear()`` esquece o valor (a próxima chamada recarrega); ``loader`` que devolve ``None`` conta como um valor válido (``is_loaded()`` vira
      verdadeiro: use um marcador interno, não ``None``, para "ainda não carregou")."""
    raise NotImplementedError
