"""
This module provides common data utilities for the Hong Kong Port Digital Twin.
"""

import pandas as pd
from typing import List, Dict, Union

def efficient_groupby(df: pd.DataFrame, group_cols: List[str], 
                     agg_funcs: Dict[str, Union[str, List[str]]]) -> pd.DataFrame:
    """Efficient groupby operation with optimization."""
    # Use categorical data types for grouping columns if beneficial
    for col in group_cols:
        if df[col].dtype == 'object' and df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')
    
    return df.groupby(group_cols).agg(agg_funcs).reset_index()