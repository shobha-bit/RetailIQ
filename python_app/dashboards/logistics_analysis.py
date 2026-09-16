import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from python_app.data.loader import RetailDataBundle
from python_app.analytics.retail_analytics import (
    calculate_logistics_kpis,
    calculate_carrier_summary,
    calculate_shipment_status_distribution,
    calculate_delivery_trend,
)
from python_app.utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
    format_days,
)
from python_app.utils.ui import (
    render_page_header,
    render_kpi_card,
    render_empty_state,
    get_plotly_theme,
)


def render_logistics_analysis(bundle: RetailDataBundle):
    """
    Render the Logistics & Carrier Performance Dashboard with transit telemetry,
    carrier SLA compliance scorecards, on-time delivery rates, and freight expenditure.
    """
    # 1. Page Header
    render_page_header(
        title="Logistics & Carrier Performance",
        description="Fulfillment tracking, carrier SLA compliance, transit time benchmarks, and shipping expenditure analysis.",
        badge_label="Logistics & Delivery",
        secondary_badge="SLA Performance",
    )

    # 2. Extract dynamic filter options from dataset
    trans_df = bundle.transportation.copy()

    # Dynamic carrier names from CSV (Blue Dart, Delhivery, Dhl, Fedex, Ups, Xpressbees)
    carrier_list = ["All"] + sorted(list(trans_df["carrier_name"].dropna().unique()))
    status_list = ["All"] + sorted(list(trans_df["shipment_status"].dropna().unique()))
    preset_list = ["All", "7D", "30D", "90D", "YTD", "1Y"]

    # Session State Initialization
    if "log_carrier" not in st.session_state:
        st.session_state["log_carrier"] = "All"
    if "log_status" not in st.session_state:
        st.session_state["log_status"] = "All"
    if "log_date_preset" not in st.session_state:
        st.session_state["log_date_preset"] = "All"
    if "log_search" not in st.session_state:
        st.session_state["log_search"] = ""

    # 3. Interactive Filter Bar
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">Carrier Breakdown</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1.5])

        with f_col1:
            selected_carrier = st.selectbox(
                "Carrier",
                options=carrier_list,
                index=carrier_list.index(st.session_state["log_carrier"]) if st.session_state["log_carrier"] in carrier_list else 0,
                key="log_select_carrier",
                label_visibility="collapsed",
            )
            st.session_state["log_carrier"] = selected_carrier

        with f_col2:
            selected_status = st.selectbox(
                "Shipment Status",
                options=status_list,
                index=status_list.index(st.session_state["log_status"]) if st.session_state["log_status"] in status_list else 0,
                key="log_select_status",
                label_visibility="collapsed",
            )
            st.session_state["log_status"] = selected_status

        with f_col3:
            selected_preset = st.selectbox(
                "Time Horizon",
                options=preset_list,
                index=preset_list.index(st.session_state["log_date_preset"]) if st.session_state["log_date_preset"] in preset_list else 0,
                key="log_select_preset",
                label_visibility="collapsed",
            )
            st.session_state["log_date_preset"] = selected_preset

        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["log_search"],
                placeholder="🔍 Search tracking number, order row ID, carrier...",
                key="log_input_search",
                label_visibility="collapsed",
            )
            st.session_state["log_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["log_carrier"] != "All"
                or st.session_state["log_status"] != "All"
                or st.session_state["log_date_preset"] != "All"
                or bool(st.session_state["log_search"].strip())
            )
            def _reset_log_filters():
                st.session_state["log_select_carrier"] = "All"
                st.session_state["log_select_status"] = "All"
                st.session_state["log_select_preset"] = "All"
                st.session_state["log_input_search"] = ""
                st.session_state["log_carrier"] = "All"
                st.session_state["log_status"] = "All"
                st.session_state["log_date_preset"] = "All"
                st.session_state["log_search"] = ""

            if st.button(
                "Reset Filters" if has_active_filters else "Clear",
                disabled=not has_active_filters,
                use_container_width=True,
                key="log_btn_reset",
                on_click=_reset_log_filters,
            ):
                st.rerun()

    # 4. Filter Transportation Data
    filtered_trans = trans_df.copy()

    if st.session_state["log_carrier"] != "All":
        filtered_trans = filtered_trans[filtered_trans["carrier_name"] == st.session_state["log_carrier"]]

    if st.session_state["log_status"] != "All":
        filtered_trans = filtered_trans[filtered_trans["shipment_status"] == st.session_state["log_status"]]

    if st.session_state["log_date_preset"] != "All" and "dispatch_date" in filtered_trans.columns:
        valid_dates = pd.to_datetime(filtered_trans["dispatch_date"].dropna())
        if not valid_dates.empty:
            max_d = valid_dates.max()
            preset = st.session_state["log_date_preset"]
            if preset == "7D":
                min_d = max_d - pd.Timedelta(days=7)
            elif preset == "30D":
                min_d = max_d - pd.Timedelta(days=30)
            elif preset == "90D":
                min_d = max_d - pd.Timedelta(days=90)
            elif preset == "YTD":
                min_d = pd.Timestamp(year=max_d.year, month=1, day=1)
            elif preset == "1Y":
                min_d = max_d - pd.Timedelta(days=365)
            else:
                min_d = valid_dates.min()
            filtered_trans = filtered_trans[(pd.to_datetime(filtered_trans["dispatch_date"]) >= min_d) & (pd.to_datetime(filtered_trans["dispatch_date"]) <= max_d)]

    if st.session_state["log_search"].strip():
        q = st.session_state["log_search"].strip().lower()
        mask = (
            filtered_trans["carrier_name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_trans["tracking_number"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_trans["order_row_id"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_trans["shipment_status"].astype(str).str.lower().str.contains(q, na=False)
        )
        filtered_trans = filtered_trans[mask]

    # 5. Dynamic KPI Calculations (Using Phase 2 Engine)
    kpis = calculate_logistics_kpis(filtered_trans)
    avg_transit_days = kpis["average_delivery_days"]
    shipment_count = kpis["shipment_count"]
    delivered_count = kpis["delivered_shipments"]
    delayed_count = kpis["delayed_shipments"]
    otd_rate = kpis["on_time_delivery_rate"]
    avg_cost = float(filtered_trans["delivery_cost"].mean()) if "delivery_cost" in filtered_trans.columns and not filtered_trans.empty else 0.0

    # 6. Render KPI Grid (5 Cards)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        render_kpi_card(
            title="Total Shipments",
            value=format_number(shipment_count),
            icon="🚚",
            icon_color_class="kpi-icon-blue",
            subtitle="Parcels in fulfillment network",
        )

    with kpi_col2:
        render_kpi_card(
            title="On-Time Delivery Rate",
            value=format_percentage(otd_rate),
            icon="🎯",
            icon_color_class="kpi-icon-green",
            delta="95.0% target SLA",
            delta_positive=otd_rate >= 90.0,
            subtitle=f"{delivered_count:,} completed arrivals",
        )

    with kpi_col3:
        render_kpi_card(
            title="Avg Transit Time",
            value=format_days(avg_transit_days),
            icon="⏱️",
            icon_color_class="kpi-icon-cyan",
            subtitle="Dispatch to delivery duration",
        )

    with kpi_col4:
        render_kpi_card(
            title="Delayed Shipments",
            value=format_number(delayed_count),
            icon="⚠️",
            icon_color_class="kpi-icon-amber",
            delta=f"{round(delayed_count / max(shipment_count, 1) * 100, 1)}% exception rate" if delayed_count > 0 else "Zero exceptions",
            delta_positive=delayed_count == 0,
            subtitle="SLA delivery breach alerts",
        )

    with kpi_col5:
        render_kpi_card(
            title="Avg Shipping Cost",
            value=format_currency(avg_cost),
            icon="💵",
            icon_color_class="kpi-icon-purple",
            subtitle="Mean carrier freight per order",
        )

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 7. Check for Empty State
    if filtered_trans.empty:
        render_empty_state("No logistics records match the active filter criteria. Try resetting filters.")
        return

    plotly_theme = get_plotly_theme()

    # Analytical breakdowns
    carrier_summary = calculate_carrier_summary(filtered_trans)
    status_summary = calculate_shipment_status_distribution(filtered_trans)
    trend_summary = calculate_delivery_trend(filtered_trans)

    # =========================================================================
    # ROW 1: Carrier SLA On-Time Performance & Status Distribution
    # =========================================================================
    row1_left, row1_right = st.columns([2, 1])

    with row1_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Carrier On-Time SLA Compliance Rate</h3>
                    <p class="chart-subtitle">Real-time on-time fulfillment rate across active logistics carriers</p>
                </div>
                <span class="badge badge-primary">SLA Benchmark</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not carrier_summary.empty:
            bar_colors = ["#10B981" if r >= 90.0 else "#F59E0B" for r in carrier_summary["on_time_rate"]]
            fig_otd = go.Figure()
            fig_otd.add_trace(
                go.Bar(
                    x=carrier_summary["carrier_name"],
                    y=carrier_summary["on_time_rate"],
                    marker_color=bar_colors,
                    hovertemplate="<b>%{x}</b><br>On-Time Rate: %{y:.2f}%<br>Total Shipments: %{customdata[0]:,}<br>Delayed: %{customdata[1]}<extra></extra>",
                    customdata=carrier_summary[["total_shipments", "delayed"]].values,
                )
            )
            # Add 90% SLA Target line
            fig_otd.add_hline(
                y=90.0,
                line_dash="dash",
                line_color="#EF4444",
                annotation_text="90% Target SLA",
                annotation_position="bottom right",
                annotation_font_size=11,
            )
            fig_otd.update_layout(
                **plotly_theme,
                height=300,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    range=[80, 100],
                    ticksuffix="%",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_otd, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No carrier data available.")

    with row1_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Shipment Status Distribution</h3>
                    <p class="chart-subtitle">Fulfillment stage breakdown across all parcels</p>
                </div>
                <span class="badge badge-purple">Pipeline</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not status_summary.empty:
            status_colors = {
                "Delivered": "#10B981",
                "In Transit": "#4F46E5",
                "Shipped": "#8B5CF6",
                "Pending": "#F59E0B",
            }
            colors = [status_colors.get(s, "#64748B") for s in status_summary["shipment_status"]]

            fig_status = go.Figure(
                go.Pie(
                    labels=status_summary["shipment_status"],
                    values=status_summary["count"],
                    hole=0.6,
                    marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="<b>%{label}</b><br>Parcels: %{value:,}<br>Share: %{percent}<extra></extra>",
                    textinfo="label+percent",
                    textposition="inside",
                    textfont=dict(size=11, color="#FFFFFF"),
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

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 2: Monthly Delivery Trend & Carrier Transit Duration Comparison
    # =========================================================================
    row2_left, row2_right = st.columns([1, 1])

    with row2_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Fulfillment Velocity & On-Time Trajectory</h3>
                    <p class="chart-subtitle">Monthly shipment volume and SLA fulfillment reliability trajectory</p>
                </div>
                <span class="badge badge-primary">Monthly Trajectory</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not trend_summary.empty:
            fig_trend = go.Figure()
            # Bar for shipments
            fig_trend.add_trace(
                go.Bar(
                    x=trend_summary["label"],
                    y=trend_summary["shipments"],
                    name="Shipments",
                    marker_color="#CBD5E1",
                    hovertemplate="<b>%{x}</b><br>Shipments: %{y:,}<extra></extra>",
                    yaxis="y",
                )
            )
            # Line for On-Time Rate
            fig_trend.add_trace(
                go.Scatter(
                    x=trend_summary["label"],
                    y=trend_summary["on_time_rate"],
                    name="On-Time Rate (%)",
                    mode="lines+markers",
                    line=dict(color="#10B981", width=2.5),
                    marker=dict(size=4),
                    hovertemplate="<b>%{x}</b><br>On-Time Rate: %{y:.1f}%<extra></extra>",
                    yaxis="y2",
                )
            )
            fig_trend.update_layout(
                **plotly_theme,
                height=290,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    title="Shipments",
                    showgrid=False,
                ),
                yaxis2=dict(
                    title="On-Time %",
                    overlaying="y",
                    side="right",
                    range=[75, 100],
                    showgrid=True,
                    gridcolor="#F1F5F9",
                    ticksuffix="%",
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
            render_empty_state("No trend data available.")

    with row2_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Carrier Transit Days & Freight Cost</h3>
                    <p class="chart-subtitle">Mean transit duration and average parcel freight expenditure by carrier</p>
                </div>
                <span class="badge badge-neutral">Freight Efficiency</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not carrier_summary.empty:
            fig_transit = go.Figure()
            fig_transit.add_trace(
                go.Bar(
                    x=carrier_summary["carrier_name"],
                    y=carrier_summary["avg_transit_days"],
                    name="Transit Days",
                    marker_color="#4F46E5",
                    hovertemplate="<b>%{x}</b><br>Avg Transit: %{y:.2f} days<extra></extra>",
                )
            )
            fig_transit.update_layout(
                **plotly_theme,
                height=290,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    title="Days",
                    range=[0, 6],
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_transit, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No transit data available.")

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 3: Carrier Partner Scorecard Table
    # =========================================================================
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Carrier Partner SLA Scorecard</h3>
                <p class="chart-subtitle">Real carrier performance benchmarks derived from operational fulfillment telemetry</p>
            </div>
            <span class="badge badge-primary">Carrier Telemetry</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not carrier_summary.empty:
        display_scorecard = carrier_summary.copy()
        display_scorecard["on_time_fmt"] = display_scorecard["on_time_rate"].apply(lambda r: f"{r:.2f}%")
        display_scorecard["transit_fmt"] = display_scorecard["avg_transit_days"].apply(lambda d: f"{d:.2f} days")
        display_scorecard["cost_fmt"] = display_scorecard["avg_shipping_cost"].apply(lambda c: f"${c:.2f}")
        display_scorecard["sla_status"] = display_scorecard["on_time_rate"].apply(
            lambda r: "🟢 Exceeds SLA" if r >= 90.0 else "🟡 Attention Required"
        )

        table_cols = [
            "carrier_name", "total_shipments", "delivered", "delayed",
            "on_time_fmt", "transit_fmt", "cost_fmt", "sla_status"
        ]
        col_renames = {
            "carrier_name": "Carrier",
            "total_shipments": "Total Shipments",
            "delivered": "Delivered",
            "delayed": "Delayed",
            "on_time_fmt": "On-Time Rate",
            "transit_fmt": "Avg Transit",
            "cost_fmt": "Avg Freight Cost",
            "sla_status": "SLA Compliance",
        }

        # Action Bar & CSV export
        t_col1, t_col2 = st.columns([3.5, 1.5])
        with t_col1:
            st.caption(f"Evaluating {len(display_scorecard)} carrier partners across {shipment_count:,} fulfillment orders")
        with t_col2:
            csv_data = display_scorecard[table_cols].rename(columns=col_renames).to_csv(index=False)
            st.download_button(
                label="📥 Export Carrier Scorecard CSV",
                data=csv_data,
                file_name="carrier_logistics_scorecard.csv",
                mime="text/csv",
                use_container_width=True,
                key="log_download_csv",
            )

        st.dataframe(
            display_scorecard[table_cols].rename(columns=col_renames),
            use_container_width=True,
            hide_index=True,
        )
    else:
        render_empty_state("No carrier scorecard records available.")

