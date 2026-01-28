import numpy as np
from eval.metrics import extract_values, relative_distance, compute_rnss


def test_extract_values_with_numpy_array():
    arr = np.array([[1.0, 2.0], [3.0, 4.0]])
    values = extract_values(arr)
    assert len(values) == 4
    assert all(v in [1.0, 2.0, 3.0, 4.0] for v in values)


def test_extract_values_with_list():
    table = [["1.5", "2.5"], ["3.5", "4.5"]]
    values = extract_values(table)
    assert len(values) == 4
    assert all(v in [1.5, 2.5, 3.5, 4.5] for v in values)


def test_extract_values_edge_cases():
    assert len(extract_values([])) == 0

    table = [["hello", "world"], ["no", "numbers"]]
    assert len(extract_values(table)) == 0

    table = [["-5", "-10.5"], ["-100%", "-0.1"]]
    values = extract_values(table)
    assert len(values) == 4
    assert all(v in [-5.0, -10.5, -100.0, -0.1] for v in values)


def test_relative_distance():
    assert relative_distance(5.0, 5.0) == 0.0
    assert relative_distance(10.0, 5.0) == 1.0
    assert relative_distance(5.0, 10.0) == 0.5
    assert relative_distance(0.0, 0.0) == 0.0
    assert relative_distance(5.0, 0.0) == 1.0
    assert relative_distance(0.0, 5.0) == 1.0


def test_compute_rnss_perfect_match():
    pred = [["1.0", "2.0"], ["3.0", "4.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    assert compute_rnss(pred, target) == 1.0

    pred = [["4.0", "3.0"], ["2.0", "1.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    assert compute_rnss(pred, target) == 1.0


def test_compute_rnss_partial_match():
    pred = [["1.0", "2.0"], ["3.0", "5.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    assert 0.0 < rnss < 1.0


def test_compute_rnss_no_match():
    pred = [["100.0", "200.0"], ["300.0", "400.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    assert compute_rnss(pred, target) == 0.0


def test_compute_rnss_edge_cases():
    assert compute_rnss([], []) == 1.0
    assert compute_rnss([], [["1.0", "2.0"]]) == 0.0
    assert compute_rnss([["1.0", "2.0"]], []) == 0.0


def test_compute_rnss_with_numpy_arrays():
    pred = np.array([[1.0, 2.0], [3.0, 4.0]])
    target = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert compute_rnss(pred, target) == 1.0


def test_compute_rnss_result_range():
    test_cases = [
        ([["1.0", "2.0"]], [["1.0", "2.0"]]),
        ([["1.0", "2.0"]], [["3.0", "4.0"]]),
        ([["1.0"]], [["1.0", "2.0"]]),
        ([["0.0", "0.0"]], [["0.0", "0.0"]]),
    ]
    for pred, target in test_cases:
        rnss = compute_rnss(pred, target)
        assert 0.0 <= rnss <= 1.0