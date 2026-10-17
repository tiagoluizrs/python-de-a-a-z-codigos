"""Um programa com um gargalo escondido, para ser medido."""


def slow_dedupe(items):
    seen = []
    for item in items:
        if item not in seen:                    # busca LINEAR em uma lista: O(n) a cada item
            seen.append(item)
    return seen


def fast_dedupe(items):
    return list(dict.fromkeys(items))           # O(n)


def make_strings(n):
    return [str(i) * 3 for i in range(n)]


def checksum(texts):
    return sum(len(t) for t in texts)


def main():
    data = [i % 2000 for i in range(30_000)]
    total = 0
    for _ in range(5):
        total += len(slow_dedupe(data))
        total += len(fast_dedupe(data))
        total += checksum(make_strings(20_000))
    return total


if __name__ == "__main__":
    print(main())
