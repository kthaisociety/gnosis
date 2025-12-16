"""
Unit tests for the Relative Number Set Similarity (RNSS) metric.
"""
import sys
import os
import numpy as np
import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from lib.metrics.rnss import extract_values, relative_distance, compute_rnss


def test_extract_values_with_numpy_array():
    """Test value extraction from numpy arrays."""
    # Test with simple numeric array
    arr = np.array([[1.0, 2.0], [3.0, 4.0]])
    values = extract_values(arr)
    assert len(values) == 4
    assert all(v in [1.0, 2.0, 3.0, 4.0] for v in values)
    
    # Test with string values containing numbers
    arr = np.array([["10%", "20%"], ["30", "40.5"]])
    values = extract_values(arr)
    assert len(values) == 4
    assert all(v in [10.0, 20.0, 30.0, 40.5] for v in values)
    
    # Test with mixed content
    arr = np.array([["Temperature: 25°C", "Humidity: 60%"], ["Pressure: 1013hPa", "Wind: 5.2m/s"]])
    values = extract_values(arr)
    assert len(values) == 4
    assert all(v in [25.0, 60.0, 1013.0, 5.2] for v in values)


def test_extract_values_with_list():
    """Test value extraction from lists."""
    # Test with simple list
    table = [["1.5", "2.5"], ["3.5", "4.5"]]
    values = extract_values(table)
    assert len(values) == 4
    assert all(v in [1.5, 2.5, 3.5, 4.5] for v in values)
    
    # Test with mixed types
    table = [[1, "2.0"], ["3", 4.5]]
    values = extract_values(table)
    assert len(values) == 4
    assert all(v in [1.0, 2.0, 3.0, 4.5] for v in values)


def test_extract_values_edge_cases():
    """Test edge cases for value extraction."""
    # Empty table
    values = extract_values([])
    assert len(values) == 0
    
    # Table with no numeric values
    table = [["hello", "world"], ["no", "numbers"]]
    values = extract_values(table)
    assert len(values) == 0
    
    # Table with negative numbers
    table = [["-5", "-10.5"], ["-100%", "-0.1"]]
    values = extract_values(table)
    assert len(values) == 4
    assert all(v in [-5.0, -10.5, -100.0, -0.1] for v in values)


def test_relative_distance():
    """Test the relative distance function."""
    # Test with identical values
    assert relative_distance(5.0, 5.0) == 0.0
    
    # Test with different values
    assert relative_distance(10.0, 5.0) == 1.0  # (10-5)/5 = 1.0
    assert relative_distance(5.0, 10.0) == 0.5  # (10-5)/10 = 0.5
    
    # Test with zero target
    assert relative_distance(0.0, 0.0) == 0.0
    assert relative_distance(5.0, 0.0) == 1.0
    assert relative_distance(0.0, 5.0) == 1.0
    
    # Test with very small target (epsilon case)
    assert relative_distance(1e-11, 1e-10) == 0.0  # Should be treated as zero
    
    # Test with negative values
    assert relative_distance(-5.0, -10.0) == 0.5  # |-5 - (-10)| / |-10| = 5/10 = 0.5
    assert relative_distance(-10.0, -5.0) == 1.0  # |-10 - (-5)| / |-5| = 5/5 = 1.0


