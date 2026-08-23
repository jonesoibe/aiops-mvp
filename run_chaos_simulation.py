#!/usr/bin/env python3
"""
Quick Chaos Engineering Simulation Script.

Injects controlled faults into simulated services and generates:
- Chaos simulation visualization
- DOS attack analysis
- Incident statistics

Usage:
    python run_chaos_simulation.py
    python run_chaos_simulation.py --duration 600 --correlation
    python run_chaos_simulation.py --services SERVICE_A SERVICE_B
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chaos_simulator import ChaosSimulator


def main():
    """Run chaos simulation."""
    parser = argparse.ArgumentParser(
        description='Run chaos engineering simulation with fault injection'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Simulation duration in seconds (default: 300)'
    )
    parser.add_argument(
        '--services',
        nargs='+',
        default=['SERVICE_A', 'SERVICE_B', 'SERVICE_C'],
        help='Services to simulate (default: SERVICE_A SERVICE_B SERVICE_C)'
    )
    parser.add_argument(
        '--correlation',
        action='store_true',
        help='Enable correlated fault injection'
    )
    parser.add_argument(
        '--noise',
        type=float,
        default=0.15,
        help='Noise level (default: 0.15)'
    )
    parser.add_argument(
        '--output',
        default='data/processed',
        help='Output directory (default: data/processed)'
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔥 Chaos Engineering Simulation")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {args.duration} seconds")
    print(f"Services: {', '.join(args.services)}")
    print(f"Correlation enabled: {args.correlation}")
    print(f"Noise level: {args.noise}")
    print("="*80 + "\n")

    try:
        # Create output directory
        os.makedirs(args.output, exist_ok=True)

        # Initialize simulator
        print("📊 Initializing simulator...")
        simulator = ChaosSimulator(
            base_metrics=60,
            noise_level=args.noise,
            services=args.services
        )

        # Run simulation
        print(f"🎯 Injecting faults into {len(args.services)} services...")
        metrics_data, df_faults = simulator.simulate(
            duration=args.duration,
            services=args.services,
            correlation=args.correlation
        )

        # Detect anomalies
        print("🔍 Detecting anomalies...")
        df_anomalies = simulator.detect_anomalies(df_faults)

        # Classify incidents
        print("📋 Classifying incidents...")
        df_incidents = simulator.classify_incidents(df_anomalies)

        # Detect correlations
        print("🔗 Analyzing correlations...")
        correlations = simulator.detect_correlations(df_faults)

        # Save visualizations
        print("📈 Generating visualizations...")
        simulator.save_results(args.output)

        # Generate statistics
        print("\n" + "="*80)
        print("📊 SIMULATION RESULTS")
        print("="*80)

        print(f"\nFault Injection:")
        print(f"  • Total faults injected: {len(df_faults)}")
        print(f"  • Services affected: {df_faults['service'].nunique() if len(df_faults) > 0 else 0}")
        print(f"  • Fault types: {df_faults['fault_type'].nunique() if len(df_faults) > 0 else 0}")

        print(f"\nAnomaly Detection:")
        print(f"  • Total anomalies detected: {len(df_anomalies)}")
        if len(df_faults) > 0:
            detection_rate = len(df_anomalies) / len(df_faults) * 100
            print(f"  • Detection rate: {detection_rate:.1f}%")

        print(f"\nIncident Classification:")
        print(f"  • Total incidents: {len(df_incidents)}")
        if len(df_incidents) > 0:
            by_type = df_incidents.groupby('incident_type').size()
            for incident_type, count in by_type.items():
                pct = count / len(df_incidents) * 100
                print(f"    - {incident_type}: {count} ({pct:.1f}%)")

        print(f"\nCorrelation Analysis:")
        print(f"  • Correlated event groups: {len(correlations)}")
        if len(correlations) > 0:
            avg_size = sum(len(group) for group in correlations) / len(correlations)
            print(f"  • Average group size: {avg_size:.1f} events")

        print(f"\nGenerated Files:")
        print(f"  • chaos_simulation.png - Fault timeline and anomalies")
        print(f"  • dos_simulation_analysis.png - Correlation heatmap and incidents")
        if len(df_anomalies) > 0:
            print(f"  • threshold_calibration.png - Detection threshold optimization")

        print(f"\nExecution:")
        print(f"  • Duration: {args.duration} seconds")
        print(f"  • End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  • Status: SUCCESS ✓")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
