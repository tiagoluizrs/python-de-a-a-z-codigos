import collections

import pytest

import tasks


def test_split_chunks(load_exercise):
    split_chunks = load_exercise("ex01_chunks").split_chunks
    assert split_chunks(range(7), 3) == [[0, 1, 2], [3, 4], [5, 6]]
    assert split_chunks([], 3) == [[], [], []] and split_chunks([1, 2], 4) == [[1], [2], [], []]
    for total, n in ((100, 7), (10, 10), (1, 1), (13, 4)):
        chunks = split_chunks(range(total), n)
        sizes = [len(c) for c in chunks]
        assert len(chunks) == n and max(sizes) - min(sizes) <= 1 and sizes == sorted(sizes, reverse=True)
        assert [x for c in chunks for x in c] == list(range(total))
    with pytest.raises(ValueError):
        split_chunks([1], 0)


def test_chunk_size(load_exercise):
    chunk_size = load_exercise("ex01_chunks").chunk_size
    assert chunk_size(20_000, 4) == 1250 and chunk_size(10, 4) == 1 and chunk_size(0, 4) == 1
    assert chunk_size(100, 2, factor=1) == 50 and chunk_size(101, 2, factor=1) == 51
    for args in ((10, 0), (10, 2, 0)):
        with pytest.raises(ValueError):
            chunk_size(*args)


def test_parallel_map_ordered_and_correct(load_exercise):
    parallel_map = load_exercise("ex02_parallel_map").parallel_map
    assert parallel_map(tasks.square, range(50), processes=3) == [x * x for x in range(50)]
    assert parallel_map(tasks.square, range(10), processes=2, chunksize=1) == [x * x for x in range(10)]
    assert parallel_map(tasks.cpu_sum, [1000, 2000], processes=2) == [tasks.cpu_sum(1000), tasks.cpu_sum(2000)]


def test_parallel_map_edges(load_exercise):
    parallel_map = load_exercise("ex02_parallel_map").parallel_map
    assert parallel_map(tasks.square, []) == []
    with pytest.raises(ValueError):
        parallel_map(tasks.square, [1], processes=0)
    with pytest.raises(ValueError, match="item 3"):
        parallel_map(tasks.fail, range(6), processes=2)


def test_parallel_map_uses_other_processes(load_exercise):
    import os
    parallel_map = load_exercise("ex02_parallel_map").parallel_map
    pids = set(parallel_map(tasks.pid, range(40), processes=2, chunksize=1))
    assert os.getpid() not in pids and 1 <= len(pids) <= 2


def test_merge_counts(load_exercise):
    merge_counts = load_exercise("ex03_word_count").merge_counts
    a, b = collections.Counter("aab"), collections.Counter("bcc")
    original = a.copy()
    assert merge_counts([a, b]) == collections.Counter("aabbcc") and a == original
    assert merge_counts([]) == collections.Counter()


def test_parallel_word_count(load_exercise):
    parallel_word_count = load_exercise("ex03_word_count").parallel_word_count
    texts = ["O rato roeu", "o REI de Roma", "rato rato"]
    result = parallel_word_count(texts, processes=2)
    assert result["rato"] == 3 and result["o"] == 2 and result["roma"] == 1
    assert result == sum((tasks.count_words(t) for t in texts), collections.Counter())
    assert parallel_word_count([]) == collections.Counter()


def test_shared_counter(load_exercise):
    count = load_exercise("ex04_shared_counter").count_with_processes
    assert count(3, 2_000) == 6_000 and count(1, 0) == 0
    for args in ((0, 5), (2, -1)):
        with pytest.raises(ValueError):
            count(*args)


def test_run_isolated_result_and_errors(load_exercise):
    m = load_exercise("ex05_isolated")
    assert m.run_isolated(tasks.square, 7, timeout=30) == 49
    with pytest.raises(ValueError, match="item 3"):
        m.run_isolated(tasks.fail, 3, timeout=30)


def test_run_isolated_crash_and_timeout(load_exercise):
    import time
    m = load_exercise("ex05_isolated")
    with pytest.raises(m.ProcessCrashed) as info:
        m.run_isolated(tasks.crash, timeout=30)
    assert info.value.exitcode == 7
    start = time.perf_counter()
    with pytest.raises(TimeoutError):
        m.run_isolated(tasks.slow, 60, timeout=1.5)
    assert time.perf_counter() - start < 20


def test_estimate_parallel_time(load_exercise):
    m = load_exercise("ex06_should_parallelize")
    assert m.estimate_parallel_time(8, 16, 4, startup=0.1, per_task_overhead=0.01) == pytest.approx(0.1 + 4 * 0.5 + 0.16)
    assert m.estimate_parallel_time(5, 5, 4, startup=0, per_task_overhead=0) == pytest.approx(2.0)
    for args in ((1, 0, 2), (1, 2, 0)):
        with pytest.raises(ValueError):
            m.estimate_parallel_time(*args)


def test_should_parallelize(load_exercise):
    should = load_exercise("ex06_should_parallelize").should_parallelize
    assert should(10, 40, 8) is True
    assert should(0.05, 10, 8) is False
    assert should(1, 1, 8) is False
    assert should(10, 40, 8, startup=20) is False
