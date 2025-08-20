"""
Report Generator Module for RSI Comparison Tool
Generates various output formats for comparison results
"""

import pandas as pd
import difflib
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComparisonResult:
    """Represents the result of comparing two sections"""
    def __init__(self, section_name: str, similarity_score: float, missing_content: List[str], 
                 present_content: List[str], comparison_method: str, details: Dict[str, Any]):
        self.section_name = section_name
        self.similarity_score = similarity_score
        self.missing_content = missing_content
        self.present_content = present_content
        self.comparison_method = comparison_method
        self.details = details

class ReportGenerator:
    """Generates various report formats for RSI comparison results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for reports"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_html_report(self, comparison_results: Dict[str, ComparisonResult], 
                           summary: Dict[str, Any], output_path: str) -> str:
        """
        Generate HTML report with detailed comparison results
        
        Args:
            comparison_results: Results from comparison engine
            summary: Summary report data
            output_path: Path to save the HTML file
            
        Returns:
            Path to the generated HTML file
        """
        html_content = self._generate_html_content(comparison_results, summary)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return output_path
    
    def _generate_html_content(self, comparison_results: Dict[str, ComparisonResult], 
                             summary: Dict[str, Any]) -> str:
        """Generate the HTML content for the report"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSI Comparison Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .summary-item {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .summary-item h4 {{
            margin: 0 0 10px 0;
            color: #007bff;
        }}
        .section {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        .section-header {{
            background-color: #007bff;
            color: white;
            padding: 15px;
            font-weight: bold;
        }}
        .section-content {{
            padding: 20px;
        }}
        .similarity-score {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .score-high {{
            background-color: #d4edda;
            color: #155724;
        }}
        .score-medium {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .score-low {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .missing-content {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 10px 0;
        }}
        .present-content {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 10px 0;
        }}
        .comparison-method {{
            background-color: #e2e3e5;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #495057;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .table th, .table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>RSI Comparison Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h4>Overall Similarity</h4>
                    <p>{summary.get('overall_similarity', 0):.1%}</p>
                </div>
                <div class="summary-item">
                    <h4>Sections Compared</h4>
                    <p>{summary.get('total_sections_compared', 0)}</p>
                </div>
                <div class="summary-item">
                    <h4>Sections with Issues</h4>
                    <p>{summary.get('sections_with_issues', 0)}</p>
                </div>
                <div class="summary-item">
                    <h4>Missing Sections</h4>
                    <p>{len(summary.get('missing_sections', []))}</p>
                </div>
            </div>
        </div>
        
        <h2>Detailed Section Analysis</h2>
"""
        
        # Add detailed section analysis
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
                
            score_class = self._get_score_class(result.similarity_score)
            
            html += f"""
        <div class="section">
            <div class="section-header">
                {section_name.replace('_', ' ').title()}
            </div>
            <div class="section-content">
                <div class="similarity-score {score_class}">
                    Similarity: {result.similarity_score:.1%}
                </div>
                <div class="comparison-method">
                    Method: {result.comparison_method.replace('_', ' ').title()}
                </div>
"""
            
            if result.missing_content:
                html += f"""
                <h4>❌ Missing Information:</h4>
                <div class="missing-content">
"""
                for item in result.missing_content[:5]:  # Show first 5 items
                    html += f"<p>• {item}</p>"
                if len(result.missing_content) > 5:
                    html += f"<p><em>... and {len(result.missing_content) - 5} more items</em></p>"
                html += "</div>"
            
            if result.present_content:
                html += f"""
                <h4>✅ Present Information:</h4>
                <div class="present-content">
"""
                for item in result.present_content[:3]:  # Show first 3 items
                    html += f"<p>• {item}</p>"
                if len(result.present_content) > 3:
                    html += f"<p><em>... and {len(result.present_content) - 3} more items</em></p>"
                html += "</div>"
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def generate_excel_report(self, comparison_results: Dict[str, ComparisonResult], 
                            summary: Dict[str, Any], output_path: str) -> str:
        """
        Generate Excel report with comparison results
        
        Args:
            comparison_results: Results from comparison engine
            summary: Summary report data
            output_path: Path to save the Excel file
            
        Returns:
            Path to the generated Excel file
        """
        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # Create summary sheet
                self._create_summary_sheet(writer, summary)
                
                # Create detailed comparison sheet
                self._create_comparison_sheet(writer, comparison_results)
                
                # Create missing content sheet
                self._create_missing_content_sheet(writer, comparison_results)
            
            logger.info(f"Excel report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            raise
    
    def _create_summary_sheet(self, writer, summary: Dict[str, Any]):
        """Create summary sheet in Excel"""
        summary_data = [
            ['Metric', 'Value'],
            ['Overall Similarity', f"{summary.get('overall_similarity', 0):.1%}"],
            ['Total Sections Compared', summary.get('total_sections_compared', 0)],
            ['Sections with Issues', summary.get('sections_with_issues', 0)],
            ['Missing Sections', len(summary.get('missing_sections', []))],
            ['', ''],
            ['Missing Sections List', ''],
        ]
        
        for section in summary.get('missing_sections', []):
            summary_data.append([section, ''])
        
        df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#007bff',
            'font_color': 'white'
        })
        
        worksheet.set_row(0, None, header_format)
        worksheet.set_column('A:B', 20)
    
    def _create_comparison_sheet(self, writer, comparison_results: Dict[str, ComparisonResult]):
        """Create detailed comparison sheet in Excel"""
        data = []
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
                
            data.append([
                section_name.replace('_', ' ').title(),
                f"{result.similarity_score:.1%}",
                result.comparison_method.replace('_', ' ').title(),
                len(result.missing_content),
                len(result.present_content),
                '; '.join(result.missing_content[:3])  # First 3 missing items
            ])
        
        df = pd.DataFrame(data, columns=[
            'Section', 'Similarity Score', 'Comparison Method', 
            'Missing Items Count', 'Present Items Count', 'Sample Missing Content'
        ])
        df.to_excel(writer, sheet_name='Detailed Comparison', index=False)
        
        # Add formatting
        workbook = writer.book
        worksheet = writer.sheets['Detailed Comparison']
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#007bff',
            'font_color': 'white'
        })
        
        worksheet.set_row(0, None, header_format)
        worksheet.set_column('A:F', 20)
    
    def _create_missing_content_sheet(self, writer, comparison_results: Dict[str, ComparisonResult]):
        """Create missing content sheet in Excel"""
        data = []
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
                
            for missing_item in result.missing_content:
                data.append([
                    section_name.replace('_', ' ').title(),
                    missing_item,
                    f"{result.similarity_score:.1%}",
                    result.comparison_method.replace('_', ' ').title()
                ])
        
        if data:
            df = pd.DataFrame(data, columns=[
                'Section', 'Missing Content', 'Similarity Score', 'Comparison Method'
            ])
            df.to_excel(writer, sheet_name='Missing Content', index=False)
            
            # Add formatting
            workbook = writer.book
            worksheet = writer.sheets['Missing Content']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#dc3545',
                'font_color': 'white'
            })
            
            worksheet.set_row(0, None, header_format)
            worksheet.set_column('A:D', 25)
    
    def generate_pdf_report(self, comparison_results: Dict[str, ComparisonResult], 
                          summary: Dict[str, Any], output_path: str) -> str:
        """
        Generate PDF report with comparison results
        
        Args:
            comparison_results: Results from comparison engine
            summary: Summary report data
            output_path: Path to save the PDF file
            
        Returns:
            Path to the generated PDF file
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Add title
            story.append(Paragraph("RSI Comparison Report", self.title_style))
            story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.normal_style))
            story.append(Spacer(1, 20))
            
            # Add summary
            story.extend(self._create_pdf_summary(summary))
            story.append(Spacer(1, 20))
            
            # Add detailed results
            story.extend(self._create_pdf_detailed_results(comparison_results))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _create_pdf_summary(self, summary: Dict[str, Any]) -> List:
        """Create summary section for PDF"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.section_style))
        
        # Create summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Overall Similarity', f"{summary.get('overall_similarity', 0):.1%}"],
            ['Total Sections Compared', str(summary.get('total_sections_compared', 0))],
            ['Sections with Issues', str(summary.get('sections_with_issues', 0))],
            ['Missing Sections', str(len(summary.get('missing_sections', [])))]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_pdf_detailed_results(self, comparison_results: Dict[str, ComparisonResult]) -> List:
        """Create detailed results section for PDF"""
        elements = []
        
        elements.append(Paragraph("Detailed Section Analysis", self.section_style))
        
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
            
            # Section header
            elements.append(Paragraph(
                f"{section_name.replace('_', ' ').title()} (Similarity: {result.similarity_score:.1%})",
                self.section_style
            ))
            
            # Method used
            elements.append(Paragraph(
                f"Comparison Method: {result.comparison_method.replace('_', ' ').title()}",
                self.normal_style
            ))
            
            # Missing content
            if result.missing_content:
                elements.append(Paragraph("Missing Information:", self.normal_style))
                for item in result.missing_content[:3]:  # Show first 3 items
                    elements.append(Paragraph(f"• {item}", self.normal_style))
                if len(result.missing_content) > 3:
                    elements.append(Paragraph(f"... and {len(result.missing_content) - 3} more items", self.normal_style))
            
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for similarity score"""
        if score >= 0.8:
            return 'score-high'
        elif score >= 0.6:
            return 'score-medium'
        else:
            return 'score-low'
