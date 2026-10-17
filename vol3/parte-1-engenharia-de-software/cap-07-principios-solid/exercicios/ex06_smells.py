"""Exercício 6: detectores de "cheiros" de SOLID lendo o código com ``ast`` (OCP, LSP e DIP)."""
import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class Smell:
    kind: str          # "OCP", "LSP" ou "DIP"
    where: str         # "NomeDaFuncao" ou "Classe.metodo"
    line: int          # linha do achado (1-based, no texto recebido, depois de ``textwrap.dedent``)


def find_smells(source: str) -> list[Smell]:
    """Analisa ``source`` (texto Python; use ``textwrap.dedent``) e devolve os cheiros encontrados, ordenados por ``(line, kind)``:

    * ``OCP``: em uma função ou método, uma cadeia ``if/elif`` com 4 ou mais ramos (contando o ``if`` e cada ``elif``), em que TODAS as condições
      comparam o MESMO nome (uma variável ou parâmetro) com uma constante (``x == "a"``, ``x == 1``, ``x in ("a", "b")`` também conta);
      reporte UM achado por cadeia, na linha do ``if`` inicial; ``where`` é o nome da função (``"Classe.metodo"`` para métodos);
    * ``LSP``: em um MÉTODO de classe que tem classe base declarada (``class B(A):``), um ``raise NotImplementedError`` (com ou sem argumentos)
      NO CORPO do método (reporte na linha do ``raise``); métodos de classes SEM base não contam (é normal em classes abstratas simples);
    * ``DIP``: dentro de uma função ou método (não no nível do módulo), uma chamada cujo nome (``x.y.Nome(...)`` ou ``Nome(...)``, olhe só o
      último nome) está em ``{"SMTP", "SMTP_SSL", "connect", "Session", "Client", "Redis", "MongoClient", "create_engine", "urlopen"}``
      ou é ``datetime.now``/``datetime.utcnow``/``time.time`` (``now``, ``utcnow`` com ``datetime`` antes; ``time.time``): infraestrutura
      criada DENTRO da regra. Reporte UM achado por chamada, na linha dela; ``where`` como acima.
    Funções aninhadas contam como funções com o seu próprio nome (``outer.inner``... use apenas o nome da função interna)."""
    raise NotImplementedError
