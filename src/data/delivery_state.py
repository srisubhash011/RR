"""
Delivery-level state reconstruction module for PRESSUREIQ.
Reconstructs the exact match situation immediately BEFORE each delivery without future leakage.
"""

import numpy as np
import pandas as pd
import time

def reconstruct_delivery_states(bbb_df, matches_df):
    """
    Takes filtered ball-by-ball dataframe and matches dataframe.
    Computes all pre-delivery match state variables.
    """
    t0 = time.time()
    print("[DeliveryState] Starting pre-delivery match state reconstruction...")
    
    df = bbb_df.copy()
    
    # 1. Delivery Classification
    # Wides, noballs, legal balls
    df['extras_type'] = df['extras_type'].fillna('none')
    df['extras1_runs'] = df['extras1_runs'].fillna(0).astype(int)
    df['extras_2_runs'] = df['extras_2_runs'].fillna(0).astype(int)
    df['runs'] = df['runs'].fillna(0).astype(int)
    
    df['is_legal'] = ~df['extras_type'].isin(['wide', 'Overstep', 'other'])
    df['is_wide'] = df['extras_type'] == 'wide'
    df['is_noball'] = df['extras_type'].isin(['Overstep', 'other'])
    df['is_bye'] = df['extras_type'] == 'byes'
    df['is_legbye'] = df['extras_type'] == 'legbyes'
    
    # Batting accounting
    df['batter_ball_faced'] = (~df['is_wide']).astype(int)
    df['batter_runs'] = df['runs']
    df['is_boundary'] = (df['is_four'] | df['is_six']).astype(int)
    df['is_four_val'] = df['is_four'].astype(int)
    df['is_six_val'] = df['is_six'].astype(int)
    
    # Total team delivery runs
    df['team_delivery_runs'] = df['runs'] + df['extras1_runs'] + df['extras_2_runs']
    
    # Bowler accounting
    # Wides: extras1_runs
    # No-balls (Overstep/other): extras1_runs (1 penalty) + batter runs, excluding byes/legbyes in extras_2_runs
    # Byes / Leg-byes: 0 runs charged to bowler
    # Standard: runs + extras1_runs
    bowler_runs = np.where(
        df['is_wide'],
        df['extras1_runs'],
        np.where(
            df['is_noball'],
            df['extras1_runs'] + df['runs'],
            np.where(
                df['is_bye'] | df['is_legbye'],
                0,
                df['runs'] + df['extras1_runs']
            )
        )
    )
    df['bowler_runs_conceded'] = bowler_runs
    
    # Bowler credited wickets vs non-bowler wickets
    bowler_wicket_types = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
    df['is_wicket_clean'] = df['is_wicket'].fillna(False).astype(bool)
    df['bowler_credited_wicket'] = (
        df['is_wicket_clean'] & df['dismissal_type'].isin(bowler_wicket_types)
    ).astype(int)
    df['is_team_wicket'] = df['is_wicket_clean'].astype(int)
    
    # Dot ball accounting: legal delivery and 0 team runs
    df['is_dot'] = (df['is_legal'] & (df['team_delivery_runs'] == 0)).astype(int)
    
    # Match revised overs and targets lookup
    revised_first = matches_df.set_index('match_id')['first_inn_revised_overs'].to_dict()
    revised_second = matches_df.set_index('match_id')['second_inn_revised_overs'].to_dict()
    revised_targets = matches_df.set_index('match_id')['revised_target'].to_dict()
    
    # Calculate Innings 1 totals per match to determine default targets
    inn1_totals = df[df['innings'] == 1].groupby('match_id')['team_delivery_runs'].sum().to_dict()
    
    # Process group-wise for match_id and innings
    print("[DeliveryState] Computing pre-delivery states by match and innings...")
    
    records = []
    
    # Grouping by match_id and innings
    for (match_id, innings), group in df.groupby(['match_id', 'innings'], sort=False):
        g = group.copy().reset_index()
        n = len(g)
        
        # Cumulative metrics strictly BEFORE delivery
        team_runs = g['team_delivery_runs'].values
        team_wickets = g['is_team_wicket'].values
        legals = g['is_legal'].astype(int).values
        boundaries = g['is_boundary'].values
        dots = g['is_dot'].values
        
        cum_runs_before = np.cumsum(team_runs) - team_runs
        cum_wickets_before = np.cumsum(team_wickets) - team_wickets
        cum_legal_before = np.cumsum(legals) - legals
        cum_boundaries_before = np.cumsum(boundaries) - boundaries
        
        # Scheduled overs & balls remaining
        if innings == 1:
            rev_o = revised_first.get(match_id, np.nan)
        else:
            rev_o = revised_second.get(match_id, np.nan)
            
        scheduled_overs = float(rev_o) if pd.notna(rev_o) and rev_o > 0 else 20.0
        total_legal_balls = int(round(scheduled_overs * 6.0))
        
        legal_balls_rem = np.maximum(0, total_legal_balls - cum_legal_before)
        overs_rem = legal_balls_rem / 6.0
        wickets_rem = np.maximum(0, 10 - cum_wickets_before)
        
        # Current run rate (CRR)
        balls_for_crr = np.maximum(cum_legal_before, 1)
        crr = np.where(cum_legal_before > 0, (cum_runs_before / balls_for_crr) * 6.0, 0.0)
        
        # Innings 2 chase variables
        if innings == 2:
            rev_t = revised_targets.get(match_id, np.nan)
            if pd.notna(rev_t) and rev_t > 0:
                target = float(rev_t)
            else:
                target = float(inn1_totals.get(match_id, 0) + 1)
                
            runs_req = np.maximum(0, target - cum_runs_before)
            rrr = np.where(
                legal_balls_rem > 0,
                (runs_req / np.maximum(legal_balls_rem, 1)) * 6.0,
                runs_req * 6.0
            )
            rrr_minus_crr = rrr - crr
        else:
            target = np.nan
            runs_req = np.nan
            rrr = np.nan
            rrr_minus_crr = np.nan
            
        # Rolling 12 and 18 legal balls context
        t12 = np.maximum(0, cum_legal_before - 12)
        idx12 = np.searchsorted(cum_legal_before, t12, side='left')
        w12 = cum_wickets_before - cum_wickets_before[idx12]
        r12 = cum_runs_before - cum_runs_before[idx12]
        b12 = cum_boundaries_before - cum_boundaries_before[idx12]
        
        t18 = np.maximum(0, cum_legal_before - 18)
        idx18 = np.searchsorted(cum_legal_before, t18, side='left')
        w18 = cum_wickets_before - cum_wickets_before[idx18]
        r18 = cum_runs_before - cum_runs_before[idx18]
        b18 = cum_boundaries_before - cum_boundaries_before[idx18]
        
        # Consecutive dot balls before delivery
        consec_dots = np.zeros(n, dtype=int)
        curr_streak = 0
        for i in range(n):
            consec_dots[i] = curr_streak
            if dots[i] == 1:
                curr_streak += 1
            elif legals[i] == 1:
                curr_streak = 0
                
        # Partnership tracking
        p_id = np.cumsum(team_wickets) - team_wickets
        # pre-delivery partnership runs and balls
        part_runs = np.zeros(n, dtype=int)
        part_balls = np.zeros(n, dtype=int)
        for pid_val in np.unique(p_id):
            p_mask = (p_id == pid_val)
            sub_runs = team_runs[p_mask]
            sub_balls = legals[p_mask]
            part_runs[p_mask] = np.cumsum(sub_runs) - sub_runs
            part_balls[p_mask] = np.cumsum(sub_balls) - sub_balls
            
        # Innings stage
        # Powerplay: 0 to 35 legal balls (overs 1-6)
        # Middle: 36 to 89 legal balls (overs 7-15)
        # Death: 90+ legal balls (overs 16-20)
        stage = np.where(
            cum_legal_before < 36,
            'powerplay',
            np.where(cum_legal_before < 90, 'middle', 'death')
        )
        
        g['score_before'] = cum_runs_before
        g['wickets_before'] = cum_wickets_before
        g['legal_balls_bowled'] = cum_legal_before
        g['legal_balls_remaining'] = legal_balls_rem
        g['overs_remaining'] = overs_rem
        g['wickets_remaining'] = wickets_rem
        g['current_run_rate'] = crr
        g['target_runs'] = target
        g['runs_required'] = runs_req
        g['required_run_rate'] = rrr
        g['rrr_minus_crr'] = rrr_minus_crr
        g['wickets_last_12'] = w12
        g['wickets_last_18'] = w18
        g['runs_last_12'] = r12
        g['runs_last_18'] = r18
        g['boundaries_last_12'] = b12
        g['boundaries_last_18'] = b18
        g['consecutive_dots_before'] = consec_dots
        g['partnership_runs_before'] = part_runs
        g['partnership_balls_before'] = part_balls
        g['innings_stage'] = stage
        
        records.append(g)
        
    result_df = pd.concat(records, ignore_index=True)
    if 'index' in result_df.columns:
        result_df = result_df.drop(columns=['index'])
        
    print(f"[DeliveryState] Completed pre-delivery states for {len(result_df):,} rows in {time.time()-t0:.2f}s.")
    return result_df

if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.abspath('.'))
    from src.data.loader import load_data
    data = load_data()
    processed_df = reconstruct_delivery_states(data['ball_by_ball'], data['matches'])
    print(processed_df[['match_id', 'innings', 'legal_balls_bowled', 'score_before', 'wickets_before', 'runs_last_12', 'wickets_last_12']].head(10))
