#!/usr/bin/env python3
"""
Smart Service Topology Simulator
Simulates service discovery, dependencies, and inter-service communication
"""

import random
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ServiceTier(Enum):
    """Service tier/layer classification"""
    FRONTEND = "frontend"
    API_GATEWAY = "api_gateway"
    MICROSERVICE = "microservice"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    CACHE = "cache"
    EXTERNAL = "external"


class ServiceHealth(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Service:
    """Represents a microservice"""
    id: str
    name: str
    tier: ServiceTier
    host: str
    port: int
    version: str
    health: ServiceHealth
    latency_ms: float  # Average response time
    error_rate: float  # Percentage of failed requests
    throughput_rps: float  # Requests per second
    dependencies: List[str]  # List of service IDs this depends on
    tags: List[str]

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'tier': self.tier.value,
            'host': self.host,
            'port': self.port,
            'version': self.version,
            'health': self.health.value,
            'latency_ms': round(self.latency_ms, 2),
            'error_rate': round(self.error_rate, 2),
            'throughput_rps': round(self.throughput_rps, 2),
            'dependencies': self.dependencies,
            'tags': self.tags
        }


@dataclass
class ServiceDependency:
    """Represents communication between services"""
    source_id: str
    target_id: str
    latency_ms: float
    error_rate: float
    throughput_rps: float
    protocol: str
    data_size_mb: float

    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'latency_ms': round(self.latency_ms, 2),
            'error_rate': round(self.error_rate, 2),
            'throughput_rps': round(self.throughput_rps, 2),
            'protocol': self.protocol,
            'data_size_mb': round(self.data_size_mb, 2)
        }


