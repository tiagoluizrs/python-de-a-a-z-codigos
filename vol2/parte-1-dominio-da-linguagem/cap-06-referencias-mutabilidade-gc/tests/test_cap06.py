import copy
import gc


class Plain:
    pass


# --- Exercício 1
def test_has_cycle(load_exercise):
    has_cycle = load_exercise("ex01_find_cycle").has_cycle
    a = []
    a.append(a)
    assert has_cycle(a)

    d = {}
    d["self"] = d
    assert has_cycle(d)

    shared = [1, 2]
    assert not has_cycle([shared, shared])
    assert not has_cycle({"a": shared, "b": (shared, "x")})
    assert not has_cycle(5)


def test_has_cycle_objects_and_depth(load_exercise):
    has_cycle = load_exercise("ex01_find_cycle").has_cycle
    x, y = Plain(), Plain()
    x.other, y.other = y, x
    assert has_cycle(x)
    assert has_cycle([1, [2, [3, x]]])
    z = Plain()
    z.child = Plain()
    assert not has_cycle(z)
    # ciclo passando por uma tupla
    inner = []
    t = (inner,)
    inner.append(t)
    assert has_cycle(t)


# --- Exercício 2
def test_deepcopy_independent(load_exercise):
    my_deepcopy = load_exercise("ex02_simple_deepcopy").my_deepcopy
    original = {"a": [1, 2, {"x": {3, 4}}], "t": (1, [2])}
    clone = my_deepcopy(original)
    assert clone == original
    assert clone["a"] is not original["a"]
    assert clone["a"][2] is not original["a"][2]
    assert clone["t"][1] is not original["t"][1]
    clone["a"].append(9)
    assert 9 not in original["a"]


def test_deepcopy_shared_and_cycles(load_exercise):
    my_deepcopy = load_exercise("ex02_simple_deepcopy").my_deepcopy
    shared = [1]
    clone = my_deepcopy({"a": shared, "b": shared})
    assert clone["a"] is clone["b"]
    assert clone["a"] is not shared

    loop = [1]
    loop.append(loop)
    copied = my_deepcopy(loop)
    assert copied is not loop
    assert copied[1] is copied

    memo: dict = {}
    my_deepcopy(shared, memo)
    assert id(shared) in memo


def test_deepcopy_matches_stdlib(load_exercise):
    my_deepcopy = load_exercise("ex02_simple_deepcopy").my_deepcopy
    data = [1, "s", (1, 2), {"k": [None, 2.5]}, {1, 2}]
    assert my_deepcopy(data) == copy.deepcopy(data)
    t = (1, "a")
    assert my_deepcopy(t) is t


# --- Exercício 3
def test_weak_cache(load_exercise):
    mod = load_exercise("ex03_weak_cache")
    cache = mod.WeakCache()
    a = cache.get("a")
    assert cache.get("a") is a
    assert cache.created == 1
    assert len(cache) == 1
    del a
    gc.collect()
    assert len(cache) == 0
    again = cache.get("a")
    assert cache.created == 2
    assert again.name == "a"


# --- Exercício 4
def test_leak_growth(load_exercise):
    leak_growth = load_exercise("ex04_leak_growth").leak_growth
    store: list[bytes] = []

    def leaky() -> None:
        store.append(bytes(1000))

    def clean() -> None:
        tmp = [bytes(1000) for _ in range(3)]
        assert len(tmp) == 3

    assert leak_growth(leaky, rounds=200) > 150_000
    assert leak_growth(clean, rounds=200) < 20_000


def test_leak_growth_ignores_collected_cycles(load_exercise):
    leak_growth = load_exercise("ex04_leak_growth").leak_growth

    def cyclic() -> None:
        a: list = [bytes(1000)]
        a.append(a)

    # o gc.collect() interno limpa os ciclos: não é vazamento
    assert leak_growth(cyclic, rounds=200) < 20_000


# --- Exercício 5
def test_release_mode(load_exercise):
    release_mode = load_exercise("ex05_release_mode").release_mode

    assert release_mode(lambda: Plain()) == "refcount"

    def cyclic():
        a = Plain()
        a.me = a
        return a

    assert release_mode(cyclic) == "gc"

    keep = []

    def immortalized():
        obj = Plain()
        keep.append(obj)
        return obj

    assert release_mode(immortalized) == "never"
    assert gc.isenabled()
