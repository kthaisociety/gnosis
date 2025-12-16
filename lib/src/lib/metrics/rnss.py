import re
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import Union, List, Any


# Link to the paper for more details: https://arxiv.org/pdf/2212.10505


#TODO double check which format we will use for table input in the end
def extract_values(table: Union[str, List[List[str]], np.ndarray]) -> List[float]:
 
    values: list[Any] = []


        
    if isinstance(table, np.ndarray):
      
        for item in table.flatten():
            try:
                values.append(float(item))
            except (ValueError, TypeError):
               
                if isinstance(item, str):
                    pattern = r'-?\d+\.?\d*%?'
                    matches: list[Any] = re.findall(pattern, item)
                    for match in matches:
                        try:
                            value = match.rstrip('%')
                            values.append(float(value))
                        except ValueError:
                            continue
                            
                        
    elif isinstance(table, list):
       
        for row in table:
            if isinstance(row, list):
                for cell in row:
                    try:
                        values.append(float(cell))
                    except (ValueError, TypeError):
                        if isinstance(cell, str):
                            pattern = r'-?\d+\.?\d*%?'
                            matches = re.findall(pattern, cell)
                            for match in matches:
                                try:
                                    value = match.rstrip('%')
                                    values.append(float(value))
                                except ValueError:
                                    continue
            else:
                try:
                    values.append(float(row))
                except (ValueError, TypeError):
                    if isinstance(row, str):
                        pattern = r'-?\d+\.?\d*%?'
                        matches = re.findall(pattern, row)
                        for match in matches:
                            try:
                                value = match.rstrip('%')
                                values.append(float(value))
                            except ValueError:
                                continue
    
    return values


def relative_distance(p: float, t: float) -> float:

    epsilon:float = 1e-10

    if abs(t) <= epsilon:
     
        if abs(p) <= epsilon:
            return 0.0  
        else:
            return 1.0 
    
    return min(1.0, abs(p - t) / abs(t))


def compute_rnss(predicted_table: Union[str, List[List[str]], np.ndarray],
                 target_table: Union[str, List[List[str]], np.ndarray]) -> float:
    """
    Compute the Relative Number Set Similarity (RNSS) between two tables.
    
    The metric:
    1. Extracts all numeric values from both tables
    2. Computes pairwise relative distances
    3. Finds optimal matching using Hungarian algorithm
    4. Returns similarity score in [0, 1]
    
    RNSS = 1 - (sum of matched distances) / max(N, M)
    
    where N and M are the number of values in predicted and target tables.
    
    Args:
        predicted_table: The predicted/extracted table
        target_table: The ground truth table
        epsilon: Small value for numerical stability
        
    Returns:
        RNSS score between 0 and 1 (higher is better)
    """

    P: list[float] = extract_values(predicted_table)
    T: list[float] = extract_values(target_table)
    N: int = len(P)
    M: int = len(T)
    
    #edge cases
    if N == 0 and M == 0:
        return 1.0  
    if N == 0 or M == 0:
        return 0.0  
    

    distance_matrix = np.zeros((N, M))
    for i, p in enumerate(P):
        for j, t in enumerate(T):
            distance_matrix[i, j] = relative_distance(p, t)
    

    max_dim: int = max(N, M)
    
    if N != M:
        # create padded cost matrix
        padded_matrix = np.ones((max_dim, max_dim))
        padded_matrix[:N, :M] = distance_matrix
    else:
        padded_matrix = distance_matrix
    
    # find optimal assignment with hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(padded_matrix)
    
    # compute total score
    total_distance = 0.0
    num_real_matches: int = min(N, M)
    
    for i, j in zip(row_ind, col_ind):
        if i < N and j < M:
            total_distance += distance_matrix[i, j]
    
    # add penalty for unmatched elements (they contribute distance of 1.0)
    unmatched_count: int = abs(N - M)
    total_distance += unmatched_count * 1.0
    
    # Compute RNSS
    rnss: float = 1.0 - (total_distance / max_dim)
    
    return max(0.0, rnss)  


    
