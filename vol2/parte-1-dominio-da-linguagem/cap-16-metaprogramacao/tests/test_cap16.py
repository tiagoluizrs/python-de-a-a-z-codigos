import pytest


def test_handler_registers_and_returns_same_class(load_exercise):
    module = load_exercise("ex01_registry")

    @module.handler("csv")
    class Csv:
        pass

    assert module.HANDLERS["csv"] is Csv and Csv.handler_name == "csv"
    with pytest.raises(ValueError):
        @module.handler("csv")
        class Again:
            pass


def test_auto_repr(load_exercise):
    auto_repr = load_exercise("ex02_auto_repr").auto_repr

    @auto_repr
    class P:
        def __init__(self, x, y=0, *args, **kwargs):
            self.x, self.y = x, y

    assert repr(P(1)) == "P(x=1, y=0)" and repr(P("a", 2)) == "P(x='a', y=2)"

    @auto_repr
    class Q:
        def __init__(self, a):
            self.a = a

        def __repr__(self):
            return "custom"

    assert repr(Q(1)) == "custom"


def test_exporter_registry(load_exercise):
    Exporter = load_exercise("ex03_plugin_base").Exporter

    class Csv(Exporter, fmt="csv"):
        def export(self, data):
            return "csv"

    class Fancy(Csv, fmt="fancy-csv"):
        pass

    assert Exporter.formats() == ["csv", "fancy-csv"]
    assert isinstance(Exporter.for_format("fancy-csv"), Fancy)
    with pytest.raises(KeyError):
        Exporter.for_format("xml")


def test_exporter_validation(load_exercise):
    Exporter = load_exercise("ex03_plugin_base").Exporter
    with pytest.raises(TypeError):
        class NoFmt(Exporter):
            def export(self, d):
                return d
    with pytest.raises(TypeError):
        class NoExport(Exporter, fmt="x1"):
            pass
    class Ok(Exporter, fmt="ok"):
        def export(self, d):
            return d
    with pytest.raises(ValueError):
        class Dup(Exporter, fmt="ok"):
            def export(self, d):
                return d


def test_singleton_metaclass(load_exercise):
    Singleton = load_exercise("ex04_singleton_meta").Singleton
    calls = []

    class Config(metaclass=Singleton):
        def __init__(self, value=None):
            calls.append(value)
            self.value = value

    a = Config(1)
    assert Config() is a and Config(1) is a and calls == [1]
    with pytest.raises(TypeError):
        Config(2)

    class Child(Config):
        pass

    assert Child() is not a and isinstance(Child(), Config)
    Singleton.reset(Config)
    assert Config(5) is not a and calls == [1, None, 5]


def test_called_names(load_exercise):
    called_names = load_exercise("ex05_ast_tools").called_names
    assert called_names("print(len(items)); items.append(sum(x))") == ["append", "len", "print", "sum"]
    assert called_names("x = 1 + 2") == []
    assert called_names("f(g(h(1)))") == ["f", "g", "h"]


def test_unsafe_and_upper(load_exercise):
    module = load_exercise("ex05_ast_tools")
    assert module.has_unsafe_calls("x = eval('1')") is True
    assert module.has_unsafe_calls("x = eval") is False
    assert module.has_unsafe_calls("obj.eval(1)") is False
    assert module.has_unsafe_calls("print(1)") is False
    assert module.has_unsafe_calls("f(1)", forbidden=("f",)) is True
    assert module.constants_to_upper("x = 'ab'; f('cd', 3)") == "x = 'AB'\nf('CD', 3)"
