"""
Universal Analytics Engine
===========================
Generic tabular dataset ingestion, schema inference, data quality profiling,
automated cleaning, statistical aggregation, and dynamic visual analytics.
"""

from python_app.universal.loader import load_uploaded_dataset, load_dataset_from_bytes, validate_file_extension
from python_app.universal.type_detector import (
    detect_column_type,
    detect_all_column_types,
    build_dataset_structure_table,
    ColumnType,
)
from python_app.universal.profiler import profile_dataset, DatasetProfile
from python_app.universal.cleaner import clean_dataset, CleaningSummary
from python_app.universal.analyzer import (
    calculate_numeric_statistics,
    calculate_categorical_statistics,
    calculate_date_statistics,
    calculate_text_statistics,
    calculate_correlation_matrix,
    generate_visual_analytics_data,
)

__all__ = [
    "load_uploaded_dataset",
    "load_dataset_from_bytes",
    "validate_file_extension",
    "detect_column_type",
    "detect_all_column_types",
    "build_dataset_structure_table",
    "ColumnType",
    "profile_dataset",
    "DatasetProfile",
    "clean_dataset",
    "CleaningSummary",
    "calculate_numeric_statistics",
    "calculate_categorical_statistics",
    "calculate_date_statistics",
    "calculate_text_statistics",
    "calculate_correlation_matrix",
    "generate_visual_analytics_data",
]
