"""
Main Execution Pipeline for PRESSUREIQ.
Executes the full end-to-end analytical pipeline deterministically and exports all required files.
Usage:
    python run_pipeline.py
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import time
import pandas as pd
import numpy as np

from src.data.loader import load_data
from src.data.validation import run_validation
from src.data.delivery_state import reconstruct_delivery_states
from src.pressure.pressure_scoring import compute_pressure_scores
from src.models.expected_models import train_and_predict_expected_models
from src.performance.player_metrics import calculate_player_baselines_and_metrics
from src.ranking.ranking_engine import compute_rankings
from src.ranking.sensitivity import run_sensitivity_analysis
from src.reporting.charts import generate_all_charts
from src.reporting.report_generator import build_pdf_report
from src.data.export_web_data import export_for_web

def main():
    start_time = time.time()
    print("=" * 80)
    print("PRESSUREIQ: CONTEXT-AWARE CRICKET PRESSURE & PLAYER RELIABILITY ENGINE")
    print("SupeRR Selector Season 2 – Round 1")
    print("=" * 80)
    
    # Step 1: Validation & Quality Audit
    print("\n>>> STEP 1: Running Data Validation & Audit...")
    run_validation()
    
    # Step 2: Load Data
    print("\n>>> STEP 2: Loading & Filtering Raw Datasets...")
    data = load_data()
    
    # Step 3: Delivery-Level State Reconstruction
    print("\n>>> STEP 3: Reconstructing Pre-Delivery Match States...")
    ds_df = reconstruct_delivery_states(data['ball_by_ball'], data['matches'])
    
    # Step 4: Context-Aware Pressure Engine
    print("\n>>> STEP 4: Computing Context-Aware Pressure Scores...")
    p_df = compute_pressure_scores(ds_df)
    
    # Step 5: Expected Performance Models (5-Fold Match-Grouped GBDT)
    print("\n>>> STEP 5: Fitting Leak-Free Expected Performance Models...")
    exp_df = train_and_predict_expected_models(p_df)
    
    # Export intermediate delivery pressure features
    os.makedirs('outputs/analytical', exist_ok=True)
    # Save parquet for fast dashboard loading and csv for portable evaluation
    print("[Pipeline] Exporting delivery_pressure_features...")
    exp_df.to_parquet('outputs/analytical/delivery_pressure_features.parquet', index=False)
    # Also export sample / essential delivery features csv to prevent excessive disk bloat
    essential_cols = [
        'match_id', 'innings', 'overid', 'over_ball_num', 'striker_id', 'striker_name',
        'bowler_id', 'bowler_name', 'batting_team_id', 'bowling_team_id', 'format_type',
        'score_before', 'wickets_before', 'legal_balls_bowled', 'legal_balls_remaining',
        'current_run_rate', 'required_run_rate', 'runs_required',
        'batting_pressure_score', 'batting_pressure_cat',
        'bowling_pressure_score', 'bowling_pressure_cat',
        'dominant_batting_scenario', 'dominant_bowling_scenario',
        'batter_runs', 'is_four', 'is_six', 'is_wicket', 'bowler_runs_conceded',
        'bowler_credited_wicket', 'exp_batter_runs', 'exp_bowler_runs',
        'batting_impact', 'bowling_impact'
    ]
    exp_df[essential_cols].to_csv('outputs/analytical/delivery_pressure_features.csv', index=False)
    print("Saved outputs/analytical/delivery_pressure_features.csv and .parquet")
    
    # Step 6: Player Baselines & Metrics
    print("\n>>> STEP 6: Computing Player Baselines and Performance Dimensions...")
    bat_df, bowl_df = calculate_player_baselines_and_metrics(exp_df)
    
    # Step 7: Ranking Engine
    print("\n>>> STEP 7: Computing Final Ratings, CIs, and Top 10 Rankings...")
    bat_ranked, bowl_ranked, top_10_batters, top_10_bowlers = compute_rankings(bat_df, bowl_df, exp_df)
    
    # Export Analytical tables
    bat_df.to_csv('outputs/analytical/batting_performance.csv', index=False)
    bowl_df.to_csv('outputs/analytical/bowling_performance.csv', index=False)
    
    # Combine baselines into player_baselines.csv
    bat_base = bat_df[['striker_id', 'striker_name', 'normal_strike_rate', 'pressure_strike_rate', 'delta_strike_rate', 'normal_impact_per_ball', 'pressure_impact_per_ball', 'delta_impact_per_ball']].rename(
        columns={'striker_id': 'player_id', 'striker_name': 'player_name'}
    )
    bat_base['role'] = 'Batter'
    
    bowl_base = bowl_df[['bowler_id', 'bowler_name', 'normal_economy', 'pressure_economy', 'delta_economy', 'normal_impact_per_ball', 'pressure_impact_per_ball', 'delta_impact_per_ball']].rename(
        columns={'bowler_id': 'player_id', 'bowler_name': 'player_name'}
    )
    bowl_base['role'] = 'Bowler'
    
    player_baselines = pd.concat([bat_base, bowl_base], ignore_index=True)
    player_baselines.to_csv('outputs/analytical/player_baselines.csv', index=False)
    print("Saved outputs/analytical/batting_performance.csv, bowling_performance.csv, player_baselines.csv")
    
    # Scenario analysis breakdown
    print("[Pipeline] Computing player scenario analysis...")
    scenario_bat = exp_df[exp_df['batting_pressure_score'] >= 35.0].groupby(['striker_id', 'dominant_batting_scenario']).agg(
        balls=('batter_ball_faced', 'sum'),
        runs=('batter_runs', 'sum'),
        avg_impact=('batting_impact', 'mean')
    ).reset_index()
    scenario_bat.to_csv('outputs/analytical/player_scenario_analysis.csv', index=False)
    print("Saved outputs/analytical/player_scenario_analysis.csv")

    # Ranking confidence summary
    conf_bat = top_10_batters[['rank', 'striker_id', 'striker_name', 'final_rating', 'ci_lower', 'ci_upper', 'pressure_balls_faced', 'pressure_matches']].rename(
        columns={'striker_id': 'player_id', 'striker_name': 'player_name', 'pressure_balls_faced': 'pressure_balls'}
    )
    conf_bat['role'] = 'Batter'
    
    conf_bowl = top_10_bowlers[['rank', 'bowler_id', 'bowler_name', 'final_rating', 'ci_lower', 'ci_upper', 'pressure_legal_balls', 'pressure_matches']].rename(
        columns={'bowler_id': 'player_id', 'bowler_name': 'player_name', 'pressure_legal_balls': 'pressure_balls'}
    )
    conf_bowl['role'] = 'Bowler'
    
    rank_conf = pd.concat([conf_bat, conf_bowl], ignore_index=True)
    rank_conf.to_csv('outputs/rankings/ranking_confidence.csv', index=False)
    print("Saved outputs/rankings/ranking_confidence.csv")

    # Step 8: Sensitivity Analysis
    print("\n>>> STEP 8: Running Sensitivity & Robustness Testing...")
    sens_df = run_sensitivity_analysis(bat_ranked, bowl_ranked)

    # Step 9: Publication Charts & PDF Methodology Report
    print("\n>>> STEP 9: Generating Publication Charts & PDF Methodology Report...")
    generate_all_charts()
    build_pdf_report()

    # Step 10: Export Web Datasets for Vercel Dashboard
    print("\n>>> STEP 10: Exporting Web Datasets for Vercel Dashboard...")
    export_for_web()

    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"PIPELINE COMPLETE: Finished all stages in {total_time:.2f} seconds.")
    print("=" * 80)
    
    print("\n--- OFFICIAL TOP 10 BATTERS UNDER PRESSURE ---")
    print(top_10_batters[['rank', 'striker_name', 'final_rating', 'pressure_strike_rate', 'normal_strike_rate', 'delta_strike_rate', 'impact_score', 'resilience_score', 'ci_lower', 'ci_upper']])
    
    print("\n--- OFFICIAL TOP 10 BOWLERS UNDER PRESSURE ---")
    print(top_10_bowlers[['rank', 'bowler_name', 'final_rating', 'pressure_economy', 'normal_economy', 'delta_economy', 'impact_score', 'resilience_score', 'ci_lower', 'ci_upper']])

if __name__ == '__main__':
    main()

