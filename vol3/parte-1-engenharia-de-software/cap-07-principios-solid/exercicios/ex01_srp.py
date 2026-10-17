"""Exercício 1 (S): medir a coesão de uma classe (LCOM4) lendo o código com ``ast``."""
import ast


def lcom4(source: str) -> dict[str, int]:
    """Para cada classe definida em ``source`` (texto Python; pode estar indentado: use ``textwrap.dedent``), devolve o número de
    GRUPOS de métodos desconectados (``{"NomeDaClasse": n}``, na ordem em que as classes aparecem no texto; classes aninhadas contam
    como classes separadas).

    * considere só os métodos (``def`` e ``async def`` diretamente no corpo da classe), EXCETO ``__init__``;
    * dois métodos são CONECTADOS se (a) ambos leem ou escrevem o MESMO atributo ``self.x`` (``x`` não é um método da classe), ou (b) um
      deles CHAMA o outro como ``self.metodo(...)`` ou o referencia como ``self.metodo``;
    * a conexão é TRANSITIVA (se A liga a B e B liga a C, os três são UM grupo);
    * um método que não usa nenhum atributo e não chama ninguém forma o SEU PRÓPRIO grupo;
    * classe sem métodos (além de ``__init__``): 0 grupos;
    * métodos de classes aninhadas não contam para a classe de fora.
    Interprete: 1 = coesa; 2 ou mais = a classe tem partes que não se falam (candidata a ser dividida)."""
    raise NotImplementedError


def split_candidates(source: str, threshold: int = 2) -> list[str]:
    """Os nomes das classes de ``source`` com ``lcom4 >= threshold``, em ordem alfabética."""
    raise NotImplementedError


def attribute_groups(source: str, class_name: str) -> list[list[str]]:
    """Os GRUPOS de métodos de ``class_name`` (o mesmo critério de ``lcom4``), cada grupo com os nomes dos métodos em ordem alfabética, e
    os grupos ordenados pelo primeiro nome de cada um. Classe inexistente: ``KeyError``. Serve para dizer COMO dividir."""
    raise NotImplementedError
