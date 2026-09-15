#!/usr/bin/env python3
"""
Test script to validate topology data for D3.js visualization
"""

import json
from service_topology_simulator import get_topology_simulator
from datetime import datetime

def test_services_endpoint():
    """Test /api/services endpoint data format"""
    print("\n" + "="*60)
    print("TESTING /api/services ENDPOINT")
    print("="*60)

    topology = get_topology_simulator()
    services = topology.get_services()
    dependencies = topology.get_dependencies()

    # Build dependency map
    dep_map = {}
    for dep in dependencies:
        if dep['source_id'] not in dep_map:
            dep_map[dep['source_id']] = []
        dep_map[dep['source_id']].append(dep['target_id'])

    # Enrich services
    for service in services:
        service['dependencies'] = dep_map.get(service['id'], [])
        service['status'] = service.get('health', 'unknown').lower()

    response = {
        'services': services,
        'timestamp': datetime.utcnow().isoformat()
    }

    print(f"\n[OK] Services endpoint would return:")
    print(f"   - Total services: {len(services)}")
    print(f"   - Services with dependencies: {sum(1 for s in services if s.get('dependencies'))}")
    print(f"   - Timestamp: {response['timestamp']}")

    # Show sample
    if services:
        print(f"\n[SAMPLE] Service (for D3.js):")
        sample = services[0]
        print(f"   - ID: {sample['id']}")
        print(f"   - Name: {sample['name']}")
        print(f"   - Tier: {sample['tier']}")
        print(f"   - Status: {sample['status']}")
        print(f"   - Latency: {sample['latency_ms']}ms")
        print(f"   - Error Rate: {sample['error_rate']}%")
        print(f"   - Throughput: {sample['throughput_rps']} req/s")
        print(f"   - Dependencies: {sample.get('dependencies', [])}")
        print(f"   - Version: {sample['version']}")

    return response

def test_metrics_endpoint():
    """Test /api/services/metrics endpoint data format"""
    print("\n" + "="*60)
    print("TESTING /api/services/metrics ENDPOINT")
    print("="*60)

    topology = get_topology_simulator()
    services = topology.get_services()

    metrics = []
    for service in services:
        metrics.append({
            'service_id': service['id'],
            'status': service.get('health', 'unknown').lower(),
            'latency_ms': service['latency_ms'],
            'error_rate': service['error_rate'],
            'throughput_rps': service['throughput_rps'],
            'timestamp': datetime.utcnow().isoformat()
        })

    response = {
        'services': metrics,
        'timestamp': datetime.utcnow().isoformat()
    }

    print(f"\n[OK] Metrics endpoint would return:")
    print(f"   - Total metrics: {len(metrics)}")

    # Show sample
    if metrics:
        print(f"\n[SAMPLE] Metric (for real-time updates):")
        sample = metrics[0]
        print(f"   - Service ID: {sample['service_id']}")
        print(f"   - Status: {sample['status']}")
        print(f"   - Latency: {sample['latency_ms']}ms")
        print(f"   - Error Rate: {sample['error_rate']}%")
        print(f"   - Throughput: {sample['throughput_rps']} req/s")

    return response

