"""
Universal Dataset Cleaner
=========================
Performs safe, non-destructive automated data cleaning:
- Strips leading/trailing whitespace from column names and string fields
- Removes completely empty rows
- Removes duplicate rows
- Imputes missing numeric values using column median
- Fills missing categorical and text values with 'Unknown'
- Preserves dates without fabricating synthetic timestamps
- Retains original DataFrame in isolation; returns a fresh cleaned copy and audit log
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

from python_app.universal.type_detector import detect_all_column_types, ColumnType


@dataclass
class CleaningSummary:
    original_rows: int
    cleaned_rows: int
    original_columns: int
    cleaned_columns: int
    duplicates_removed: int
    empty_rows_removed: int
    missing_values_before: int
    missing_values_after: int
    numeric_imputed_columns: List[str] = field(default_factory=list)
    categorical_imputed_columns: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_rows": self.original_rows,
            "cleaned_rows": self.cleaned_rows,
            "original_columns": self.original_columns,
            "cleaned_columns": self.cleaned_columns,
            "duplicates_removed": self.duplicates_removed,
            "empty_rows_removed": self.empty_rows_removed,
            "missing_values_before": self.missing_values_before,
            "missing_values_after": self.missing_values_after,
            "numeric_imputed_columns": self.numeric_imputed_columns,
            "categorical_imputed_columns": self.categorical_imputed_columns,
            "actions_taken": self.actions_taken,
        }


def clean_dataset(
    df: pd.DataFrame,
    type_map: Optional[Dict[str, str]] = None,
    impute_numeric_median: bool = True,
    fill_categorical_unknown: bool = True,
    drop_duplicates: bool = True,
    drop_empty_rows: bool = True,
) -> Tuple[pd.DataFrame, CleaningSummary]:
    """
    Safely clean a generic DataFrame without modifying the input in-place.
    Produces a new DataFrame and a detailed CleaningSummary audit object.
    """
    if df.empty:
        return df.copy(), CleaningSummary(
            original_rows=0,
            cleaned_rows=0,
            original_columns=0,
            cleaned_columns=0,
            duplicates_removed=0,
            empty_rows_removed=0,
            missing_values_before=0,
            missing_values_after=0,
        )

    # Work on an isolated copy
    cleaned = df.copy(deep=True)
    orig_rows = len(cleaned)
    orig_cols = len(cleaned.columns)
    missing_before = int(cleaned.isna().sum().sum())
    actions = []

    # 1. Clean column headers: strip whitespace
    cleaned.columns = [str(c).strip() for c in cleaned.columns]
    actions.append("Normalized column headers by trimming whitespace.")

    # 2. Remove completely empty rows
    empty_rows_removed = 0
    if drop_empty_rows:
        initial_count = len(cleaned)
        cleaned = cleaned.dropna(how="all").reset_index(drop=True)
        empty_rows_removed = initial_count - len(cleaned)
        if empty_rows_removed > 0:
            actions.append(f"Removed {empty_rows_removed} completely empty rows.")

    # 3. Remove duplicate rows
    duplicates_removed = 0
    if drop_duplicates:
        initial_count = len(cleaned)
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        duplicates_removed = initial_count - len(cleaned)
        if duplicates_removed > 0:
            actions.append(f"Removed {duplicates_removed} duplicate rows.")

    # Re-infer or utilize provided type map
    if type_map is None:
        type_map = detect_all_column_types(cleaned)

    # 4. Clean string fields (strip leading/trailing spaces in object/string columns)
    for col in cleaned.columns:
        if pd.api.types.is_object_dtype(cleaned[col]) or pd.api.types.is_string_dtype(cleaned[col]):
            # Clean string values
            cleaned[col] = cleaned[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )

    numeric_imputed = []
    categorical_imputed = []

    # 5. Handle missing values
    for col in cleaned.columns:
        col_type = type_map.get(col, ColumnType.TEXT)
        series = cleaned[col]
        missing_count = int(series.isna().sum())

        if missing_count == 0:
            continue

        # Numeric columns -> Median imputation
        if col_type == ColumnType.NUMERIC and impute_numeric_median:
            # Convert series to numeric if needed
            numeric_vals = pd.to_numeric(
                series.astype(str).str.replace(r"[$,%\s]", "", regex=True),
                errors="coerce"
            )
            median_val = numeric_vals.dropna().median()
            if pd.notna(median_val):
                # If original was integer-like without decimals, keep rounded
                if (numeric_vals.dropna() % 1 == 0).all():
                    fill_val = int(round(median_val))
                else:
                    fill_val = round(float(median_val), 2)
                cleaned[col] = numeric_vals.fillna(fill_val)
                numeric_imputed.append(str(col))
                actions.append(f"Imputed {missing_count} missing values in numeric column '{col}' with median ({fill_val}).")

        # Categorical / Text columns -> "Unknown"
        elif col_type in {ColumnType.CATEGORICAL, ColumnType.TEXT} and fill_categorical_unknown:
            cleaned[col] = series.fillna("Unknown")
            categorical_imputed.append(str(col))
            actions.append(f"Replaced {missing_count} missing values in categorical column '{col}' with 'Unknown'.")

        # Boolean columns -> False fallback
        elif col_type == ColumnType.BOOLEAN:
            cleaned[col] = series.fillna(False)
            actions.append(f"Filled {missing_count} missing boolean flags in '{col}' with False.")

        # Date columns: leave as NaT or preserve (do NOT invent arbitrary dates)
        elif col_type == ColumnType.DATE:
            actions.append(f"Preserved {missing_count} missing date timestamps in '{col}' as unrecorded (NaT).")

    missing_after = int(cleaned.isna().sum().sum())

    summary = CleaningSummary(
        original_rows=orig_rows,
        cleaned_rows=len(cleaned),
        original_columns=orig_cols,
        cleaned_columns=len(cleaned.columns),
        duplicates_removed=duplicates_removed,
        empty_rows_removed=empty_rows_removed,
        missing_values_before=missing_before,
        missing_values_after=missing_after,
        numeric_imputed_columns=numeric_imputed,
        categorical_imputed_columns=categorical_imputed,
        actions_taken=actions,
    )

    return cleaned, summary
