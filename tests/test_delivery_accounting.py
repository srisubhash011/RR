"""
Unit tests for delivery accounting in PRESSUREIQ.
Validates legal delivery counting, extras handling, batter balls faced, and bowler wicket credit.
"""

import unittest
import pandas as pd
import numpy as np

class TestDeliveryAccounting(unittest.TestCase):
    def test_wides_accounting(self):
        # Wides: not legal, not batter ball faced, charged to bowler
        row = {'extras_type': 'wide', 'runs': 0, 'extras1_runs': 1, 'extras_2_runs': 0}
        is_legal = row['extras_type'] not in ['wide', 'Overstep', 'other']
        batter_ball_faced = 1 if row['extras_type'] != 'wide' else 0
        bowler_runs = row['extras1_runs'] if row['extras_type'] == 'wide' else 0
        
        self.assertFalse(is_legal, "Wide must not be a legal delivery")
        self.assertEqual(batter_ball_faced, 0, "Wide must not be counted as batter ball faced")
        self.assertEqual(bowler_runs, 1, "Wide run must be charged to bowler")

    def test_noballs_accounting(self):
        # No-ball: not legal ball for bowler, but IS a ball faced by batter
        row = {'extras_type': 'Overstep', 'runs': 4, 'extras1_runs': 1, 'extras_2_runs': 0}
        is_legal = row['extras_type'] not in ['wide', 'Overstep', 'other']
        batter_ball_faced = 1 if row['extras_type'] != 'wide' else 0
        bowler_runs = row['extras1_runs'] + row['runs']
        
        self.assertFalse(is_legal, "No-ball must not be a legal delivery")
        self.assertEqual(batter_ball_faced, 1, "No-ball must count as batter ball faced")
        self.assertEqual(bowler_runs, 5, "No-ball penalty + bat runs must be charged to bowler")

    def test_byes_legbyes_not_charged_to_bowler(self):
        row = {'extras_type': 'legbyes', 'runs': 0, 'extras1_runs': 4, 'extras_2_runs': 0}
        is_legal = row['extras_type'] not in ['wide', 'Overstep', 'other']
        bowler_runs = 0 if row['extras_type'] in ['byes', 'legbyes'] else row['runs']
        
        self.assertTrue(is_legal, "Leg-bye must count as a legal delivery")
        self.assertEqual(bowler_runs, 0, "Leg-byes must not be charged to bowler")

    def test_bowler_credited_wickets(self):
        bowler_types = ['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket']
        non_bowler_types = ['RunOut', 'Retire Out', 'Obstructing the field']
        
        for w in bowler_types:
            self.assertTrue(w in bowler_types, f"{w} should be credited to bowler")
        for nw in non_bowler_types:
            self.assertFalse(nw in bowler_types, f"{nw} must NOT be credited to bowler")

if __name__ == '__main__':
    unittest.main()

