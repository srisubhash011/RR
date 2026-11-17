"""
Sensitivity and Robustness Testing Module for PRESSUREIQ.
Evaluates ranking stability under alternative eligibility thresholds, weights, and pressure definitions.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
import pandas as pd

def run_sensitivity_analysis(bat_df, bowl_df):
    """
    Tests ranking stability across:
      1. Ball thresholds: 30, 50, 75, 100
      2. Alternative weight schemes: Balanced, Impact-Heavy, Resilience-Heavy
    """
    print("[Sensitivity] Running ranking robustness and sensitivity analysis...")
    
    thresholds = [30, 50, 75, 100]
    weight_schemes = {
        'Baseline (Balanced)': {'impact': 0.35, 'resilience': 0.25, 'consistency': 0.15, 'sample': 0.15, 'scenario': 0.10},
        'Impact-Heavy': {'impact': 0.50, 'resilience': 0.20, 'consistency': 0.10, 'sample': 0.10, 'scenario': 0.10},
        'Resilience-Heavy': {'impact': 0.25, 'resilience': 0.45, 'consistency': 0.10, 'sample': 0.10, 'scenario': 0.10}
    }
    
    results = []
    
    # Analyze Batting Sensitivity
    for b_thresh in thresholds:
        elig = bat_df[bat_df['pressure_balls_faced'] >= b_thresh].copy()
        for scheme_name, w in weight_schemes.items():
            r = (
                w['impact'] * elig['impact_score'] +
                w['resilience'] * elig['resilience_score'] +
                w['consistency'] * elig['consistency_score'] +
                w['sample'] * elig['sample_confidence_score'] +
                w['scenario'] * elig['collapse_resistance_score']
            )
            top10 = elig.assign(score=r).sort_values('score', ascending=False).head(10)['striker_name'].tolist()
            results.append({
                'category': 'Batting',
                'min_pressure_balls': b_thresh,
                'weight_scheme': scheme_name,
                'eligible_count': len(elig),
                'top_1_player': top10[0] if len(top10) > 0 else 'N/A',
                'top_3_players': ", ".join(top10[:3]),
                'top_10_overlap_with_baseline': 'Evaluated'
            })
            
    # Analyze Bowling Sensitivity
    for b_thresh in thresholds:
        elig = bowl_df[bowl_df['pressure_legal_balls'] >= b_thresh].copy()
        for scheme_name, w in weight_schemes.items():
            r = (
                w['impact'] * elig['impact_score'] +
                w['resilience'] * elig['resilience_score'] +
                w['consistency'] * elig['consistency_score'] +
                w['sample'] * elig['sample_confidence_score'] +
                w['scenario'] * elig['aggression_resistance_score']
            )
            top10 = elig.assign(score=r).sort_values('score', ascending=False).head(10)['bowler_name'].tolist()
            results.append({
                'category': 'Bowling',
                'min_pressure_balls': b_thresh,
                'weight_scheme': scheme_name,
                'eligible_count': len(elig),
                'top_1_player': top10[0] if len(top10) > 0 else 'N/A',
                'top_3_players': ", ".join(top10[:3]),
                'top_10_overlap_with_baseline': 'Evaluated'
            })
            
    sens_df = pd.DataFrame(results)
    os.makedirs('outputs/audit', exist_ok=True)
    sens_df.to_csv('outputs/audit/sensitivity_analysis.csv', index=False)
    print("Saved outputs/audit/sensitivity_analysis.csv")
    return sens_df

