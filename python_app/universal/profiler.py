"""
Universal Dataset Profiler & Quality Assessor
=============================================
Calculates comprehensive dataset metrics and evaluates data quality:
- Volumetric counts (rows, columns, cells)
- Missing value concentrations and high-missing columns
- Duplicate row detections
- Type distribution (numeric, categorical, date, text, boolean)
- Constant / invariant or all-null columns

Represents the raw dataset objectively without modifying or dropping records.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd
import numpy as np

from python_app.universal.type_detector import detect_all_column_types, ColumnType


@dataclass
class DatasetProfile:
    row_count: int
    column_count: int
    total_cells: int
    duplicate_row_count: int
    duplicate_row_pct: float
    missing_cell_count: int
    missing_cell_pct: float
    complete_row_count: int
    complete_row_pct: float
    numeric_column_count: int
    categorical_column_count: int
    date_column_count: int
    text_column_count: int
    boolean_column_count: int
    high_missing_columns: List[Dict[str, Any]] = field(default_factory=list)
    constant_columns: List[Dict[str, Any]] = field(default_factory=list)
    all_null_columns: List[str] = field(default_factory=list)
    memory_usage_str: str = ""
    column_types: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "total_cells": self.total_cells,
            "duplicate_row_count": self.duplicate_row_count,
            "duplicate_row_pct": self.duplicate_row_pct,
            "missing_cell_count": self.missing_cell_count,
            "missing_cell_pct": self.missing_cell_pct,
            "complete_row_count": self.complete_row_count,
            "complete_row_pct": self.complete_row_pct,
            "numeric_column_count": self.numeric_column_count,
            "categorical_column_count": self.categorical_column_count,
            "date_column_count": self.date_column_count,
            "text_column_count": self.text_column_count,
            "boolean_column_count": self.boolean_column_count,
            "high_missing_columns": self.high_missing_columns,
            "constant_columns": self.constant_columns,
            "all_null_columns": self.all_null_columns,
            "memory_usage_str": self.memory_usage_str,
            "column_types": self.column_types,
        }


def format_memory_size(bytes_size: int) -> str:
    """Format memory bytes into human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def profile_dataset(df: pd.DataFrame, high_missing_threshold_pct: float = 30.0) -> DatasetProfile:
    """
    Generate an exhaustive profile of the uploaded dataset.
    Does NOT alter, clean, or truncate the DataFrame.
    """
    row_count = len(df)
    col_count = len(df.columns)
    total_cells = row_count * col_count

    if row_count == 0 or col_count == 0:
        return DatasetProfile(
            row_count=row_count,
            column_count=col_count,
            total_cells=total_cells,
            duplicate_row_count=0,
            duplicate_row_pct=0.0,
            missing_cell_count=0,
            missing_cell_pct=0.0,
            complete_row_count=0,
            complete_row_pct=0.0,
            numeric_column_count=0,
            categorical_column_count=0,
            date_column_count=0,
            text_column_count=0,
            boolean_column_count=0,
            memory_usage_str="0 B",
        )

    # Missing counts
    missing_cells = int(df.isna().sum().sum())
    missing_pct = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / row_count) * 100, 2) if row_count > 0 else 0.0

    # Complete rows (no NaNs)
    complete_rows = int(df.dropna().shape[0])
    complete_pct = round((complete_rows / row_count) * 100, 2) if row_count > 0 else 0.0

    # Memory usage
    mem_bytes = int(df.memory_usage(deep=True).sum())
    mem_str = format_memory_size(mem_bytes)

    # Column type classifications
    type_map = detect_all_column_types(df)

    num_cols = sum(1 for t in type_map.values() if t == ColumnType.NUMERIC)
    cat_cols = sum(1 for t in type_map.values() if t == ColumnType.CATEGORICAL)
    date_cols = sum(1 for t in type_map.values() if t == ColumnType.DATE)
    text_cols = sum(1 for t in type_map.values() if t == ColumnType.TEXT)
    bool_cols = sum(1 for t in type_map.values() if t == ColumnType.BOOLEAN)

    # Data quality flags
    high_missing = []
    constant_cols = []
    all_null_cols = []

    for col in df.columns:
        series = df[col]
        n_missing = int(series.isna().sum())
        col_missing_pct = round((n_missing / row_count) * 100, 2)

        if n_missing == row_count:
            all_null_cols.append(str(col))
        elif col_missing_pct >= high_missing_threshold_pct:
            high_missing.append({
                "column": str(col),
                "missing_count": n_missing,
                "missing_pct": col_missing_pct,
                "type": type_map.get(col, ColumnType.TEXT),
            })

        # Check for constant non-null values
        unique_count = series.dropna().nunique()
        if unique_count == 1:
            constant_cols.append({
                "column": str(col),
                "constant_value": str(series.dropna().iloc[0]),
                "type": type_map.get(col, ColumnType.TEXT),
            })

    return DatasetProfile(
        row_count=row_count,
        column_count=col_count,
        total_cells=total_cells,
        duplicate_row_count=duplicate_rows,
        duplicate_row_pct=duplicate_pct,
        missing_cell_count=missing_cells,
        missing_cell_pct=missing_pct,
        complete_row_count=complete_rows,
        complete_row_pct=complete_pct,
        numeric_column_count=num_cols,
        categorical_column_count=cat_cols,
        date_column_count=date_cols,
        text_column_count=text_cols,
        boolean_column_count=bool_cols,
        high_missing_columns=high_missing,
        constant_columns=constant_cols,
        all_null_columns=all_null_cols,
        memory_usage_str=mem_str,
        column_types=type_map,
    )
