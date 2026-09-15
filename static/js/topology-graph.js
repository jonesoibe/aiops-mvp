/**
 * Topology Graph Visualization
 * Interactive D3.js force-directed graph for service dependencies
 * Shows real-time metrics, traffic flow, and bottlenecks
 */

class TopologyGraph {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);

        // Configuration
        this.options = {
            width: window.innerWidth - 280, // Account for sidebar
            height: window.innerHeight - 150,
            nodeRadius: 40,
            linkDistance: 150,
            chargeStrength: -500,
            friction: 0.9,
            animationDuration: 300,
            metricsUpdateInterval: 5000,
            ...options
        };

        // Data
        this.nodes = [];
        this.links = [];
        this.services = {};
        this.metrics = {};
        this.selectedNode = null;

        // D3 objects
        this.svg = null;
        this.simulation = null;
        this.g = null;
        this.linkGroup = null;
        this.nodeGroup = null;
        this.labelGroup = null;

        // Real-time updates
        this.socket = null;
        this.metricsInterval = null;

        this.init();
    }

    /**
     * Initialize the graph
     */
    init() {
        // Create SVG
        this.svg = d3.select(`#${this.containerId}`)
            .append('svg')
            .attr('width', this.options.width)
            .attr('height', this.options.height)
            .attr('class', 'topology-svg');

        // Add background
        this.svg.append('rect')
            .attr('width', this.options.width)
            .attr('height', this.options.height)
            .attr('class', 'topology-background')
            .on('click', () => this.deselectNode());

        // Create main group
        this.g = this.svg.append('g')
            .attr('class', 'topology-group');

        // Add zoom behavior
        const zoom = d3.zoom()
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        this.svg.call(zoom);

        // Create layer groups
        this.linkGroup = this.g.append('g').attr('class', 'links');
        this.nodeGroup = this.g.append('g').attr('class', 'nodes');
        this.labelGroup = this.g.append('g').attr('class', 'labels');

        // Create force simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink()
                .id(d => d.id)
                .distance(this.options.linkDistance))
            .force('charge', d3.forceManyBody()
                .strength(this.options.chargeStrength))
            .force('center', d3.forceCenter(
                this.options.width / 2,
                this.options.height / 2))
            .force('collision', d3.forceCollide()
                .radius(d => this.options.nodeRadius + 10));

        // Handle window resize
        window.addEventListener('resize', () => this.resize());

        // Load data
        this.loadTopologyData();
    }

    /**
     * Load topology data from backend
     */
    async loadTopologyData() {
        try {
            const response = await fetch('/api/services');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.processServiceData(data);
            this.render();
            this.startRealTimeUpdates();
        } catch (error) {
            console.error('Error loading topology data:', error);
            this.showError('Failed to load topology data');
        }
    }

    /**
     * Process service data into graph format
     */
    processServiceData(data) {
        // Extract nodes
        const servicesList = data.services || [];
        this.nodes = servicesList.map(service => ({
            id: service.service_id,
            name: service.service_name,
            tier: service.tier || 'api',
            status: service.status || 'healthy',
            version: service.version || '1.0',
            replicas: service.replicas || 1,
            latency: service.latency_ms || 0,
            errorRate: service.error_rate || 0,
            throughput: service.throughput_rps || 0,
            cpu: service.cpu_usage || 0,
            memory: service.memory_usage || 0,
            connections: service.connection_count || 0
        }));

        // Extract links (dependencies)
        this.links = [];
        const linkSet = new Set();

        servicesList.forEach(service => {
            if (service.dependencies && Array.isArray(service.dependencies)) {
                service.dependencies.forEach(depId => {
                    const linkKey = `${service.service_id}-${depId}`;
                    if (!linkSet.has(linkKey)) {
                        this.links.push({
                            source: service.service_id,
                            target: depId,
                            protocol: service.protocol || 'http',
                            port: service.port || 80,
                            latency: service.latency_ms || 0,
                            errorRate: service.error_rate || 0,
                            throughput: service.throughput_rps || 0
                        });
                        linkSet.add(linkKey);
                    }
                });
            }
        });

        // Create services map for quick lookup
        this.services = {};
        this.nodes.forEach(node => {
            this.services[node.id] = node;
        });
    }

    /**
     * Render the graph
     */
    render() {
        // Bind data
        this.simulation.nodes(this.nodes);
        this.simulation.force('link').links(this.links);

        // Render links (connections)
        this.renderLinks();

        // Render nodes (services)
        this.renderNodes();

        // Render labels
        this.renderLabels();

        // Start simulation
        this.simulation.on('tick', () => this.tick());
    }

    /**
     * Render connection links
     */
    renderLinks() {
        const links = this.linkGroup.selectAll('line')
            .data(this.links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);

        links.exit().remove();

        links.enter()
            .append('line')
            .attr('class', d => {
                let className = 'topology-link';
                if (d.errorRate > 5) className += ' error';
                else if (d.errorRate > 1) className += ' warning';
                return className;
            })
            .attr('stroke-width', d => Math.max(2, d.throughput / 100))
            .merge(links)
            .attr('class', d => {
                let className = 'topology-link';
                if (d.errorRate > 5) className += ' error';
                else if (d.errorRate > 1) className += ' warning';
                return className;
            });
    }

    /**
     * Render service nodes
     */
    renderNodes() {
        const nodes = this.nodeGroup.selectAll('g.node')
            .data(this.nodes, d => d.id);

        // Remove exiting nodes
        nodes.exit().remove();

        // Create new nodes
        const nodeEnter = nodes.enter()
            .append('g')
            .attr('class', d => `node ${d.tier} ${d.status}`)
            .on('click', (event, d) => {
                event.stopPropagation();
                this.selectNode(d);
            })
            .on('mouseenter', (event, d) => this.showNodeTooltip(event, d))
            .on('mouseleave', () => this.hideTooltip())
            .call(d3.drag()
                .on('start', (event, d) => this.dragStarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragEnded(event, d)));

        // Add circle for node
        nodeEnter.append('circle')
            .attr('r', this.options.nodeRadius)
            .attr('class', 'node-circle');

        // Add status indicator (inner circle)
        nodeEnter.append('circle')
            .attr('r', this.options.nodeRadius * 0.6)
            .attr('class', d => `node-status ${d.status}`)
            .attr('fill', d => this.getStatusColor(d.status));

        // Add icon/label in center
        nodeEnter.append('text')
            .attr('class', 'node-icon')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'central')
            .attr('font-size', '20px')
            .text(d => this.getTierEmoji(d.tier));

        // Merge with existing
        const merged = nodeEnter.merge(nodes);

        // Update classes based on selection
        merged.attr('class', d => {
            let className = `node ${d.tier} ${d.status}`;
            if (this.selectedNode && this.selectedNode.id === d.id) {
                className += ' selected';
            }
            return className;
        });

        // Add pulse animation for unhealthy services
        merged.select('.node-status')
            .attr('class', d => {
                let className = `node-status ${d.status}`;
                if (d.status !== 'healthy') className += ' pulse';
                return className;
            });
    }

    /**
     * Render service labels
     */
    renderLabels() {
        const labels = this.labelGroup.selectAll('text.node-label')
            .data(this.nodes, d => d.id);

        labels.exit().remove();

        labels.enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', `${this.options.nodeRadius + 25}px`)
            .text(d => d.name)
            .merge(labels)
            .text(d => d.name);
    }

    /**
     * Update simulation tick
     */
    tick() {
        // Update link positions
        this.linkGroup.selectAll('line')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        // Update node positions
        this.nodeGroup.selectAll('g.node')
            .attr('transform', d => `translate(${d.x},${d.y})`);

        // Update label positions
        this.labelGroup.selectAll('text.node-label')
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }

    /**
     * Select a node and show details
     */
    selectNode(node) {
        this.selectedNode = node;

        // Update visual
        this.nodeGroup.selectAll('g.node')
            .attr('class', d => {
                let className = `node ${d.tier} ${d.status}`;
                if (d.id === node.id) className += ' selected';
                return className;
            });

        // Highlight connected nodes
        this.nodeGroup.selectAll('g.node')
            .attr('class', d => {
                let className = `node ${d.tier} ${d.status}`;
                if (d.id === node.id) className += ' selected';
                else if (this.isConnected(node, d)) className += ' connected';
                return className;
            });

        this.linkGroup.selectAll('line')
            .attr('class', d => {
                let className = 'topology-link';
                if ((d.source.id === node.id) || (d.target.id === node.id)) {
                    className += ' highlighted';
                }
                if (d.errorRate > 5) className += ' error';
                else if (d.errorRate > 1) className += ' warning';
                return className;
            });

        // Show details panel
        this.showDetailsPanel(node);
    }

    /**
     * Deselect node
     */
    deselectNode() {
        this.selectedNode = null;

        this.nodeGroup.selectAll('g.node')
            .attr('class', d => `node ${d.tier} ${d.status}`);

        this.linkGroup.selectAll('line')
            .attr('class', d => {
                let className = 'topology-link';
                if (d.errorRate > 5) className += ' error';
                else if (d.errorRate > 1) className += ' warning';
                return className;
            });

        this.hideDetailsPanel();
    }

    /**
     * Check if two nodes are connected
     */
    isConnected(a, b) {
        return this.links.some(link =>
            (link.source.id === a.id && link.target.id === b.id) ||
            (link.source.id === b.id && link.target.id === a.id)
        );
    }

    /**
     * Show node details panel
     */
    showDetailsPanel(node) {
        let panel = document.getElementById('topology-details-panel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'topology-details-panel';
            panel.className = 'topology-details-panel';
            document.querySelector('.topology-container').appendChild(panel);
        }

        // Get connected services
        const inbound = this.links
            .filter(l => l.target.id === node.id)
            .map(l => this.services[l.source.id]);

        const outbound = this.links
            .filter(l => l.source.id === node.id)
            .map(l => this.services[l.target.id]);

        // Build HTML
        const html = `
            <div class="details-header">
                <h3>${node.name}</h3>
                <button class="close-btn" onclick="document.getElementById('topology-details-panel').style.display='none'">✕</button>
            </div>
            <div class="details-content">
                <div class="metric-row">
                    <span class="metric-label">Status:</span>
                    <span class="status-badge ${node.status}">${node.status.toUpperCase()}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Tier:</span>
                    <span>${node.tier}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Version:</span>
                    <span>${node.version}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Replicas:</span>
                    <span>${node.replicas}</span>
                </div>

                <div class="metrics-section">
                    <h4>Performance Metrics</h4>
                    <div class="metric-row">
                        <span class="metric-label">Latency (P95):</span>
                        <span>${node.latency}ms</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Error Rate:</span>
                        <span class="error-rate ${node.errorRate > 5 ? 'critical' : node.errorRate > 1 ? 'warning' : ''}">${node.errorRate.toFixed(2)}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Throughput:</span>
                        <span>${node.throughput} req/s</span>
                    </div>
                </div>

                <div class="resources-section">
                    <h4>Resource Usage</h4>
                    <div class="metric-row">
                        <span class="metric-label">CPU:</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${node.cpu}%"></div>
                            <span class="progress-text">${node.cpu}%</span>
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Memory:</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${node.memory}%"></div>
                            <span class="progress-text">${node.memory}%</span>
                        </div>
                    </div>
                </div>

                ${inbound.length > 0 ? `
                    <div class="dependencies-section">
                        <h4>Inbound Dependencies (${inbound.length})</h4>
                        <div class="dependency-list">
                            ${inbound.map(dep => `
                                <div class="dependency-item">
                                    <span class="status-indicator ${dep.status}"></span>
                                    ${dep.name}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                ${outbound.length > 0 ? `
                    <div class="dependencies-section">
                        <h4>Outbound Dependencies (${outbound.length})</h4>
                        <div class="dependency-list">
                            ${outbound.map(dep => `
                                <div class="dependency-item">
                                    <span class="status-indicator ${dep.status}"></span>
                                    ${dep.name}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        panel.innerHTML = html;
        panel.style.display = 'block';
    }

    /**
     * Hide details panel
     */
    hideDetailsPanel() {
        const panel = document.getElementById('topology-details-panel');
        if (panel) panel.style.display = 'none';
    }

    /**
     * Show tooltip on node hover
     */
    showNodeTooltip(event, node) {
        const tooltip = document.getElementById('topology-tooltip') ||
            this.createTooltip();

        tooltip.innerHTML = `
            <strong>${node.name}</strong><br/>
            Status: <span class="status-badge ${node.status}">${node.status}</span><br/>
            Latency: ${node.latency}ms<br/>
            Error Rate: ${node.errorRate.toFixed(2)}%<br/>
            Throughput: ${node.throughput} req/s
        `;

        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY + 10) + 'px';
        tooltip.style.display = 'block';
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        const tooltip = document.getElementById('topology-tooltip');
        if (tooltip) tooltip.style.display = 'none';
    }

    /**
     * Create tooltip element
     */
    createTooltip() {
        const tooltip = document.createElement('div');
        tooltip.id = 'topology-tooltip';
        tooltip.className = 'topology-tooltip';
        document.body.appendChild(tooltip);
        return tooltip;
    }

    /**
     * Drag handlers
     */
    dragStarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragEnded(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    /**
     * Start real-time metric updates
     */
    startRealTimeUpdates() {
        // Poll for metrics every 5 seconds
        this.metricsInterval = setInterval(() => {
            this.updateMetrics();
        }, this.options.metricsUpdateInterval);

        // Also listen for WebSocket updates if available
        if (window.socket) {
            window.socket.on('service_metrics_update', (data) => {
                this.updateNodeMetrics(data);
            });
        }
    }

    /**
     * Update metrics from backend
     */
    async updateMetrics() {
        try {
            const response = await fetch('/api/services/metrics');
            if (!response.ok) return;

            const data = await response.json();
            data.services?.forEach(serviceMetrics => {
                this.updateNodeMetrics(serviceMetrics);
            });
        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    }

    /**
     * Update individual node metrics
     */
    updateNodeMetrics(metrics) {
        const node = this.services[metrics.service_id];
        if (!node) return;

        // Update metrics
        node.status = metrics.status || node.status;
        node.latency = metrics.latency_ms || node.latency;
        node.errorRate = metrics.error_rate || node.errorRate;
        node.throughput = metrics.throughput_rps || node.throughput;
        node.cpu = metrics.cpu_usage || node.cpu;
        node.memory = metrics.memory_usage || node.memory;
        node.connections = metrics.connection_count || node.connections;

        // Update visual
        this.nodeGroup.selectAll('g.node')
            .filter(d => d.id === metrics.service_id)
            .attr('class', d => {
                let className = `node ${d.tier} ${d.status}`;
                if (this.selectedNode && this.selectedNode.id === d.id) {
                    className += ' selected';
                }
                return className;
            })
            .select('.node-status')
            .attr('fill', this.getStatusColor(node.status));

        // Update links if this node is involved
        this.linkGroup.selectAll('line')
            .attr('class', d => {
                let className = 'topology-link';
                if ((d.source.id === metrics.service_id || d.target.id === metrics.service_id)) {
                    d.errorRate = metrics.error_rate || d.errorRate;
                    d.latency = metrics.latency_ms || d.latency;
                }
                if (d.errorRate > 5) className += ' error';
                else if (d.errorRate > 1) className += ' warning';
                return className;
            });

        // Update details panel if open
        if (this.selectedNode && this.selectedNode.id === metrics.service_id) {
            this.showDetailsPanel(node);
        }
    }

    /**
     * Get status color
     */
    getStatusColor(status) {
        const colors = {
            'healthy': '#6bffb8',
            'degraded': '#ffc247',
            'critical': '#ff4da6',
            'offline': '#6e7681'
        };
        return colors[status] || colors['healthy'];
    }

    /**
     * Get tier emoji
     */
    getTierEmoji(tier) {
        const emojis = {
            'frontend': '🌐',
            'api': '⚡',
            'database': '💾',
            'cache': '⚙️',
            'message-queue': '📨',
            'monitoring': '📊'
        };
        return emojis[tier] || '🔧';
    }

    /**
     * Show error message
     */
    showError(message) {
        const error = document.createElement('div');
        error.className = 'topology-error';
        error.textContent = message;
        this.container.appendChild(error);
    }

    /**
     * Handle window resize
     */
    resize() {
        this.options.width = window.innerWidth - 280;
        this.options.height = window.innerHeight - 150;

        this.svg
            .attr('width', this.options.width)
            .attr('height', this.options.height);

        this.simulation.force('center',
            d3.forceCenter(this.options.width / 2, this.options.height / 2));
        this.simulation.alpha(0.3).restart();
    }

    /**
     * Cleanup
     */
    destroy() {
        if (this.metricsInterval) clearInterval(this.metricsInterval);
        if (this.simulation) this.simulation.stop();
        if (this.svg) this.svg.remove();
    }
}

// Export for use
window.TopologyGraph = TopologyGraph;
