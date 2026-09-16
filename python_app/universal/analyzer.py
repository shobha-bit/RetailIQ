"""
Universal Statistical Analyzer & Visual Generator
==================================================
Performs type-driven statistical aggregation and prepares data structures for
Plotly visualizations.
Works generically on arbitrary tabular data without assuming e-commerce or retail schemas.
Guards against plotting artificial identifier columns or crowded high-cardinality labels.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from python_app.universal.type_detector import detect_all_column_types, ColumnType


def is_likely_id_column(column_name: str, series: pd.Series) -> bool:
    """
    Check if a numeric or string column appears to be a surrogate key or record ID
    (e.g., sequential 1..N, 'id', 'row_id', or 100% unique with 'id' in name).
    """
    col_lower = str(column_name).lower()
    if col_lower in {"id", "row_id", "index", "key", "_id"} or col_lower.endswith("_id") or col_lower.startswith("id_"):
        return True

    # Check if numeric and strictly sequential 1..N or 0..N-1
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if len(non_null) > 5 and non_null.nunique() == len(non_null):
            diffs = non_null.sort_values().diff().dropna()
            if (diffs == 1).all():
                return True

    return False


def calculate_numeric_statistics(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Computes count, mean, median, min, max, and std for numeric columns.
    Returns a formatted summary DataFrame.
    """
    if numeric_cols is None:
        type_map = detect_all_column_types(df)
        numeric_cols = [c for c, t in type_map.items() if t == ColumnType.NUMERIC]

    if not numeric_cols:
        return pd.DataFrame(columns=["Column", "Count", "Mean", "Median", "Min", "Max", "Std Dev"])

    stats_list = []
    for col in numeric_cols:
        # Coerce safely in case of string representation
        s = pd.to_numeric(
            df[col].astype(str).str.replace(r"[$,%\s]", "", regex=True),
            errors="coerce"
        ).dropna()

        if len(s) == 0:
            continue

        stats_list.append({
            "Column": str(col),
            "Count": int(s.count()),
            "Mean": round(float(s.mean()), 2),
            "Median": round(float(s.median()), 2),
            "Min": round(float(s.min()), 2),
            "Max": round(float(s.max()), 2),
            "Std Dev": round(float(s.std()), 2) if len(s) > 1 else 0.0,
        })

    return pd.DataFrame(stats_list)


