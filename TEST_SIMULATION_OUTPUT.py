#!/usr/bin/env python3
"""
Test script to verify the Synchronized Simulation Output System
Run this to confirm all outputs are working correctly
"""

import json
from simulation_output_generator import SimulationOutputGenerator


def test_cpu_spike():
    """Test CPU Spike chaos type"""
    print("\n" + "="*70)
    print("TEST 1: CPU SPIKE @ 75% INTENSITY")
    print("="*70)

    config = {
        'execution_id': 'test_cpu_001',
        'chaos_type': 'cpu_spike',
        'intensity': 0.75,
        'duration': 60,
        'target_service': 'api-gateway',
        'advanced': {
            'ramp_up_time': 5,
            'ramp_down_time': 5
        }
    }

    gen = SimulationOutputGenerator(config)
    outputs = gen.generate_all()

    print("\n[CONSOLE OUTPUT]")
    print(f"  Lines: {len(outputs['console'])}")
    print(f"  First log: {outputs['console'][0]['message'][:60]}")
    print(f"  Last log: {outputs['console'][-1]['message'][:60]}")

    print("\n[METRICS OUTPUT]")
    print(f"  Total metrics: {len(outputs['metrics'])}")
    print(f"  Metric names: {[m['name'] for m in outputs['metrics']]}")
    for metric in outputs['metrics'][:2]:
        print(f"    - {metric['name']}: min={metric['min']:.1f}, max={metric['max']:.1f}, mean={metric['mean']:.1f} {metric['unit']}")

    print("\n[ANALYSIS OUTPUT]")
    analysis = outputs['analysis']
    print(f"  Chaos type: {analysis['simulation_config']['chaos_type']}")
    print(f"  Intensity: {analysis['simulation_config']['intensity']:.0%}")
    print(f"  Anomalies detected: {analysis['detection_results']['anomalies_detected']}")
    print(f"  Detection rate: {analysis['detection_results']['detection_rate']:.2%}")
    print(f"  Top feature: {list(analysis['feature_analysis'].keys())[0]} ({list(analysis['feature_analysis'].values())[0]:.0%})")
    print(f"  Recommendations: {len(analysis['recommendations'])} suggestions")

    print("\n[ANOMALIES OUTPUT]")
    print(f"  Total anomalies: {len(outputs['anomalies'])}")
    for anom in outputs['anomalies'][:3]:
        print(f"    - {anom['id']}: {anom['type']} ({anom['severity']}) score={anom['anomaly_score']:.3f}")


def test_memory_leak():
    """Test Memory Leak chaos type"""
    print("\n" + "="*70)
    print("TEST 2: MEMORY LEAK @ 50% INTENSITY")
    print("="*70)

    config = {
        'execution_id': 'test_mem_001',
        'chaos_type': 'memory_leak',
        'intensity': 0.5,
        'duration': 60,
        'target_service': 'api-gateway',
        'advanced': {
            'ramp_up_time': 5,
            'ramp_down_time': 5
        }
    }

    gen = SimulationOutputGenerator(config)
    outputs = gen.generate_all()

    print("\n[METRICS OUTPUT]")
    print(f"  Total metrics: {len(outputs['metrics'])}")
    print(f"  Metric names: {[m['name'] for m in outputs['metrics']]}")
    for metric in outputs['metrics'][:2]:
        print(f"    - {metric['name']}: min={metric['min']:.1f}, max={metric['max']:.1f} {metric['unit']}")

    print("\n[ANALYSIS OUTPUT]")
    analysis = outputs['analysis']
    print(f"  Anomalies detected: {analysis['detection_results']['anomalies_detected']}")
    print(f"  Detection rate: {analysis['detection_results']['detection_rate']:.2%}")
    print(f"  Top feature: {list(analysis['feature_analysis'].keys())[0]} ({list(analysis['feature_analysis'].values())[0]:.0%})")

    print("\n[ANOMALIES OUTPUT]")
    print(f"  Total anomalies: {len(outputs['anomalies'])}")
    anomaly_types = set(a['type'] for a in outputs['anomalies'])
    print(f"  Anomaly types: {anomaly_types}")


