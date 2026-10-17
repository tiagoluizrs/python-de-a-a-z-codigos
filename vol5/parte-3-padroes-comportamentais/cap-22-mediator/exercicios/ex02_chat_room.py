"""Exercício 2: uma sala de bate-papo: o mediador é quem decide quem recebe o quê (silenciar, palavras proibidas, mensagens privadas)."""


class ChatRoom:
    """Os usuários só conhecem a sala. ``deliver`` de cada usuário é uma função ``deliver(sender, text, private) -> None``.

    * ``join(name, deliver)``: entra na sala; nome repetido: ``ValueError(f"nome já em uso: {name}")``; ``deliver`` não chamável: ``TypeError``;
    * ``leave(name)``: sai (``LookupError(f"usuário desconhecido: {name}")`` se não está); também apaga os silenciamentos que envolvem esse nome;
    * ``members()``: os nomes em ordem alfabética;
    * ``mute(by, who)``: ``by`` deixa de receber mensagens de ``who`` (ambos precisam estar na sala, senão ``LookupError`` como acima; ``by == who``: ``ValueError("não pode silenciar a si mesmo")``);
      ``unmute(by, who)`` desfaz (silenciar de novo ou desfazer sem existir não é erro);
    * ``ban_word(word)``: passa a recusar mensagens que contenham a palavra (sem diferenciar maiúsculas de minúsculas, como PALAVRA inteira: ``"gato"`` bloqueia ``"o gato dorme"`` mas NÃO
      ``"gatos"``; as palavras são separadas por espaço e pontuação ``.,;:!?`` é ignorada nas pontas de cada palavra);
    * ``send(sender, text, to=None)``: ``sender`` precisa estar na sala (``LookupError``); mensagem com palavra proibida: ``ValueError("palavra proibida: ...")`` (a primeira, na ordem em
      que aparece no texto) e NADA é entregue nem registrado; ``to=None``: entrega a todos os outros membros; ``to="x"``: só a ``x`` (``LookupError`` se não está; ``private=True`` na entrega);
      quem silenciou o remetente NÃO recebe; devolve QUANTAS entregas foram feitas; o remetente NUNCA recebe a própria mensagem;
    * ``history``: lista (cópia) de ``(sender, to, text)`` das mensagens ACEITAS (mesmo as que ninguém recebeu por silenciamento)."""

    def __init__(self):
        raise NotImplementedError

    def join(self, name: str, deliver) -> None:
        raise NotImplementedError

    def leave(self, name: str) -> None:
        raise NotImplementedError

    def members(self) -> list[str]:
        raise NotImplementedError

    def mute(self, by: str, who: str) -> None:
        raise NotImplementedError

    def unmute(self, by: str, who: str) -> None:
        raise NotImplementedError

    def ban_word(self, word: str) -> None:
        raise NotImplementedError

    def send(self, sender: str, text: str, to: str | None = None) -> int:
        raise NotImplementedError

    @property
    def history(self) -> list:
        raise NotImplementedError
