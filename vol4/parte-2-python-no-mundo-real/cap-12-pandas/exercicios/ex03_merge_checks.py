"""Exercício 3: juntar tabelas SEM multiplicar nem perder linhas sem perceber."""
import pandas as pd


def enrich(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta as colunas de ``customers`` (chave ``customer_id``) a cada pedido (``left join``).

    * o resultado tem EXATAMENTE as linhas de ``orders``, na mesma ordem e com índice ``0..n-1``;
    * se ``customers`` tiver ``customer_id`` repetido, levante ``ValueError`` com a mensagem
      ``"clientes duplicados: [ids]"`` (os ids repetidos, em ordem crescente, em uma lista);
    * pedidos de cliente inexistente continuam no resultado (colunas do cliente vazias)."""
    raise NotImplementedError


def orphan_orders(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Os pedidos cujo ``customer_id`` NÃO existe em ``customers`` (anti-join), com as colunas de ``orders``,
    na ordem original e índice ``0..k-1``."""
    raise NotImplementedError


def customers_without_orders(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Os clientes que NÃO têm nenhum pedido (anti-join), com as colunas de ``customers``, ordem original, índice
    ``0..k-1``."""
    raise NotImplementedError
