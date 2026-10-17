import io
import json

import pytest


def test_copy_stream_with_text_and_bytes(load_exercise):
    copy_stream = load_exercise("ex01_duck").copy_stream
    target = io.StringIO()
    assert copy_stream(io.StringIO("olá mundo!"), target) == 10
    assert target.getvalue() == "olá mundo!"
    target = io.BytesIO()
    assert copy_stream(io.BytesIO(b"abcdefghij"), target, chunk_size=3) == 10
    assert target.getvalue() == b"abcdefghij"


def test_copy_stream_custom_objects(load_exercise):
    copy_stream = load_exercise("ex01_duck").copy_stream

    class Source:
        def __init__(self):
            self.parts = ["ab", "cd", ""]

        def read(self, n):
            return self.parts.pop(0)

    class Target:
        def __init__(self):
            self.data = []

        def write(self, chunk):
            self.data.append(chunk)

    target = Target()
    assert copy_stream(Source(), target) == 4 and target.data == ["ab", "cd"]


def test_quack_all(load_exercise):
    quack_all = load_exercise("ex01_duck").quack_all

    class Dog:
        def speak(self):
            return "au"

    class Cat:
        def speak(self):
            return "miau"

    class Rock:
        pass

    class Broken:
        def speak(self):
            return self.missing_attribute        # erro DENTRO do método

    assert quack_all([Dog(), Rock(), Cat()]) == ["au", "miau"]
    assert quack_all([Dog()], method="walk") == []
    with pytest.raises(AttributeError, match="missing_attribute"):
        quack_all([Broken()])


def test_arith_seq_basics(load_exercise):
    ArithSeq = load_exercise("ex02_range_seq").ArithSeq
    seq = ArithSeq(2, 3, 4)                       # 2, 5, 8, 11
    assert list(seq) == [2, 5, 8, 11] and len(seq) == 4
    assert seq[0] == 2 and seq[-1] == 11 and seq[2] == 8
    assert repr(seq) == "ArithSeq(2, 3, 4)"
    with pytest.raises(IndexError):
        seq[4]
    with pytest.raises(IndexError):
        seq[-5]


def test_arith_seq_inherits_the_rest(load_exercise):
    from collections.abc import Sequence
    ArithSeq = load_exercise("ex02_range_seq").ArithSeq
    seq = ArithSeq(2, 3, 4)
    assert isinstance(seq, Sequence)
    assert 8 in seq and 9 not in seq and seq.index(8) == 2 and seq.count(5) == 1
    assert list(reversed(seq)) == [11, 8, 5, 2]
    # só __init__, __len__, __getitem__ e __repr__ foram escritos na classe
    for name in ("index", "count", "__contains__", "__iter__", "__reversed__"):
        assert name not in vars(ArithSeq)


def test_arith_seq_slices(load_exercise):
    ArithSeq = load_exercise("ex02_range_seq").ArithSeq
    seq = ArithSeq(0, 10, 6)                      # 0, 10, ..., 50
    sliced = seq[1:5:2]
    assert isinstance(sliced, ArithSeq) and list(sliced) == [10, 30]
    assert list(seq[::-1]) == [50, 40, 30, 20, 10, 0]
    assert list(seq[-2:]) == [40, 50] and list(seq[10:]) == []
    assert repr(seq[::2]) == "ArithSeq(0, 20, 3)"


def test_exporter_is_abstract(load_exercise):
    module = load_exercise("ex03_exporter")
    with pytest.raises(TypeError):
        module.Exporter()

    class Half(module.Exporter):
        extension = "x"

    with pytest.raises(TypeError):
        Half()
    assert "extension" in module.Exporter.__abstractmethods__
    assert "render" in module.Exporter.__abstractmethods__


def test_exporters_save(load_exercise, tmp_path):
    module = load_exercise("ex03_exporter")
    rows = [{"id": 1, "nome": "Ana"}, {"id": 2, "nome": "Zé"}]
    path = module.CsvExporter().save(tmp_path, "pessoas", rows)
    assert path == tmp_path / "pessoas.csv"
    assert path.read_text(encoding="utf-8") == "id,nome\n1,Ana\n2,Zé"
    path = module.JsonExporter().save(tmp_path, "pessoas", rows)
    assert path.name == "pessoas.json"
    assert json.loads(path.read_text(encoding="utf-8")) == rows
    assert "Zé" in path.read_text(encoding="utf-8")        # ensure_ascii=False


def test_close_all(load_exercise):
    close_all = load_exercise("ex04_protocol").close_all

    class Res:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    a, b = Res(), Res()
    assert close_all([a, 42, b, "texto", io.StringIO()]) == 3
    assert a.closed and b.closed


def test_close_all_continues_after_error(load_exercise):
    close_all = load_exercise("ex04_protocol").close_all

    class Boom:
        def close(self):
            raise OSError("falhou")

    class Res:
        closed = False

        def close(self):
            self.closed = True

    ok = Res()
    with pytest.raises(OSError, match="falhou"):
        close_all([Boom(), ok])
    assert ok.closed


def test_protocol_is_runtime_checkable(load_exercise):
    module = load_exercise("ex04_protocol")
    assert isinstance(io.StringIO(), module.SupportsClose)
    assert not isinstance(42, module.SupportsClose)


def test_drawable_hook(load_exercise):
    Drawable = load_exercise("ex05_hook").Drawable

    class Circle:
        def draw(self):
            return "o"

    class Child(Circle):
        pass

    class Rock:
        pass

    class Fake:
        draw = 1

    assert issubclass(Circle, Drawable) and issubclass(Child, Drawable)
    assert isinstance(Circle(), Drawable)
    assert not issubclass(int, Drawable) and not issubclass(Rock, Drawable)
    assert not issubclass(Fake, Drawable)
    Drawable.register(Rock)
    assert issubclass(Rock, Drawable) and isinstance(Rock(), Drawable)
