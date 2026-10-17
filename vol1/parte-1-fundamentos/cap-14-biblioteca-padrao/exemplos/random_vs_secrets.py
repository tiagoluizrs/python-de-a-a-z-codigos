"""random (reprodutível, previsível) x secrets (imprevisível)."""
import random
import secrets
import timeit

# random com a mesma semente gera SEMPRE a mesma "senha"
a = random.Random(2026)
b = random.Random(2026)
print(a.randrange(10**8), b.randrange(10**8))

# Quem observa saídas do Mersenne Twister prevê as próximas:
# o estado tem 624 palavras de 32 bits (mais um índice) e é recuperável.
state = random.getstate()
print(len(state[1]))

# secrets usa a fonte do sistema operacional (os.urandom)
print(len(secrets.token_hex(16)), len(secrets.token_urlsafe(16)))
print(secrets.compare_digest("abc", "abc"))
print(secrets.randbelow(10) in range(10))

n = 100_000
t_random = timeit.timeit(lambda: random.getrandbits(64), number=n)
t_secrets = timeit.timeit(lambda: secrets.randbits(64), number=n)
print(f"random : {t_random / n * 1e9:6.0f} ns por chamada")
print(f"secrets: {t_secrets / n * 1e9:6.0f} ns por chamada")
