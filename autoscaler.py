import docker
import time
import os
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("autoscaler")

class AutoScaler:
    def __init__(self):
        self.client = docker.from_env()
        self.min_instances = int(os.getenv("MIN_INSTANCES", 2))
        self.max_instances = int(os.getenv("MAX_INSTANCES", 10))
        self.cpu_threshold_up = int(os.getenv("CPU_THRESHOLD_UP", 80))
        self.cpu_threshold_down = int(os.getenv("CPU_THRESHOLD_DOWN", 40))
        self.memory_threshold_up = int(os.getenv("MEMORY_THRESHOLD_UP", 80))
        self.memory_threshold_down = int(os.getenv("MEMORY_THRESHOLD_DOWN", 40))
        self.scale_history = []
        
    def get_app_metrics(self):
        """Get metrics for all running app containers"""
        try:
            containers = self.client.containers.list(
                filters={"label": "com.docker.compose.service=app"},
                all=False
            )
            metrics = []
            for container in containers:
                stats = container.stats(stream=False)
                cpu_percent = self.calculate_cpu_percent(stats)
                memory_percent = self.calculate_memory_percent(stats)
                
                metrics.append({
                    "id": container.id[:12],
                    "name": container.name,
                    "cpu": cpu_percent,
                    "memory": memory_percent,
                    "timestamp": datetime.now().isoformat()
                })
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    def calculate_cpu_percent(self, stats):
        """Calculate CPU percentage from container stats"""
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                   stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                      stats["precpu_stats"]["system_cpu_usage"]
        cpu_percent = (cpu_delta / system_delta) * \
                     len(stats["cpu_stats"]["cpus"]) * 100.0
        return round(cpu_percent, 2)
    
    def calculate_memory_percent(self, stats):
        """Calculate memory percentage from container stats"""
        usage = stats["memory_stats"]["usage"]
        limit = stats["memory_stats"]["limit"]
        return round((usage / limit) * 100, 2)
    
    def get_current_instance_count(self):
        """Get number of running app instances"""
        try:
            containers = self.client.containers.list(
                filters={"label": "com.docker.compose.service=app"},
                all=False
            )
            return len(containers)
        except:
            return 0
    
    def should_scale_up(self, metrics):
        """Determine if we should scale up"""
        if not metrics:
            return False
        avg_cpu = sum(m["cpu"] for m in metrics) / len(metrics)
        avg_memory = sum(m["memory"] for m in metrics) / len(metrics)
        return (avg_cpu > self.cpu_threshold_up or 
                avg_memory > self.memory_threshold_up)
    
    def should_scale_down(self, metrics):
        """Determine if we should scale down"""
        if not metrics:
            return False
        avg_cpu = sum(m["cpu"] for m in metrics) / len(metrics)
        avg_memory = sum(m["memory"] for m in metrics) / len(metrics)
        return (avg_cpu < self.cpu_threshold_down and 
                avg_memory < self.memory_threshold_down)
    
    def log_scaling_event(self, action, reason, instance_count, metrics):
        """Log scaling decision"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "reason": reason,
            "instance_count": instance_count,
            "metrics": metrics
        }
        self.scale_history.append(event)
        logger.info(f"SCALING {action}: {reason}")
        logger.info(f"Instances: {instance_count}, Metrics: {metrics}")
    
    def run(self):
        """Main autoscaler loop"""
        logger.info(f"AutoScaler started: min={self.min_instances}, " +
                   f"max={self.max_instances}, cpu_up={self.cpu_threshold_up}%, " +
                   f"cpu_down={self.cpu_threshold_down}%, " +
                   f"mem_up={self.memory_threshold_up}%, " +
                   f"mem_down={self.memory_threshold_down}%")
        
        while True:
            try:
                metrics = self.get_app_metrics()
                current_count = self.get_current_instance_count()
                
                if metrics:
                    avg_cpu = sum(m["cpu"] for m in metrics) / len(metrics)
                    avg_mem = sum(m["memory"] for m in metrics) / len(metrics)
                    
                    logger.info(f"Current instances: {current_count}, " +
                               f"CPU: {avg_cpu:.1f}%, Memory: {avg_mem:.1f}%")
                    
                    # Note: Actual Docker scaling would require docker-compose CLI
                    # For now, we log the decision
                    if self.should_scale_up(metrics) and current_count < self.max_instances:
                        self.log_scaling_event("UP", 
                            f"High resource usage (CPU: {avg_cpu:.1f}%, Mem: {avg_mem:.1f}%)",
                            current_count, metrics)
                    
                    elif self.should_scale_down(metrics) and current_count > self.min_instances:
                        self.log_scaling_event("DOWN",
                            f"Low resource usage (CPU: {avg_cpu:.1f}%, Mem: {avg_mem:.1f}%)",
                            current_count, metrics)
                
                time.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                logger.error(f"Error in autoscaler loop: {e}")
                time.sleep(10)

if __name__ == "__main__":
    scaler = AutoScaler()
    scaler.run()
