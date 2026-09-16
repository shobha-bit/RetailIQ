import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from python_app.data.loader import RetailDataBundle
from python_app.analytics.retail_analytics import (
    RetailFilters,
    filter_retail_data,
    calculate_retail_kpis,
    calculate_monthly_sales,
    calculate_sales_by_category,
    calculate_sales_by_region,
    calculate_sales_by_segment,
    calculate_top_products,
    get_filter_options,
)
from python_app.utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
    format_days,
    format_abbreviated_currency,
)
from python_app.utils.ui import (
    render_page_header,
    render_kpi_card,
    render_supply_chain_alert,
    render_empty_state,
    render_recent_insights_card,
    get_plotly_theme,
)

SEGMENT_COLORS = {
    "Consumer": "#4F46E5",
    "Corporate": "#8B5CF6",
    "Home Office": "#06B6D4",
}

CATEGORY_COLORS = {
    "Technology": "#4F46E5",
    "Furniture": "#F59E0B",
    "Office Supplies": "#10B981",
}


def render_executive_dashboard(bundle: RetailDataBundle):
    """
    Render the Executive Intelligence Dashboard with dynamic KPI cards,
    real-time supply chain alerts, Plotly analytical visualizations, and interactive filters.
    """
    # 1. Page Header with Shobha greeting and status badges
    render_page_header(
        title="Executive Dashboard",
        user_greeting="Welcome back, Shobha! 👋",
        description="Unified enterprise view of revenue velocity, customer segments, and inventory health.",
        badge_label="Live Telemetry",
    )

    # 2. Extract dynamic filter options from datasets (no hardcoding)
    filter_opts = get_filter_options(bundle)
    regions = ["All"] + filter_opts["regions"]
    categories = ["All"] + filter_opts["categories"]
    segments = ["All"] + filter_opts["segments"]
    date_presets = ["All", "7D", "30D", "90D", "YTD", "1Y"]

    # Initialize session state for filters if not present
    if "exec_date_preset" not in st.session_state:
        st.session_state["exec_date_preset"] = "All"
    if "exec_region" not in st.session_state:
        st.session_state["exec_region"] = "All"
    if "exec_category" not in st.session_state:
        st.session_state["exec_category"] = "All"
    if "exec_segment" not in st.session_state:
        st.session_state["exec_segment"] = "All"
    if "exec_search" not in st.session_state:
        st.session_state["exec_search"] = ""

    # 3. Interactive Filter Bar in SaaS Container Card
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">Cross-Table Slicing</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3, f_col4 = st.columns([1.6, 1.2, 1.2, 1.2])

        with f_col1:
            selected_date = st.pills(
                "Time Horizon",
                options=date_presets,
                default=st.session_state["exec_date_preset"],
                key="pills_date_preset",
                label_visibility="collapsed",
            )
            if selected_date:
                st.session_state["exec_date_preset"] = selected_date

        with f_col2:
            selected_region = st.selectbox(
                "Region",
                options=regions,
                index=regions.index(st.session_state["exec_region"]) if st.session_state["exec_region"] in regions else 0,
                key="select_region",
                label_visibility="collapsed",
            )
            st.session_state["exec_region"] = selected_region

        with f_col3:
            selected_category = st.selectbox(
                "Category",
                options=categories,
                index=categories.index(st.session_state["exec_category"]) if st.session_state["exec_category"] in categories else 0,
                key="select_category",
                label_visibility="collapsed",
            )
            st.session_state["exec_category"] = selected_category

        with f_col4:
            selected_segment = st.selectbox(
                "Segment",
                options=segments,
                index=segments.index(st.session_state["exec_segment"]) if st.session_state["exec_segment"] in segments else 0,
                key="select_segment",
                label_visibility="collapsed",
            )
            st.session_state["exec_segment"] = selected_segment

        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["exec_search"],
                placeholder="🔍 Search SKU, product name, order ID, city, customer...",
                key="input_search",
                label_visibility="collapsed",
            )
            st.session_state["exec_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["exec_date_preset"] != "All"
                or st.session_state["exec_region"] != "All"
                or st.session_state["exec_category"] != "All"
                or st.session_state["exec_segment"] != "All"
                or bool(st.session_state["exec_search"].strip())
            )

            def _reset_exec_filters():
                st.session_state["pills_date_preset"] = "All"
                st.session_state["select_region"] = "All"
                st.session_state["select_category"] = "All"
                st.session_state["select_segment"] = "All"
                st.session_state["input_search"] = ""
                st.session_state["exec_date_preset"] = "All"
                st.session_state["exec_region"] = "All"
                st.session_state["exec_category"] = "All"
                st.session_state["exec_segment"] = "All"
                st.session_state["exec_search"] = ""

            if st.button("↺ Reset Filters", use_container_width=True, disabled=not has_active_filters, on_click=_reset_exec_filters):
                st.rerun()

    # 4. Construct RetailFilters and apply filtering via Phase 2 analytics engine
    filters = RetailFilters(
        date_range=st.session_state["exec_date_preset"],
        region=None if st.session_state["exec_region"] == "All" else st.session_state["exec_region"],
        category=None if st.session_state["exec_category"] == "All" else st.session_state["exec_category"],
        segment=None if st.session_state["exec_segment"] == "All" else st.session_state["exec_segment"],
        search_query=st.session_state["exec_search"].strip() or None,
    )

    filtered_bundle = filter_retail_data(bundle, filters)
    kpis = calculate_retail_kpis(filtered_bundle)

    # 5. ROW 1: KPI Overview Grid (6 Standard Executive KPIs + Dynamic YoY)
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        render_kpi_card(
            title="Total Sales",
            value=format_currency(kpis["total_sales"]),
            change=kpis.get("sales_yoy_growth_pct"),
            change_period="YoY Growth",
            target="$2.5M",
            icon="💰",
            color_variant="blue",
        )

    with col2:
        render_kpi_card(
            title="Total Orders",
            value=format_number(kpis["distinct_orders"]),
            subtitle="Completed transactions",
            icon="🛒",
            color_variant="green",
        )

    with col3:
        render_kpi_card(
            title="Avg Order Value",
            value=format_currency(kpis["aov"]),
            subtitle="Mean revenue per order",
            icon="💳",
            color_variant="purple",
        )

    with col4:
        render_kpi_card(
            title="Total Returns",
            value=format_number(kpis["total_returns"]),
            subtitle="Verified refund records",
            icon="↩️",
            color_variant="rose",
        )

    with col5:
        render_kpi_card(
            title="Return Rate",
            value=format_percentage(kpis["return_rate_pct"]),
            target="< 10%",
            icon="📊",
            color_variant="amber",
        )

    with col6:
        render_kpi_card(
            title="Avg Delivery Days",
            value=format_days(kpis["avg_delivery_days"]),
            target="< 5 days",
            icon="🚚",
            color_variant="cyan",
        )

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 6. Real-Time Supply Chain Stockout Alert
    if kpis["low_stock_items"] > 0:
        critical_inv = bundle.inventory[
            bundle.inventory["stock_status"].isin(["Critical", "Out of Stock", "Low Stock"])
        ]
        critical_skus = critical_inv["product_id"].head(3).tolist() if not critical_inv.empty else []
        render_supply_chain_alert(
            low_stock_count=kpis["low_stock_items"],
            avg_delivery_days=kpis["avg_delivery_days"],
            critical_skus=critical_skus,
        )

    # 7. Check for Empty State
    if filtered_bundle.orders.empty:
        render_empty_state("No order records match the active filter criteria. Try expanding the time horizon or clearing filters.")
        return

    # 8. Analytical Visualizations
    plotly_theme = get_plotly_theme()

    # Calculate analytical aggregations
    monthly_df = calculate_monthly_sales(filtered_bundle.orders)
    seg_df = calculate_sales_by_segment(filtered_bundle.orders, bundle.customers)
    cat_df = calculate_sales_by_category(filtered_bundle.orders, bundle.products)
    reg_df = calculate_sales_by_region(filtered_bundle.orders)
    top_products_df = calculate_top_products(filtered_bundle.orders, bundle.products, limit=5)

    # =========================================================================
    # ROW 2: Sales Trend (1.8 col) | Channel Performance (1.1 col) | Sales by Category (1.1 col)
    # =========================================================================
    chart_row1_left, chart_row1_mid, chart_row1_right = st.columns([1.8, 1.1, 1.1])

    with chart_row1_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Sales Trend</h3>
                    <p class="chart-subtitle">Monthly net sales volume and growth trajectory</p>
                </div>
                <span class="badge badge-primary">Monthly Trend</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not monthly_df.empty:
            fig_monthly = go.Figure()
            # Net Revenue Bar with gradient-like modern indigo color
            fig_monthly.add_trace(
                go.Bar(
                    x=monthly_df["label"],
                    y=monthly_df["sales"],
                    name="Net Revenue",
                    marker=dict(
                        color="#4F46E5",
                        opacity=0.9,
                    ),
                    hovertemplate="<b>%{x}</b><br>Net Revenue: $%{y:,.2f}<br>Orders: %{customdata[0]:,}<br>AOV: $%{customdata[1]:,.2f}<extra></extra>",
                    customdata=monthly_df[["orders", "aov"]].values,
                )
            )
            # Growth Trajectory Line
            fig_monthly.add_trace(
                go.Scatter(
                    x=monthly_df["label"],
                    y=monthly_df["sales"],
                    name="Growth Trajectory",
                    mode="lines+markers",
                    line=dict(color="#06B6D4", width=2.5, shape="spline"),
                    marker=dict(size=5, color="#06B6D4"),
                    hovertemplate="<b>%{x} Trajectory</b><br>Revenue: $%{y:,.2f}<extra></extra>",
                )
            )

            fig_monthly.update_layout(
                **plotly_theme,
                height=290,
                xaxis=dict(
                    **plotly_theme["xaxis"],
                    tickangle=-45 if len(monthly_df) > 18 else 0,
                ),
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickprefix="$",
                    tickformat="~s",
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
            st.plotly_chart(fig_monthly, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No monthly trend data available.")

    with chart_row1_mid:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Channel Performance</h3>
                    <p class="chart-subtitle">Contribution by customer segment</p>
                </div>
                <span class="badge badge-purple">Omnichannel</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not seg_df.empty:
            slice_colors = [SEGMENT_COLORS.get(str(s), "#64748B") for s in seg_df["segment"]]
            fig_seg = go.Figure(
                data=[
                    go.Pie(
                        labels=seg_df["segment"],
                        values=seg_df["sales"],
                        hole=0.6,
                        marker=dict(colors=slice_colors, line=dict(color="#FFFFFF", width=2)),
                        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<br>Orders: %{customdata[0]:,}<extra></extra>",
                        customdata=seg_df[["orders"]].values,
                        textinfo="percent",
                        textposition="inside",
                        textfont=dict(size=11, color="#FFFFFF"),
                    )
                ]
            )
            fig_seg.update_layout(
                **plotly_theme,
                height=290,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.05,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
            )
            st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No customer segment data available.")

    with chart_row1_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Sales by Category</h3>
                    <p class="chart-subtitle">Gross volume by department</p>
                </div>
                <span class="badge badge-success">Department</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not cat_df.empty:
            cat_slice_colors = [CATEGORY_COLORS.get(str(c), "#6366F1") for c in cat_df["category"]]
            fig_cat_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=cat_df["category"],
                        values=cat_df["sales"],
                        hole=0.6,
                        marker=dict(colors=cat_slice_colors, line=dict(color="#FFFFFF", width=2)),
                        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<br>Orders: %{customdata[0]:,}<extra></extra>",
                        customdata=cat_df[["orders"]].values,
                        textinfo="percent",
                        textposition="inside",
                        textfont=dict(size=11, color="#FFFFFF"),
                    )
                ]
            )
            fig_cat_donut.update_layout(
                **plotly_theme,
                height=290,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.05,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
            )
            st.plotly_chart(fig_cat_donut, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No category data available.")

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 3: Top Performing Products (1.4 col) | Sales by Region (1.1 col) | Business Insights (1.5 col)
    # =========================================================================
    chart_row2_left, chart_row2_mid, chart_row2_right = st.columns([1.4, 1.1, 1.5])

    with chart_row2_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Top Performing Products</h3>
                    <p class="chart-subtitle">Highest revenue generating catalog SKUs</p>
                </div>
                <span class="badge badge-primary">Catalog Leaders</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not top_products_df.empty:
            display_top = top_products_df.copy()
            display_top["Total Sales"] = display_top["sales"].apply(lambda v: format_currency(v))
            display_top["Orders"] = display_top["orders"].apply(lambda v: format_number(v))
            display_top = display_top.rename(
                columns={
                    "product_id": "SKU",
                    "product_name": "Product Name",
                    "category": "Category",
                }
            )
            cols_to_render = ["SKU"]
            if "Product Name" in display_top.columns:
                cols_to_render.append("Product Name")
            if "Category" in display_top.columns:
                cols_to_render.append("Category")
            cols_to_render.extend(["Total Sales", "Orders"])

            st.dataframe(
                display_top[cols_to_render],
                use_container_width=True,
                hide_index=True,
                height=280,
            )
        else:
            render_empty_state("No product sales data available for the active filter.")

    with chart_row2_mid:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Sales by Region</h3>
                    <p class="chart-subtitle">Geographic revenue & order density</p>
                </div>
                <span class="badge badge-neutral">Territories</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not reg_df.empty:
            fig_reg = go.Figure(
                data=[
                    go.Bar(
                        x=reg_df["region"],
                        y=reg_df["sales"],
                        marker=dict(
                            color="#8B5CF6",
                            line=dict(color="#7C3AED", width=1),
                        ),
                        hovertemplate="<b>%{x} Region</b><br>Revenue: $%{y:,.2f}<br>Share: %{customdata[0]:.2f}%<br>Orders: %{customdata[1]:,}<extra></extra>",
                        customdata=reg_df[["pct_of_total", "orders"]].values,
                    )
                ]
            )
            fig_reg.update_layout(
                **plotly_theme,
                height=280,
                xaxis=dict(
                    **plotly_theme["xaxis"],
                ),
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickprefix="$",
                    tickformat="~s",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No regional data available.")

    with chart_row2_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Business Insights</h3>
                    <p class="chart-subtitle">Key findings derived from analytics engine</p>
                </div>
                <span class="badge badge-purple">Insights</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Generate live dynamic insights derived strictly from verified data
        top_region_name = reg_df.iloc[0]["region"] if not reg_df.empty else "N/A"
        top_region_sales = format_currency(reg_df.iloc[0]["sales"]) if not reg_df.empty else "$0"
        top_cat_name = cat_df.iloc[0]["category"] if not cat_df.empty else "N/A"
        top_cat_pct = f"{cat_df.iloc[0]['pct_of_total']:.1f}%" if not cat_df.empty else "0%"

        render_recent_insights_card(
            title=f"Regional Lead: {top_region_name} Territory",
            text=f"Generates {top_region_sales} in gross volume, representing the primary revenue anchor.",
            icon="🏆",
            color_variant="blue",
            badge="Revenue Leader",
        )

        render_recent_insights_card(
            title=f"Category Concentration: {top_cat_name}",
            text=f"Commands {top_cat_pct} of total catalog revenue. Monitor margins and stock buffers closely.",
            icon="📦",
            color_variant="purple",
            badge="Merchandise",
        )

        render_recent_insights_card(
            title="Logistics & Delivery Turnaround",
            text=f"Average turnaround is {kpis['avg_delivery_days']:.2f} days across carrier networks.",
            icon="🚚",
            color_variant="cyan",
            badge="Fulfillment",
        )

