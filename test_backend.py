import unittest
from backend.engine import analyze

class EngineTests(unittest.TestCase):
    def test_exact_copy(self):
        text = 'Machine learning discovers patterns in data. Models learn from examples.'
        result = analyze(text, [{'name': 'Copy', 'text': text}])
        self.assertAlmostEqual(result['similarity'], 1)
        self.assertTrue(all(p['flagged'] for p in result['passages']))

    def test_unrelated(self):
        result = analyze('Zebras gallop across savannas.', [{'name': 'Other', 'text': 'Quantum photons exhibit entanglement.'}])
        self.assertLess(result['similarity'], .15)

    def test_limits(self):
        with self.assertRaises(ValueError):
            analyze('Sentence. ' * 301, [{'name': 'Ref', 'text': 'Hello.'}])

if __name__ == '__main__':
    unittest.main()
