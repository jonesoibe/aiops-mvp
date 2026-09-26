"""
Flask routes for Machine Analyzer
Integrates with Flask-SocketIO for real-time WebSocket updates
"""

from flask import Blueprint, jsonify, request, render_template, send_file
from flask_socketio import emit, disconnect
import threading
import time
import os
from machine_analyzer import analyzer
from analysis_visualizations import AnalysisVisualizations, EvaluationReports, IncidentLog
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from PIL import Image as PILImage
import base64

bp = Blueprint('machine_analyzer', __name__, url_prefix='/api/machine-analyzer')

# Store active streaming threads
streaming_threads = {}

# ==================== REST ENDPOINTS ====================

@bp.route('/machines', methods=['GET'])
def get_machines():
    """Get list of all available machines grouped by server"""
    try:
        grouped = analyzer.loader.get_machines()
        return jsonify({
            'machines': grouped,
            'total_machines': len(analyzer.loader.available_machines)
        })
    except Exception as e:
        print(f"[*] Error listing machines: {e}")
        return jsonify({'error': 'Failed to list machines', 'details': str(e)}), 500

@bp.route('/status', methods=['GET'])
def get_status():
    """Get current analyzer status"""
    try:
        return jsonify({
            'is_running': analyzer.is_running,
            'is_paused': analyzer.is_paused,
            'current_machine': analyzer.current_machine,
            'anomaly_score': analyzer.current_anomaly_score,
            'metrics_count': len(analyzer.metrics_buffer),
            'alerts_count': len(analyzer.alerts_buffer),
            'update_frequency': analyzer.update_frequency
        })
    except Exception as e:
        print(f"[*] Error reading analyzer status: {e}")
        return jsonify({'error': 'Failed to read status', 'details': str(e)}), 500

@bp.route('/config', methods=['GET', 'POST'])
def config():
    """Get/set analyzer configuration"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body required'}), 400

            if 'anomaly_threshold' in data:
                analyzer.anomaly_detector.anomaly_threshold = data['anomaly_threshold']

            if 'update_frequency' in data:
                analyzer.update_frequency = data['update_frequency']

            if 'baseline_window' in data:
                analyzer.baseline_calc.window_size = data['baseline_window']

            if 'feature_weights' in data:
                analyzer.anomaly_detector.weights = data['feature_weights']

            return jsonify({'success': True, 'message': 'Configuration updated'})

        else:  # GET
            return jsonify({
                'anomaly_threshold': analyzer.anomaly_detector.anomaly_threshold,
                'update_frequency': analyzer.update_frequency,
                'baseline_window': analyzer.baseline_calc.window_size,
                'feature_weights': analyzer.anomaly_detector.weights
            })
    except Exception as e:
        print(f"[*] Error in analyzer config: {e}")
        return jsonify({'error': 'Failed to get/set configuration', 'details': str(e)}), 500

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get current metrics buffer (60-second window)"""
    try:
        return jsonify({
            'metrics': list(analyzer.metrics_buffer),
            'count': len(analyzer.metrics_buffer),
            'anomaly_score': analyzer.current_anomaly_score
        })
    except Exception as e:
        print(f"[*] Error reading metrics buffer: {e}")
        return jsonify({'error': 'Failed to read metrics', 'details': str(e)}), 500

@bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alert history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        return jsonify({
            'alerts': list(analyzer.alerts_buffer)[-limit:],
            'count': len(analyzer.alerts_buffer)
        })
    except Exception as e:
        print(f"[*] Error reading alerts: {e}")
        return jsonify({'error': 'Failed to read alerts', 'details': str(e)}), 500

