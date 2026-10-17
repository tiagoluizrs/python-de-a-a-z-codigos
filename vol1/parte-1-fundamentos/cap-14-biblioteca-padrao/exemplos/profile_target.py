"""Alvo para os profilers: uma função quente e uma fria."""


def hot(n):
    return sum(i * i for i in range(n))


def cold():
    return sorted(range(1000), reverse=True)


def main():
    for _ in range(200):
        hot(20_000)
    cold()


if __name__ == "__main__":
    main()
