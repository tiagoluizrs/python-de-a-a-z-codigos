import json
import os
import tracemalloc
from datetime import date, datetime
from decimal import Decimal

import pytest


# ---------------------------------------------------------- exercício 1
def test_count_stream_small(load_exercise, tmp_path):
    count_stream = load_exercise("ex01_count_stream").count_stream
    path = tmp_path / "a.txt"
    path.write_bytes("olá mundo\r\nsegunda  linha aqui\nfim".encode())
    assert count_stream(path) == (3, 6, 34)


def test_count_stream_empty(load_exercise, tmp_path):
    count_stream = load_exercise("ex01_count_stream").count_stream
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")
    assert count_stream(path) == (0, 0, 0)


def test_count_stream_uses_little_memory(load_exercise, tmp_path):
    count_stream = load_exercise("ex01_count_stream").count_stream
    path = tmp_path / "big.txt"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for i in range(100_000):
            f.write(f"line number {i} with words\n")
    assert path.stat().st_size > 2_500_000
    tracemalloc.start()
    try:
        result = count_stream(path)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert result[0] == 100_000 and result[1] == 500_000
    assert peak < 1_000_000


# ---------------------------------------------------------- exercício 2
def test_csv_to_json(load_exercise, tmp_path):
    csv_to_json = load_exercise("ex02_csv_to_json").csv_to_json
    src = tmp_path / "in.csv"
    content = ('id,name,price,note\n'
               '1,Ana,9.5,"a, b"\n'
               '2,Bia,,"line 1\nline 2"\n'
               '3,José,10,\n')
    src.write_bytes(content.encode("utf-8-sig"))
    dst = tmp_path / "out.json"
    count = csv_to_json(src, dst, {"id": int, "price": float})
    assert count == 3
    assert json.loads(dst.read_text(encoding="utf-8")) == [
        {"id": 1, "name": "Ana", "price": 9.5, "note": "a, b"},
        {"id": 2, "name": "Bia", "price": None, "note": "line 1\nline 2"},
        {"id": 3, "name": "José", "price": 10.0, "note": None},
    ]
    assert "José" in dst.read_text(encoding="utf-8")   # sem é


# ---------------------------------------------------------- exercício 3
def test_safe_write_text_and_bytes(load_exercise, tmp_path):
    safe_write = load_exercise("ex03_safe_write").safe_write
    target = tmp_path / "f.txt"
    safe_write(target, "olá\nmundo\n")
    assert target.read_bytes() == "olá\nmundo\n".encode()
    safe_write(target, b"\x00\x01")
    assert target.read_bytes() == b"\x00\x01"
    assert [p.name for p in tmp_path.iterdir()] == ["f.txt"]


def test_safe_write_bad_type_keeps_original(load_exercise, tmp_path):
    safe_write = load_exercise("ex03_safe_write").safe_write
    target = tmp_path / "f.txt"
    target.write_text("original", encoding="utf-8")
    with pytest.raises(TypeError):
        safe_write(target, 123)
    assert target.read_text(encoding="utf-8") == "original"
    assert [p.name for p in tmp_path.iterdir()] == ["f.txt"]


def test_safe_write_failure_in_replace(load_exercise, tmp_path, monkeypatch):
    safe_write = load_exercise("ex03_safe_write").safe_write
    target = tmp_path / "f.txt"
    target.write_text("original", encoding="utf-8")

    def boom(src, dst):
        raise OSError("disk exploded")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError, match="disk exploded"):
        safe_write(target, "new content")
    monkeypatch.undo()
    assert target.read_text(encoding="utf-8") == "original"
    assert [p.name for p in tmp_path.iterdir()] == ["f.txt"]


def test_safe_write_creates_new_file(load_exercise, tmp_path):
    safe_write = load_exercise("ex03_safe_write").safe_write
    target = tmp_path / "new.txt"
    safe_write(target, "x")
    assert target.read_text(encoding="utf-8") == "x"


# ---------------------------------------------------------- exercício 4
def test_find_duplicates(load_exercise, tmp_path):
    find_duplicates = load_exercise("ex04_find_duplicates").find_duplicates
    (tmp_path / "sub" / "deep").mkdir(parents=True)
    (tmp_path / "a.txt").write_bytes(b"same content")
    (tmp_path / "sub" / "b.txt").write_bytes(b"same content")
    (tmp_path / "sub" / "deep" / "c.txt").write_bytes(b"same content")
    (tmp_path / "x.bin").write_bytes(b"1234")
    (tmp_path / "sub" / "y.bin").write_bytes(b"1234")
    (tmp_path / "same_size_1.txt").write_bytes(b"abcd")   # 4 bytes, outro
    (tmp_path / "unique.txt").write_bytes(b"unique!")
    (tmp_path / "e1").write_bytes(b"")
    (tmp_path / "sub" / "e2").write_bytes(b"")

    groups = find_duplicates(tmp_path)
    assert groups == [
        [tmp_path / "a.txt", tmp_path / "sub" / "b.txt",
         tmp_path / "sub" / "deep" / "c.txt"],
        [tmp_path / "e1", tmp_path / "sub" / "e2"],
        # Path ordena por componentes: "sub" vem antes de "x.bin"
        [tmp_path / "sub" / "y.bin", tmp_path / "x.bin"],
    ]


def test_find_duplicates_none(load_exercise, tmp_path):
    find_duplicates = load_exercise("ex04_find_duplicates").find_duplicates
    (tmp_path / "a").write_bytes(b"1")
    (tmp_path / "b").write_bytes(b"2")
    assert find_duplicates(tmp_path) == []


# ---------------------------------------------------------- exercício 5
@pytest.fixture
def order(load_exercise):
    module = load_exercise("ex05_json_codec")
    return module, module.Order(
        id=7, customer="José", total=Decimal("19.90"),
        created=datetime(2026, 10, 12, 9, 30), due=date(2026, 11, 1))


def test_dumps(order):
    module, o = order
    assert json.loads(module.dumps(o)) == {
        "id": 7, "customer": "José", "total": "19.90",
        "created": "2026-10-12T09:30:00", "due": "2026-11-01"}
    assert module.dumps(o) == module.dumps(o)
    assert module.dumps({"b": 1, "a": 2}) == '{"a": 2, "b": 1}'


def test_round_trip(order):
    module, o = order
    back = module.loads_as(module.Order, module.dumps(o))
    assert back == o
    assert isinstance(back.total, Decimal)
    assert isinstance(back.created, datetime)


def test_codec_errors(order):
    module, o = order
    with pytest.raises(TypeError):
        module.dumps({"x": object()})
    with pytest.raises(KeyError):
        module.loads_as(module.Order, '{"id": 1}')
