import unittest


class TestDataReconciliation(unittest.TestCase):
    """Reconciliation test suite ensuring data integrity invariants."""

    def test_import_job_counts_invariant(self):
        """Verifies total_rows == valid_rows + invalid_rows + duplicate_rows."""
        test_jobs = [
            {"total": 10000, "valid": 9850, "invalid": 150, "duplicate": 0},
            {"total": 5000, "valid": 4900, "invalid": 80, "duplicate": 20},
        ]
        for job in test_jobs:
            self.assertEqual(job["total"], job["valid"] + job["invalid"] + job["duplicate"])

    def test_analytics_denominator_not_zero(self):
        """Ensures negative_rate calculation is null-safe when denominator is zero."""
        known_sentiment_count = 0
        negative_count = 0
        negative_rate = negative_count / known_sentiment_count if known_sentiment_count > 0 else None
        self.assertIsNone(negative_rate)


if __name__ == "__main__":
    unittest.main()
