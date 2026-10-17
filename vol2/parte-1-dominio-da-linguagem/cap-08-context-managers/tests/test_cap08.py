import io

import pytest


class FakeClock:
    def __init__(self, *values):
        self.values = iter(values)

    def __call__(self):
        return next(self.values)


def test_timer(load_exercise):
    Timer = load_exercise("ex01_timer").Timer
    timer = Timer(clock=FakeClock(10.0, 12.5, 20.0, 21.0))
    assert timer.elapsed is None
    with timer as same:
        pass
    assert same is timer and timer.elapsed == 2.5
    with timer:
        pass
    assert timer.laps == [2.5, 1.0]


def test_timer_does_not_suppress(load_exercise):
    Timer = load_exercise("ex01_timer").Timer
    timer = Timer(clock=FakeClock(1.0, 4.0))
    with pytest.raises(ZeroDivisionError):
        with timer:
            1 / 0
    assert timer.elapsed == 3.0


def test_transaction_commit_and_rollback(load_exercise):
    transaction = load_exercise("ex02_transaction").transaction
    data = {"a": 1}
    with transaction(data) as tx:
        assert tx is data
        tx["a"] = 2
        tx["b"] = 3
    assert data == {"a": 2, "b": 3}
    with pytest.raises(RuntimeError):
        with transaction(data) as tx:
            tx["a"] = 99
            del tx["b"]
            raise RuntimeError("falha")
    assert data == {"a": 2, "b": 3}


def test_suppress_and_count(load_exercise):
    suppress_and_count = load_exercise("ex02_transaction").suppress_and_count
    with suppress_and_count(KeyError, ValueError) as counter:
        assert counter.count == 0
        {}["x"]
    assert counter.count == 1
    with suppress_and_count(ValueError) as counter:
        int("x")
    assert counter.count == 1
    with pytest.raises(ZeroDivisionError):
        with suppress_and_count(KeyError):
            1 / 0


class Handle(io.StringIO):
    pass


def test_read_all_closes_everything(load_exercise):
    read_all = load_exercise("ex03_open_all").read_all
    handles = {}

    def opener(path):
        handles[path] = Handle(f"conteudo {path}")
        return handles[path]

    assert read_all(["a", "b", "c"], opener=opener) == [
        "conteudo a", "conteudo b", "conteudo c"]
    assert all(h.closed for h in handles.values())


def test_read_all_failure_closes_opened(load_exercise):
    read_all = load_exercise("ex03_open_all").read_all
    handles = []

    def opener(path):
        if path == "c":
            raise FileNotFoundError(path)
        handle = Handle("x")
        handles.append(handle)
        return handle

    with pytest.raises(FileNotFoundError):
        read_all(["a", "b", "c", "d"], opener=opener)
    assert len(handles) == 2 and all(h.closed for h in handles)


class Res:
    def __init__(self, log, name, fail=False):
        self.log, self.name, self.fail = log, name, fail

    def __enter__(self):
        if self.fail:
            raise OSError(self.name)
        self.log.append(f"open {self.name}")
        return self.name.upper()

    def __exit__(self, *exc):
        self.log.append(f"close {self.name}")
        return False


def test_pool_success_and_order(load_exercise):
    Pool = load_exercise("ex04_pool").Pool
    log = []
    with Pool([lambda: Res(log, "a"), lambda: Res(log, "b")]) as values:
        assert values == ["A", "B"]
        log.append("body")
    assert log == ["open a", "open b", "body", "close b", "close a"]


def test_pool_failure_rolls_back(load_exercise):
    Pool = load_exercise("ex04_pool").Pool
    log = []
    factories = [lambda: Res(log, "a"), lambda: Res(log, "b"),
                 lambda: Res(log, "c", fail=True)]
    with pytest.raises(OSError):
        with Pool(factories):
            pass
    assert log == ["open a", "open b", "close b", "close a"]


def test_pool_body_exception_propagates(load_exercise):
    Pool = load_exercise("ex04_pool").Pool
    log = []
    with pytest.raises(ValueError):
        with Pool([lambda: Res(log, "a")]):
            raise ValueError("corpo")
    assert log == ["open a", "close a"]


def test_capture_prints(load_exercise, capsys):
    capture_prints = load_exercise("ex05_capture").capture_prints
    with capture_prints() as cap:
        print("a")
        print("b", "c")
    assert cap.lines() == ["a", "b c"]
    with pytest.raises(RuntimeError):
        with capture_prints():
            print("dentro")
            raise RuntimeError("x")
    print("restaurado")
    assert capsys.readouterr().out == "restaurado\n"
