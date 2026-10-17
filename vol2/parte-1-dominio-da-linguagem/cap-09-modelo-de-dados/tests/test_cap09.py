import pytest


def test_money_voices(load_exercise):
    Money = load_exercise("ex01_money").Money
    price = Money(1990)
    assert repr(price) == "Money(1990, 'BRL')"
    assert str(price) == "R$ 19,90"
    assert str(Money(5, "USD")) == "USD 0.05"
    assert f"{price}" == "R$ 19,90"
    assert f"{price:plain}" == "19.90"
    assert f"{price:code}" == "BRL 19.90"
    with pytest.raises(ValueError):
        f"{price:xyz}"
    assert repr([Money(1)]) == "[Money(1, 'BRL')]"


def test_money_bool_eq_hash(load_exercise):
    Money = load_exercise("ex01_money").Money
    assert not Money(0) and Money(1)
    assert Money(100) == Money(100) and Money(100) != Money(100, "USD")
    assert Money(100) != 100
    assert hash(Money(100)) == hash(Money(100))
    assert {Money(100): "a"}[Money(100)] == "a"


def test_inventory(load_exercise):
    Inventory = load_exercise("ex02_inventory").Inventory
    inv = Inventory(apple=3, pear=5)
    assert len(inv) == 2 and "apple" in inv and "kiwi" not in inv
    assert list(inv) == ["apple", "pear"]
    inv["kiwi"] = 7
    assert inv["kiwi"] == 7 and len(inv) == 3
    inv["pear"] = 0                      # zero remove
    assert "pear" not in inv
    del inv["apple"]
    assert repr(inv) == "Inventory({'kiwi': 7})"
    assert bool(inv) and not Inventory()
    with pytest.raises(KeyError):
        inv["plum"]
    with pytest.raises(ValueError):
        inv["x"] = -1
    with pytest.raises(ValueError):
        inv["x"] = 1.5


def test_playlist(load_exercise):
    Playlist = load_exercise("ex03_playlist").Playlist
    songs = Playlist(["a", "b", "c", "d", "e"])
    assert len(songs) == 5 and songs[0] == "a" and songs[-1] == "e"
    sliced = songs[1:4]
    assert isinstance(sliced, Playlist) and repr(sliced) == "Playlist(['b', 'c', 'd'])"
    assert repr(songs[::-1]) == "Playlist(['e', 'd', 'c', 'b', 'a'])"
    assert list(songs) == ["a", "b", "c", "d", "e"]
    assert list(reversed(songs)) == ["e", "d", "c", "b", "a"]
    with pytest.raises(IndexError):
        songs[10]
    with pytest.raises(TypeError):
        songs[1.5]


def test_grid(load_exercise):
    Grid = load_exercise("ex04_grid").Grid
    g = Grid(2, 3)
    assert len(g) == 2 and g[1, 2] == 0
    g[1, 2] = 9
    g[0, -1] = 4
    assert g[1, 2] == 9 and g[0, 2] == 4 and g[-1, -1] == 9
    row = g[1]
    row[0] = 123                          # cópia: não afeta a grade
    assert g[1, 0] == 0 and row == [123, 0, 9]
    assert 9 in g and 5 not in g
    other = Grid(2, 3)
    other[1, 2], other[0, 2] = 9, 4
    assert g == other and g != Grid(2, 3) and g != "x"
    with pytest.raises(IndexError):
        g[2, 0]
    with pytest.raises(IndexError):
        g[0, 3]


def test_attr_view(load_exercise):
    AttrView = load_exercise("ex05_attr_view").AttrView
    source = {"host": "x", "port": 1, "a-b": 7}
    view = AttrView(source)
    source["host"] = "mudou"
    assert view.host == "x" and view.port == 1 and getattr(view, "a-b") == 7
    assert dir(view) == ["a-b", "host", "port"]
    assert hasattr(view, "host") and not hasattr(view, "nope")
    with pytest.raises(AttributeError, match="nope"):
        view.nope
    with pytest.raises(AttributeError):
        view.host = "y"
    with pytest.raises(AttributeError):
        view.new = 1
    with pytest.raises(AttributeError):
        del view.host
