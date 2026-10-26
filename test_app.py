"""
Automated Verification Test Suite for Behaviour Insights
Validates statistical correctness, edge cases, response structures, and platform behaviors.
"""

import unittest
import json
from app import app, PLATFORMS, generate_synthetic_data

class BehaviourInsightsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_1_homepage_renders(self):
        """Test GET / returns 200 and loads HTML template."""
        res = self.app.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Behaviour Insights', res.data)
        self.assertIn(b'analyticsChart', res.data)

    def test_2_netflix_normal_pdf(self):
        """Test Netflix returns continuous model with normal PDF reflecting mean and std."""
        payload = {
            "platform": "Netflix",
            "data_source": "preset",
            "preset_key": "balanced",
            "threshold": 150
        }
        res = self.app.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['analysis']['model_type'], 'continuous')
        stats = data['analysis']['stats']
        self.assertGreater(stats['mean'], 0)
        self.assertGreater(stats['pop_std'], 0)
        # Verify chart data contains continuous histogram and pdf
        chart = data['analysis']['chart_data']
        self.assertEqual(chart['chart_type'], 'continuous_normal')
        self.assertIn('histogram', chart)
        self.assertIn('pdf_curve', chart)
        self.assertEqual(len(chart['histogram']['counts']), len(chart['histogram']['labels']))

    def test_3_spotify_changes_with_different_data(self):
        """Test Spotify data updates dynamically when input changes."""
        payload1 = {
            "platform": "Spotify",
            "data_source": "manual",
            "manual_input": "20, 25, 30, 22, 18",
            "threshold": 90
        }
        res1 = self.app.post('/api/analyze', data=json.dumps(payload1), content_type='application/json')
        data1 = res1.get_json()

        payload2 = {
            "platform": "Spotify",
            "data_source": "manual",
            "manual_input": "160, 180, 200, 190, 175",
            "threshold": 90
        }
        res2 = self.app.post('/api/analyze', data=json.dumps(payload2), content_type='application/json')
        data2 = res2.get_json()

        # Check means are vastly different
        self.assertNotEqual(data1['analysis']['stats']['mean'], data2['analysis']['stats']['mean'])
        self.assertNotEqual(data1['insights']['tier'], data2['insights']['tier'])
        self.assertNotEqual(data1['analysis']['stats']['empirical_prob'], data2['analysis']['stats']['empirical_prob'])

    def test_4_amazon_discrete_poisson(self):
        """Test Amazon returns discrete Poisson model with integer k values and PMF."""
        payload = {
            "platform": "Amazon",
            "data_source": "preset",
            "preset_key": "balanced",
            "threshold": 20
        }
        res = self.app.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['analysis']['model_type'], 'discrete')
        chart = data['analysis']['chart_data']
        self.assertEqual(chart['chart_type'], 'discrete_poisson')
        self.assertIn('k_values', chart)
        self.assertIn('poisson_pmf', chart)
        self.assertIn('observed_counts', chart)
        # Verify k values are integers
        for k in chart['k_values']:
            self.assertIsInstance(k, int)

    def test_5_threshold_change_updates_probabilities(self):
        """Test modifying threshold changes empirical and theoretical probabilities."""
        payload_low_thresh = {
            "platform": "Netflix",
            "data_source": "preset",
            "preset_key": "balanced",
            "threshold": 50
        }
        res_low = self.app.post('/api/analyze', data=json.dumps(payload_low_thresh), content_type='application/json')
        data_low = res_low.get_json()

        payload_high_thresh = {
            "platform": "Netflix",
            "data_source": "preset",
            "preset_key": "balanced",
            "threshold": 250
        }
        res_high = self.app.post('/api/analyze', data=json.dumps(payload_high_thresh), content_type='application/json')
        data_high = res_high.get_json()

        # Lower threshold must have higher probability than high threshold
        self.assertGreater(data_low['analysis']['stats']['empirical_prob'], data_high['analysis']['stats']['empirical_prob'])
        self.assertGreater(data_low['analysis']['stats']['theoretical_prob'], data_high['analysis']['stats']['theoretical_prob'])

    def test_6_zero_variance_safety(self):
        """Test that identical observations (zero variance) do not crash the app."""
        payload = {
            "platform": "Netflix",
            "data_source": "manual",
            "manual_input": "120, 120, 120, 120, 120",
            "threshold": 120
        }
        res = self.app.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['analysis']['stats']['pop_std'], 0.0)
        self.assertEqual(data['analysis']['stats']['pop_variance'], 0.0)
        self.assertEqual(data['analysis']['stats']['empirical_prob'], 1.0)

    def test_7_invalid_inputs_handled_gracefully(self):
        """Test empty input and negative numbers return friendly JSON errors."""
        # Negative numbers
        res_neg = self.app.post('/api/analyze', data=json.dumps({
            "platform": "Netflix",
            "data_source": "manual",
            "manual_input": "100, -25, 120"
        }), content_type='application/json')
        self.assertEqual(res_neg.status_code, 400)
        self.assertIn("non-negative", res_neg.get_json()['error'])

        # Non-numeric text
        res_char = self.app.post('/api/analyze', data=json.dumps({
            "platform": "Netflix",
            "data_source": "manual",
            "manual_input": "abc, def"
        }), content_type='application/json')
        self.assertEqual(res_char.status_code, 400)
        self.assertIn("non-numeric", res_char.get_json()['error'])

        # Empty manual input
        res_empty = self.app.post('/api/analyze', data=json.dumps({
            "platform": "Netflix",
            "data_source": "manual",
            "manual_input": "   "
        }), content_type='application/json')
        self.assertEqual(res_empty.status_code, 400)

if __name__ == '__main__':
    unittest.main()
