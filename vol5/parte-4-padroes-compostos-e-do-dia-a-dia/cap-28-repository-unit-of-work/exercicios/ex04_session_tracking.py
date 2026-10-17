"""Exercício 4: uma "Session" em miniatura: mapa de identidade + rastreamento de mudanças (a ideia por trás dos ORMs): o commit grava SÓ o que mudou."""
import sqlite3
from dataclasses import dataclass

# Esquema (criado pelos testes):  items(id INTEGER PRIMARY KEY, name TEXT NOT NULL, qty INTEGER NOT NULL)


@dataclass
class Item:
    """(Pronto, NÃO edite.) Um item MUTÁVEL: o código muda ``item.qty`` direto, sem chamar nenhum ``save()``."""

    id: int
    name: str
    qty: int


class Session:
    """``Session(conn)``: gerencia objetos ``Item`` de uma conexão sqlite.

    * ``get(item_id)``: se o item já foi carregado (ou adicionado) nesta sessão, devolve o MESMO objeto SEM consultar o banco; senão faz UM ``SELECT``, guarda o objeto e um INSTANTÂNEO dele
      ``(name, qty)``, e o devolve. Item inexistente (ou já marcado para apagar): ``KeyError(f"item inexistente: {item_id}")``;
    * ``add(item)``: id que já existe na sessão OU no banco (um ``SELECT``): ``ValueError(f"item já existe: {item.id}")``; senão registra o item como NOVO (o ``INSERT`` só acontece no
      ``commit``) e ``get(item.id)`` passa a devolvê-lo sem consultar o banco;
    * ``delete(item)``: o item precisa ser um objeto GERENCIADO por esta sessão (a mesma instância, ``is``; senão ``ValueError("item não gerenciado")``); marca para apagar (o ``DELETE`` só
      acontece no ``commit``); depois disso ``get`` do id levanta ``KeyError``;
    * ``dirty()``: a lista ORDENADA dos ids dos itens carregados cujo ``(name, qty)`` hoje difere do instantâneo (mudar e depois voltar ao valor original NÃO é "sujo");
    * ``commit()``: grava, nesta ordem, um ``INSERT`` por item novo, um ``UPDATE items SET name = ?, qty = ? WHERE id = ?`` por item sujo e um ``DELETE`` por item apagado; depois
      ``conn.commit()``. Itens limpos NÃO geram nenhum comando de escrita. Depois do commit tudo está "limpo": os instantâneos são atualizados, os novos contam como carregados e os apagados
      saem da sessão;
    * ``rollback()``: ``conn.rollback()`` e ESQUECE tudo (mapa de identidade, instantâneos, novos e apagados): um ``get`` seguinte lê o banco de novo e devolve um objeto NOVO;
    * como gerenciador de contexto: ``__enter__`` devolve a sessão; ``__exit__`` NÃO confirma nada sozinho: sair sem ``commit()`` (com ou sem exceção) faz ``rollback()``; a exceção sobe."""

    def __init__(self, conn: sqlite3.Connection):
        raise NotImplementedError

    def get(self, item_id: int) -> Item:
        raise NotImplementedError

    def add(self, item: Item) -> None:
        raise NotImplementedError

    def delete(self, item: Item) -> None:
        raise NotImplementedError

    def dirty(self) -> list[int]:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError
