"""Exercício 1: injeção pelo construtor: um serviço que RECEBE tudo o que usa (e que, por isso, se testa com dublês de uma linha)."""


class PaymentDeclined(Exception):
    """(Pronto, NÃO edite.) O meio de pagamento recusou a cobrança."""


class CheckoutService:
    """``CheckoutService(orders, payments, mailer, clock)``: guarda os quatro colaboradores e NÃO cria nenhum deles (nem lê relógio, nem variável global).

    Os colaboradores (os testes passam dublês):

    * ``orders.next_id()`` devolve o próximo id (``int``); ``orders.save(order)`` grava;
    * ``payments.charge(customer, total_cents)`` devolve o id do pagamento (``str``) ou levanta ``PaymentDeclined``; ``payments.refund(payment_id)`` estorna;
    * ``mailer.send(to, subject)`` envia (pode levantar ``ConnectionError``); ``clock()`` devolve o ``datetime`` de agora.

    ``checkout(customer, items)``: ``items`` é uma lista de ``(nome, quantidade, valor_unitario_em_centavos)``.

    * lista vazia: ``ValueError("carrinho vazio")``; quantidade que não seja um ``int > 0`` (``bool`` NÃO vale): ``ValueError("quantidade inválida")``; valor unitário que não seja
      um ``int >= 0``: ``ValueError("valor inválido")``; TUDO isto ANTES de qualquer chamada aos colaboradores;
    * ``total = soma de quantidade * valor``; as chamadas, NESTA ORDEM: ``orders.next_id()``, ``payments.charge(customer, total)``, ``orders.save(order)``, ``mailer.send(...)``;
    * ``order`` é o dicionário ``{"id", "customer", "total", "payment_id", "at": clock(), "email_sent"}``; ``save`` recebe o pedido SEM a chave ``"email_sent"``;
    * ``PaymentDeclined`` na cobrança: nada é gravado, nenhum e-mail sai e a exceção sobe;
    * qualquer exceção em ``orders.save`` DEPOIS de cobrar: estorna com ``payments.refund(payment_id)`` e a exceção original continua subindo;
    * o e-mail: ``mailer.send(customer, f"pedido {id} confirmado")``; um ``ConnectionError`` ao enviar NÃO desfaz o pedido: ``order["email_sent"]`` é ``False`` (e ``True`` se enviou);
    * devolve o ``order`` (com ``email_sent``)."""

    def __init__(self, orders, payments, mailer, clock):
        raise NotImplementedError

    def checkout(self, customer: str, items: list) -> dict:
        raise NotImplementedError
