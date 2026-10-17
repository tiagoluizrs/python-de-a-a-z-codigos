"""Exercício 6: verificação de saúde com dependências críticas, tolerância a lentidão e limite de tempo."""


class HealthChecker:
    def __init__(self):
        """Sem verificações registradas."""
        raise NotImplementedError

    def add(self, name: str, fn, critical: bool = True, timeout: float = 0.5) -> None:
        """Registra uma verificação: ``fn()`` não recebe argumentos; ``None`` (ou qualquer retorno) significa saudável e
        qualquer exceção significa falha. ``critical`` diz se a falha derruba o serviço; ``timeout`` (segundos) é o limite
        desta verificação. Nome repetido: ``ValueError``."""
        raise NotImplementedError

    def run(self) -> tuple[int, dict]:
        """Executa TODAS as verificações ao mesmo tempo (threads) e devolve ``(http_status, corpo)``:

        * cada verificação vira ``{"status": "ok"}``, ``{"status": "fail", "error": "<mensagem da exceção>"}`` ou
          ``{"status": "timeout"}`` (passou do limite) em ``corpo["checks"][nome]``; todas com ``"ms"`` (duração, ``int``);
        * ``corpo["status"]``: ``"down"`` se alguma verificação CRÍTICA falhou ou estourou o tempo; senão ``"degraded"`` se
          alguma NÃO crítica falhou; senão ``"ok"``;
        * ``http_status``: ``503`` para ``"down"``, ``200`` para os outros;
        * a chamada inteira NÃO pode demorar mais que o maior ``timeout`` (mais uma folga pequena), mesmo que uma
          verificação trave por muito mais tempo: não use ``with ThreadPoolExecutor`` (a saída do ``with`` espera as
          threads terminarem; use ``shutdown(wait=False)``);
        * sem verificações registradas: ``(200, {"status": "ok", "checks": {}})``."""
        raise NotImplementedError
