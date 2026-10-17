"""Exercício 1: MVC clássico: modelo (Observer + Memento), visões e um controlador com desfazer/refazer."""


class Model:
    """O estado e as regras; NÃO conhece as visões. As tarefas são ``[texto, feito]``; ``items`` devolve uma LISTA NOVA de tuplas ``(texto, feito)``.

    * ``subscribe(observer)``: o ``observer`` tem ``update(model)``, chamado a cada mudança, NA ORDEM de inscrição; ``unsubscribe(observer)``: ``ValueError("não inscrito")`` se não estava;
    * ``add(text)``: texto vazio ou só espaços: ``ValueError("texto vazio")``; senão acrescenta ``[text, False]`` (o texto SEM os espaços das pontas);
    * ``toggle(index)`` e ``remove(index)`` (índices de ``0``): fora do intervalo (inclusive negativo): ``IndexError(f"tarefa inexistente: {index}")``;
    * toda mudança avisa os observadores UMA vez (depois de mudar); erro de validação NÃO avisa ninguém;
    * ``snapshot()``: uma cópia INDEPENDENTE do estado; ``restore(snapshot)``: recoloca o estado (também uma cópia, para o mesmo snapshot poder ser usado de novo) e avisa;
    * ``batch()``: gerenciador de contexto: dentro dele as mudanças NÃO avisam; ao sair do ``with`` mais externo (mesmo que por exceção, que continua subindo) avisa UMA vez, se algo mudou
      (nenhuma mudança: nenhum aviso). Lotes aninhados funcionam."""

    def __init__(self):
        raise NotImplementedError

    @property
    def items(self) -> list[tuple[str, bool]]:
        raise NotImplementedError

    def subscribe(self, observer) -> None:
        raise NotImplementedError

    def unsubscribe(self, observer) -> None:
        raise NotImplementedError

    def add(self, text: str) -> None:
        raise NotImplementedError

    def toggle(self, index: int) -> None:
        raise NotImplementedError

    def remove(self, index: int) -> None:
        raise NotImplementedError

    def snapshot(self):
        raise NotImplementedError

    def restore(self, snapshot) -> None:
        raise NotImplementedError

    def batch(self):
        raise NotImplementedError


class TextView:
    """``TextView(model, out)``: inscreve-se no ``model`` ao ser criada; a cada ``update`` acrescenta a ``out`` (uma lista) o texto ``"[x] leite | [ ] pão"`` (``"(vazio)"`` se não há tarefas)."""

    def __init__(self, model: Model, out: list):
        raise NotImplementedError

    def update(self, model: Model) -> None:
        raise NotImplementedError


class StatsView:
    """``StatsView(model, out)``: igual, mas acrescenta ``"1/2 feitas"`` (feitas/total; sem tarefas: ``"0/0 feitas"``)."""

    def __init__(self, model: Model, out: list):
        raise NotImplementedError

    def update(self, model: Model) -> None:
        raise NotImplementedError


class Controller:
    """Traduz linhas de texto em chamadas ao modelo, com desfazer e refazer. ``handle(line)`` devolve ``None``. Os números das tarefas começam em ``1``.

    * ``add <texto>``; ``done <n>`` (alterna feito/aberto); ``rm <n>``; ``clear`` (remove TODAS as tarefas feitas de uma vez, em UM lote: uma só notificação e UM passo no histórico;
      se não há tarefas feitas, não faz nada, não notifica e não cria passo); ``undo``; ``redo``;
    * comando desconhecido (inclusive linha vazia): ``ValueError(f"comando desconhecido: {comando}")``; ``n`` que não é um inteiro: ``ValueError(f"número inválido: {texto}")``;
      ``n`` fora de ``1..len``: ``IndexError(f"tarefa inexistente: {n}")``;
    * todo comando que MUDA o modelo guarda um ``snapshot()`` ANTES e o põe no histórico; um comando que FALHA não cria passo e não notifica; um comando novo apaga o "refazer";
    * ``undo`` sem passos: ``LookupError("nada para desfazer")``; ``redo`` sem passos: ``LookupError("nada para refazer")``; ambos restauram via ``restore`` (o ``undo`` guarda o estado atual
      para o ``redo``)."""

    def __init__(self, model: Model):
        raise NotImplementedError

    def handle(self, line: str) -> None:
        raise NotImplementedError
