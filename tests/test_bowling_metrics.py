"""
Unit tests for bowling metrics, economy rate, and runs saved.
"""

import unittest
import numpy as np

class TestBowlingMetrics(unittest.TestCase):
    def test_economy_calculation(self):
        runs = 28
        legal_balls = 24
        econ = (runs / legal_balls) * 6.0
        self.assertAlmostEqual(econ, 7.0)

    def test_runs_saved(self):
        exp_runs = 12.5
        act_runs = 8.0
        runs_saved = exp_runs - act_runs
        self.assertAlmostEqual(runs_saved, 4.5)

    def test_bowling_resilience_delta_econ(self):
        # Positive delta indicates tighter bowling under pressure
        norm_econ = 8.8
        press_econ = 7.2
        delta_econ = norm_econ - press_econ
        self.assertAlmostEqual(delta_econ, 1.6)

if __name__ == '__main__':
    unittest.main()

