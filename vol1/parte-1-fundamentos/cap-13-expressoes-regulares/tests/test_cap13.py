import time

import pytest


def test_parse_logs(load_exercise):
    parse_logs = load_exercise("ex01_parse_logs").parse_logs
    text = (
        "2026-10-12 14:03:22 [INFO] started on port 8000\n"
        "garbage\n"
        "2026-10-12T14:03:25 [ERROR] db: lost [retry 1]\n"
        "2026-10-12 14:03 [INFO] no seconds\n"
    )
    assert parse_logs(text) == [
        {"timestamp": "2026-10-12 14:03:22", "level": "INFO",
         "message": "started on port 8000"},
        {"timestamp": "2026-10-12T14:03:25", "level": "ERROR",
         "message": "db: lost [retry 1]"},
    ]
    assert parse_logs("") == []


def test_find_phones(load_exercise):
    find_phones = load_exercise("ex02_find_phones").find_phones
    text = "Ligue (11) 98765-4321 ou 21 3456-7890, ou +55 31 99999-8888."
    assert find_phones(text) == [
        "+5511987654321", "+552134567890", "+5531999998888"]
    assert find_phones("11987654321") == ["+5511987654321"]
    assert find_phones("protocolo 123456789012345") == []
    assert find_phones("(01) 98765-4321") == []
    assert find_phones("sem telefone") == []


def test_tokenizer(load_exercise):
    tokenize = load_exercise("ex03_tokenizer").tokenize
    assert tokenize("x = 2.5*y") == [
        ("IDENT", "x"), ("OP", "="), ("NUMBER", "2.5"),
        ("OP", "*"), ("IDENT", "y")]
    assert tokenize("(a1+_b)") == [
        ("LPAREN", "("), ("IDENT", "a1"), ("OP", "+"),
        ("IDENT", "_b"), ("RPAREN", ")")]
    assert tokenize("   ") == []
    with pytest.raises(ValueError, match="2"):
        tokenize("a $ b")


def test_cpf(load_exercise):
    module = load_exercise("ex04_cpf")
    assert module.is_valid_cpf("529.982.247-25")
    assert module.is_valid_cpf("52998224725")
    assert not module.is_valid_cpf("529.982.247-26")
    assert not module.is_valid_cpf("111.111.111-11")
    assert not module.is_valid_cpf("529982.247-25")
    assert not module.is_valid_cpf("529.982.247-25 ")
    assert not module.is_valid_cpf("")
    text = "CPF 529.982.247-25, outro 529.982.247-26 e 52998224725."
    assert module.mask_cpfs(text) == (
        "CPF ***.***.***-25, outro 529.982.247-26 e ***.***.***-25.")


def test_redos(load_exercise):
    module = load_exercise("ex05_redos")
    safe = module.build_safe_pattern()
    samples = ["", "ab cd", "ab  cd", " ab", "ab ", "a b c ", "ab!",
               "a\tb", "x y  ", "olá mundo", "a-b"]
    for sample in samples:
        assert bool(safe.search(sample)) == bool(
            module.VULNERABLE.search(sample)), sample
    start = time.perf_counter()
    assert safe.search("a" * 20_000 + "!") is None
    assert time.perf_counter() - start < 1.0


def test_dates(load_exercise):
    dates_to_iso = load_exercise("ex06_dates").dates_to_iso
    text = "Pago em 12/10/2026, vence 31/02/2026 e 05/11/2026."
    assert dates_to_iso(text) == (
        "Pago em 2026-10-12, vence 31/02/2026 e 2026-11-05.")
    assert dates_to_iso("112/10/2026 e 12/10/20261") == (
        "112/10/2026 e 12/10/20261")
    assert dates_to_iso("29/02/2024 29/02/2025") == "2024-02-29 29/02/2025"
    assert dates_to_iso("sem data") == "sem data"
