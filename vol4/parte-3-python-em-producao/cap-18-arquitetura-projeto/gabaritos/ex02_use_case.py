"""Gabarito do exercício 2."""
from dataclasses import dataclass


class TransferError(Exception):
    pass


@dataclass(frozen=True)
class Transfer:
    source: str
    target: str
    cents: int


def transfer_money(accounts, ledger, notifier, clock, source, target, cents):
    if cents <= 0:
        raise TransferError("valor deve ser positivo")
    if source == target:
        raise TransferError("origem e destino iguais")
    balances = {}
    for account_id in (source, target):
        try:
            balances[account_id] = accounts.balance(account_id)
        except KeyError:
            raise TransferError(f"conta inexistente: {account_id}") from None
    if balances[source] < cents:
        raise TransferError("saldo insuficiente")
    accounts.set_balance(source, balances[source] - cents)
    accounts.set_balance(target, balances[target] + cents)
    ledger.record(source, target, cents, clock.now())
    for account_id, text in ((source, f"enviou {cents}"), (target, f"recebeu {cents}")):
        try:
            notifier.send(account_id, text)
        except Exception:
            pass
    return Transfer(source, target, cents)