def test_compute_rnss_perfect_match():
    """Test RNSS with perfect matching tables."""
    # Identical tables
    pred = [["1.0", "2.0"], ["3.0", "4.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0
    
    # Same values, different order
    pred = [["4.0", "3.0"], ["2.0", "1.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0


def test_compute_rnss_partial_match():
    """Test RNSS with partially matching tables."""
    # Some matching, some different values
    pred = [["1.0", "2.0"], ["3.0", "5.0"]]  # 5.0 instead of 4.0
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    # Should be less than 1.0 but greater than 0.0
    assert 0.0 < rnss < 1.0


def test_compute_rnss_no_match():
    """Test RNSS with completely different tables."""
    pred = [["100.0", "200.0"], ["300.0", "400.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 0.0


def test_compute_rnss_different_sizes():
    """Test RNSS with tables of different sizes."""
    # Pred has more values
    pred = [["1.0", "2.0"], ["3.0", "4.0"], ["5.0", "6.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    # Should account for unmatched elements
    assert 0.0 < rnss < 1.0
    
    # Target has more values
    pred = [["1.0", "2.0"]]
    target = [["1.0", "2.0"], ["3.0", "4.0"], ["5.0", "6.0"]]
    rnss = compute_rnss(pred, target)
    assert 0.0 < rnss < 1.0


def test_compute_rnss_edge_cases():
    """Test RNSS edge cases."""
    # Empty tables
    rnss = compute_rnss([], [])
    assert rnss == 1.0
    
    # One empty table
    rnss = compute_rnss([], [["1.0", "2.0"]])
    assert rnss == 0.0
    
    rnss = compute_rnss([["1.0", "2.0"]], [])
    assert rnss == 0.0
    
    # Tables with no numeric values
    pred = [["hello", "world"], ["no", "numbers"]]
    target = [["foo", "bar"], ["baz", "qux"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0  # Both empty after extraction


def test_compute_rnss_with_numpy_arrays():
    """Test RNSS with numpy array inputs."""
    pred = np.array([[1.0, 2.0], [3.0, 4.0]])
    target = np.array([[1.0, 2.0], [3.0, 4.0]])
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0
    
    pred = np.array([[1.0, 2.0], [3.0, 5.0]])
    target = np.array([[1.0, 2.0], [3.0, 4.0]])
    rnss = compute_rnss(pred, target)
    assert 0.0 < rnss < 1.0


def test_compute_rnss_with_mixed_formats():
    """Test RNSS with mixed input formats."""
    # List pred, numpy target
    pred = [["1.0", "2.0"], ["3.0", "4.0"]]
    target = np.array([[1.0, 2.0], [3.0, 4.0]])
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0
    
    # Numpy pred, list target
    pred = np.array([[1.0, 2.0], [3.0, 4.0]])
    target = [["1.0", "2.0"], ["3.0", "4.0"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0


def test_compute_rnss_with_percentages():
    """Test RNSS with percentage values."""
    pred = [["50%", "75%"], ["100%", "25%"]]
    target = [["50%", "75%"], ["100%", "25%"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0
    
    # Different percentage values
    pred = [["50%", "75%"], ["100%", "25%"]]
    target = [["50%", "75%"], ["100%", "30%"]]
    rnss = compute_rnss(pred, target)
    assert 0.0 < rnss < 1.0


def test_compute_rnss_with_negative_numbers():
    """Test RNSS with negative numbers."""
    pred = [["-1.0", "-2.0"], ["-3.0", "-4.0"]]
    target = [["-1.0", "-2.0"], ["-3.0", "-4.0"]]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0
    
    # Different negative values
    pred = [["-1.0", "-2.0"], ["-3.0", "-5.0"]]
    target = [["-1.0", "-2.0"], ["-3.0", "-4.0"]]
    rnss = compute_rnss(pred, target)
    assert 0.0 < rnss < 1.0


def test_compute_rnss_with_complex_strings():
    """Test RNSS with complex strings containing numbers."""
    pred = [
        ["Temperature: 25.5°C", "Humidity: 60%"],
        ["Pressure: 1013.25hPa", "Wind: 5.2m/s"]
    ]
    target = [
        ["Temperature: 25.5°C", "Humidity: 60%"],
        ["Pressure: 1013.25hPa", "Wind: 5.2m/s"]
    ]
    rnss = compute_rnss(pred, target)
    assert rnss == 1.0
    
    # Slightly different values
    pred = [
        ["Temperature: 25.5°C", "Humidity: 60%"],
        ["Pressure: 1013.25hPa", "Wind: 5.2m/s"]
    ]
    target = [
        ["Temperature: 25.5°C", "Humidity: 65%"],
        ["Pressure: 1013.25hPa", "Wind: 5.2m/s"]
    ]
    rnss = compute_rnss(pred, target)
    assert 0.0 < rnss < 1.0


def test_compute_rnss_result_range():
    """Test that RNSS always returns values in [0, 1] range."""
    test_cases = [
        ([["1.0", "2.0"]], [["1.0", "2.0"]]),  # Perfect match
        ([["1.0", "2.0"]], [["3.0", "4.0"]]),  # No match
        ([["1.0"]], [["1.0", "2.0"]]),  # Different sizes
        ([["100%", "200%"], ["300%", "400%"]], [["1%", "2%"], ["3%", "4%"]]),  # Large differences
        ([["0.0", "0.0"]], [["0.0", "0.0"]]),  # All zeros
        ([["-1.0", "1.0"]], [["-1.0", "1.0"]]),  # Mixed signs
    ]
    
    for pred, target in test_cases:
        rnss = compute_rnss(pred, target)
        assert 0.0 <= rnss <= 1.0, f"RNSS out of range for pred={pred}, target={target}: {rnss}"


def test_compute_rnss_asymmetric_property():
    """
    Test that RNSS is asymmetric (order of arguments matters).

    RNSS uses relative distance D(p,t) = |p-t|/|t|, which is asymmetric
    because it measures error relative to the target value.
    This is intentional: RNSS(pred, target) measures how well pred matches target,
    while RNSS(target, pred) measures how well target matches pred.
    """
    pred = [["1.0", "2.0"], ["3.0", "4.0"]]
    target = [["1.0", "2.0"], ["3.0", "5.0"]]

    rnss1 = compute_rnss(pred, target)
    rnss2 = compute_rnss(target, pred)

    # Verify asymmetry: swapping arguments should give different results
    # when the values differ
    assert rnss1 != rnss2, "RNSS should be asymmetric"

    # Both should still be in valid range [0, 1]
    assert 0.0 <= rnss1 <= 1.0
    assert 0.0 <= rnss2 <= 1.0


def test_compute_rnss_with_single_values():
    """Test RNSS with single value tables."""
    # Single matching value
    rnss = compute_rnss([["5.0"]], [["5.0"]])
    assert rnss == 1.0
    
    # Single non-matching value
    rnss = compute_rnss([["5.0"]], [["10.0"]])
    assert 0.0 < rnss < 1.0
    
    # Single value vs empty
    rnss = compute_rnss([["5.0"]], [])
    assert rnss == 0.0
