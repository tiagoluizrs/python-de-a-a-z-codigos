"""Gabarito do exercício 2."""
import pytest
from stack_impl import EmptyStackError, Stack


def test_new_stack_is_empty():
    stack = Stack()
    assert stack.is_empty() and len(stack) == 0


def test_push_updates_size_and_emptiness():
    stack = Stack()
    stack.push(1)
    assert not stack.is_empty() and len(stack) == 1
    stack.push(2)
    assert len(stack) == 2 and not stack.is_empty()


def test_pop_returns_last_and_removes():
    stack = Stack()
    for item in (1, 2, 3):
        stack.push(item)
    assert stack.pop() == 3
    assert len(stack) == 2
    assert stack.pop() == 2 and stack.pop() == 1
    assert stack.is_empty()


def test_peek_does_not_remove():
    stack = Stack()
    stack.push("a")
    stack.push("b")
    assert stack.peek() == "b" and stack.peek() == "b" and len(stack) == 2


def test_pop_empty_raises():
    with pytest.raises(EmptyStackError):
        Stack().pop()


def test_peek_empty_raises():
    with pytest.raises(EmptyStackError):
        Stack().peek()


def test_empty_after_draining_one_item():
    stack = Stack()
    stack.push(1)
    stack.pop()
    assert stack.is_empty()
    with pytest.raises(EmptyStackError):
        stack.pop()
