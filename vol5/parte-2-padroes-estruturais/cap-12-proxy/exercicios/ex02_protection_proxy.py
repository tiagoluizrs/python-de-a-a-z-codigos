"""Exercício 2: um proxy de PROTEÇÃO: controla quem pode ler, chamar e alterar, e registra cada tentativa."""


class ProtectedProxy:
    """``ProtectedProxy(target, user, roles, rules)``: ``user`` é um texto, ``roles`` um conjunto de papéis do usuário e ``rules`` um dict
    ``{nome_do_atributo: papel_exigido}``.

    * LER ``proxy.nome``: se ``nome`` está em ``rules`` e o papel exigido NÃO está em ``roles``: ``PermissionError(f"{user} não pode acessar {nome}")`` (isso vale
      já ao obter o método, antes de chamá-lo); caso contrário devolve ``getattr(target, nome)``. Nomes fora de ``rules`` passam livres;
    * ESCREVER ``proxy.nome = valor``: mesma regra, com a mensagem ``f"{user} não pode alterar {nome}"``; permitido, faz ``setattr`` no alvo;
    * nomes que começam com ``_`` NÃO são repassados ao alvo: ler (via ``__getattr__``) ou escrever um desses nomes levanta ``AttributeError(f"acesso a {nome} bloqueado")`` (e
      NÃO entram na auditoria); os atributos internos do próprio proxy continuam acessíveis normalmente por dentro;
    * ``audit``: propriedade que devolve uma CÓPIA da lista de tentativas, cada uma uma tupla ``(user, nome, acao, permitido)`` com ``acao`` igual a
      ``"read"`` ou ``"write"`` e ``permitido`` verdadeiro ou falso, na ordem em que aconteceram (inclusive as negadas);
    * ``audit`` e ``can(nome)`` são do próprio proxy: ``can(nome)`` diz se o usuário poderia LER ``nome`` (não registra nada na auditoria);
    * o proxy não guarda nada no alvo: os atributos internos (``_target``, ``_user``, ``_roles``, ``_rules``, ``_audit``) vão com ``object.__setattr__``."""

    def __init__(self, target, user: str, roles: set, rules: dict):
        raise NotImplementedError

    def __getattr__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, value):
        raise NotImplementedError

    @property
    def audit(self) -> list:
        raise NotImplementedError

    def can(self, name: str) -> bool:
        raise NotImplementedError
