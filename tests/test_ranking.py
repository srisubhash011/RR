"""
Unit tests for final ranking outputs, top 10 lists, and player mappings.
"""

import unittest
import pandas as pd
import numpy as np
import os

class TestRanking(unittest.TestCase):
    def setUp(self):
        self.top_bat = pd.read_csv('outputs/rankings/top_10_batters.csv')
        self.top_bowl = pd.read_csv('outputs/rankings/top_10_bowlers.csv')
        self.mapping = pd.read_csv('competition_team_player_mapping.csv')
        self.mapped_ids = set(self.mapping['player_id'].unique())

    def test_top_10_length_and_uniqueness(self):
        self.assertEqual(len(self.top_bat), 10, "Top 10 batters must have exactly 10 rows")
        self.assertEqual(len(self.top_bowl), 10, "Top 10 bowlers must have exactly 10 rows")
        
        self.assertEqual(self.top_bat['striker_id'].nunique(), 10, "Top 10 batters must have 10 distinct player IDs")
        self.assertEqual(self.top_bowl['bowler_id'].nunique(), 10, "Top 10 bowlers must have 10 distinct player IDs")

    def test_sequential_ranks(self):
        self.assertListEqual(list(self.top_bat['rank']), list(range(1, 11)), "Batters ranks must be 1 to 10")
        self.assertListEqual(list(self.top_bowl['rank']), list(range(1, 11)), "Bowlers ranks must be 1 to 10")

    def test_players_exist_in_mapping(self):
        for pid in self.top_bat['striker_id']:
            self.assertIn(pid, self.mapped_ids, f"Batter ID {pid} must exist in official mapping")
        for pid in self.top_bowl['bowler_id']:
            self.assertIn(pid, self.mapped_ids, f"Bowler ID {pid} must exist in official mapping")

    def test_confidence_intervals_valid(self):
        for idx, r in self.top_bat.iterrows():
            self.assertLessEqual(r['ci_lower'], r['final_rating'])
            self.assertGreaterEqual(r['ci_upper'], r['final_rating'])
        for idx, r in self.top_bowl.iterrows():
            self.assertLessEqual(r['ci_lower'], r['final_rating'])
            self.assertGreaterEqual(r['ci_upper'], r['final_rating'])

if __name__ == '__main__':
    unittest.main()

