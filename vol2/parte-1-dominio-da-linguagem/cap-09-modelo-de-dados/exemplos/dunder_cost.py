"""O custo de chamar a sintaxe, o método explícito e um método Python."""
import timeit


class Native(list):
    pass


class Custom:
    def __init__(self):
        self.items = [1, 2, 3]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


plain = [1, 2, 3]
native = Native([1, 2, 3])
custom = Custom()
namespace = {"plain": plain, "native": native, "custom": custom}
cases = [
    ("len(list)", "len(plain)"),
    ("len(subclasse de list)", "len(native)"),
    ("len(custom)  __len__ em Python", "len(custom)"),
    ("custom.__len__()  chamada direta", "custom.__len__()"),
    ("plain[1]", "plain[1]"),
    ("custom[1]  __getitem__ em Python", "custom[1]"),
]
for label, statement in cases:
    seconds = min(timeit.repeat(statement, globals=namespace,
                                number=1_000_000, repeat=5)) / 1_000_000
    print(f"{label:<36}{seconds * 1e9:7.1f} ns")
