"""Gabarito do exercício 2."""


def primes_up_to(n: int) -> list[int]:
    if n < 2:
        return []
    is_prime = [True] * (n + 1)          # índice = o próprio número
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p <= n:
        if is_prime[p]:
            # múltiplos menores que p*p já foram riscados por primos menores
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
        p += 1
    return [number for number, flag in enumerate(is_prime) if flag]
