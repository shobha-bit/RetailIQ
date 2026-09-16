import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

from python_app.data.loader import RetailDataBundle
from python_app.analytics.retail_analytics import (
    calculate_inventory_kpis,
    calculate_stock_by_warehouse,
    calculate_stock_status_distribution,
    calculate_inventory_by_category,
    calculate_low_stock_products,
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


def render_inventory_analysis(bundle: RetailDataBundle):
    """
    Render the Inventory Analysis Dashboard with real-time stock balances,
    warehouse capacity utilization, stockout alerts, and replenishment controls.
    """
    # 1. Page Header
    render_page_header(
        title="Inventory Optimization & Supply Chain",
        description="Continuous stock monitoring, safety stock buffers, economic reorder thresholds, and warehouse capacity utilization.",
        badge_label="Inventory Management",
        secondary_badge="Stock Monitoring",
    )

    # 2. Extract dynamic filter options from datasets
    inv_df = bundle.inventory.copy()
    prod_df = bundle.products.copy() if bundle.products is not None else pd.DataFrame()

    warehouse_list = ["All"] + sorted(list(inv_df["warehouse_name"].dropna().unique()))
    stock_status_list = ["All", "In Stock", "Low Stock"]
    category_list = ["All"] + (sorted(list(prod_df["category"].dropna().unique())) if not prod_df.empty else [])

    # Session State Initialization
    if "inv_warehouse" not in st.session_state:
        st.session_state["inv_warehouse"] = "All"
    if "inv_status" not in st.session_state:
        st.session_state["inv_status"] = "All"
    if "inv_category" not in st.session_state:
        st.session_state["inv_category"] = "All"
    if "inv_search" not in st.session_state:
        st.session_state["inv_search"] = ""
    if "reordered_skus" not in st.session_state:
        st.session_state["reordered_skus"] = set()
    if "latest_reordered_sku" not in st.session_state:
        st.session_state["latest_reordered_sku"] = None

    # 3. Interactive Filter Bar
    with st.container():
        st.markdown(
            """
            <div class="filter-container-card">
                <div class="filter-header-title">
                    <span>Filters</span>
                    <span style="font-size: 0.7rem; font-weight: 500; color: #64748B;">Facility Breakdown</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 1.5])

        with f_col1:
            selected_wh = st.selectbox(
                "Warehouse",
                options=warehouse_list,
                index=warehouse_list.index(st.session_state["inv_warehouse"]) if st.session_state["inv_warehouse"] in warehouse_list else 0,
                key="inv_select_warehouse",
                label_visibility="collapsed",
            )
            st.session_state["inv_warehouse"] = selected_wh

        with f_col2:
            selected_status = st.selectbox(
                "Stock Status",
                options=stock_status_list,
                index=stock_status_list.index(st.session_state["inv_status"]) if st.session_state["inv_status"] in stock_status_list else 0,
                key="inv_select_status",
                label_visibility="collapsed",
            )
            st.session_state["inv_status"] = selected_status

        with f_col3:
            selected_cat = st.selectbox(
                "Category",
                options=category_list,
                index=category_list.index(st.session_state["inv_category"]) if st.session_state["inv_category"] in category_list else 0,
                key="inv_select_category",
                label_visibility="collapsed",
            )
            st.session_state["inv_category"] = selected_cat

        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            search_query = st.text_input(
                "Search",
                value=st.session_state["inv_search"],
                placeholder="🔍 Search SKU, product name, warehouse, location...",
                key="inv_input_search",
                label_visibility="collapsed",
            )
            st.session_state["inv_search"] = search_query

        with s_col2:
            has_active_filters = (
                st.session_state["inv_warehouse"] != "All"
                or st.session_state["inv_status"] != "All"
                or st.session_state["inv_category"] != "All"
                or bool(st.session_state["inv_search"].strip())
            )
            def _reset_inv_filters():
                st.session_state["inv_select_warehouse"] = "All"
                st.session_state["inv_select_status"] = "All"
                st.session_state["inv_select_category"] = "All"
                st.session_state["inv_input_search"] = ""
                st.session_state["inv_warehouse"] = "All"
                st.session_state["inv_status"] = "All"
                st.session_state["inv_category"] = "All"
                st.session_state["inv_search"] = ""

            if st.button(
                "Reset Filters" if has_active_filters else "Clear",
                disabled=not has_active_filters,
                use_container_width=True,
                key="inv_btn_reset",
                on_click=_reset_inv_filters,
            ):
                st.rerun()

    # 4. Filter Inventory Data
    filtered_inv = inv_df.copy()

    # Merge category/name metadata if available for filtering
    if not prod_df.empty:
        prod_meta = prod_df[["product_id", "product_name", "category"]].drop_duplicates(subset=["product_id"])
        filtered_inv = filtered_inv.merge(prod_meta, on="product_id", how="left")
        filtered_inv["product_name"] = filtered_inv["product_name"].fillna(filtered_inv["product_id"])
        filtered_inv["category"] = filtered_inv["category"].fillna("General")
    else:
        filtered_inv["product_name"] = filtered_inv["product_id"]
        filtered_inv["category"] = "General"

    if st.session_state["inv_warehouse"] != "All":
        filtered_inv = filtered_inv[filtered_inv["warehouse_name"] == st.session_state["inv_warehouse"]]

    if st.session_state["inv_status"] != "All":
        filtered_inv = filtered_inv[filtered_inv["stock_status"] == st.session_state["inv_status"]]

    if st.session_state["inv_category"] != "All":
        filtered_inv = filtered_inv[filtered_inv["category"] == st.session_state["inv_category"]]

    if st.session_state["inv_search"].strip():
        q = st.session_state["inv_search"].strip().lower()
        mask = (
            filtered_inv["product_id"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_inv["product_name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_inv["warehouse_name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_inv["warehouse_location"].astype(str).str.lower().str.contains(q, na=False)
        )
        filtered_inv = filtered_inv[mask]

    # 5. Dynamic KPI Calculations (Using Phase 2 Engine)
    kpis = calculate_inventory_kpis(filtered_inv)
    total_stock = kpis["total_stock"]
    inventory_items = kpis["inventory_items"]
    low_stock_items = kpis["low_stock_items"]
    warehouses = kpis["warehouses"]
    in_stock_items = inventory_items - low_stock_items
    health_rate = (in_stock_items / inventory_items * 100.0) if inventory_items > 0 else 100.0
    avg_stock_per_sku = round(total_stock / inventory_items, 1) if inventory_items > 0 else 0.0

    # 6. Render KPI Grid (6 Cards)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

    with kpi_col1:
        render_kpi_card(
            title="Total Stock",
            value=format_number(total_stock),
            icon="📦",
            icon_color_class="kpi-icon-blue",
            subtitle="Physical units on hand",
        )

    with kpi_col2:
        render_kpi_card(
            title="Inventory Items",
            value=format_number(inventory_items),
            icon="🏷️",
            icon_color_class="kpi-icon-purple",
            subtitle="Active catalog SKUs",
        )

    with kpi_col3:
        render_kpi_card(
            title="Low Stock Items",
            value=format_number(low_stock_items),
            icon="⚠️",
            icon_color_class="kpi-icon-amber",
            delta=f"{low_stock_items} restock alerts" if low_stock_items > 0 else "Optimal buffer",
            delta_positive=low_stock_items == 0,
            subtitle="SKUs below reorder point",
        )

    with kpi_col4:
        render_kpi_card(
            title="Warehouses",
            value=format_number(warehouses),
            icon="🏢",
            icon_color_class="kpi-icon-green",
            subtitle="Active distribution hubs",
        )

    with kpi_col5:
        render_kpi_card(
            title="Stock Health Rate",
            value=format_percentage(health_rate),
            icon="✅",
            icon_color_class="kpi-icon-green",
            delta="In-stock catalog ratio",
            delta_positive=health_rate >= 95.0,
            subtitle=f"{in_stock_items:,} fully stocked SKUs",
        )

    with kpi_col6:
        render_kpi_card(
            title="Avg Units / SKU",
            value=format_number(avg_stock_per_sku),
            icon="📊",
            icon_color_class="kpi-icon-blue",
            subtitle="Mean stocking depth",
        )

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # 7. Check for Empty State
    if filtered_inv.empty:
        render_empty_state("No inventory records match the active filter criteria. Try clearing filters.")
        return

    plotly_theme = get_plotly_theme()

    # Analytical breakdowns
    wh_summary = calculate_stock_by_warehouse(filtered_inv)
    status_summary = calculate_stock_status_distribution(filtered_inv)
    cat_inv_summary = calculate_inventory_by_category(filtered_inv, prod_df)
    low_stock_df = calculate_low_stock_products(filtered_inv, prod_df)

    # =========================================================================
    # ROW 1: Warehouse Hub Cards
    # =========================================================================
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Warehouse Distribution Centers</h3>
                <p class="chart-subtitle">Operational status, physical stock reserves, and low-stock count by facility</p>
            </div>
            <span class="badge badge-neutral">Distribution Network</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    wh_cols = st.columns(max(len(wh_summary), 1))
    for idx, (_, wh_row) in enumerate(wh_summary.iterrows()):
        col = wh_cols[idx % len(wh_cols)]
        with col:
            low_alert = int(wh_row["low_stock_count"])
            alert_color = "#D97706" if low_alert > 0 else "#059669"
            alert_bg = "#FEF3C7" if low_alert > 0 else "#ECFDF5"
            alert_label = f"{low_alert} Low Stock" if low_alert > 0 else "All Stocked"

            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.15rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                        <div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A;">{wh_row['warehouse_name']}</div>
                            <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.15rem;">Distribution Hub</div>
                        </div>
                        <span style="background: {alert_bg}; color: {alert_color}; font-size: 0.725rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px;">
                            {alert_label}
                        </span>
                    </div>
                    <div style="border-top: 1px solid #F1F5F9; padding-top: 0.75rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.775rem;">
                        <div>
                            <span style="color: #64748B; display: block;">Stock Units</span>
                            <span style="font-size: 1.1rem; font-weight: 700; color: #0F172A; display: block;">{wh_row['stock_quantity']:,}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #64748B; display: block;">Catalog SKUs</span>
                            <span style="font-size: 1.1rem; font-weight: 700; color: #334155; display: block;">{wh_row['items_count']:,}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 2: Stock by Warehouse (Bar) & Status Breakdown (Donut)
    # =========================================================================
    row2_left, row2_right = st.columns([2, 1])

    with row2_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Warehouse Inventory Volume</h3>
                    <p class="chart-subtitle">Aggregate physical unit stocking across distribution facilities</p>
                </div>
                <span class="badge badge-primary">Facility Volume</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not wh_summary.empty:
            fig_wh = go.Figure(
                go.Bar(
                    x=wh_summary["warehouse_name"],
                    y=wh_summary["stock_quantity"],
                    marker=dict(color="#4F46E5", line=dict(color="#4338CA", width=1)),
                    hovertemplate="<b>%{x}</b><br>Stock Units: %{y:,}<br>SKUs: %{customdata[0]:,}<br>Low Stock: %{customdata[1]}<extra></extra>",
                    customdata=wh_summary[["items_count", "low_stock_count"]].values,
                )
            )
            fig_wh.update_layout(
                **plotly_theme,
                height=290,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickformat="~s",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_wh, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No warehouse records available.")

    with row2_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Stock Status Health</h3>
                    <p class="chart-subtitle">Ratio of in-stock versus replenishment threshold SKUs</p>
                </div>
                <span class="badge badge-success">Buffer Ratio</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not status_summary.empty:
            colors = {"In Stock": "#10B981", "Low Stock": "#F59E0B"}
            pie_colors = [colors.get(s, "#4F46E5") for s in status_summary["stock_status"]]

            fig_status = go.Figure(
                go.Pie(
                    labels=status_summary["stock_status"],
                    values=status_summary["count"],
                    hole=0.6,
                    marker=dict(colors=pie_colors, line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="<b>%{label}</b><br>SKUs: %{value:,}<br>Share: %{percent}<extra></extra>",
                    textinfo="label+percent",
                    textposition="inside",
                    textfont=dict(size=11, color="#FFFFFF"),
                )
            )
            fig_status.update_layout(
                **plotly_theme,
                height=290,
                showlegend=False,
            )
            st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No status distribution records available.")

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 3: Stock Quantity by Product Category & Stock vs Reorder Level
    # =========================================================================
    row3_left, row3_right = st.columns([1, 1])

    with row3_left:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Inventory Stock by Product Category</h3>
                    <p class="chart-subtitle">Physical merchandise stocking volume grouped by primary catalog line</p>
                </div>
                <span class="badge badge-primary">Merchandise</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not cat_inv_summary.empty:
            cat_palette = ["#4F46E5", "#8B5CF6", "#10B981"]
            fig_cat = go.Figure(
                go.Bar(
                    x=cat_inv_summary["category"],
                    y=cat_inv_summary["stock_quantity"],
                    marker=dict(color=cat_palette[:len(cat_inv_summary)]),
                    hovertemplate="<b>%{x}</b><br>Stock Units: %{y:,}<br>SKUs: %{customdata:,}<extra></extra>",
                    customdata=cat_inv_summary["items_count"].values,
                )
            )
            fig_cat.update_layout(
                **plotly_theme,
                height=290,
                yaxis=dict(
                    **plotly_theme["yaxis"],
                    tickformat="~s",
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No category inventory records available.")

    with row3_right:
        st.markdown(
            """
            <div class="chart-header">
                <div>
                    <h3 class="chart-title">Low-Stock SKUs vs Reorder Trigger</h3>
                    <p class="chart-subtitle">Current physical stock versus mandated safety buffer for top depleted items</p>
                </div>
                <span class="badge badge-warning">Deficit Audit</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not low_stock_df.empty:
            sample_low = low_stock_df.head(8).copy()
            sample_low["short_id"] = sample_low["product_id"].apply(lambda p: str(p).replace("FUR-", "").replace("OFF-", "").replace("TEC-", ""))

            fig_comp = go.Figure()
            fig_comp.add_trace(
                go.Bar(
                    x=sample_low["short_id"],
                    y=sample_low["stock_quantity"],
                    name="Current Stock",
                    marker_color="#F59E0B",
                    hovertemplate="<b>%{customdata}</b><br>Stock: %{y:,} units<extra></extra>",
                    customdata=sample_low["product_id"].values,
                )
            )
            fig_comp.add_trace(
                go.Bar(
                    x=sample_low["short_id"],
                    y=sample_low["reorder_level"],
                    name="Reorder Level",
                    marker_color="#EF4444",
                    hovertemplate="<b>%{customdata}</b><br>Reorder Point: %{y:,} units<extra></extra>",
                    customdata=sample_low["product_id"].values,
                )
            )
            fig_comp.update_layout(
                **plotly_theme,
                height=290,
                barmode="group",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11),
                ),
            )
            st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
        else:
            render_empty_state("No low-stock items in the active filter selection.")

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 4: Reorder Purchase Order Confirmation Banner
    # =========================================================================
    if st.session_state["latest_reordered_sku"]:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1px solid #A7F3D0; border-radius: 12px; padding: 0.85rem 1.25rem; display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; color: #065F46;">
                <span style="font-size: 1.25rem;">✅</span>
                <div style="font-size: 0.85rem;">
                    <b>Purchase Order Queued:</b> Automated replenishment order dispatched for SKU <b>{st.session_state['latest_reordered_sku']}</b> to warehouse supplier.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # ROW 5: Low-Stock Product Alerts & Reorder Level Register Table
    # =========================================================================
    st.markdown(
        """
        <div class="chart-header">
            <div>
                <h3 class="chart-title">Low-Stock Alerts & Reorder Register</h3>
                <p class="chart-subtitle">Catalog items breaching safety stock thresholds with automated replenishment controls</p>
            </div>
            <span class="badge badge-warning">Replenishment Priority</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not low_stock_df.empty:
        display_low = low_stock_df.copy()
        display_low["stock_fmt"] = display_low["stock_quantity"].apply(lambda s: f"{s:,} units")
        display_low["reorder_fmt"] = display_low["reorder_level"].apply(lambda r: f"{r:,} units")
        display_low["deficit_fmt"] = display_low["deficit"].apply(lambda d: f"{d:,} units")

        table_cols = [
            "product_id", "product_name", "category", "warehouse_name",
            "stock_fmt", "reorder_fmt", "deficit_fmt", "last_restock_date", "stock_status"
        ]
        col_renames = {
            "product_id": "SKU",
            "product_name": "Product Name",
            "category": "Category",
            "warehouse_name": "Warehouse",
            "stock_fmt": "Current Stock",
            "reorder_fmt": "Reorder Point",
            "deficit_fmt": "Deficit Units",
            "last_restock_date": "Last Restocked",
            "stock_status": "Status",
        }

        # Action Bar & CSV export
        t_col1, t_col2 = st.columns([3.5, 1.5])
        with t_col1:
            st.caption(f"Displaying {len(display_low):,} items requiring replenishment attention")
        with t_col2:
            csv_data = display_low[table_cols].rename(columns=col_renames).to_csv(index=False)
            st.download_button(
                label="📥 Export Low Stock CSV",
                data=csv_data,
                file_name="low_stock_inventory_alerts.csv",
                mime="text/csv",
                use_container_width=True,
                key="inv_download_csv",
            )

        st.dataframe(
            display_low[table_cols].rename(columns=col_renames),
            use_container_width=True,
            hide_index=True,
        )

        # Quick Reorder Trigger Section
        with st.expander("Dispatch Purchase Order for Low-Stock SKU"):
            skus_available = display_low["product_id"].tolist()
            sel_sku = st.selectbox("Select SKU to Restock", options=skus_available, key="sel_restock_sku")
            if st.button("Authorize & Transmit Purchase Order", key="btn_trigger_restock"):
                st.session_state["reordered_skus"].add(sel_sku)
                st.session_state["latest_reordered_sku"] = sel_sku
                st.rerun()
    else:
        render_empty_state("No low stock alerts in the current selection. All items meet safety thresholds.")

