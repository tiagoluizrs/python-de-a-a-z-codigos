import copy

import pytest


def test_invert(load_exercise):
    invert = load_exercise("ex01_invert").invert
    grades = {"Ana": "A", "Bia": "B", "Caio": "A"}
    original = dict(grades)
    assert invert(grades) == {"A": ["Ana", "Caio"], "B": ["Bia"]}
    assert list(invert(grades)) == ["A", "B"]
    assert invert({}) == {}
    assert grades == original


def test_group_by(load_exercise):
    group_by = load_exercise("ex02_group_by").group_by
    assert group_by(["apple", "avocado", "fig", "pear"], len) == {
        5: ["apple"], 7: ["avocado"], 3: ["fig"], 4: ["pear"]}
    assert list(group_by([3, 1, 2, 4], lambda n: n % 2)) == [1, 0]
    assert group_by(iter([]), len) == {}
    assert group_by((x for x in range(5)), lambda n: n % 2) == {
        0: [0, 2, 4], 1: [1, 3]}


def test_audit(load_exercise):
    audit = load_exercise("ex03_permissions").audit
    result = audit({"read", "write", "admin"}, {"read", "delete"})
    assert result == {"unused": {"write", "admin"},
                      "missing": {"delete"}, "active": {"read"}}
    assert audit(set(), set()) == {"unused": set(), "missing": set(),
                                   "active": set()}
    granted = {"a"}
    audit(granted, {"b"})
    assert granted == {"a"}


def test_dedup(load_exercise):
    dedup = load_exercise("ex04_dedup").dedup
    assert dedup("banana") == ["b", "a", "n"]
    assert dedup([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedup([]) == []
    assert dedup([[1], [2], [1]], key=tuple) == [[1], [2]]
    assert dedup(["Ab", "aB", "c"], key=str.lower) == ["Ab", "c"]
    assert dedup(iter([1, 1, 2])) == [1, 2]


def test_merge(load_exercise):
    merge = load_exercise("ex05_merge").merge
    base = {"a": 1, "n": {"x": 1, "deep": {"k": 1}}, "only_base": 0}
    other = {"a": 2, "n": {"y": 2, "deep": {"k": 9}}, "only_other": 5}
    snapshot = (copy.deepcopy(base), copy.deepcopy(other))
    assert merge(base, other) == {
        "a": 2, "n": {"x": 1, "y": 2, "deep": {"k": 9}},
        "only_base": 0, "only_other": 5}
    assert (base, other) == snapshot
    total = merge({"a": 1, "n": {"b": 2}}, {"a": 10, "n": {"b": 3}},
                  on_conflict=lambda key, old, new: old + new)
    assert total == {"a": 11, "n": {"b": 5}}
    # dict versus não dict conta como conflito comum
    assert merge({"a": {"x": 1}}, {"a": 5}) == {"a": 5}
    with pytest.raises(ZeroDivisionError):
        merge({"a": 1}, {"a": 2}, on_conflict=lambda k, o, n: 1 / 0)
