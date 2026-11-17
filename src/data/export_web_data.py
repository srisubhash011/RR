"""
Export analytical outputs to JSON for Vercel-deployable web dashboard.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import json
import pandas as pd
import numpy as np

def export_for_web(target_dir='web/src/data'):
    print(f"[WebExport] Exporting analytical outputs to {target_dir}...")
    os.makedirs(target_dir, exist_ok=True)
    
    top_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
    top_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')
    all_bat = pd.read_csv('outputs/rankings/all_batters_ranked.csv')
    all_bowl = pd.read_csv('outputs/rankings/all_bowlers_ranked.csv')
    metrics_df = pd.read_csv('outputs/audit/model_evaluation_metrics.csv')
    sens_df = pd.read_csv('outputs/audit/sensitivity_analysis.csv')
    
    # Save rankings JSON
    top_bat.to_json(os.path.join(target_dir, 'top_10_batters.json'), orient='records', indent=2)
    top_bowl.to_json(os.path.join(target_dir, 'top_10_bowlers.json'), orient='records', indent=2)
    all_bat.to_json(os.path.join(target_dir, 'all_batters.json'), orient='records', indent=2)
    all_bowl.to_json(os.path.join(target_dir, 'all_bowlers.json'), orient='records', indent=2)
    metrics_df.to_json(os.path.join(target_dir, 'model_metrics.json'), orient='records', indent=2)
    sens_df.to_json(os.path.join(target_dir, 'sensitivity.json'), orient='records', indent=2)

    # Deliveries sample for match evidence: select high pressure deliveries for top 10 batters & bowlers
    df_del = pd.read_csv('outputs/analytical/delivery_pressure_features.csv')
    top_bat_names = set(top_bat['striker_name'])
    top_bowl_names = set(top_bowl['bowler_name'])
    
    bat_evidence = df_del[
        (df_del['striker_name'].isin(top_bat_names)) &
        (df_del['batting_pressure_score'] >= 35.0)
    ].sort_values('batting_pressure_score', ascending=False).groupby('striker_name').head(15)
    
    bowl_evidence = df_del[
        (df_del['bowler_name'].isin(top_bowl_names)) &
        (df_del['bowling_pressure_score'] >= 35.0)
    ].sort_values('bowling_pressure_score', ascending=False).groupby('bowler_name').head(15)
    
    evidence_df = pd.concat([bat_evidence, bowl_evidence], ignore_index=True)
    evidence_df.to_json(os.path.join(target_dir, 'match_evidence.json'), orient='records', indent=2)
    
    # Aggregate KPIs and overview stats
    summary = {
        'total_matches': 837,
        'total_deliveries': 193988,
        'eligible_batters': len(all_bat),
        'eligible_bowlers': len(all_bowl),
        'pressure_batting_balls': int((df_del['batting_pressure_score'] >= 35.0).sum()),
        'pressure_bowling_balls': int((df_del['bowling_pressure_score'] >= 35.0).sum()),
        'ipl_deliveries': int((df_del['format_type'] == 'IPL').sum()),
        't20i_deliveries': int((df_del['format_type'] == 'T20I').sum()),
        'batting_tiers': df_del['batting_pressure_cat'].value_counts().to_dict(),
        'bowling_tiers': df_del['bowling_pressure_cat'].value_counts().to_dict(),
        'dominant_batting_scenarios': df_del['dominant_batting_scenario'].value_counts().to_dict(),
        'dominant_bowling_scenarios': df_del['dominant_bowling_scenario'].value_counts().to_dict()
    }
    
    with open(os.path.join(target_dir, 'summary_kpis.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print("[WebExport] Successfully exported JSON datasets for web dashboard.")

if __name__ == '__main__':
    export_for_web()
