"""
Universal Dataset Loader & Validator
====================================
Safely loads and validates arbitrary CSV and XLSX/Excel datasets.
Handles varied encodings, corrupt archives, malformed rows, and empty structures gracefully.
Protects internal filesystem paths and infrastructure secrets from exposure.
"""

import io
import os
from typing import Tuple, Optional, Union
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """Check if the provided filename has an authorized tabular extension."""
    if not filename:
        return False, "No filename provided."

    _, ext = os.path.splitext(filename.lower())
    if ext in SUPPORTED_EXTENSIONS:
        return True, ""
    return False, f"Unsupported file extension '{ext}'. Please upload a CSV (.csv) or Excel (.xlsx, .xls) file."


def load_dataset_from_bytes(
    file_bytes: bytes,
    filename: str,
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load a tabular dataset directly from in-memory bytes.
    Validates structure, encodings, and headers.
    """
    if not file_bytes or len(file_bytes) == 0:
        return None, "The uploaded file is empty (0 bytes)."

    is_valid, ext_err = validate_file_extension(filename)
    if not is_valid:
        return None, ext_err

    _, ext = os.path.splitext(filename.lower())

    # Process Excel
    if ext in {".xlsx", ".xls"}:
        try:
            excel_buffer = io.BytesIO(file_bytes)
            # Read first available sheet
            df = pd.read_excel(excel_buffer, sheet_name=0, engine="openpyxl" if ext == ".xlsx" else None)
        except Exception as e:
            err_str = str(e).lower()
            if "bad zip" in err_str or "corrupt" in err_str:
                return None, "Corrupted or invalid Excel file. Please ensure the file is an uncorrupted .xlsx or .xls document."
            return None, f"Failed to parse Excel workbook: {str(e)[:120]}"

    # Process CSV
    else:
        encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        df = None
        last_error = None

        for enc in encodings_to_try:
            try:
                csv_buffer = io.StringIO(file_bytes.decode(enc))
                # Attempt standard read with python parser fallback for malformed delimiters
                df = pd.read_csv(csv_buffer, sep=None, engine="python")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
            except pd.errors.EmptyDataError:
                return None, "The CSV file contains no tabular data or columns."
            except Exception as e:
                last_error = e

        if df is None:
            if last_error is not None:
                return None, f"Malformed CSV file could not be parsed: {str(last_error)[:120]}"
            return None, "Unable to decode CSV file using supported character encodings (UTF-8, Latin-1, CP1252)."

    # Structural validation
    if df.empty or len(df) == 0:
        return None, "The loaded dataset contains 0 rows."

    if len(df.columns) == 0:
        return None, "The loaded dataset has no columns."

    # Check if columns are all unnamed or empty
    usable_cols = [c for c in df.columns if str(c).strip() and not str(c).startswith("Unnamed:")]
    if len(usable_cols) == 0 and df.dropna(how="all").empty:
        return None, "The loaded dataset has no usable columns or valid data rows."

    # Clean initial column names (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]

    return df, None


def load_uploaded_dataset(
    file_or_path: Union[str, io.BytesIO, io.StringIO, any],
    filename: Optional[str] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    High-level loader accepting a file path, Streamlit UploadedFile, or file-like buffer.
    """
    if file_or_path is None:
        return None, "No file provided."

    # 1. Streamlit UploadedFile or file-like object
    if hasattr(file_or_path, "read"):
        actual_name = filename or getattr(file_or_path, "name", "uploaded_dataset.csv")
        try:
            content_bytes = file_or_path.read()
            # Reset seek position if seekable
            if hasattr(file_or_path, "seek"):
                file_or_path.seek(0)
            return load_dataset_from_bytes(content_bytes, actual_name)
        except Exception as e:
            return None, f"Error reading uploaded file: {str(e)[:120]}"

    # 2. Local filesystem path (string)
    if isinstance(file_or_path, str):
        if not os.path.exists(file_or_path):
            return None, "Specified dataset file does not exist."
        actual_name = filename or os.path.basename(file_or_path)
        try:
            with open(file_or_path, "rb") as f:
                content_bytes = f.read()
            return load_dataset_from_bytes(content_bytes, actual_name)
        except Exception as e:
            return None, f"Error reading dataset file: {str(e)[:120]}"

    # 3. Raw bytes
    if isinstance(file_or_path, bytes):
        actual_name = filename or "dataset.csv"
        return load_dataset_from_bytes(file_or_path, actual_name)

    return None, "Unsupported file input type."
