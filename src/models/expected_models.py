"""
Expected Performance Models for PRESSUREIQ.
Implements leak-free out-of-fold match-grouped GBDT models for Batting and Bowling expected outcomes.
Evaluates expected runs, boundaries, dot balls, dismissals, and wickets.
"""

import os, sys
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, roc_auc_score, log_loss
import time

def train_and_predict_expected_models(df):
    """
    Fits expected performance models using 5-Fold GroupKFold on match_id.
    Produces out-of-fold predictions for every delivery:
      Batting:
        exp_batter_runs
        exp_is_boundary
        exp_is_dot
        exp_is_out
      Bowling:
        exp_bowler_runs
        exp_bowler_wicket
        exp_bowler_dot
    """
    t0 = time.time()
    print("[ExpectedModels] Starting leak-free match-grouped expected performance modeling...")
    
    # Feature preparation
    features = [
        'innings',
        'legal_balls_bowled',
        'legal_balls_remaining',
        'wickets_before',
        'wickets_remaining',
        'current_run_rate',
        'required_run_rate_filled',
        'runs_last_12',
        'wickets_last_12',
        'runs_last_18',
        'wickets_last_18',
        'boundaries_last_12',
        'consecutive_dots_before',
        'partnership_runs_before',
        'partnership_balls_before',
        'batting_order_filled',
        'is_ipl',
        'stage_powerplay',
        'stage_death',
        'is_spin'
    ]
    
    df_feat = pd.DataFrame(index=df.index)
    df_feat['innings'] = df['innings'].astype(float)
    df_feat['legal_balls_bowled'] = df['legal_balls_bowled'].astype(float)
    df_feat['legal_balls_remaining'] = df['legal_balls_remaining'].astype(float)
    df_feat['wickets_before'] = df['wickets_before'].astype(float)
    df_feat['wickets_remaining'] = df['wickets_remaining'].astype(float)
    df_feat['current_run_rate'] = df['current_run_rate'].astype(float)
    df_feat['required_run_rate_filled'] = df['required_run_rate'].fillna(0.0).astype(float)
    df_feat['runs_last_12'] = df['runs_last_12'].astype(float)
    df_feat['wickets_last_12'] = df['wickets_last_12'].astype(float)
    df_feat['runs_last_18'] = df['runs_last_18'].astype(float)
    df_feat['wickets_last_18'] = df['wickets_last_18'].astype(float)
    df_feat['boundaries_last_12'] = df['boundaries_last_12'].astype(float)
    df_feat['consecutive_dots_before'] = df['consecutive_dots_before'].astype(float)
    df_feat['partnership_runs_before'] = df['partnership_runs_before'].astype(float)
    df_feat['partnership_balls_before'] = df['partnership_balls_before'].astype(float)
    df_feat['batting_order_filled'] = df['batting_order'].fillna(4).astype(float)
    df_feat['is_ipl'] = (df['format_type'] == 'IPL').astype(float)
    df_feat['stage_powerplay'] = (df['innings_stage'] == 'powerplay').astype(float)
    df_feat['stage_death'] = (df['innings_stage'] == 'death').astype(float)
    df_feat['is_spin'] = (df['pace_or_spin'].str.lower().fillna('pace') == 'spin').astype(float)
    
    X = df_feat[features].values
    groups = df['match_id'].values
    n = len(df)
    
    # Target variables
    # 1. Batter runs (for legal balls faced)
    y_bat_runs = df['batter_runs'].values.astype(float)
    # 2. Striker out on delivery
    is_striker_out = (df['is_wicket'] & (df['dismissed_player_id'] == df['striker_id'])).astype(int).values
    # 3. Boundary
    y_boundary = df['is_boundary'].values.astype(int)
    # 4. Dot ball
    y_dot = df['is_dot'].values.astype(int)
    # 5. Bowler runs conceded
    y_bowl_runs = df['bowler_runs_conceded'].values.astype(float)
    # 6. Bowler credited wicket
    y_bowl_wicket = df['bowler_credited_wicket'].values.astype(int)
    
    # Placeholders for out-of-fold predictions
    oof_bat_runs = np.zeros(n, dtype=float)
    oof_bat_boundary = np.zeros(n, dtype=float)
    oof_bat_dot = np.zeros(n, dtype=float)
    oof_bat_out = np.zeros(n, dtype=float)
    
    oof_bowl_runs = np.zeros(n, dtype=float)
    oof_bowl_wicket = np.zeros(n, dtype=float)
    oof_bowl_dot = np.zeros(n, dtype=float)
    
    # GroupKFold (5 splits)
    gkf = GroupKFold(n_splits=5)
    
    reg_params = {
        'n_estimators': 80,
        'learning_rate': 0.08,
        'max_depth': 5,
        'num_leaves': 31,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1
    }
    
    clf_params = {
        'n_estimators': 80,
        'learning_rate': 0.08,
        'max_depth': 5,
        'num_leaves': 31,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1
    }
    
    print("[ExpectedModels] Running 5-fold cross-validation with GroupKFold by match_id...")
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, groups=groups), 1):
        print(f"  Training Fold {fold}/5 on {len(train_idx):,} rows, validating on {len(val_idx):,} rows...")
        X_tr, X_val = X[train_idx], X[val_idx]
        
        # 1. Batter runs
        m_bat_runs = lgb.LGBMRegressor(**reg_params).fit(X_tr, y_bat_runs[train_idx])
        oof_bat_runs[val_idx] = m_bat_runs.predict(X_val)
        
        # 2. Boundary prob
        m_boundary = lgb.LGBMClassifier(**clf_params).fit(X_tr, y_boundary[train_idx])
        oof_bat_boundary[val_idx] = m_boundary.predict_proba(X_val)[:, 1]
        
        # 3. Striker dismissal prob
        m_out = lgb.LGBMClassifier(**clf_params).fit(X_tr, is_striker_out[train_idx])
        oof_bat_out[val_idx] = m_out.predict_proba(X_val)[:, 1]
        
        # 4. Dot ball prob
        m_dot = lgb.LGBMClassifier(**clf_params).fit(X_tr, y_dot[train_idx])
        oof_bat_dot[val_idx] = m_dot.predict_proba(X_val)[:, 1]
        
        # 5. Bowler runs
        m_bowl_runs = lgb.LGBMRegressor(**reg_params).fit(X_tr, y_bowl_runs[train_idx])
        oof_bowl_runs[val_idx] = m_bowl_runs.predict(X_val)
        
        # 6. Bowler wicket prob
        m_wicket = lgb.LGBMClassifier(**clf_params).fit(X_tr, y_bowl_wicket[train_idx])
        oof_bowl_wicket[val_idx] = m_wicket.predict_proba(X_val)[:, 1]
        
        # Bowler dot matches dot ball
        oof_bowl_dot[val_idx] = oof_bat_dot[val_idx]

    # Evaluate validation metrics
    metrics = [
        {
            'model': 'Batting Expected Runs',
            'metric': 'RMSE',
            'value': np.sqrt(mean_squared_error(y_bat_runs, oof_bat_runs)),
            'target_mean': np.mean(y_bat_runs)
        },
        {
            'model': 'Batting Expected Runs',
            'metric': 'MAE',
            'value': mean_absolute_error(y_bat_runs, oof_bat_runs),
            'target_mean': np.mean(y_bat_runs)
        },
        {
            'model': 'Batting Dismissal Probability',
            'metric': 'ROC-AUC',
            'value': roc_auc_score(is_striker_out, oof_bat_out),
            'target_mean': np.mean(is_striker_out)
        },
        {
            'model': 'Batting Boundary Probability',
            'metric': 'ROC-AUC',
            'value': roc_auc_score(y_boundary, oof_bat_boundary),
            'target_mean': np.mean(y_boundary)
        },
        {
            'model': 'Bowling Expected Runs Conceded',
            'metric': 'RMSE',
            'value': np.sqrt(mean_squared_error(y_bowl_runs, oof_bowl_runs)),
            'target_mean': np.mean(y_bowl_runs)
        },
        {
            'model': 'Bowling Wicket Probability',
            'metric': 'ROC-AUC',
            'value': roc_auc_score(y_bowl_wicket, oof_bowl_wicket),
            'target_mean': np.mean(y_bowl_wicket)
        }
    ]
    
    metrics_df = pd.DataFrame(metrics)
    os.makedirs('outputs/audit', exist_ok=True)
    metrics_df.to_csv('outputs/audit/model_evaluation_metrics.csv', index=False)
    print("\nSaved outputs/audit/model_evaluation_metrics.csv")
    print(metrics_df)
    
    # Assign out-of-fold predictions to DataFrame
    df = df.copy()
    df['exp_batter_runs'] = np.maximum(0.0, oof_bat_runs)
    df['exp_is_boundary'] = np.clip(oof_bat_boundary, 0.0, 1.0)
    df['exp_is_dot'] = np.clip(oof_bat_dot, 0.0, 1.0)
    df['exp_is_out'] = np.clip(oof_bat_out, 0.0, 1.0)
    
    df['exp_bowler_runs'] = np.maximum(0.0, oof_bowl_runs)
    df['exp_bowler_wicket'] = np.clip(oof_bowl_wicket, 0.0, 1.0)
    df['exp_bowler_dot'] = np.clip(oof_bowl_dot, 0.0, 1.0)
    
    # Compute delivery-level impacts
    # Batting Impact: Actual runs - Expected runs
    # (Adjusted for wicket loss: losing a wicket costs ~expected runs that wicket would have produced)
    df['batting_impact'] = df['batter_runs'] - df['exp_batter_runs']
    # Bowling Impact: Expected runs - Actual runs (runs saved, higher is better for bowler)
    # Wicket impact: taking a wicket saves expected runs (~10 runs per wicket in T20)
    df['bowling_runs_saved'] = df['exp_bowler_runs'] - df['bowler_runs_conceded']
    df['bowling_impact'] = df['bowling_runs_saved'] + (df['bowler_credited_wicket'] - df['exp_bowler_wicket']) * 8.0
    
    print(f"[ExpectedModels] Completed all models in {time.time()-t0:.2f}s.")
    return df

if __name__ == '__main__':
    from src.data.loader import load_data
    from src.data.delivery_state import reconstruct_delivery_states
    from src.pressure.pressure_scoring import compute_pressure_scores
    
    data = load_data()
    ds_df = reconstruct_delivery_states(data['ball_by_ball'], data['matches'])
    p_df = compute_pressure_scores(ds_df)
    exp_df = train_and_predict_expected_models(p_df)
    print(exp_df[['match_id', 'striker_name', 'bowler_name', 'batting_pressure_score', 'batting_impact', 'bowling_impact']].head(10))

