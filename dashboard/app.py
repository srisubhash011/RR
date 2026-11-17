"""
PRESSUREIQ – Cricket Pressure Intelligence Dashboard
SupeRR Selector Season 2 – Round 1
Professional Dark-Themed Sports Analytics Interface built with Streamlit & Plotly.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="PRESSUREIQ | Cricket Pressure Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Sports Analytics CSS
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Metrics cards */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.82rem;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 700;
        font-size: 1.6rem;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #1e293b;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        font-weight: 600;
        border-radius: 6px;
        padding: 6px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_dashboard_data():
    top_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
    top_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')
    all_bat = pd.read_csv('outputs/rankings/all_batters_ranked.csv')
    all_bowl = pd.read_csv('outputs/rankings/all_bowlers_ranked.csv')
    audit_df = pd.read_csv('outputs/audit/data_quality_report.csv')
    comp_audit = pd.read_csv('outputs/audit/competition_audit.csv')
    metrics_df = pd.read_csv('outputs/audit/model_evaluation_metrics.csv')
    sens_df = pd.read_csv('outputs/audit/sensitivity_analysis.csv')
    baselines = pd.read_csv('outputs/analytical/player_baselines.csv')
    
    # Load deliveries (parquet or sample)
    if os.path.exists('outputs/analytical/delivery_pressure_features.parquet'):
        deliveries = pd.read_parquet('outputs/analytical/delivery_pressure_features.parquet')
    else:
        deliveries = pd.read_csv('outputs/analytical/delivery_pressure_features.csv')
        
    return {
        'top_bat': top_bat,
        'top_bowl': top_bowl,
        'all_bat': all_bat,
        'all_bowl': all_bowl,
        'audit': audit_df,
        'comp_audit': comp_audit,
        'metrics': metrics_df,
        'sens': sens_df,
        'baselines': baselines,
        'deliveries': deliveries
    }

data = load_dashboard_data()

# -----------------------------------------------------------------------------
# Navigation Sidebar
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/cricket.png", width=60)
st.sidebar.title("PRESSUREIQ")
st.sidebar.caption("SupeRR Selector Season 2 – Round 1")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation Menu",
    [
        "1. Executive Overview",
        "2. Pressure Intelligence",
        "3. Top Batters Under Pressure",
        "4. Top Bowlers Under Pressure",
        "5. Individual Player Intelligence",
        "6. Head-to-Head Comparison",
        "7. Match Evidence & Explainability"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.8rem; color: #64748b;'>
<b>Model Specs:</b><br/>
• 193,988 Deliveries Analyzed<br/>
• 837 Total Matches (2022–2026)<br/>
• 5-Fold GroupKFold Expectation<br/>
• Bayesian Shrinkage Prior (k=25)<br/>
• 500-Iteration Bootstrap CIs
</div>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =============================================================================
if page == "1. Executive Overview":
    st.title("🏏 PRESSUREIQ: Executive Overview")
    st.markdown("##### Context-Aware Cricket Pressure & Player Reliability Analytics Engine")
    st.markdown("---")
    
    # Top KPI Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Matches Analyzed", "837", "IPL & T20I (2022-26)")
    c2.metric("Deliveries Evaluated", "193,988", "100% Pre-Delivery")
    c3.metric("Eligible Batters", f"{len(data['all_bat'])}", "Min 75 Pressure Balls")
    c4.metric("Eligible Bowlers", f"{len(data['all_bowl'])}", "Min 60 Pressure Balls")
    c5.metric("Model Leakage", "0.0%", "GroupKFold by Match")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("🏆 Official Top 10 Batters")
        bat_display = data['top_bat'][['rank', 'striker_name', 'final_rating', 'pressure_strike_rate', 'normal_strike_rate', 'adj_delta_sr', 'pressure_runs', 'ci_lower', 'ci_upper']].rename(
            columns={
                'rank': 'Rank',
                'striker_name': 'Batter',
                'final_rating': 'Rating',
                'pressure_strike_rate': 'Press SR',
                'normal_strike_rate': 'Norm SR',
                'adj_delta_sr': 'Δ SR',
                'pressure_runs': 'Runs',
                'ci_lower': 'CI Low',
                'ci_upper': 'CI High'
            }
        )
        st.dataframe(bat_display, use_container_width=True, hide_index=True)
        
    with col_right:
        st.subheader("🎯 Official Top 10 Bowlers")
        bowl_display = data['top_bowl'][['rank', 'bowler_name', 'final_rating', 'pressure_economy', 'normal_economy', 'adj_delta_econ', 'pressure_wickets', 'ci_lower', 'ci_upper']].rename(
            columns={
                'rank': 'Rank',
                'bowler_name': 'Bowler',
                'final_rating': 'Rating',
                'pressure_economy': 'Press Econ',
                'normal_economy': 'Norm Econ',
                'adj_delta_econ': 'Δ Econ',
                'pressure_wickets': 'Wickets',
                'ci_lower': 'CI Low',
                'ci_upper': 'CI High'
            }
        )
        st.dataframe(bowl_display, use_container_width=True, hide_index=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Visual Highlights
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("#### Pressure Distribution Breakdown")
        bat_dist = data['deliveries']['batting_pressure_cat'].value_counts()
        fig_pie = px.pie(
            names=bat_dist.index,
            values=bat_dist.values,
            color=bat_dist.index,
            color_discrete_map={'low': '#3b82f6', 'moderate': '#eab308', 'high': '#f97316', 'extreme': '#ef4444'},
            hole=0.45,
            title="Batting Deliveries by Pressure Tier"
        )
        fig_pie.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with ch2:
        st.markdown("#### IPL vs. T20I Competition Scope")
        fmt_counts = data['deliveries']['format_type'].value_counts()
        fig_bar = px.bar(
            x=fmt_counts.index,
            y=fmt_counts.values,
            color=fmt_counts.index,
            color_discrete_map={'IPL': '#6366f1', 'T20I': '#06b6d4'},
            labels={'x': 'Competition Format', 'y': 'Deliveries Analyzed'},
            title="Dataset Coverage by Tournament Tier"
        )
        fig_bar.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# =============================================================================
# PAGE 2: PRESSURE INTELLIGENCE
# =============================================================================
elif page == "2. Pressure Intelligence":
    st.title("⚡ Pressure Intelligence & Scenario Dynamics")
    st.markdown("##### Detailed breakdown of pre-delivery pressure scenarios across innings and match stages")
    st.markdown("---")
    
    # Filter Controls
    f1, f2, f3 = st.columns(3)
    sel_format = f1.selectbox("Filter Format", ["All", "IPL", "T20I"])
    sel_stage = f2.selectbox("Filter Innings Stage", ["All", "powerplay", "middle", "death"])
    sel_inn = f3.selectbox("Filter Innings", ["All", "1st Innings", "2nd Innings"])
    
    filtered_df = data['deliveries'].copy()
    if sel_format != "All":
        filtered_df = filtered_df[filtered_df['format_type'] == sel_format]
    if sel_stage != "All":
        filtered_df = filtered_df[filtered_df['innings_stage'] == sel_stage]
    if sel_inn == "1st Innings":
        filtered_df = filtered_df[filtered_df['innings'] == 1]
    elif sel_inn == "2nd Innings":
        filtered_df = filtered_df[filtered_df['innings'] == 2]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Batting Pressure by Dominant Scenario")
        bat_scen = filtered_df['dominant_batting_scenario'].value_counts()
        fig_scen_bat = px.bar(
            x=bat_scen.index,
            y=bat_scen.values,
            color=bat_scen.index,
            labels={'x': 'Scenario', 'y': 'Delivery Count'},
            title="Dominant Batting Pressure Scenarios"
        )
        fig_scen_bat.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'), showlegend=False)
        st.plotly_chart(fig_scen_bat, use_container_width=True)
        
    with c2:
        st.subheader("Bowling Pressure by Dominant Scenario")
        bowl_scen = filtered_df['dominant_bowling_scenario'].value_counts()
        fig_scen_bowl = px.bar(
            x=bowl_scen.index,
            y=bowl_scen.values,
            color=bowl_scen.index,
            labels={'x': 'Scenario', 'y': 'Delivery Count'},
            title="Dominant Bowling Pressure Scenarios"
        )
        fig_scen_bowl.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'), showlegend=False)
        st.plotly_chart(fig_scen_bowl, use_container_width=True)

    st.markdown("---")
    st.subheader("Pressure Distribution by Innings Stage")
    fig_box = px.box(
        filtered_df,
        x='innings_stage',
        y='batting_pressure_score',
        color='innings_stage',
        title="Batting Pressure Variation Across Match Phases",
        labels={'innings_stage': 'Match Phase', 'batting_pressure_score': 'Batting Pressure Score (0 - 100)'}
    )
    fig_box.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'), showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# =============================================================================
# PAGE 3: TOP BATTERS UNDER PRESSURE
# =============================================================================
elif page == "3. Top Batters Under Pressure":
    st.title("🥇 Top Batters Under Pressure")
    st.markdown("##### Multi-dimensional ranking of the most reliable batters in high-pressure match situations")
    st.markdown("---")
    
    # Ranked Table with search filter
    search_q = st.text_input("🔍 Search Batter Name", "")
    display_df = data['all_bat'].copy()
    if search_q:
        display_df = display_df[display_df['striker_name'].str.contains(search_q, case=False)]
        
    table_cols = [
        'rank', 'striker_name', 'final_rating', 'pressure_strike_rate', 'normal_strike_rate',
        'adj_delta_sr', 'pressure_balls_faced', 'pressure_runs', 'impact_score',
        'resilience_score', 'consistency_score', 'sample_confidence_score', 'collapse_resistance_score',
        'ci_lower', 'ci_upper'
    ]
    renamed = display_df[table_cols].rename(columns={
        'rank': 'Rank',
        'striker_name': 'Batter',
        'final_rating': 'Rating',
        'pressure_strike_rate': 'Press SR',
        'normal_strike_rate': 'Norm SR',
        'adj_delta_sr': 'Δ SR',
        'pressure_balls_faced': 'Balls',
        'pressure_runs': 'Runs',
        'impact_score': 'Impact',
        'resilience_score': 'Resilience',
        'consistency_score': 'Consistency',
        'sample_confidence_score': 'Confidence',
        'collapse_resistance_score': 'Collapse Res.',
        'ci_lower': 'CI Low',
        'ci_upper': 'CI High'
    })
    
    st.dataframe(renamed, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Top 10 Batters: Pressure Strike Rate vs. Resilience")
    fig_scat = px.scatter(
        data['top_bat'],
        x='pressure_strike_rate',
        y='resilience_score',
        size='pressure_runs',
        color='final_rating',
        text='striker_name',
        title="Top 10 Batters: Aggression vs. Resilience",
        labels={'pressure_strike_rate': 'Pressure Strike Rate', 'resilience_score': 'Resilience Score (0 - 100)'}
    )
    fig_scat.update_traces(textposition='top center')
    fig_scat.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'))
    st.plotly_chart(fig_scat, use_container_width=True)

# =============================================================================
# PAGE 4: TOP BOWLERS UNDER PRESSURE
# =============================================================================
elif page == "4. Top Bowlers Under Pressure":
    st.title("🎯 Top Bowlers Under Pressure")
    st.markdown("##### Multi-dimensional ranking of the most reliable bowlers defending targets and restricting attacks")
    st.markdown("---")
    
    search_qb = st.text_input("🔍 Search Bowler Name", "")
    display_bowl = data['all_bowl'].copy()
    if search_qb:
        display_bowl = display_bowl[display_bowl['bowler_name'].str.contains(search_qb, case=False)]
        
    table_cols_b = [
        'rank', 'bowler_name', 'final_rating', 'pressure_economy', 'normal_economy',
        'adj_delta_econ', 'pressure_legal_balls', 'pressure_wickets', 'impact_score',
        'resilience_score', 'consistency_score', 'sample_confidence_score', 'aggression_resistance_score',
        'ci_lower', 'ci_upper'
    ]
    renamed_b = display_bowl[table_cols_b].rename(columns={
        'rank': 'Rank',
        'bowler_name': 'Bowler',
        'final_rating': 'Rating',
        'pressure_economy': 'Press Econ',
        'normal_economy': 'Norm Econ',
        'adj_delta_econ': 'Δ Econ',
        'pressure_legal_balls': 'Balls',
        'pressure_wickets': 'Wickets',
        'impact_score': 'Impact',
        'resilience_score': 'Resilience',
        'consistency_score': 'Consistency',
        'sample_confidence_score': 'Confidence',
        'aggression_resistance_score': 'Aggression Res.',
        'ci_lower': 'CI Low',
        'ci_upper': 'CI High'
    })
    
    st.dataframe(renamed_b, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Top 10 Bowlers: Economy vs. Wickets")
    fig_scat_b = px.scatter(
        data['top_bowl'],
        x='pressure_economy',
        y='pressure_wickets',
        size='pressure_legal_balls',
        color='final_rating',
        text='bowler_name',
        title="Top 10 Bowlers: Pressure Economy vs. Total Pressure Wickets",
        labels={'pressure_economy': 'Pressure Economy (Lower is Better)', 'pressure_wickets': 'Pressure Wickets Taken'}
    )
    fig_scat_b.update_traces(textposition='top center')
    fig_scat_b.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'))
    st.plotly_chart(fig_scat_b, use_container_width=True)

# =============================================================================
# PAGE 5: INDIVIDUAL PLAYER INTELLIGENCE
# =============================================================================
elif page == "5. Individual Player Intelligence":
    st.title("👤 Player Intelligence Deep Dive")
    st.markdown("##### Comprehensive situational diagnostic and match-by-match profile for any player")
    st.markdown("---")
    
    role = st.radio("Select Role", ["Batter", "Bowler"], horizontal=True)
    
    if role == "Batter":
        player_list = data['all_bat']['striker_name'].tolist()
        sel_player = st.selectbox("Select Batter", player_list, index=0)
        p_row = data['all_bat'][data['all_bat']['striker_name'] == sel_player].iloc[0]
        
        # Profile header
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Rank", f"#{int(p_row['rank'])}", f"Rating: {p_row['final_rating']:.2f}")
        c2.metric("Pressure SR", f"{p_row['pressure_strike_rate']:.1f}", f"Normal: {p_row['normal_strike_rate']:.1f}")
        c3.metric("Δ Strike Rate", f"{p_row['adj_delta_sr']:+.1f}", "Vs Shrunk Baseline")
        c4.metric("90% CI", f"[{p_row['ci_lower']:.1f}, {p_row['ci_upper']:.1f}]", "Bootstrap Range")
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        col_rad, col_bar = st.columns([1, 1])
        with col_rad:
            st.markdown("#### Five Reliability Dimensions (0 - 100)")
            categories = ['Impact', 'Resilience', 'Consistency', 'Confidence', 'Collapse Resistance']
            values = [
                p_row['impact_score'], p_row['resilience_score'],
                p_row['consistency_score'], p_row['sample_confidence_score'],
                p_row['collapse_resistance_score']
            ]
            fig_rad = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(56, 189, 248, 0.3)',
                line=dict(color='#38bdf8', width=2)
            ))
            fig_rad.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155'),
                    bgcolor='#0f172a'
                ),
                paper_bgcolor='#0f172a',
                font=dict(color='#cbd5e1')
            )
            st.plotly_chart(fig_rad, use_container_width=True)
            
        with col_bar:
            st.markdown("#### Normal vs. Pressure Output Comparison")
            comp_df = pd.DataFrame({
                'Metric': ['Strike Rate', 'Dot Ball %', 'Boundary %'],
                'Normal': [p_row['normal_strike_rate'], p_row['normal_dot_pct'], p_row['normal_boundary_pct']],
                'Pressure': [p_row['pressure_strike_rate'], p_row['pressure_dot_pct'], p_row['pressure_boundary_pct']]
            })
            fig_comp = px.bar(
                comp_df.melt(id_vars='Metric', var_name='Context', value_name='Rate'),
                x='Metric',
                y='Rate',
                color='Context',
                barmode='group',
                color_discrete_map={'Normal': '#94a3b8', 'Pressure': '#38bdf8'}
            )
            fig_comp.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'))
            st.plotly_chart(fig_comp, use_container_width=True)

    else:
        player_list = data['all_bowl']['bowler_name'].tolist()
        sel_player = st.selectbox("Select Bowler", player_list, index=0)
        p_row = data['all_bowl'][data['all_bowl']['bowler_name'] == sel_player].iloc[0]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Rank", f"#{int(p_row['rank'])}", f"Rating: {p_row['final_rating']:.2f}")
        c2.metric("Pressure Economy", f"{p_row['pressure_economy']:.2f}", f"Normal: {p_row['normal_economy']:.2f}")
        c3.metric("Δ Economy", f"{p_row['adj_delta_econ']:+.2f}", "Tighter is Better")
        c4.metric("90% CI", f"[{p_row['ci_lower']:.1f}, {p_row['ci_upper']:.1f}]", "Bootstrap Range")
        
        st.markdown("<br/>", unsafe_allow_html=True)
        col_rad, col_bar = st.columns([1, 1])
        with col_rad:
            st.markdown("#### Five Reliability Dimensions (0 - 100)")
            categories = ['Impact', 'Resilience', 'Consistency', 'Confidence', 'Aggression Resistance']
            values = [
                p_row['impact_score'], p_row['resilience_score'],
                p_row['consistency_score'], p_row['sample_confidence_score'],
                p_row['aggression_resistance_score']
            ]
            fig_rad = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(248, 113, 113, 0.3)',
                line=dict(color='#f87171', width=2)
            ))
            fig_rad.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155'),
                    bgcolor='#0f172a'
                ),
                paper_bgcolor='#0f172a',
                font=dict(color='#cbd5e1')
            )
            st.plotly_chart(fig_rad, use_container_width=True)
            
        with col_bar:
            st.markdown("#### Normal vs. Pressure Economy & Control")
            comp_df = pd.DataFrame({
                'Metric': ['Economy', 'Dot Ball %', 'Boundary Conceded %'],
                'Normal': [p_row['normal_economy'], p_row['normal_dot_pct'], p_row['normal_boundary_pct']],
                'Pressure': [p_row['pressure_economy'], p_row['pressure_dot_pct'], p_row['pressure_boundary_pct']]
            })
            fig_comp = px.bar(
                comp_df.melt(id_vars='Metric', var_name='Context', value_name='Rate'),
                x='Metric',
                y='Rate',
                color='Context',
                barmode='group',
                color_discrete_map={'Normal': '#94a3b8', 'Pressure': '#f87171'}
            )
            fig_comp.update_layout(paper_bgcolor='#0f172a', plot_bgcolor='#0f172a', font=dict(color='#cbd5e1'))
            st.plotly_chart(fig_comp, use_container_width=True)

# =============================================================================
# PAGE 6: HEAD-TO-HEAD COMPARISON
# =============================================================================
elif page == "6. Head-to-Head Comparison":
    st.title("⚔️ Head-to-Head Player Comparison")
    st.markdown("##### Compare two players across multi-dimensional pressure metrics")
    st.markdown("---")
    
    role = st.radio("Comparison Discipline", ["Batters", "Bowlers"], horizontal=True)
    
    if role == "Batters":
        p_list = data['all_bat']['striker_name'].tolist()
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Select Player A", p_list, index=0)
        p2 = c2.selectbox("Select Player B", p_list, index=1)
        
        row1 = data['all_bat'][data['all_bat']['striker_name'] == p1].iloc[0]
        row2 = data['all_bat'][data['all_bat']['striker_name'] == p2].iloc[0]
        
        categories = ['Impact', 'Resilience', 'Consistency', 'Confidence', 'Collapse Resistance']
        v1 = [row1['impact_score'], row1['resilience_score'], row1['consistency_score'], row1['sample_confidence_score'], row1['collapse_resistance_score']]
        v2 = [row2['impact_score'], row2['resilience_score'], row2['consistency_score'], row2['sample_confidence_score'], row2['collapse_resistance_score']]
        
        fig_h2h = go.Figure()
        fig_h2h.add_trace(go.Scatterpolar(r=v1 + [v1[0]], theta=categories + [categories[0]], fill='toself', name=p1, line=dict(color='#38bdf8')))
        fig_h2h.add_trace(go.Scatterpolar(r=v2 + [v2[0]], theta=categories + [categories[0]], fill='toself', name=p2, line=dict(color='#f43f5e')))
        fig_h2h.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155'), bgcolor='#0f172a'),
            paper_bgcolor='#0f172a', font=dict(color='#cbd5e1'), title="Reliability Dimension Radar Overlay"
        )
        st.plotly_chart(fig_h2h, use_container_width=True)
        
        # Comparison Table
        h2h_data = {
            'Metric': ['Overall Rank', 'Final Rating', 'Pressure Strike Rate', 'Normal Strike Rate', 'Δ Strike Rate', 'Pressure Balls Faced', 'Pressure Runs Scored', '90% CI'],
            p1: [f"#{int(row1['rank'])}", f"{row1['final_rating']:.2f}", f"{row1['pressure_strike_rate']:.1f}", f"{row1['normal_strike_rate']:.1f}", f"{row1['adj_delta_sr']:+.1f}", f"{int(row1['pressure_balls_faced'])}", f"{int(row1['pressure_runs'])}", f"[{row1['ci_lower']:.1f}, {row1['ci_upper']:.1f}]"],
            p2: [f"#{int(row2['rank'])}", f"{row2['final_rating']:.2f}", f"{row2['pressure_strike_rate']:.1f}", f"{row2['normal_strike_rate']:.1f}", f"{row2['adj_delta_sr']:+.1f}", f"{int(row2['pressure_balls_faced'])}", f"{int(row2['pressure_runs'])}", f"[{row2['ci_lower']:.1f}, {row2['ci_upper']:.1f}]"]
        }
        st.dataframe(pd.DataFrame(h2h_data), use_container_width=True, hide_index=True)

    else:
        p_list = data['all_bowl']['bowler_name'].tolist()
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Select Player A", p_list, index=0)
        p2 = c2.selectbox("Select Player B", p_list, index=2)
        
        row1 = data['all_bowl'][data['all_bowl']['bowler_name'] == p1].iloc[0]
        row2 = data['all_bowl'][data['all_bowl']['bowler_name'] == p2].iloc[0]
        
        categories = ['Impact', 'Resilience', 'Consistency', 'Confidence', 'Aggression Resistance']
        v1 = [row1['impact_score'], row1['resilience_score'], row1['consistency_score'], row1['sample_confidence_score'], row1['aggression_resistance_score']]
        v2 = [row2['impact_score'], row2['resilience_score'], row2['consistency_score'], row2['sample_confidence_score'], row2['aggression_resistance_score']]
        
        fig_h2h = go.Figure()
        fig_h2h.add_trace(go.Scatterpolar(r=v1 + [v1[0]], theta=categories + [categories[0]], fill='toself', name=p1, line=dict(color='#38bdf8')))
        fig_h2h.add_trace(go.Scatterpolar(r=v2 + [v2[0]], theta=categories + [categories[0]], fill='toself', name=p2, line=dict(color='#f43f5e')))
        fig_h2h.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155'), bgcolor='#0f172a'),
            paper_bgcolor='#0f172a', font=dict(color='#cbd5e1'), title="Reliability Dimension Radar Overlay"
        )
        st.plotly_chart(fig_h2h, use_container_width=True)
        
        h2h_data_b = {
            'Metric': ['Overall Rank', 'Final Rating', 'Pressure Economy', 'Normal Economy', 'Δ Economy', 'Pressure Balls Bowled', 'Pressure Wickets Taken', '90% CI'],
            p1: [f"#{int(row1['rank'])}", f"{row1['final_rating']:.2f}", f"{row1['pressure_economy']:.2f}", f"{row1['normal_economy']:.2f}", f"{row1['adj_delta_econ']:+.2f}", f"{int(row1['pressure_legal_balls'])}", f"{int(row1['pressure_wickets'])}", f"[{row1['ci_lower']:.1f}, {row1['ci_upper']:.1f}]"],
            p2: [f"#{int(row2['rank'])}", f"{row2['final_rating']:.2f}", f"{row2['pressure_economy']:.2f}", f"{row2['normal_economy']:.2f}", f"{row2['adj_delta_econ']:+.2f}", f"{int(row2['pressure_legal_balls'])}", f"{int(row2['pressure_wickets'])}", f"[{row2['ci_lower']:.1f}, {row2['ci_upper']:.1f}]"]
        }
        st.dataframe(pd.DataFrame(h2h_data_b), use_container_width=True, hide_index=True)

# =============================================================================
# PAGE 7: MATCH EVIDENCE & EXPLAINABILITY
# =============================================================================
elif page == "7. Match Evidence & Explainability":
    st.title("📋 Match Evidence & Delivery Explainability")
    st.markdown("##### Inspect actual historical deliveries that substantiate individual player rankings")
    st.markdown("---")
    
    role = st.selectbox("Select Role to Inspect", ["Batting Evidence", "Bowling Evidence"])
    
    if role == "Batting Evidence":
        top_names = data['top_bat']['striker_name'].head(10).tolist()
        player_sel = st.selectbox("Select Batter to Audit", top_names, index=0)
        
        # Filter deliveries for this player under pressure
        p_balls = data['deliveries'][
            (data['deliveries']['striker_name'] == player_sel) &
            (data['deliveries']['batting_pressure_score'] >= 35.0)
        ].copy()
        
        st.markdown(f"**Found {len(p_balls):,} high-pressure deliveries for {player_sel}:**")
        
        sample_display = p_balls[[
            'match_id', 'innings', 'overid', 'over_ball_num', 'bowler_name', 'format_type',
            'score_before', 'wickets_before', 'batting_pressure_score', 'batting_pressure_cat',
            'dominant_batting_scenario', 'batter_runs', 'exp_batter_runs', 'batting_impact'
        ]].sort_values('batting_pressure_score', ascending=False).head(50).rename(columns={
            'match_id': 'Match ID',
            'innings': 'Inn',
            'overid': 'Over',
            'over_ball_num': 'Ball',
            'bowler_name': 'Bowler Faced',
            'format_type': 'Format',
            'score_before': 'Score Before',
            'wickets_before': 'Wkts Before',
            'batting_pressure_score': 'Pressure Score',
            'batting_pressure_cat': 'Tier',
            'dominant_batting_scenario': 'Scenario',
            'batter_runs': 'Actual Runs',
            'exp_batter_runs': 'Expected Runs',
            'batting_impact': 'Impact (Act - Exp)'
        })
        st.dataframe(sample_display, use_container_width=True, hide_index=True)

    else:
        top_names_b = data['top_bowl']['bowler_name'].head(10).tolist()
        player_sel_b = st.selectbox("Select Bowler to Audit", top_names_b, index=0)
        
        p_balls_b = data['deliveries'][
            (data['deliveries']['bowler_name'] == player_sel_b) &
            (data['deliveries']['bowling_pressure_score'] >= 35.0)
        ].copy()
        
        st.markdown(f"**Found {len(p_balls_b):,} high-pressure deliveries for {player_sel_b}:**")
        
        sample_display_b = p_balls_b[[
            'match_id', 'innings', 'overid', 'over_ball_num', 'striker_name', 'format_type',
            'score_before', 'wickets_before', 'bowling_pressure_score', 'bowling_pressure_cat',
            'dominant_bowling_scenario', 'bowler_runs_conceded', 'exp_bowler_runs', 'bowling_impact'
        ]].sort_values('bowling_pressure_score', ascending=False).head(50).rename(columns={
            'match_id': 'Match ID',
            'innings': 'Inn',
            'overid': 'Over',
            'over_ball_num': 'Ball',
            'striker_name': 'Striker Faced',
            'format_type': 'Format',
            'score_before': 'Score Before',
            'wickets_before': 'Wkts Before',
            'bowling_pressure_score': 'Pressure Score',
            'bowling_pressure_cat': 'Tier',
            'dominant_bowling_scenario': 'Scenario',
            'bowler_runs_conceded': 'Runs Conceded',
            'exp_bowler_runs': 'Expected Runs',
            'bowling_impact': 'Impact (Saved)'
        })
        st.dataframe(sample_display_b, use_container_width=True, hide_index=True)

