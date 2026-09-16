"""
Unit Tests for Phase 7: Universal Analytics
===========================================
Validates arbitrary tabular ingestion, file validation, dynamic type detection,
data quality profiling, safe non-destructive cleaning, generic statistical analysis,
visualization generation, cleaned CSV export, and retail dataset protection.

Includes benchmark verification against the 8-row Student test dataset:
- Rows = 8, Columns = 5
- Numeric Columns = 2 (Age, Marks)
- Categorical Columns = 2 (Department, City)
- Text Columns = 1 (Student)
"""

import io
import unittest
import pandas as pd
import numpy as np

from python_app.data.loader import load_all_retail_data
from python_app.analytics.retail_analytics import calculate_retail_kpis
from python_app.universal.loader import (
    load_uploaded_dataset,
    load_dataset_from_bytes,
    validate_file_extension,
)
from python_app.universal.type_detector import (
    detect_column_type,
    detect_all_column_types,
    build_dataset_structure_table,
    is_boolean_series,
    is_date_series,
    is_numeric_series,
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
    create_categorical_bar_chart,
    create_numeric_distribution_chart,
    create_scatter_plot,
    create_aggregated_bar_chart,
    create_time_series_chart,
    create_correlation_heatmap,
    is_likely_id_column,
)


STUDENT_TEST_CSV = """Student,Age,Marks,Department,City
Aman,21,85,Computer Science,Delhi
Riya,22,91,Commerce,Mumbai
Rahul,20,72,Computer Science,Delhi
Priya,21,88,Arts,Jaipur
Neha,23,95,Commerce,Mumbai
Karan,22,67,Arts,Pune
Simran,20,79,Computer Science,Jaipur
Vikas,24,90,Commerce,Delhi"""


