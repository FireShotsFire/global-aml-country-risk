import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Add local package directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_data
from src.scoring import (
    calculate_score,
    risk_band,
    confidence_score,
    component_contributions,
    WEIGHTS,
)

# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------
st.set_page_config(
    page_title="Global AML/CFT Country Risk Index (GACRI)",
    page_icon="🌍",
    layout="wide",
)

# -------------------------------------------------------
# DATA LOADING & PREPROCESSING
# -------------------------------------------------------
df, sources = load_data()

numeric_columns = [
    "fatf_score",
    "eu_score",
    "effectiveness_score",
    "structural_score",
    "sanctions_score",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Calculate risk metrics
df["risk_score"] = df.apply(calculate_score, axis=1)
df["risk_band"] = df["risk_score"].apply(risk_band)
df["confidence"] = df.apply(confidence_score, axis=1)

# Load History & Change Datasets if available
history_path = os.path.join(os.path.dirname(__file__), "data", "history.csv")
changes_path = os.path.join(os.path.dirname(__file__), "data", "changes.csv")

history_df = pd.read_csv(history_path) if os.path.exists(history_path) else pd.DataFrame()
changes_df = pd.read_csv(changes_path) if os.path.exists(changes_path) else pd.DataFrame()

if not history_df.empty:
    history_df["assessment_date"] = pd.to_datetime(history_df["assessment_date"])
if not changes_df.empty:
    changes_df["event_date"] = pd.to_datetime(changes_df["event_date"])

# -------------------------------------------------------
# NAVIGATION TABS
# -------------------------------------------------------
tab_map, tab_changes, tab_methodology = st.tabs([
    "🌍 Interactive Risk Map & Deep Dive",
    "🔄 Regulatory Changes & Deltas",
    "📖 Methodology & Data Sources",
])

# -------------------------------------------------------
# TAB 1: INTERACTIVE MAP & DEEP DIVE
# -------------------------------------------------------
with tab_map:
    st.markdown("### 🌍 Global Jurisdictional Risk Overview")
    st.caption("Independent analytical framework integrating FATF, EU AMLR (Reg 2024/1624), Effectiveness & Structural Risk")

    # Sidebar Filter
    st.sidebar.title("Index Controls")
    risk_filter = st.sidebar.multiselect(
        "Filter by Risk Band",
        options=["Critical", "High", "Elevated", "Moderate", "Low"],
        default=["Critical", "High", "Elevated", "Moderate", "Low"],
    )

    filtered_df = df[df["risk_band"].isin(risk_filter)]

    # Choropleth Map
    fig = px.choropleth(
        filtered_df,
        locations="iso3",
        color="risk_score",
        hover_name="country",
        custom_data=["country", "iso3"],
        hover_data={
            "risk_score": ":.1f",
            "risk_band": True,
            "fatf_status": True,
            "eu_status": True,
            "confidence": ":.0f%",
            "iso3": False,
        },
        color_continuous_scale=[
            [0.00, "#238443"],
            [0.20, "#78c679"],
            [0.40, "#fdcc8a"],
            [0.60, "#fc8d59"],
            [0.80, "#d7301f"],
            [1.00, "#7f0000"],
        ],
        range_color=(0, 100),
        projection="natural earth",
    )

    fig.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=10, b=10),
        geo=dict(showframe=False, showcoastlines=True),
    )

    selected_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # Map Selection Interactivity
    default_country = "Germany"
    if selected_event and "selection" in selected_event and selected_event["selection"]["points"]:
        point = selected_event["selection"]["points"][0]
        if "customdata" in point:
            default_country = point["customdata"][0]

    st.divider()
    st.subheader("Jurisdiction Deep-Dive")

    countries_list = sorted(df["country"].unique())
    selected_index = countries_list.index(default_country) if default_country in countries_list else 0
    selected_country = st.selectbox("Select Jurisdiction:", countries_list, index=selected_index)

    country = df[df["country"] == selected_country].iloc[0]

    # Metrics Display
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Risk Score", f"{country['risk_score']:.1f} / 100")
    c2.metric("Risk Category", country["risk_band"])
    c3.metric("FATF Status", country["fatf_status"])
    c4.metric("Data Coverage", f"{country['confidence']}%")

    # Explainability Drawer ("Why?")
    with st.expander(f"🔍 Explainability Analysis: Why is {country['country']} rated {country['risk_band']}?", expanded=True):
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("#### Weighted Contribution Breakdown")
            contributions = component_contributions(country)
            contrib_df = pd.DataFrame(
                {"Component": list(contributions.keys()), "Points Contribution": list(contributions.values())}
            )
            st.dataframe(contrib_df, hide_index=True, use_container_width=True)

        with col_right:
            st.markdown("#### Key Drivers & Regulatory Status")
            st.markdown(f"- **FATF Listing:** `{country['fatf_status']}`")
            st.markdown(f"- **EU AMLR Designation:** `{country['eu_status']}`")
            st.markdown(f"- **Legal Basis:** *{country['legal_basis']}*")
            st.markdown(f"- **Effectiveness Score:** `{country['effectiveness_score']:.1f}/100`")
            st.markdown(f"- **Structural Risk:** `{country['structural_score']:.1f}/100`")

    # Historical Time-Series Chart
    if not history_df.empty:
        country_hist = history_df[history_df["iso3"] == country["iso3"]].sort_values("assessment_date")
        if not country_hist.empty:
            st.markdown("#### 📈 Risk Score Evolution Over Time")
            fig_hist = px.line(
                country_hist,
                x="assessment_date",
                y="overall_score",
                markers=True,
                text="overall_score",
                labels={"assessment_date": "Assessment Date", "overall_score": "Risk Score"},
            )
            fig_hist.update_traces(textposition="top center", line_color="#1a2b4c", line_width=3)
            fig_hist.update_yaxes(range=[0, 100])
            st.plotly_chart(fig_hist, use_container_width=True)

