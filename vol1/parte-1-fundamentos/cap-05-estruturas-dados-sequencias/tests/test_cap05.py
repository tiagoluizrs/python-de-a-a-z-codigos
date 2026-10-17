import pytest


def test_rotate(load_exercise):
    rotate = load_exercise("ex01_rotate").rotate
    data = [1, 2, 3, 4]
    assert rotate(data, 1) == [4, 1, 2, 3]
    assert rotate(data, -1) == [2, 3, 4, 1]
    assert rotate(data, 4) == [1, 2, 3, 4]
    assert rotate(data, 9) == [4, 1, 2, 3]
    assert rotate([], 3) == []
    assert data == [1, 2, 3, 4]
    assert rotate(data, 0) is not data


def test_chunked(load_exercise):
    chunked = load_exercise("ex02_chunked").chunked
    assert chunked([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunked([], 3) == []
    assert chunked([1, 2], 5) == [[1, 2]]
    with pytest.raises(ValueError):
        chunked([1], 0)


def test_sort_employees(load_exercise):
    sort_employees = load_exercise("ex03_sort_records").sort_employees
    staff = [("Zed", "IT", 5000), ("Ana", "HR", 4000), ("Bob", "IT", 7000),
             ("Cid", "IT", 7000), ("Eva", "HR", 4500)]
    assert sort_employees(staff) == [
        ("Eva", "HR", 4500), ("Ana", "HR", 4000),
        ("Bob", "IT", 7000), ("Cid", "IT", 7000), ("Zed", "IT", 5000)]
    assert staff[0] == ("Zed", "IT", 5000)


def test_flatten_and_transpose(load_exercise):
    module = load_exercise("ex04_matrix")
    assert module.flatten([[1, 2], [3], []]) == [1, 2, 3]
    assert module.flatten([]) == []
    assert module.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert module.transpose([]) == []


def test_remove_in_place(load_exercise):
    remove_in_place = load_exercise("ex05_remove_in_place").remove_in_place
    items = [2, 4, 6, 8, 3]
    same = items
    assert remove_in_place(items, lambda n: n % 2 == 0) == 4
    assert items == [3] and items is same
