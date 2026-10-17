"""Exercício 4: encerrar com educação quando o orquestrador manda SIGTERM (o ``docker stop``)."""
import signal
import threading


class GracefulShutdown:
    """Instala tratadores de ``SIGTERM`` e ``SIGINT`` que apenas MARCAM o pedido de encerramento (sem sair na hora).

    Use como gerenciador de contexto: ao entrar, instala os tratadores (guardando os anteriores); ao sair, RESTAURA os
    anteriores (mesmo com exceção). Funciona só na thread principal."""

    def __init__(self):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *exc):
        raise NotImplementedError

    @property
    def requested(self) -> bool:
        """``True`` depois que um sinal chegou."""
        raise NotImplementedError

    @property
    def signal_name(self) -> str | None:
        """O nome do primeiro sinal recebido (``"SIGTERM"``/``"SIGINT"``) ou ``None``."""
        raise NotImplementedError

    def wait(self, timeout: float | None = None) -> bool:
        """Espera até um sinal chegar (sem consumir CPU); devolve ``True`` se chegou e ``False`` se o tempo acabou."""
        raise NotImplementedError


def serve(handle_one, shutdown: GracefulShutdown, pending: list, grace_seconds: float = 1.0) -> dict:
    """Um laço de serviço: enquanto ``shutdown.requested`` for falso e houver itens em ``pending`` (uma lista de itens a
    processar, consumida do começo), chame ``handle_one(item)``. Quando o encerramento for pedido, pare de PEGAR itens
    novos, mas termine o item em andamento. Devolve ``{"handled": n, "left": m, "reason": r}``: ``reason`` é
    ``"done"`` (acabaram os itens) ou o nome do sinal (``"SIGTERM"``...). ``grace_seconds`` é o tempo que o orquestrador
    dá: se o item em andamento demorar mais que isso depois do pedido, apenas registre ``"late": True`` no resultado
    (não interrompa); sem demora, ``"late": False``."""
    raise NotImplementedError
