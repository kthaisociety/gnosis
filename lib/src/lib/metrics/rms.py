import numpy as np
from typing import Union, List, Tuple
from scipy.optimize import linear_sum_assignment
import Levenshtein

# Link to the paper for more details: https://arxiv.org/pdf/2212.10505




def relative_distance(p: float, t: float, epsilon: float = 1e-10) -> float:
    # Relative error w.r.t. the target value, clipped to [0, 1]
    if abs(t) < epsilon:
        return 0.0 if abs(p) < epsilon else 1.0
    return min(1.0, abs(p - t) / abs(t))


def extract_mappings(
    table: Union[str, List[List[str]], np.ndarray]
) -> List[Tuple[str, str, float]]:
    # Convert table into unordered (row_label, col_label, value) mappings

    if isinstance(table, np.ndarray):
        table = table.tolist()

    if not table or not isinstance(table, list):
        return []

    header = table[0][1:]
    mappings = []

    for row in table[1:]:
        row_label = str(row[0])
        for col_label, cell in zip(header, row[1:]):
            try:
                value = float(cell)
                mappings.append((row_label, str(col_label), value))
            except (ValueError, TypeError):
                continue

    return mappings


def compute_rms(
    predicted_table: Union[str, List[List[str]], np.ndarray],
    target_table: Union[str, List[List[str]], np.ndarray],
    tau: float = 1.0,
    theta: float = 1.0,
) -> float:

    P = extract_mappings(predicted_table)
    T = extract_mappings(target_table)

    N, M = len(P), len(T)

    if N == 0 and M == 0:
        return 1.0
    if N == 0 or M == 0:
        return 0.0

    # Cost matrices for Hungarian matching:
    # key_cost decides WHICH entries are matched
    # value_cost only affects the similarity score after matching
    key_cost = np.zeros((N, M))
    value_cost = np.zeros((N, M))

    for i, (pr, pc, pv) in enumerate(P):
        pk = f"{pr}|{pc}"
        for j, (tr, tc, tv) in enumerate(T):
            tk = f"{tr}|{tc}"

            # Normalized Levenshtein distance between (row, column) keys
            key_dist = Levenshtein.distance(pk, tk) / max(len(pk), len(tk))
            key_cost[i, j] = min(1.0, key_dist / tau)

            # Relative numeric distance between values
            val_dist = relative_distance(pv, tv)
            value_cost[i, j] = min(1.0, val_dist / theta)

    # Find optimal one-to-one mapping between predicted and target entries
    row_ind, col_ind = linear_sum_assignment(key_cost)

    similarities = []
    for i, j in zip(row_ind, col_ind):
        # Entry similarity requires BOTH correct placement and correct value
        key_sim = 1.0 - key_cost[i, j]
        val_sim = 1.0 - value_cost[i, j]
        similarities.append(key_sim * val_sim)

    # Unmatched entries are treated as maximally wrong
    matched = len(similarities)
    unmatched_p = N - matched
    unmatched_t = M - matched

    total_error = sum(1.0 - s for s in similarities)
    total_error += unmatched_p + unmatched_t

    precision = 1.0 - total_error / N
    recall = 1.0 - total_error / M

    if precision + recall == 0:
        return 0.0

    # RMS is reported as F1 to balance over- and under-generation
    return 2.0 * precision * recall / (precision + recall)