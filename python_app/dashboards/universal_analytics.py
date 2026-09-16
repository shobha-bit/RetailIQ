"""
Universal Analytics Dashboard (Streamlit)
=========================================
Generic tabular ingestion, schema detection, automated cleaning, profiling,
statistical breakdown, and dynamic visual analytics.
Works autonomously on arbitrary CSV or Excel datasets without requiring retail-specific schemas.
Protects the underlying retail engine and databases from contamination.
"""

import io
import streamlit as st
import pandas as pd
import numpy as np

from python_app.universal.loader import (
    load_uploaded_dataset,
    load_dataset_from_bytes,
    validate_file_extension,
)
from python_app.universal.type_detector import (
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
    create_categorical_bar_chart,
    create_numeric_distribution_chart,
    create_scatter_plot,
    create_aggregated_bar_chart,
    create_time_series_chart,
    create_correlation_heatmap,
)
from python_app.utils.ui import (
    render_page_header,
    render_kpi_card,
    render_empty_state,
    get_plotly_theme,
)

STUDENT_SAMPLE_CSV = """Student,Age,Marks,Department,City
Aman,21,85,Computer Science,Delhi
Riya,22,91,Commerce,Mumbai
Rahul,20,72,Computer Science,Delhi
Priya,21,88,Arts,Jaipur
Neha,23,95,Commerce,Mumbai
Karan,22,67,Arts,Pune
Simran,20,79,Computer Science,Jaipur
Vikas,24,90,Commerce,Delhi"""


def initialize_universal_session_state():
    """Ensure isolated session state variables exist for Universal Analytics."""
    if "universal_orig_df" not in st.session_state:
        st.session_state["universal_orig_df"] = None
    if "universal_clean_df" not in st.session_state:
        st.session_state["universal_clean_df"] = None
    if "universal_filename" not in st.session_state:
        st.session_state["universal_filename"] = None
    if "universal_profile" not in st.session_state:
        st.session_state["universal_profile"] = None
    if "universal_summary" not in st.session_state:
        st.session_state["universal_summary"] = None
    if "universal_type_map" not in st.session_state:
        st.session_state["universal_type_map"] = None


def process_and_cache_dataset(df: pd.DataFrame, filename: str):
    """Processes, profiles, cleans, and stores a new universal dataset in session state."""
    type_map = detect_all_column_types(df)
    profile = profile_dataset(df)
    cleaned_df, summary = clean_dataset(df, type_map=type_map)

    st.session_state["universal_orig_df"] = df
    st.session_state["universal_clean_df"] = cleaned_df
    st.session_state["universal_filename"] = filename
    st.session_state["universal_profile"] = profile
    st.session_state["universal_summary"] = summary
    st.session_state["universal_type_map"] = type_map


