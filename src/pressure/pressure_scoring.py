"""
Pressure Scoring Engine for PRESSUREIQ.
Calculates independent batting and bowling pressure scores (0-100) and detects scenarios A-F.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))
import numpy as np
import pandas as pd
from src.pressure.par_model import HistoricalParModel

def compute_pressure_scores(df, par_model=None):
    """
    Computes context-aware batting and bowling pressure scores for every delivery.
    Strictly uses pre-delivery match state information.
    """
    print("[PressureEngine] Calculating context-aware pressure scores...")
    df = df.copy()
    
    if par_model is None:
        par_model = HistoricalParModel().fit(df)
        
    n = len(df)
    
    # 1. Par Score & Deficit for 1st Innings
    par_scores = par_model.predict_par(df['format_type'].values, df['overid'].values)
    df['par_score'] = par_scores
    # Par deficit (positive means behind par, negative means ahead of par)
    df['par_deficit'] = np.where(
        df['innings'] == 1,
        df['par_score'] - df['score_before'],
        0.0
    )
    
    # Extract pre-delivery variables
    inn = df['innings'].values
    w_lost = df['wickets_before'].values
    w_rem = df['wickets_remaining'].values
    w12 = df['wickets_last_12'].values
    w18 = df['wickets_last_18'].values
    r12 = df['runs_last_12'].values
    r18 = df['runs_last_18'].values
    b12 = df['boundaries_last_12'].values
    b18 = df['boundaries_last_18'].values
    dots = df['consecutive_dots_before'].values
    part_runs = df['partnership_runs_before'].values
    part_balls = df['partnership_balls_before'].values
    legal_balls_bowled = df['legal_balls_bowled'].values
    legal_balls_rem = df['legal_balls_remaining'].values
    overs_rem = df['overs_remaining'].values
    crr = df['current_run_rate'].values
    rrr = df['required_run_rate'].fillna(0.0).values
    runs_req = df['runs_required'].fillna(0.0).values
    rrr_diff = df['rrr_minus_crr'].fillna(0.0).values
    bat_pos = df['batting_order'].fillna(4).values
    par_def = df['par_deficit'].values

    # =========================================================================
    # SCENARIO A: Batting Collapse Pressure (0 - 100)
    # =========================================================================
    # High when wickets are falling in rapid succession, high wickets lost early, or severe par deficit
    raw_collapse = (
        28.0 * w12 +
        16.0 * np.maximum(0, w18 - w12) +
        5.5 * w_lost +
        15.0 * np.clip(par_def / 20.0, 0.0, 1.5) -
        0.25 * np.minimum(part_runs, 60.0)
    )
    # Calibrate: baseline is ~10 when 0 wickets down
    p_collapse = np.clip(raw_collapse, 0.0, 100.0)

    # =========================================================================
    # SCENARIO B: Run Chase Pressure (Innings 2) (0 - 100)
    # =========================================================================
    # High when RRR is steep, balls remaining are low, or wickets in hand are depleted
    raw_chase = np.where(
        inn == 2,
        (
            np.clip((rrr - 6.0) / 8.0, 0.0, 2.0) * 40.0 +
            np.clip(rrr_diff / 5.0, 0.0, 2.0) * 20.0 +
            ((10.0 - w_rem) / 9.0) * 25.0 +
            np.clip((60.0 - legal_balls_rem) / 60.0, 0.0, 1.0) * 15.0
        ),
        0.0
    )
    p_chase = np.clip(raw_chase, 0.0, 100.0)

    # =========================================================================
    # SCENARIO C: Lower-Order Survival Pressure (0 - 100)
    # =========================================================================
    # Batter batting at #7+ or 6+ wickets lost while considerable overs remain
    is_lower_order = (bat_pos >= 7) | (w_lost >= 6)
    raw_survival = np.where(
        is_lower_order,
        (
            30.0 +
            8.0 * np.maximum(0, w_lost - 5) +
            18.0 * np.clip(overs_rem / 5.0, 0.0, 1.0) +
            12.0 * np.clip((60.0 - part_runs) / 60.0, 0.0, 1.0)
        ),
        np.maximum(0.0, (w_lost - 4) * 8.0)
    )
    p_survival = np.clip(raw_survival, 0.0, 100.0)

    # =========================================================================
    # SCENARIO F: Momentum Pressure (Batting) (0 - 100)
    # =========================================================================
    # High dot ball accumulation, stagnation
    raw_mom_bat = (
        12.0 * np.minimum(dots, 5) +
        25.0 * np.clip((14.0 - r12) / 14.0, 0.0, 1.0) +
        15.0 * np.clip((w12 > 0).astype(float) + (w18 > 1).astype(float), 0.0, 2.0)
    )
    p_mom_bat = np.clip(raw_mom_bat, 0.0, 100.0)

    # =========================================================================
    # COMBINED BATTING PRESSURE SCORE (0 - 100)
    # =========================================================================
    batting_pressure = np.where(
        inn == 1,
        0.48 * p_collapse + 0.28 * p_survival + 0.24 * p_mom_bat,
        0.45 * p_chase + 0.30 * p_collapse + 0.15 * p_survival + 0.10 * p_mom_bat
    )
    # Ensure standard 0-100 scaling
    batting_pressure = np.clip(batting_pressure, 0.0, 100.0)

    # =========================================================================
    # SCENARIO D: Aggressive Opposition Batting Pressure (Bowling) (0 - 100)
    # =========================================================================
    # Opposition scoring rapidly, hitting multiple boundaries, or building large set partnership
    raw_aggression = (
        35.0 * np.clip(r12 / 24.0, 0.0, 1.5) +
        25.0 * np.clip(b12 / 3.0, 0.0, 1.5) +
        20.0 * np.clip(part_runs / 65.0, 0.0, 1.5) +
        20.0 * (w_rem / 10.0)
    )
    p_aggression = np.clip(raw_aggression, 0.0, 100.0)

    # =========================================================================
    # SCENARIO E: Defensive Bowling Pressure (Innings 2 Close Chase) (0 - 100)
    # =========================================================================
    # Bowler defending a tight target where match outcome hangs in balance
    closeness = np.clip(1.0 - np.abs(rrr - 8.5) / 6.5, 0.0, 1.0)
    raw_defend = np.where(
        inn == 2,
        (
            35.0 * closeness +
            25.0 * (w_rem / 10.0) +
            40.0 * np.clip((36.0 - legal_balls_rem) / 36.0, 0.0, 1.0)
        ),
        0.0
    )
    p_defend = np.clip(raw_defend, 0.0, 100.0)

    # =========================================================================
    # Death Overs & High Leverage Pressure (Bowling) (0 - 100)
    # =========================================================================
    raw_leverage = (
        65.0 * np.clip((legal_balls_bowled - 72.0) / 48.0, 0.0, 1.0) +
        35.0 * (w_rem / 10.0)
    )
    p_leverage = np.clip(raw_leverage, 0.0, 100.0)

    # =========================================================================
    # Momentum Against Bowler (0 - 100)
    # =========================================================================
    raw_mom_bowl = (
        50.0 * np.clip(r12 / 22.0, 0.0, 1.2) +
        30.0 * np.clip(b18 / 4.0, 0.0, 1.2) +
        20.0 * (w18 == 0).astype(float)
    )
    p_mom_bowl = np.clip(raw_mom_bowl, 0.0, 100.0)

    # =========================================================================
    # COMBINED BOWLING PRESSURE SCORE (0 - 100)
    # =========================================================================
    bowling_pressure = np.where(
        inn == 1,
        0.45 * p_aggression + 0.35 * p_leverage + 0.20 * p_mom_bowl,
        0.40 * p_defend + 0.30 * p_aggression + 0.20 * p_leverage + 0.10 * p_mom_bowl
    )
    bowling_pressure = np.clip(bowling_pressure, 0.0, 100.0)

    # Assign Scenario Columns
    df['scenario_collapse_score'] = np.round(p_collapse, 1)
    df['scenario_chase_score'] = np.round(p_chase, 1)
    df['scenario_survival_score'] = np.round(p_survival, 1)
    df['scenario_aggression_score'] = np.round(p_aggression, 1)
    df['scenario_defend_score'] = np.round(p_defend, 1)
    df['scenario_momentum_bat_score'] = np.round(p_mom_bat, 1)
    df['scenario_momentum_bowl_score'] = np.round(p_mom_bowl, 1)
    
    df['batting_pressure_score'] = np.round(batting_pressure, 1)
    df['bowling_pressure_score'] = np.round(bowling_pressure, 1)

    # Assign Pressure Categories
    # Low: < 35, Moderate: 35-60, High: 60-80, Extreme: >= 80
    def assign_category(score):
        return np.where(
            score < 35.0, 'low',
            np.where(
                score < 60.0, 'moderate',
                np.where(score < 80.0, 'high', 'extreme')
            )
        )
        
    df['batting_pressure_cat'] = assign_category(df['batting_pressure_score'].values)
    df['bowling_pressure_cat'] = assign_category(df['bowling_pressure_score'].values)

    # Dominant Scenario Identification
    # Batting dominant scenario
    bat_scenarios = np.column_stack([p_collapse, p_chase, p_survival, p_mom_bat])
    bat_scenario_names = ['Collapse', 'Run Chase', 'Survival', 'Momentum Deficit']
    bat_max_idx = np.argmax(bat_scenarios, axis=1)
    df['dominant_batting_scenario'] = [bat_scenario_names[i] if batting_pressure[j] >= 35.0 else 'Normal' for j, i in enumerate(bat_max_idx)]
    
    # Bowling dominant scenario
    bowl_scenarios = np.column_stack([p_aggression, p_defend, p_leverage, p_mom_bowl])
    bowl_scenario_names = ['Aggressive Opposition', 'Defending Chase', 'Death Leverage', 'Adverse Momentum']
    bowl_max_idx = np.argmax(bowl_scenarios, axis=1)
    df['dominant_bowling_scenario'] = [bowl_scenario_names[i] if bowling_pressure[j] >= 35.0 else 'Normal' for j, i in enumerate(bowl_max_idx)]

    print("[PressureEngine] Computed pressure scores successfully.")
    print(f"Batting pressure distribution: {pd.Series(df['batting_pressure_cat']).value_counts().to_dict()}")
    print(f"Bowling pressure distribution: {pd.Series(df['bowling_pressure_cat']).value_counts().to_dict()}")
    
    return df

if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.abspath('.'))
    from src.data.loader import load_data
    from src.data.delivery_state import reconstruct_delivery_states
    
    data = load_data()
    ds_df = reconstruct_delivery_states(data['ball_by_ball'], data['matches'])
    p_df = compute_pressure_scores(ds_df)
    print(p_df[['match_id', 'innings', 'batting_pressure_score', 'batting_pressure_cat', 'bowling_pressure_score', 'bowling_pressure_cat', 'dominant_batting_scenario']].head(10))
