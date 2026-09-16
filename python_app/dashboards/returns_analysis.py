import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from python_app.data.loader import RetailDataBundle
from python_app.analytics.retail_analytics import (
    calculate_returns_kpis,
    calculate_return_reasons,
    calculate_return_status_distribution,
    calculate_monthly_returns,
    calculate_top_returned_products,
    calculate_returns_by_category,
)
from python_app.utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
)
from python_app.utils.ui import (
    render_page_header,
    render_kpi_card,
    render_empty_state,
    get_plotly_theme,
)


def render_returns_analysis(bundle: RetailDataBundle):
    """
    Render the Returns & Refund Liability Analysis Dashboard with root-cause defect analysis,
    category return rates, warranty liabilities, and SKU-level quality indicators.
    """
    # 1. Page Header
    render_page_header(
        title="Returns & Refund Liability Analysis",
        description="Root-cause defect analysis, category return rates, warranty refund liabilities, and SKU-level quality indicators.",
        badge_label="Returns Analytics",
        secondary_badge="Defect Tracking",
    )

    # 2. Extract dynamic filter options from datasets
    ret_df = bundle.returns.copy()
    ord_df = bundle.orders.copy()
    prod_df = bundle.products.copy() if bundle.products is not None else pd.DataFrame()

    reason_list = ["All"] + sorted(list(ret_df["return_reason"].dropna().unique()))
    status_list = ["All"] + sorted(list(ret_df["return_status"].dropna().unique()))
    category_list = ["All"] + (sorted(list(prod_df["category"].dropna().unique())) if not prod_df.empty else [])

    # Session State Initialization
    if "ret_reason" not in st.session_state:
        st.session_state["ret_reason"] = "All"
    if "ret_status" not in st.session_state:
        st.session_state["ret_status"] = "All"
    if "ret_category" not in st.session_state:
        st.session_state["ret_category"] = "All"
    if "ret_search" not in st.session_state:
        st.session_state["ret_search"] = ""

    # 3. Interactive Filter Bar
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">Returns Slicing</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1.5])

        with f_col1:
            st.caption("DEFECT REASON")
            selected_reason = st.selectbox(
                "Return Reason",
                options=reason_list,
                index=reason_list.index(st.session_state["ret_reason"]) if st.session_state["ret_reason"] in reason_list else 0,
                key="ret_select_reason",
                label_visibility="collapsed",
            )
            st.session_state["ret_reason"] = selected_reason

        with f_col2:
            st.caption("CLAIM STATUS")
            selected_status = st.selectbox(
                "Return Status",
                options=status_list,
                index=status_list.index(st.session_state["ret_status"]) if st.session_state["ret_status"] in status_list else 0,
                key="ret_select_status",
                label_visibility="collapsed",
            )
            st.session_state["ret_status"] = selected_status

        with f_col3:
            st.caption("MERCHANDISE CATEGORY")
            selected_cat = st.selectbox(
                "Category",
                options=category_list,
                index=category_list.index(st.session_state["ret_category"]) if st.session_state["ret_category"] in category_list else 0,
                key="ret_select_category",
                label_visibility="collapsed",
            )
            st.session_state["ret_category"] = selected_cat

        s_col1, s_col2 = st.columns([4.2, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["ret_search"],
                placeholder="🔍 Search return ID, product ID, product name, order ID, or defect trigger...",
                key="ret_input_search",
                label_visibility="collapsed",
            )
            st.session_state["ret_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["ret_reason"] != "All"
                or st.session_state["ret_status"] != "All"
                or st.session_state["ret_category"] != "All"
                or bool(st.session_state["ret_search"].strip())
            )
            def _reset_ret_filters():
                st.session_state["ret_select_reason"] = "All"
                st.session_state["ret_select_status"] = "All"
                st.session_state["ret_select_category"] = "All"
                st.session_state["ret_input_search"] = ""
                st.session_state["ret_reason"] = "All"
                st.session_state["ret_status"] = "All"
                st.session_state["ret_category"] = "All"
                st.session_state["ret_search"] = ""

            if st.button(
                "Reset Filters" if has_active_filters else "Clear",
                disabled=not has_active_filters,
                use_container_width=True,
                key="ret_btn_reset",
                on_click=_reset_ret_filters,
            ):
                st.rerun()

    # 4. Filter Returns Data
    filtered_ret = ret_df.copy()

    # Merge product metadata if available for category/name filtering
    if not prod_df.empty:
        prod_meta = prod_df[["product_id", "product_name", "category"]].drop_duplicates(subset=["product_id"])
        filtered_ret = filtered_ret.merge(prod_meta, on="product_id", how="left")
        filtered_ret["product_name"] = filtered_ret["product_name"].fillna(filtered_ret["product_id"])
        filtered_ret["category"] = filtered_ret["category"].fillna("General")
    else:
        filtered_ret["product_name"] = filtered_ret["product_id"]
        filtered_ret["category"] = "General"

    if st.session_state["ret_reason"] != "All":
        filtered_ret = filtered_ret[filtered_ret["return_reason"] == st.session_state["ret_reason"]]

    if st.session_state["ret_status"] != "All":
        filtered_ret = filtered_ret[filtered_ret["return_status"] == st.session_state["ret_status"]]

    if st.session_state["ret_category"] != "All":
        filtered_ret = filtered_ret[filtered_ret["category"] == st.session_state["ret_category"]]

    if st.session_state["ret_search"].strip():
        q = st.session_state["ret_search"].strip().lower()
        mask = (
            filtered_ret["return_id"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_ret["product_id"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_ret["product_name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_ret["order_row_id"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_ret["return_reason"].astype(str).str.lower().str.contains(q, na=False)
        )
        filtered_ret = filtered_ret[mask]

    # 5. Dynamic KPI Calculations (Using Phase 2 Engine)
    kpis = calculate_returns_kpis(filtered_ret, ord_df)
    total_returns = kpis["total_returns"]
    returned_products = kpis["returned_products"]
    distinct_returned_orders = kpis["distinct_returned_orders"]
    return_rate_pct = kpis["return_rate_pct"]
    total_refund = kpis["total_refund_amount"]
    avg_refund = (total_refund / total_returns) if total_returns > 0 else 0.0

    # 6. Render KPI Grid (5 Cards)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        render_kpi_card(
            title="Total Returns",
            value=format_number(total_returns),
            icon="↩️",
            icon_color_class="kpi-icon-indigo",
            subtitle="Total return records filed",
        )

    with kpi_col2:
        render_kpi_card(
            title="Distinct Returned Orders",
            value=format_number(distinct_returned_orders),
            icon="🛍️",
            icon_color_class="kpi-icon-purple",
            subtitle="Unique orders impacted",
        )

    with kpi_col3:
        render_kpi_card(
            title="Returned Products",
            value=format_number(returned_products),
            icon="📦",
            icon_color_class="kpi-icon-cyan",
            subtitle="Distinct catalog SKUs",
        )

    with kpi_col4:
        render_kpi_card(
            title="Return Rate",
            value=format_percentage(return_rate_pct),
            icon="🎯",
            icon_color_class="kpi-icon-amber",
            delta=f"{return_rate_pct:.2f}% of orders",
            delta_positive=return_rate_pct <= 10.0,
            subtitle="Returns / Total Distinct Orders",
        )

    with kpi_col5:
        render_kpi_card(
            title="Total Refund Liability",
            value=format_currency(total_refund),
            icon="💳",
            icon_color_class="kpi-icon-rose",
            subtitle=f"Avg {format_currency(avg_refund)} per return event",
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 7. Check for Empty State
    if filtered_ret.empty:
        render_empty_state(
            title="No Return Records Found",
            message="No return records match the active filter criteria. Try clearing or expanding your filter selections.",
        )
        return

    plotly_theme = get_plotly_theme()

    # Analytical breakdowns
    reason_summary = calculate_return_reasons(filtered_ret)
    status_summary = calculate_return_status_distribution(filtered_ret)
    cat_summary = calculate_returns_by_category(filtered_ret, prod_df)
    monthly_ret_summary = calculate_monthly_returns(filtered_ret)
    top_returned = calculate_top_returned_products(filtered_ret, prod_df, ord_df, limit=10)

    # =========================================================================
    # ROW 1: Root Cause Defect Breakdown & Return Status Distribution
    # =========================================================================
    row1_left, row1_right = st.columns([1.6, 1.2])

    with row1_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Return Reasons & Defect Root Causes</h3>
                    <p class="chart-subtitle">Primary operational and product quality triggers driving returns</p>
                </div>
                <span class="badge badge-warning">Root Cause Audit</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not reason_summary.empty:
            reason_colors = {
                "Late Delivery": "#F59E0B",
                "Defective Product": "#F43F5E",
                "Customer Changed Mind": "#8B5CF6",
                "Wrong Item": "#EC4899",
                "Damaged Product": "#FB923C",
                "Other": "#64748B",
            }
            bar_colors = [reason_colors.get(r, "#4F46E5") for r in reason_summary["return_reason"]]

            fig_reason = go.Figure(
                go.Bar(
                    x=reason_summary["return_reason"],
                    y=reason_summary["count"],
                    marker=dict(
                        color=bar_colors,
                        line=dict(color="rgba(255, 255, 255, 0.6)", width=1),
                    ),
                    hovertemplate="<b>%{x}</b><br>Returns: %{y:,}<br>Share: %{customdata[0]:.1f}%<br>Refunds: $%{customdata[1]:,}<extra></extra>",
                    customdata=reason_summary[["pct_of_total", "total_refund"]].values,
                    text=[f"{y:,}" for y in reason_summary["count"]],
                    textposition="outside",
                    textfont=dict(size=11, color="#475569"),
                )
            )
            fig_reason.update_layout(
                **plotly_theme,
                height=300,
                showlegend=False,
                xaxis=dict(**plotly_theme["xaxis"], title=None),
                yaxis=dict(**plotly_theme["yaxis"], title="Return Incidents"),
            )
            st.plotly_chart(fig_reason, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No return reasons available.")

    with row1_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Claim Processing Status</h3>
                    <p class="chart-subtitle">Resolution workflow stages across submitted return requests</p>
                </div>
                <span class="badge badge-neutral">Workflow</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not status_summary.empty:
            status_colors = {
                "Completed": "#10B981",
                "Rejected": "#F43F5E",
                "Requested": "#F59E0B",
                "Approved": "#4F46E5",
            }
            colors = [status_colors.get(s, "#64748B") for s in status_summary["return_status"]]

            fig_status = go.Figure(
                go.Pie(
                    labels=status_summary["return_status"],
                    values=status_summary["count"],
                    hole=0.68,
                    marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="<b>%{label}</b><br>Returns: %{value:,}<br>Share: %{percent}<extra></extra>",
                    textinfo="label+percent",
                    textposition="outside",
                    textfont=dict(size=11),
                )
            )
            fig_status.update_layout(
                **plotly_theme,
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No status records available.")

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 2: Category Return Exposure & Monthly Returns Trend
    # =========================================================================
    row2_left, row2_right = st.columns([1, 1.4])

    with row2_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Returns by Merchandise Category</h3>
                    <p class="chart-subtitle">Return volume and refund liabilities across catalog lines</p>
                </div>
                <span class="badge badge-neutral">Category Exposure</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not cat_summary.empty:
            cat_palette = ["#4F46E5", "#8B5CF6", "#06B6D4"]
            fig_cat = go.Figure(
                go.Bar(
                    x=cat_summary["category"],
                    y=cat_summary["return_count"],
                    marker=dict(
                        color=cat_palette[:len(cat_summary)],
                        line=dict(color="rgba(255, 255, 255, 0.6)", width=1),
                    ),
                    hovertemplate="<b>%{x}</b><br>Returns: %{y:,}<br>Refunds: $%{customdata:,}<extra></extra>",
                    customdata=cat_summary["total_refund"].values,
                    text=[f"{y:,}" for y in cat_summary["return_count"]],
                    textposition="outside",
                    textfont=dict(size=11, color="#475569"),
                )
            )
            fig_cat.update_layout(
                **plotly_theme,
                height=300,
                showlegend=False,
                xaxis=dict(**plotly_theme["xaxis"], title=None),
                yaxis=dict(**plotly_theme["yaxis"], title="Return Count"),
            )
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No category returns data available.")

    with row2_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Monthly Return Events & Refund Liabilities</h3>
                    <p class="chart-subtitle">Chronological return volume and dollar warranty liabilities</p>
                </div>
                <span class="badge badge-neutral">Historical Trend</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not monthly_ret_summary.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(
                go.Bar(
                    x=monthly_ret_summary["label"],
                    y=monthly_ret_summary["returns_count"],
                    name="Returns Count",
                    marker=dict(color="#C7D2FE", line=dict(color="#A5B4FC", width=1)),
                    hovertemplate="<b>%{x}</b><br>Returns: %{y:,}<extra></extra>",
                    yaxis="y",
                )
            )
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_ret_summary["label"],
                    y=monthly_ret_summary["total_refund"],
                    name="Refund Liabilities ($)",
                    mode="lines+markers",
                    line=dict(color="#F43F5E", width=2.5),
                    marker=dict(size=6, color="#F43F5E", line=dict(color="#FFFFFF", width=1.5)),
                    hovertemplate="<b>%{x}</b><br>Refunds: $%{y:,.2f}<extra></extra>",
                    yaxis="y2",
                )
            )
            fig_trend.update_layout(
                **plotly_theme,
                height=300,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    title="Returns Count",
                    showgrid=False,
                ),
                yaxis2=dict(
                    title="Refund Liability ($)",
                    overlaying="y",
                    side="right",
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    tickprefix="$",
                    tickformat="~s",
                    tickfont=dict(color="#64748B", size=10),
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11),
                ),
            )
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No monthly return records available.")

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 3: Top Returned Products & Actionable Root-Cause Register
    # =========================================================================
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Top Returned Products & Root-Cause Remediation</h3>
                <p class="chart-subtitle">SKUs exhibiting highest return frequency with targeted vendor and fulfillment remedies</p>
            </div>
            <span class="badge badge-warning">Remediation Action Plan</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not top_returned.empty:
        display_top = top_returned.copy()
        display_top["refund_fmt"] = display_top["total_refund"].apply(lambda r: f"${r:,.2f}")

        table_cols = [
            "product_id", "product_name", "category", "return_count",
            "refund_fmt", "top_reason", "recommendation"
        ]
        col_renames = {
            "product_id": "SKU",
            "product_name": "Product Name",
            "category": "Category",
            "return_count": "Return Count",
            "refund_fmt": "Total Refunds",
            "top_reason": "Primary Defect Reason",
            "recommendation": "Quality Remediation Action",
        }

        # Action Bar & CSV export
        t_col1, t_col2 = st.columns([3.5, 1.5])
        with t_col1:
            st.caption(f"Displaying top {len(display_top)} return SKUs requiring operational QA intervention")
        with t_col2:
            csv_data = display_top[table_cols].rename(columns=col_renames).to_csv(index=False)
            st.download_button(
                label="📥 Export Returns Register CSV",
                data=csv_data,
                file_name="returns_remediation_register.csv",
                mime="text/csv",
                use_container_width=True,
                key="ret_download_csv",
            )

        st.dataframe(
            display_top[table_cols].rename(columns=col_renames),
            use_container_width=True,
            hide_index=True,
        )
    else:
        render_empty_state("No returned product records available.")
