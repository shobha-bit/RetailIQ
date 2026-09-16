import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from python_app.data.loader import RetailDataBundle
from python_app.analytics.retail_analytics import (
    RetailFilters,
    filter_retail_data,
    calculate_customer_rfm,
    calculate_rfm_segment_summary,
    calculate_retail_kpis,
    get_filter_options,
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

SEGMENT_COLORS = {
    "Champions": "#10B981",
    "Loyal Customers": "#4F46E5",
    "Potential Loyalists": "#8B5CF6",
    "At Risk": "#F59E0B",
    "Hibernating": "#EC4899",
    "Lost": "#64748B",
}


def render_customer_analysis(bundle: RetailDataBundle):
    """
    Render the Customer Intelligence & RFM Segmentation Dashboard with
    behavioral clustering, lifetime value modeling, cohort scatter matrix,
    interactive retention triggers, and individual customer profiles.
    """
    # 1. Page Header
    render_page_header(
        title="Customer Intelligence & RFM Segmentation",
        description="Behavioral clustering based on Recency, Frequency, and Monetary quintiles to optimize retention and lifetime value (CLV).",
        badge_label="Customer Analytics",
        secondary_badge="RFM Quintiles",
    )

    # 2. Extract dynamic filter options
    filter_opts = get_filter_options(bundle)
    regions = ["All"] + filter_opts["regions"]
    categories = ["All"] + filter_opts["categories"]
    segments = ["All"] + filter_opts["segments"]
    date_presets = ["All", "7D", "30D", "90D", "YTD", "1Y"]

    # Initialize session state for filters
    if "cust_date_preset" not in st.session_state:
        st.session_state["cust_date_preset"] = "All"
    if "cust_region" not in st.session_state:
        st.session_state["cust_region"] = "All"
    if "cust_category" not in st.session_state:
        st.session_state["cust_category"] = "All"
    if "cust_segment" not in st.session_state:
        st.session_state["cust_segment"] = "All"
    if "cust_search" not in st.session_state:
        st.session_state["cust_search"] = ""
    if "cust_rfm_cohort" not in st.session_state:
        st.session_state["cust_rfm_cohort"] = "All"
    if "targeted_customer" not in st.session_state:
        st.session_state["targeted_customer"] = None

    # 3. Interactive Filter Bar
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">RFM Cohorts</span>
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
                default=st.session_state["cust_date_preset"],
                key="cust_pills_date_preset",
                label_visibility="collapsed",
            )
            if selected_date:
                st.session_state["cust_date_preset"] = selected_date

        with f_col2:
            selected_region = st.selectbox(
                "Region",
                options=regions,
                index=regions.index(st.session_state["cust_region"]) if st.session_state["cust_region"] in regions else 0,
                key="cust_select_region",
                label_visibility="collapsed",
            )
            st.session_state["cust_region"] = selected_region

        with f_col3:
            selected_category = st.selectbox(
                "Category",
                options=categories,
                index=categories.index(st.session_state["cust_category"]) if st.session_state["cust_category"] in categories else 0,
                key="cust_select_category",
                label_visibility="collapsed",
            )
            st.session_state["cust_category"] = selected_category

        with f_col4:
            selected_segment = st.selectbox(
                "Segment",
                options=segments,
                index=segments.index(st.session_state["cust_segment"]) if st.session_state["cust_segment"] in segments else 0,
                key="cust_select_segment",
                label_visibility="collapsed",
            )
            st.session_state["cust_segment"] = selected_segment

        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["cust_search"],
                placeholder="🔍 Search customer name, customer ID, email, or city...",
                key="cust_input_search",
                label_visibility="collapsed",
            )
            st.session_state["cust_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["cust_date_preset"] != "All"
                or st.session_state["cust_region"] != "All"
                or st.session_state["cust_category"] != "All"
                or st.session_state["cust_segment"] != "All"
                or st.session_state["cust_rfm_cohort"] != "All"
                or bool(st.session_state["cust_search"].strip())
            )
            def _reset_cust_filters():
                st.session_state["cust_pills_date_preset"] = "All"
                st.session_state["cust_select_region"] = "All"
                st.session_state["cust_select_category"] = "All"
                st.session_state["cust_select_segment"] = "All"
                st.session_state["cust_input_search"] = ""
                st.session_state["cust_date_preset"] = "All"
                st.session_state["cust_region"] = "All"
                st.session_state["cust_category"] = "All"
                st.session_state["cust_segment"] = "All"
                st.session_state["cust_rfm_cohort"] = "All"
                st.session_state["cust_search"] = ""

            if st.button(
                "Reset Filters" if has_active_filters else "Clear",
                disabled=not has_active_filters,
                use_container_width=True,
                key="cust_btn_reset",
                on_click=_reset_cust_filters,
            ):
                st.rerun()

    # 4. Filter Orders & Run RFM Engine
    active_filters = RetailFilters(
        date_range=st.session_state["cust_date_preset"] if st.session_state["cust_date_preset"] != "All" else None,
        region=st.session_state["cust_region"] if st.session_state["cust_region"] != "All" else None,
        category=st.session_state["cust_category"] if st.session_state["cust_category"] != "All" else None,
        segment=st.session_state["cust_segment"] if st.session_state["cust_segment"] != "All" else None,
        search_query=st.session_state["cust_search"].strip() or None,
    )

    filtered_bundle = filter_retail_data(bundle, active_filters)

    # Calculate RFM dataframe
    rfm_df = calculate_customer_rfm(
        orders=filtered_bundle.orders,
        customers=bundle.customers,
        products=bundle.products,
    )

    # Also compute master retail KPIs for baseline comparison
    master_kpis = calculate_retail_kpis(filtered_bundle, active_filters)

    # 5. Dynamic RFM Stats (Derived strictly from real data)
    total_customers = len(rfm_df)
    champions = rfm_df[rfm_df["rfm_segment"] == "Champions"]
    champions_count = len(champions)
    champions_spend = champions["monetary_value"].sum()

    at_risk = rfm_df[rfm_df["rfm_segment"].isin(["At Risk", "Hibernating"])]
    at_risk_count = len(at_risk)
    revenue_at_risk = at_risk["monetary_value"].sum()

    total_spend = rfm_df["monetary_value"].sum()
    avg_clv = round(total_spend / total_customers, 2) if total_customers > 0 else 0.0

    # 6. Customer KPI Grid (5 High-Contrast Cards matching reference)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        render_kpi_card(
            title="Active Customer Base",
            value=format_number(total_customers),
            icon="👥",
            icon_color_class="kpi-icon-blue",
            subtitle="Unique retail accounts verified",
        )

    with kpi_col2:
        render_kpi_card(
            title="Champions Cohort",
            value=format_number(champions_count),
            icon="🏆",
            icon_color_class="kpi-icon-green",
            delta=f"{champions_count/total_customers*100:.1f}% base" if total_customers > 0 else None,
            delta_positive=True,
            subtitle=f"{format_currency(champions_spend)} revenue contribution",
        )

    with kpi_col3:
        render_kpi_card(
            title="Average CLV",
            value=format_currency(avg_clv),
            icon="🤝",
            icon_color_class="kpi-icon-purple",
            subtitle="Customer Lifetime Value baseline",
        )

    with kpi_col4:
        render_kpi_card(
            title="At-Risk Customers",
            value=format_number(at_risk_count),
            icon="⚠️",
            icon_color_class="kpi-icon-amber",
            subtitle="Dormant > 90 purchase days",
        )

    with kpi_col5:
        render_kpi_card(
            title="Revenue at Churn Risk",
            value=format_currency(revenue_at_risk),
            icon="📉",
            icon_color_class="kpi-icon-amber",
            subtitle="Target volume for win-back",
        )

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 7. RFM Segment Distribution Summary
    segment_summary = calculate_rfm_segment_summary(rfm_df)

    # Segment Quick-Filter Pills
    st.markdown(
        """
        <div style="font-size: 0.8rem; font-weight: 700; color: #4F46E5; margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.04em;">
            Filter by Behavioral Cohort:
        </div>
        """,
        unsafe_allow_html=True,
    )

    cohort_options = ["All"]
    cohort_counts = {"All": total_customers}
    if not segment_summary.empty:
        for _, row in segment_summary.iterrows():
            seg_name = str(row["rfm_segment"])
            cohort_options.append(seg_name)
            cohort_counts[seg_name] = int(row["customer_count"])

    selected_cohort_pill = st.pills(
        "RFM Cohorts",
        options=cohort_options,
        default=st.session_state["cust_rfm_cohort"],
        key="cust_rfm_cohort_pills",
        label_visibility="collapsed",
    )
    if selected_cohort_pill and selected_cohort_pill != st.session_state["cust_rfm_cohort"]:
        st.session_state["cust_rfm_cohort"] = selected_cohort_pill
        st.rerun()

    # Slice RFM list based on selected cohort pill
    filtered_rfm = rfm_df.copy()
    if st.session_state["cust_rfm_cohort"] != "All":
        filtered_rfm = filtered_rfm[filtered_rfm["rfm_segment"] == st.session_state["cust_rfm_cohort"]]

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 8. Visual Analytics (Plotly Charts)
    plotly_theme = get_plotly_theme()
    row1_left, row1_right = st.columns([1, 2])

    with row1_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Customer Cluster Distribution</h3>
                    <p class="chart-subtitle">Customer head-count grouped by behavioral segment</p>
                </div>
                <span class="badge badge-purple">Clustering</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not segment_summary.empty:
            bar_colors = [SEGMENT_COLORS.get(str(s), "#4F46E5") for s in segment_summary["rfm_segment"]]
            fig_cluster = go.Figure(
                go.Bar(
                    y=segment_summary["rfm_segment"],
                    x=segment_summary["customer_count"],
                    orientation="h",
                    marker=dict(color=bar_colors),
                    hovertemplate="<b>%{y}</b><br>Headcount: %{x:,} Customers<br>Total Spend: $%{customdata[0]:,.2f}<br>Share: %{customdata[1]:.1f}%<extra></extra>",
                    customdata=segment_summary[["total_spend", "pct_of_customers"]].values,
                )
            )
            fig_cluster.update_layout(
                **plotly_theme,
                height=320,
                xaxis=dict(
                    **plotly_theme["xaxis"],
                    title="Customer Headcount",
                ),
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    autorange="reversed",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_cluster, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No RFM segment records available.")

    with row1_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">RFM Behavioral Matrix (Recency vs Spend)</h3>
                    <p class="chart-subtitle">Bubble size represents order frequency; X-axis represents recency days</p>
                </div>
                <span class="badge badge-primary">Matrix Plot</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not rfm_df.empty:
            scatter_sample = rfm_df.copy()

            fig_scatter = go.Figure()
            for seg in SEGMENT_COLORS.keys():
                seg_sub = scatter_sample[scatter_sample["rfm_segment"] == seg]
                if seg_sub.empty:
                    continue
                sizes = seg_sub["frequency"].clip(lower=1, upper=25) * 1.5 + 4

                fig_scatter.add_trace(
                    go.Scatter(
                        x=seg_sub["recency_days"],
                        y=seg_sub["monetary_value"],
                        mode="markers",
                        name=seg,
                        marker=dict(
                            size=sizes,
                            color=SEGMENT_COLORS.get(seg, "#4F46E5"),
                            opacity=0.75,
                            line=dict(color="#FFFFFF", width=0.75),
                        ),
                        hovertemplate="<b>%{customdata[0]}</b><br>Segment: " + seg + "<br>Recency: %{x} days<br>Spend: $%{y:,.2f}<br>Orders: %{customdata[1]}<extra></extra>",
                        customdata=seg_sub[["customer_name", "frequency"]].values,
                    )
                )

            fig_scatter.update_layout(
                **plotly_theme,
                height=320,
                xaxis=dict(
                    **plotly_theme["xaxis"],
                    title="Recency (Days Since Last Order)",
                ),
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    title="Lifetime Spend ($)",
                    tickprefix="$",
                    tickformat="~s",
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=10),
                ),
            )
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No customer scatter records available.")

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 9. Segment Breakdown Summary Table
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">RFM Strategic Cohort Breakdown</h3>
                <p class="chart-subtitle">Aggregate commercial contributions and churn risk calibration by behavioral cluster</p>
            </div>
            <span class="badge badge-neutral">Portfolio Health</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not segment_summary.empty:
        summary_display = segment_summary.copy()
        summary_display["customer_count_fmt"] = summary_display["customer_count"].apply(lambda x: f"{x:,}")
        summary_display["total_spend_fmt"] = summary_display["total_spend"].apply(lambda x: f"${x:,.2f}")
        summary_display["avg_spend_fmt"] = summary_display["avg_spend"].apply(lambda x: f"${x:,.2f}")
        summary_display["avg_freq_fmt"] = summary_display["avg_frequency"].apply(lambda x: f"{x:.1f} orders")
        summary_display["avg_rec_fmt"] = summary_display["avg_recency_days"].apply(lambda x: f"{x:.0f} days")
        summary_display["churn_risk_fmt"] = summary_display["avg_churn_prob"].apply(lambda x: f"{x:.1f}%")
        summary_display["share_fmt"] = summary_display["pct_of_customers"].apply(lambda x: f"{x:.1f}%")

        table_cols = [
            "rfm_segment", "customer_count_fmt", "share_fmt", "total_spend_fmt",
            "avg_spend_fmt", "avg_freq_fmt", "avg_rec_fmt", "churn_risk_fmt"
        ]
        table_renames = {
            "rfm_segment": "Behavioral Segment",
            "customer_count_fmt": "Headcount",
            "share_fmt": "% of Base",
            "total_spend_fmt": "Total Revenue",
            "avg_spend_fmt": "Avg CLV",
            "avg_freq_fmt": "Mean Frequency",
            "avg_rec_fmt": "Mean Recency",
            "churn_risk_fmt": "Avg Churn Risk",
        }

        st.dataframe(
            summary_display[table_cols].rename(columns=table_renames),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 10. Automated Re-Engagement Campaign Trigger Banner
    if st.session_state["targeted_customer"]:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1px solid #A7F3D0; border-radius: 12px; padding: 0.85rem 1.25rem; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; color: #065F46;">
                <span style="font-size: 1.25rem;">✅</span>
                <div style="font-size: 0.85rem;">
                    <b>Automated Re-engagement Triggered:</b> Personalized retention promotion code and win-back email sequence successfully dispatched to customer <b>{st.session_state['targeted_customer']}</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 11. Individual Customer Profiles Table
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Customer RFM Profiles & Retention Matrix</h3>
                <p class="chart-subtitle">Individual customer RFM scores, segment categorizations, and churn risk probability</p>
            </div>
            <span class="badge badge-neutral">Client Profiles</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not filtered_rfm.empty:
        display_rfm = filtered_rfm.sort_values(by="monetary_value", ascending=False).copy()
        display_rfm["spend_fmt"] = display_rfm["monetary_value"].apply(lambda s: f"${s:,.2f}")
        display_rfm["recency_fmt"] = display_rfm["recency_days"].apply(lambda r: f"{r}d ago")
        display_rfm["rfm_score_str"] = display_rfm.apply(lambda r: f"{r['r_score']}-{r['f_score']}-{r['m_score']}", axis=1)
        display_rfm["churn_risk_fmt"] = (display_rfm["churn_probability"] * 100).apply(lambda c: f"{c:.0f}%")

        # Table columns
        rfm_cols = [
            "customer_name", "customer_email", "rfm_segment", "recency_fmt",
            "frequency", "spend_fmt", "rfm_score_str", "preferred_category", "churn_risk_fmt"
        ]
        rfm_renames = {
            "customer_name": "Customer Name",
            "customer_email": "Email",
            "rfm_segment": "Segment",
            "recency_fmt": "Recency",
            "frequency": "Orders",
            "spend_fmt": "Lifetime Spend",
            "rfm_score_str": "R-F-M Score",
            "preferred_category": "Favorite Category",
            "churn_risk_fmt": "Churn Risk",
        }

        # Action Bar & CSV export
        t_col1, t_col2 = st.columns([3.5, 1.5])
        with t_col1:
            st.caption(f"Displaying {min(len(display_rfm), 50)} of {len(display_rfm):,} customer profiles matching active criteria")
        with t_col2:
            csv_data = display_rfm[rfm_cols].rename(columns=rfm_renames).to_csv(index=False)
            st.download_button(
                label="📥 Export RFM Customer List",
                data=csv_data,
                file_name="customer_rfm_segmentation.csv",
                mime="text/csv",
                use_container_width=True,
                key="cust_download_csv",
            )

        st.dataframe(
            display_rfm[rfm_cols].head(50).rename(columns=rfm_renames),
            use_container_width=True,
            hide_index=True,
        )

        # Re-engagement Campaign Trigger Section
        with st.expander("Launch Retention Campaign for At-Risk / Hibernating Customers"):
            at_risk_customers = display_rfm[display_rfm["rfm_segment"].isin(["At Risk", "Hibernating", "Lost"])]
            if not at_risk_customers.empty:
                cust_names = at_risk_customers["customer_name"].tolist()
                sel_cust = st.selectbox("Select Customer to Re-engage", options=cust_names, key="sel_reengage_cust")
                if st.button("Dispatch Personalized Win-Back Campaign", key="btn_trigger_reengage"):
                    st.session_state["targeted_customer"] = sel_cust
                    st.rerun()
            else:
                st.info("No At-Risk or Hibernating customers in the currently filtered segment.")
    else:
        render_empty_state("No customer records match the active criteria.")
