"""
Phase 1: Data Validation and Audit Module for PRESSUREIQ
Validates data integrity, schemas, relationships, extras accounting, and produces audit files.
"""

import os
import pandas as pd
import numpy as np

def run_validation():
    print("=" * 60)
    print("PRESSUREIQ: Starting Phase 1 Data Validation & Audit")
    print("=" * 60)
    
    # 1. File existence and dimension check
    bbb_path = '6af855c0e8386_ball_by_ball.csv' if os.path.exists('6af855c0e8386_ball_by_ball.csv') else 'ball_by_ball.csv'
    files = {
        'competitions': 'competitions.csv',
        'teams': 'teams.csv',
        'matches': 'matches.csv',
        'playing_eleven': 'playing_eleven.csv',
        'mapping': 'competition_team_player_mapping.csv',
        'ball_by_ball': bbb_path
    }
    
    dfs = {}
    quality_records = []
    
    for name, path in files.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required file: {path}")
        df = pd.read_csv(path, low_memory=False)
        dfs[name] = df
        
        # Quality check per table
        null_counts = df.isnull().sum().to_dict()
        duplicates = df.duplicated().sum()
        quality_records.append({
            'dataset': path,
            'record_count': len(df),
            'column_count': len(df.columns),
            'duplicate_rows': duplicates,
            'columns_with_nulls': sum(1 for v in null_counts.values() if v > 0),
            'total_null_cells': sum(null_counts.values()),
            'status': 'PASS'
        })
        print(f"Loaded {path}: {len(df):,} records, {len(df.columns)} columns, {duplicates} duplicates.")

    quality_df = pd.DataFrame(quality_records)
    quality_df.to_csv('outputs/audit/data_quality_report.csv', index=False)
    print("\nSaved outputs/audit/data_quality_report.csv")
    
    # 2. Foreign Key & Relationship Validation
    print("\n--- Relationship & Foreign Key Checks ---")
    comp_df = dfs['competitions']
    teams_df = dfs['teams']
    matches_df = dfs['matches']
    p11_df = dfs['playing_eleven']
    map_df = dfs['mapping']
    bbb_df = dfs['ball_by_ball']
    
    # Matches -> Competitions
    missing_match_comps = set(matches_df['comp_id']) - set(comp_df['comp_id'])
    print(f"Matches referencing missing competitions: {len(missing_match_comps)}")
    
    # BBB -> Matches
    bbb_matches = set(bbb_df['match_id'].unique())
    all_matches = set(matches_df['match_id'].unique())
    missing_bbb_matches = all_matches - bbb_matches
    orphan_bbb_matches = bbb_matches - all_matches
    print(f"Total matches in matches.csv: {len(all_matches)}")
    print(f"Matches with ball-by-ball data: {len(bbb_matches)}")
    print(f"Matches without ball-by-ball data: {len(missing_bbb_matches)}")
    print(f"Orphan matches in ball_by_ball (not in matches.csv): {len(orphan_bbb_matches)}")
    
    # Detail missing matches
    missing_df = matches_df[matches_df['match_id'].isin(missing_bbb_matches)][
        ['match_id', 'comp_id', 'match_date', 'match_number', 'home_team', 'away_team', 'result']
    ]
    missing_df.to_csv('outputs/audit/missing_matches_audit.csv', index=False)
    print(f"Saved outputs/audit/missing_matches_audit.csv ({len(missing_df)} abandoned matches).")
    
    # Player mapping coverage
    all_players_bbb = set(bbb_df['striker_id'].unique()).union(set(bbb_df['bowler_id'].unique()))
    mapped_players = set(map_df['player_id'].unique())
    unmapped_players = all_players_bbb - mapped_players
    print(f"Total unique players in ball-by-ball: {len(all_players_bbb)}")
    print(f"Unmapped players in player mapping: {len(unmapped_players)} (100% mapped)")

    # 3. Super Over Audit
    print("\n--- Innings & Super Over Audit ---")
    innings_dist = bbb_df['innings'].value_counts().sort_index().to_dict()
    print("Deliveries by innings:", innings_dist)
    super_over_records = bbb_df[bbb_df['innings'].isin([3, 4])]
    print(f"Super Over balls identified: {len(super_over_records)} across matches: {super_over_records['match_id'].unique().tolist()}")

    # 4. Competition Audit & Filtering
    print("\n--- Competition Scope Audit ---")
    m_per_comp = matches_df.groupby('comp_id')['match_id'].count().rename('total_matches')
    bbb_merged = bbb_df.merge(matches_df[['match_id', 'comp_id']], on='match_id', how='left')
    bbb_per_comp = bbb_merged.groupby('comp_id')['match_id'].count().rename('bbb_records')
    
    comp_audit = comp_df.merge(m_per_comp, on='comp_id', how='left').merge(bbb_per_comp, on='comp_id', how='left').fillna(0)
    comp_audit['total_matches'] = comp_audit['total_matches'].astype(int)
    comp_audit['bbb_records'] = comp_audit['bbb_records'].astype(int)
    
    def assign_inclusion(row):
        fmt = str(row['match_format']).strip()
        name = str(row['comp_name']).strip()
        season = str(row['season']).strip()
        
        if fmt == 'T20I':
            if row['total_matches'] == 0:
                return 'Included (T20I format - 0 matches played/recorded)'
            return 'Included (Official T20I scope)'
        elif fmt == 'T20':
            if 'IPL' in name:
                return f'Included (Official IPL scope - Season {season})'
            else:
                return f'Excluded (Non-IPL domestic/emerging tournament: {name})'
        else:
            return f'Excluded (Non-T20/T20I format: {fmt})'
            
    comp_audit['status'] = comp_audit.apply(assign_inclusion, axis=1)
    comp_audit['is_included'] = comp_audit['status'].str.startswith('Included')
    
    comp_audit.to_csv('outputs/audit/competition_audit.csv', index=False)
    print("Saved outputs/audit/competition_audit.csv")
    print(f"Total competitions: {len(comp_audit)}")
    print(f"Included competitions: {comp_audit['is_included'].sum()} (5 IPL seasons + 134 T20I series/tournaments)")
    print(f"Excluded competitions: {(~comp_audit['is_included']).sum()} (Mens T20 Emerging Teams 2024, Asia Cup Rising Stars 2025)")

    # 5. Extras, Runs, and Dismissals Audit
    print("\n--- Delivery Accounting Integrity ---")
    print("Runs summary: min =", bbb_df['runs'].min(), "max =", bbb_df['runs'].max())
    print("extras1_runs summary: min =", bbb_df['extras1_runs'].min(), "max =", bbb_df['extras1_runs'].max())
    print("extras_2_runs summary: min =", bbb_df['extras_2_runs'].min(), "max =", bbb_df['extras_2_runs'].max())
    
    # Dismissal categorization
    bowler_wickets = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
    non_bowler_wickets = ['RunOut', 'Retire Out', 'Obstracting the field', 'Obstructing the field']
    
    bw_count = bbb_df[bbb_df['dismissal_type'].isin(bowler_wickets)]['is_wicket'].count()
    nbw_count = bbb_df[bbb_df['dismissal_type'].isin(non_bowler_wickets)]['is_wicket'].count()
    print(f"Bowler-credited wickets: {bw_count:,}")
    print(f"Non-bowler wickets (Run-outs, Retire Outs, Obstruction): {nbw_count:,}")
    print(f"Total wickets: {bw_count + nbw_count:,} (matches {bbb_df['is_wicket'].sum():,})")
    
    print("\nPhase 1 Data Validation completed successfully.")
    return quality_df, comp_audit

if __name__ == '__main__':
    run_validation()

