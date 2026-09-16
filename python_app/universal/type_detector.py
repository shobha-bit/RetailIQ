"""
Universal Column Type Detector
==============================
Dynamically identifies and classifies tabular columns into:
- Numeric
- Date
- Boolean
- Categorical
- Text

Operates on observed values and statistical distributions rather than column names alone.
Protects against false positives (e.g. arbitrary identifiers or numeric codes mistyped as dates).
"""

import re
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class ColumnType:
    NUMERIC = "Numeric"
    DATE = "Date"
    BOOLEAN = "Boolean"
    CATEGORICAL = "Categorical"
    TEXT = "Text"


# Common date patterns (requiring standard date separators)
DATE_PATTERN_REGEX = re.compile(
    r"^\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})"
    r"(\s+\d{1,2}:\d{2}(:\d{2})?(\s*(AM|PM|am|pm))?)?\s*$"
)

# Common boolean string representations
BOOLEAN_STRINGS = {"true", "false", "yes", "no", "t", "f", "1", "0", "y", "n"}


def is_boolean_series(series: pd.Series) -> bool:
    """Check if a series behaves as a boolean column."""
    if pd.api.types.is_bool_dtype(series):
        return True

    non_null = series.dropna()
    if len(non_null) == 0:
        return False

    # Check unique values
    unique_vals = set(non_null.unique())

    # Direct python booleans
    if unique_vals.issubset({True, False}):
        return True

    # Check 0 and 1 integer values only if clearly binary
    if unique_vals.issubset({0, 1}) and len(unique_vals) <= 2:
        # Check if the name or context suggests boolean or small binary flag
        return True

    # Check string representations
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        str_vals = {str(v).strip().lower() for v in unique_vals}
        if str_vals.issubset(BOOLEAN_STRINGS) and len(str_vals) <= 2:
            return True

    return False


def is_date_series(series: pd.Series) -> bool:
    """
    Check if a series represents dates/timestamps.
    Safely rejects pure numbers, postal codes, and alphanumeric IDs (e.g., 'ORD-101').
    """
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    non_null = series.dropna()
    if len(non_null) == 0:
        return False

    # Never classify pure numeric dtypes as dates automatically
    if pd.api.types.is_numeric_dtype(series):
        return False

    sample = non_null.head(50).astype(str).str.strip()

    # Reject if values are plain digits (e.g., '12345' or '2024') or simple IDs
    matches_date_pattern = 0
    for val in sample:
        if not val or val.isdigit() or len(val) < 6:
            continue
        # Check for typical date separators
        if any(sep in val for sep in ["-", "/", "."]) and DATE_PATTERN_REGEX.match(val):
            matches_date_pattern += 1

    pattern_ratio = matches_date_pattern / len(sample)
    if pattern_ratio < 0.7:
        return False

    # Verify pd.to_datetime can parse without throwing errors
    try:
        parsed = pd.to_datetime(sample, errors="coerce")
        valid_ratio = parsed.notna().sum() / len(sample)
        if valid_ratio >= 0.8:
            # Check year plausibility (between 1900 and 2100)
            years = parsed.dropna().dt.year
            if ((years >= 1900) & (years <= 2100)).all():
                return True
    except Exception:
        return False

    return False


def is_numeric_series(series: pd.Series) -> bool:
    """Check if a series is numeric or cleanly coercible to numbers."""
    if is_boolean_series(series):
        return False

    if pd.api.types.is_numeric_dtype(series):
        return True

    non_null = series.dropna()
    if len(non_null) == 0:
        return False

    # If it's an object, check if strings are formatted numbers (e.g., '$1,200.50' or '95%')
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        sample = non_null.head(50).astype(str).str.strip()
        # Clean currency and percentage symbols
        cleaned = sample.str.replace(r"[$,%\s]", "", regex=True)
        # Check if values are numeric
        numeric_count = 0
        for val in cleaned:
            if not val:
                continue
            try:
                float(val)
                numeric_count += 1
            except ValueError:
                pass
        if numeric_count / len(sample) >= 0.9:
            return True

    return False


def detect_column_type(series: pd.Series) -> str:
    """
    Detect the operational analytical type of a single pandas Series.
    Returns one of: 'Numeric', 'Date', 'Boolean', 'Categorical', 'Text'.
    """
    if series.empty or series.dropna().empty:
        return ColumnType.TEXT

    # 1. Boolean check
    if is_boolean_series(series):
        return ColumnType.BOOLEAN

    # 2. Date check
    if is_date_series(series):
        return ColumnType.DATE

    # 3. Numeric check
    if is_numeric_series(series):
        return ColumnType.NUMERIC

    # 4. Distinguish Categorical vs Text
    non_null = series.dropna()
    total_count = len(non_null)
    unique_count = non_null.nunique()

    # Average string length
    str_series = non_null.astype(str)
    avg_len = str_series.str.len().mean()

    # If average length is long, treat as text
    if avg_len > 40:
        return ColumnType.TEXT

    # If 100% unique and dataset has 5+ rows, treat as unique identifier / text
    if total_count >= 5 and unique_count == total_count:
        return ColumnType.TEXT

    # Low unique cardinality relative to total count
    if unique_count <= 20 and unique_count < total_count:
        return ColumnType.CATEGORICAL

    if (unique_count / total_count <= 0.35) and unique_count <= 100:
        return ColumnType.CATEGORICAL

    return ColumnType.TEXT


def detect_all_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect types for all columns in a DataFrame."""
    return {col: detect_column_type(df[col]) for col in df.columns}


def build_dataset_structure_table(df: pd.DataFrame, type_map: Dict[str, str] = None) -> pd.DataFrame:
    """
    Builds the Dataset Structure summary table:
    - Column
    - Detected Type
    - Non-null Count
    - Missing Count
    - Missing %
    - Unique Values
    """
    if type_map is None:
        type_map = detect_all_column_types(df)

    total_rows = len(df)
    records = []

    for col in df.columns:
        series = df[col]
        non_null = int(series.notna().sum())
        missing = int(series.isna().sum())
        missing_pct = round((missing / total_rows) * 100, 2) if total_rows > 0 else 0.0
        unique_vals = int(series.nunique())

        records.append({
            "Column": str(col),
            "Detected Type": type_map.get(col, ColumnType.TEXT),
            "Non-null Count": non_null,
            "Missing Count": missing,
            "Missing %": missing_pct,
            "Unique Values": unique_vals,
        })

    return pd.DataFrame(records)