class ServiceTopologySimulator:
    """Simulates a realistic microservice architecture"""

    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.dependencies: List[ServiceDependency] = []
        self._generate_topology()

    def _generate_topology(self):
        """Generate a realistic microservice topology"""

        # Frontend Services
        self.services['web-ui'] = Service(
            id='web-ui',
            name='Web UI',
            tier=ServiceTier.FRONTEND,
            host='frontend.internal',
            port=443,
            version='3.2.1',
            health=ServiceHealth.HEALTHY,
            latency_ms=45.2,
            error_rate=0.1,
            throughput_rps=2500.0,
            dependencies=['api-gateway'],
            tags=['frontend', 'react', 'cdn']
        )

        self.services['mobile-app'] = Service(
            id='mobile-app',
            name='Mobile App',
            tier=ServiceTier.FRONTEND,
            host='mobile.internal',
            port=443,
            version='2.8.3',
            health=ServiceHealth.HEALTHY,
            latency_ms=52.5,
            error_rate=0.15,
            throughput_rps=1800.0,
            dependencies=['api-gateway'],
            tags=['mobile', 'ios', 'android']
        )

        # API Gateway
        self.services['api-gateway'] = Service(
            id='api-gateway',
            name='API Gateway',
            tier=ServiceTier.API_GATEWAY,
            host='api.internal',
            port=8080,
            version='1.5.2',
            health=ServiceHealth.HEALTHY,
            latency_ms=28.3,
            error_rate=0.08,
            throughput_rps=4300.0,
            dependencies=['user-service', 'order-service', 'inventory-service', 'auth-service'],
            tags=['router', 'ratelimit', 'auth']
        )

        # Core Microservices
        self.services['user-service'] = Service(
            id='user-service',
            name='User Service',
            tier=ServiceTier.MICROSERVICE,
            host='users.internal',
            port=8081,
            version='2.1.0',
            health=ServiceHealth.HEALTHY,
            latency_ms=35.8,
            error_rate=0.05,
            throughput_rps=1200.0,
            dependencies=['user-db', 'cache-service', 'auth-service'],
            tags=['identity', 'profiles', 'crud']
        )

        self.services['order-service'] = Service(
            id='order-service',
            name='Order Service',
            tier=ServiceTier.MICROSERVICE,
            host='orders.internal',
            port=8082,
            version='1.8.5',
            health=ServiceHealth.DEGRADED,
            latency_ms=125.4,
            error_rate=0.22,
            throughput_rps=800.0,
            dependencies=['order-db', 'inventory-service', 'payment-service', 'notification-queue'],
            tags=['commerce', 'transactions', 'stateful']
        )

        self.services['inventory-service'] = Service(
            id='inventory-service',
            name='Inventory Service',
            tier=ServiceTier.MICROSERVICE,
            host='inventory.internal',
            port=8083,
            version='1.3.2',
            health=ServiceHealth.HEALTHY,
            latency_ms=42.1,
            error_rate=0.08,
            throughput_rps=950.0,
            dependencies=['inventory-db', 'cache-service'],
            tags=['stock', 'warehouse', 'realtime']
        )

        self.services['payment-service'] = Service(
            id='payment-service',
            name='Payment Service',
            tier=ServiceTier.MICROSERVICE,
            host='payments.internal',
            port=8084,
            version='2.5.1',
            health=ServiceHealth.HEALTHY,
            latency_ms=185.3,
            error_rate=0.01,
            throughput_rps=500.0,
            dependencies=['payment-db', 'external-processor'],
            tags=['transactions', 'pci', 'secure']
        )

        self.services['auth-service'] = Service(
            id='auth-service',
            name='Auth Service',
            tier=ServiceTier.MICROSERVICE,
            host='auth.internal',
            port=8085,
            version='3.0.1',
            health=ServiceHealth.HEALTHY,
            latency_ms=22.5,
            error_rate=0.02,
            throughput_rps=5500.0,
            dependencies=['auth-db', 'cache-service'],
            tags=['security', 'jwt', 'oauth2']
        )

        self.services['notification-service'] = Service(
            id='notification-service',
            name='Notification Service',
            tier=ServiceTier.MICROSERVICE,
            host='notifications.internal',
            port=8086,
            version='1.2.0',
            health=ServiceHealth.HEALTHY,
            latency_ms=15.3,
            error_rate=0.03,
            throughput_rps=2000.0,
            dependencies=['notification-queue', 'user-db'],
            tags=['events', 'email', 'sms']
        )

        # Databases
        self.services['user-db'] = Service(
            id='user-db',
            name='User Database',
            tier=ServiceTier.DATABASE,
            host='db-primary.internal',
            port=5432,
            version='14.2',
            health=ServiceHealth.HEALTHY,
            latency_ms=8.2,
            error_rate=0.0,
            throughput_rps=3000.0,
            dependencies=[],
            tags=['postgres', 'primary', 'replication']
        )

        self.services['order-db'] = Service(
            id='order-db',
            name='Order Database',
            tier=ServiceTier.DATABASE,
            host='db-orders.internal',
            port=5432,
            version='14.2',
            health=ServiceHealth.CRITICAL,
            latency_ms=245.8,
            error_rate=0.15,
            throughput_rps=500.0,
            dependencies=[],
            tags=['postgres', 'primary', 'slow']
        )

        self.services['inventory-db'] = Service(
            id='inventory-db',
            name='Inventory Database',
            tier=ServiceTier.DATABASE,
            host='db-inventory.internal',
            port=5432,
            version='14.2',
            health=ServiceHealth.HEALTHY,
            latency_ms=12.3,
            error_rate=0.0,
            throughput_rps=1500.0,
            dependencies=[],
            tags=['postgres', 'primary']
        )

        self.services['payment-db'] = Service(
            id='payment-db',
            name='Payment Database',
            tier=ServiceTier.DATABASE,
            host='db-payments.internal',
            port=5432,
            version='14.2',
            health=ServiceHealth.HEALTHY,
            latency_ms=5.8,
            error_rate=0.0,
            throughput_rps=400.0,
            dependencies=[],
            tags=['postgres', 'encrypted', 'pci']
        )

        self.services['auth-db'] = Service(
            id='auth-db',
            name='Auth Database',
            tier=ServiceTier.DATABASE,
            host='db-auth.internal',
            port=5432,
            version='14.2',
            health=ServiceHealth.HEALTHY,
            latency_ms=3.2,
            error_rate=0.0,
            throughput_rps=4500.0,
            dependencies=[],
            tags=['postgres', 'cache', 'sessions']
        )

        # Cache Layer
        self.services['cache-service'] = Service(
            id='cache-service',
            name='Redis Cache',
            tier=ServiceTier.CACHE,
            host='cache.internal',
            port=6379,
            version='7.0.1',
            health=ServiceHealth.HEALTHY,
            latency_ms=2.1,
            error_rate=0.01,
            throughput_rps=8000.0,
            dependencies=[],
            tags=['redis', 'distributed', 'cluster']
        )

        # Message Queues
        self.services['notification-queue'] = Service(
            id='notification-queue',
            name='Notification Queue',
            tier=ServiceTier.MESSAGE_QUEUE,
            host='queue.internal',
            port=5672,
            version='9.2.0',
            health=ServiceHealth.HEALTHY,
            latency_ms=5.4,
            error_rate=0.01,
            throughput_rps=3000.0,
            dependencies=[],
            tags=['rabbitmq', 'events', 'async']
        )

        # External Services
        self.services['external-processor'] = Service(
            id='external-processor',
            name='Payment Processor',
            tier=ServiceTier.EXTERNAL,
            host='api.stripe.com',
            port=443,
            version='2023-08-01',
            health=ServiceHealth.HEALTHY,
            latency_ms=250.5,
            error_rate=0.005,
            throughput_rps=500.0,
            dependencies=[],
            tags=['stripe', 'external', 'third-party']
        )

        # Generate dependencies
        self._generate_dependencies()

    def _generate_dependencies(self):
        """Generate inter-service communication patterns"""

        # Define dependency relationships
        dependency_pairs = [
            ('web-ui', 'api-gateway'),
            ('mobile-app', 'api-gateway'),
            ('api-gateway', 'user-service'),
            ('api-gateway', 'order-service'),
            ('api-gateway', 'inventory-service'),
            ('api-gateway', 'auth-service'),
            ('user-service', 'user-db'),
            ('user-service', 'cache-service'),
            ('user-service', 'auth-service'),
            ('order-service', 'order-db'),
            ('order-service', 'inventory-service'),
            ('order-service', 'payment-service'),
            ('order-service', 'notification-queue'),
            ('inventory-service', 'inventory-db'),
            ('inventory-service', 'cache-service'),
            ('payment-service', 'payment-db'),
            ('payment-service', 'external-processor'),
            ('auth-service', 'auth-db'),
            ('auth-service', 'cache-service'),
            ('notification-service', 'notification-queue'),
            ('notification-service', 'user-db'),
        ]

        for source_id, target_id in dependency_pairs:
            if source_id in self.services and target_id in self.services:
                source = self.services[source_id]
                target = self.services[target_id]

                # Calculate realistic latency based on tier
                base_latency = target.latency_ms
                if source.tier == ServiceTier.FRONTEND:
                    base_latency += random.uniform(50, 100)
                elif source.tier == ServiceTier.API_GATEWAY:
                    base_latency += random.uniform(10, 30)

                # Add some randomness
                latency = base_latency * random.uniform(0.8, 1.2)

                # Error rate correlation
                error_rate = (source.error_rate + target.error_rate) / 2
                error_rate *= random.uniform(0.5, 1.5)

                # Throughput based on calling pattern
                throughput = min(source.throughput_rps, target.throughput_rps) * random.uniform(0.3, 0.8)

                # Determine protocol
                if target.tier == ServiceTier.DATABASE:
                    protocol = 'JDBC'
                elif target.tier == ServiceTier.CACHE:
                    protocol = 'Redis'
                elif target.tier == ServiceTier.MESSAGE_QUEUE:
                    protocol = 'AMQP'
                elif target.tier == ServiceTier.EXTERNAL:
                    protocol = 'HTTPS'
                else:
                    protocol = 'HTTP/REST'

                self.dependencies.append(ServiceDependency(
                    source_id=source_id,
                    target_id=target_id,
                    latency_ms=latency,
                    error_rate=min(error_rate, 0.5),  # Cap at 50%
                    throughput_rps=throughput,
                    protocol=protocol,
                    data_size_mb=random.uniform(0.001, 5.0)
                ))

    def get_services(self) -> List[Dict]:
        """Get all services"""
        return [service.to_dict() for service in self.services.values()]

    def get_dependencies(self) -> List[Dict]:
        """Get all service dependencies"""
        return [dep.to_dict() for dep in self.dependencies]

    def get_service(self, service_id: str) -> Dict:
        """Get a specific service"""
        if service_id in self.services:
            return self.services[service_id].to_dict()
        return None

    def get_topology_summary(self) -> Dict:
        """Get topology summary statistics"""
        services = list(self.services.values())

        return {
            'total_services': len(services),
            'services_by_tier': {
                tier.value: len([s for s in services if s.tier == tier])
                for tier in ServiceTier
            },
            'health_distribution': {
                'healthy': len([s for s in services if s.health == ServiceHealth.HEALTHY]),
                'degraded': len([s for s in services if s.health == ServiceHealth.DEGRADED]),
                'critical': len([s for s in services if s.health == ServiceHealth.CRITICAL]),
                'unknown': len([s for s in services if s.health == ServiceHealth.UNKNOWN])
            },
            'avg_latency_ms': round(sum(s.latency_ms for s in services) / len(services), 2),
            'avg_error_rate': round(sum(s.error_rate for s in services) / len(services), 2),
            'total_throughput_rps': round(sum(s.throughput_rps for s in services), 2),
            'total_dependencies': len(self.dependencies),
            'timestamp': datetime.utcnow().isoformat()
        }


# Global instance
_topology_simulator = None


def get_topology_simulator() -> ServiceTopologySimulator:
    """Get or create the topology simulator"""
    global _topology_simulator
    if _topology_simulator is None:
        _topology_simulator = ServiceTopologySimulator()
    return _topology_simulator
