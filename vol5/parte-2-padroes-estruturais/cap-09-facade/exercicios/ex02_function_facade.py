"""Exercício 2: uma facade em forma de FUNÇÃO sobre ``csv``, ``json`` e ``pathlib``, com escrita atômica e erros do seu domínio."""


class ConversionError(Exception):
    """O erro do domínio: a facade traduz as exceções de ``csv``, ``json`` e do sistema de arquivos para esta."""


def csv_to_json(src, dst, *, delimiter: str = ",", numeric: bool = True, encoding: str = "utf-8") -> int:
    """Lê o CSV ``src`` (com cabeçalho), escreve a lista de registros em ``dst`` como JSON (``indent=2``, ``ensure_ascii=False``, com ``\\n`` no fim)
    e devolve quantos registros foram escritos.

    * ``numeric=True`` converte valores que parecem inteiros (``"42"``, ``"-7"``) em ``int`` e decimais (``"3.5"``, ``"-0.25"``) em ``float``;
      o resto fica texto (incluindo vazio); ``numeric=False`` mantém tudo como texto;
    * arquivo de entrada inexistente: ``ConversionError(f"arquivo não encontrado: {src}")``;
    * CSV vazio (sem nem o cabeçalho): ``ConversionError("csv vazio")``; uma linha com MAIS colunas que o cabeçalho:
      ``ConversionError(f"linha {n} tem colunas demais")`` (``n`` a partir de 2: a linha 1 é o cabeçalho); linha com MENOS colunas: os campos
      que faltam viram ``""``;
    * ESCRITA ATÔMICA: escreva primeiro em um arquivo temporário na MESMA pasta de ``dst`` (``dst`` + ``".tmp"``) e depois ``Path.replace`` para ``dst``;
      se algo falhar no meio, ``dst`` NÃO pode ter sido criado nem alterado, e o temporário não pode sobrar;
    * ``src`` e ``dst`` podem ser ``str`` ou ``Path``."""
    raise NotImplementedError
