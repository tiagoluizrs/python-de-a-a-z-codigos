import re
import urllib.error
import urllib.request

import pytest


def test_wc_count_text(load_exercise):
    count_text = load_exercise("ex01_wc").count_text
    assert count_text("a b\nc\n") == (2, 3, 6)
    assert count_text("") == (0, 0, 0)


def test_wc_main(load_exercise, tmp_path, capsys):
    main = load_exercise("ex01_wc").main
    f = tmp_path / "a.txt"
    f.write_text("um dois\ntrês\n", encoding="utf-8")
    assert main([str(f)]) == 0
    assert capsys.readouterr().out.split() == ["2", "3", "13", str(f)]
    assert main(["-w", str(f)]) == 0
    assert capsys.readouterr().out.split() == ["3", str(f)]
    assert main(["-c", "-l", str(f)]) == 0
    assert capsys.readouterr().out.split() == ["2", "13", str(f)]


def test_wc_missing_file(load_exercise, tmp_path, capsys):
    main = load_exercise("ex01_wc").main
    ok = tmp_path / "ok.txt"
    ok.write_text("x\n", encoding="utf-8")
    assert main([str(tmp_path / "nope.txt"), str(ok)]) == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err
    assert "1 1 2" in captured.out


def test_password(load_exercise):
    module = load_exercise("ex02_password")
    for _ in range(50):
        pw = module.generate_password(12)
        assert len(pw) == 12
        assert re.search(r"[a-z]", pw) and re.search(r"[A-Z]", pw)
        assert re.search(r"\d", pw) and re.search(r"[!@#$%&*?\-_]", pw)
    assert module.generate_password() != module.generate_password()
    assert len(module.generate_password()) == 16
    with pytest.raises(ValueError):
        module.generate_password(7)
    token = module.make_token(8)
    assert re.fullmatch(r"[A-Za-z0-9_-]+", token)


def test_password_never_uses_random(load_exercise, monkeypatch):
    import random

    def boom(*args, **kwargs):
        raise AssertionError("não use random para senhas")

    for name in ("choice", "choices", "shuffle", "randrange", "randint",
                 "sample", "random"):
        monkeypatch.setattr(random, name, boom)
    module = load_exercise("ex02_password")
    assert len(module.generate_password(10)) == 10


def test_diff(load_exercise):
    module = load_exercise("ex03_diff")
    assert module.text_diff("a\nb", "a\nb") == []
    diff = module.text_diff("a\nb\nc", "a\nx\nc\nd")
    assert diff[0] == "--- old" and diff[1] == "+++ new"
    assert "-b" in diff and "+x" in diff and "+d" in diff
    assert module.changed_lines("a\nb\nc", "a\nx\nc\nd") == (["b"], ["x", "d"])
    assert module.changed_lines("same", "same") == ([], [])


def test_closest(load_exercise):
    closest = load_exercise("ex03_diff").closest
    assert closest("pythn", ["java", "python", "ruby"]) == "python"
    assert closest("zzz", ["java", "python"]) is None


def test_stats(load_exercise):
    text_stats = load_exercise("ex04_stats").text_stats
    result = text_stats("the cat and the dog and the horse")
    assert result["words"] == 8 and result["unique"] == 5
    assert result["mean_len"] == 3.25
    assert result["median_len"] == 3
    assert result["top"] == [("the", 3), ("and", 2)]
    assert text_stats("   ") == {"words": 0, "unique": 0, "mean_len": 0.0,
                                 "median_len": 0, "top": []}


def test_file_server(load_exercise, tmp_path):
    serve = load_exercise("ex05_file_server").serve_directory
    (tmp_path / "hello.txt").write_text("olá", encoding="utf-8")
    with serve(tmp_path) as base:
        assert base.startswith("http://127.0.0.1:")
        with urllib.request.urlopen(base + "/hello.txt", timeout=5) as r:
            assert r.read().decode("utf-8") == "olá"
        with pytest.raises(urllib.error.HTTPError) as info:
            urllib.request.urlopen(base + "/missing.txt", timeout=5)
        assert info.value.code == 404
    # Depois do with, a porta está fechada
    with pytest.raises(OSError):
        urllib.request.urlopen(base + "/hello.txt", timeout=2)