class TestPhase7UniversalAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load baseline retail data to ensure complete isolation
        cls.retail_bundle = load_all_retail_data()
        cls.retail_baseline_kpis = calculate_retail_kpis(cls.retail_bundle)

    def test_student_test_dataset_benchmark(self):
        """
        Verify the required benchmark student test dataset:
        8 rows, 5 columns, 2 numeric (Age, Marks), 2 categorical (Department, City), 1 text (Student).
        """
        df, err = load_dataset_from_bytes(STUDENT_TEST_CSV.encode("utf-8"), "student.csv")
        self.assertIsNone(err)
        self.assertIsNotNone(df)

        # 1. Structural dimensions
        self.assertEqual(len(df), 8)
        self.assertEqual(len(df.columns), 5)
        self.assertListEqual(list(df.columns), ["Student", "Age", "Marks", "Department", "City"])

        # 2. Type detection
        type_map = detect_all_column_types(df)

        self.assertEqual(type_map["Student"], ColumnType.TEXT)
        self.assertEqual(type_map["Age"], ColumnType.NUMERIC)
        self.assertEqual(type_map["Marks"], ColumnType.NUMERIC)
        self.assertEqual(type_map["Department"], ColumnType.CATEGORICAL)
        self.assertEqual(type_map["City"], ColumnType.CATEGORICAL)

        # Total counts by type
        num_count = sum(1 for t in type_map.values() if t == ColumnType.NUMERIC)
        cat_count = sum(1 for t in type_map.values() if t == ColumnType.CATEGORICAL)
        text_count = sum(1 for t in type_map.values() if t == ColumnType.TEXT)

        self.assertEqual(num_count, 2)
        self.assertEqual(cat_count, 2)
        self.assertEqual(text_count, 1)

    def test_csv_loading_variations(self):
        """Verify CSV loading with commas, tabs, semicolons, and utf-8 encodings."""
        # Standard CSV
        df1, err1 = load_dataset_from_bytes(b"colA,colB\n1,val1\n2,val2", "test.csv")
        self.assertIsNone(err1)
        self.assertEqual(len(df1), 2)

        # Semicolon CSV
        df2, err2 = load_dataset_from_bytes(b"colA;colB\n10;val10\n20;val20", "test.csv")
        self.assertIsNone(err2)
        self.assertEqual(len(df2), 2)
        self.assertIn("colA", df2.columns)

    def test_xlsx_loading(self):
        """Verify XLSX loading using openpyxl engine."""
        # Create in-memory excel workbook
        buffer = io.BytesIO()
        test_df = pd.DataFrame({
            "Item": ["Alpha", "Beta", "Gamma"],
            "Price": [10.5, 20.0, 15.75],
            "Active": [True, False, True]
        })
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            test_df.to_excel(writer, index=False, sheet_name="Sheet1")

        excel_bytes = buffer.getvalue()
        df, err = load_dataset_from_bytes(excel_bytes, "sample.xlsx")

        self.assertIsNone(err)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ["Item", "Price", "Active"])

    def test_invalid_file_handling(self):
        """Verify graceful error reporting for unsupported, corrupt, or empty inputs."""
        # Unsupported extension
        df_bad_ext, err_bad_ext = load_dataset_from_bytes(b"test data", "image.png")
        self.assertIsNone(df_bad_ext)
        self.assertIn("Unsupported file extension", err_bad_ext)

        # Empty file (0 bytes)
        df_empty, err_empty = load_dataset_from_bytes(b"", "empty.csv")
        self.assertIsNone(df_empty)
        self.assertIn("empty", err_empty.lower())

        # Corrupt Excel file
        df_corrupt, err_corrupt = load_dataset_from_bytes(b"PK\x03\x04not-a-valid-zip-or-excel", "corrupt.xlsx")
        self.assertIsNone(df_corrupt)
        self.assertTrue("excel" in err_corrupt.lower() or "corrupt" in err_corrupt.lower())

        # CSV with only whitespace
        df_blank, err_blank = load_dataset_from_bytes(b"   \n  \n  ", "blank.csv")
        self.assertIsNone(df_blank)

    def test_column_type_detector_subtypes(self):
        """Verify detailed subtype classifications (Date, Boolean, Numeric, Categorical, Text)."""
        test_data = pd.DataFrame({
            "numeric_int": [1, 2, 3, 4, 5],
            "numeric_float": [1.5, 2.5, 3.5, 4.5, 5.5],
            "numeric_string": ["$10.00", "$20.50", "$30.00", "$40.00", "$50.00"],
            "date_col": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "bool_col": [True, False, True, True, False],
            "bool_string": ["yes", "no", "yes", "no", "yes"],
            "cat_col": ["North", "South", "North", "South", "North"],
            "id_col": ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004", "ORD-1005"],
        })

        self.assertEqual(detect_column_type(test_data["numeric_int"]), ColumnType.NUMERIC)
        self.assertEqual(detect_column_type(test_data["numeric_float"]), ColumnType.NUMERIC)
        self.assertEqual(detect_column_type(test_data["numeric_string"]), ColumnType.NUMERIC)
        self.assertEqual(detect_column_type(test_data["date_col"]), ColumnType.DATE)
        self.assertEqual(detect_column_type(test_data["bool_col"]), ColumnType.BOOLEAN)
        self.assertEqual(detect_column_type(test_data["bool_string"]), ColumnType.BOOLEAN)
        self.assertEqual(detect_column_type(test_data["cat_col"]), ColumnType.CATEGORICAL)
        # ID column should NOT be detected as date
        self.assertNotEqual(detect_column_type(test_data["id_col"]), ColumnType.DATE)
        self.assertEqual(detect_column_type(test_data["id_col"]), ColumnType.TEXT)

    def test_dataset_structure_table(self):
        """Verify building of structure table."""
        df = pd.DataFrame({
            "A": [1, 2, None, 4],
            "B": ["cat", "dog", "cat", "dog"],
        })
        table = build_dataset_structure_table(df)

        self.assertEqual(len(table), 2)
        row_a = table[table["Column"] == "A"].iloc[0]
        self.assertEqual(row_a["Non-null Count"], 3)
        self.assertEqual(row_a["Missing Count"], 1)
        self.assertEqual(row_a["Missing %"], 25.0)

    def test_dataset_profiling_and_quality(self):
        """Verify volumetric and quality metrics in DatasetProfile."""
        df = pd.DataFrame({
            "val": [10, 20, 30, None, 50],
            "group": ["A", "B", "C", "D", "E"],
            "all_nan": [None, None, None, None, None],
            "constant": [1, 1, 1, 1, 1],
        })
        # Add a single duplicate row
        df = pd.concat([df, df.iloc[[1]]], ignore_index=True)

        profile = profile_dataset(df)

        self.assertEqual(profile.row_count, 6)
        self.assertEqual(profile.column_count, 4)
        self.assertEqual(profile.duplicate_row_count, 1)
        self.assertGreater(profile.missing_cell_count, 0)
        self.assertIn("all_nan", profile.all_null_columns)
        self.assertTrue(any(c["column"] == "constant" for c in profile.constant_columns))

    def test_safe_data_cleaning(self):
        """Verify non-destructive cleaning: trims whitespace, removes duplicates, drops empty rows, imputer."""
        raw_df = pd.DataFrame({
            " Name ": [" Alice ", " Bob ", " Bob ", " Charlie ", None],
            "Score": [90.0, None, None, 70.0, None],
            "Dept": ["HR", None, None, "HR", None],
        })
        # Last row is completely empty

        cleaned, summary = clean_dataset(raw_df)

        # Trims column names
        self.assertIn("Name", cleaned.columns)
        self.assertNotIn(" Name ", cleaned.columns)

        # Drops completely empty row
        self.assertEqual(summary.empty_rows_removed, 1)

        # Drops duplicate row
        self.assertEqual(summary.duplicates_removed, 1)

        # Imputes numeric median (90 and 70 median is 80)
        self.assertIn("Score", summary.numeric_imputed_columns)
        bob_score = cleaned[cleaned["Name"] == "Bob"]["Score"].iloc[0]
        self.assertEqual(bob_score, 80.0)

        # Imputes categorical with 'Unknown'
        self.assertIn("Dept", summary.categorical_imputed_columns)
        bob_dept = cleaned[cleaned["Name"] == "Bob"]["Dept"].iloc[0]
        self.assertEqual(bob_dept, "Unknown")

        # Verify original raw_df is UNTOUCHED
        self.assertEqual(len(raw_df), 5)
        self.assertIn(" Name ", raw_df.columns)

    def test_generic_statistical_analysis(self):
        """Verify statistical metrics on numeric, categorical, date, and text columns."""
        df = pd.DataFrame({
            "score": [10.0, 20.0, 30.0, 40.0, 50.0],
            "category": ["A", "A", "A", "B", "B"],
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
            "notes": ["short", "a longer note here", "note 3", "another text string", "final"],
        })

        # Numeric stats
        num_stats = calculate_numeric_statistics(df, ["score"])
        self.assertEqual(len(num_stats), 1)
        self.assertEqual(num_stats.iloc[0]["Mean"], 30.0)
        self.assertEqual(num_stats.iloc[0]["Median"], 30.0)
        self.assertEqual(num_stats.iloc[0]["Min"], 10.0)
        self.assertEqual(num_stats.iloc[0]["Max"], 50.0)

        # Categorical stats
        cat_stats = calculate_categorical_statistics(df, ["category"])
        self.assertEqual(len(cat_stats), 1)
        self.assertEqual(cat_stats.iloc[0]["Top Value"], "A")
        self.assertEqual(cat_stats.iloc[0]["Top Frequency"], 3)
        self.assertEqual(cat_stats.iloc[0]["Top Share %"], 60.0)

        # Date stats
        date_stats = calculate_date_statistics(df, ["timestamp"])
        self.assertEqual(len(date_stats), 1)
        self.assertEqual(date_stats.iloc[0]["Earliest Date"], "2024-01-01")
        self.assertEqual(date_stats.iloc[0]["Latest Date"], "2024-01-05")
        self.assertEqual(date_stats.iloc[0]["Date Span (Days)"], 4)

        # Text stats
        text_stats = calculate_text_statistics(df, ["notes"])
        self.assertEqual(len(text_stats), 1)
        self.assertEqual(text_stats.iloc[0]["Non-null Count"], 5)
        self.assertGreater(text_stats.iloc[0]["Avg Text Length"], 0)

        # Correlation
        df["score2"] = df["score"] * 2
        corr = calculate_correlation_matrix(df, ["score", "score2"])
        self.assertIsNotNone(corr)
        self.assertAlmostEqual(corr.loc["score", "score2"], 1.0, delta=0.01)

    def test_visual_analytics_generation(self):
        """Verify Plotly chart generation for categorical, numeric, scatter, and time series."""
        df = pd.DataFrame({
            "Cat": ["Red", "Blue", "Green", "Red", "Blue"],
            "Val1": [10, 20, 30, 40, 50],
            "Val2": [100, 200, 300, 400, 500],
            "Date": pd.date_range("2024-01-01", periods=5),
        })

        fig_bar = create_categorical_bar_chart(df, "Cat")
        self.assertIsNotNone(fig_bar)

        fig_hist = create_numeric_distribution_chart(df, "Val1")
        self.assertIsNotNone(fig_hist)

        fig_scatter = create_scatter_plot(df, "Val1", "Val2", "Cat")
        self.assertIsNotNone(fig_scatter)

        fig_agg = create_aggregated_bar_chart(df, "Cat", "Val1", "mean")
        self.assertIsNotNone(fig_agg)

        fig_ts = create_time_series_chart(df, "Date", "Val1")
        self.assertIsNotNone(fig_ts)

        corr = calculate_correlation_matrix(df, ["Val1", "Val2"])
        fig_corr = create_correlation_heatmap(corr)
        self.assertIsNotNone(fig_corr)

    def test_id_column_detection(self):
        """Verify identification of surrogate IDs to avoid plotting them as metrics."""
        s_id = pd.Series([1, 2, 3, 4, 5, 6])
        self.assertTrue(is_likely_id_column("row_id", s_id))
        self.assertTrue(is_likely_id_column("order_id", s_id))
        self.assertTrue(is_likely_id_column("id", s_id))
        self.assertTrue(is_likely_id_column("index", s_id))

        s_metric = pd.Series([100.5, 45.2, 98.7, 120.0])
        self.assertFalse(is_likely_id_column("revenue", s_metric))
        self.assertFalse(is_likely_id_column("sales", s_metric))
        self.assertFalse(is_likely_id_column("score", s_metric))

    def test_retail_data_isolation_and_integrity(self):
        """
        CRITICAL TEST: Ensure uploading and processing universal datasets DOES NOT
        modify, overwrite, or mutate the underlying retail datasets or KPIs.
        """
        # Load and clean student test dataset
        df, _ = load_dataset_from_bytes(STUDENT_TEST_CSV.encode("utf-8"), "student.csv")
        cleaned, _ = clean_dataset(df)

        # Re-check baseline retail bundle KPIs
        retail_kpis_now = calculate_retail_kpis(self.retail_bundle)

        self.assertAlmostEqual(retail_kpis_now["total_sales"], 2261536.97, delta=0.5)
        self.assertEqual(retail_kpis_now["total_orders"], 4922)
        self.assertAlmostEqual(retail_kpis_now["aov"], 459.48, delta=0.5)
        self.assertAlmostEqual(retail_kpis_now["sales_yoy"], 20.30, delta=0.2)
        self.assertAlmostEqual(retail_kpis_now["return_rate"], 9.96, delta=0.1)
        self.assertAlmostEqual(retail_kpis_now["average_delivery_days"], 4.11, delta=0.1)
        self.assertEqual(retail_kpis_now["low_stock_items"], 34)

        # Baseline bundle record counts
        self.assertEqual(len(self.retail_bundle.orders), 9800)
        self.assertEqual(self.retail_bundle.orders["order_id"].nunique(), 4922)
        self.assertEqual(len(self.retail_bundle.customers), 793)
        self.assertEqual(len(self.retail_bundle.products), 1861)
        self.assertEqual(len(self.retail_bundle.inventory), 1861)
        self.assertEqual(len(self.retail_bundle.transportation), 9800)
        self.assertEqual(len(self.retail_bundle.returns), 490)


if __name__ == "__main__":
    unittest.main()
