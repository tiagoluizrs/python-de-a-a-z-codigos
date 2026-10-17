import pytest


def test_normalize_name(load_exercise):
    normalize_name = load_exercise("ex01_normalize_name").normalize_name
    assert normalize_name("  José   da  Silva ") == "José da Silva"
    assert normalize_name("D'Ávila-Souza") == "D'Ávila-Souza"
    assert normalize_name("Ana\tMaria Lima") == "Ana Maria Lima"
    result = normalize_name("José")
    assert len(result) == 4 and result == "José"
    for bad in ("R2D2", "", "   ", "Ana!", "Ana_Maria", "😀"):
        with pytest.raises(ValueError):
            normalize_name(bad)


def test_visible_length(load_exercise):
    module = load_exercise("ex02_visible_length")
    assert module.visible_length("abc") == 3
    assert module.visible_length("") == 0
    assert module.visible_length("é") == 1
    assert module.visible_length("\U0001F1E7\U0001F1F7") == 1
    family = "\U0001F468‍\U0001F469‍\U0001F467"
    assert module.visible_length(family) == 1
    assert module.visible_length("a" + family + "b") == 3
    assert module.truncate_visible("ábc", 2) == "áb"
    assert module.truncate_visible("abc", 10) == "abc"
    assert module.truncate_visible("abc", 0) == ""
    with pytest.raises(ValueError):
        module.truncate_visible("abc", -1)


def test_to_snake(load_exercise):
    to_snake = load_exercise("ex03_case_converter").to_snake
    assert to_snake("userName") == "user_name"
    assert to_snake("HTTPServerError") == "http_server_error"
    assert to_snake("getHTTPResponseCode") == "get_http_response_code"
    assert to_snake("already_snake") == "already_snake"
    assert to_snake("version2Beta") == "version2_beta"
    assert to_snake("Name") == "name"
    assert to_snake("") == ""


def test_to_camel(load_exercise):
    to_camel = load_exercise("ex03_case_converter").to_camel
    assert to_camel("user_name") == "userName"
    assert to_camel("user_name", pascal=True) == "UserName"
    assert to_camel("__private_value") == "privateValue"
    assert to_camel("a__b") == "aB"
    assert to_camel("") == ""
    assert to_camel("word") == "word"


def test_caesar(load_exercise):
    caesar = load_exercise("ex04_caesar").caesar
    assert caesar("Hello, World!", 3) == "Khoor, Zruog!"
    assert caesar("xyz", 3) == "abc"
    assert caesar("XYZ", 3) == "ABC"
    assert caesar("Ação 😀 123", 1) == "Bçãp 😀 123"
    assert caesar("Python", 26) == "Python"
    assert caesar("Python", 52 + 5) == caesar("Python", 5)
    assert caesar(caesar("Python 3.15", 7), -7) == "Python 3.15"
    assert caesar("abc", -1) == "zab"


def test_fix_mojibake(load_exercise):
    module = load_exercise("ex05_mojibake")
    fix = module.fix_mojibake
    assert fix("AÃ§Ã£o") == "Ação"
    assert fix("coraÃ§Ã£o") == "coração"
    assert fix("Ação") == "Ação"
    assert fix("你好") == "你好"
    assert fix("plain") == "plain"
    assert fix("") == ""
    assert fix("itâ€™s") == "it’s"
    assert fix("Ã\u0081guia") == "Águia"
    # round trip com os dois jeitos de estragar
    original = "Ação, coração e não"
    assert fix(original.encode("utf-8").decode("latin-1")) == original
    assert module.looks_like_mojibake("AÃ§Ã£o") is True
    assert module.looks_like_mojibake("Ação") is False


def test_format_brl(load_exercise):
    from decimal import Decimal
    format_brl = load_exercise("ex06_money_brl").format_brl
    assert format_brl(1234567.891) == "R$ 1.234.567,89"
    assert format_brl("1999.9", symbol=False) == "1.999,90"
    assert format_brl(0) == "R$ 0,00"
    assert format_brl(-0.5) == "-R$ 0,50"
    assert format_brl(Decimal("2.675")) == "R$ 2,68"
    assert format_brl(2.675) == "R$ 2,68"
    assert format_brl(-0.001) == "R$ 0,00"
    assert format_brl(1000) == "R$ 1.000,00"
    assert format_brl(999.999) == "R$ 1.000,00"
    assert format_brl(-1234567, symbol=False) == "-1.234.567,00"
    assert format_brl(12) == "R$ 12,00"
