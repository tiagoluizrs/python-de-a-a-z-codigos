"""Exercício 2: um CASO DE USO que depende de PORTAS (Protocol), não de implementações."""
from dataclasses import dataclass


class TransferError(Exception):
    pass


@dataclass(frozen=True)
class Transfer:
    source: str
    target: str
    cents: int


def transfer_money(accounts, ledger, notifier, clock, source: str, target: str, cents: int) -> Transfer:
    """Transfere ``cents`` (inteiro, centavos) de ``source`` para ``target`` usando quatro PORTAS (objetos com estes métodos;
    nada de importar banco ou rede):

    * ``accounts.balance(account_id) -> int`` (``KeyError`` se a conta não existir) e ``accounts.set_balance(account_id, cents)``;
    * ``ledger.record(source, target, cents, when)`` registra a transferência (``when`` vem de ``clock.now()``);
    * ``notifier.send(account_id, text)``;
    * ``clock.now() -> str``.

    Regras e ORDEM (a ordem importa para não deixar o sistema pela metade):

    1. ``cents`` precisa ser positivo e ``source != target`` (``TransferError``);
    2. as duas contas precisam existir: se faltar, ``TransferError(f"conta inexistente: {id}")``, ANTES de alterar qualquer coisa;
    3. saldo insuficiente: ``TransferError("saldo insuficiente")``, sem tocar em nada;
    4. grave os dois saldos novos e registre no ``ledger`` com ``clock.now()``;
    5. SÓ DEPOIS de gravar, notifique os DOIS lados (``"enviou <cents>"`` para a origem e ``"recebeu <cents>"`` para o destino);
       se a notificação falhar (qualquer exceção), a transferência vale: NÃO desfaça e NÃO propague a exceção.

    Devolve ``Transfer(source, target, cents)``."""
    raise NotImplementedError