@bp.route('/start', methods=['POST'])
def start_analysis():
    """Start analyzing a machine"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        machine_name = data.get('machine')
        update_freq = data.get('update_frequency', 1.0)

        if not machine_name:
            return jsonify({'error': 'machine parameter required'}), 400

        analyzer.reset()

        if analyzer.start_simulation(machine_name, update_freq):
            # Start streaming in background thread
            thread = threading.Thread(target=_run_stream, daemon=True)
            thread.start()
            streaming_threads[machine_name] = thread

            return jsonify({
                'success': True,
                'message': f'Analysis started for {machine_name}',
                'machine': machine_name
            })
        else:
            return jsonify({'error': 'Failed to load machine'}), 400
    except Exception as e:
        print(f"[*] Error starting analysis: {e}")
        return jsonify({'error': 'Failed to start analysis', 'details': str(e)}), 500

@bp.route('/pause', methods=['POST'])
def pause_analysis():
    """Pause current analysis"""
    try:
        analyzer.pause()
        return jsonify({'success': True, 'message': 'Analysis paused'})
    except Exception as e:
        print(f"[*] Error pausing analysis: {e}")
        return jsonify({'error': 'Failed to pause analysis', 'details': str(e)}), 500

@bp.route('/resume', methods=['POST'])
def resume_analysis():
    """Resume paused analysis"""
    try:
        analyzer.resume()
        return jsonify({'success': True, 'message': 'Analysis resumed'})
    except Exception as e:
        print(f"[*] Error resuming analysis: {e}")
        return jsonify({'error': 'Failed to resume analysis', 'details': str(e)}), 500

@bp.route('/reset', methods=['POST'])
def reset_analysis():
    """Reset analysis"""
    try:
        analyzer.reset()
        return jsonify({'success': True, 'message': 'Analysis reset'})
    except Exception as e:
        print(f"[*] Error resetting analysis: {e}")
        return jsonify({'error': 'Failed to reset analysis', 'details': str(e)}), 500

# ==================== HELPER FUNCTIONS ====================

def _run_stream():
    """Run the analyzer stream (background thread -- has no HTTP response to
    return errors through, so a failure here must be logged rather than left
    to crash the thread silently)."""
    try:
        analyzer.run_stream()
    except Exception as e:
        print(f"[*] Error in analyzer stream thread: {e}")

# ==================== PAGE ROUTE ====================

@bp.route('/page', methods=['GET'])
def machine_analyzer_page():
    """Render the machine analyzer page"""
    try:
        return render_template('nexus/machine_analyzer.html')
    except Exception as e:
        print(f"[*] Error rendering machine analyzer page: {e}")
        return jsonify({'error': 'Failed to render page', 'details': str(e)}), 500

# ==================== ANALYSIS VISUALIZATIONS ====================

@bp.route('/analysis/visualizations', methods=['GET'])
def get_all_visualizations():
    """Get all analysis visualizations as base64-encoded images"""
    try:
        visualizations = AnalysisVisualizations.generate_all_visualizations()
        return jsonify({
            'success': True,
            'visualizations': visualizations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analysis/visualization/<viz_type>', methods=['GET'])
def get_visualization(viz_type):
    """Get a specific visualization"""
    try:
        method_name = viz_type.lower()
        if not hasattr(AnalysisVisualizations, method_name):
            return jsonify({'error': f'Unknown visualization: {viz_type}'}), 404

        method = getattr(AnalysisVisualizations, method_name)
        fig = method()
        image_base64 = AnalysisVisualizations.fig_to_base64(fig)

        return jsonify({
            'success': True,
            'type': viz_type,
            'image': image_base64
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== EVALUATION REPORTS ====================

@bp.route('/analysis/reports', methods=['GET'])
def get_all_reports():
    """Get all evaluation reports"""
    try:
        reports = EvaluationReports.get_all_reports()
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analysis/report/<report_type>', methods=['GET'])
def get_report(report_type):
    """Get a specific evaluation report"""
    try:
        reports = EvaluationReports.get_all_reports()
        if report_type not in reports:
            return jsonify({'error': f'Unknown report: {report_type}'}), 404

        return jsonify({
            'success': True,
            'type': report_type,
            'report': reports[report_type]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== INCIDENT LOGS ====================

@bp.route('/analysis/incident-log', methods=['GET'])
def get_incident_log():
    """Get detailed incident log"""
    try:
        incidents = IncidentLog.get_incident_log()
        return jsonify({
            'success': True,
            'incidents': incidents,
            'total_count': len(incidents)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analysis/incident-log/export-png', methods=['GET'])
def export_incident_dashboard_png():
    """Export an aesthetically-designed incident dashboard as a PNG image"""
    try:
        incidents = IncidentLog.get_incident_log()
        fig = IncidentLog.generate_incident_dashboard(incidents)
        png_bytes = IncidentLog.fig_to_png_bytes(fig)

        return send_file(
            BytesIO(png_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name=f'incident_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate incident dashboard: {str(e)}'
        }), 500

# ==================== PDF EXPORT ====================

@bp.route('/analysis/reports/export-pdf', methods=['GET'])
def export_reports_pdf():
    """Export all analysis reports as PDF"""
    try:
        # Create PDF in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00ff41'),
            spaceAfter=30,
            alignment=1  # Center
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#00d4ff'),
            spaceAfter=12,
            spaceBefore=12
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            leading=12
        )
        summary_intro_style = ParagraphStyle(
            'SummaryIntro',
            parent=styles['Normal'],
            fontSize=10.5,
            textColor=colors.HexColor('#333333'),
            spaceAfter=14,
            leading=15
        )

        # Build document content
        story = []

        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Machine Analyzer", title_style))
        story.append(Paragraph("Comprehensive Analysis Report", heading_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
        story.append(PageBreak())

        # Add all reports
        reports = EvaluationReports.get_all_reports()

        # ---- Executive Summary Page ----
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(
            "This report captures the Machine Analyzer's full evaluation cycle: chaos-engineering "
            "resilience testing, anomaly-classification model performance, DoS attack simulation, "
            "threshold calibration, and automated incident remediation. The table below summarizes "
            "the headline result from each of the {0} detailed reports that follow.".format(len(reports)),
            summary_intro_style
        ))
        story.append(Spacer(1, 0.15*inch))

        summary_highlights = {
            'chaos_simulation': '96.5% average detection rate across 6 chaos scenarios; 1.18s average response time',
            'classification_results': '94% overall accuracy, 0.95 F1-score, 0.96 ROC-AUC',
            'confusion_matrix_mvp': '96.9% accuracy for the real-time MVP anomaly detector',
            'confusion_matrix_supervised': '97.9% accuracy, a +1.0% improvement over the MVP model',
            'dos_simulation_analysis': '99.3% attack prevention rate across 5 DoS attack vectors',
            'threshold_calibration': 'Optimal threshold of 0.52 balancing 94.5% precision and 96.2% recall',
            'remediation_results': '98.6% remediation success rate, 87.6% automation rate, ~$21,000/month savings',
        }

        table_header_style = ParagraphStyle(
            'TableHeader', parent=styles['Normal'], fontSize=9.5,
            textColor=colors.white, fontName='Helvetica-Bold'
        )
        table_cell_style = ParagraphStyle(
            'TableCell', parent=styles['Normal'], fontSize=9, leading=12,
            textColor=colors.HexColor('#222222')
        )

        table_data = [[
            Paragraph('Report', table_header_style),
            Paragraph('Key Result', table_header_style)
        ]]
        for report_key, report_data in reports.items():
            highlight = summary_highlights.get(report_key, report_data.get('description', ''))
            table_data.append([
                Paragraph(report_data['title'], table_cell_style),
                Paragraph(highlight, table_cell_style)
            ])

        summary_table = Table(table_data, colWidths=[2.1*inch, 4.4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a0e27')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f7fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(PageBreak())

        # ---- Evaluation Visualizations (chart for each report above) ----
        try:
            visualizations = AnalysisVisualizations.generate_all_visualizations()
        except Exception as e:
            visualizations = {}
            print(f"[*] Failed to generate evaluation visualizations for PDF: {e}")

        if visualizations:
            story.append(Paragraph("Evaluation Visualizations", heading_style))
            story.append(Paragraph(
                "Supporting chart for each evaluation report above.",
                summary_intro_style
            ))
            story.append(PageBreak())

            viz_max_width = 7.0 * inch
            viz_max_height = 8.5 * inch

            for report_key, report_data in reports.items():
                b64_data = visualizations.get(report_key)
                if not b64_data:
                    continue

                img_buffer = BytesIO(base64.b64decode(b64_data))
                with PILImage.open(img_buffer) as pil_img:
                    img_w, img_h = pil_img.size
                img_buffer.seek(0)

                aspect = img_h / img_w
                display_w = viz_max_width
                display_h = display_w * aspect
                if display_h > viz_max_height:
                    display_h = viz_max_height
                    display_w = display_h / aspect

                story.append(Paragraph(report_data['title'], heading_style))
                story.append(Spacer(1, 0.1*inch))
                story.append(Image(img_buffer, width=display_w, height=display_h))
                story.append(PageBreak())

        # ---- Machine Analysis (real per-machine data, with charts) ----
        import json as _json

        per_machine_root = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'data', 'processed', 'per_machine'
        )
        # analyzer.current_machine is the raw SMD filename (e.g. "machine-2-3.txt"),
        # but per-machine report folders are named without the extension.
        machine_name = analyzer.current_machine
        if machine_name and machine_name.endswith('.txt'):
            machine_name = machine_name[:-4]
        if not machine_name or not os.path.isdir(os.path.join(per_machine_root, machine_name)):
            available = sorted(
                d for d in os.listdir(per_machine_root)
                if os.path.isdir(os.path.join(per_machine_root, d))
            ) if os.path.isdir(per_machine_root) else []
            machine_name = available[0] if available else None

        if machine_name:
            machine_dir = os.path.join(per_machine_root, machine_name)
            summary_path = os.path.join(machine_dir, 'summary.json')

            story.append(Paragraph(f"Machine Analysis: {machine_name}", heading_style))

            if os.path.exists(summary_path):
                with open(summary_path, 'r') as f:
                    summary = _json.load(f)

                severity_bits = ', '.join(
                    f"{count} {sev}" for sev, count in summary.get('incidents_by_severity', {}).items()
                ) or 'none'
                top_faults = summary.get('top_fault_types', [])[:3]

                story.append(Paragraph(
                    "Replayed {readings:,} real telemetry readings through the live anomaly-detection "
                    "pipeline (threshold {threshold}). Average anomaly score was {avg}, peaking at {mx}. "
                    "This triggered {incidents} incident(s) ({severity}) across {clusters} distinct burst(s)."
                    .format(
                        readings=summary.get('readings_analyzed', 0),
                        threshold=summary.get('anomaly_threshold', '-'),
                        avg=summary.get('avg_anomaly_score', '-'),
                        mx=summary.get('max_anomaly_score', '-'),
                        incidents=summary.get('total_incidents_triggered', 0),
                        severity=severity_bits,
                        clusters=summary.get('incident_clusters', 0),
                    ),
                    summary_intro_style
                ))

                if top_faults:
                    story.append(Paragraph("Top fault types:", body_style))
                    for fault in top_faults:
                        story.append(Paragraph(
                            "- {name} ({severity}, {count}x)".format(
                                name=fault.get('fault_name', 'Unknown'),
                                severity=fault.get('severity', 'unknown'),
                                count=fault.get('count', 0),
                            ),
                            body_style
                        ))
                story.append(Spacer(1, 0.2*inch))

            # Embed the machine's own charts
            chart_files = ['summary_dashboard.png', 'anomaly_timeline.png', 'threshold_sensitivity.png']
            max_width = 7.0 * inch
            max_height = 4.2 * inch

            for chart_file in chart_files:
                img_path = os.path.join(machine_dir, chart_file)
                if not os.path.exists(img_path):
                    continue

                with PILImage.open(img_path) as pil_img:
                    img_w, img_h = pil_img.size

                aspect = img_h / img_w
                display_w = max_width
                display_h = display_w * aspect
                if display_h > max_height:
                    display_h = max_height
                    display_w = display_h / aspect

                story.append(Image(img_path, width=display_w, height=display_h))
                story.append(Spacer(1, 0.15*inch))

        # Build PDF
        doc.build(story)

        # Reset buffer position
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'machine_analyzer_reports_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate PDF: {str(e)}'
        }), 500
