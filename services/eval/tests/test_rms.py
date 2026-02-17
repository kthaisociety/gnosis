import numpy as np
from eval.metrics import compute_rms, extract_mappings


def test_identical_tables():
    table = [["Year", "Sales"], ["2020", 100], ["2021", 120]]
    assert compute_rms(table, table) == 1.0


def test_value_error_only():
    pred = [["Year", "Sales"], ["2020", 95], ["2021", 120]]
    target = [["Year", "Sales"], ["2020", 100], ["2021", 120]]
    score = compute_rms(pred, target)
    assert 0.8 < score < 1.0


def test_missing_row_penalized():
    pred = [["Year", "Sales"], ["2020", 100]]
    target = [["Year", "Sales"], ["2020", 100], ["2021", 120]]
    assert compute_rms(pred, target) == 0.0


def test_extra_row_penalized():
    pred = [["Year", "Sales"], ["2020", 100], ["2021", 120], ["2022", 130]]
    target = [["Year", "Sales"], ["2020", 100], ["2021", 120]]
    score = compute_rms(pred, target)
    assert 0.0 < score < 1.0


def test_wrong_header_penalized():
    pred = [["Year", "Revenue"], ["2020", 100]]
    target = [["Year", "Sales"], ["2020", 100]]
    assert compute_rms(pred, target) < 1.0


def test_completely_wrong_table():
    pred = [["Foo", "Bar"], ["A", 1], ["B", 2]]
    target = [["Year", "Sales"], ["2020", 100], ["2021", 120]]
    assert compute_rms(pred, target) < 0.01


def test_empty_tables():
    assert compute_rms([], []) == 1.0


def test_one_empty_table():
    target = [["Year", "Sales"], ["2020", 100]]
    assert compute_rms([], target) == 0.0
    assert compute_rms(target, []) == 0.0


def test_numpy_input():
    pred = np.array([["Year", "Sales"], ["2020", "100"], ["2021", "120"]])
    target = [["Year", "Sales"], ["2020", 100], ["2021", 120]]
    assert compute_rms(pred, target) == 1.0


def test_extract_mappings_basic():
    table = [["Year", "Sales", "Profit"], ["2020", 100, 20], ["2021", 120, 25]]
    mappings = extract_mappings(table)
    expected = {
        ("2020", "Sales", 100.0),
        ("2020", "Profit", 20.0),
        ("2021", "Sales", 120.0),
        ("2021", "Profit", 25.0),
    }
    assert set(mappings) == expected


def test_extract_mappings_ignores_non_numeric_cells():
    table = [
        ["Year", "Sales", "Note"],
        ["2020", "100", "approx"],
        ["2021", "N/A", "missing"],
    ]
    mappings = extract_mappings(table)
    expected = {("2020", "Sales", 100.0)}
    assert set(mappings) == expected
