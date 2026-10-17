"""Exercício 2: um adaptador de FUNÇÃO genérico: renomear argumentos, dar padrões e converter dados sem editar a função original."""
import functools


def adapt(fn, *, rename=None, defaults=None, convert_args=None, convert_result=None):
    """Devolve uma função adaptada que chama ``fn``.

    * ``rename``: ``{nome_novo: nome_antigo}``; a função adaptada aceita os NOMES NOVOS como argumentos nomeados e os traduz. Argumentos posicionais
      passam direto. Passar o nome novo E o antigo (ou o novo duas vezes via ``**``): ``TypeError(f"argumento repetido: {nome_antigo}")``;
    * ``defaults``: ``{nome_antigo: valor}`` usados quando o argumento (já traduzido) não foi dado por nome (se o argumento foi passado
      posicionalmente, ele não é substituído: use ``inspect.signature(fn).bind_partial`` para saber quais nomes já foram dados);
    * ``convert_args``: ``{nome_antigo: função}``; aplicada ao valor do argumento (dado ou padrão) ANTES de chamar ``fn``;
    * ``convert_result``: função aplicada ao resultado de ``fn``;
    * a função adaptada preserva ``__name__`` e ``__doc__`` de ``fn`` (``functools.wraps``) e tem ``__wrapped__``;
    * nomes em ``rename``, ``defaults`` ou ``convert_args`` que ``fn`` não tem como parâmetro: ``ValueError(f"parâmetro inexistente: {nome}")`` na CRIAÇÃO
      do adaptador (para ``rename``, vale o nome ANTIGO)."""
    raise NotImplementedError