# -------------------------------------------------------
# TAB 2: REGULATORY CHANGES & DELTAS
# -------------------------------------------------------
with tab_changes:
    st.markdown("### 🔄 Regulatory Changes & Model Deltas")
    st.markdown("Track real-time FATF, EU AMLR, and effectiveness revisions affecting country scores.")

    if not changes_df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Events Logged", len(changes_df))
        m2.metric("Latest Regulatory Update", changes_df["event_date"].max().strftime("%Y-%m-%d"))
        m3.metric("Jurisdictions Affected", changes_df["iso3"].nunique())

        st.divider()

        for idx, row in changes_df.sort_values("event_date", ascending=False).iterrows():
            delta_sign = "+" if row["score_delta"] > 0 else ""
            card_title = (
                f"🗓️ {row['event_date'].strftime('%Y-%m-%d')} | {row['country']}"
                f" ({row['iso3']}) — {row['dimension']}: {row['change_type']}"
            )

            with st.expander(card_title, expanded=True):
                c_left, c_right = st.columns([3, 1])

                with c_left:
                    st.markdown(f"**Regulatory Movement:** `{row['previous_value']}` ➔ `{row['new_value']}`")
                    st.markdown(f"**Legal Basis / Authority:** *{row['legal_basis_or_source']}*")
                    st.markdown(f"**Analyst Notes:** {row['summary_notes']}")

                with c_right:
                    st.metric("Composite Impact", f"{delta_sign}{row['score_delta']:.1f} pts")
                    st.caption(f"Component Shift: {row['previous_score']} ➔ {row['new_score']}")
    else:
        st.info("No regulatory change deltas logged yet.")

# -------------------------------------------------------
# TAB 3: METHODOLOGY & SOURCES
# -------------------------------------------------------
with tab_methodology:
    st.markdown("### 📚 Methodology & Sources Lineage")
    st.markdown("""
    #### Weighting Framework (v1.0)
    | Component | Weight | Standard / Source |
    |---|---:|---|
    | **FATF Listing** | **35%** | FATF Plenary Statements (Call for Action / Increased Monitoring) |
    | **EU AMLR** | **30%** | Regulation (EU) 2024/1624 (Articles 29, 30, 31 & Annex III) |
    | **AML/CFT Effectiveness** | **20%** | FATF Mutual Evaluations (Immediate Outcomes 1–11) |
    | **Structural Risk** | **10%** | Transparency International CPI / Institutional Governance |
    | **Sanctions / PF** | **5%** | UN Consolidated Sanctions & Proliferation Financing Indicators |
    """)

    st.markdown("#### Primary Data Sources")
    if not sources.empty:
        st.dataframe(sources, hide_index=True, use_container_width=True)

st.caption("Global AML/CFT Country Risk Index (GACRI) | Engine v1.0 | Open Analytical Standard")