def test_network_latency():
    """Test Network Latency chaos type"""
    print("\n" + "="*70)
    print("TEST 3: NETWORK LATENCY @ 80% INTENSITY")
    print("="*70)

    config = {
        'execution_id': 'test_net_001',
        'chaos_type': 'network_latency',
        'intensity': 0.8,
        'duration': 60,
        'target_service': 'api-gateway',
        'advanced': {
            'ramp_up_time': 5,
            'ramp_down_time': 5
        }
    }

    gen = SimulationOutputGenerator(config)
    outputs = gen.generate_all()

    print("\n[METRICS OUTPUT]")
    metrics_dict = {m['name']: m for m in outputs['metrics']}
    print(f"  Latency range: {metrics_dict['network_latency']['min']:.1f}ms - {metrics_dict['network_latency']['max']:.1f}ms")
    print(f"  Packet loss range: {metrics_dict['packet_loss']['min']:.1f}% - {metrics_dict['packet_loss']['max']:.1f}%")
    print(f"  Jitter range: {metrics_dict['jitter']['min']:.1f}ms - {metrics_dict['jitter']['max']:.1f}ms")

    print("\n[ANALYSIS OUTPUT]")
    analysis = outputs['analysis']
    print(f"  Anomalies detected: {analysis['detection_results']['anomalies_detected']}")
    print(f"  Model accuracy: {analysis['model_performance']['classifier_accuracy']:.2%}")

    print("\n[ANOMALIES OUTPUT]")
    print(f"  Total anomalies: {len(outputs['anomalies'])}")
    severity_dist = {}
    for anom in outputs['anomalies']:
        severity_dist[anom['severity']] = severity_dist.get(anom['severity'], 0) + 1
    print(f"  Severity distribution: {severity_dist}")


def test_high_error_rate():
    """Test High Error Rate chaos type"""
    print("\n" + "="*70)
    print("TEST 4: HIGH ERROR RATE @ 90% INTENSITY")
    print("="*70)

    config = {
        'execution_id': 'test_err_001',
        'chaos_type': 'high_error_rate',
        'intensity': 0.9,
        'duration': 60,
        'target_service': 'api-gateway',
        'advanced': {
            'ramp_up_time': 5,
            'ramp_down_time': 5
        }
    }

    gen = SimulationOutputGenerator(config)
    outputs = gen.generate_all()

    print("\n[METRICS OUTPUT]")
    metrics_dict = {m['name']: m for m in outputs['metrics']}
    print(f"  Error rate range: {metrics_dict['error_rate']['min']:.1f}% - {metrics_dict['error_rate']['max']:.1f}%")
    print(f"  Response time p99: {metrics_dict['response_time_p99']['mean']:.0f}ms (avg)")

    print("\n[ANALYSIS OUTPUT]")
    analysis = outputs['analysis']
    print(f"  Anomalies detected: {analysis['detection_results']['anomalies_detected']}")
    print(f"  Detection rate: {analysis['detection_results']['detection_rate']:.2%}")
    print(f"  Top feature: {list(analysis['feature_analysis'].keys())[0]} ({list(analysis['feature_analysis'].values())[0]:.0%})")
    print(f"  Recommendations: {[r['action'] for r in analysis['recommendations'][:2]]}")


def test_intensity_scaling():
    """Test that intensity scaling works correctly"""
    print("\n" + "="*70)
    print("TEST 5: INTENSITY SCALING VERIFICATION")
    print("="*70)

    intensities = [0.3, 0.6, 0.9]
    results = []

    for intensity in intensities:
        config = {
            'execution_id': f'test_scale_{intensity}',
            'chaos_type': 'cpu_spike',
            'intensity': intensity,
            'duration': 60,
            'target_service': 'api-gateway',
            'advanced': {'ramp_up_time': 5, 'ramp_down_time': 5}
        }

        gen = SimulationOutputGenerator(config)
        outputs = gen.generate_all()
        analysis = outputs['analysis']

        results.append({
            'intensity': intensity,
            'anomalies': analysis['detection_results']['anomalies_detected'],
            'detection_rate': analysis['detection_results']['detection_rate'],
            'mean_score': analysis['detection_results']['mean_anomaly_score']
        })

    print("\nIntensity Scaling Test:")
    print(f"{'Intensity':<12} {'Anomalies':<12} {'Detection Rate':<18} {'Mean Score':<12}")
    print("-" * 54)
    for r in results:
        print(f"{r['intensity']:.0%}          {r['anomalies']:<12} {r['detection_rate']:.2%}             {r['mean_score']:.3f}")

    # Verify scaling
    print("\nVerification:")
    print("  [OK] Anomalies increase with intensity" if results[0]['anomalies'] < results[2]['anomalies'] else "  [FAIL] Anomalies not scaling")
    print("  [OK] Detection rate increases with intensity" if results[0]['detection_rate'] < results[2]['detection_rate'] else "  [FAIL] Detection rate not scaling")


def main():
    """Run all tests"""
    print("\n")
    print("*" * 70)
    print("* SYNCHRONIZED SIMULATION OUTPUT SYSTEM - TEST SUITE")
    print("*" * 70)

    try:
        test_cpu_spike()
        test_memory_leak()
        test_network_latency()
        test_high_error_rate()
        test_intensity_scaling()

        print("\n" + "="*70)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("1. Start Flask app: python nexus_app.py")
        print("2. Open browser: http://localhost:5000/simulator")
        print("3. Configure chaos type, intensity, duration")
        print("4. Click 'Run Simulation'")
        print("5. Check Console, Metrics, Analysis, and Anomalies tabs")
        print("\nAll outputs should now be synchronized with your configuration!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
