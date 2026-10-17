import subprocess
import sys

import pytest

SRC_NAMES = """
class my_class:
    def getUser(self, userId, Mode=1):
        Total = 1
        lower = 2
        return Total

class _Helper:
    def _private(self): pass
    def __init__(self): pass

async def Fetch(): pass
def ok(a, b=2, *args, **kwargs):
    value = a
    return value
"""


def test_check_names(load_exercise):
    check_names = load_exercise("ex01_names").check_names
    assert check_names(SRC_NAMES) == [
        (2, "N801", "my_class"), (3, "N802", "getUser"), (3, "N803", "Mode"), (3, "N803", "userId"),
        (4, "N806", "Total"), (12, "N802", "Fetch")]
    assert check_names("def f(self, cls): x = 1") == []


SRC_LINT = """
import os, sys
import json as js
from collections import OrderedDict, deque
from __future__ import annotations
import xml.etree.ElementTree
from pkg import used_name, unused_name as alias

def f(a, items=[], *, cache={}, ok=None, other=set(), fine=()):
    try:
        pass
    except:
        pass
    if a == None or a != None:
        pass
    if a == True and a != False:
        pass
    return deque, used_name, js

g = lambda x, y=[]: x
__all__ = ["os"]
"""


def test_lint_rules(load_exercise):
    lint = load_exercise("ex02_lint").lint
    result = lint(SRC_LINT)
    assert result == [
        (2, "F401"),                      # sys (os está em __all__)
        (4, "F401"),                      # OrderedDict
        (6, "F401"),                      # xml (import xml.etree... define xml)
        (7, "F401"),                      # alias
        (9, "B006"), (9, "B006"), (9, "B006"),
        (12, "E722"),
        (14, "E711"), (14, "E711"),
        (16, "E712"), (16, "E712"),
        (20, "B006")]
    assert lint("import os\nprint(os.getcwd())\n") == []
    assert lint("from __future__ import annotations\n") == []


def test_cyclomatic_complexity(load_exercise):
    cc = load_exercise("ex03_complexity").cyclomatic_complexity
    source = """
def simple(): return 1

def branches(a, b):
    if a and b or a:
        return 1
    elif b:
        return 2
    for x in range(3):
        while x:
            x -= 1
    try:
        pass
    except ValueError:
        pass
    return [i for i in range(a) if i % 2 if i > 1]

class K:
    def method(self, v):
        def inner(w):
            return 1 if w else 2
        return inner(v) if v else 0

async def go(items):
    match items:
        case [] | [_]:
            return 0
        case _:
            return 1
"""
    result = cc(source)
    assert result == {"simple": 1, "branches": 11,
                      "K.method": 2, "K.method.inner": 2, "go": 3}


def test_too_complex(load_exercise):
    module = load_exercise("ex03_complexity")
    ladder = "def f(x):\n" + "".join(f"    if x == {i}:\n        return {i}\n" for i in range(11)) + "    return -1\n"
    assert module.cyclomatic_complexity(ladder)["f"] == 12
    assert module.too_complex(ladder) == ["f"] and module.too_complex(ladder, limit=12) == []


IMPORTS = """import requests
from . import sibling
import os, sys
from typing import Optional, Any
import numpy as np
from __future__ import annotations
from collections import deque
import abc
from .models import User
from Collections import X
"""


def test_sort_imports(load_exercise):
    sort_imports = load_exercise("ex04_imports").sort_imports
    result = sort_imports(IMPORTS)
    assert result == (
        "from __future__ import annotations\n\n"
        "import abc\nimport os\nimport sys\nfrom collections import deque\nfrom typing import Any, Optional\n\n"
        "import numpy as np\nimport requests\nfrom Collections import X\n\n"
        "from . import sibling\nfrom .models import User\n")
    assert sort_imports("") == "" and sort_imports("\n\n") == ""


def test_sort_imports_agrees_with_ruff(load_exercise):
    sort_imports = load_exercise("ex04_imports").sort_imports
    result = sort_imports("import sys, os\nimport requests\nfrom pathlib import Path, PurePath\nimport json as j\n")
    check = subprocess.run([sys.executable, "-m", "ruff", "check", "--isolated", "--select", "I", "--stdin-filename", "x.py", "-"],
                           input=result, capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr


def test_line_issues(load_exercise):
    line_issues = load_exercise("ex05_whitespace").line_issues
    source = "ok = 1\n\tindented = 2\ntrailing = 3   \n   \n" + "x = '" + "a" * 90 + "'\nlast = 4\n\n\n"
    assert line_issues(source) == [(2, "W191"), (3, "W291"), (4, "W293"), (5, "E501"), (7, "W391")]
    assert line_issues("a = 1\nb = 2", max_length=3) == [(1, "E501"), (2, "E501"), (2, "W292")]
    assert line_issues("") == [] and line_issues("x = 1\n") == []


def test_line_issues_only_blank(load_exercise):
    line_issues = load_exercise("ex05_whitespace").line_issues
    assert line_issues("\n\n") == [(1, "W391")]


def test_remove_unused_imports(load_exercise):
    remove = load_exercise("ex06_autofix").remove_unused_imports
    source = ('''from __future__ import annotations
import os, sys, json
from typing import Any, Optional as Opt, List
import numpy as np
from m import *
import (
    multi
)
__all__ = ["List"]

def f():
    import local_thing
    return os.getcwd(), Opt
''').replace("import (\n    multi\n)", "from big import (\n    a,\n    b,\n)")
    result = remove(source)
    assert result == ('''from __future__ import annotations
import os
from typing import Optional as Opt, List
from m import *
from big import (
    a,
    b,
)
__all__ = ["List"]

def f():
    import local_thing
    return os.getcwd(), Opt
''')
    assert remove("import os\n") == "" and remove("x = 1") == "x = 1"
    assert remove("import a, b\nprint(a)") == "import a\nprint(a)"
