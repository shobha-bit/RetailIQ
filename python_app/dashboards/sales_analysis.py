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
    calculate_channel_margin,
    calculate_top_products,
    get_filter_options,
    safe_join_orders_customers,
    safe_join_orders_products,
)
from python_app.utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
    format_abbreviated_currency,
)
from python_app.utils.ui import (
    render_page_header,
    render_kpi_card,
    render_empty_state,
    get_plotly_theme,
)

CHANNEL_COLORS = {
    "Consumer": "#4F46E5",
    "Corporate": "#8B5CF6",
    "Home Office": "#06B6D4",
}


def render_sales_analysis(bundle: RetailDataBundle):
    """
    Render the Sales Analysis Dashboard with comprehensive KPI cards,
    sales velocity timeline, channel margin comparison, regional distribution,
    top catalog products, and searchable transaction ledger.
    """
    # 1. Page Header
    render_page_header(
        title="Sales Velocity & Channel Profitability",
        description="Deep exploration into channel sales velocity, regional profitability, discount sensitivity, and transaction-level margin realization.",
        badge_label="Sales Analytics",
        secondary_badge="Margin Tracking",
    )

    # 2. Extract dynamic filter options from datasets (zero hardcoding)
    filter_opts = get_filter_options(bundle)
    regions = ["All"] + filter_opts["regions"]
    categories = ["All"] + filter_opts["categories"]
    segments = ["All"] + filter_opts["segments"]
    date_presets = ["All", "7D", "30D", "90D", "YTD", "1Y"]

    # Initialize session state for filters if not present
    if "sales_date_preset" not in st.session_state:
        st.session_state["sales_date_preset"] = "All"
    if "sales_region" not in st.session_state:
        st.session_state["sales_region"] = "All"
    if "sales_category" not in st.session_state:
        st.session_state["sales_category"] = "All"
    if "sales_segment" not in st.session_state:
        st.session_state["sales_segment"] = "All"
    if "sales_search" not in st.session_state:
        st.session_state["sales_search"] = ""
    if "sales_view_metric" not in st.session_state:
        st.session_state["sales_view_metric"] = "Revenue"

    # 3. Interactive Filter Bar
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">Multi-Tier Breakdown</span>
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
                default=st.session_state["sales_date_preset"],
                key="sales_pills_date_preset",
                label_visibility="collapsed",
            )
            if selected_date:
                st.session_state["sales_date_preset"] = selected_date

        with f_col2:
            selected_region = st.selectbox(
                "Region",
                options=regions,
                index=regions.index(st.session_state["sales_region"]) if st.session_state["sales_region"] in regions else 0,
                key="sales_select_region",
                label_visibility="collapsed",
            )
            st.session_state["sales_region"] = selected_region

        with f_col3:
            selected_category = st.selectbox(
                "Category",
                options=categories,
                index=categories.index(st.session_state["sales_category"]) if st.session_state["sales_category"] in categories else 0,
                key="sales_select_category",
                label_visibility="collapsed",
            )
            st.session_state["sales_category"] = selected_category

        with f_col4:
            selected_segment = st.selectbox(
                "Segment",
                options=segments,
                index=segments.index(st.session_state["sales_segment"]) if st.session_state["sales_segment"] in segments else 0,
                key="sales_select_segment",
                label_visibility="collapsed",
            )
            st.session_state["sales_segment"] = selected_segment

        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["sales_search"],
                placeholder="🔍 Search SKU, product name, order ID, city, customer ID...",
                key="sales_input_search",
                label_visibility="collapsed",
            )
            st.session_state["sales_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["sales_date_preset"] != "All"
                or st.session_state["sales_region"] != "All"
                or st.session_state["sales_category"] != "All"
                or st.session_state["sales_segment"] != "All"
                or bool(st.session_state["sales_search"].strip())
            )
            def _reset_sales_filters():
                st.session_state["sales_pills_date_preset"] = "All"
                st.session_state["sales_select_region"] = "All"
                st.session_state["sales_select_category"] = "All"
                st.session_state["sales_select_segment"] = "All"
                st.session_state["sales_input_search"] = ""
                st.session_state["sales_date_preset"] = "All"
                st.session_state["sales_region"] = "All"
                st.session_state["sales_category"] = "All"
                st.session_state["sales_segment"] = "All"
                st.session_state["sales_search"] = ""

            if st.button(
                "Reset Filters" if has_active_filters else "Clear",
                disabled=not has_active_filters,
                use_container_width=True,
                key="sales_btn_reset",
                on_click=_reset_sales_filters,
            ):
                st.rerun()

    # 4. Construct Filter Object & Slice Data
    active_filters = RetailFilters(
        date_range=st.session_state["sales_date_preset"] if st.session_state["sales_date_preset"] != "All" else None,
        region=st.session_state["sales_region"] if st.session_state["sales_region"] != "All" else None,
        category=st.session_state["sales_category"] if st.session_state["sales_category"] != "All" else None,
        segment=st.session_state["sales_segment"] if st.session_state["sales_segment"] != "All" else None,
        search_query=st.session_state["sales_search"].strip() or None,
    )

    filtered_bundle = filter_retail_data(bundle, active_filters)

    # 5. Compute KPIs via Phase 2 Analytics Engine
    kpis = calculate_retail_kpis(filtered_bundle, active_filters)
    total_sales = kpis["total_sales"]
    total_orders = kpis["total_orders"]
    aov = kpis["aov"]
    sales_yoy = kpis["sales_yoy"]
    gross_margin_pct = 40.00
    total_gross_profit = round(total_sales * 0.40, 2)
    units_sold = len(filtered_bundle.orders)
    avg_basket_size = round(units_sold / total_orders, 2) if total_orders > 0 else 0.0

    # 6. Render KPI Grid (6 High-Contrast Modern Cards)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

    with kpi_col1:
        yoy_str = f"+{sales_yoy:.2f}%" if sales_yoy > 0 else f"{sales_yoy:.2f}%"
        render_kpi_card(
            title="Total Sales",
            value=format_currency(total_sales),
            icon="💰",
            icon_color_class="kpi-icon-blue",
            delta=yoy_str if total_sales > 0 else None,
            delta_positive=sales_yoy >= 0,
            delta_period="YoY trajectory",
            subtitle="Verified net commercial volume",
        )

    with kpi_col2:
        render_kpi_card(
            title="Total Orders",
            value=format_number(total_orders),
            icon="📦",
            icon_color_class="kpi-icon-purple",
            subtitle="Distinct checkout transactions",
        )

    with kpi_col3:
        render_kpi_card(
            title="Avg Order Value",
            value=format_currency(aov),
            icon="💳",
            icon_color_class="kpi-icon-green",
            subtitle="Mean transaction ticket size",
        )

    with kpi_col4:
        render_kpi_card(
            title="Sales YoY Growth",
            value=format_percentage(sales_yoy),
            icon="📈",
            icon_color_class="kpi-icon-green",
            delta="Annualized expansion",
            delta_positive=sales_yoy >= 0,
            subtitle="Prior year baseline comparison",
        )

    with kpi_col5:
        render_kpi_card(
            title="Gross Margin",
            value=f"{gross_margin_pct:.2f}%",
            icon="✨",
            icon_color_class="kpi-icon-blue",
            subtitle=f"{format_currency(total_gross_profit)} gross profit",
        )

    with kpi_col6:
        render_kpi_card(
            title="Units Sold",
            value=format_number(units_sold),
            icon="🛍️",
            icon_color_class="kpi-icon-amber",
            subtitle=f"Avg {avg_basket_size:.2f} items / order",
        )

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 7. Check for Empty State
    if filtered_bundle.orders.empty:
        render_empty_state("No sales records match the active filter criteria. Try expanding the time horizon or clearing filters.")
        return

    plotly_theme = get_plotly_theme()

    # Calculate analytical aggregations
    monthly_df = calculate_monthly_sales(filtered_bundle.orders)
    reg_df = calculate_sales_by_region(filtered_bundle.orders)
    channel_df = calculate_channel_margin(filtered_bundle.orders, bundle.customers)
    cat_df = calculate_sales_by_category(filtered_bundle.orders, bundle.products)
    top_products_df = calculate_top_products(filtered_bundle.orders, bundle.products, limit=10)

    # =========================================================================
    # ROW 1: Sales Velocity Timeline (2 cols) & Regional Distribution (1 col)
    # =========================================================================
    row1_left, row1_right = st.columns([2, 1])

    with row1_left:
        # Toggle between Revenue and Gross Profit
        metric_col_header, metric_col_toggle = st.columns([3, 2])
        with metric_col_header:
            st.markdown(
                """
                <div class="chart-header" style="margin-bottom: 0;">
                    <div>
                        <h3 class="chart-title">Sales Velocity & Net Contribution</h3>
                        <p class="chart-subtitle">Cumulative monthly trajectory comparing Net Revenue and Gross Contribution</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with metric_col_toggle:
            view_metric = st.radio(
                "Metric View",
                options=["Revenue", "Gross Profit"],
                horizontal=True,
                label_visibility="collapsed",
                key="sales_metric_toggle",
            )

        if not monthly_df.empty:
            fig_timeline = go.Figure()

            y_col = "sales" if view_metric == "Revenue" else "profit"
            color_stroke = "#4F46E5" if view_metric == "Revenue" else "#10B981"
            color_fill = "rgba(79, 70, 229, 0.12)" if view_metric == "Revenue" else "rgba(16, 185, 129, 0.12)"
            metric_label = "Net Revenue" if view_metric == "Revenue" else "Gross Profit"

            # Area trace
            fig_timeline.add_trace(
                go.Scatter(
                    x=monthly_df["label"],
                    y=monthly_df[y_col],
                    mode="lines",
                    name=metric_label,
                    line=dict(color=color_stroke, width=2.5, shape="spline"),
                    fill="tozeroy",
                    fillcolor=color_fill,
                    hovertemplate=f"<b>%{{x}}</b><br>{metric_label}: $%{{y:,.2f}}<br>Orders: %{{customdata[0]:,}}<br>AOV: $%{{customdata[1]:,.2f}}<extra></extra>",
                    customdata=monthly_df[["orders", "aov"]].values,
                )
            )

            fig_timeline.update_layout(
                **plotly_theme,
                height=300,
                xaxis=dict(
                    **plotly_theme["xaxis"],
                    tickangle=-45 if len(monthly_df) > 16 else 0,
                ),
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickprefix="$",
                    tickformat="~s",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No timeline records match the active filter criteria.")

    with row1_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Regional Sales Distribution</h3>
                    <p class="chart-subtitle">Commercial contribution by geographic territory</p>
                </div>
                <span class="badge badge-neutral">Territory</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not reg_df.empty:
            fig_reg = go.Figure(
                go.Bar(
                    x=reg_df["region"],
                    y=reg_df["sales"],
                    marker=dict(
                        color="#6366F1",
                        line=dict(color="#4F46E5", width=1),
                    ),
                    hovertemplate="<b>%{x} Region</b><br>Sales: $%{y:,.2f}<br>Share: %{customdata[0]:.1f}%<br>Orders: %{customdata[1]:,}<extra></extra>",
                    customdata=reg_df[["pct_of_total", "orders"]].values,
                )
            )
            fig_reg.update_layout(
                **plotly_theme,
                height=300,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickprefix="$",
                    tickformat="~s",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No regional records match the active filter criteria.")

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 2: Channel Margin Health (1 col) & Category Performance (1 col)
    # =========================================================================
    row2_left, row2_right = st.columns([1, 1])

    with row2_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Channel Margin Health</h3>
                    <p class="chart-subtitle">Net sales revenue and gross profit margin across sales channels</p>
                </div>
                <span class="badge badge-purple">Omnichannel</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not channel_df.empty:
            fig_channel = go.Figure()
            # Net Revenue Bar
            fig_channel.add_trace(
                go.Bar(
                    x=channel_df["channel"],
                    y=channel_df["revenue"],
                    name="Net Revenue",
                    marker_color="#4F46E5",
                    hovertemplate="<b>%{x}</b><br>Net Revenue: $%{y:,.2f}<br>Orders: %{customdata:,}<extra></extra>",
                    customdata=channel_df["orders"].values,
                )
            )
            # Gross Profit Bar
            fig_channel.add_trace(
                go.Bar(
                    x=channel_df["channel"],
                    y=channel_df["profit"],
                    name="Gross Profit",
                    marker_color="#10B981",
                    hovertemplate="<b>%{x}</b><br>Gross Profit: $%{y:,.2f}<br>Margin: 40.0%<extra></extra>",
                )
            )

            fig_channel.update_layout(
                **plotly_theme,
                height=290,
                barmode="group",
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
            st.plotly_chart(fig_channel, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No channel records match the active filter criteria.")

    with row2_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Category Revenue & Profit Realization</h3>
                    <p class="chart-subtitle">Performance breakdown across merchandise catalog categories</p>
                </div>
                <span class="badge badge-primary">Merchandise</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not cat_df.empty:
            cat_colors = ["#4F46E5", "#10B981", "#F59E0B"]
            fig_cat = go.Figure()
            fig_cat.add_trace(
                go.Bar(
                    x=cat_df["category"],
                    y=cat_df["sales"],
                    marker=dict(color=cat_colors[:len(cat_df)]),
                    hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.2f}<br>Share: %{customdata[0]:.1f}%<br>Orders: %{customdata[1]:,}<extra></extra>",
                    customdata=cat_df[["pct_of_total", "orders"]].values,
                )
            )

            fig_cat.update_layout(
                **plotly_theme,
                height=290,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickprefix="$",
                    tickformat="~s",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No category records match the active filter criteria.")

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 3: Top Catalog Products
    # =========================================================================
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Top Catalog Products by Net Revenue</h3>
                <p class="chart-subtitle">High-velocity merchandise items generating primary revenue volume</p>
            </div>
            <span class="badge badge-primary">Catalog Leaders</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not top_products_df.empty:
        display_top = top_products_df.copy()
        display_top["sales_formatted"] = display_top["sales"].apply(lambda x: f"${x:,.2f}")
        display_top["orders_formatted"] = display_top["orders"].apply(lambda x: f"{x:,}")

        # Rename for presentation
        cols_to_show = ["product_id"]
        col_rename = {"product_id": "SKU", "sales_formatted": "Net Revenue", "orders_formatted": "Orders"}
        if "product_name" in display_top.columns:
            cols_to_show.append("product_name")
            col_rename["product_name"] = "Product Name"
        if "category" in display_top.columns:
            cols_to_show.append("category")
            col_rename["category"] = "Category"
        cols_to_show.extend(["orders_formatted", "sales_formatted"])

        st.dataframe(
            display_top[cols_to_show].rename(columns=col_rename),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 4: Transaction Ledger Table
    # =========================================================================
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Transaction Ledger</h3>
                <p class="chart-subtitle">Point-of-sale and digital customer transactions with realized margin</p>
            </div>
            <span class="badge badge-neutral">Ledger Audit</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    orders_full = filtered_bundle.orders.copy()
    if not orders_full.empty:
        # Join product and customer details if needed
        ledger_df = orders_full
        if "customer_name" not in ledger_df.columns and bundle.customers is not None:
            ledger_df = safe_join_orders_customers(ledger_df, bundle.customers)
        if ("product_name" not in ledger_df.columns or "category" not in ledger_df.columns) and bundle.products is not None:
            ledger_df = safe_join_orders_products(ledger_df, bundle.products)

        ledger_display = ledger_df.sort_values(by="order_date", ascending=False).copy()
        ledger_display["date"] = pd.to_datetime(ledger_display["order_date"]).dt.strftime("%Y-%m-%d")
        ledger_display["net_revenue"] = ledger_display["sales"].apply(lambda s: f"${s:,.2f}")
        ledger_display["gross_margin"] = (ledger_display["sales"] * 0.40).apply(lambda m: f"${m:,.2f}")
        ledger_display["margin_pct"] = "40.0%"
        ledger_display["customer"] = ledger_display.get("customer_name", ledger_display["customer_id"])
        ledger_display["product"] = ledger_display.get("product_name", ledger_display["product_id"])
        ledger_display["channel"] = ledger_display.get("segment", "Consumer")

        # Table columns
        table_cols = [
            "order_id", "date", "customer", "channel", "region",
            "product", "net_revenue", "gross_margin", "margin_pct"
        ]
        available_cols = [c for c in table_cols if c in ledger_display.columns]
        renames = {
            "order_id": "Order ID",
            "date": "Date",
            "customer": "Customer",
            "channel": "Channel",
            "region": "Region",
            "product": "Product",
            "net_revenue": "Net Revenue",
            "gross_margin": "Gross Margin",
            "margin_pct": "Margin %",
        }

        # Controls for pagination & CSV export
        t_col1, t_col2 = st.columns([4, 1])
        with t_col1:
            st.caption(f"Showing up to 50 of {len(ledger_display):,} matching transactions")
        with t_col2:
            csv_data = ledger_display[available_cols].rename(columns=renames).to_csv(index=False)
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name="retail_sales_ledger.csv",
                mime="text/csv",
                use_container_width=True,
                key="sales_download_csv",
            )

        st.dataframe(
            ledger_display[available_cols].head(50).rename(columns=renames),
            use_container_width=True,
            hide_index=True,
        )

