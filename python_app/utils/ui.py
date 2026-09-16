import streamlit as st
from typing import Optional, List, Dict, Any


def inject_custom_css():
    """Inject premium SaaS styling matching the Enterprise RetailIQ design system."""
    st.markdown(
        """
        <style>
        /* Import clean modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
        
        :root {
            --primary-color: #4F46E5;
            --primary-hover: #4338CA;
            --card-bg: #FFFFFF;
            --card-border: #E2E8F0;
            --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
            --text-dark: #0F172A;
            --text-muted: #64748B;
        }

        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0F172A;
            background-color: #F8FAFC;
        }

        /* Top Header Navbar */
        .top-navbar-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 0.6rem 1.15rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .top-navbar-left {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .top-search-box {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 0.4rem 0.75rem;
            font-size: 0.8rem;
            color: #64748B;
            width: 250px;
            transition: all 0.15s ease;
        }

        .top-navbar-right {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .user-profile-badge {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.25rem 0.65rem 0.25rem 0.35rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 9999px;
        }

        .user-avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
            color: #FFFFFF;
            font-weight: 700;
            font-size: 0.725rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .user-info-text {
            display: flex;
            flex-direction: column;
            line-height: 1.15;
        }

        .user-name {
            font-size: 0.75rem;
            font-weight: 700;
            color: #0F172A;
        }

        .user-role {
            font-size: 0.65rem;
            color: #64748B;
        }

        /* Page Header */
        .page-header-container {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 1.1rem 1.4rem;
            margin-bottom: 1.15rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .page-header-left {
            max-width: 82%;
        }

        .page-greeting {
            font-size: 0.75rem;
            font-weight: 700;
            color: #4F46E5;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.2rem;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }

        .page-title {
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }

        .page-description {
            font-size: 0.85rem;
            color: #64748B;
            margin-top: 0.25rem;
            margin-bottom: 0;
            line-height: 1.4;
        }

        .page-header-badges {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.35rem;
        }

        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.725rem;
            font-weight: 600;
            line-height: 1;
        }
        .badge-primary, .badge-indigo {
            background-color: #EEF2FF;
            color: #4F46E5;
            border: 1px solid #C7D2FE;
        }
        .badge-success {
            background-color: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
        }
        .badge-warning {
            background-color: #FFFBEB;
            color: #D97706;
            border: 1px solid #FDE68A;
        }
        .badge-neutral {
            background-color: #F8FAFC;
            color: #475569;
            border: 1px solid #E2E8F0;
        }
        .badge-purple {
            background-color: #FAF5FF;
            color: #7E22CE;
            border: 1px solid #E9D5FF;
        }

        /* Pulsing Status Dot */
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #10B981;
            display: inline-block;
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
            animation: pulse-dot 2s infinite ease-in-out;
        }

        @keyframes pulse-dot {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
            70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Filter Bar Container */
        .filter-container-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .filter-header-title {
            font-size: 0.75rem;
            font-weight: 700;
            color: #4F46E5;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* KPI Card */
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
            transition: all 0.15s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px -2px rgba(79, 70, 229, 0.06);
            border-color: #CBD5E1;
        }
        .kpi-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        .kpi-title {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748B;
        }
        .kpi-icon-wrap {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
        }
        .kpi-icon-blue, .kpi-icon-indigo { background: #EEF2FF; color: #4F46E5; }
        .kpi-icon-green, .kpi-icon-emerald { background: #ECFDF5; color: #059669; }
        .kpi-icon-purple { background: #FAF5FF; color: #8B5CF6; }
        .kpi-icon-amber { background: #FFFBEB; color: #D97706; }
        .kpi-icon-rose, .kpi-icon-red { background: #FFF1F2; color: #E11D48; }
        .kpi-icon-cyan { background: #ECFEFF; color: #0891B2; }
        .kpi-icon-slate { background: #F1F5F9; color: #475569; }

        .kpi-value {
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 1.5rem;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin-bottom: 0.35rem;
        }
        .kpi-footer {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.4rem;
            font-size: 0.725rem;
            color: #64748B;
            margin-top: auto;
            padding-top: 0.3rem;
            border-top: 1px dashed #F1F5F9;
        }
        .kpi-delta {
            display: inline-flex;
            align-items: center;
            font-weight: 700;
            font-size: 0.7rem;
            padding: 0.12rem 0.4rem;
            border-radius: 4px;
        }
        .kpi-delta-positive {
            background-color: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
        }
        .kpi-delta-negative {
            background-color: #FEF2F2;
            color: #DC2626;
            border: 1px solid #FECACA;
        }
        .kpi-target {
            font-size: 0.7rem;
            font-weight: 500;
            color: #64748B;
            background: #F8FAFC;
            padding: 0.12rem 0.35rem;
            border-radius: 4px;
            border: 1px solid #E2E8F0;
        }

        /* Supply Chain Alert Banner */
        .supply-alert-banner {
            background: linear-gradient(135deg, #FFFDF5 0%, #FEF3C7 100%);
            border: 1px solid #FCD34D;
            border-radius: 12px;
            padding: 0.85rem 1.15rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.85rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 1px 2px rgba(245, 158, 11, 0.05);
        }
        .supply-alert-left {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }
        .supply-alert-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background-color: #FDE68A;
            color: #92400E;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            flex-shrink: 0;
        }
        .supply-alert-title-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        .supply-alert-title {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #78350F;
            margin: 0;
        }
        .supply-alert-text {
            font-size: 0.8rem;
            color: #92400E;
            margin: 0.2rem 0 0 0;
            line-height: 1.35;
        }

        /* Chart Container Styling */
        .chart-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.1rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
            transition: all 0.15s ease;
        }
        .chart-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 0.75rem;
            gap: 0.5rem;
        }
        .chart-title {
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 0.925rem;
            font-weight: 700;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.01em;
        }
        .chart-subtitle {
            font-size: 0.75rem;
            color: #64748B;
            margin: 0.15rem 0 0 0;
        }

        /* Insight Mini Card */
        .insight-mini-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.55rem;
            display: flex;
            align-items: flex-start;
            gap: 0.65rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            transition: all 0.15s ease;
        }
        .insight-mini-card:hover {
            border-color: #C7D2FE;
            background: #FAFAFE;
        }
        .insight-mini-icon {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            flex-shrink: 0;
        }
        .insight-mini-content {
            flex: 1;
        }
        .insight-mini-title {
            font-size: 0.775rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.1rem;
        }
        .insight-mini-text {
            font-size: 0.725rem;
            color: #64748B;
            line-height: 1.35;
        }

        /* Sidebar Styling - Compact & Modern */
        section[data-testid="stSidebar"] {
            width: 255px !important;
            min-width: 255px !important;
            max-width: 255px !important;
            background: linear-gradient(180deg, #0B0F19 0%, #13112E 40%, #1C1942 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        section[data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] .stRadio > div {
            gap: 0.25rem;
        }

        section[data-testid="stSidebar"] .stRadio label {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 0.55rem 0.75rem !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease;
            cursor: pointer;
            margin-bottom: 0.1rem;
        }

        section[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(99, 102, 241, 0.15) !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] .stRadio label[data-checked="true"],
        section[data-testid="stSidebar"] .stRadio div[aria-checked="true"] {
            background: linear-gradient(90deg, #4F46E5 0%, #6366F1 100%) !important;
            border-color: #818CF8 !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.35) !important;
        }

        /* Streamlit widget tweaks */
        div[data-testid="stSidebarNav"] { display: none; }
        .block-container { 
            padding-top: 1rem !important; 
            padding-bottom: 3rem !important;
            max-width: 1440px !important;
        }

        /* Modernize Streamlit Button */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            padding: 0.45rem 0.85rem !important;
            transition: all 0.15s ease !important;
            border: 1px solid #E2E8F0 !important;
            background: #FFFFFF !important;
            color: #334155 !important;
        }
        .stButton > button:hover {
            border-color: #4F46E5 !important;
            color: #4F46E5 !important;
            box-shadow: 0 1px 3px rgba(79, 70, 229, 0.1) !important;
        }
        /* Streamlit Tabs - Visibility Fix */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.35rem !important;
    border-bottom: 1px solid #E2E8F0 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #475569 !important;
    background: #FFFFFF !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 0.55rem 0.85rem !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #4F46E5 !important;
    background: #F8FAFC !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #4F46E5 !important;
    font-weight: 700 !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background: #4F46E5 !important;
    height: 2px !important;
}

        /* Streamlit Dataframe wrapper */
        div[data-testid="stDataFrame"] {
            border-radius: 10px !important;
            overflow: hidden !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        }

        /* Streamlit Pills */
        div[data-testid="stPills"] button {
            border-radius: 6px !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


class PlotlyThemeDict(dict):
    """Layout dictionary that prevents duplicate keyword argument errors when unpacked
    via **plotly_theme alongside explicit xaxis, yaxis, or legend arguments."""
    def keys(self):
        return [k for k in super().keys() if k not in ("xaxis", "yaxis", "legend")]

    def __iter__(self):
        return (k for k in super().__iter__() if k not in ("xaxis", "yaxis", "legend"))

    def items(self):
        return [(k, v) for k, v in super().items() if k not in ("xaxis", "yaxis", "legend")]

    def values(self):
        return [v for k, v in super().items() if k not in ("xaxis", "yaxis", "legend")]


def get_plotly_theme() -> Dict[str, Any]:
    """Return standard modern layout configuration for enterprise Plotly visualizations."""
    return PlotlyThemeDict(
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size=11, color="#64748B"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=25, r=20, l=20, b=25),
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor="#0F172A",
            font=dict(color="#FFFFFF", size=11, family="Inter, sans-serif"),
        ),
        xaxis=dict(
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            tickfont=dict(color="#64748B", size=11),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            tickfont=dict(color="#64748B", size=11),
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#475569"),
        ),
    )


def render_top_navbar(
    active_page: str = "Executive Dashboard",
    user_name: str = "Shobha S",
    user_role: str = "Enterprise VP / Analytics Lead",
):
    """Render a premium top header navbar matching modern enterprise SaaS platforms."""
    st.markdown(
        f"""
        <div class="top-navbar-container">
            <div class="top-navbar-left">
                <div class="top-search-box">
                    <span>🔍</span>
                    <span>Search orders, SKUs, customers, metrics...</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.775rem; color: #64748B;">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
                    <span>Enterprise Engine</span>
                    <span style="color: #CBD5E1;">&bull;</span>
                    <span style="font-weight: 600; color: #4F46E5;">{active_page}</span>
                </div>
            </div>
            <div class="top-navbar-right">
                <div class="badge badge-success" style="padding: 0.25rem 0.65rem;">
                    <span class="status-dot"></span>
                    <span>Live Telemetry</span>
                </div>
                <div class="user-profile-badge">
                    <div class="user-avatar">SS</div>
                    <div class="user-info-text">
                        <span class="user-name">{user_name}</span>
                        <span class="user-role">{user_role}</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str = "Executive Dashboard",
    description: str = "Unified view of revenue velocity, margin health, omnichannel fulfillment, and strategic inventory signals.",
    badge_label: Optional[str] = "Live",
    user_greeting: Optional[str] = None,
    secondary_badge: Optional[str] = None,
    **kwargs: Any,
):
    """Render modern enterprise page header with clean hierarchy."""
    greeting_html = f'<div class="page-greeting">{user_greeting}</div>' if user_greeting else ""
    badge_html = f'<span class="badge badge-primary"><span class="status-dot"></span>{badge_label}</span>' if badge_label else ""
    secondary_badge_html = f'<span class="badge badge-neutral">{secondary_badge}</span>' if secondary_badge else ""

    st.markdown(
        f"""
        <div class="page-header-container">
            <div class="page-header-left">
                {greeting_html}
                <h1 class="page-title">{title}</h1>
                <p class="page-description">{description}</p>
            </div>
            <div class="page-header-badges">
                {badge_html}
                {secondary_badge_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    change: Optional[float] = None,
    change_period: str = "YoY Growth",
    target: Optional[str] = None,
    icon: str = "💵",
    color_variant: str = "blue",
    delta: Optional[str] = None,
    delta_positive: Optional[bool] = None,
    icon_color_class: Optional[str] = None,
    delta_period: Optional[str] = None,
    **kwargs: Any,
):
    """
    Render a modern SaaS KPI card with crisp typography, icon badge, delta, and target.
    """
    delta_html = ""
    if delta is not None:
        delta_class = "kpi-delta-positive" if (delta_positive is not False) else "kpi-delta-negative"
        period_text = f" {delta_period}" if delta_period else ""
        delta_html = f'<span class="kpi-delta {delta_class}">{delta}{period_text}</span>'
    elif change is not None:
        delta_class = "kpi-delta-positive" if change >= 0 else "kpi-delta-negative"
        prefix = "+" if change >= 0 else ""
        delta_html = f'<span class="kpi-delta {delta_class}">{prefix}{change:.2f}% {change_period}</span>'

    target_html = f'<span class="kpi-target">Target: {target}</span>' if target else ""
    sub_html = f'<span>{subtitle}</span>' if subtitle else ""

    footer_content = f"{delta_html} {target_html} {sub_html}".strip()

    # Resolve color variant
    resolved_color = color_variant
    if icon_color_class:
        resolved_color = icon_color_class.replace("kpi-icon-", "")

    st.markdown(
        f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-header">
                    <span class="kpi-title">{title}</span>
                    <div class="kpi-icon-wrap kpi-icon-{resolved_color}">{icon}</div>
                </div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="kpi-footer">
                {footer_content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_supply_chain_alert(
    low_stock_count: int,
    avg_delivery_days: float,
    critical_skus: Optional[List[str]] = None,
    **kwargs: Any,
):
    """Render real-time supply chain alert banner for stockout risks."""
    sku_text = ""
    if critical_skus and len(critical_skus) > 0:
        sku_list = ", ".join(critical_skus[:3])
        sku_text = f" ({sku_list})"

    st.markdown(
        f"""
        <div class="supply-alert-banner">
            <div class="supply-alert-left">
                <div class="supply-alert-icon">⚠️</div>
                <div>
                    <div class="supply-alert-title-row">
                        <span class="supply-alert-title">Supply Chain Alert: Stockout Risk</span>
                        <span class="badge badge-warning">{low_stock_count} SKUs Below Threshold</span>
                    </div>
                    <p class="supply-alert-text">
                        {low_stock_count} catalog items are below safety thresholds{sku_text}.
                        Average delivery duration is currently {avg_delivery_days:.2f} days.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(
    message: str = "No data available for the selected filters.",
    title: str = "No Records Found",
    action_label: Optional[str] = None,
    on_action_click: Optional[Any] = None,
    **kwargs: Any,
):
    """Render a clean message when filters return zero records."""
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 2.5rem 1.5rem; text-align: center; margin: 1.25rem 0;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
            <h3 style="font-size: 1rem; font-weight: 700; color: #1E293B; margin: 0 0 0.25rem 0;">{title}</h3>
            <p style="font-size: 0.825rem; color: #64748B; margin: 0;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recent_insights_card(
    title: str,
    text: str,
    icon: str = "💡",
    color_variant: str = "blue",
    badge: Optional[str] = None,
):
    """Render a clean modern insight mini-card."""
    badge_html = f'<span class="badge badge-primary" style="font-size: 0.675rem; padding: 0.12rem 0.4rem;">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="insight-mini-card">
            <div class="insight-mini-icon kpi-icon-{color_variant}">{icon}</div>
            <div class="insight-mini-content">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.1rem;">
                    <div class="insight-mini-title">{title}</div>
                    {badge_html}
                </div>
                <div class="insight-mini-text">{text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
