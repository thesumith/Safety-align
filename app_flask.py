"""
Fast Flask Web Application for RSI Comparison Tool
Provides a split-screen interface for comparing RSI documents with highlighted missing information
"""

from flask import Flask, render_template, request, jsonify, send_file, session
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
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for sessions

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
        
        # Save uploaded files with unique IDs
        comparator_id = str(uuid.uuid4())
        our_id = str(uuid.uuid4())
        
        comparator_path = os.path.join(app.config['UPLOAD_FOLDER'], f"comparator_{comparator_id}.pdf")
        our_path = os.path.join(app.config['UPLOAD_FOLDER'], f"our_{our_id}.pdf")
        
        comparator_file.save(comparator_path)
        our_file.save(our_path)
        
        # Also save copies to output directory for PDF viewing
        comparator_output_path = os.path.join(output_dir, 'comparator_original.pdf')
        our_output_path = os.path.join(output_dir, 'our_original.pdf')
        
        import shutil
        shutil.copy2(comparator_path, comparator_output_path)
        shutil.copy2(our_path, our_output_path)
        
        # Store file IDs in session for later access
        if 'uploaded_files' not in session:
            session['uploaded_files'] = {}
        
        session['uploaded_files'][output_dir] = {
            'comparator_id': comparator_id,
            'our_id': our_id,
            'comparator_path': comparator_path,
            'our_path': our_path
        }
        
        # Run comparison
        tool = RSIComparisonTool(similarity_threshold)
        results = tool.compare_rsis(comparator_path, our_path, output_dir)
        
        # Add debugging information
        print(f"DEBUG: Found {len(results.get('comparator_sections', {}))} comparator sections")
        print(f"DEBUG: Found {len(results.get('our_sections', {}))} our sections")
        print(f"DEBUG: Comparison results keys: {list(results.get('comparison_results', {}).keys())}")
        
        # Debug section content
        for section_name, section_data in results.get('comparator_sections', {}).items():
            print(f"DEBUG: Comparator section '{section_name}': {len(section_data.get('content', ''))} chars")
            print(f"DEBUG: First 100 chars: {section_data.get('content', '')[:100]}...")
        
        for section_name, section_data in results.get('our_sections', {}).items():
            print(f"DEBUG: Our section '{section_name}': {len(section_data.get('content', ''))} chars")
            print(f"DEBUG: First 100 chars: {section_data.get('content', '')[:100]}...")
        
        # Note: Files are kept for PDF viewing, cleanup happens later
        
        # Prepare response data with PDF URLs
        response_data = {
            'success': True,
            'output_dir': output_dir,
            'summary': results['summary'],
            'detailed_results': results['comparison_results'],
            'comparator_sections': results.get('comparator_sections', {}),
            'our_sections': results.get('our_sections', {}),
            'comparator_pdf_url': f'/api/pdf/comparator?output_dir={output_dir}',
            'our_pdf_url': f'/api/pdf/our?output_dir={output_dir}'
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
        
        if report_type == 'excel':
            excel_file = os.path.join(output_dir, 'rsi_comparison_report.xlsx')
            if os.path.exists(excel_file):
                return send_file(excel_file, as_attachment=True,
                               download_name=f'rsi_comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        
        elif report_type == 'pdf':
            pdf_file = os.path.join(output_dir, 'rsi_comparison_report.pdf')
            if os.path.exists(pdf_file):
                return send_file(pdf_file, as_attachment=True,
                               download_name=f'rsi_comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        elif report_type == 'all':
            # Create ZIP file with all reports
            zip_path = os.path.join(output_dir, 'all_reports.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for filename in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, filename)
                    if os.path.isfile(file_path) and filename.endswith(('.xlsx', '.pdf')):
                        zipf.write(file_path, filename)
            
            return send_file(zip_path, as_attachment=True,
                           download_name=f'rsi_comparison_reports_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        
        return jsonify({'success': False, 'error': 'Report type not supported'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pdf/<pdf_type>')
def serve_pdf(pdf_type):
    """Serve original PDF files for viewing"""
    try:
        output_dir = request.args.get('output_dir')
        if not output_dir:
            return jsonify({'success': False, 'error': 'Output directory not specified'})
        
        print(f"DEBUG: Serving PDF {pdf_type} for output_dir: {output_dir}")
        
        # Get file information from session
        uploaded_files = session.get('uploaded_files', {})
        file_info = uploaded_files.get(output_dir)
        
        print(f"DEBUG: Session uploaded_files keys: {list(uploaded_files.keys())}")
        print(f"DEBUG: File info for {output_dir}: {file_info}")
        
        if not file_info:
            print(f"DEBUG: No file info found, trying fallback to output directory")
            # Fallback to output directory files
            if pdf_type == 'comparator':
                pdf_path = os.path.join(output_dir, 'comparator_original.pdf')
                print(f"DEBUG: Trying fallback path: {pdf_path}")
                if os.path.exists(pdf_path):
                    print(f"DEBUG: Fallback file exists, serving: {pdf_path}")
                    return send_file(pdf_path, mimetype='application/pdf')
            
            elif pdf_type == 'our':
                pdf_path = os.path.join(output_dir, 'our_original.pdf')
                print(f"DEBUG: Trying fallback path: {pdf_path}")
                if os.path.exists(pdf_path):
                    print(f"DEBUG: Fallback file exists, serving: {pdf_path}")
                    return send_file(pdf_path, mimetype='application/pdf')
            
            print(f"DEBUG: No fallback files found")
            return jsonify({'success': False, 'error': 'PDF file not found'})
        
        # Serve files from upload directory using stored paths
        if pdf_type == 'comparator':
            pdf_path = file_info['comparator_path']
            print(f"DEBUG: Serving comparator from: {pdf_path}")
            if os.path.exists(pdf_path):
                print(f"DEBUG: File exists, serving: {pdf_path}")
                return send_file(pdf_path, mimetype='application/pdf')
            else:
                print(f"DEBUG: File does not exist: {pdf_path}")
        
        elif pdf_type == 'our':
            pdf_path = file_info['our_path']
            print(f"DEBUG: Serving our PDF from: {pdf_path}")
            if os.path.exists(pdf_path):
                print(f"DEBUG: File exists, serving: {pdf_path}")
                return send_file(pdf_path, mimetype='application/pdf')
            else:
                print(f"DEBUG: File does not exist: {pdf_path}")
        
        print(f"DEBUG: No matching PDF type found: {pdf_type}")
        return jsonify({'success': False, 'error': 'PDF file not found'})
        
    except Exception as e:
        print(f"DEBUG: Exception in serve_pdf: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up uploaded files for a specific comparison"""
    try:
        output_dir = request.json.get('output_dir')
        if not output_dir:
            return jsonify({'success': False, 'error': 'Output directory not specified'})
        
        # Get file information from session
        uploaded_files = session.get('uploaded_files', {})
        file_info = uploaded_files.get(output_dir)
        
        if file_info:
            # Remove files from upload directory
            try:
                if os.path.exists(file_info['comparator_path']):
                    os.remove(file_info['comparator_path'])
                if os.path.exists(file_info['our_path']):
                    os.remove(file_info['our_path'])
            except Exception as e:
                print(f"Warning: Could not remove files: {e}")
            
            # Remove from session
            del uploaded_files[output_dir]
            session['uploaded_files'] = uploaded_files
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-pdf-access')
def test_pdf_access():
    """Test endpoint to verify PDF access"""
    try:
        output_dir = request.args.get('output_dir')
        if not output_dir:
            return jsonify({'success': False, 'error': 'Output directory not specified'})
        
        # Get file information from session
        uploaded_files = session.get('uploaded_files', {})
        file_info = uploaded_files.get(output_dir)
        
        result = {
            'output_dir': output_dir,
            'session_keys': list(uploaded_files.keys()),
            'file_info': file_info,
            'output_dir_exists': os.path.exists(output_dir),
            'fallback_files': {}
        }
        
        # Check fallback files
        if output_dir and os.path.exists(output_dir):
            comparator_fallback = os.path.join(output_dir, 'comparator_original.pdf')
            our_fallback = os.path.join(output_dir, 'our_original.pdf')
            
            result['fallback_files'] = {
                'comparator_exists': os.path.exists(comparator_fallback),
                'our_exists': os.path.exists(our_fallback),
                'comparator_path': comparator_fallback,
                'our_path': our_fallback
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
