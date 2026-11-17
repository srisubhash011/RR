"""
Par-score model for 1st innings historical baseline trajectory in PRESSUREIQ.
Estimates the expected runs trajectory based on format (IPL / T20I) and overs completed.
"""

import numpy as np
import pandas as pd

class HistoricalParModel:
    def __init__(self):
        # Default empirical baselines from 2022-2026 data
        # Average run trajectory by over (1 to 20)
        self.ipl_over_par = {
            1: 6.5, 2: 14.5, 3: 23.0, 4: 32.5, 5: 42.0, 6: 52.0,
            7: 60.5, 8: 69.0, 9: 77.5, 10: 86.5, 11: 95.5, 12: 105.0,
            13: 115.5, 14: 126.5, 15: 138.0, 16: 150.5, 17: 164.0, 18: 178.5,
            19: 193.0, 20: 205.0
        }
        self.t20i_over_par = {
            1: 6.0, 2: 13.0, 3: 21.0, 4: 29.5, 5: 38.0, 6: 47.0,
            7: 54.5, 8: 62.0, 9: 70.0, 10: 78.0, 11: 86.0, 12: 94.5,
            13: 103.5, 14: 113.0, 15: 123.0, 16: 134.0, 17: 146.0, 18: 159.0,
            19: 172.0, 20: 184.0
        }
        self.fitted = False

    def fit(self, df):
        """Fit empirical average score_before by format and overid for 1st innings."""
        inn1 = df[df['innings'] == 1]
        grouped = inn1.groupby(['format_type', 'overid'])['score_before'].mean().to_dict()
        
        for o in range(1, 21):
            if ('IPL', o) in grouped:
                self.ipl_over_par[o] = grouped[('IPL', o)]
            if ('T20I', o) in grouped:
                self.t20i_over_par[o] = grouped[('T20I', o)]
        self.fitted = True
        return self

    def predict_par(self, format_types, overids):
        """Vectorized par score lookup."""
        n = len(overids)
        pars = np.zeros(n, dtype=float)
        
        for i in range(n):
            fmt = format_types[i]
            ov = max(1, min(20, int(overids[i])))
            if fmt == 'IPL':
                pars[i] = self.ipl_over_par.get(ov, 100.0)
            else:
                pars[i] = self.t20i_over_par.get(ov, 90.0)
        return pars

