"""while, break, continue, else e o operador morsa."""
from collections import deque

# while com condicao: nao sabemos quantas voltas
n = 27
steps = 0
while n != 1:                      # sequencia de Collatz
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    steps += 1
print("collatz(27) levou", steps, "passos")

# while True + break: o "meio" do laco decide a saida
inputs = deque(["3", "x", "4", "", "99"])
total = 0
while True:
    raw = inputs.popleft()
    if raw == "":
        break                  # sentinela: fim da entrada
    if not raw.isdigit():
        print("ignorando", repr(raw))
        continue               # pula para a proxima volta
    total += int(raw)
print("total:", total, "| sobrou:", list(inputs))

# o mesmo laco com o operador morsa (:=)
inputs = deque(["3", "x", "4", "", "99"])
total = 0
while (raw := inputs.popleft()) != "":
    if raw.isdigit():
        total += int(raw)
print("total com morsa:", total)

# lendo blocos de tamanho fixo (padrao classico)
import io
stream = io.BytesIO(b"abcdefghij")
while chunk := stream.read(4):     # b"" e falso: fim do arquivo
    print(chunk)

# else no while: roda se o laco terminou SEM break
attempts = 0
while attempts < 3:
    attempts += 1
    if attempts == 10:
        break
else:
    print("else executou: nenhum break")
