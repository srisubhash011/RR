"""
Player Performance and Baseline Engine for PRESSUREIQ.
Calculates normal vs pressure metrics, resilience, impact, consistency, and scenario-specific resistance.
"""

import numpy as np
import pandas as pd

def calculate_player_baselines_and_metrics(df, p_thresh=35.0):
    """
    Computes comprehensive player metrics for both Batting and Bowling.
    Separates Normal (< p_thresh) from Pressure (>= p_thresh).
    Calculates impact, resilience, consistency, and scenario scores.
    """
    print("[PlayerMetrics] Calculating player baselines and reliability metrics...")
    
    # -------------------------------------------------------------------------
    # 1. BATTING METRICS & BASELINES
    # -------------------------------------------------------------------------
    # We aggregate by striker_id across:
    # A) All deliveries
    # B) Normal deliveries (batting_pressure_score < p_thresh)
    # C) Pressure deliveries (batting_pressure_score >= p_thresh)
    # D) Collapse deliveries (scenario_collapse_score >= 60.0)
    
    # Identify dismissals of striker
    df['is_striker_dismissed'] = (
        df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])
    ).astype(int)
    
    # Pressure flags
    df['is_bat_pressure'] = df['batting_pressure_score'] >= p_thresh
    df['is_bat_collapse'] = df['scenario_collapse_score'] >= 60.0
    
    # Groupings
    def get_bat_stats(sub_df, prefix=''):
        grouped = sub_df.groupby('striker_id').agg(
            striker_name=('striker_name', 'last'),
            balls_faced=('batter_ball_faced', 'sum'),
            runs=('batter_runs', 'sum'),
            fours=('is_four_val', 'sum'),
            sixes=('is_six_val', 'sum'),
            dots=('is_dot', 'sum'),
            dismissals=('is_striker_dismissed', 'sum'),
            total_impact=('batting_impact', 'sum'),
            exp_runs=('exp_batter_runs', 'sum'),
            matches=('match_id', 'nunique'),
            ipl_balls=('batter_ball_faced', lambda s: s[sub_df.loc[s.index, 'format_type'] == 'IPL'].sum()),
            t20i_balls=('batter_ball_faced', lambda s: s[sub_df.loc[s.index, 'format_type'] == 'T20I'].sum())
        ).reset_index()
        
        # Rates
        bf = np.maximum(grouped['balls_faced'], 1)
        grouped[f'{prefix}strike_rate'] = (grouped['runs'] / bf) * 100.0
        grouped[f'{prefix}boundary_pct'] = ((grouped['fours'] + grouped['sixes']) / bf) * 100.0
        grouped[f'{prefix}dot_pct'] = (grouped['dots'] / bf) * 100.0
        grouped[f'{prefix}impact_per_ball'] = grouped['total_impact'] / bf
        grouped[f'{prefix}runs_per_dismissal'] = grouped['runs'] / np.maximum(grouped['dismissals'], 1)
        
        # Rename base columns with prefix
        rename_dict = {
            'balls_faced': f'{prefix}balls_faced',
            'runs': f'{prefix}runs',
            'fours': f'{prefix}fours',
            'sixes': f'{prefix}sixes',
            'dots': f'{prefix}dots',
            'dismissals': f'{prefix}dismissals',
            'total_impact': f'{prefix}total_impact',
            'exp_runs': f'{prefix}exp_runs',
            'matches': f'{prefix}matches',
            'ipl_balls': f'{prefix}ipl_balls',
            't20i_balls': f'{prefix}t20i_balls'
        }
        return grouped.rename(columns=rename_dict)
    
    # Compute Normal and Pressure stats
    bat_normal = get_bat_stats(df[~df['is_bat_pressure']], prefix='normal_')
    bat_pressure = get_bat_stats(df[df['is_bat_pressure']], prefix='pressure_')
    bat_collapse = get_bat_stats(df[df['is_bat_collapse']], prefix='collapse_')
    
    # Merge batting metrics
    bat_all = bat_pressure.merge(
        bat_normal[['striker_id', 'normal_balls_faced', 'normal_runs', 'normal_strike_rate', 'normal_boundary_pct', 'normal_dot_pct', 'normal_impact_per_ball', 'normal_runs_per_dismissal']],
        on='striker_id', how='left'
    ).merge(
        bat_collapse[['striker_id', 'collapse_balls_faced', 'collapse_runs', 'collapse_strike_rate', 'collapse_impact_per_ball']],
        on='striker_id', how='left'
    ).fillna(0)
    
    # Batting Resilience
    # Delta strike rate & Delta impact
    bat_all['delta_strike_rate'] = bat_all['pressure_strike_rate'] - bat_all['normal_strike_rate']
    bat_all['delta_impact_per_ball'] = bat_all['pressure_impact_per_ball'] - bat_all['normal_impact_per_ball']
    
    # Match Consistency (variance across matches under pressure)
    p_bat_df = df[df['is_bat_pressure']]
    m_bat = p_bat_df.groupby(['striker_id', 'match_id'])['batting_impact'].sum().reset_index()
    bat_m_std = m_bat.groupby('striker_id')['batting_impact'].agg(['std', 'count']).reset_index()
    bat_m_std['std'] = bat_m_std['std'].fillna(2.0)
    bat_all = bat_all.merge(bat_m_std.rename(columns={'std': 'match_impact_std', 'count': 'pressure_match_count'}), on='striker_id', how='left').fillna(0)

    # -------------------------------------------------------------------------
    # 2. BOWLING METRICS & BASELINES
    # -------------------------------------------------------------------------
    df['is_bowl_pressure'] = df['bowling_pressure_score'] >= p_thresh
    df['is_bowl_aggression'] = df['scenario_aggression_score'] >= 60.0
    
    def get_bowl_stats(sub_df, prefix=''):
        grouped = sub_df.groupby('bowler_id').agg(
            bowler_name=('bowler_name', 'last'),
            legal_balls=('is_legal', 'sum'),
            runs_conceded=('bowler_runs_conceded', 'sum'),
            wickets=('bowler_credited_wicket', 'sum'),
            dots=('is_dot', 'sum'),
            boundaries=('is_boundary', 'sum'),
            runs_saved=('bowling_runs_saved', 'sum'),
            total_impact=('bowling_impact', 'sum'),
            exp_runs=('exp_bowler_runs', 'sum'),
            matches=('match_id', 'nunique'),
            ipl_balls=('is_legal', lambda s: s[sub_df.loc[s.index, 'format_type'] == 'IPL'].sum()),
            t20i_balls=('is_legal', lambda s: s[sub_df.loc[s.index, 'format_type'] == 'T20I'].sum())
        ).reset_index()
        
        lb = np.maximum(grouped['legal_balls'], 1)
        grouped[f'{prefix}economy'] = (grouped['runs_conceded'] / lb) * 6.0
        grouped[f'{prefix}dot_pct'] = (grouped['dots'] / lb) * 100.0
        grouped[f'{prefix}boundary_pct'] = (grouped['boundaries'] / lb) * 100.0
        grouped[f'{prefix}wicket_rate'] = grouped['wickets'] / lb
        grouped[f'{prefix}impact_per_ball'] = grouped['total_impact'] / lb
        grouped[f'{prefix}runs_saved_per_ball'] = grouped['runs_saved'] / lb
        
        rename_dict = {
            'legal_balls': f'{prefix}legal_balls',
            'runs_conceded': f'{prefix}runs_conceded',
            'wickets': f'{prefix}wickets',
            'dots': f'{prefix}dots',
            'boundaries': f'{prefix}boundaries',
            'runs_saved': f'{prefix}runs_saved',
            'total_impact': f'{prefix}total_impact',
            'exp_runs': f'{prefix}exp_runs',
            'matches': f'{prefix}matches',
            'ipl_balls': f'{prefix}ipl_balls',
            't20i_balls': f'{prefix}t20i_balls'
        }
        return grouped.rename(columns=rename_dict)
        
    bowl_normal = get_bowl_stats(df[~df['is_bowl_pressure']], prefix='normal_')
    bowl_pressure = get_bowl_stats(df[df['is_bowl_pressure']], prefix='pressure_')
    bowl_aggression = get_bowl_stats(df[df['is_bowl_aggression']], prefix='aggression_')
    
    # Merge bowling metrics
    bowl_all = bowl_pressure.merge(
        bowl_normal[['bowler_id', 'normal_legal_balls', 'normal_runs_conceded', 'normal_economy', 'normal_dot_pct', 'normal_boundary_pct', 'normal_wicket_rate', 'normal_impact_per_ball']],
        on='bowler_id', how='left'
    ).merge(
        bowl_aggression[['bowler_id', 'aggression_legal_balls', 'aggression_runs_conceded', 'aggression_economy', 'aggression_impact_per_ball']],
        on='bowler_id', how='left'
    ).fillna(0)
    
    # Bowling Resilience
    # Economy delta (positive is good: lower economy under pressure than normal)
    bowl_all['delta_economy'] = bowl_all['normal_economy'] - bowl_all['pressure_economy']
    bowl_all['delta_impact_per_ball'] = bowl_all['pressure_impact_per_ball'] - bowl_all['normal_impact_per_ball']
    
    # Match consistency
    p_bowl_df = df[df['is_bowl_pressure']]
    m_bowl = p_bowl_df.groupby(['bowler_id', 'match_id'])['bowling_impact'].sum().reset_index()
    bowl_m_std = m_bowl.groupby('bowler_id')['bowling_impact'].agg(['std', 'count']).reset_index()
    bowl_m_std['std'] = bowl_m_std['std'].fillna(2.0)
    bowl_all = bowl_all.merge(bowl_m_std.rename(columns={'std': 'match_impact_std', 'count': 'pressure_match_count'}), on='bowler_id', how='left').fillna(0)

    print(f"[PlayerMetrics] Computed stats for {len(bat_all)} batters and {len(bowl_all)} bowlers.")
    return bat_all, bowl_all