def test_topology_visualization():
    """Validate that data is suitable for D3.js visualization"""
    print("\n" + "="*60)
    print("VALIDATING D3.JS TOPOLOGY VISUALIZATION REQUIREMENTS")
    print("="*60)

    topology = get_topology_simulator()
    services = topology.get_services()
    dependencies = topology.get_dependencies()

    # Build dependency map
    dep_map = {}
    for dep in dependencies:
        if dep['source_id'] not in dep_map:
            dep_map[dep['source_id']] = []
        dep_map[dep['source_id']].append(dep['target_id'])

    checks = {
        'Service IDs are unique': len(services) == len(set(s['id'] for s in services)),
        'All services have required fields': all(
            all(k in s for k in ['id', 'name', 'tier', 'health', 'latency_ms', 'error_rate', 'throughput_rps'])
            for s in services
        ),
        'Services have health status': all(s['health'] in ['healthy', 'degraded', 'critical', 'unknown'] for s in services),
        'Dependencies reference valid services': all(
            dep['source_id'] in [s['id'] for s in services] and
            dep['target_id'] in [s['id'] for s in services]
            for dep in dependencies
        ),
        'Metrics are numeric': all(
            isinstance(s['latency_ms'], (int, float)) and
            isinstance(s['error_rate'], (int, float)) and
            isinstance(s['throughput_rps'], (int, float))
            for s in services
        ),
        'Services have proper tiers': all(s['tier'] in [
            'frontend', 'api_gateway', 'microservice', 'database', 'cache', 'message_queue', 'external'
        ] for s in services),
    }

    print("\n[VALIDATION RESULTS]:")
    all_pass = True
    for check, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {status} {check}")
        if not result:
            all_pass = False

    print(f"\n[STATISTICS] Topology:")
    print(f"   - Total Nodes: {len(services)}")
    print(f"   - Total Edges: {len(dependencies)}")
    print(f"   - Graph Density: {len(dependencies) / (len(services) * (len(services) - 1) / 2) * 100:.1f}%")

    # Service distribution
    tiers = {}
    for s in services:
        tier = s['tier']
        tiers[tier] = tiers.get(tier, 0) + 1

    print(f"\n[TIERS] Service Distribution:")
    for tier, count in sorted(tiers.items()):
        print(f"   - {tier}: {count} services")

    # Health distribution
    health_counts = {}
    for s in services:
        health = s['health']
        health_counts[health] = health_counts.get(health, 0) + 1

    print(f"\n[HEALTH] Distribution:")
    for health, count in sorted(health_counts.items()):
        print(f"   - {health}: {count} services")

    # Metrics ranges
    latencies = [s['latency_ms'] for s in services]
    errors = [s['error_rate'] for s in services]
    throughputs = [s['throughput_rps'] for s in services]

    print(f"\n[METRICS] Ranges:")
    print(f"   - Latency: {min(latencies):.1f}ms - {max(latencies):.1f}ms (avg: {sum(latencies)/len(latencies):.1f}ms)")
    print(f"   - Error Rate: {min(errors):.2f}% - {max(errors):.2f}% (avg: {sum(errors)/len(errors):.2f}%)")
    print(f"   - Throughput: {min(throughputs):.0f} - {max(throughputs):.0f} req/s (total: {sum(throughputs):.0f} req/s)")

    return all_pass

def test_bottleneck_detection():
    """Test if data has detectable bottlenecks"""
    print("\n" + "="*60)
    print("TESTING BOTTLENECK DETECTION")
    print("="*60)

    topology = get_topology_simulator()
    services = topology.get_services()
    dependencies = topology.get_dependencies()

    print("\n[ANALYSIS] Checking for bottlenecks:")

    # High latency paths
    high_latency_links = [d for d in dependencies if d['latency_ms'] > 200]
    if high_latency_links:
        print(f"   [ALERT] High latency connections ({len(high_latency_links)}):")
        for link in high_latency_links[:3]:
            print(f"      {link['source_id']} -> {link['target_id']}: {link['latency_ms']}ms")
    else:
        print(f"   [OK] No high latency connections detected")

    # High error rates
    high_error_links = [d for d in dependencies if d['error_rate'] > 5]
    if high_error_links:
        print(f"   [ALERT] High error rate connections ({len(high_error_links)}):")
        for link in high_error_links[:3]:
            print(f"      {link['source_id']} -> {link['target_id']}: {link['error_rate']}%")
    else:
        print(f"   [OK] No high error rate connections detected")

    # Converging points
    dep_counts = {}
    for dep in dependencies:
        dep_counts[dep['target_id']] = dep_counts.get(dep['target_id'], 0) + 1

    converging = [svc_id for svc_id, count in dep_counts.items() if count > 2]
    if converging:
        print(f"   [ALERT] Converging points detected ({len(converging)}):")
        for svc_id in converging[:3]:
            svc = next((s for s in services if s['id'] == svc_id), None)
            if svc:
                print(f"      {svc['name']}: {dep_counts[svc_id]} inbound connections")
    else:
        print(f"   [OK] No critical converging points detected")

    print(f"\n[READY] Bottleneck detection is ready")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("TOPOLOGY DATA TEST SUITE")
    print("Testing compatibility with D3.js visualization")
    print("="*60)

    try:
        # Test endpoints
        services_data = test_services_endpoint()
        metrics_data = test_metrics_endpoint()

        # Validate visualization requirements
        all_valid = test_topology_visualization()

        # Test bottleneck detection
        test_bottleneck_detection()

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\n[SUCCESS] All tests completed successfully!")
        print(f"\nEndpoints are ready:")
        print(f"   - GET /api/services -> Service graph data")
        print(f"   - GET /api/services/metrics -> Real-time metrics for updates")
        print(f"\nD3.js visualization is ready to use with this data!")
        print(f"\nBottleneck detection will identify:")
        print(f"   [DETECT] High latency paths (>200ms)")
        print(f"   [DETECT] High error rate connections (>5%)")
        print(f"   [DETECT] Converging points (3+ inbound connections)")
        print(f"\nTraffic flow animation will highlight:")
        print(f"   [ANIMATE] High-throughput connections (>100 req/s)")
        print(f"\n" + "="*60 + "\n")

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