def calculate_categorical_statistics(df: pd.DataFrame, categorical_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Computes unique count, most frequent value (mode), top frequency, and top percentage.
    """
    if categorical_cols is None:
        type_map = detect_all_column_types(df)
        categorical_cols = [c for c, t in type_map.items() if t == ColumnType.CATEGORICAL]

    if not categorical_cols:
        return pd.DataFrame(columns=["Column", "Unique Count", "Top Value", "Top Frequency", "Top Share %"])

    stats_list = []
    for col in categorical_cols:
        s = df[col].dropna().astype(str)
        if len(s) == 0:
            continue

        vc = s.value_counts()
        top_val = vc.index[0]
        top_freq = int(vc.iloc[0])
        top_share = round((top_freq / len(s)) * 100, 2)

        stats_list.append({
            "Column": str(col),
            "Unique Count": int(s.nunique()),
            "Top Value": top_val,
            "Top Frequency": top_freq,
            "Top Share %": top_share,
        })

    return pd.DataFrame(stats_list)


def calculate_date_statistics(df: pd.DataFrame, date_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Computes min date, max date, date range span, and valid count.
    """
    if date_cols is None:
        type_map = detect_all_column_types(df)
        date_cols = [c for c, t in type_map.items() if t == ColumnType.DATE]

    if not date_cols:
        return pd.DataFrame(columns=["Column", "Earliest Date", "Latest Date", "Date Span (Days)", "Valid Records"])

    stats_list = []
    for col in date_cols:
        s = pd.to_datetime(df[col], errors="coerce").dropna()
        if len(s) == 0:
            continue

        min_d = s.min()
        max_d = s.max()
        span_days = (max_d - min_d).days

        stats_list.append({
            "Column": str(col),
            "Earliest Date": min_d.strftime("%Y-%m-%d"),
            "Latest Date": max_d.strftime("%Y-%m-%d"),
            "Date Span (Days)": int(span_days),
            "Valid Records": int(len(s)),
        })

    return pd.DataFrame(stats_list)


def calculate_text_statistics(df: pd.DataFrame, text_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Computes non-null count, unique count, and text length metrics for text columns.
    """
    if text_cols is None:
        type_map = detect_all_column_types(df)
        text_cols = [c for c, t in type_map.items() if t == ColumnType.TEXT]

    if not text_cols:
        return pd.DataFrame(columns=["Column", "Non-null Count", "Unique Count", "Avg Text Length", "Max Text Length"])

    stats_list = []
    for col in text_cols:
        s = df[col].dropna().astype(str)
        if len(s) == 0:
            continue

        lengths = s.str.len()
        stats_list.append({
            "Column": str(col),
            "Non-null Count": int(len(s)),
            "Unique Count": int(s.nunique()),
            "Avg Text Length": round(float(lengths.mean()), 1),
            "Max Text Length": int(lengths.max()),
        })

    return pd.DataFrame(stats_list)


def calculate_correlation_matrix(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
    """
    Calculates Pearson correlation matrix for numeric columns, filtering out obvious ID columns.
    """
    if numeric_cols is None:
        type_map = detect_all_column_types(df)
        numeric_cols = [c for c, t in type_map.items() if t == ColumnType.NUMERIC]

    # Exclude obvious IDs
    meaningful_numeric = [c for c in numeric_cols if not is_likely_id_column(c, df[c])]

    if len(meaningful_numeric) < 2:
        return None

    # Coerce to numeric
    clean_numeric_df = pd.DataFrame()
    for c in meaningful_numeric:
        clean_numeric_df[c] = pd.to_numeric(
            df[c].astype(str).str.replace(r"[$,%\s]", "", regex=True),
            errors="coerce"
        )

    corr = clean_numeric_df.corr(method="pearson").round(3)
    return corr


def generate_visual_analytics_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prepares structured data and recommended pairings for automatic visual analytics:
    - Categorical bar charts (top 10 categories)
    - Numeric distribution histograms
    - Time-series pairings (Date + Numeric)
    - Scatter plot pairings (Numeric + Numeric)
    - Categorical aggregation (Grouped mean/sum of numeric by category)
    - Correlation matrix
    """
    type_map = detect_all_column_types(df)

    numeric_cols = [c for c, t in type_map.items() if t == ColumnType.NUMERIC]
    cat_cols = [c for c, t in type_map.items() if t == ColumnType.CATEGORICAL]
    date_cols = [c for c, t in type_map.items() if t == ColumnType.DATE]

    # Filter out pure IDs from numeric pairings
    metric_cols = [c for c in numeric_cols if not is_likely_id_column(c, df[c])]
    if not metric_cols and numeric_cols:
        metric_cols = numeric_cols  # Fallback if all look like IDs

    corr_df = calculate_correlation_matrix(df, numeric_cols)

    return {
        "type_map": type_map,
        "numeric_cols": numeric_cols,
        "metric_cols": metric_cols,
        "categorical_cols": cat_cols,
        "date_cols": date_cols,
        "correlation_matrix": corr_df,
    }


def create_categorical_bar_chart(df: pd.DataFrame, column: str, top_n: int = 12) -> Optional[go.Figure]:
    """Create a clean horizontal bar chart for a categorical column."""
    if column not in df.columns or df[column].dropna().empty:
        return None

    vc = df[column].dropna().astype(str).value_counts().head(top_n).reset_index()
    vc.columns = [column, "Count"]

    fig = px.bar(
        vc,
        x="Count",
        y=column,
        orientation="h",
        color="Count",
        color_continuous_scale=[[0, "#93C5FD"], [1, "#1D4ED8"]],
        title=f"Top Categories: {column}",
    )
    fig.update_layout(
        template="plotly_white",
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis={"title": "Occurrences"},
        coloraxis_showscale=False,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        height=320,
    )
    return fig


def create_numeric_distribution_chart(df: pd.DataFrame, column: str) -> Optional[go.Figure]:
    """Create an interactive distribution histogram for a numeric column."""
    if column not in df.columns:
        return None

    s = pd.to_numeric(df[column].astype(str).str.replace(r"[$,%\s]", "", regex=True), errors="coerce").dropna()
    if len(s) == 0:
        return None

    fig = px.histogram(
        x=s,
        nbins=25,
        title=f"Distribution: {column}",
        color_discrete_sequence=["#2563EB"],
        marginal="box",
    )
    fig.update_layout(
        template="plotly_white",
        xaxis={"title": column},
        yaxis={"title": "Frequency"},
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        height=320,
    )
    return fig


def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None) -> Optional[go.Figure]:
    """Create a scatter plot comparing two numeric variables."""
    if x_col not in df.columns or y_col not in df.columns:
        return None

    x_s = pd.to_numeric(df[x_col].astype(str).str.replace(r"[$,%\s]", "", regex=True), errors="coerce")
    y_s = pd.to_numeric(df[y_col].astype(str).str.replace(r"[$,%\s]", "", regex=True), errors="coerce")

    plot_df = pd.DataFrame({"x": x_s, "y": y_s})
    if color_col and color_col in df.columns:
        plot_df["color"] = df[color_col].astype(str)
        fig = px.scatter(
            plot_df.dropna(subset=["x", "y"]),
            x="x",
            y="y",
            color="color",
            title=f"{y_col} vs {x_col}",
            opacity=0.75,
        )
    else:
        fig = px.scatter(
            plot_df.dropna(subset=["x", "y"]),
            x="x",
            y="y",
            title=f"{y_col} vs {x_col}",
            opacity=0.75,
            color_discrete_sequence=["#3B82F6"],
        )

    fig.update_layout(
        template="plotly_white",
        xaxis={"title": x_col},
        yaxis={"title": y_col},
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        height=350,
    )
    return fig


def create_aggregated_bar_chart(
    df: pd.DataFrame,
    cat_col: str,
    num_col: str,
    agg_func: str = "mean",
    top_n: int = 10,
) -> Optional[go.Figure]:
    """Create a grouped aggregation chart (e.g. Mean Marks by Department)."""
    if cat_col not in df.columns or num_col not in df.columns:
        return None

    clean_df = pd.DataFrame({
        "cat": df[cat_col].astype(str),
        "num": pd.to_numeric(df[num_col].astype(str).str.replace(r"[$,%\s]", "", regex=True), errors="coerce"),
    }).dropna()

    if clean_df.empty:
        return None

    if agg_func == "sum":
        agg_df = clean_df.groupby("cat")["num"].sum().reset_index()
        title_agg = "Total"
    else:
        agg_df = clean_df.groupby("cat")["num"].mean().reset_index()
        title_agg = "Average"

    agg_df = agg_df.sort_values(by="num", ascending=False).head(top_n)

    fig = px.bar(
        agg_df,
        x="cat",
        y="num",
        color="num",
        color_continuous_scale=[[0, "#BAE6FD"], [1, "#0284C7"]],
        title=f"{title_agg} {num_col} by {cat_col}",
    )
    fig.update_layout(
        template="plotly_white",
        xaxis={"title": cat_col, "categoryorder": "total descending"},
        yaxis={"title": f"{title_agg} {num_col}"},
        coloraxis_showscale=False,
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        height=340,
    )
    return fig


def create_time_series_chart(df: pd.DataFrame, date_col: str, num_col: str) -> Optional[go.Figure]:
    """Create a time-series aggregation line chart for Date + Numeric pairs."""
    if date_col not in df.columns or num_col not in df.columns:
        return None

    dates = pd.to_datetime(df[date_col], errors="coerce")
    nums = pd.to_numeric(df[num_col].astype(str).str.replace(r"[$,%\s]", "", regex=True), errors="coerce")

    ts_df = pd.DataFrame({"date": dates, "val": nums}).dropna().sort_values("date")
    if len(ts_df) == 0:
        return None

    # Group by date or month depending on range
    ts_agg = ts_df.groupby("date")["val"].sum().reset_index()

    fig = px.line(
        ts_agg,
        x="date",
        y="val",
        markers=True,
        title=f"{num_col} Over Time ({date_col})",
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_layout(
        template="plotly_white",
        xaxis={"title": "Date"},
        yaxis={"title": f"Total {num_col}"},
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
        height=320,
    )
    return fig


def create_correlation_heatmap(
    df_or_corr: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
) -> Optional[go.Figure]:
    """
    Create a styled correlation heatmap for numeric columns.
    Accepts either a pre-computed correlation DataFrame or a raw DataFrame with numeric columns.
    """
    if df_or_corr is None or df_or_corr.empty:
        return None

    # Check if df_or_corr is already a square correlation matrix
    is_square_corr = (
        len(df_or_corr.columns) == len(df_or_corr.index)
        and list(df_or_corr.columns) == list(df_or_corr.index)
        and (df_or_corr.values.diagonal() == 1.0).all()
    )

    if is_square_corr:
        corr_df = df_or_corr
    else:
        corr_df = calculate_correlation_matrix(df_or_corr, numeric_cols)

    if corr_df is None or corr_df.empty:
        return None

    fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[[0, "#EFF6FF"], [0.5, "#93C5FD"], [1, "#1D4ED8"]],
        title="Numeric Pearson Correlation Heatmap",
        zmin=-1.0,
        zmax=1.0,
    )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 30, "r": 30, "t": 40, "b": 30},
        height=340,
    )
    return fig
