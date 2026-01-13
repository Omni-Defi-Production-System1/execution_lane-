"""
Dashboard Server
HTTP server providing real-time dashboard interface
"""
import logging
import json
from typing import Dict
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/metrics':
            self.serve_metrics()
        elif self.path == '/api/opportunities':
            self.serve_opportunities()
        elif self.path == '/api/transactions':
            self.serve_transactions()
        else:
            self.send_error(404)
            
    def serve_dashboard(self):
        """Serve main dashboard HTML"""
        html = self.server.dashboard_html
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
        
    def serve_metrics(self):
        """Serve system metrics as JSON"""
        metrics = self.server.metrics_collector.get_system_metrics()
        self.send_json(metrics.__dict__)
        
    def serve_opportunities(self):
        """Serve recent opportunities as JSON"""
        opportunities = self.server.metrics_collector.get_recent_opportunities(50)
        self.send_json({'opportunities': opportunities})
        
    def serve_transactions(self):
        """Serve recent transactions as JSON"""
        transactions = self.server.metrics_collector.get_recent_transactions(50)
        self.send_json({'transactions': transactions})
        
    def send_json(self, data: Dict):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        
    def log_message(self, format, *args):
        """Override to use logger instead of stderr"""
        pass


class DashboardServer:
    """
    HTTP dashboard server for real-time monitoring
    
    Features:
    - Live metrics display
    - Opportunity feed
    - Transaction history
    - Performance charts
    """
    
    def __init__(self, metrics_collector, host: str = '0.0.0.0', port: int = 8080):
        """
        Initialize dashboard server
        
        Args:
            metrics_collector: MetricsCollector instance
            host: Server host
            port: Server port
        """
        self.metrics_collector = metrics_collector
        self.host = host
        self.port = port
        self.logger = logging.getLogger("DashboardServer")
        self.server = None
        self.server_thread = None
        self.dashboard_html = self._generate_dashboard_html()
        
    def start(self):
        """Start the dashboard server"""
        try:
            self.server = HTTPServer((self.host, self.port), DashboardHandler)
            self.server.metrics_collector = self.metrics_collector
            self.server.dashboard_html = self.dashboard_html
            
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.logger.info(f"Dashboard server started on http://{self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Error starting dashboard server: {e}")
            
    def stop(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            self.logger.info("Dashboard server stopped")
            
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>OmniArb Dashboard - Real-Time Monitoring</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #0a0e27;
            color: #e0e6ed;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #1a1f3a;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #2d3561;
        }
        .metric-card h3 {
            color: #8b9dc3;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-value.positive { color: #10b981; }
        .metric-value.negative { color: #ef4444; }
        .section {
            background: #1a1f3a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #2d3561;
        }
        .section h2 {
            margin-bottom: 15px;
            color: #667eea;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2d3561;
        }
        th {
            background: #0f1629;
            color: #8b9dc3;
            font-weight: 600;
        }
        .status-success { color: #10b981; }
        .status-failed { color: #ef4444; }
        .status-pending { color: #f59e0b; }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .refresh-btn:hover { background: #5568d3; }
        .update-time {
            text-align: center;
            color: #8b9dc3;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ OmniArb Real-Time Dashboard</h1>
        <p>Enterprise-Grade Arbitrage Monitoring System</p>
    </div>

    <div class="metrics-grid" id="metricsGrid">
        <!-- Metrics will be populated here -->
    </div>

    <div class="section">
        <h2>📊 Recent Opportunities</h2>
        <table id="opportunitiesTable">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Profit (USD)</th>
                    <th>Gas Cost</th>
                    <th>Net Profit</th>
                    <th>Hops</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <!-- Opportunities will be populated here -->
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>💰 Recent Transactions</h2>
        <table id="transactionsTable">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>TX Hash</th>
                    <th>Status</th>
                    <th>Profit</th>
                    <th>Gas Used</th>
                </tr>
            </thead>
            <tbody>
                <!-- Transactions will be populated here -->
            </tbody>
        </table>
    </div>

    <div style="text-align: center;">
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
    </div>
    
    <div class="update-time" id="updateTime"></div>

    <script>
        async function refreshData() {
            try {
                // Fetch metrics
                const metricsRes = await fetch('/api/metrics');
                const metrics = await metricsRes.json();
                updateMetrics(metrics);

                // Fetch opportunities
                const oppRes = await fetch('/api/opportunities');
                const oppData = await oppRes.json();
                updateOpportunities(oppData.opportunities);

                // Fetch transactions
                const txRes = await fetch('/api/transactions');
                const txData = await txRes.json();
                updateTransactions(txData.transactions);

                document.getElementById('updateTime').textContent = 
                    'Last updated: ' + new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        function updateMetrics(metrics) {
            const grid = document.getElementById('metricsGrid');
            grid.innerHTML = `
                <div class="metric-card">
                    <h3>Total Profit</h3>
                    <div class="metric-value positive">$${metrics.total_profit.toFixed(2)}</div>
                </div>
                <div class="metric-card">
                    <h3>Opportunities Detected</h3>
                    <div class="metric-value">${metrics.opportunities_detected}</div>
                </div>
                <div class="metric-card">
                    <h3>Success Rate</h3>
                    <div class="metric-value">${metrics.success_rate.toFixed(1)}%</div>
                </div>
                <div class="metric-card">
                    <h3>Avg Profit/Trade</h3>
                    <div class="metric-value positive">$${metrics.avg_profit_per_trade.toFixed(2)}</div>
                </div>
                <div class="metric-card">
                    <h3>Opportunities/Hour</h3>
                    <div class="metric-value">${metrics.opportunities_per_hour.toFixed(1)}</div>
                </div>
                <div class="metric-card">
                    <h3>Uptime</h3>
                    <div class="metric-value">${formatUptime(metrics.uptime_seconds)}</div>
                </div>
            `;
        }

        function updateOpportunities(opportunities) {
            const tbody = document.querySelector('#opportunitiesTable tbody');
            tbody.innerHTML = opportunities.slice(0, 20).map(opp => `
                <tr>
                    <td>${new Date(opp.timestamp * 1000).toLocaleTimeString()}</td>
                    <td>$${opp.profit_usd.toFixed(2)}</td>
                    <td>$${opp.gas_cost.toFixed(2)}</td>
                    <td class="${opp.net_profit > 0 ? 'status-success' : 'status-failed'}">
                        $${opp.net_profit.toFixed(2)}
                    </td>
                    <td>${opp.hops}</td>
                    <td class="${opp.executed ? 'status-success' : 'status-pending'}">
                        ${opp.executed ? '✓ Executed' : '○ Detected'}
                    </td>
                </tr>
            `).join('');
        }

        function updateTransactions(transactions) {
            const tbody = document.querySelector('#transactionsTable tbody');
            tbody.innerHTML = transactions.slice(0, 20).map(tx => `
                <tr>
                    <td>${new Date(tx.timestamp * 1000).toLocaleTimeString()}</td>
                    <td>${tx.tx_hash.substring(0, 16)}...</td>
                    <td class="status-${tx.status}">${tx.status.toUpperCase()}</td>
                    <td class="${tx.profit > 0 ? 'status-success' : 'status-failed'}">
                        $${tx.profit.toFixed(2)}
                    </td>
                    <td>${tx.gas_used.toLocaleString()}</td>
                </tr>
            `).join('');
        }

        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${mins}m`;
        }

        // Auto-refresh every 10 seconds
        setInterval(refreshData, 10000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
        """
