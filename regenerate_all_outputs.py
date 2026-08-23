#!/usr/bin/env python3
"""
Regenerate all AIOps MVP outputs and visualizations.

This script:
1. Runs the complete chaos simulation
2. Detects anomalies
3. Classifies incidents
4. Generates all visualizations
5. Saves results to data/processed/

Usage:
    python regenerate_all_outputs.py
    python regenerate_all_outputs.py --duration 600 --services SERVICE_A SERVICE_B
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chaos_simulator import ChaosSimulator


def main():
    """Main regeneration workflow."""
    parser = argparse.ArgumentParser(
        description='Regenerate all AIOps MVP outputs and visualizations'
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
        '--noise',
        type=float,
        default=0.15,
        help='Noise level (default: 0.15)'
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔧 AIOps MVP - Output Regeneration")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {args.duration} seconds")
    print(f"Services: {', '.join(args.services)}")
    print(f"Noise level: {args.noise}")
    print("="*80 + "\n")

    try:
        # Ensure output directory exists
        output_dir = 'data/processed'
        os.makedirs(output_dir, exist_ok=True)

        # Initialize simulator
        print("📊 Initializing chaos simulator...")
        simulator = ChaosSimulator(
            base_metrics=60,
            noise_level=args.noise,
            services=args.services
        )

        # Run complete simulation
        print("🔥 Running complete chaos simulation...")
        metrics_data, df_faults = simulator.simulate(
            duration=args.duration,
            services=args.services
        )
        print(f"   ✓ Generated {len(df_faults)} fault events")

        # Detect anomalies
        print("🔍 Detecting anomalies...")
        df_anomalies = simulator.detect_anomalies(df_faults)
        print(f"   ✓ Detected {len(df_anomalies)} anomalies")

        # Classify incidents
        print("📋 Classifying incidents...")
        df_incidents = simulator.classify_incidents(df_anomalies)
        print(f"   ✓ Classified {len(df_incidents)} incidents")

        # Detect correlations
        print("🔗 Analyzing correlations...")
        correlations = simulator.detect_correlations(df_faults)
        print(f"   ✓ Found {len(correlations)} correlated events")

        # Save results
        print("💾 Saving results...")
        simulator.save_results(output_dir)
        print(f"   ✓ Results saved to {output_dir}/")

        # Generate summary
        print("\n" + "="*80)
        print("✅ REGENERATION COMPLETE")
        print("="*80)
        print(f"\nGenerated files:")
        print(f"  • {output_dir}/chaos_simulation.png")
        print(f"  • {output_dir}/dos_simulation_analysis.png")
        print(f"  • {output_dir}/threshold_calibration.png (if validation data available)")
        print(f"\nStatistics:")
        print(f"  • Total faults injected: {len(df_faults)}")
        print(f"  • Anomalies detected: {len(df_anomalies)}")
        print(f"  • Incidents classified: {len(df_incidents)}")
        print(f"  • Detection rate: {len(df_anomalies) / max(len(df_faults), 1) * 100:.1f}%")
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
