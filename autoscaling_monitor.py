import json
from datetime import datetime, timedelta
from collections import deque
import os

class AutoScalingMonitor:
    """Monitor and track auto-scaling events and metrics"""
    
    def __init__(self):
        self.min_instances = int(os.getenv("MIN_INSTANCES", 2))
        self.max_instances = int(os.getenv("MAX_INSTANCES", 10))
        self.current_instances = self.min_instances
        
        # Alert thresholds at 75% (not 90%)
        self.cpu_threshold_scale_up = 75
        self.memory_threshold_scale_up = 75
        self.cpu_threshold_scale_down = 40
        self.memory_threshold_scale_down = 40
        
        # History tracking (keep last 100 events)
        self.scaling_history = deque(maxlen=100)
        self.metrics_history = deque(maxlen=1000)
        self.alerts_triggered = deque(maxlen=100)
        
        # Load balancing info
        self.instances = [
            {"id": 1, "name": "app1", "port": 5001, "health": "healthy", "load": 0},
            {"id": 2, "name": "app2", "port": 5002, "health": "healthy", "load": 0}
        ]
        self.lb_algorithm = "least_conn"
        
    def record_metrics(self, cpu: float, memory: float, request_rate: float, error_rate: float):
        """Record system metrics"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "cpu": cpu,
            "memory": memory,
            "request_rate": request_rate,
            "error_rate": error_rate,
            "instances": self.current_instances
        }
        self.metrics_history.append(event)
        return event
    
    def check_and_scale(self, cpu: float, memory: float) -> dict:
        """Check if scaling is needed and return action"""
        action = "none"
        reason = ""
        
        # Check if scale up is needed
        if (cpu > self.cpu_threshold_scale_up or 
            memory > self.memory_threshold_scale_up) and \
           self.current_instances < self.max_instances:
            action = "scale_up"
            reason = f"High resource usage: CPU={cpu:.1f}%, Memory={memory:.1f}%"
            self.current_instances += 1
        
        # Check if scale down is possible
        elif (cpu < self.cpu_threshold_scale_down and 
              memory < self.memory_threshold_scale_down) and \
             self.current_instances > self.min_instances:
            action = "scale_down"
            reason = f"Low resource usage: CPU={cpu:.1f}%, Memory={memory:.1f}%"
            self.current_instances -= 1
        
        if action != "none":
            self.log_scaling_event(action, reason)
        
        return {
            "action": action,
            "reason": reason,
            "instances_before": self.current_instances if action == "none" else self.current_instances - (1 if action == "scale_up" else -1),
            "instances_after": self.current_instances,
            "timestamp": datetime.now().isoformat()
        }
    
    def log_scaling_event(self, action: str, reason: str):
        """Log scaling event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "reason": reason,
            "instances": self.current_instances
        }
        self.scaling_history.append(event)
    
    def trigger_alert(self, severity: str, metric: str, threshold: float, actual: float):
        """Trigger an alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "metric": metric,
            "threshold": threshold,
            "actual": actual,
            "message": f"{metric} exceeded threshold: {actual:.1f}% (limit: {threshold}%)"
        }
        self.alerts_triggered.append(alert)
        return alert
    
    def update_instance_load(self, instance_id: int, load: float):
        """Update instance load percentage"""
        for inst in self.instances:
            if inst["id"] == instance_id:
                inst["load"] = load
                break
    
    def get_scaling_status(self) -> dict:
        """Get current scaling status"""
        recent_events = list(self.scaling_history)[-10:] if self.scaling_history else []
        return {
            "current_instances": self.current_instances,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "thresholds": {
                "cpu_scale_up": self.cpu_threshold_scale_up,
                "cpu_scale_down": self.cpu_threshold_scale_down,
                "memory_scale_up": self.memory_threshold_scale_up,
                "memory_scale_down": self.memory_threshold_scale_down
            },
            "recent_events": recent_events
        }
    
    def get_load_balancing_status(self) -> dict:
        """Get load balancing status"""
        total_load = sum(inst["load"] for inst in self.instances)
        avg_load = total_load / len(self.instances) if self.instances else 0
        
        return {
            "algorithm": self.lb_algorithm,
            "instances": self.instances,
            "total_load": round(total_load, 2),
            "average_load": round(avg_load, 2),
            "max_load": max((inst["load"] for inst in self.instances), default=0),
            "min_load": min((inst["load"] for inst in self.instances), default=0)
        }
    
    def get_alerts_history(self, limit: int = 20) -> list:
        """Get recent alerts"""
        return list(self.alerts_triggered)[-limit:]
    
    def get_metrics_history(self, limit: int = 100) -> list:
        """Get recent metrics"""
        return list(self.metrics_history)[-limit:]
    
    def optimize_resources(self) -> dict:
        """Provide resource optimization recommendations"""
        recommendations = []
        recent_metrics = self.get_metrics_history(50)

        if not recent_metrics:
            return {
                "timestamp": datetime.now().isoformat(),
                "current_metrics": {
                    "cpu": 0,
                    "memory": 0,
                    "error_rate": 0
                },
                "recommendations": []
            }
        
        avg_cpu = sum(m["cpu"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["memory"] for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m["error_rate"] for m in recent_metrics) / len(recent_metrics)
        
        if avg_cpu > 70:
            recommendations.append({
                "type": "cpu_optimization",
                "severity": "high" if avg_cpu > 85 else "medium",
                "recommendation": "CPU usage is high. Consider: 1) Optimize expensive queries, 2) Cache frequently accessed data, 3) Review large data transfers",
                "metric": f"Current CPU: {avg_cpu:.1f}%"
            })
        
        if avg_memory > 70:
            recommendations.append({
                "type": "memory_optimization",
                "severity": "high" if avg_memory > 85 else "medium",
                "recommendation": "Memory usage is high. Consider: 1) Implement connection pooling, 2) Reduce in-memory cache size, 3) Implement garbage collection, 4) Review memory leaks",
                "metric": f"Current Memory: {avg_memory:.1f}%"
            })
        
        if avg_error_rate > 2:
            recommendations.append({
                "type": "reliability_optimization",
                "severity": "high" if avg_error_rate > 5 else "medium",
                "recommendation": f"Error rate is elevated at {avg_error_rate:.2f}%. Consider: 1) Add retry logic, 2) Implement circuit breakers, 3) Review timeout settings, 4) Check dependency health",
                "metric": f"Current error rate: {avg_error_rate:.2f}%"
            })
        
        if len(self.instances) < self.max_instances and avg_cpu > 60:
            recommendations.append({
                "type": "scaling_recommendation",
                "severity": "medium",
                "recommendation": f"Consider scaling up. Current load allows reaching up to {self.max_instances} instances for better distribution.",
                "metric": f"Current instances: {self.current_instances}/{self.max_instances}"
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": {
                "cpu": round(avg_cpu, 2),
                "memory": round(avg_memory, 2),
                "error_rate": round(avg_error_rate, 2)
            },
            "recommendations": recommendations
        }


# Global monitor instance
autoscaling_monitor = AutoScalingMonitor()
