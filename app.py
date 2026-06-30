from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(
    page_title="Alberta TRM Financing Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

FY_ORDER = [
    "2025-26 Budget",
    "2025-26 Forecast",
    "2026-27 Target",
    "2027-28 Target",
    "2028-29 Target",
]
MATURITY_ORDER = ["2025-26", "2026-27", "2027-28", "2028-29"]

NAVY = "#1F4E79"
BLUE = "#4F81BD"
SKY = "#A9C5E8"
SLATE = "#4B637A"
INK = "#1F2933"
MUTED = "#64748B"
BORDER = "#D7E1EC"
GRID = "#E9EFF5"
SURFACE = "#FFFFFF"
CANVAS = "#F4F8FB"
TERM_DEBT_SOURCE_DATE = "June 17, 2026"
TERM_DEBT_FX_SOURCE_LABEL = "Bank of Canada daily exchange rates"
INVESTOR_RELATIONS_URL = "https://www.alberta.ca/investor-relations"
BUDGET_2026_URL = "https://open.alberta.ca/publications/budget-2026"
TERM_CURRENCY_COLORS = {
    "CAD": NAVY,
    "USD": BLUE,
    "EUR": "#6D8EB9",
    "AUD": "#88A9D1",
    "SEK": "#A9C5E8",
    "CHF": "#C2D8EE",
    "NZD": "#D7E6F5",
}


def format_billions(value: float, prefix: str = "$") -> str:
    return f"{prefix}{value:,.3f}B"


def format_native_billions(currency_label: str, value: float) -> str:
    if currency_label.endswith("$") or currency_label == "€":
        return f"{currency_label}{value:,.3f}B"
    return f"{currency_label} {value:,.3f}B"


def metric_card(title: str, value: str, note: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{escape(title)}</div>
        <div class="metric-value">{escape(value)}</div>
        <div class="metric-note">{escape(note)}</div>
    </div>
    """


def section_heading(title: str, body: str) -> str:
    return f"""
    <div class="section-block">
        <div class="section-title">{title}</div>
        <div class="section-body">{body}</div>
    </div>
    """


def insight_card(text: str) -> str:
    return f"""
    <div class="insight-card">
        <div class="insight-label">Insight</div>
        <div class="insight-text">{text}</div>
    </div>
    """

def source_footer(sources: list[tuple[str, str]]) -> str:
    lines = "".join(
        f'<div class="source-line"><a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a></div>'
        for label, url in sources
    )
    return f"""
    <div class="source-shell">
        <div class="source-title">Source</div>
        {lines}
    </div>
    """


def executive_summary_table(df: pd.DataFrame) -> str:
    rows = []
    for row in df.to_dict(orient="records"):
        as_of_note = ""
        as_of_value = row.get("as_of_note", "")
        if pd.notna(as_of_value) and str(as_of_value).strip():
            as_of_note = f'<div class="summary-kpi-note">{escape(str(as_of_value).strip())}</div>'

        kpi_name = row.get("kpi", row.get("metric", ""))
        value_display = row.get("value_display", row.get("display_value", ""))
        kpi_type = row.get("kpi_type", "")
        official_source = row.get("official_source", "")
        why_it_matters = row.get("why_it_matters", row.get("notes", ""))
        card_type = "summary-card-flow" if str(kpi_type).lower() == "flow" else "summary-card-stock"

        rows.append(
            f"""
            <article class="summary-card {card_type}">
                <div class="summary-card-top">
                    <span class="summary-type-chip">{escape(str(kpi_type))}</span>
                </div>
                <div class="summary-kpi-name">{escape(str(kpi_name))}</div>
                {as_of_note}
                <div class="summary-value-cell">{escape(str(value_display))}</div>
                <div class="summary-meta-grid">
                    <div class="summary-meta-block">
                        <div class="summary-meta-label">Official Source</div>
                        <div class="summary-meta-text">{escape(str(official_source))}</div>
                    </div>
                    <div class="summary-meta-block">
                        <div class="summary-meta-label">Why It Matters</div>
                        <div class="summary-meta-text">{escape(str(why_it_matters))}</div>
                    </div>
                </div>
            </article>
            """
        )

    return f"""
    <div class="summary-card-grid">
        {''.join(rows)}
    </div>
    """


def load_data() -> dict[str, pd.DataFrame]:
    data = {
        "kpis": pd.read_csv(DATA_DIR / "trm_financing_data.csv"),
        "borrowing": pd.read_csv(DATA_DIR / "borrowing_requirements.csv"),
        "maturities": pd.read_csv(DATA_DIR / "debt_maturities.csv"),
        "funding_programs": pd.read_csv(DATA_DIR / "funding_programs.csv"),
        "term_currency": pd.read_csv(DATA_DIR / "term_debt_currency.csv"),
        "average_term": pd.read_csv(DATA_DIR / "average_term_by_currency.csv"),
        "money_market": pd.read_csv(DATA_DIR / "money_market_debt.csv"),
        "ratings": pd.read_csv(DATA_DIR / "credit_ratings.csv"),
    }

    data["kpis"] = data["kpis"].sort_values("sort_order")

    data["borrowing"]["fiscal_year"] = pd.Categorical(
        data["borrowing"]["fiscal_year"],
        categories=FY_ORDER,
        ordered=True,
    )
    data["borrowing"] = data["borrowing"].sort_values("fiscal_year")

    data["maturities"]["fiscal_year"] = pd.Categorical(
        data["maturities"]["fiscal_year"],
        categories=MATURITY_ORDER,
        ordered=True,
    )
    data["maturities"] = data["maturities"].sort_values("fiscal_year")

    data["term_currency"]["native_display"] = data["term_currency"].apply(
        lambda row: format_native_billions(row["currency_label"], row["outstanding"]),
        axis=1,
    )
    data["term_currency"]["cad_equivalent"] = (
        data["term_currency"]["outstanding"] * data["term_currency"]["fx_rate_to_cad"]
    )
    total_term_cad = float(data["term_currency"]["cad_equivalent"].sum())
    data["term_currency"]["cad_equivalent_display"] = data["term_currency"][
        "cad_equivalent"
    ].map(format_billions)
    data["term_currency"]["portfolio_share"] = (
        data["term_currency"]["cad_equivalent"] / total_term_cad
    )
    data["term_currency"]["portfolio_share_display"] = data["term_currency"][
        "portfolio_share"
    ].map(lambda value: f"{value:.1%}")
    data["term_currency"]["fx_rate_display"] = data["term_currency"][
        "fx_rate_to_cad"
    ].map(lambda value: f"{value:,.4f}")
    data["term_currency"]["fx_date_display"] = pd.to_datetime(
        data["term_currency"]["fx_rate_date"]
    ).map(lambda value: f"{value.strftime('%B')} {value.day}, {value.year}")
    data["money_market"]["display_total"] = data["money_market"].apply(
        lambda row: f"{row['currency_label']} {row['total_money_market_debt']:,.3f}B",
        axis=1,
    )
    return data


def apply_chart_theme(fig: go.Figure, *, height: int, yaxis_title: str) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=18, r=18, t=54, b=24),
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=INK),
        hoverlabel=dict(bgcolor=SURFACE, font_color=INK),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            title=None,
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(size=12))
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(size=12),
        title=yaxis_title,
    )
    return fig


def build_borrowing_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=df["fiscal_year"],
        y=df["term_debt_planned"],
        name="Term Debt Planned",
        marker_color=NAVY,
        hovertemplate="%{x}<br>Term Debt Planned: $%{y:.3f}B<extra></extra>",
    )
    fig.add_bar(
        x=df["fiscal_year"],
        y=df["money_market_net_change"],
        name="Money Market Net Change",
        marker_color=SKY,
        hovertemplate="%{x}<br>Money Market Net Change: $%{y:.3f}B<extra></extra>",
    )
    fig.add_scatter(
        x=df["fiscal_year"],
        y=df["total_borrowing_requirement"],
        name="Total Borrowing Requirement",
        mode="lines+markers+text",
        marker=dict(size=10, color=SLATE),
        line=dict(width=3, color=SLATE),
        text=[format_billions(value) for value in df["total_borrowing_requirement"]],
        textposition="top center",
        hovertemplate="%{x}<br>Total Borrowing Requirement: $%{y:.3f}B<extra></extra>",
    )
    fig.update_layout(
        barmode="stack",
        title="Borrowing Requirement Trend",
    )
    return apply_chart_theme(fig, height=430, yaxis_title="Borrowing requirement ($ billions)")


def build_maturity_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=df["fiscal_year"],
        y=df["long_term_maturities"],
        name="Long-Term Maturities",
        marker_color=NAVY,
        hovertemplate="%{x}<br>Long-Term Maturities: $%{y:.3f}B<extra></extra>",
    )
    fig.add_bar(
        x=df["fiscal_year"],
        y=df["short_term_maturities"],
        name="Short-Term Maturities",
        marker_color=BLUE,
        hovertemplate="%{x}<br>Short-Term Maturities: $%{y:.3f}B<extra></extra>",
    )
    fig.add_scatter(
        x=df["fiscal_year"],
        y=df["total_maturities"],
        mode="text",
        text=[format_billions(value) for value in df["total_maturities"]],
        textposition="top center",
        showlegend=False,
        hoverinfo="skip",
    )
    fig.update_layout(
        barmode="stack",
        title="Debt Maturity Pressure",
    )
    return apply_chart_theme(fig, height=420, yaxis_title="Maturities ($ billions)")


def build_term_currency_cad_chart(df: pd.DataFrame) -> go.Figure:
    ordered_df = df.sort_values("cad_equivalent", ascending=True)
    fig = go.Figure()
    fig.add_bar(
        x=ordered_df["cad_equivalent"],
        y=ordered_df["currency"],
        orientation="h",
        marker_color=[TERM_CURRENCY_COLORS[currency] for currency in ordered_df["currency"]],
        text=ordered_df["cad_equivalent_display"],
        textposition="outside",
        customdata=ordered_df[["native_display", "fx_rate_display", "fx_date_display"]],
        hovertemplate=(
            "%{y}<br>CAD Equivalent: %{text}"
            "<br>Native Outstanding: %{customdata[0]}"
            "<br>FX Rate: %{customdata[1]} CAD per 1 unit"
            "<br>FX Date: %{customdata[2]}"
            "<extra></extra>"
        ),
    )
    fig.update_layout(title="Outstanding Term Debt — CAD Equivalent", showlegend=False)
    fig.update_xaxes(title="CAD equivalent ($ billions)")
    return apply_chart_theme(fig, height=420, yaxis_title="")


def build_term_currency_share_chart(df: pd.DataFrame) -> go.Figure:
    ordered_df = df.sort_values("cad_equivalent", ascending=False)
    total_cad_equivalent = float(ordered_df["cad_equivalent"].sum())
    fig = go.Figure(
        data=[
            go.Pie(
                labels=ordered_df["currency"],
                values=ordered_df["cad_equivalent"],
                hole=0.6,
                sort=False,
                marker=dict(
                    colors=[
                        TERM_CURRENCY_COLORS[currency]
                        for currency in ordered_df["currency"]
                    ],
                    line=dict(color=SURFACE, width=2),
                ),
                text=[
                    f"{currency} {share}"
                    for currency, share in zip(
                        ordered_df["currency"],
                        ordered_df["portfolio_share_display"],
                    )
                ],
                textinfo="text",
                textposition="outside",
                hovertemplate=(
                    "%{label}<br>Portfolio Share: %{percent}"
                    "<br>CAD Equivalent: $%{value:.3f}B"
                    "<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(
        title="Outstanding Term Debt by Currency — % of Portfolio",
        height=420,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=18, r=18, t=54, b=24),
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=INK),
        showlegend=False,
        annotations=[
            dict(
                text=f"Total CAD Eq.<br>{format_billions(total_cad_equivalent)}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color=INK),
            )
        ],
    )
    return fig


def build_average_term_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=df["currency"],
        y=df["average_term_years"],
        marker_color=[NAVY, BLUE, SKY, BLUE, SKY, BLUE, SKY, SKY],
        text=[f"{value:.1f} yrs" for value in df["average_term_years"]],
        textposition="outside",
        hovertemplate="%{x}<br>Average Term: %{y:.1f} years<extra></extra>",
    )
    fig.update_layout(title="Average Term by Currency")
    return apply_chart_theme(fig, height=420, yaxis_title="Average term (years)")


def build_money_market_chart(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=df["currency"],
        y=df["government_cash_management"],
        name="Government / Cash Management",
        marker_color=NAVY,
        hovertemplate="%{x}<br>Government / Cash Management: %{y:.3f}B<extra></extra>",
        secondary_y=False,
    )
    fig.add_bar(
        x=df["currency"],
        y=df["lending_to_provincial_corporations"],
        name="Lending to Provincial Corporations",
        marker_color=SKY,
        hovertemplate="%{x}<br>Lending to Provincial Corporations: %{y:.3f}B<extra></extra>",
        secondary_y=False,
    )
    fig.add_scatter(
        x=df["currency"],
        y=df["average_term_days"],
        name="Average Term Days",
        mode="lines+markers+text",
        marker=dict(size=9, color=SLATE),
        line=dict(width=2.5, color=SLATE),
        text=[f"{value:.0f} days" for value in df["average_term_days"]],
        textposition="top center",
        hovertemplate="%{x}<br>Average Term: %{y:.0f} days<extra></extra>",
        secondary_y=True,
    )
    fig.update_layout(
        barmode="stack",
        title="Money Market Debt",
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=18, r=18, t=54, b=24),
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=INK),
        hoverlabel=dict(bgcolor=SURFACE, font_color=INK),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            title=None,
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(size=12))
    fig.update_yaxes(
        title_text="Money market debt (billions)",
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(size=12),
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Average term (days)",
        showgrid=False,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(size=12),
        secondary_y=True,
    )
    return fig


st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@500;600&display=swap');

        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(79, 129, 189, 0.10), transparent 32%),
                linear-gradient(180deg, {CANVAS} 0%, #FFFFFF 28%);
            color: {INK};
            font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #F7FBFF 0%, #EDF4FA 100%);
            border-right: 1px solid {BORDER};
        }}

        .sidebar-brand {{
            padding: 0.35rem 0 1rem 0;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 1rem;
        }}

        .sidebar-title {{
            color: {NAVY};
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.35rem;
        }}

        .sidebar-text {{
            color: {MUTED};
            font-size: 0.92rem;
            line-height: 1.5;
        }}

        .section-block {{
            margin: 0.35rem 0 0.9rem 0;
        }}

        .section-title {{
            color: {NAVY};
            font-size: 1.18rem;
            font-weight: 700;
            margin-bottom: 0.28rem;
        }}

        .section-body {{
            color: {SLATE};
            font-size: 0.96rem;
            line-height: 1.6;
        }}

        .metric-card {{
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid {BORDER};
            border-top: 4px solid {NAVY};
            border-radius: 20px;
            padding: 1.1rem 1.15rem;
            min-height: 152px;
            box-shadow: 0 14px 28px rgba(31, 78, 121, 0.07);
        }}

        .metric-label {{
            color: {MUTED};
            font-size: 0.92rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
        }}

        .metric-value {{
            color: {INK};
            font-size: 1.68rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.55rem;
        }}

        .metric-note {{
            color: {SLATE};
            font-size: 0.9rem;
            line-height: 1.45;
        }}

        .insight-card {{
            background: rgba(220, 234, 247, 0.55);
            border: 1px solid rgba(31, 78, 121, 0.12);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-top: 0.55rem;
        }}

        .insight-label {{
            color: {NAVY};
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }}

        .insight-text {{
            color: {INK};
            font-size: 0.95rem;
            line-height: 1.55;
        }}

        .source-shell {{
            background: rgba(247, 251, 255, 0.92);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-top: 0.85rem;
        }}

        .source-title {{
            color: {NAVY};
            font-size: 0.84rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }}

        .source-line {{
            color: {SLATE};
            font-size: 0.9rem;
            line-height: 1.55;
        }}

        .source-line a {{
            color: {SLATE};
            text-decoration: none;
        }}

        .source-line a:hover {{
            color: {NAVY};
            text-decoration: underline;
        }}

        .summary-card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
            gap: 1rem;
        }}

        .summary-card {{
            background: rgba(255, 255, 255, 0.98);
            border: 1px solid {BORDER};
            border-radius: 22px;
            padding: 1.15rem 1.15rem 1.05rem;
            box-shadow: 0 14px 28px rgba(31, 78, 121, 0.08);
            min-height: 100%;
            position: relative;
            overflow: hidden;
        }}

        .summary-card::before {{
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 5px;
            background: var(--summary-card-accent, {NAVY});
        }}

        .summary-card-flow {{
            --summary-card-accent: #2B6CB0;
            background:
                radial-gradient(circle at top right, rgba(79, 129, 189, 0.14), transparent 32%),
                rgba(255, 255, 255, 0.98);
        }}

        .summary-card-stock {{
            --summary-card-accent: #0D7377;
            background:
                radial-gradient(circle at top right, rgba(20, 184, 166, 0.13), transparent 32%),
                rgba(255, 255, 255, 0.98);
        }}

        .summary-card-top {{
            display: flex;
            justify-content: flex-start;
            margin-bottom: 0.85rem;
        }}

        .summary-kpi-name {{
            color: {INK};
            font-weight: 700;
            font-size: 1.04rem;
            line-height: 1.45;
            margin-bottom: 0.25rem;
        }}

        .summary-kpi-note {{
            color: {SLATE};
            font-size: 0.9rem;
            font-style: italic;
            margin-bottom: 0.85rem;
        }}

        .summary-value-cell {{
            color: {NAVY};
            font-weight: 700;
            font-size: 2rem;
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 1rem;
        }}

        .summary-type-chip {{
            display: inline-block;
            min-width: 72px;
            padding: 0.35rem 0.78rem;
            border-radius: 999px;
            background: rgba(220, 234, 247, 0.72);
            color: {NAVY};
            font-size: 0.84rem;
            font-weight: 700;
            text-align: center;
        }}

        .summary-meta-grid {{
            display: grid;
            gap: 0.8rem;
        }}

        .summary-meta-block {{
            background: rgba(247, 251, 255, 0.76);
            border: 1px solid rgba(215, 225, 236, 0.88);
            border-radius: 16px;
            padding: 0.8rem 0.9rem;
        }}

        .summary-meta-label {{
            color: {MUTED};
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }}

        .summary-meta-text {{
            color: {INK};
            font-size: 0.92rem;
            line-height: 1.55;
        }}

        div[data-testid="stTabs"] {{
            margin-top: 0.35rem;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab-list"],
        div[data-testid="stTabs"] [role="tablist"] {{
            gap: 0.7rem;
            background: rgba(237, 244, 250, 0.92);
            border: 1px solid {BORDER};
            border-radius: 22px;
            padding: 0.45rem;
            box-shadow: 0 12px 26px rgba(31, 78, 121, 0.08);
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"],
        div[data-testid="stTabs"] [role="tab"] {{
            flex: 1 1 0;
            justify-content: center;
            min-height: 64px;
            padding: 0.95rem 1rem 0.85rem;
            background: rgba(255, 255, 255, 0.98);
            border: 1px solid {BORDER};
            border-radius: 16px;
            color: {SLATE};
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.25;
            transition: all 0.18s ease;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:hover,
        div[data-testid="stTabs"] [role="tab"]:hover {{
            border-color: {BLUE};
            color: {NAVY};
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(31, 78, 121, 0.08);
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"] p,
        div[data-testid="stTabs"] [role="tab"] p {{
            margin: 0;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
            background: transparent;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
            background: linear-gradient(135deg, {NAVY} 0%, {BLUE} 100%);
            border-color: {NAVY};
            color: #FFFFFF;
            box-shadow: 0 14px 28px rgba(31, 78, 121, 0.18);
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"]:hover,
        div[data-testid="stTabs"] [role="tab"][aria-selected="true"]:hover {{
            color: #FFFFFF;
            transform: none;
        }}

        .tab-theme-marker {{
            height: 0;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(1),
        div[data-testid="stTabs"] [role="tab"]:nth-child(1) {{
            background: rgba(31, 78, 121, 0.08);
            border-color: rgba(31, 78, 121, 0.18);
            color: #1F4E79;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(1)[aria-selected="true"],
        div[data-testid="stTabs"] [role="tab"]:nth-child(1)[aria-selected="true"] {{
            background: linear-gradient(135deg, #1F4E79 0%, #4F81BD 100%);
            border-color: #1F4E79;
            color: #FFFFFF;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(2),
        div[data-testid="stTabs"] [role="tab"]:nth-child(2) {{
            background: rgba(13, 115, 119, 0.08);
            border-color: rgba(13, 115, 119, 0.18);
            color: #0D7377;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(2)[aria-selected="true"],
        div[data-testid="stTabs"] [role="tab"]:nth-child(2)[aria-selected="true"] {{
            background: linear-gradient(135deg, #0D7377 0%, #14B8A6 100%);
            border-color: #0D7377;
            color: #FFFFFF;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(3),
        div[data-testid="stTabs"] [role="tab"]:nth-child(3) {{
            background: rgba(180, 83, 9, 0.08);
            border-color: rgba(180, 83, 9, 0.18);
            color: #B45309;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(3)[aria-selected="true"],
        div[data-testid="stTabs"] [role="tab"]:nth-child(3)[aria-selected="true"] {{
            background: linear-gradient(135deg, #B45309 0%, #F59E0B 100%);
            border-color: #B45309;
            color: #FFFFFF;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(4),
        div[data-testid="stTabs"] [role="tab"]:nth-child(4) {{
            background: rgba(157, 23, 77, 0.08);
            border-color: rgba(157, 23, 77, 0.18);
            color: #9D174D;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"]:nth-child(4)[aria-selected="true"],
        div[data-testid="stTabs"] [role="tab"]:nth-child(4)[aria-selected="true"] {{
            background: linear-gradient(135deg, #9D174D 0%, #E11D48 100%);
            border-color: #9D174D;
            color: #FFFFFF;
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.theme-executive),
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.theme-executive) {{
            --tab-accent: #1F4E79;
            --tab-soft: rgba(31, 78, 121, 0.08);
            --tab-card: rgba(220, 234, 247, 0.50);
            --tab-border: rgba(31, 78, 121, 0.16);
            --tab-shadow: rgba(31, 78, 121, 0.08);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.theme-funding),
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.theme-funding) {{
            --tab-accent: #0D7377;
            --tab-soft: rgba(13, 115, 119, 0.08);
            --tab-card: rgba(209, 250, 246, 0.55);
            --tab-border: rgba(13, 115, 119, 0.16);
            --tab-shadow: rgba(13, 115, 119, 0.08);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.theme-structure),
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.theme-structure) {{
            --tab-accent: #B45309;
            --tab-soft: rgba(180, 83, 9, 0.08);
            --tab-card: rgba(254, 243, 199, 0.58);
            --tab-border: rgba(180, 83, 9, 0.18);
            --tab-shadow: rgba(180, 83, 9, 0.08);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.theme-market),
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.theme-market) {{
            --tab-accent: #9D174D;
            --tab-soft: rgba(157, 23, 77, 0.08);
            --tab-card: rgba(251, 207, 232, 0.42);
            --tab-border: rgba(157, 23, 77, 0.16);
            --tab-shadow: rgba(157, 23, 77, 0.08);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker),
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) {{
            background: linear-gradient(180deg, var(--tab-soft) 0%, rgba(255, 255, 255, 0.78) 22%, rgba(255, 255, 255, 0.98) 100%);
            border: 1px solid var(--tab-border);
            border-top: 4px solid var(--tab-accent);
            border-radius: 26px;
            padding: 1rem 1rem 0.85rem;
            margin-top: 1rem;
            box-shadow: 0 14px 30px var(--tab-shadow);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .section-title,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .section-title {{
            color: var(--tab-accent);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .metric-card,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .metric-card {{
            border-top-color: var(--tab-accent);
            box-shadow: 0 14px 28px var(--tab-shadow);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .insight-card,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .insight-card {{
            background: var(--tab-card);
            border-color: var(--tab-border);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .insight-label,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .insight-label,
        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .summary-value-cell,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .summary-value-cell,
        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .source-title,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .source-title {{
            color: var(--tab-accent);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .summary-type-chip,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .summary-type-chip {{
            background: var(--tab-card);
            color: var(--tab-accent);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) .source-shell,
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) .source-shell {{
            background: linear-gradient(180deg, var(--tab-soft) 0%, rgba(255, 255, 255, 0.96) 100%);
            border-color: var(--tab-border);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) div[data-testid="stDataFrame"],
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) div[data-testid="stDataFrame"] {{
            border-color: var(--tab-border);
            box-shadow: 0 12px 24px var(--tab-shadow);
        }}

        div[data-testid="stTabs"] [role="tabpanel"]:has(.tab-theme-marker) div[data-testid="stPlotlyChart"],
        div[data-testid="stTabs"] [data-baseweb="tab-panel"]:has(.tab-theme-marker) div[data-testid="stPlotlyChart"] {{
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--tab-border);
            border-radius: 20px;
            padding: 0.3rem;
            box-shadow: 0 12px 22px var(--tab-shadow);
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid {BORDER};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


data = load_data()

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">Alberta TRM Financing Dashboard</div>
            <div class="sidebar-text">
                Treasury &amp; Risk Management / Director of Financing analytical view
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    topic_options = [
        "Executive Summary",
        "Borrowing Requirement Trend",
        "Debt Maturity Pressure",
        "Term Debt by Currency",
        "Average Term by Currency",
        "Money Market Debt",
        "Funding Programs & Market Access",
        "Credit Ratings",
    ]
    selected_topics = st.multiselect("Topics", topic_options, default=topic_options)
    selected_borrowing_years = st.multiselect(
        "Borrowing horizon",
        FY_ORDER,
        default=FY_ORDER,
    )
    selected_maturity_years = st.multiselect(
        "Maturity horizon",
        MATURITY_ORDER,
        default=MATURITY_ORDER,
    )
    show_tables = st.checkbox("Show supporting tables", value=True)

if not selected_topics:
    st.warning("Select at least one topic in the sidebar to populate the dashboard.")
    st.stop()


borrowing_filtered = data["borrowing"][
    data["borrowing"]["fiscal_year"].isin(selected_borrowing_years)
].copy()
maturities_filtered = data["maturities"][
    data["maturities"]["fiscal_year"].isin(selected_maturity_years)
].copy()

executive_tab, funding_tab, structure_tab, market_tab = st.tabs(
    [
        "Executive Summary",
        "Funding Outlook",
        "Debt Structure",
        "Market Access",
    ]
)

with executive_tab:
    st.markdown('<div class="tab-theme-marker theme-executive"></div>', unsafe_allow_html=True)
    if "Executive Summary" in selected_topics:
        st.markdown(
            section_heading(
                "1. Executive Summary",
                "Key financing flow and portfolio stock indicators are summarized below with their official source and management relevance.",
            ),
            unsafe_allow_html=True,
        )
        st.html(executive_summary_table(data["kpis"]))
    else:
        st.info("Executive Summary is currently hidden by the topic filter.")

with funding_tab:
    st.markdown('<div class="tab-theme-marker theme-funding"></div>', unsafe_allow_html=True)
    if "Borrowing Requirement Trend" in selected_topics:
        st.markdown(
            section_heading(
                "2. Borrowing Requirement Trend",
                "Borrowing requirements combine planned term issuance and money market net change across the fiscal planning horizon.",
            ),
            unsafe_allow_html=True,
        )
        if borrowing_filtered.empty:
            st.info("Select at least one borrowing year in the sidebar to display the funding trend.")
        else:
            st.plotly_chart(build_borrowing_chart(borrowing_filtered), use_container_width=True)
            st.markdown(
                insight_card(
                    "Borrowing requirements rise materially from $11.4B to a peak of $22.6B, indicating a higher-volume financing cycle."
                ),
                unsafe_allow_html=True,
            )
            if show_tables:
                borrowing_table = borrowing_filtered.copy()
                borrowing_table["Total Borrowing Requirement"] = borrowing_table[
                    "total_borrowing_requirement"
                ].map(format_billions)
                borrowing_table["Term Debt Planned"] = borrowing_table[
                    "term_debt_planned"
                ].map(format_billions)
                borrowing_table["Money Market Net Change"] = borrowing_table[
                    "money_market_net_change"
                ].map(format_billions)
                st.dataframe(
                    borrowing_table[
                        [
                            "fiscal_year",
                            "Total Borrowing Requirement",
                            "Term Debt Planned",
                            "Money Market Net Change",
                        ]
                    ].rename(columns={"fiscal_year": "Fiscal Year"}),
                    use_container_width=True,
                    hide_index=True,
                )

    if "Debt Maturity Pressure" in selected_topics:
        st.markdown(
            section_heading(
                "3. Debt Maturity Pressure",
                "Maturity concentration highlights the refinancing workload and liquidity planning burden in each fiscal year.",
            ),
            unsafe_allow_html=True,
        )
        if maturities_filtered.empty:
            st.info("Select at least one maturity year in the sidebar to display the maturity profile.")
        else:
            st.plotly_chart(build_maturity_chart(maturities_filtered), use_container_width=True)
            st.markdown(
                insight_card(
                    "2025-26 shows a significant maturity wall, increasing refinancing and liquidity-planning pressure."
                ),
                unsafe_allow_html=True,
            )
            if show_tables:
                maturity_table = maturities_filtered.copy()
                maturity_table["Long-Term Maturities"] = maturity_table[
                    "long_term_maturities"
                ].map(format_billions)
                maturity_table["Short-Term Maturities"] = maturity_table[
                    "short_term_maturities"
                ].map(format_billions)
                maturity_table["Total Maturities"] = maturity_table[
                    "total_maturities"
                ].map(format_billions)
                st.dataframe(
                    maturity_table[
                        [
                            "fiscal_year",
                            "Long-Term Maturities",
                            "Short-Term Maturities",
                            "Total Maturities",
                        ]
                    ].rename(columns={"fiscal_year": "Fiscal Year"}),
                    use_container_width=True,
                    hide_index=True,
                )

with structure_tab:
    st.markdown('<div class="tab-theme-marker theme-structure"></div>', unsafe_allow_html=True)
    if "Term Debt by Currency" in selected_topics:
        st.markdown(
            section_heading(
                "4. Term Debt by Currency",
                "Official native currency amounts are preserved for source fidelity, while cross-currency comparisons below use CAD-equivalent values based on June 17, 2026 FX rates.",
            ),
            unsafe_allow_html=True,
        )
        term_left, term_right = st.columns(2, gap="large")
        with term_left:
            st.plotly_chart(
                build_term_currency_cad_chart(data["term_currency"]),
                use_container_width=True,
            )
            st.caption(
                f"Converted from native currency using FX rates as of {TERM_DEBT_SOURCE_DATE}."
            )
        with term_right:
            st.plotly_chart(
                build_term_currency_share_chart(data["term_currency"]),
                use_container_width=True,
            )
        st.caption(
            "Source: Government of Alberta Investor Relations, Term Debt Outstanding as of June 17, 2026. "
            f"FX conversion based on {TERM_DEBT_FX_SOURCE_LABEL}, {TERM_DEBT_SOURCE_DATE}."
        )
        if show_tables:
            term_table = data["term_currency"].copy()
            st.dataframe(
                term_table[
                    [
                        "currency",
                        "native_display",
                        "fx_rate_display",
                        "fx_date_display",
                        "cad_equivalent_display",
                        "portfolio_share_display",
                    ]
                ].rename(
                    columns={
                        "currency": "Currency",
                        "native_display": "Official Native Outstanding",
                        "fx_rate_display": "FX Rate to CAD",
                        "fx_date_display": "FX Date Used",
                        "cad_equivalent_display": "CAD Equivalent",
                        "portfolio_share_display": "% of CAD-Equivalent Portfolio",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    if "Average Term by Currency" in selected_topics:
        st.markdown(
            section_heading(
                "5. Average Term by Currency",
                "Average term highlights where the debt book is longer-dated versus where refinancing recurs more frequently.",
            ),
            unsafe_allow_html=True,
        )
        st.plotly_chart(build_average_term_chart(data["average_term"]), use_container_width=True)
        st.markdown(
            insight_card(
                "CAD debt is longer-dated, while USD, SEK, and CHF exposures have shorter average terms, creating more frequent refinancing sensitivity."
            ),
            unsafe_allow_html=True,
        )

    if "Money Market Debt" in selected_topics:
        st.markdown(
            section_heading(
                "6. Money Market Debt",
                "Short-term borrowing supports government cash management needs and lending activity for provincial corporations.",
            ),
            unsafe_allow_html=True,
        )
        money_left, money_right = st.columns([1.2, 1], gap="large")
        with money_left:
            st.plotly_chart(build_money_market_chart(data["money_market"]), use_container_width=True)
        with money_right:
            money_table = data["money_market"].copy()
            money_table["Total Money Market Debt"] = money_table.apply(
                lambda row: format_billions(
                    row["total_money_market_debt"],
                    prefix="$" if row["currency"] == "CAD" else "US$",
                ),
                axis=1,
            )
            money_table["Government / Cash Management"] = money_table.apply(
                lambda row: format_billions(
                    row["government_cash_management"],
                    prefix="$" if row["currency"] == "CAD" else "US$",
                ),
                axis=1,
            )
            money_table["Lending to Provincial Corporations"] = money_table.apply(
                lambda row: format_billions(
                    row["lending_to_provincial_corporations"],
                    prefix="$" if row["currency"] == "CAD" else "US$",
                ),
                axis=1,
            )
            money_table["Average Term Days"] = money_table["average_term_days"].map(
                lambda value: f"{value:.0f}"
            )
            st.dataframe(
                money_table[
                    [
                        "currency",
                        "Total Money Market Debt",
                        "Government / Cash Management",
                        "Lending to Provincial Corporations",
                        "Average Term Days",
                    ]
                ].rename(columns={"currency": "Currency"}),
                use_container_width=True,
                hide_index=True,
            )
        st.markdown(
            insight_card(
                "Short-term borrowing activity is material, supporting the need for strong daily liquidity forecasting and trading desk support."
            ),
            unsafe_allow_html=True,
        )

with market_tab:
    st.markdown('<div class="tab-theme-marker theme-market"></div>', unsafe_allow_html=True)
    if "Funding Programs & Market Access" in selected_topics:
        st.markdown(
            section_heading(
                "7. Funding Programs & Market Access",
                "The Province maintains multiple funding programs to diversify investors, currencies and maturities.",
            ),
            unsafe_allow_html=True,
        )
        st.dataframe(
            data["funding_programs"][
                ["funding_program", "market", "purpose", "public_status"]
            ].rename(
                columns={
                    "funding_program": "Funding Program",
                    "market": "Market",
                    "purpose": "Purpose",
                    "public_status": "Public Status",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.html(
            source_footer(
                [("Government of Alberta Investor Relations", INVESTOR_RELATIONS_URL)]
            )
        )

    if "Credit Ratings" in selected_topics:
        st.markdown(
            section_heading(
                "8. Credit Ratings",
                "Official credit ratings, outlooks and latest public review dates are shown below as posted on Alberta Investor Relations.",
            ),
            unsafe_allow_html=True,
        )
        st.dataframe(
            data["ratings"].rename(
                columns={
                    "agency": "Agency",
                    "long_term_rating": "Long-term",
                    "short_term_rating": "Short-term",
                    "outlook": "Outlook",
                    "latest_review_date": "Latest Review Date",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown(
            insight_card(
                "Credit ratings directly influence borrowing costs and investor demand. Maintaining strong ratings supports efficient market access."
            ),
            unsafe_allow_html=True,
        )
        st.html(
            source_footer(
                [("Government of Alberta Investor Relations - Credit Ratings", INVESTOR_RELATIONS_URL)]
            )
        )
