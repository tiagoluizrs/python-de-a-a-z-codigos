import pytest


def test_parse_command(load_exercise):
    parse = load_exercise("ex01_commands").parse_command
    assert parse("go north") == ("move", "north")
    assert parse("go west") == ("move", "west")
    assert parse("go") == ("error", "go where?")
    assert parse("go up") == ("error", "go where?")
    assert parse("go north now") == ("error", "go where?")
    assert parse("pick sword") == ("pick", "sword")
    assert parse("pick magic sword") == ("pick", "magic sword")
    assert parse("pick") == ("unknown", "pick")
    assert parse("quit") == ("quit",)
    assert parse("exit") == ("quit",)
    assert parse("") == ("noop",)
    assert parse("   ") == ("noop",)
    assert parse("dance now") == ("unknown", "dance")


def test_normalize_event(load_exercise):
    normalize = load_exercise("ex02_normalize_event").normalize
    assert normalize({"type": "click", "x": 1, "y": 2, "z": 0}) == {
        "kind": "click", "pos": (1, 2)}
    assert normalize({"type": "key", "key": "A"}) == {
        "kind": "key", "key": "a"}
    assert normalize({"type": "scroll", "dy": -3}) == {
        "kind": "scroll", "delta": -3}
    bad = [{"type": "click", "x": 1}, {"type": "click", "x": "1", "y": 2},
           {"type": "key", "key": 1}, {"type": "other"}, {}, [], None,
           "click"]
    for event in bad:
        with pytest.raises(ValueError):
            normalize(event)


def test_fizzbuzz(load_exercise):
    fizzbuzz = load_exercise("ex03_fizzbuzz").fizzbuzz
    out = [fizzbuzz(n) for n in range(1, 16)]
    assert out == ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8",
                   "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
    assert fizzbuzz(30) == "FizzBuzz"
    assert fizzbuzz(0) == "FizzBuzz"


def test_evaluate(load_exercise):
    evaluate = load_exercise("ex04_calculator").evaluate
    assert evaluate(7) == 7
    assert evaluate(2.5) == 2.5
    assert evaluate(("+", 2, ("*", 3, 4))) == 14
    assert evaluate(("-", 10, 4)) == 6
    assert evaluate(("/", 9, 2)) == 4.5
    assert evaluate(("neg", ("+", 1, 2))) == -3
    assert evaluate(("sum", [1, 2, ("*", 2, 3)])) == 9
    assert evaluate(("sum", [])) == 0
    for bad in [("^", 1, 2), ("+", 1), "x", None, True, ("+", 1, False),
                ("neg",), ("sum", 5)]:
        with pytest.raises(ValueError):
            evaluate(bad)
    with pytest.raises(ZeroDivisionError):
        evaluate(("/", 1, 0))


def test_convert(load_exercise):
    module = load_exercise("ex05_dispatch")
    assert module.FACTORS, "preencha FACTORS"
    for unit in ("km", "m", "cm", "mm", "mi"):
        assert module.convert(3.7, unit) == pytest.approx(
            module.convert_slow(3.7, unit))
    with pytest.raises(ValueError):
        module.convert(1, "ft")
