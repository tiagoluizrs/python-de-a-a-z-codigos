import numpy as np
import pytest


# ---------- ex01 ----------
def test_standardize_columns(load_exercise):
    m = load_exercise("ex01_standardize")
    rng = np.random.default_rng(0)
    data = rng.normal([5, 100, -3], [1, 20, 0.1], size=(500, 3))
    z = m.standardize(data)
    assert z.dtype == np.float64 and z.shape == data.shape
    assert np.allclose(z.mean(axis=0), 0, atol=1e-12) and np.allclose(z.std(axis=0), 1)


def test_standardize_keeps_input_and_accepts_lists(load_exercise):
    m = load_exercise("ex01_standardize")
    data = np.array([[1, 2], [3, 4], [5, 6]])
    before = data.copy()
    out = m.standardize(data)
    assert np.array_equal(data, before) and out is not data and out.dtype == np.float64
    assert np.allclose(m.standardize([[1, 2], [3, 4], [5, 6]]), out)


def test_standardize_constant_column_and_axis(load_exercise):
    m = load_exercise("ex01_standardize")
    z = m.standardize(np.array([[1.0, 7.0], [3.0, 7.0], [5.0, 7.0]]))
    assert np.all(np.isfinite(z)) and np.array_equal(z[:, 1], [0, 0, 0])
    rows = m.standardize(np.array([[1.0, 2.0, 3.0], [4.0, 4.0, 4.0]]), axis=1)
    assert np.allclose(rows[0], [-1.2247449, 0, 1.2247449]) and np.array_equal(rows[1], [0, 0, 0])


def test_minmax(load_exercise):
    m = load_exercise("ex01_standardize")
    out = m.minmax_scale(np.array([[0, 10, 5], [5, 20, 5], [10, 30, 5]]))
    assert np.allclose(out, [[0, 0, 0], [0.5, 0.5, 0], [1, 1, 0]])
    assert np.allclose(m.minmax_scale([[0, 1], [10, 3]], low=-1, high=1), [[-1, -1], [1, 1]])


# ---------- ex02 ----------
def test_pairwise_matches_bruteforce(load_exercise):
    m = load_exercise("ex02_nearest")
    pts = np.random.default_rng(1).random((40, 3))
    dist = m.pairwise_distances(pts)
    assert dist.shape == (40, 40) and np.allclose(dist, dist.T) and np.allclose(np.diag(dist), 0)
    for i in (0, 7, 39):
        for j in (1, 5, 22):
            assert dist[i, j] == pytest.approx(np.linalg.norm(pts[i] - pts[j]))
    assert m.pairwise_distances([[0, 0], [3, 4]])[0, 1] == 5.0


def test_nearest_neighbor(load_exercise):
    m = load_exercise("ex02_nearest")
    pts = np.array([[0, 0], [1, 0], [10, 10], [10, 11], [0, 1]])
    assert m.nearest_neighbor(pts).tolist() == [1, 0, 3, 2, 0]
    pts = np.random.default_rng(2).random((60, 2))
    got = m.nearest_neighbor(pts)
    for i in range(60):
        others = [j for j in range(60) if j != i]
        assert got[i] == min(others, key=lambda j: np.linalg.norm(pts[i] - pts[j]))
    assert np.issubdtype(got.dtype, np.integer)


def test_nearest_neighbor_errors_and_ties(load_exercise):
    m = load_exercise("ex02_nearest")
    with pytest.raises(ValueError):
        m.nearest_neighbor([[1.0, 2.0]])
    assert m.nearest_neighbor([[0, 0], [1, 0], [-1, 0]]).tolist() == [1, 0, 0]


# ---------- ex03 ----------
def test_moving_average(load_exercise):
    m = load_exercise("ex03_windows")
    assert np.allclose(m.moving_average([1, 2, 3, 4, 5], 2), [1.5, 2.5, 3.5, 4.5])
    assert np.allclose(m.moving_average([1, 2, 3], 3), [2.0])
    x = np.random.default_rng(3).random(1000)
    expected = [x[i:i + 7].mean() for i in range(1000 - 7 + 1)]
    assert np.allclose(m.moving_average(x, 7), expected)
    assert m.moving_average([1, 2, 3], 1).dtype == np.float64


def test_moving_average_errors(load_exercise):
    m = load_exercise("ex03_windows")
    for window in (0, -1, 4):
        with pytest.raises(ValueError):
            m.moving_average([1, 2, 3], window)
        with pytest.raises(ValueError):
            m.rolling_max([1, 2, 3], window)


def test_rolling_max_and_exceed(load_exercise):
    m = load_exercise("ex03_windows")
    assert m.rolling_max([1, 3, 2, 5, 4], 3).tolist() == [3, 5, 5]
    assert m.rolling_max([5, 4, 3], 1).tolist() == [5, 4, 3]
    count = m.exceed_count([1, 2, 3, 4, 5, 6], 2, 3.0)
    assert count == 3 and type(count) is int
    assert m.exceed_count([1, 1, 1], 2, 5) == 0


# ---------- ex04 ----------
def test_group_sum_and_mean(load_exercise):
    m = load_exercise("ex04_groups")
    keys, values = [0, 1, 0, 2, 1, 0], [1.0, 2.0, 3.0, 10.0, 4.0, 5.0]
    assert m.group_sum(keys, values, 4).tolist() == [9.0, 6.0, 10.0, 0.0]
    mean = m.group_mean(keys, values, 4)
    assert mean[:3].tolist() == [3.0, 3.0, 10.0] and np.isnan(mean[3])