def render_universal_analytics_dashboard(bundle=None):
    """
    Primary rendering entrypoint for Universal Analytics.
    Isolated from the retail bundle to guarantee zero contamination.
    """
    initialize_universal_session_state()

    # 1. Header & Context
    render_page_header(
        title="Universal Analytics Sandbox",
        description="Upload arbitrary CSV or Excel spreadsheets. Autonomously infers column schemas, assesses data quality, performs non-destructive cleaning, and generates visual analytics.",
        badge_label="Universal Analytics",
        secondary_badge="Data Sandbox",
    )

    # 2. Upload Dataset Section
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">1. Ingest & Load Dataset</h3>
                <p class="chart-subtitle">Upload custom CSV/Excel files or initialize with benchmark data</p>
            </div>
            <span class="badge badge-indigo">Data Source</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_col1, upload_col2 = st.columns([3, 1.2])

    with upload_col1:
        uploaded_file = st.file_uploader(
            "Upload any CSV or Excel (.xlsx, .xls) dataset",
            type=["csv", "xlsx", "xls"],
            help="Supported tabular formats: CSV (comma, semicolon, tab, auto-delimited) and Excel workbooks.",
            key="universal_file_uploader",
        )

    with upload_col2:
        st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
        if st.button("Load Student Test Sample", use_container_width=True, help="Load the standard 8-row benchmark test dataset."):
            sample_df, err = load_dataset_from_bytes(STUDENT_SAMPLE_CSV.encode("utf-8"), "student_test_dataset.csv")
            if sample_df is not None:
                process_and_cache_dataset(sample_df, "student_test_dataset.csv")
                st.success("Loaded 'student_test_dataset.csv' successfully.")
                st.rerun()

    # Handle file upload change
    if uploaded_file is not None:
        # Check if it's already the loaded file
        if uploaded_file.name != st.session_state.get("universal_filename"):
            try:
                df, err = load_uploaded_dataset(uploaded_file, uploaded_file.name)
                if err:
                    st.error(f"Upload Error: {err}")
                elif df is not None:
                    process_and_cache_dataset(df, uploaded_file.name)
                    st.success(f"Successfully processed and profiled '{uploaded_file.name}'.")
                    st.rerun()
            except Exception as e:
                st.error("Failed to process the uploaded file. Please ensure it is a valid tabular document.")

    # Guard: Check if a dataset is currently loaded
    orig_df = st.session_state.get("universal_orig_df")
    clean_df = st.session_state.get("universal_clean_df")
    filename = st.session_state.get("universal_filename")
    profile: DatasetProfile = st.session_state.get("universal_profile")
    summary: CleaningSummary = st.session_state.get("universal_summary")
    type_map = st.session_state.get("universal_type_map")

    if orig_df is None or profile is None:
        render_empty_state(
            title="No Tabular Dataset Loaded",
            message="Upload a CSV or Excel spreadsheet above, or click 'Load Student Test Sample' to begin autonomous profiling.",
        )
        return

    # Clear active dataset button
    col_file_info, col_clear = st.columns([4, 1])
    with col_file_info:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 0.6rem 1rem; border-radius: 8px; font-size: 0.85rem; color: #334155; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;">
                <span>📄 <strong>Active Source:</strong> <code>{filename}</code></span> &bull; 
                <span>💾 <strong>Memory:</strong> {profile.memory_usage_str}</span> &bull; 
                <span class="badge badge-success">Validated & Cleaned</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_clear:
        if st.button("Reset Dataset", use_container_width=True):
            st.session_state["universal_orig_df"] = None
            st.session_state["universal_clean_df"] = None
            st.session_state["universal_filename"] = None
            st.session_state["universal_profile"] = None
            st.session_state["universal_summary"] = None
            st.session_state["universal_type_map"] = None
            st.rerun()

    # 3. Dataset Overview
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">2. Volumetric Metrics & Dimensionality</h3>
                <p class="chart-subtitle">Core row/column counts, missingness rates, and memory footprint</p>
            </div>
            <span class="badge badge-neutral">Overview</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ov_c1, ov_c2, ov_c3, ov_c4, ov_c5, ov_c6 = st.columns(6)
    with ov_c1:
        render_kpi_card(
            title="Total Rows",
            value=f"{profile.row_count:,}",
            icon="📄",
            icon_color_class="kpi-icon-indigo",
            subtitle="Record count",
        )
    with ov_c2:
        render_kpi_card(
            title="Total Columns",
            value=f"{profile.column_count}",
            icon="📊",
            icon_color_class="kpi-icon-cyan",
            subtitle="Feature dimensions",
        )
    with ov_c3:
        render_kpi_card(
            title="Duplicate Rows",
            value=f"{profile.duplicate_row_count}",
            delta=f"{profile.duplicate_row_pct}%",
            delta_positive=profile.duplicate_row_count == 0,
            icon="👥",
            icon_color_class="kpi-icon-amber" if profile.duplicate_row_count > 0 else "kpi-icon-emerald",
            subtitle="Redundant records",
        )
    with ov_c4:
        render_kpi_card(
            title="Missing Cells",
            value=f"{profile.missing_cell_count:,}",
            delta=f"{profile.missing_cell_pct}%",
            delta_positive=profile.missing_cell_count == 0,
            icon="❓",
            icon_color_class="kpi-icon-rose" if profile.missing_cell_count > 0 else "kpi-icon-emerald",
            subtitle="Sparsity index",
        )
    with ov_c5:
        render_kpi_card(
            title="Numeric Columns",
            value=f"{profile.numeric_column_count}",
            icon="🔢",
            icon_color_class="kpi-icon-purple",
            subtitle="Quantitative fields",
        )
    with ov_c6:
        render_kpi_card(
            title="Categorical",
            value=f"{profile.categorical_column_count}",
            icon="🏷️",
            icon_color_class="kpi-icon-blue",
            subtitle="Discrete attributes",
        )

    st.markdown(
        f"""
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem; margin-bottom: 1.25rem;">
            <span style="font-size: 0.75rem; background: #F8FAFC; color: #475569; padding: 0.25rem 0.65rem; border-radius: 6px; border: 1px solid #E2E8F0;">
                📅 Date Columns: <strong>{profile.date_column_count}</strong>
            </span>
            <span style="font-size: 0.75rem; background: #F8FAFC; color: #475569; padding: 0.25rem 0.65rem; border-radius: 6px; border: 1px solid #E2E8F0;">
                📝 Text Columns: <strong>{profile.text_column_count}</strong>
            </span>
            <span style="font-size: 0.75rem; background: #F8FAFC; color: #475569; padding: 0.25rem 0.65rem; border-radius: 6px; border: 1px solid #E2E8F0;">
                🔘 Boolean Columns: <strong>{profile.boolean_column_count}</strong>
            </span>
            <span style="font-size: 0.75rem; background: #F8FAFC; color: #475569; padding: 0.25rem 0.65rem; border-radius: 6px; border: 1px solid #E2E8F0;">
                ✅ Complete Rows: <strong>{profile.complete_row_count} ({profile.complete_row_pct}%)</strong>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Data Quality Section
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">3. Data Quality & Integrity Assessor</h3>
                <p class="chart-subtitle">Automated structural health audit detecting anomalies, nulls, and constant columns</p>
            </div>
            <span class="badge badge-indigo">Quality Audit</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    quality_col1, quality_col2 = st.columns(2)

    with quality_col1:
        if profile.duplicate_row_count > 0:
            st.warning(f"Detected {profile.duplicate_row_count} duplicate rows ({profile.duplicate_row_pct}% of records).")
        else:
            st.success("Zero duplicate rows detected across the dataset.")

        if profile.missing_cell_count > 0:
            st.warning(f"Detected {profile.missing_cell_count:,} missing cells ({profile.missing_cell_pct}% total sparsity).")
        else:
            st.success("Dataset is 100% complete with zero missing values.")

    with quality_col2:
        if profile.high_missing_columns:
            st.warning(f"High-Missing Columns (>= 30% NaNs): {', '.join([c['column'] + ' (' + str(c['missing_pct']) + '%)' for c in profile.high_missing_columns])}")
        else:
            st.success("No columns exceed the 30% missing data risk threshold.")

        if profile.constant_columns:
            st.info(f"Constant/Invariant Columns: {', '.join([c['column'] + ' [val: ' + c['constant_value'] + ']' for c in profile.constant_columns])}")
        elif profile.all_null_columns:
            st.warning(f"Completely Empty Columns: {', '.join(profile.all_null_columns)}")
        else:
            st.success("All columns exhibit normal variance and active data values.")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 5. Dataset Structure
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">4. Schema Detection & Structural Typing</h3>
                <p class="chart-subtitle">Inferred data formats, semantic types, and unique cardinality counts</p>
            </div>
            <span class="badge badge-neutral">Schema</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    structure_df = build_dataset_structure_table(orig_df, type_map=type_map)
    st.dataframe(structure_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 6. Automated Cleaning Before/After
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">5. Automated Non-Destructive Data Cleaning</h3>
                <p class="chart-subtitle">Trims whitespace, removes duplicates, drops empty rows, and applies median/mode imputation</p>
            </div>
            <span class="badge badge-success">Automated Pipeline</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    clean_m1, clean_m2, clean_m3, clean_m4 = st.columns(4)
    with clean_m1:
        render_kpi_card(
            title="Cleaned Rows",
            value=f"{summary.cleaned_rows:,}",
            delta=f"{summary.cleaned_rows - summary.original_rows:+d} rows",
            delta_positive=summary.cleaned_rows >= summary.original_rows,
            icon="🧹",
            icon_color_class="kpi-icon-indigo",
            subtitle=f"Original: {summary.original_rows:,}",
        )
    with clean_m2:
        render_kpi_card(
            title="Duplicates Removed",
            value=f"{summary.duplicates_removed}",
            icon="👥",
            icon_color_class="kpi-icon-cyan",
            subtitle="Purged redundant records",
        )
    with clean_m3:
        render_kpi_card(
            title="Missing Before",
            value=f"{summary.missing_values_before:,}",
            icon="❓",
            icon_color_class="kpi-icon-amber",
            subtitle="Initial null values",
        )
    with clean_m4:
        render_kpi_card(
            title="Missing After",
            value=f"{summary.missing_values_after:,}",
            delta=f"{summary.missing_values_after - summary.missing_values_before:+d}",
            delta_positive=summary.missing_values_after <= summary.missing_values_before,
            icon="✅",
            icon_color_class="kpi-icon-emerald",
            subtitle="Residual null cells",
        )

    with st.expander("View Automated Cleaning Actions Log", expanded=False):
        for act in summary.actions_taken:
            st.markdown(f"- {act}")

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Choose dataset mode for visualizations and stats
    dataset_mode = st.radio(
        "Select Analytical Scope:",
        ["Cleaned Dataset (Recommended)", "Original Raw Dataset"],
        horizontal=True,
        key="universal_dataset_mode_selector",
    )
    active_df = clean_df if "Cleaned" in dataset_mode else orig_df

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 7. Automatic Visual Analytics
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">6. Dynamic Visual Analytics</h3>
                <p class="chart-subtitle">Autonomously synthesized distributions, relationships, and correlation matrices</p>
            </div>
            <span class="badge badge-indigo">Visual Laboratory</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    viz_data = generate_visual_analytics_data(active_df)

    # Tabs for different visualization perspectives
    tab_cat, tab_num, tab_rel, tab_corr = st.tabs([
        "Categorical Distributions",
        "Numeric Distributions",
        "Bivariate & Aggregated Relationships",
        "Correlation Matrix",
    ])

    with tab_cat:
        cat_cols = viz_data["categorical_cols"]
        if cat_cols:
            selected_cat = st.selectbox("Select Categorical Column to Visualize:", cat_cols, key="viz_cat_select")
            fig_cat = create_categorical_bar_chart(active_df, selected_cat)
            if fig_cat:
                st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No categorical columns detected in this dataset.")

    with tab_num:
        num_cols = viz_data["numeric_cols"]
        if num_cols:
            selected_num = st.selectbox("Select Numeric Column to Visualize:", num_cols, key="viz_num_select")
            fig_num = create_numeric_distribution_chart(active_df, selected_num)
            if fig_num:
                st.plotly_chart(fig_num, use_container_width=True)
        else:
            st.info("No numeric columns detected in this dataset.")

    with tab_rel:
        rel_c1, rel_c2 = st.columns(2)
        # Categorical + Numeric Aggregation
        with rel_c1:
            if cat_cols and num_cols:
                st.markdown("**Categorical Metric Aggregation**")
                sel_cat_rel = st.selectbox("Group By (Category):", cat_cols, key="rel_cat_group")
                sel_num_rel = st.selectbox("Aggregate (Metric):", viz_data["metric_cols"] or num_cols, key="rel_num_agg")
                agg_type = st.radio("Function:", ["mean", "sum"], horizontal=True, key="rel_agg_type")
                fig_agg = create_aggregated_bar_chart(active_df, sel_cat_rel, sel_num_rel, agg_func=agg_type)
                if fig_agg:
                    st.plotly_chart(fig_agg, use_container_width=True)
            else:
                st.info("Need at least 1 categorical and 1 numeric column for categorical metric aggregation.")

        # Numeric + Numeric Scatter or Date + Numeric Time Series
        with rel_c2:
            if len(num_cols) >= 2:
                st.markdown("**Numeric Bivariate Scatter Plot**")
                x_num = st.selectbox("X-Axis (Metric):", num_cols, index=0, key="scatter_x")
                y_num = st.selectbox("Y-Axis (Metric):", num_cols, index=min(1, len(num_cols) - 1), key="scatter_y")
                color_dim = st.selectbox("Color By (Optional Category):", [None] + cat_cols, key="scatter_color")
                fig_scatter = create_scatter_plot(active_df, x_num, y_num, color_dim)
                if fig_scatter:
                    st.plotly_chart(fig_scatter, use_container_width=True)
            elif viz_data["date_cols"] and num_cols:
                st.markdown("**Time-Series Trend**")
                date_c = viz_data["date_cols"][0]
                num_c = num_cols[0]
                fig_ts = create_time_series_chart(active_df, date_c, num_c)
                if fig_ts:
                    st.plotly_chart(fig_ts, use_container_width=True)
            else:
                st.info("Insufficient numeric or date columns for bivariate scatter or time-series charts.")

    with tab_corr:
        corr_matrix = viz_data["correlation_matrix"]
        if corr_matrix is not None and not corr_matrix.empty:
            fig_corr = create_correlation_heatmap(corr_matrix)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Correlation matrix requires at least 2 non-identifier numeric columns.")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 8. Generic Statistical Analysis
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">7. Tabular Statistical Breakdown</h3>
                <p class="chart-subtitle">Descriptive summary statistics across numeric, categorical, date, and text features</p>
            </div>
            <span class="badge badge-neutral">Statistics</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    stat_tab1, stat_tab2, stat_tab3, stat_tab4 = st.tabs([
        "Numeric Statistics",
        "Categorical Summaries",
        "Date Timeline Stats",
        "Text Field Analysis",
    ])

    with stat_tab1:
        num_stats = calculate_numeric_statistics(active_df, viz_data["numeric_cols"])
        if not num_stats.empty:
            st.dataframe(num_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No numeric columns found.")

    with stat_tab2:
        cat_stats = calculate_categorical_statistics(active_df, viz_data["categorical_cols"])
        if not cat_stats.empty:
            st.dataframe(cat_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No categorical columns found.")

    with stat_tab3:
        date_stats = calculate_date_statistics(active_df, viz_data["date_cols"])
        if not date_stats.empty:
            st.dataframe(date_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No date columns found.")

    with stat_tab4:
        text_cols = [c for c, t in type_map.items() if t == ColumnType.TEXT]
        text_stats = calculate_text_statistics(active_df, text_cols)
        if not text_stats.empty:
            st.dataframe(text_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No free-form text columns found.")

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 9. Dataset Preview & Cleaned Download
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">8. Dataset Preview & Cleaned CSV Export</h3>
                <p class="chart-subtitle">Direct row-level data inspector and export pipeline</p>
            </div>
            <span class="badge badge-indigo">Export</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_prev_head, col_prev_dl = st.columns([3, 1.2])
    with col_prev_head:
        st.caption(f"Displaying first 100 rows of **{active_df.shape[0]:,}** records across **{active_df.shape[1]}** columns.")
    with col_prev_dl:
        cleaned_csv_bytes = clean_df.to_csv(index=False).encode("utf-8")
        clean_name = f"{filename.rsplit('.', 1)[0]}_cleaned.csv" if filename else "dataset_cleaned.csv"
        st.download_button(
            label="📥 Download Cleaned CSV",
            data=cleaned_csv_bytes,
            file_name=clean_name,
            mime="text/csv",
            use_container_width=True,
        )

    st.dataframe(active_df.head(100), use_container_width=True)
