"""O problema da escrita dupla (banco + fila) e o padrão Outbox transacional."""
import random
import sqlite3

random.seed(7)


class Broker:
    """Uma fila 'de rede': publicar pode falhar DEPOIS de o banco já ter confirmado (o caso difícil)."""

    def __init__(self, failure_rate: float):
        self.messages: list[str] = []
        self.failure_rate = failure_rate

    def publish(self, message: str) -> None:
        if random.random() < self.failure_rate:
            raise ConnectionError("broker fora do ar")
        self.messages.append(message)


def make_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.executescript("""
        create table orders (id integer primary key, total integer not null);
        create table outbox (id integer primary key autoincrement, topic text not null, body text not null, published integer not null default 0);
    """)
    return db


N = 1000
FAIL = 0.10

# 1. escrita dupla ingênua: grava no banco e DEPOIS publica
db, broker = make_db(), Broker(FAIL)
errors = 0
for order_id in range(N):
    with db:
        db.execute("insert into orders values (?, ?)", (order_id, 100))
    try:
        broker.publish(f"order_created:{order_id}")
    except ConnectionError:
        errors += 1                                      # o pedido JÁ está no banco; o evento nunca será enviado
orders = db.execute("select count(*) from orders").fetchone()[0]
print(f"escrita dupla (banco, depois fila), {FAIL:.0%} de falha ao publicar:")
print(f"  pedidos gravados {orders} | eventos publicados {len(broker.messages)} | PERDIDOS {orders - len(broker.messages)} (inconsistência silenciosa)")

# 2. publicar ANTES de gravar troca o problema: eventos de pedidos que nunca existiram
db, broker = make_db(), Broker(0.0)
phantom = 0
for order_id in range(N):
    broker.publish(f"order_created:{order_id}")
    try:
        if random.random() < FAIL:
            raise sqlite3.OperationalError("disco cheio")
        with db:
            db.execute("insert into orders values (?, ?)", (order_id, 100))
    except sqlite3.OperationalError:
        phantom += 1
print(f"publicar antes de gravar: {phantom} eventos de pedidos que NÃO existem (fantasmas)")

# 3. Outbox: o evento é gravado NA MESMA TRANSAÇÃO do pedido; um relé publica depois
db, broker = make_db(), Broker(FAIL)
for order_id in range(N):
    with db:                                              # uma transação: ou os dois, ou nenhum
        db.execute("insert into orders values (?, ?)", (order_id, 100))
        db.execute("insert into outbox (topic, body) values (?, ?)", ("order_created", str(order_id)))


def relay(db, broker, batch=100) -> tuple[int, int]:
    """Lê as pendentes, publica, marca como publicadas. Se publicar falha, a linha continua pendente (tenta na próxima rodada)."""
    sent = failed = 0
    rows = db.execute("select id, body from outbox where published = 0 order by id limit ?", (batch,)).fetchall()
    for row_id, body in rows:
        try:
            broker.publish(f"order_created:{body}")
        except ConnectionError:
            failed += 1
            continue
        with db:
            db.execute("update outbox set published = 1 where id = ?", (row_id,))
        sent += 1
    return sent, failed


rounds = 0
while db.execute("select count(*) from outbox where published = 0").fetchone()[0]:
    sent, failed = relay(db, broker)
    rounds += 1
orders = db.execute("select count(*) from orders").fetchone()[0]
print(f"\noutbox: pedidos {orders} | eventos publicados {len(set(broker.messages))} | perdidos {orders - len(set(broker.messages))} | rodadas do relé {rounds}")

# 4. a contrapartida: o relé pode publicar e cair ANTES de marcar -> duplicata (por isso o consumidor precisa ser idempotente)
db, broker = make_db(), Broker(0.0)
with db:
    db.execute("insert into orders values (1, 100)")
    db.execute("insert into outbox (topic, body) values ('order_created', '1')")
row_id, body = db.execute("select id, body from outbox where published = 0").fetchone()
broker.publish(f"order_created:{body}")                   # publicou...
# ...e o relé morreu antes do UPDATE: a linha continua pendente
relay(db, broker)                                         # a rodada seguinte publica de novo
print(f"relé que cai entre publicar e marcar: a mensagem sai {len(broker.messages)} vezes (entrega 'pelo menos uma vez': consumidor idempotente)")

# 5. custo do outbox: uma linha a mais na mesma transação
import time

db = make_db()
start = time.perf_counter()
for i in range(5000):
    with db:
        db.execute("insert into orders values (?, ?)", (i, 100))
t_plain = time.perf_counter() - start
db = make_db()
start = time.perf_counter()
for i in range(5000):
    with db:
        db.execute("insert into orders values (?, ?)", (i, 100))
        db.execute("insert into outbox (topic, body) values ('order_created', ?)", (str(i),))
t_outbox = time.perf_counter() - start
print(f"\ncusto: 5.000 pedidos sem outbox {t_plain * 1e3:6.0f} ms | com a linha de outbox na mesma transação {t_outbox * 1e3:6.0f} ms ({t_outbox / t_plain:.2f}x)")
