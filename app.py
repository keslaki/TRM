import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="FIS Quantum - TRM Desktop Layout",
    layout="wide",
    initial_sidebar_state="expanded",
)


PRIMARY_NAVY = "#1A365D"
SLATE_GREY = "#4A5568"
CHARCOAL = "#1F2933"
SOFT_BG = "#F7FAFC"
CARD_BG = "#FFFFFF"
SUCCESS_GREEN = "#2F855A"
ALERT_RED = "#C53030"
LIGHT_BORDER = "#D9E2EC"
LIGHT_BLUE = "#90CDF4"


def format_currency(value: float, currency: str = "CAD", show_sign: bool = False) -> str:
    """Format numeric values with commas, symbols, and an optional leading sign."""
    sign = ""
    if show_sign:
        sign = "+" if value >= 0 else "-"
    absolute_value = abs(value)
    return f"{sign}${absolute_value:,.0f} {currency}"


def build_metric_card(title: str, value: str, subtext: str = "") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtext">{subtext}</div>
    </div>
    """


def build_impact_card(impact_value: float) -> str:
    impact_color = SUCCESS_GREEN if impact_value > 0 else PRIMARY_NAVY
    if impact_value < 0:
        impact_color = ALERT_RED

    return f"""
    <div class="impact-card">
        <div class="impact-label">Projected Revenue Variance</div>
        <div class="impact-value" style="color: {impact_color};">
            {format_currency(impact_value, currency="CAD", show_sign=True)}
        </div>
        <div class="impact-subtext">
            Calculated as simulated WTI price change multiplied by
            $680,000,000 CAD per US$1/bbl.
        </div>
    </div>
    """


def build_currency_chart() -> go.Figure:
    labels = ["CAD Debt", "USD Debt", "AUD Debt"]
    values = [75, 18, 7]
    colors = [PRIMARY_NAVY, SLATE_GREY, LIGHT_BLUE]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.56,
                marker=dict(colors=colors, line=dict(color=SOFT_BG, width=3)),
                sort=False,
                textinfo="label+percent",
                textfont=dict(size=13, color=CHARCOAL),
                hovertemplate="%{label}: %{value}%<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Debt Portfolio Composition by Currency",
            x=0.02,
            font=dict(size=18, color=PRIMARY_NAVY),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, r=20, b=20, l=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(color=SLATE_GREY),
        ),
        annotations=[
            dict(
                text="Currency<br>Mix",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=18, color=PRIMARY_NAVY),
            )
        ],
    )
    return fig


st.markdown(
    f"""
    <style>
        :root {{
            --primary-navy: {PRIMARY_NAVY};
            --slate-grey: {SLATE_GREY};
            --charcoal: {CHARCOAL};
            --soft-bg: {SOFT_BG};
            --card-bg: {CARD_BG};
            --success-green: {SUCCESS_GREEN};
            --alert-red: {ALERT_RED};
            --light-border: {LIGHT_BORDER};
        }}

        .stApp {{
            background: linear-gradient(180deg, #F7FAFC 0%, #EDF2F7 100%);
            color: var(--charcoal);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #102A43 0%, #1A365D 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: #F7FAFC;
        }}

        .sidebar-brand {{
            padding: 0.25rem 0 1.5rem 0;
        }}

        .sidebar-title {{
            font-size: 1.55rem;
            font-weight: 700;
            line-height: 1.2;
        }}

        .sidebar-group {{
            margin-top: 0.5rem;
            font-size: 0.95rem;
            color: #D9E2EC;
        }}

        .hero-card {{
            background: linear-gradient(135deg, rgba(26,54,93,0.98), rgba(74,85,104,0.94));
            border-radius: 20px;
            padding: 1.8rem 2rem;
            margin-bottom: 1.35rem;
            box-shadow: 0 18px 36px rgba(16, 42, 67, 0.18);
        }}

        .hero-title {{
            color: white;
            font-size: 2.15rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.35rem;
        }}

        .hero-subtitle {{
            color: #E2E8F0;
            font-size: 1rem;
            line-height: 1.5;
            margin: 0;
        }}

        .section-heading {{
            color: var(--primary-navy);
            font-size: 1.1rem;
            font-weight: 700;
            margin: 0.45rem 0 0.9rem 0;
            padding-bottom: 0.4rem;
            border-bottom: 2px solid rgba(26, 54, 93, 0.12);
            letter-spacing: 0.01em;
        }}

        .metric-card {{
            background: white;
            border-radius: 18px;
            padding: 1.15rem 1.2rem;
            min-height: 145px;
            border: 1px solid rgba(217, 226, 236, 0.9);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
        }}

        .metric-title {{
            color: var(--slate-grey);
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
        }}

        .metric-value {{
            color: var(--primary-navy);
            font-size: 1.7rem;
            font-weight: 750;
            line-height: 1.15;
            margin-bottom: 0.65rem;
        }}

        .metric-subtext {{
            color: var(--slate-grey);
            font-size: 0.88rem;
            min-height: 1rem;
        }}

        .context-card, .impact-card, .table-shell {{
            background: white;
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            border: 1px solid rgba(217, 226, 236, 0.9);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
        }}

        .context-card {{
            border-left: 6px solid var(--primary-navy);
            min-height: 235px;
        }}

        .context-title {{
            color: var(--primary-navy);
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }}

        .context-text {{
            color: var(--charcoal);
            font-size: 0.98rem;
            line-height: 1.65;
            margin: 0;
        }}

        .impact-card {{
            min-height: 235px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .impact-label {{
            color: var(--slate-grey);
            font-size: 0.95rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.8rem;
        }}

        .impact-value {{
            font-size: 2.1rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 0.8rem;
        }}

        .impact-subtext {{
            color: var(--slate-grey);
            font-size: 0.92rem;
            line-height: 1.55;
        }}

        .alert-banner {{
            background: rgba(197, 48, 48, 0.10);
            color: var(--alert-red);
            border: 1px solid rgba(197, 48, 48, 0.28);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            font-weight: 700;
            margin-top: 0.9rem;
        }}

        .stable-banner {{
            background: rgba(26, 54, 93, 0.08);
            color: var(--primary-navy);
            border: 1px solid rgba(26, 54, 93, 0.16);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            font-weight: 600;
            margin-top: 0.9rem;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(217, 226, 236, 0.9);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">FIS Quantum - TRM Desktop Layout</div>
            <div class="sidebar-group">
                Capital Markets Group | Treasury Board &amp; Finance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    wti_price_change = st.slider(
        "Simulated WTI Crude Price Change (USD/bbl)",
        min_value=-10,
        max_value=10,
        value=0,
        step=1,
    )


st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Alberta Capital Markets &amp; Treasury Risk Analytics</div>
        <p class="hero-subtitle">
            Real-time, one-touch liquidity position snapshot across borrowing requirements,
            foreign exchange maturity exposure, and commodity-linked fiscal sensitivity.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.container():
    st.markdown(
        '<div class="section-heading">Section 1: Global Cash & FX Risk Position</div>',
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.markdown(
            build_metric_card(
                "Gross Borrowing Requirement",
                "$20.9 Billion CAD",
            ),
            unsafe_allow_html=True,
        )
    with metric_cols[1]:
        st.markdown(
            build_metric_card(
                "Immediate FX Exposure Maturity",
                "$1.0 Billion USD",
                "Due August 17",
            ),
            unsafe_allow_html=True,
        )
    with metric_cols[2]:
        st.markdown(
            build_metric_card(
                "Budgeted CAD/USD Target",
                "73.0¢ USD",
            ),
            unsafe_allow_html=True,
        )

    st.plotly_chart(build_currency_chart(), use_container_width=True)


with st.container():
    st.markdown(
        '<div class="section-heading">Section 2: Commodity Trading Sensitivity &amp; Automated Auto-Hedging</div>',
        unsafe_allow_html=True,
    )

    sensitivity_cols = st.columns([1.15, 1.0], gap="large")
    projected_impact = wti_price_change * 680_000_000

    with sensitivity_cols[0]:
        # This dashboard pattern mirrors how FIS Quantum Ad-Hoc Report Writer inquiries
        # can bring together disparate treasury, funding, and market-risk data structures
        # into a single operating view for decision-makers.
        st.markdown(
            """
            <div class="context-card">
                <div class="context-title">Commodity Revenue Context</div>
                <p class="context-text">
                    Alberta's revenue base is highly sensitive to commodity price volatility.
                    A US$1/bbl change in the WTI benchmark impacts provincial revenue by
                    <strong>$680,000,000 CAD</strong>, while a US$1/bbl shift in the
                    WTI-WCS differential impacts revenue by
                    <strong>$670,000,000 CAD</strong>.
                </p>
                <p class="context-text" style="margin-top: 0.9rem;">
                    The simulation control in the sidebar supports fast scenario analysis
                    for Treasury and Capital Markets staff monitoring downstream liquidity,
                    hedge timing, and funding requirements.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with sensitivity_cols[1]:
        st.markdown(build_impact_card(projected_impact), unsafe_allow_html=True)
        if projected_impact < -1_300_000_000:
            st.markdown(
                """
                <div class="alert-banner">
                    RECOMMENDATION: Trigger Automated USD Currency Hedge Action.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="stable-banner">
                    Treasury position remains within the current monitoring tolerance band.
                </div>
                """,
                unsafe_allow_html=True,
            )


with st.container():
    st.markdown(
        '<div class="section-heading">Section 3: Term Debt Maturity Schedule</div>',
        unsafe_allow_html=True,
    )

    # This maturity schedule is intentionally assembled from distinct structures to reflect
    # how FIS Quantum-style ad-hoc reporting can unify settlements, debt, and legal entity views.
    maturity_df = pd.DataFrame(
        [
            {
                "Maturity Date": "Aug 17, 2026",
                "Instrument Type": "Global USD Bond",
                "Par Amount": format_currency(1_000_000_000, currency="USD"),
                "Currency": "USD",
                "ISIN / Legal Entity": "XS1476553711",
            },
            {
                "Maturity Date": "Nov 03, 2026",
                "Instrument Type": "Domestic CAD Bond",
                "Par Amount": format_currency(200_000_000, currency="CAD"),
                "Currency": "CAD",
                "ISIN / Legal Entity": "Alberta Domestic",
            },
            {
                "Maturity Date": "Dec 14, 2026",
                "Instrument Type": "AUD Term Note",
                "Par Amount": format_currency(505_000_000, currency="AUD"),
                "Currency": "AUD",
                "ISIN / Legal Entity": "AU3CB0237949",
            },
        ]
    )

    st.markdown('<div class="table-shell">', unsafe_allow_html=True)
    st.dataframe(maturity_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
