"""
Visualization and Chart Generation Module for PRESSUREIQ.
Generates publication-quality charts for the methodology report and interactive analytics dashboard.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# Set professional styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def generate_all_charts():
    """Generates and saves all required charts to outputs/charts/."""
    print("[Charts] Generating publication-quality charts for PRESSUREIQ...")
    os.makedirs('outputs/charts', exist_ok=True)
    
    # Load required analytical outputs
    top_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
    top_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')
    all_bat = pd.read_csv('outputs/rankings/all_batters_ranked.csv')
    all_bowl = pd.read_csv('outputs/rankings/all_bowlers_ranked.csv')
    
    # Load sample delivery pressure features
    df_p = pd.read_csv('outputs/analytical/delivery_pressure_features.csv', nrows=50000)

    # -------------------------------------------------------------------------
    # Chart 1: Pressure Distribution Histogram
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    ax.hist(df_p['batting_pressure_score'], bins=40, alpha=0.6, color='#1f77b4', label='Batting Pressure Score', density=True)
    ax.hist(df_p['bowling_pressure_score'], bins=40, alpha=0.6, color='#d62728', label='Bowling Pressure Score', density=True)
    ax.axvline(35, color='#ff7f0e', linestyle='--', linewidth=1.5, label='Moderate Pressure Threshold (35)')
    ax.axvline(60, color='#2ca02c', linestyle='--', linewidth=1.5, label='High Pressure Threshold (60)')
    ax.axvline(80, color='#9467bd', linestyle='--', linewidth=1.5, label='Extreme Pressure Threshold (80)')
    ax.set_title('Context-Aware Pressure Score Distributions (0 - 100)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Pressure Score', fontsize=10)
    ax.set_ylabel('Probability Density', fontsize=10)
    ax.legend(loc='upper right', frameon=True, fontsize=8)
    plt.tight_layout()
    fig.savefig('outputs/charts/pressure_distribution.png')
    plt.close()

    # -------------------------------------------------------------------------
    # Chart 2: Top 10 Batters Reliability Ratings & CIs (Forest Plot)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    y_pos = np.arange(len(top_bat))[::-1]
    ratings = top_bat['final_rating'].values
    ci_low = top_bat['ci_lower'].values
    ci_high = top_bat['ci_upper'].values
    names = top_bat['striker_name'].values
    
    xerr = [ratings - ci_low, ci_high - ratings]
    ax.errorbar(ratings, y_pos, xerr=xerr, fmt='o', color='#1f77b4', ecolor='#aec7e8', elinewidth=2.5, capsize=4, markersize=8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel('Final Batting Reliability Rating (with 90% Bootstrap CI)', fontsize=10)
    ax.set_title('Top 10 Batters Under Pressure: Reliability Rating & Stability', fontsize=12, fontweight='bold', pad=12)
    for i, v in enumerate(ratings):
        ax.text(v + 0.8, y_pos[i] - 0.15, f"{v:.1f}", fontsize=8, fontweight='bold', color='#1f77b4')
    plt.tight_layout()
    fig.savefig('outputs/charts/top_10_batters_ranking.png')
    plt.close()

    # -------------------------------------------------------------------------
    # Chart 3: Top 10 Bowlers Reliability Ratings & CIs (Forest Plot)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    y_pos = np.arange(len(top_bowl))[::-1]
    ratings_b = top_bowl['final_rating'].values
    ci_low_b = top_bowl['ci_lower'].values
    ci_high_b = top_bowl['ci_upper'].values
    names_b = top_bowl['bowler_name'].values
    
    xerr_b = [ratings_b - ci_low_b, ci_high_b - ratings_b]
    ax.errorbar(ratings_b, y_pos, xerr=xerr_b, fmt='o', color='#d62728', ecolor='#ff9896', elinewidth=2.5, capsize=4, markersize=8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names_b, fontsize=10)
    ax.set_xlabel('Final Bowling Reliability Rating (with 90% Bootstrap CI)', fontsize=10)
    ax.set_title('Top 10 Bowlers Under Pressure: Reliability Rating & Stability', fontsize=12, fontweight='bold', pad=12)
    for i, v in enumerate(ratings_b):
        ax.text(v + 0.8, y_pos[i] - 0.15, f"{v:.1f}", fontsize=8, fontweight='bold', color='#d62728')
    plt.tight_layout()
    fig.savefig('outputs/charts/top_10_bowlers_ranking.png')
    plt.close()

    # -------------------------------------------------------------------------
    # Chart 4: Normal vs Pressure Performance Comparison (Batters Delta SR)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    x = np.arange(len(top_bat))
    width = 0.35
    ax.bar(x - width/2, top_bat['normal_strike_rate'], width, label='Normal Strike Rate', color='#9ecae1')
    ax.bar(x + width/2, top_bat['pressure_strike_rate'], width, label='Pressure Strike Rate', color='#1f77b4')
    ax.set_xticks(x)
    ax.set_xticklabels([n.split()[-1] for n in top_bat['striker_name']], rotation=30, ha='right', fontsize=9)
    ax.set_ylabel('Strike Rate', fontsize=10)
    ax.set_title('Top 10 Batters: Normal vs. Pressure Strike Rate Comparison', fontsize=12, fontweight='bold', pad=12)
    ax.legend(frameon=True, fontsize=8)
    plt.tight_layout()
    fig.savefig('outputs/charts/batter_normal_vs_pressure.png')
    plt.close()

    # -------------------------------------------------------------------------
    # Chart 5: Normal vs Pressure Performance Comparison (Bowlers Economy)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    x = np.arange(len(top_bowl))
    ax.bar(x - width/2, top_bowl['normal_economy'], width, label='Normal Economy', color='#ff9896')
    ax.bar(x + width/2, top_bowl['pressure_economy'], width, label='Pressure Economy', color='#d62728')
    ax.set_xticks(x)
    ax.set_xticklabels([n.split()[-1] for n in top_bowl['bowler_name']], rotation=30, ha='right', fontsize=9)
    ax.set_ylabel('Economy Rate (Runs/Over)', fontsize=10)
    ax.set_title('Top 10 Bowlers: Normal vs. Pressure Economy Comparison (Lower is Better)', fontsize=12, fontweight='bold', pad=12)
    ax.legend(frameon=True, fontsize=8)
    plt.tight_layout()
    fig.savefig('outputs/charts/bowler_normal_vs_pressure.png')
    plt.close()

    # -------------------------------------------------------------------------
    # Chart 6: Collapse Resistance vs Pressure Strike Rate (Scatter)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    scatter = ax.scatter(all_bat['pressure_strike_rate'], all_bat['collapse_resistance_score'], c=all_bat['final_rating'], cmap='viridis', alpha=0.75, s=all_bat['pressure_balls_faced']*0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Final Rating', fontsize=9)
    # Highlight top 5
    for idx, r in top_bat.head(5).iterrows():
        ax.annotate(r['striker_name'], (r['pressure_strike_rate'], r['collapse_resistance_score']), fontsize=8, fontweight='bold', xytext=(5, 5), textcoords='offset points')
    ax.set_title('Batters: Pressure Strike Rate vs Collapse Resistance Score', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Pressure Strike Rate', fontsize=10)
    ax.set_ylabel('Collapse Resistance Score (0 - 100)', fontsize=10)
    plt.tight_layout()
    fig.savefig('outputs/charts/collapse_resistance_scatter.png')
    plt.close()

    # -------------------------------------------------------------------------
    # Chart 7: Aggression Resistance vs Pressure Economy (Scatter)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    scatter_b = ax.scatter(all_bowl['pressure_economy'], all_bowl['aggression_resistance_score'], c=all_bowl['final_rating'], cmap='coolwarm', alpha=0.75, s=all_bowl['pressure_legal_balls']*0.15)
    cbar_b = plt.colorbar(scatter_b, ax=ax)
    cbar_b.set_label('Final Rating', fontsize=9)
    for idx, r in top_bowl.head(5).iterrows():
        ax.annotate(r['bowler_name'], (r['pressure_economy'], r['aggression_resistance_score']), fontsize=8, fontweight='bold', xytext=(5, 5), textcoords='offset points')
    ax.set_title('Bowlers: Pressure Economy vs Aggression Resistance Score', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Pressure Economy (Runs/Over - Lower is Better)', fontsize=10)
    ax.set_ylabel('Aggression Resistance Score (0 - 100)', fontsize=10)
    plt.tight_layout()
    fig.savefig('outputs/charts/aggression_resistance_scatter.png')
    plt.close()

    print("[Charts] All publication-quality charts saved successfully.")

if __name__ == '__main__':
    generate_all_charts()

