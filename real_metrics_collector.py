"""
Real Metrics Collector
Gathers system metrics from psutil, Windows Performance Monitor, and application sources
Provides unified interface for hybrid metrics simulator
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Optional
import traceback

try:
    import win32com.client
    PERFMON_AVAILABLE = True
except ImportError:
    PERFMON_AVAILABLE = False
    print("⚠️  pywin32 not installed. Windows PerfMon metrics unavailable.")
    print("   Install with: pip install pywin32")


class RealMetricsCollector:
    """Collect real system metrics from multiple sources"""

    def __init__(self, use_perfmon=True):
        """Initialize collector

        Args:
            use_perfmon: Enable Windows Performance Monitor (requires pywin32)
        """
        self.use_perfmon = use_perfmon and PERFMON_AVAILABLE
        self.last_update = {}
        self.perfmon = None

        if self.use_perfmon:
            self._init_perfmon()

    def _init_perfmon(self):
        """Initialize Windows Performance Monitor"""
        try:
            self.perfmon = win32com.client.GetObject("winmgmts:")
            print("✅ Windows Performance Monitor initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize PerfMon: {e}")
            self.perfmon = None
            self.use_perfmon = False

    # ============================================================================
    # PSUTIL COLLECTORS (Always Available)
    # ============================================================================

    def get_psutil_metrics(self) -> Dict:
        """Collect metrics using psutil (cross-platform, always available)"""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            io = psutil.disk_io_counters()

            # Calculate rates (bytes per second)
            # Note: This is approximate - better with two samples
            net_in_rate = net.bytes_recv / 1024 / 1024  # MB
            net_out_rate = net.bytes_sent / 1024 / 1024  # MB
            disk_read_rate = io.read_bytes / 1024 / 1024  # MB
            disk_write_rate = io.write_bytes / 1024 / 1024  # MB

            metrics = {
                # CPU
                'cpu_usage': float(cpu),
                'cpu_cores': psutil.cpu_count(),

                # Memory
                'memory_usage': float(mem.percent),
                'memory_total_gb': float(mem.total / (1024**3)),
                'memory_used_gb': float(mem.used / (1024**3)),

                # Disk
                'disk_usage': float(disk.percent),
                'disk_read_rate': float(disk_read_rate),
                'disk_write_rate': float(disk_write_rate),

                # Network
                'network_in': float(net_in_rate),
                'network_out': float(net_out_rate),
                'network_errors': float(net.errin + net.errout),

                # Processes
                'process_count': len(psutil.pids()),
                'open_connections': len(psutil.net_connections()),

                # Timestamp
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'psutil'
            }

            return metrics

        except Exception as e:
            print(f"❌ Error collecting psutil metrics: {e}")
            traceback.print_exc()
            return {}

    # ============================================================================
    # WINDOWS PERFORMANCE MONITOR COLLECTORS
    # ============================================================================

    def get_perfmon_metrics(self) -> Dict:
        """Collect metrics from Windows Performance Monitor (more detailed)"""
        if not self.perfmon:
            return {}

        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'perfmon'
            }

            # ---- CPU Metrics ----
            try:
                cpu_query = self.perfmon.ExecQuery(
                    "Select * from Win32_PerfFormattedData_PerfOS_Processor "
                    "where Name='_Total'"
                )
                if cpu_query:
                    cpu = cpu_query[0]
                    metrics['cpu_usage'] = float(cpu.PercentProcessorTime)
                    metrics['cpu_user_time'] = float(cpu.PercentUserTime)
                    metrics['cpu_privileged_time'] = float(cpu.PercentPrivilegedTime)
            except Exception as e:
                print(f"⚠️  CPU PerfMon error: {e}")

            # ---- Memory Metrics ----
            try:
                mem_query = self.perfmon.ExecQuery(
                    "Select * from Win32_PerfFormattedData_PerfOS_Memory"
                )
                if mem_query:
                    mem = mem_query[0]
                    metrics['memory_usage'] = float(mem.PercentCommittedBytesInUse)
                    metrics['memory_page_faults'] = float(mem.PageFaultsPerSec)
                    metrics['memory_pages_per_sec'] = float(mem.PagesPerSec)
            except Exception as e:
                print(f"⚠️  Memory PerfMon error: {e}")

            # ---- Disk Metrics ----
            try:
                disk_query = self.perfmon.ExecQuery(
                    "Select * from Win32_PerfFormattedData_PerfLogicalDisk "
                    "where Name='C:'"
                )
                if disk_query:
                    disk = disk_query[0]
                    metrics['disk_usage'] = float(disk.PercentDiskTime)
                    metrics['disk_read_bytes_per_sec'] = float(disk.DiskReadBytesPerSec)
                    metrics['disk_write_bytes_per_sec'] = float(disk.DiskWriteBytesPerSec)
                    metrics['disk_read_rate'] = float(disk.DiskReadBytesPerSec) / (1024*1024)  # MB/s
                    metrics['disk_write_rate'] = float(disk.DiskWriteBytesPerSec) / (1024*1024)  # MB/s
            except Exception as e:
                print(f"⚠️  Disk PerfMon error: {e}")

            # ---- Network Metrics ----
            try:
                net_query = self.perfmon.ExecQuery(
                    "Select * from Win32_PerfFormattedData_Tcpip_NetworkInterface"
                )
                if net_query:
                    total_in = 0
                    total_out = 0
                    for nic in net_query:
                        total_in += float(nic.BytesReceivedPerSec)
                        total_out += float(nic.BytesSentPerSec)

                    metrics['network_in'] = total_in / (1024*1024)  # MB/s
                    metrics['network_out'] = total_out / (1024*1024)  # MB/s
            except Exception as e:
                print(f"⚠️  Network PerfMon error: {e}")

            return metrics

        except Exception as e:
            print(f"❌ Error collecting PerfMon metrics: {e}")
            traceback.print_exc()
            return {}

    # ============================================================================
    # HYBRID COLLECTION (Best of both sources)
    # ============================================================================

    def get_hybrid_metrics(self) -> Dict:
        """Get metrics from best available source(s)

        Priority:
        1. Use Windows PerfMon for detailed metrics (if available)
        2. Fall back to psutil for common metrics
        3. Combine both for complete picture
        """
        psutil_metrics = self.get_psutil_metrics()

        if self.use_perfmon:
            perfmon_metrics = self.get_perfmon_metrics()
            # Merge, preferring PerfMon values when available
            combined = {**psutil_metrics, **perfmon_metrics}
            combined['source'] = 'hybrid (perfmon + psutil)'
            return combined

        return psutil_metrics

    # ============================================================================
    # APPLICATION METRICS (Can be extended)
    # ============================================================================

    def get_application_metrics(self) -> Dict:
        """Collect application-specific metrics

        Can be extended to:
        - Parse application logs
        - Query application APIs
        - Connect to APM tools
        """
        try:
            # Default: simulate application metrics
            # These could come from actual app instrumentation
            return {
                'request_rate': 500,  # requests/sec
                'response_time_ms': 150,  # milliseconds
                'error_rate': 0.1,  # percentage
                'active_connections': 45,
                'db_connections': 20,
                'db_queries_per_sec': 250,
                'db_query_time_ms': 45,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'application'
            }
        except Exception as e:
            print(f"❌ Error collecting application metrics: {e}")
            return {}

    # ============================================================================
    # UNIFIED INTERFACE
    # ============================================================================

    def collect_all(self) -> Dict:
        """Collect all available metrics"""
        all_metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': self.get_hybrid_metrics(),
            'application': self.get_application_metrics(),
            'sources': []
        }

        if self.get_psutil_metrics():
            all_metrics['sources'].append('psutil')
        if self.use_perfmon and self.get_perfmon_metrics():
            all_metrics['sources'].append('perfmon')
        if self.get_application_metrics():
            all_metrics['sources'].append('application')

        return all_metrics

    def get_metrics_snapshot(self) -> Dict:
        """Get current snapshot for dashboard"""
        metrics = self.get_hybrid_metrics()
        metrics.update(self.get_application_metrics())
        return metrics

    def print_metrics(self):
        """Print current metrics (for debugging)"""
        metrics = self.get_metrics_snapshot()

        print("\n" + "="*60)
        print("📊 REAL SYSTEM METRICS")
        print("="*60)

        if 'cpu_usage' in metrics:
            print(f"CPU:              {metrics['cpu_usage']:.1f}%")
        if 'memory_usage' in metrics:
            print(f"Memory:           {metrics['memory_usage']:.1f}%")
        if 'disk_usage' in metrics:
            print(f"Disk:             {metrics['disk_usage']:.1f}%")
        if 'network_in' in metrics:
            print(f"Network In:       {metrics['network_in']:.1f} MB/s")
        if 'network_out' in metrics:
            print(f"Network Out:      {metrics['network_out']:.1f} MB/s")
        if 'process_count' in metrics:
            print(f"Processes:        {metrics['process_count']}")
        if 'request_rate' in metrics:
            print(f"Request Rate:     {metrics['request_rate']:.0f} req/sec")
        if 'error_rate' in metrics:
            print(f"Error Rate:       {metrics['error_rate']:.1f}%")

        if 'source' in metrics:
            print(f"\nSource:           {metrics['source']}")

        print("="*60 + "\n")


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == '__main__':
    # Test the collector
    print("🚀 Real Metrics Collector Test\n")

    collector = RealMetricsCollector(use_perfmon=True)

    print("📋 Available collectors:")
    print("  ✅ psutil (system metrics)")
    if PERFMON_AVAILABLE:
        print("  ✅ Windows Performance Monitor")
    else:
        print("  ⚠️  Windows Performance Monitor (not installed)")
    print()

    # Collect and display metrics
    for i in range(5):
        print(f"📊 Sample {i+1}/5:")
        collector.print_metrics()
        if i < 4:
            print("⏳ Waiting 2 seconds...\n")
            time.sleep(2)

    print("✅ Collection complete!")
    print("\n💡 Next: Integrate with HybridMetricsSimulator")
