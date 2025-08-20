"""
Fast Flask Web Application for RSI Comparison Tool
Provides a split-screen interface for comparing RSI documents with highlighted missing information
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import uuid
import zipfile
from datetime import datetime
import json

from src.main import RSIComparisonTool

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Main page with split-screen interface"""
    return render_template('index.html')

@app.route('/api/compare', methods=['POST'])
def compare_documents():
    """API endpoint for document comparison"""
    try:
        # Check if files were uploaded
        if 'comparator_pdf' not in request.files or 'our_pdf' not in request.files:
            return jsonify({'success': False, 'error': 'Both PDF files are required'})
        
        comparator_file = request.files['comparator_pdf']
        our_file = request.files['our_pdf']
        
        if comparator_file.filename == '' or our_file.filename == '':
            return jsonify({'success': False, 'error': 'Both PDF files are required'})
        
        # Get similarity threshold
        similarity_threshold = float(request.form.get('similarity_threshold', 0.7))
        
        # Create unique output directory
        output_dir = os.path.join('output', str(uuid.uuid4()))
        os.makedirs(output_dir, exist_ok=True)
        
        # Save uploaded files
        comparator_path = os.path.join(app.config['UPLOAD_FOLDER'], f"comparator_{uuid.uuid4()}.pdf")
        our_path = os.path.join(app.config['UPLOAD_FOLDER'], f"our_{uuid.uuid4()}.pdf")
        
        comparator_file.save(comparator_path)
        our_file.save(our_path)
        
        # Run comparison
        tool = RSIComparisonTool(similarity_threshold)
        results = tool.compare_rsis(comparator_path, our_path, output_dir)
        
        # Clean up uploaded files
        os.remove(comparator_path)
        os.remove(our_path)
        
        # Prepare response data
        response_data = {
            'success': True,
            'output_dir': output_dir,
            'summary': results['summary'],
            'detailed_results': results['comparison_results'],
            'comparator_sections': results.get('comparator_sections', {}),
            'our_sections': results.get('our_sections', {})
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download/<report_type>')
def download_report(report_type):
    """Download generated reports"""
    try:
        output_dir = request.args.get('output_dir')
        if not output_dir or not os.path.exists(output_dir):
            return jsonify({'success': False, 'error': 'Report not found'})
        
        if report_type == 'html':
            html_file = os.path.join(output_dir, 'comparison_report.html')
            if os.path.exists(html_file):
                return send_file(html_file, as_attachment=True, 
                               download_name=f'rsi_comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        
        elif report_type == 'excel':
            excel_file = os.path.join(output_dir, 'comparison_report.xlsx')
            if os.path.exists(excel_file):
                return send_file(excel_file, as_attachment=True,
                               download_name=f'rsi_comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        
        elif report_type == 'pdf':
            pdf_file = os.path.join(output_dir, 'comparison_report.pdf')
            if os.path.exists(pdf_file):
                return send_file(pdf_file, as_attachment=True,
                               download_name=f'rsi_comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        elif report_type == 'all':
            # Create ZIP file with all reports
            zip_path = os.path.join(output_dir, 'all_reports.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for filename in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, filename)
                    if os.path.isfile(file_path) and filename.endswith(('.html', '.xlsx', '.pdf')):
                        zipf.write(file_path, filename)
            
            return send_file(zip_path, as_attachment=True,
                           download_name=f'rsi_comparison_reports_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        
        return jsonify({'success': False, 'error': 'Report type not supported'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
