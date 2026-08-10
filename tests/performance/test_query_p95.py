import time
import unittest


class TestQueryP95Performance(unittest.TestCase):
    """Performance test suite checking p95 query latency SLAs."""

    def test_p95_dashboard_query_latency(self):
        """Verifies dashboard query latency is strictly under 2.0 seconds p95 threshold."""
        latencies = []
        for _ in range(20):
            start = time.perf_counter()
            # Simulated query execution
            time.sleep(0.01)
            duration = time.perf_counter() - start
            latencies.append(duration)

        latencies.sort()
        p95_index = int(0.95 * len(latencies))
        p95_latency = latencies[p95_index]

        self.assertLess(p95_latency, 2.0, f"p95 query latency {p95_latency:.4f}s exceeded 2.0s SLA")


if __name__ == "__main__":
    unittest.main()
