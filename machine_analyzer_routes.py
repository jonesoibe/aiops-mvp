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

bp = Blueprint('machine_analyzer', __name__, url_prefix='/api/machine-analyzer')

# Store active streaming threads
streaming_threads = {}

# ==================== REST ENDPOINTS ====================

@bp.route('/machines', methods=['GET'])
def get_machines():
    """Get list of all available machines grouped by server"""
    grouped = analyzer.loader.get_machines()
    return jsonify({
        'machines': grouped,
        'total_machines': len(analyzer.loader.available_machines)
    })

@bp.route('/status', methods=['GET'])
def get_status():
    """Get current analyzer status"""
    return jsonify({
        'is_running': analyzer.is_running,
        'is_paused': analyzer.is_paused,
        'current_machine': analyzer.current_machine,
        'anomaly_score': analyzer.current_anomaly_score,
        'metrics_count': len(analyzer.metrics_buffer),
        'alerts_count': len(analyzer.alerts_buffer),
        'update_frequency': analyzer.update_frequency
    })

@bp.route('/config', methods=['GET', 'POST'])
def config():
    """Get/set analyzer configuration"""
    if request.method == 'POST':
        data = request.get_json()

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

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get current metrics buffer (60-second window)"""
    return jsonify({
        'metrics': list(analyzer.metrics_buffer),
        'count': len(analyzer.metrics_buffer),
        'anomaly_score': analyzer.current_anomaly_score
    })

@bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get alert history"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({
        'alerts': list(analyzer.alerts_buffer)[-limit:],
        'count': len(analyzer.alerts_buffer)
    })

@bp.route('/start', methods=['POST'])
def start_analysis():
    """Start analyzing a machine"""
    data = request.get_json()
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

@bp.route('/pause', methods=['POST'])
def pause_analysis():
    """Pause current analysis"""
    analyzer.pause()
    return jsonify({'success': True, 'message': 'Analysis paused'})

@bp.route('/resume', methods=['POST'])
def resume_analysis():
    """Resume paused analysis"""
    analyzer.resume()
    return jsonify({'success': True, 'message': 'Analysis resumed'})

@bp.route('/reset', methods=['POST'])
def reset_analysis():
    """Reset analysis"""
    analyzer.reset()
    return jsonify({'success': True, 'message': 'Analysis reset'})

# ==================== HELPER FUNCTIONS ====================

def _run_stream():
    """Run the analyzer stream"""
    analyzer.run_stream()

# ==================== PAGE ROUTE ====================

@bp.route('/page', methods=['GET'])
def machine_analyzer_page():
    """Render the machine analyzer page"""
    return render_template('nexus/machine_analyzer.html')

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

        for report_key, report_data in reports.items():
            # Report title
            story.append(Paragraph(report_data['title'], heading_style))

            # Report description
            story.append(Paragraph(report_data['description'], body_style))
            story.append(Spacer(1, 0.2*inch))

            # Report content (convert markdown to basic text)
            content_text = report_data['content'].strip()
            # Remove markdown formatting for simplicity
            content_text = content_text.replace('##', '').replace('**', '').replace('###', '')

            for line in content_text.split('\n'):
                line = line.strip()
                if line:
                    story.append(Paragraph(line, body_style))

            story.append(Spacer(1, 0.3*inch))
            story.append(PageBreak())

        # ---- Appendix: Screenshots ----
        appendix_images = [
            'chaos_simulation',
            'classification_results',
            'confusion_matrix_mvp',
            'confusion_matrix_supervised',
            'dos_simulation_analysis',
            'feature_importance',
            'remediation_results',
            'sprint6_evaluation',
            'threshold_calibration',
        ]
        screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'processed')

        available_images = [
            name for name in appendix_images
            if os.path.exists(os.path.join(screenshots_dir, f'{name}.png'))
        ]

        if available_images:
            story.append(Paragraph("Appendix: Screenshots", heading_style))
            story.append(Paragraph(
                "Supporting visualizations from the evaluation pipeline, included for reference.",
                body_style
            ))
            story.append(PageBreak())

            max_width = 7.0 * inch
            max_height = 9.0 * inch

            for name in available_images:
                img_path = os.path.join(screenshots_dir, f'{name}.png')

                with PILImage.open(img_path) as pil_img:
                    img_w, img_h = pil_img.size

                aspect = img_h / img_w
                display_w = max_width
                display_h = display_w * aspect
                if display_h > max_height:
                    display_h = max_height
                    display_w = display_h / aspect

                title = name.replace('_', ' ').title()
                story.append(Paragraph(title, heading_style))
                story.append(Spacer(1, 0.1*inch))
                story.append(Image(img_path, width=display_w, height=display_h))
                story.append(PageBreak())

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
