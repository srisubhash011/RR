"""
Data loader module for PRESSUREIQ
Handles loading and scope filtering according to competition_filters.yaml.
"""

import os
import yaml
import pandas as pd
import numpy as np

def load_config(config_path='config/competition_filters.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_data(base_dir='.'):
    """
    Loads all raw CSV files, applies competition and innings filtering.
    Returns:
        dict of dataframes: 'competitions', 'teams', 'matches', 'playing_eleven', 'mapping', 'ball_by_ball'
    """
    cfg = load_config()
    
    comp_df = pd.read_csv(os.path.join(base_dir, 'competitions.csv'))
    teams_df = pd.read_csv(os.path.join(base_dir, 'teams.csv'))
    matches_df = pd.read_csv(os.path.join(base_dir, 'matches.csv'))
    p11_df = pd.read_csv(os.path.join(base_dir, 'playing_eleven.csv'))
    map_df = pd.read_csv(os.path.join(base_dir, 'competition_team_player_mapping.csv'))
    # Support both 6af855c0e8386_ball_by_ball.csv and ball_by_ball.csv
    bbb_path = os.path.join(base_dir, '6af855c0e8386_ball_by_ball.csv')
    if not os.path.exists(bbb_path):
        bbb_path = os.path.join(base_dir, 'ball_by_ball.csv')
        
    bbb_df = pd.read_csv(bbb_path, low_memory=False)
    
    # Identify included competitions:
    # 1. Match format is in included_formats (T20I)
    # 2. Comp ID is in ipl_competition_ids (1358, 1715, 2193, 2725, 3298)
    ipl_ids = set(cfg['scope']['ipl_competition_ids'])
    t20i_ids = set(comp_df[comp_df['match_format'].isin(cfg['scope']['included_formats'])]['comp_id'])
    included_comp_ids = (ipl_ids | t20i_ids) - set(cfg['scope']['excluded_competition_ids'])
    
    valid_matches_df = matches_df[matches_df['comp_id'].isin(included_comp_ids)].copy()
    valid_match_ids = set(valid_matches_df['match_id'])
    
    # Filter ball-by-ball
    # Innings 1 and 2 only (exclude super overs)
    filtered_bbb = bbb_df[
        (bbb_df['match_id'].isin(valid_match_ids)) &
        (bbb_df['innings'].isin(cfg['scope']['valid_innings']))
    ].copy()
    
    # Sort chronologically
    filtered_bbb = filtered_bbb.sort_values(
        ['match_id', 'innings', 'overid', 'over_ball_num', 'innings_ball_num']
    ).reset_index(drop=True)
    
    # Tag competition type (IPL vs T20I)
    comp_map = comp_df.set_index('comp_id')['match_format'].to_dict()
    comp_name_map = comp_df.set_index('comp_id')['comp_name'].to_dict()
    season_map = comp_df.set_index('comp_id')['season'].to_dict()
    match_comp_map = matches_df.set_index('match_id')['comp_id'].to_dict()
    
    filtered_bbb['comp_id'] = filtered_bbb['match_id'].map(match_comp_map)
    filtered_bbb['comp_name'] = filtered_bbb['comp_id'].map(comp_name_map)
    filtered_bbb['season'] = filtered_bbb['comp_id'].map(season_map)
    filtered_bbb['format_type'] = filtered_bbb['comp_id'].apply(
        lambda cid: 'IPL' if cid in ipl_ids else 'T20I'
    )
    
    print(f"[Loader] Loaded and filtered: {len(filtered_bbb):,} deliveries across {filtered_bbb['match_id'].nunique()} matches.")
    print(f"[Loader] Format breakdown: {filtered_bbb['format_type'].value_counts().to_dict()}")
    
    return {
        'competitions': comp_df,
        'teams': teams_df,
        'matches': valid_matches_df,
        'playing_eleven': p11_df,
        'mapping': map_df,
        'ball_by_ball': filtered_bbb
    }

if __name__ == '__main__':
    data = load_data()

