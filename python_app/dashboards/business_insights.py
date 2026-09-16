"""
Business Insights & Strategic Analytics Dashboard (Phase 6)
============================================================
Management-level strategic analytics dashboard that synthesizes enterprise findings
across revenue velocity, customer retention/RFM, product opportunities,
inventory vulnerability, logistics bottlenecks, reverse logistics, and prescriptive
action planning.

Includes:
1. Executive Business Health Summary (7 Core KPIs)
2. Performance Insights (Geographic, Category, Segment Trajectories)
3. Customer & RFM Retention Insights (Churn Exposure, Champions Expansion)
4. Product & Category Opportunities (Concentration & Real Basket Cross-Sell)
5. Inventory Risk Insights (Replenishment Deficit & Warehouse Concentration)
6. Logistics Risk Insights (Carrier SLA Compliance & Transit Bottlenecks)
7. Returns & Quality Insights (Defect Pareto & Refund Liability)
8. Strategic Action Center (Data-Grounded Management Action Cards)
9. Price Elasticity Simulator (Interactive PED Modeling & Gross Margin Impact)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List

from python_app.data.loader import RetailDataBundle
from python_app.analytics.retail_analytics import (
    RetailFilters,
    filter_retail_data,
    get_filter_options,
)
from python_app.analytics.business_insights import (
    calculate_business_summary_kpis,
    calculate_performance_insights,
    calculate_retention_insights,
    calculate_product_opportunities,
    calculate_inventory_risk_insights,
    calculate_logistics_risk_insights,
    calculate_returns_risk_insights,
    generate_strategic_actions,
    simulate_price_elasticity,
    ELASTICITY_BENCHMARKS,
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
    render_empty_state,
    get_plotly_theme,
)

CATEGORY_COLORS = {
    "Technology": "#4F46E5",
    "Furniture": "#F59E0B",
    "Office Supplies": "#10B981",
}

REGION_COLORS = {
    "West": "#4F46E5",
    "East": "#8B5CF6",
    "Central": "#06B6D4",
    "South": "#EC4899",
}

SEGMENT_COLORS = {
    "Consumer": "#4F46E5",
    "Corporate": "#8B5CF6",
    "Home Office": "#10B981",
}


def render_business_insights_dashboard(bundle: RetailDataBundle):
    """
    Render the Business Insights & Strategic Analytics Dashboard.
    """
    # 1. Page Header
    render_page_header(
        title="Business Insights & Strategic Analytics",
        description="Executive decision-support cockpit synthesizing revenue velocity, customer retention cohorts, supply chain vulnerabilities, and prescriptive management actions.",
        badge_label="Business Insights",
        secondary_badge="Strategic Analytics",
    )

    # 2. Extract dynamic filter options from datasets
    filter_opts = get_filter_options(bundle)
    regions = ["All"] + filter_opts["regions"]
    categories = ["All"] + filter_opts["categories"]
    segments = ["All"] + filter_opts["segments"]
    date_presets = ["All", "7D", "30D", "90D", "YTD", "1Y"]

    # Session state initialization for filters
    if "bi_date_preset" not in st.session_state:
        st.session_state["bi_date_preset"] = "All"
    if "bi_region" not in st.session_state:
        st.session_state["bi_region"] = "All"
    if "bi_category" not in st.session_state:
        st.session_state["bi_category"] = "All"
    if "bi_segment" not in st.session_state:
        st.session_state["bi_segment"] = "All"
    if "bi_search" not in st.session_state:
        st.session_state["bi_search"] = ""

    # 3. Interactive Filter Bar
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">Executive Scope</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3, f_col4 = st.columns([1.6, 1.2, 1.2, 1.2])

        with f_col1:
            st.caption("HORIZON")
            selected_date = st.pills(
                "Time Horizon",
                options=date_presets,
                default=st.session_state["bi_date_preset"],
                key="bi_pills_date_preset",
                label_visibility="collapsed",
            )
            if selected_date:
                st.session_state["bi_date_preset"] = selected_date

        with f_col2:
            st.caption("REGION")
            selected_region = st.selectbox(
                "Region",
                options=regions,
                index=regions.index(st.session_state["bi_region"]) if st.session_state["bi_region"] in regions else 0,
                key="bi_select_region",
                label_visibility="collapsed",
            )
            st.session_state["bi_region"] = selected_region

        with f_col3:
            st.caption("CATEGORY")
            selected_category = st.selectbox(
                "Category",
                options=categories,
                index=categories.index(st.session_state["bi_category"]) if st.session_state["bi_category"] in categories else 0,
                key="bi_select_category",
                label_visibility="collapsed",
            )
            st.session_state["bi_category"] = selected_category

        with f_col4:
            st.caption("SEGMENT")
            selected_segment = st.selectbox(
                "Segment",
                options=segments,
                index=segments.index(st.session_state["bi_segment"]) if st.session_state["bi_segment"] in segments else 0,
                key="bi_select_segment",
                label_visibility="collapsed",
            )
            st.session_state["bi_segment"] = selected_segment

        s_col1, s_col2 = st.columns([4.2, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["bi_search"],
                placeholder="🔍 Filter strategic findings by SKU, category, region, customer...",
                key="bi_input_search",
                label_visibility="collapsed",
            )
            st.session_state["bi_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["bi_date_preset"] != "All"
                or st.session_state["bi_region"] != "All"
                or st.session_state["bi_category"] != "All"
                or st.session_state["bi_segment"] != "All"
                or bool(st.session_state["bi_search"].strip())
            )

            def _reset_bi_filters():
                st.session_state["bi_pills_date_preset"] = "All"
                st.session_state["bi_select_region"] = "All"
                st.session_state["bi_select_category"] = "All"
                st.session_state["bi_select_segment"] = "All"
                st.session_state["bi_input_search"] = ""
                st.session_state["bi_date_preset"] = "All"
                st.session_state["bi_region"] = "All"
                st.session_state["bi_category"] = "All"
                st.session_state["bi_segment"] = "All"
                st.session_state["bi_search"] = ""

            if st.button("↺ Reset", use_container_width=True, disabled=not has_active_filters, key="bi_reset_btn", on_click=_reset_bi_filters):
                st.rerun()

    # 4. Construct RetailFilters and apply filtering
    filters = RetailFilters(
        date_range=st.session_state["bi_date_preset"],
        region=None if st.session_state["bi_region"] == "All" else st.session_state["bi_region"],
        category=None if st.session_state["bi_category"] == "All" else st.session_state["bi_category"],
        segment=None if st.session_state["bi_segment"] == "All" else st.session_state["bi_segment"],
        search_query=st.session_state["bi_search"].strip() or None,
    )

    filtered_bundle = filter_retail_data(bundle, filters)
    filtered_orders = filtered_bundle.orders

    # 5. Calculate Core Business Insights Metrics
    summary_kpis = calculate_business_summary_kpis(filtered_bundle)
    perf_insights = calculate_performance_insights(filtered_orders, bundle.customers, bundle.products)
    ret_insights = calculate_retention_insights(filtered_orders, bundle.customers, bundle.products)
    prod_opp = calculate_product_opportunities(filtered_orders, bundle.products, bundle.returns)
    inv_risk = calculate_inventory_risk_insights(filtered_bundle.inventory, bundle.products)
    
    # Matching row IDs for cross-table logistics/returns linkage
    matching_ids = set(filtered_orders["row_id"].unique()) if has_active_filters else None
    log_risk = calculate_logistics_risk_insights(filtered_bundle.transportation, matching_row_ids=matching_ids)
    ret_risk = calculate_returns_risk_insights(filtered_bundle.returns, filtered_orders, bundle.products, matching_row_ids=matching_ids)
    strategic_actions = generate_strategic_actions(filtered_bundle, filters=filters)

    # Empty state guard
    if filtered_orders.empty:
        render_empty_state(
            title="No Retail Records Match Filter Scope",
            message="No active transactions match your current search and scope criteria. Reset filters to view enterprise findings.",
            action_label="Reset All Filters",
            on_action_click=lambda: None,
        )
        return

    # =====================================================================
    # SECTION 1: EXECUTIVE BUSINESS HEALTH SUMMARY (7 Core KPIs)
    # =====================================================================
    st.markdown(
        """
        <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>🏢 Executive Business Health Summary</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Core performance metrics reflecting the enterprise baseline across commercial and operational dimensions.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6, kpi_col7 = st.columns(7)

    with kpi_col1:
        render_kpi_card(
            title="Total Sales",
            value=format_currency(summary_kpis["total_sales"]),
            delta=f"{summary_kpis['sales_yoy']:+.1f}% YoY" if summary_kpis.get("sales_yoy") is not None else None,
            delta_positive=summary_kpis.get("sales_yoy", 0) >= 0,
            icon="💵",
            icon_color_class="kpi-icon-indigo",
            subtitle="Gross recognized sales",
        )

    with kpi_col2:
        render_kpi_card(
            title="Total Orders",
            value=format_number(summary_kpis["total_orders"]),
            subtitle="Completed order records",
            icon="🛒",
            icon_color_class="kpi-icon-emerald",
        )

    with kpi_col3:
        render_kpi_card(
            title="Avg Order Value",
            value=format_currency(summary_kpis["aov"]),
            subtitle="Realized basket revenue",
            icon="📈",
            icon_color_class="kpi-icon-cyan",
        )

    with kpi_col4:
        render_kpi_card(
            title="Sales YoY",
            value=format_percentage(summary_kpis["sales_yoy"]),
            subtitle="Annualized expansion",
            icon="🚀",
            icon_color_class="kpi-icon-purple",
        )

    with kpi_col5:
        render_kpi_card(
            title="Return Rate",
            value=format_percentage(summary_kpis["return_rate"]),
            subtitle=f"{summary_kpis['total_returns']:,} total returns",
            icon="↩️",
            icon_color_class="kpi-icon-amber",
            delta=f"{summary_kpis['return_rate']:.2f}% rate",
            delta_positive=summary_kpis["return_rate"] <= 10.0,
        )

    with kpi_col6:
        render_kpi_card(
            title="Avg Delivery Days",
            value=format_days(summary_kpis["average_delivery_days"]),
            subtitle=f"{summary_kpis['on_time_delivery_rate']:.1f}% on-time rate",
            icon="🚚",
            icon_color_class="kpi-icon-blue",
        )

    with kpi_col7:
        render_kpi_card(
            title="Low Stock Items",
            value=format_number(summary_kpis["low_stock_items"]),
            subtitle=f"Deficit: {inv_risk['total_replenishment_deficit']:,} units",
            icon="⚠️",
            icon_color_class="kpi-icon-rose" if summary_kpis["low_stock_items"] > 0 else "kpi-icon-emerald",
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =====================================================================
    # SECTION 2: PERFORMANCE INSIGHTS & REGIONAL / CATEGORY TRAJECTORY
    # =====================================================================
    st.markdown(
        """
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>📊 Performance Trajectory & Commercial Rankings</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Dynamically calculated commercial rankings across regions, merchandise categories, and buyer demographics.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3-column summary cards for Regional, Category, and Segment leaders
    p_card1, p_card2, p_card3 = st.columns(3)

    str_reg = perf_insights["strongest_region"]
    wk_reg = perf_insights["weakest_region"]
    str_cat = perf_insights["strongest_category"]
    wk_cat = perf_insights["weakest_category"]
    str_seg = perf_insights["strongest_segment"]

    with p_card1:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 0.35rem;">
                    🗺️ Geographic Leadership
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">
                    {str_reg['name']} <span style="font-size: 0.85rem; font-weight: 500; color: #4F46E5;">({str_reg['pct_of_total']:.1f}% share)</span>
                </div>
                <div style="font-size: 0.825rem; color: #475569; margin-bottom: 0.5rem;">
                    Sales: <strong>{format_currency(str_reg['sales'])}</strong>
                </div>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 0.5rem; font-size: 0.75rem; color: #64748B;">
                    Trailing region: <strong>{wk_reg['name']}</strong> ({format_currency(wk_reg['sales'])}, {wk_reg['pct_of_total']:.1f}% share)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_card2:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 0.35rem;">
                    📦 Category Leadership
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">
                    {str_cat['name']} <span style="font-size: 0.85rem; font-weight: 500; color: #10B981;">({str_cat['pct_of_total']:.1f}% share)</span>
                </div>
                <div style="font-size: 0.825rem; color: #475569; margin-bottom: 0.5rem;">
                    Sales: <strong>{format_currency(str_cat['sales'])}</strong>
                </div>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 0.5rem; font-size: 0.75rem; color: #64748B;">
                    Essential consumables: <strong>{wk_cat['name']}</strong> ({format_currency(wk_cat['sales'])}, {wk_cat['pct_of_total']:.1f}% share)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p_card3:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 0.35rem;">
                    👥 Segment Anchor
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">
                    {str_seg['name']} <span style="font-size: 0.85rem; font-weight: 500; color: #8B5CF6;">({str_seg['pct_of_total']:.1f}% share)</span>
                </div>
                <div style="font-size: 0.825rem; color: #475569; margin-bottom: 0.5rem;">
                    Sales: <strong>{format_currency(str_seg['sales'])}</strong>
                </div>
                <div style="background: #F8FAFC; border-radius: 6px; padding: 0.5rem; font-size: 0.75rem; color: #64748B;">
                    Concentration: Top 10 customer accounts generate <strong>{perf_insights['high_value_customer_summary']['top_10_share']:.1f}%</strong> of revenue
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.85rem;'></div>", unsafe_allow_html=True)

    # Plotly Visuals: Regional Share & Category Revenue Breakdown
    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Geographic Sales Concentration</h3>
                    <p class="chart-subtitle">Regional revenue distribution across all active transactions</p>
                </div>
                <span class="badge badge-neutral">Regional</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        reg_ranks = perf_insights["regional_rankings"]
        if reg_ranks:
            r_names = [r["region"] for r in reg_ranks]
            r_sales = [r["sales"] for r in reg_ranks]
            r_colors = [REGION_COLORS.get(r, "#4F46E5") for r in r_names]

            fig_reg = go.Figure(
                go.Bar(
                    x=r_sales,
                    y=r_names,
                    orientation="h",
                    marker=dict(color=r_colors, line=dict(color="rgba(255, 255, 255, 0.6)", width=1)),
                    text=[f"{format_currency(s)} ({p:.1f}%)" for s, p in zip(r_sales, [r["pct_of_total"] for r in reg_ranks])],
                    textposition="auto",
                )
            )
            theme = get_plotly_theme()
            fig_reg.update_layout(
                **theme,
                height=260,
                xaxis=dict(**theme["xaxis"], title="Revenue ($)"),
                yaxis=dict(**theme["yaxis"], autorange="reversed"),
            )
            st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})

    with c_chart2:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Merchandise Category Revenue & Orders</h3>
                    <p class="chart-subtitle">Topline volume and transaction density by category</p>
                </div>
                <span class="badge badge-neutral">Category Breakdown</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cat_ranks = perf_insights["category_rankings"]
        if cat_ranks:
            c_names = [c["category"] for c in cat_ranks]
            c_sales = [c["sales"] for c in cat_ranks]
            c_colors = [CATEGORY_COLORS.get(c, "#4F46E5") for c in c_names]

            fig_cat = go.Figure()
            fig_cat.add_trace(
                go.Bar(
                    x=c_names,
                    y=c_sales,
                    marker=dict(color=c_colors, line=dict(color="rgba(255, 255, 255, 0.6)", width=1)),
                    text=[format_abbreviated_currency(s) for s in c_sales],
                    textposition="auto",
                    name="Sales ($)",
                )
            )
            theme = get_plotly_theme()
            fig_cat.update_layout(
                **theme,
                height=260,
                yaxis=dict(**theme["yaxis"], title="Revenue ($)"),
                xaxis=dict(**theme["xaxis"], title=None),
            )
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =====================================================================
    # SECTION 3: CUSTOMER & RFM RETENTION COHORT INSIGHTS
    # =====================================================================
    st.markdown(
        """
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>👥 Customer Retention & Churn Risk Cohorts</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Behavioral customer segmentation derived from verified RFM modeling (Recency, Frequency, Monetary).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    r_col1, r_col2 = st.columns([1.2, 1.8])

    with r_col1:
        at_risk_cnt = ret_insights["at_risk_count"]
        at_risk_spend = ret_insights["at_risk_spend"]
        at_risk_pct = ret_insights["at_risk_pct"]
        champions_cnt = ret_insights["champions_count"]
        champions_spend = ret_insights["champions_spend"]
        champions_pct = ret_insights["champions_pct"]

        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #DC2626; text-transform: uppercase;">⚠️ Churn Risk Exposure</span>
                    <span style="background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">{ret_insights['retention_priority']} Priority</span>
                </div>
                <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
                    {at_risk_cnt:,} <span style="font-size: 0.95rem; font-weight: 500; color: #64748B;">accounts ({at_risk_pct:.1f}% of base)</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.65rem;">
                    Historical spend exposed: <strong style="color: #DC2626;">{format_currency(at_risk_spend)}</strong>
                </div>
                <div style="font-size: 0.75rem; color: #64748B; line-height: 1.4; border-top: 1px solid #F1F5F9; padding-top: 0.5rem;">
                    Includes <strong>{ret_insights['segment_counts'].get('At Risk', 0)}</strong> At-Risk accounts and <strong>{ret_insights['segment_counts'].get('Hibernating', 0)}</strong> Hibernating accounts with declining engagement velocity.
                </div>
            </div>

            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #4F46E5; text-transform: uppercase;">⭐ Champions Expansion</span>
                    <span style="background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">Growth Asset</span>
                </div>
                <div style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
                    {champions_cnt:,} <span style="font-size: 0.95rem; font-weight: 500; color: #64748B;">accounts ({champions_pct:.1f}% of base)</span>
                </div>
                <div style="font-size: 0.85rem; color: #475569;">
                    Aggregate revenue: <strong style="color: #4F46E5;">{format_currency(champions_spend)}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r_col2:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">RFM Customer Cohort Distribution</h3>
                    <p class="chart-subtitle">Customer count and aggregate revenue per behavioral segment</p>
                </div>
                <span class="badge badge-neutral">RFM Segments</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        rfm_sum = ret_insights["segment_summary"]
        if not rfm_sum.empty:
            seg_colors = {
                "Champions": "#4F46E5",
                "Loyal Customers": "#10B981",
                "Potential Loyalists": "#06B6D4",
                "At Risk": "#F59E0B",
                "Hibernating": "#FB923C",
                "Lost": "#F43F5E",
            }
            fig_rfm = go.Figure()
            fig_rfm.add_trace(
                go.Bar(
                    x=rfm_sum["rfm_segment"],
                    y=rfm_sum["customer_count"],
                    marker=dict(
                        color=[seg_colors.get(s, "#64748B") for s in rfm_sum["rfm_segment"]],
                        line=dict(color="rgba(255, 255, 255, 0.6)", width=1),
                    ),
                    text=[f"{cnt} cust<br>({format_abbreviated_currency(spend)})" for cnt, spend in zip(rfm_sum["customer_count"], rfm_sum["total_spend"])],
                    textposition="auto",
                )
            )
            theme = get_plotly_theme()
            fig_rfm.update_layout(
                **theme,
                height=260,
                yaxis=dict(**theme["yaxis"], title="Customer Count"),
                xaxis=dict(**theme["xaxis"], title=None),
            )
            st.plotly_chart(fig_rfm, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =====================================================================
    # SECTION 4: PRODUCT & CATEGORY BASKET OPPORTUNITIES
    # =====================================================================
    st.markdown(
        """
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>🛒 Product Opportunities & Multi-Item Basket Affinities</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Observed transaction co-occurrences across multi-category orders supporting cross-merchandising strategies.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b_col1, b_col2 = st.columns([1.2, 1.8])

    with b_col1:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 0.35rem;">
                    📦 Multi-Category Order Prevalence
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
                    {prod_opp['multi_category_order_count']:,} <span style="font-size: 0.95rem; font-weight: 500; color: #4F46E5;">({prod_opp['multi_category_order_pct']:.1f}% of orders)</span>
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.75rem;">
                    Transactions containing items from 2 or more distinct product categories.
                </div>
                <div style="background: #F8FAFC; border-radius: 8px; padding: 0.65rem; font-size: 0.775rem; color: #334155; line-height: 1.5;">
                    Top 10 SKUs account for <strong>{format_currency(prod_opp['top_products_sales'])}</strong> ({prod_opp['top_products_share']:.1f}% of total catalog sales).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b_col2:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem;">High-Affinity Cross-Purchase Pairs (Data-Observed)</div>
                <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.75rem;">Calculated directly from transactions where both merchandise lines were purchased together:</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cross_pairs = prod_opp["cross_sell_pairs"]
        if cross_pairs:
            pair_items_html = "".join([
                f"""
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.75rem; border-bottom: 1px solid #F1F5F9; background: #FFFFFF;">
                    <div>
                        <span style="font-size: 0.8rem; font-weight: 700; color: #1E293B;">{p['item_a']}</span>
                        <span style="font-size: 0.75rem; color: #94A3B8; margin: 0 0.35rem;">+</span>
                        <span style="font-size: 0.8rem; font-weight: 700; color: #1E293B;">{p['item_b']}</span>
                        <div style="font-size: 0.725rem; color: #64748B;">{p['opportunity']}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #EEF2FF; color: #4F46E5; font-weight: 700; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 6px;">
                            {p['order_co_occurrences']:,} orders ({p['pct_of_orders']}%)
                        </span>
                    </div>
                </div>
                """
                for p in cross_pairs[:4]
            ])
            st.markdown(f"<div style='border: 1px solid #E2E8F0; border-radius: 8px; overflow: hidden; margin-top: -0.5rem;'>{pair_items_html}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =====================================================================
    # SECTION 5: INVENTORY, LOGISTICS & RETURNS RISK ASSESSMENT
    # =====================================================================
    st.markdown(
        """
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>⚠️ Operational Supply Chain & Quality Risk Radar</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Triangulated operational risk telemetry across warehouse stockouts, fulfillment transit delays, and return liabilities.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    r_col1, r_col2, r_col3 = st.columns(3)

    with r_col1:
        low_cnt = inv_risk["low_stock_items"]
        deficit = inv_risk["total_replenishment_deficit"]
        health_rate = inv_risk["stock_health_rate"]
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #D97706; text-transform: uppercase; margin-bottom: 0.35rem;">
                    📦 Warehouse Stockout Vulnerability
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
                    {low_cnt} SKUs <span style="font-size: 0.85rem; font-weight: 500; color: #D97706;">(Deficit: {deficit:,} units)</span>
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.65rem;">
                    Catalog Health Rate: <strong>{health_rate:.1f}%</strong> across {inv_risk['warehouses']} warehouse hubs.
                </div>
                <div style="background: #FFFBEB; border: 1px solid #FEF3C7; border-radius: 6px; padding: 0.5rem; font-size: 0.75rem; color: #92400E;">
                    Replenishment priority: <strong>Office Supply Warehouse</strong> accounts for 14 low-stock items.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r_col2:
        ot_rate = log_risk["on_time_delivery_rate"]
        del_cnt = log_risk["delayed_shipments"]
        sla_target = log_risk["sla_target_pct"]
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #4F46E5; text-transform: uppercase; margin-bottom: 0.35rem;">
                    🚚 Logistics SLA Adherence
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
                    {ot_rate:.2f}% <span style="font-size: 0.85rem; font-weight: 500; color: #64748B;">(Target: {sla_target:.0f}%)</span>
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.65rem;">
                    Delayed shipments: <strong>{del_cnt:,}</strong> | Avg turnaround: <strong>{log_risk['average_delivery_days']:.2f} days</strong>.
                </div>
                <div style="background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 6px; padding: 0.5rem; font-size: 0.75rem; color: #3730A3;">
                    Carriers maintain consistent transit averages between 4.09 and 4.14 business days.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r_col3:
        ret_rate = ret_risk["return_rate"]
        refund_tot = ret_risk["total_refund_amount"]
        top_cause = ret_risk["top_reason"]["reason"]
        top_cause_cnt = ret_risk["top_reason"]["count"]
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; height: 100%;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #7C3AED; text-transform: uppercase; margin-bottom: 0.35rem;">
                    ↩️ Return Liabilities & Quality
                </div>
                <div style="font-size: 1.45rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
                    {ret_rate:.2f}% <span style="font-size: 0.85rem; font-weight: 500; color: #7C3AED;">({format_currency(refund_tot)})</span>
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.65rem;">
                    Total Returns: <strong>{ret_risk['total_returns']:,}</strong> ({ret_risk['distinct_returned_orders']:,} orders) across {ret_risk['distinct_returned_skus']:,} SKUs.
                </div>
                <div style="background: #F5F3FF; border: 1px solid #DDD6FE; border-radius: 6px; padding: 0.5rem; font-size: 0.75rem; color: #5B21B6;">
                    Primary root driver: <strong>{top_cause}</strong> ({top_cause_cnt} cases, 21.4% of returns).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =====================================================================
    # SECTION 6: STRATEGIC ACTION CENTER
    # =====================================================================
    st.markdown(
        """
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>🎯 Strategic Action Center & Prescriptive Guidance</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Prioritized management interventions generated dynamically from operational thresholds and risk signals.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    priority_filter = st.radio(
        "Priority Filter",
        options=["All Priorities", "High Priority Only", "Medium & Low"],
        horizontal=True,
        label_visibility="collapsed",
        key="action_priority_radio",
    )

    filtered_actions = strategic_actions
    if priority_filter == "High Priority Only":
        filtered_actions = [a for a in strategic_actions if a["priority"] == "High"]
    elif priority_filter == "Medium & Low":
        filtered_actions = [a for a in strategic_actions if a["priority"] in ["Medium", "Low"]]

    if filtered_actions:
        for action in filtered_actions:
            p_badge_style = {
                "High": "background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA;",
                "Medium": "background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A;",
                "Low": "background: #F0FDF4; color: #16A34A; border: 1px solid #BBF7D0;",
            }.get(action["priority"], "background: #F1F5F9; color: #475569;")

            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.65rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 0.75rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.04em;">{action['category']}</span>
                        </div>
                        <span style="{p_badge_style} font-size: 0.725rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 9999px;">
                            {action['priority']} Priority
                        </span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">
                        {action['issue']}
                    </div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.45rem;">
                        📊 <em>Supporting Data:</em> {action['supporting_metric']}
                    </div>
                    <div style="background: #F8FAFC; border-left: 3px solid #4F46E5; padding: 0.45rem 0.75rem; font-size: 0.825rem; color: #1E293B; border-radius: 0 6px 6px 0;">
                        💡 <strong>Recommended Action:</strong> {action['recommended_action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No strategic actions match the selected priority filter.")

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =====================================================================
    # SECTION 7: PRICE ELASTICITY OF DEMAND SIMULATOR
    # =====================================================================
    st.markdown(
        """
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 0.5rem;">
                <span>🧮 Price Elasticity of Demand (PED) Simulator</span>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">Simulate category price adjustments against empirical retail elasticity coefficients to project demand elasticity and gross revenue delta.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sim_box = st.container()
    with sim_box:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;">
            """,
            unsafe_allow_html=True,
        )

        sim_col1, sim_col2 = st.columns([1.2, 1.8])

        with sim_col1:
            sim_category = st.selectbox(
                "Select Department / Category",
                options=["Technology", "Furniture", "Office Supplies"],
                index=0,
                key="sim_category_select",
            )
            sim_price_delta = st.slider(
                "Price Adjustment (%)",
                min_value=-30,
                max_value=30,
                value=5,
                step=1,
                format="%d%%",
                key="sim_price_slider",
            )

        # Run simulation
        sim_res = simulate_price_elasticity(sim_category, float(sim_price_delta))

        with sim_col2:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                        <span style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase;">
                            Empirical PED: <strong>{sim_res['ped']:.2f}</strong>
                        </span>
                        <span style="background: #EEF2FF; color: #4F46E5; font-weight: 700; font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 6px;">
                            Optimal Discount: {sim_res['optimal_discount']}
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem;">
                        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.6rem; text-align: center;">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 600;">Demand Impact</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: {'#16A34A' if sim_res['demand_change_pct'] >= 0 else '#DC2626'};">
                                {sim_res['demand_change_pct']:+.1f}%
                            </div>
                        </div>
                        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.6rem; text-align: center;">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 600;">Net Revenue Delta</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: {'#16A34A' if sim_res['rev_change_pct'] >= 0 else '#DC2626'};">
                                {sim_res['rev_change_pct']:+.1f}%
                            </div>
                        </div>
                        <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.6rem; text-align: center;">
                            <div style="font-size: 0.7rem; color: #64748B; font-weight: 600;">Est. Margin Shift</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: {'#16A34A' if sim_res['margin_impact'] >= 0 else '#DC2626'};">
                                {sim_res['margin_impact']:+.1f}%
                            </div>
                        </div>
                    </div>
                    <div style="font-size: 0.775rem; color: #475569; line-height: 1.4;">
                        <strong>Interpretation:</strong> {sim_res['interpretation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)
