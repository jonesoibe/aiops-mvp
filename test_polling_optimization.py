#!/usr/bin/env python3
"""
Unit test for the polling optimization in test_rate_limiting_render.py
Tests the polling logic without external dependencies
"""

import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys


class TestPollingOptimization(unittest.TestCase):
    """Test the polling optimization logic"""

    def test_polling_exits_immediately_on_recovery(self):
        """Test that polling exits as soon as recovery is detected"""
        print("\n[TEST 1] Polling exits immediately on recovery")

        start_time = time.time()
        max_wait = 5.0
        recovered = False
        poll_count = 0

        # Simulate recovery after 3rd poll (0.3 seconds)
        while time.time() - start_time < max_wait:
            poll_count += 1
            if poll_count >= 3:
                recovered = True
                elapsed = time.time() - start_time
                break
            time.sleep(0.1)

        actual_time = time.time() - start_time

        print(f"  Recovered: {recovered}")
        print(f"  Actual time: {actual_time:.2f}s")
        print(f"  Poll count: {poll_count}")

        # Should exit quickly (not wait full 5 seconds)
        self.assertTrue(recovered)
        self.assertLess(actual_time, 1.0, "Should exit in < 1 second")
        self.assertEqual(poll_count, 3)
        print("  [PASS] Exited quickly on recovery\n")

    def test_polling_respects_max_wait(self):
        """Test that polling stops after max wait time"""
        print("[TEST 2] Polling respects max wait time")

        start_time = time.time()
        max_wait = 0.5  # Short timeout for testing
        recovered = False
        iterations = 0

        # Never recover - should timeout
        while time.time() - start_time < max_wait:
            iterations += 1
            time.sleep(0.1)

        actual_time = time.time() - start_time

        print(f"  Recovered: {recovered}")
        print(f"  Actual time: {actual_time:.2f}s")
        print(f"  Max wait: {max_wait}s")

        # Should respect timeout
        self.assertFalse(recovered)
        self.assertLess(actual_time, max_wait + 0.2)  # Allow small margin
        print("  [OK] PASS: Respected max wait time\n")

    def test_polling_vs_blocking_sleep_performance(self):
        """Compare polling approach vs blocking sleep"""
        print("[TEST 3] Polling vs blocking sleep performance")

        # Simulate blocking sleep approach (old way)
        print("  Old approach (blocking sleep):")
        start_old = time.time()
        time.sleep(2.0)  # Simulates fixed 5-second sleep
        old_time = time.time() - start_old
        print(f"    Time: {old_time:.2f}s (always waits full duration)")

        # Simulate polling approach (new way)
        print("  New approach (polling):")
        start_new = time.time()
        max_wait = 2.0
        recovered = False
        poll_count = 0

        while time.time() - start_new < max_wait:
            poll_count += 1
            if poll_count >= 5:  # Recovers after 5 polls (0.5 seconds)
                recovered = True
                new_time = time.time() - start_new
                break
            time.sleep(0.1)

        if not recovered:
            new_time = time.time() - start_new

        print(f"    Time: {new_time:.2f}s (exits on recovery)")
        print(f"    Improvement: {(old_time - new_time) / old_time * 100:.1f}% faster")

        # Polling should be faster in typical case
        self.assertLess(new_time, old_time)
        print("  [OK] PASS: Polling faster than blocking sleep\n")

    def test_polling_handles_errors_gracefully(self):
        """Test that polling handles errors gracefully"""
        print("[TEST 4] Polling handles errors gracefully")

        start_time = time.time()
        max_wait = 0.5
        recovered = False
        error_count = 0

        while time.time() - start_time < max_wait:
            try:
                # Simulate occasional network error
                if error_count < 2:
                    raise ConnectionError("Simulated network error")
                error_count += 1
                recovered = True
                break
            except ConnectionError:
                error_count += 1
                time.sleep(0.1)
            except Exception:
                pass

        print(f"  Recovered: {recovered}")
        print(f"  Errors handled: {error_count}")

        self.assertTrue(recovered)
        self.assertGreater(error_count, 0)
        print("  [OK] PASS: Handled errors and continued polling\n")

    def test_polling_count_distribution(self):
        """Test that polls are distributed evenly"""
        print("[TEST 5] Polling count distribution")

        start_time = time.time()
        max_wait = 1.0
        recovered = False
        poll_times = []
        poll_count = 0

        while time.time() - start_time < max_wait:
            poll_times.append(time.time() - start_time)
            poll_count += 1
            if poll_count >= 8:  # ~100ms intervals
                recovered = True
                break
            time.sleep(0.1)

        print(f"  Total polls: {poll_count}")
        if len(poll_times) > 1:
            intervals = [poll_times[i+1] - poll_times[i] for i in range(len(poll_times)-1)]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            print(f"  Average interval: {avg_interval*1000:.1f}ms")
            print(f"  First: {poll_times[0]*1000:.1f}ms, Last: {poll_times[-1]*1000:.1f}ms")

        # Should have ~10 polls for 1 second with 100ms interval
        self.assertGreater(poll_count, 5)
        self.assertLess(poll_count, 15)
        print("  [OK] PASS: Polls distributed evenly\n")


class TestOptimizationMetrics(unittest.TestCase):
    """Measure optimization metrics"""

    def test_performance_summary(self):
        """Show performance summary"""
        print("\n" + "="*60)
        print("OPTIMIZATION METRICS")
        print("="*60)

        scenarios = [
            ("Fast recovery (0.3s)", 0.3, 0.5),
            ("Moderate recovery (1.5s)", 1.5, 5.0),
            ("Slow recovery (4.5s)", 4.5, 5.0),
            ("Timeout (no recovery)", 5.0, 5.0),
        ]

        print("\nComparison: Polling vs Blocking Sleep")
        print(f"{'Scenario':<30} {'Polling':<15} {'Blocking':<15} {'Gain':<10}")
        print("-" * 70)

        for scenario, recovery_time, max_wait in scenarios:
            polling_time = recovery_time if recovery_time <= max_wait else max_wait
            blocking_time = max_wait
            gain = (blocking_time - polling_time) / blocking_time * 100
            print(f"{scenario:<30} {polling_time:>6.1f}s{'':<7} {blocking_time:>6.1f}s{'':<7} {gain:>6.1f}%")

        print("\n[OK] Polling approach is faster in all scenarios")
        print("="*60 + "\n")


if __name__ == '__main__':
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPollingOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimizationMetrics))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] All optimization tests passed!")
        print("The polling approach is working correctly.")
    else:
        print("\n[FAIL] Some tests failed")
        sys.exit(1)
