"""Exercício 4: MVP: o Presenter decide, a visão é burra (e, nos testes, falsa): a lógica de um formulário de login sem nenhuma tela."""


class LoginPresenter:
    """A ``view`` é qualquer objeto com os métodos ``clear_errors()``, ``clear_error(field)``, ``show_error(field, message)``, ``set_busy(busy)`` e ``show_success(name)``.
    ``auth(username, password)`` devolve o NOME de exibição se as credenciais valem, ``None`` se não valem, e pode levantar ``ConnectionError``.

    ``LoginPresenter(view, auth, max_attempts=3)``.

    * ``on_input_changed(field)``: só chama ``view.clear_error(field)``;
    * ``on_submit(username, password)`` devolve ``True`` (entrou) ou ``False``. Os passos, NESTA ORDEM:
      1. se a conta está BLOQUEADA: ``view.clear_errors()``, ``view.show_error("form", "conta bloqueada")`` e ``False`` (sem chamar ``auth``);
      2. ``view.clear_errors()``;
      3. validação (TODOS os erros são mostrados, na ordem usuário e depois senha): o usuário sem as pontas (``strip``) vazio: ``show_error("username", "informe o usuário")``; com 1 ou 2
         caracteres: ``"mínimo de 3 caracteres"``; a senha vazia: ``show_error("password", "informe a senha")``; com menos de 8 caracteres: ``"mínimo de 8 caracteres"``.
         Havendo erro: ``False``, SEM ocupar a visão e SEM chamar ``auth``;
      4. ``view.set_busy(True)``; chama ``auth(username.strip().lower(), password)`` (a senha NÃO é alterada); ``view.set_busy(False)`` acontece SEMPRE (use ``finally``) e ANTES de qualquer mensagem dos passos 5 e 6; outras exceções
         (um ``RuntimeError``, por exemplo) sobem, depois do ``set_busy(False)``;
      5. ``ConnectionError``: ``show_error("form", "sem conexão, tente de novo")``, ``False`` (não conta como tentativa);
      6. ``None``: conta uma tentativa FALHA; se chegou a ``max_attempts`` seguidas, a conta fica bloqueada e a mensagem é ``show_error("form", "conta bloqueada")``; senão
         ``show_error("form", "usuário ou senha inválidos")``; ``False``;
      7. nome devolvido: zera as falhas, ``view.show_success(nome)`` e ``True``;
    * ``reset()``: desbloqueia e zera as falhas;
    * propriedades ``failures`` (falhas seguidas) e ``blocked``."""

    def __init__(self, view, auth, max_attempts: int = 3):
        raise NotImplementedError

    def on_input_changed(self, field: str) -> None:
        raise NotImplementedError

    def on_submit(self, username: str, password: str) -> bool:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    @property
    def failures(self) -> int:
        raise NotImplementedError

    @property
    def blocked(self) -> bool:
        raise NotImplementedError
