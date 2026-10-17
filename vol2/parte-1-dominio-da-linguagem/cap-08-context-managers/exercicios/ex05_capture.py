"""Exercício 5: capturar o que o código imprime."""


def capture_prints():
    """Context manager que captura tudo que for impresso no bloco.

    Deve devolver (via ``as``) um objeto com um método ``lines()`` que
    retorna a lista de linhas impressas (sem o ``\\n`` final) e restaurar
    o ``sys.stdout`` ao sair, mesmo com exceção. Dica:
    ``contextlib.redirect_stdout`` e ``io.StringIO``.

    Exemplo::

        with capture_prints() as cap:
            print("a"); print("b")
        assert cap.lines() == ["a", "b"]
    """
    raise NotImplementedError