def test_group_mean_without_warnings(load_exercise, recwarn):
    m = load_exercise("ex04_groups")
    m.group_mean([0, 0], [1.0, 3.0], 3)
    assert not [w for w in recwarn.list if issubclass(w.category, RuntimeWarning)]


def test_group_max_and_topk(load_exercise):
    m = load_exercise("ex04_groups")
    keys, values = [0, 1, 0, 2, 1, 0], [1.0, 2.0, 3.0, 10.0, 4.0, 5.0]
    mx = m.group_max(keys, values, 4)
    assert mx[:3].tolist() == [5.0, 4.0, 10.0] and mx[3] == -np.inf
    top = m.top_k_per_group(keys, values, 4, 2)
    assert [t.tolist() for t in top] == [[5.0, 3.0], [4.0, 2.0], [10.0], []]


def test_groups_large_matches_python(load_exercise):
    m = load_exercise("ex04_groups")
    rng = np.random.default_rng(4)
    keys = rng.integers(0, 50, 20_000)
    values = rng.normal(size=20_000)
    sums = m.group_sum(keys, values, 50)
    for g in (0, 17, 49):
        assert sums[g] == pytest.approx(values[keys == g].sum())
    assert m.group_max(keys, values, 50)[5] == values[keys == 5].max()


# ---------- ex05 ----------
def test_softmax_basic_and_stable(load_exercise):
    m = load_exercise("ex05_softmax")
    out = m.softmax([1.0, 2.0, 3.0])
    assert np.allclose(out, [0.09003057, 0.24472847, 0.66524096]) and out.sum() == pytest.approx(1.0)
    big = m.softmax([1000.0, 1001.0])
    assert np.all(np.isfinite(big)) and np.allclose(big, [0.26894142, 0.73105858])
    assert np.allclose(m.softmax([-1000.0, -1000.0]), [0.5, 0.5])


def test_softmax_axis_and_input_untouched(load_exercise):
    m = load_exercise("ex05_softmax")
    logits = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
    before = logits.copy()
    out = m.softmax(logits, axis=1)
    assert np.allclose(out.sum(axis=1), 1) and np.allclose(out[1], 1 / 3) and np.array_equal(logits, before)
    cols = m.softmax(logits, axis=0)
    assert np.allclose(cols.sum(axis=0), 1)


def test_one_hot(load_exercise):
    m = load_exercise("ex05_softmax")
    out = m.one_hot([2, 0, 1, 2], 3)
    assert out.dtype == np.uint8 and out.tolist() == [[0, 0, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert m.one_hot([], 3).shape == (0, 3)
    for bad in ([3], [-1], [0, 5]):
        with pytest.raises(ValueError):
            m.one_hot(bad, 3)


def test_accuracy(load_exercise):
    m = load_exercise("ex05_softmax")
    logits = [[0.1, 0.9], [0.8, 0.2], [0.3, 0.7], [0.6, 0.4]]
    assert m.accuracy(logits, [1, 0, 0, 0]) == 0.75
    assert m.accuracy(np.empty((0, 3)), []) == 0.0
    assert isinstance(m.accuracy(logits, [1, 0, 1, 1]), float)


# ---------- ex06 ----------
def test_to_gray(load_exercise):
    m = load_exercise("ex06_image")
    img = np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]], dtype=np.uint8)
    gray = m.to_gray(img)
    assert gray.dtype == np.uint8 and gray.shape == (2, 2)
    assert gray.tolist() == [[76, 149], [29, 254]] or gray.tolist() == [[76, 149], [29, 255]]
    already = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    out = m.to_gray(already)
    assert np.array_equal(out, already) and out is not already


def test_brighten_no_wraparound(load_exercise):
    m = load_exercise("ex06_image")
    img = np.array([[0, 100, 200, 255]], dtype=np.uint8)
    before = img.copy()
    up = m.brighten(img, 100)
    assert up.dtype == np.uint8 and up.tolist() == [[100, 200, 255, 255]]
    assert m.brighten(img, -150).tolist() == [[0, 0, 50, 105]]
    assert np.array_equal(img, before)


def test_center_crop_is_view(load_exercise):
    m = load_exercise("ex06_image")
    img = np.arange(100, dtype=np.uint8).reshape(10, 10)
    crop = m.center_crop(img, 4, 6)
    assert crop.shape == (4, 6) and np.shares_memory(img, crop) and crop[0, 0] == img[3, 2]
    assert m.center_crop(np.zeros((8, 8, 3), np.uint8), 8, 8).shape == (8, 8, 3)
    with pytest.raises(ValueError):
        m.center_crop(img, 11, 2)


def test_histogram_and_threshold(load_exercise):
    m = load_exercise("ex06_image")
    gray = np.array([[0, 0, 255], [10, 10, 10]], dtype=np.uint8)
    hist = m.histogram(gray)
    assert hist.shape == (256,) and hist[0] == 2 and hist[10] == 3 and hist[255] == 1 and hist.sum() == 6
    mask = m.threshold(gray, 10)
    assert mask.dtype == bool and mask.tolist() == [[False, False, True], [True, True, True]]
