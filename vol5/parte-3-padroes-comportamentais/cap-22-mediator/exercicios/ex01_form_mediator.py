"""Exercício 1: o Mediator clássico: os componentes de um formulário só conhecem o mediador, e as regras de interação moram nele."""


class Component:
    """Base: guarda o ``mediator`` e oferece ``changed()``, que chama ``mediator.notify(self)`` (se houver mediador)."""

    def __init__(self, mediator=None):
        raise NotImplementedError

    def changed(self) -> None:
        raise NotImplementedError


class Checkbox(Component):
    """``checked`` começa ``False``. ``toggle()`` inverte o valor e avisa o mediador (``changed``). ``set(value)`` define o valor e só avisa se ele MUDOU."""

    def toggle(self) -> None:
        raise NotImplementedError

    def set(self, value: bool) -> None:
        raise NotImplementedError


class TextBox(Component):
    """``text`` começa ``""``. ``type(text)`` define o texto e avisa o mediador SÓ se o texto MUDOU (o mesmo texto de novo não avisa)."""

    def type(self, text: str) -> None:
        raise NotImplementedError


class Button(Component):
    """``enabled`` começa ``False`` e ``clicks`` em ``0``. ``click()``: se desabilitado, ``RuntimeError("botão desabilitado")``; senão acrescenta 1 a ``clicks`` e avisa o
    mediador; devolve o resultado de ``mediator.submitted()`` (se não houver mediador: ``None``). Quem altera ``enabled`` é o mediador."""

    def click(self):
        raise NotImplementedError


class Label(Component):
    """``text`` começa ``""``. Quem altera é o mediador."""


class FormMediator:
    """Cria os quatro componentes (``agree``: ``Checkbox``, ``email``: ``TextBox``, ``submit``: ``Button``, ``error``: ``Label``), todos ligados a este mediador. A regra, aplicada em
    ``notify(sender)`` (a cada aviso de ``agree`` ou ``email``; avisos de ``submit`` e ``error`` são IGNORADOS):

    * ``agree`` desmarcado: ``error.text = "aceite os termos"`` e botão desabilitado;
    * ``agree`` marcado e ``email.text`` sem ``"@"`` (ou com ``@`` no início/fim): ``error.text = "e-mail inválido"`` e botão desabilitado;
    * senão: ``error.text = ""`` e botão HABILITADO.
    Antes de qualquer interação, o estado inicial já deve refletir a regra (``error.text == "aceite os termos"``, botão desabilitado): chame a regra no construtor.
    ``submitted()``: devolve ``{"email": email.text}`` e guarda em ``self.submissions`` (lista) esse mesmo dict. ``notify`` NÃO deve causar laços: alterar ``enabled`` e ``text`` dos
    componentes não avisa ninguém (esses atributos são simples)."""

    def __init__(self):
        raise NotImplementedError

    def notify(self, sender: Component) -> None:
        raise NotImplementedError

    def submitted(self) -> dict:
        raise NotImplementedError
