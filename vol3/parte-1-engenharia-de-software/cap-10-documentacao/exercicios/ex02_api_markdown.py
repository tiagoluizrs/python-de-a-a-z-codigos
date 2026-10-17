"""Exercício 2: gerar a referência da API em Markdown."""
import inspect
import types


def module_to_markdown(module):
    """Gera Markdown a partir de ``module`` (um ``types.ModuleType``).

    Formato EXATO (linhas separadas por ``"\\n"``; termine com ``"\\n"``):

    * ``# <nome do módulo>`` e uma linha em branco; depois o RESUMO do módulo
      (primeira linha de ``inspect.getdoc``; ``(sem documentação)`` se não
      houver) e uma linha em branco;
    * para cada nome PÚBLICO, em ordem alfabética (``__all__`` se existir; senão
      os nomes sem ``_`` inicial definidos no próprio módulo: ``obj.__module__ ==
      module.__name__``): ``## `<nome><assinatura>` (classe)`` ou ``(função)``,
      linha em branco, o resumo, linha em branco;
    * para classes, depois do resumo, uma linha ``- `<método><assinatura>`: <resumo>``
      por método público (sem ``_`` inicial), em ordem alfabética, e uma linha
      em branco ao final. A assinatura do método inclui ``self``.
    Sem documentação: ``(sem documentação)``."""
    raise NotImplementedError
