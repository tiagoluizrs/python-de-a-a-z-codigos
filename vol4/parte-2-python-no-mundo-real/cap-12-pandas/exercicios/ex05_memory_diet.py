"""Exercício 5: uma dieta de memória automática e segura para um DataFrame."""
import pandas as pd


def slim(df: pd.DataFrame, max_unique_ratio: float = 0.5) -> pd.DataFrame:
    """Devolve uma CÓPIA de ``df`` com tipos menores, SEM mudar nenhum valor e sem alterar ``df``:

    * colunas inteiras (com ou sem sinal) viram o MENOR inteiro que comporta os valores (``uint8`` quando todos forem
      >= 0 e couberem, senão ``int8``/``int16``...); use ``pd.to_numeric(..., downcast=...)``;
    * colunas de texto (``str`` ou ``object``) viram ``category`` quando ``nunique / len`` for MENOR que
      ``max_unique_ratio`` (e a coluna não for vazia); caso contrário continuam como estão;
    * colunas ``float64`` viram ``float32`` SOMENTE se a conversão ida e volta não alterar nenhum valor
      (``astype("float32").astype("float64")`` igual ao original, ``NaN`` contam como iguais);
    * as demais colunas (datas, bool, etc.) ficam intactas; ordem das colunas e índice preservados."""
    raise NotImplementedError


def savings(before: pd.DataFrame, after: pd.DataFrame) -> dict:
    """``{"before": bytes, "after": bytes, "ratio": before / after}``, medindo com ``memory_usage(deep=True)``
    somado; ``ratio`` arredondado para 2 casas."""
    raise NotImplementedError
