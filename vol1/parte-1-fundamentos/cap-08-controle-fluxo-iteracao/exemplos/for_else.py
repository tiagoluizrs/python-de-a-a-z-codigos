"""for/else: o else roda quando o laco termina sem break."""


def first_negative(values):
    for index, value in enumerate(values):
        if value < 0:
            print("achou", value, "na posicao", index)
            break
    else:
        # chegamos aqui somente se NAO houve break
        print("nenhum negativo")


first_negative([4, 7, -2, 9])
first_negative([4, 7, 9])
first_negative([])             # laco vazio: o else tambem roda


def is_prime(n):
    if n < 2:
        return False
    for divisor in range(2, int(n ** 0.5) + 1):
        if n % divisor == 0:
            break
    else:
        return True
    return False


print([n for n in range(20) if is_prime(n)])

# continue nao impede o else; return dentro do laco tambem o pula
for n in range(3):
    continue
else:
    print("else roda: continue nao e break")

# a alternativa sem else: uma flag (mais verbosa)
found = False
for n in [1, 2, 3]:
    if n == 2:
        found = True
        break
print("com flag:", found)

# ... e a alternativa mais curta quando basta saber SE existe
print("com any:", any(n == 2 for n in [1, 2, 3]))
