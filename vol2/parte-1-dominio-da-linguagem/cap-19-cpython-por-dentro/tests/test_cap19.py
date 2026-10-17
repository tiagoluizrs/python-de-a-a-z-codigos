import os
import py_compile
import sys

import pytest


def sample(a, b):
    def inner(x):
        return x * 2

    total = helper(a) + b
    return inner(total) + len(str(total))


def helper(x):
    return x + 1


def test_opcode_histogram(load_exercise):
    module = load_exercise("ex01_opcodes")
    histogram = module.opcode_histogram(sample)
    assert histogram["BINARY_OP"] >= 3                      # a + b, x * 2 (inner), x + 1 não (helper)
    assert sum(v for k, v in histogram.items() if k.startswith("RETURN")) >= 2
    assert module.count_instructions(sample) == sum(histogram.values())
    assert module.count_instructions(sample) > module.count_instructions(helper)


def test_uses_global(load_exercise):
    uses_global = load_exercise("ex01_opcodes").uses_global
    assert uses_global(sample, "helper") and uses_global(sample, "len") and uses_global(sample, "str")
    assert not uses_global(helper, "len") and not uses_global(sample, "inner")


def test_constants_of(load_exercise):
    constants_of = load_exercise("ex02_constants").constants_of
    source = "x = 1000\ny = 'a' + 'b'\nf = lambda z: z * 3.5 + 'k'.upper().count('k') + 700\nflag = True\nn = None\n"
    assert constants_of(source) == sorted({1000, "ab", 3.5, "k", 700}, key=repr)
    assert constants_of("pass") == []


def test_is_folded(load_exercise):
    is_folded = load_exercise("ex02_constants").is_folded
    assert is_folded("2 * 3 + 1") and is_folded("'a' + 'b'") and is_folded("(1, 2)")
    assert not is_folded("x + 1") and not is_folded("len('abc')") and not is_folded("1 + x * 2")


def test_trace_calls(load_exercise):
    trace_calls = load_exercise("ex03_call_tracer").trace_calls

    def c():
        return 1

    def b():
        return c() + c()

    def a():
        return b()

    result, names = trace_calls(a)
    assert result == 2 and names == ["a", "b", "c", "c"]
    # a ferramenta foi liberada: pode ser usada de novo
    assert trace_calls(c)[1] == ["c"]


def test_trace_calls_cleans_up_on_error(load_exercise):
    trace_calls = load_exercise("ex03_call_tracer").trace_calls

    def boom():
        raise RuntimeError("falhou")

    with pytest.raises(RuntimeError):
        trace_calls(boom)
    assert trace_calls(lambda: 5)[0] == 5                    # id liberado (não levanta ValueError)
    assert sys.monitoring.get_tool(sys.monitoring.PROFILER_ID) is None


def test_count_calls(load_exercise):
    count_calls = load_exercise("ex03_call_tracer").count_calls

    def leaf():
        pass

    def root():
        for _ in range(3):
            leaf()

    counts = count_calls(root)
    assert counts["leaf"] == 3 and counts["root"] == 1


def test_pyc_roundtrip(load_exercise, tmp_path):
    module = load_exercise("ex04_pyc")
    source = tmp_path / "mod.py"
    source.write_text("VALUE = 6 * 7\n")
    pyc = tmp_path / "mod.pyc"
    py_compile.compile(str(source), cfile=str(pyc))
    header = module.read_pyc_header(str(pyc))
    assert header["size"] == source.stat().st_size and header["flags"] == 0 and len(header["magic"]) == 4
    namespace = {}
    exec(module.load_pyc(str(pyc)), namespace)
    assert namespace["VALUE"] == 42
    assert module.is_fresh(str(source), str(pyc)) is True
    source.write_text("VALUE = 6 * 7 + 1000\n")
    assert module.is_fresh(str(source), str(pyc)) is False


def test_pyc_bad_magic(load_exercise, tmp_path):
    module = load_exercise("ex04_pyc")
    bad = tmp_path / "bad.pyc"
    bad.write_bytes(b"\x00" * 32)
    with pytest.raises(ValueError):
        module.read_pyc_header(str(bad))


def test_stack_tools(load_exercise):
    module = load_exercise("ex05_stack")

    def a():
        return b()

    def b():
        return module.caller_names()

    names = a()
    assert names[:2] == ["b", "a"] and "test_stack_tools" in names
    line = module.calling_line()
    assert line == sys._getframe().f_lineno - 1


def test_recursion_capacity(load_exercise):
    module = load_exercise("ex05_stack")
    limit = sys.getrecursionlimit()
    capacity = module.recursion_capacity()
    assert sys.getrecursionlimit() == limit
    assert limit - 200 < capacity <= limit
