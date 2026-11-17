"""
Unit tests for batting metrics, expected impact, and resilience.
"""

import unittest
import numpy as np
import pandas as pd

class TestBattingMetrics(unittest.TestCase):
    def test_strike_rate_calculation(self):
        runs = 45
        balls = 30
        sr = (runs / balls) * 100.0
        self.assertAlmostEqual(sr, 150.0)

    def test_batting_impact(self):
        actual_runs = 6
        exp_runs = 1.35
        impact = actual_runs - exp_runs
        self.assertAlmostEqual(impact, 4.65)

    def test_resilience_delta_sr(self):
        norm_sr = 140.0
        press_sr = 165.0
        delta_sr = press_sr - norm_sr
        self.assertAlmostEqual(delta_sr, 25.0)

if __name__ == '__main__':
    unittest.main()

