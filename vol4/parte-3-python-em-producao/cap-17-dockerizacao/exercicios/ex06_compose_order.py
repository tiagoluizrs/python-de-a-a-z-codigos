"""Exercício 6: a ordem de partida de um ``compose.yaml`` (``depends_on``) e o que fazer com ciclos."""


def startup_waves(services: dict[str, dict]) -> list[list[str]]:
    """``services`` mapeia o nome de cada serviço para um dict que pode ter ``"depends_on"``: uma lista de nomes OU um dict
    ``{nome: {"condition": ...}}`` (as duas formas do Compose; use só os nomes).

    Devolve as ONDAS de partida: a onda 0 tem os serviços sem dependências; a onda ``n`` tem os que só dependem de serviços
    de ondas anteriores (e ao menos um da onda ``n - 1``). Dentro de cada onda, ordem alfabética (os serviços de uma onda
    podem subir em paralelo).

    * dependência de um serviço que não existe: ``ValueError`` com ``"<servico> depende de <nome>, que não existe"``;
    * ciclo (``a -> b -> a``): ``ValueError`` com ``"ciclo: a -> b -> a"`` (o caminho do ciclo, começando pelo menor nome
      que participa dele, voltando a ele no fim);
    * sem serviços: ``[]``."""
    raise NotImplementedError


def shutdown_order(services: dict[str, dict]) -> list[str]:
    """A ordem de DESLIGAMENTO: o inverso da partida (quem depende dos outros é desligado ANTES). Uma lista plana com todos
    os serviços: ondas em ordem inversa, e dentro de cada onda a ordem alfabética."""
    raise NotImplementedError


def dependents_of(services: dict[str, dict], name: str) -> list[str]:
    """Todos os serviços que dependem de ``name``, direta ou indiretamente, em ordem alfabética (o que cai se ``name`` cair).
    ``name`` inexistente: ``ValueError``."""
    raise NotImplementedError
