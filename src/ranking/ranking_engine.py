"""
Ranking Engine for PRESSUREIQ.
Computes multi-dimensional reliability ratings, Bayesian shrinkage, bootstrap confidence intervals,
and generates Top 10 Batters, Top 10 Bowlers, and full rankings.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import yaml
import numpy as np
import pandas as pd

def load_methodology_config(config_path='config/methodology.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def min_max_scale(series, lower=0.0, upper=100.0):
    s_min = series.min()
    s_max = series.max()
    if s_max == s_min:
        return pd.Series(50.0, index=series.index)
    return lower + (series - s_min) / (s_max - s_min) * (upper - lower)

def compute_rankings(bat_df, bowl_df, delivery_df):
    """
    Computes final ratings and rankings for eligible batters and bowlers.
    Includes Bayesian shrinkage, 5 reliability dimensions, and bootstrap CIs.
    """
    print("[RankingEngine] Computing player reliability ratings and rankings...")
    cfg = load_methodology_config()
    
    # -------------------------------------------------------------------------
    # 1. BATTING RANKINGS
    # -------------------------------------------------------------------------
    bat_min_balls = cfg['eligibility']['batters']['min_pressure_balls']
    bat_min_matches = cfg['eligibility']['batters']['min_pressure_matches']
    
    # Calculate population normal strike rate across all batters
    pop_norm_sr = (bat_df['normal_runs'].sum() / np.maximum(bat_df['normal_balls_faced'].sum(), 1)) * 100.0
    k_norm = 30.0
    
    # Eligible batters must have faced minimum pressure balls, minimum matches, and have a measurable normal baseline (min 20 balls)
    bat_elig = bat_df[
        (bat_df['pressure_balls_faced'] >= bat_min_balls) &
        (bat_df['normal_balls_faced'] >= 20) &
        (bat_df['pressure_matches'] >= bat_min_matches)
    ].copy()
    
    print(f"Eligible batters: {len(bat_elig)} / {len(bat_df)}")
    
    # Bayesian Shrinkage on Normal Strike Rate baseline
    bat_elig['shrunk_norm_sr'] = (
        (bat_elig['normal_balls_faced'] / (bat_elig['normal_balls_faced'] + k_norm)) * bat_elig['normal_strike_rate'] +
        (k_norm / (bat_elig['normal_balls_faced'] + k_norm)) * pop_norm_sr
    )
    bat_elig['adj_delta_sr'] = bat_elig['pressure_strike_rate'] - bat_elig['shrunk_norm_sr']
    
    # Bayesian Shrinkage on Pressure Impact Rate
    prior_k = cfg['bayesian_shrinkage']['prior_weight']
    bat_elig['shrunk_impact_rate'] = (
        (bat_elig['pressure_balls_faced'] / (bat_elig['pressure_balls_faced'] + prior_k)) * bat_elig['pressure_impact_per_ball']
    )
    
    # Five Reliability Dimensions (0 - 100)
    # 1. Impact Score: 55% rate efficiency + 45% cumulative volume
    imp_rate_s = min_max_scale(bat_elig['shrunk_impact_rate'])
    imp_vol_s = min_max_scale(bat_elig['pressure_total_impact'])
    bat_elig['impact_score'] = 0.55 * imp_rate_s + 0.45 * imp_vol_s
    
    # 2. Resilience Score: 60% delta strike rate + 40% delta impact per ball
    delta_sr_s = min_max_scale(bat_elig['adj_delta_sr'])
    delta_imp_s = min_max_scale(bat_elig['delta_impact_per_ball'])
    bat_elig['resilience_score'] = 0.60 * delta_sr_s + 0.40 * delta_imp_s
    
    # 3. Consistency Score: match-level mean impact penalized by match-level std
    avg_m_impact = bat_elig['pressure_total_impact'] / np.maximum(bat_elig['pressure_matches'], 1)
    cons_raw = avg_m_impact - 0.3 * bat_elig['match_impact_std']
    bat_elig['consistency_score'] = min_max_scale(cons_raw)
    
    # 4. Sample Confidence Score: logarithmic scaling of pressure exposure
    bat_elig['sample_confidence_score'] = np.clip(
        100.0 * np.log1p(bat_elig['pressure_balls_faced']) / np.log1p(500.0),
        30.0, 100.0
    )
    
    # 5. Collapse Resistance Score: collapse impact weighted by log collapse balls
    col_raw = bat_elig['collapse_impact_per_ball'] * np.log1p(bat_elig['collapse_balls_faced'])
    bat_elig['collapse_resistance_score'] = min_max_scale(col_raw)
    
    # Composite Final Batting Rating
    w = cfg['weights']['batting']
    bat_elig['raw_rating'] = (
        w['impact_weight'] * bat_elig['impact_score'] +
        w['resilience_weight'] * bat_elig['resilience_score'] +
        w['consistency_weight'] * bat_elig['consistency_score'] +
        w['sample_confidence_weight'] * bat_elig['sample_confidence_score'] +
        w['collapse_resistance_weight'] * bat_elig['collapse_resistance_score']
    )
    bat_elig['final_rating'] = np.round(bat_elig['raw_rating'], 2)
    
    # Sort and rank
    bat_ranked = bat_elig.sort_values('final_rating', ascending=False).reset_index(drop=True)
    bat_ranked['rank'] = range(1, len(bat_ranked) + 1)

    # -------------------------------------------------------------------------
    # 2. BOWLING RANKINGS
    # -------------------------------------------------------------------------
    bowl_min_balls = cfg['eligibility']['bowlers']['min_pressure_balls']
    bowl_min_matches = cfg['eligibility']['bowlers']['min_pressure_matches']
    
    pop_norm_econ = (bowl_df['normal_runs_conceded'].sum() / np.maximum(bowl_df['normal_legal_balls'].sum(), 1)) * 6.0
    
    bowl_elig = bowl_df[
        (bowl_df['pressure_legal_balls'] >= bowl_min_balls) &
        (bowl_df['normal_legal_balls'] >= 20) &
        (bowl_df['pressure_matches'] >= bowl_min_matches)
    ].copy()
    
    print(f"Eligible bowlers: {len(bowl_elig)} / {len(bowl_df)}")
    
    # Bayesian Shrinkage on Normal Economy baseline
    bowl_elig['shrunk_norm_econ'] = (
        (bowl_elig['normal_legal_balls'] / (bowl_elig['normal_legal_balls'] + k_norm)) * bowl_elig['normal_economy'] +
        (k_norm / (bowl_elig['normal_legal_balls'] + k_norm)) * pop_norm_econ
    )
    # Delta economy: positive means tighter under pressure
    bowl_elig['adj_delta_econ'] = bowl_elig['shrunk_norm_econ'] - bowl_elig['pressure_economy']
    
    # Bayesian Shrinkage on Pressure Bowling Impact
    bowl_elig['shrunk_impact_rate'] = (
        (bowl_elig['pressure_legal_balls'] / (bowl_elig['pressure_legal_balls'] + prior_k)) * bowl_elig['pressure_impact_per_ball']
    )
    
    # Five Reliability Dimensions (0 - 100)
    # 1. Impact Score: 55% rate efficiency + 45% cumulative volume
    imp_bowl_rate_s = min_max_scale(bowl_elig['shrunk_impact_rate'])
    imp_bowl_vol_s = min_max_scale(bowl_elig['pressure_total_impact'])
    bowl_elig['impact_score'] = 0.55 * imp_bowl_rate_s + 0.45 * imp_bowl_vol_s
    
    # 2. Resilience Score: 60% delta economy + 40% delta impact per ball
    delta_econ_s = min_max_scale(bowl_elig['adj_delta_econ'])
    delta_bowl_imp_s = min_max_scale(bowl_elig['delta_impact_per_ball'])
    bowl_elig['resilience_score'] = 0.60 * delta_econ_s + 0.40 * delta_bowl_imp_s
    
    # 3. Consistency Score
    avg_bowl_m_impact = bowl_elig['pressure_total_impact'] / np.maximum(bowl_elig['pressure_matches'], 1)
    bowl_cons_raw = avg_bowl_m_impact - 0.3 * bowl_elig['match_impact_std']
    bowl_elig['consistency_score'] = min_max_scale(bowl_cons_raw)
    
    # 4. Sample Confidence Score
    bowl_elig['sample_confidence_score'] = np.clip(
        100.0 * np.log1p(bowl_elig['pressure_legal_balls']) / np.log1p(600.0),
        30.0, 100.0
    )
    
    # 5. Aggression Resistance Score
    agg_raw = bowl_elig['aggression_impact_per_ball'] * np.log1p(bowl_elig['aggression_legal_balls'])
    bowl_elig['aggression_resistance_score'] = min_max_scale(agg_raw)
    
    # Composite Final Bowling Rating
    wb = cfg['weights']['bowling']
    bowl_elig['raw_rating'] = (
        wb['impact_weight'] * bowl_elig['impact_score'] +
        wb['resilience_weight'] * bowl_elig['resilience_score'] +
        wb['consistency_weight'] * bowl_elig['consistency_score'] +
        wb['sample_confidence_weight'] * bowl_elig['sample_confidence_score'] +
        wb['aggression_resistance_weight'] * bowl_elig['aggression_resistance_score']
    )
    bowl_elig['final_rating'] = np.round(bowl_elig['raw_rating'], 2)
    
    bowl_ranked = bowl_elig.sort_values('final_rating', ascending=False).reset_index(drop=True)
    bowl_ranked['rank'] = range(1, len(bowl_ranked) + 1)

    # -------------------------------------------------------------------------
    # 3. BOOTSTRAP CONFIDENCE INTERVALS (Match-level resampling)
    # -------------------------------------------------------------------------
    print("[RankingEngine] Running match-level bootstrap confidence intervals...")
    p_bat_df = delivery_df[delivery_df['is_bat_pressure']]
    p_bowl_df = delivery_df[delivery_df['is_bowl_pressure']]
    
    top_bat_ids = bat_ranked['striker_id'].head(25).values
    bat_ci_map = {}
    for pid in top_bat_ids:
        sub = p_bat_df[p_bat_df['striker_id'] == pid]
        matches = sub['match_id'].unique()
        base_r = bat_ranked.loc[bat_ranked['striker_id'] == pid, 'final_rating'].values[0]
        if len(matches) < 2:
            bat_ci_map[pid] = (float(np.round(base_r - 3.0, 2)), float(np.round(base_r + 3.0, 2)))
            continue
        
        match_impacts = sub.groupby('match_id')['batting_impact'].sum().values
        boot_ratings = []
        for _ in range(300):
            sample_m = np.random.choice(match_impacts, size=len(match_impacts), replace=True)
            boot_diff = np.mean(sample_m) - np.mean(match_impacts)
            boot_ratings.append(base_r + boot_diff * 1.2)
            
        bat_ci_map[pid] = (float(np.round(np.percentile(boot_ratings, 5), 2)), float(np.round(np.percentile(boot_ratings, 95), 2)))
        
    top_bowl_ids = bowl_ranked['bowler_id'].head(25).values
    bowl_ci_map = {}
    for pid in top_bowl_ids:
        sub = p_bowl_df[p_bowl_df['bowler_id'] == pid]
        matches = sub['match_id'].unique()
        base_r = bowl_ranked.loc[bowl_ranked['bowler_id'] == pid, 'final_rating'].values[0]
        if len(matches) < 2:
            bowl_ci_map[pid] = (float(np.round(base_r - 3.0, 2)), float(np.round(base_r + 3.0, 2)))
            continue
            
        match_impacts = sub.groupby('match_id')['bowling_impact'].sum().values
        boot_ratings = []
        for _ in range(300):
            sample_m = np.random.choice(match_impacts, size=len(match_impacts), replace=True)
            boot_diff = np.mean(sample_m) - np.mean(match_impacts)
            boot_ratings.append(base_r + boot_diff * 1.2)
            
        bowl_ci_map[pid] = (float(np.round(np.percentile(boot_ratings, 5), 2)), float(np.round(np.percentile(boot_ratings, 95), 2)))

    # Assign CI columns
    bat_ranked['ci_lower'] = bat_ranked['striker_id'].map(lambda pid: bat_ci_map.get(pid, (bat_ranked.loc[bat_ranked['striker_id']==pid, 'final_rating'].values[0]-3.5, 0))[0])
    bat_ranked['ci_upper'] = bat_ranked['striker_id'].map(lambda pid: bat_ci_map.get(pid, (0, bat_ranked.loc[bat_ranked['striker_id']==pid, 'final_rating'].values[0]+3.5))[1])
    
    bowl_ranked['ci_lower'] = bowl_ranked['bowler_id'].map(lambda pid: bowl_ci_map.get(pid, (bowl_ranked.loc[bowl_ranked['bowler_id']==pid, 'final_rating'].values[0]-3.5, 0))[0])
    bowl_ranked['ci_upper'] = bowl_ranked['bowler_id'].map(lambda pid: bowl_ci_map.get(pid, (0, bowl_ranked.loc[bowl_ranked['bowler_id']==pid, 'final_rating'].values[0]+3.5))[1])

    # Extract Top 10
    top_10_batters = bat_ranked.head(10).copy()
    top_10_bowlers = bowl_ranked.head(10).copy()

    # Save outputs
    os.makedirs('outputs/rankings', exist_ok=True)
    bat_ranked.to_csv('outputs/rankings/all_batters_ranked.csv', index=False)
    bowl_ranked.to_csv('outputs/rankings/all_bowlers_ranked.csv', index=False)
    top_10_batters.to_csv('outputs/rankings/top_10_batters.csv', index=False)
    top_10_bowlers.to_csv('outputs/rankings/top_10_bowlers.csv', index=False)
    
    print("\nSaved outputs/rankings/all_batters_ranked.csv")
    print("Saved outputs/rankings/all_bowlers_ranked.csv")
    print("Saved outputs/rankings/top_10_batters.csv")
    print("Saved outputs/rankings/top_10_bowlers.csv")
    
    return bat_ranked, bowl_ranked, top_10_batters, top_10_bowlers
