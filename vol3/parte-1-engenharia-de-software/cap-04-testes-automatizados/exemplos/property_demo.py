"""O Hypothesis encontra um contraexemplo mínimo (shrinking)."""
from hypothesis import given, settings
from hypothesis import strategies as st


def buggy_abs_diff(a, b):
    """Bug: esquece o caso em que a diferença passa de 100."""
    d = a - b
    return -d if d < 0 else (d if d <= 100 else 0)


@settings(max_examples=200, database=None, derandomize=True)
@given(st.integers(-1000, 1000), st.integers(-1000, 1000))
def check(a, b):
    assert buggy_abs_diff(a, b) == abs(a - b)


try:
    check()
except AssertionError:
    import re
    import traceback
    text = traceback.format_exc()
    block = re.search(r"(?:Falsifying example|Failing test case): (check\(.*?\n\))", text, re.DOTALL)
    print("contraexemplo mínimo:", " ".join(block.group(1).split()) if block else text[-300:])
