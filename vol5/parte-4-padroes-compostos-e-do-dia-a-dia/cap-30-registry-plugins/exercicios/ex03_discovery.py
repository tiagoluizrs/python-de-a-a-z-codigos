"""Exercício 3: a DESCOBERTA de plugins: os módulos de um pacote (``pkgutil``) e os pacotes instalados (``entry points``), com os plugins quebrados isolados."""
import importlib
import importlib.metadata
import pkgutil
from dataclasses import dataclass, field

SUPPORTED_API = 2                                               # (Pronto.) a versão da API de plugins que este aplicativo entende


@dataclass
class Discovery:
    """(Pronto, NÃO edite.) O resultado: ``plugins`` (nome -> módulo ou objeto) e ``errors`` (nome do módulo/entry point -> mensagem)."""

    plugins: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)


def discover(package_name: str) -> Discovery:
    """Importa os módulos de um PACOTE e devolve os que são plugins válidos.

    * ``package_name`` precisa ser um pacote importável (``importlib.import_module``); um módulo comum (sem ``__path__``): ``ValueError(f"{package_name} não é um pacote")``; se o próprio
      pacote não importa, o erro sobe;
    * percorra os módulos com ``pkgutil.iter_modules(pacote.__path__)`` e IGNORE os que começam com ``"_"``; importe cada um (``f"{package_name}.{modulo}"``);
    * um plugin VÁLIDO tem ``NAME`` (``str`` não vazia), ``API_VERSION == SUPPORTED_API`` e ``run`` chamável; as verificações são feitas NESTA ORDEM e a primeira que falha define a mensagem
      em ``errors[modulo]``: ``"falta NAME"``, ``f"versão de API não suportada: {valor}"`` (``None`` se não existe) e ``"falta run"``;
    * uma exceção (``Exception``) ao IMPORTAR o módulo: ``errors[modulo] = f"{TipoDoErro}: {mensagem}"``, e a descoberta CONTINUA com os outros;
    * dois módulos com o mesmo ``NAME``: o primeiro (em ordem de módulo) fica e o segundo vai para ``errors[modulo] = f"nome repetido: {NAME} (já usado por {primeiro_modulo})"``;
    * ``plugins`` mapeia ``NAME`` -> módulo, com as chaves em ORDEM ALFABÉTICA."""
    raise NotImplementedError


def load_entry_points(group: str) -> Discovery:
    """Carrega os *entry points* de um GRUPO (``importlib.metadata.entry_points(group=group)``), em ordem alfabética do nome (e do valor, no empate).

    * ``plugins[nome] = entry_point.load()``;
    * uma exceção (``Exception``) em ``load()``: ``errors[nome] = f"{TipoDoErro}: {mensagem}"`` e segue adiante;
    * um nome que aparece de novo (de outro pacote instalado): o primeiro fica e o segundo vai para ``errors[nome] = f"nome repetido: {nome}"``;
    * um grupo sem entry points: ``Discovery()`` vazio."""
    raise NotImplementedError
