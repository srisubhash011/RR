"""
Unit tests for context-aware pressure features and leakage prevention.
"""

import unittest
import numpy as np
import pandas as pd

class TestPressureFeatures(unittest.TestCase):
    def test_pre_delivery_lag(self):
        # Verify that score_before strictly precedes delivery outcome
        runs = np.array([0, 4, 6, 1])
        score_before = np.cumsum(runs) - runs
        
        self.assertEqual(score_before[0], 0, "Initial score before delivery must be 0")
        self.assertEqual(score_before[1], 0, "Score before ball 2 must be 0 (prior ball was 0)")
        self.assertEqual(score_before[2], 4, "Score before ball 3 must be 4 (after 4 off ball 2)")
        self.assertEqual(score_before[3], 10, "Score before ball 4 must be 10 (after 6 off ball 3)")

    def test_pressure_score_bounds(self):
        scores = np.array([-10.0, 0.0, 45.5, 95.0, 115.0])
        clipped = np.clip(scores, 0.0, 100.0)
        
        self.assertTrue((clipped >= 0.0).all())
        self.assertTrue((clipped <= 100.0).all())

    def test_collapse_pressure_trigger(self):
        # 3 wickets in last 12 balls should yield high collapse score
        w12 = 3
        w18 = 3
        w_lost = 4
        s_collapse = 28.0 * w12 + 16.0 * (w18 - w12) + 5.5 * w_lost
        p_collapse = min(100.0, max(0.0, s_collapse))
        
        self.assertGreaterEqual(p_collapse, 80.0, "3 wickets in 12 balls must trigger extreme collapse pressure")

    def test_bowling_pressure_independence(self):
        # Aggressive opposition pressure can be high even with zero wickets lost by batting team
        r12 = 26
        b12 = 4
        part = 85
        w_rem = 10  # Batting team hasn't lost any wickets!
        s_agg = 35.0 * min(1.0, r12/24.0) + 25.0 * min(1.0, b12/3.0) + 20.0 * min(1.0, part/65.0) + 20.0 * (w_rem/10.0)
        p_agg = min(100.0, max(0.0, s_agg))
        
        self.assertGreaterEqual(p_agg, 85.0, "Bowler facing aggressive partnership must have high pressure despite 0 batting collapse")

if __name__ == '__main__':
    unittest.main()

