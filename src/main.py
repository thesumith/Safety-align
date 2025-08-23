"""
Main Application Module for RSI Comparison Tool
Orchestrates the entire comparison process
"""

import os
import logging
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

from src.pdf_processor import PDFProcessor
from src.section_parser import SectionParser
from src.comparison_engine import ComparisonEngine, Section
from src.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RSIComparisonTool:
    """Main class for RSI comparison tool"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize the RSI comparison tool
        
        Args:
            similarity_threshold: Threshold for similarity comparison (0.0 to 1.0)
        """
        self.pdf_processor = PDFProcessor()
        self.section_parser = SectionParser()
        self.comparison_engine = ComparisonEngine(similarity_threshold)
        self.report_generator = ReportGenerator()
        
        logger.info("RSI Comparison Tool initialized successfully")
    
    def compare_rsis(self, comparator_pdf_path: str, our_pdf_path: str, 
                    output_dir: str = "output") -> Dict[str, Any]:
        """
        Compare two RSI documents
        
        Args:
            comparator_pdf_path: Path to the comparator RSI PDF
            our_pdf_path: Path to our RSI PDF
            output_dir: Directory to save output reports
            
        Returns:
            Dictionary containing comparison results and report paths
        """
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info("Starting RSI comparison process...")
            
            # Step 1: Extract text from PDFs
            logger.info("Extracting text from PDFs...")
            comparator_text = self.pdf_processor.extract_text_from_pdf(comparator_pdf_path)
            our_text = self.pdf_processor.extract_text_from_pdf(our_pdf_path)
            
            logger.info(f"Comparator PDF text length: {len(comparator_text)} characters")
            logger.info(f"Our PDF text length: {len(our_text)} characters")
            
            # Step 2: Parse sections
            logger.info("Parsing sections from both documents...")
            comparator_sections = self.section_parser.parse_sections(comparator_text)
            our_sections = self.section_parser.parse_sections(our_text)
            
            logger.info(f"Found {len(comparator_sections)} sections in comparator RSI")
            logger.info(f"Found {len(our_sections)} sections in our RSI")
            
            # If no sections found, create a whole document section
            if not comparator_sections and comparator_text.strip():
                from src.section_parser import Section
                comparator_sections['full_document'] = Section(
                    name='full_document',
                    content=comparator_text.strip(),
                    start_line=0,
                    end_line=len(comparator_text.split('\n')),
                    confidence=0.5
                )
                logger.info("No sections found in comparator - using full document")
            
            if not our_sections and our_text.strip():
                from src.section_parser import Section
                our_sections['full_document'] = Section(
                    name='full_document',
                    content=our_text.strip(),
                    start_line=0,
                    end_line=len(our_text.split('\n')),
                    confidence=0.5
                )
                logger.info("No sections found in our RSI - using full document")
            
            # Log section summary
            comparator_summary = self.section_parser.get_section_summary(comparator_sections)
            our_summary = self.section_parser.get_section_summary(our_sections)
            
            logger.info("Comparator sections found:")
            for section_name, info in comparator_summary.items():
                logger.info(f"  - {section_name}: {info['content_length']} chars, confidence: {info['confidence']:.2f}")
            
            logger.info("Our RSI sections found:")
            for section_name, info in our_summary.items():
                logger.info(f"  - {section_name}: {info['content_length']} chars, confidence: {info['confidence']:.2f}")
            
            # Step 3: Compare sections
            logger.info("Comparing sections...")
            comparison_results = self.comparison_engine.compare_documents(comparator_sections, our_sections)
            
            # Step 4: Generate summary
            logger.info("Generating summary report...")
            summary = self.comparison_engine.generate_summary_report(comparison_results)
            
            logger.info(f"Comparison completed. Overall similarity: {summary['overall_similarity']:.1%}")
            logger.info(f"Sections with issues: {summary['sections_with_issues']}")
            
            # Step 5: Generate reports
            logger.info("Generating output reports...")
            report_paths = self._generate_reports(comparison_results, summary, output_dir)
            
            # Convert sections to serializable format for web interface
            comparator_sections_serializable = {}
            our_sections_serializable = {}
            
            for section_name, section in comparator_sections.items():
                comparator_sections_serializable[section_name] = {
                    'content': section.content,
                    'confidence': section.confidence,
                    'start_line': section.start_line,
                    'end_line': section.end_line
                }
            
            for section_name, section in our_sections.items():
                our_sections_serializable[section_name] = {
                    'content': section.content,
                    'confidence': section.confidence,
                    'start_line': section.start_line,
                    'end_line': section.end_line
                }
            
            return {
                'comparison_results': comparison_results,
                'summary': summary,
                'report_paths': report_paths,
                'comparator_sections': comparator_sections_serializable,
                'our_sections': our_sections_serializable
            }
            
        except Exception as e:
            logger.error(f"Error during RSI comparison: {e}")
            raise
    
    def _generate_reports(self, comparison_results: Dict, summary: Dict[str, Any], 
                         output_dir: str) -> Dict[str, str]:
        """Generate all report formats"""
        report_paths = {}
        
        try:
            # Generate Excel report
            excel_path = os.path.join(output_dir, "rsi_comparison_report.xlsx")
            self.report_generator.generate_excel_report(comparison_results, summary, excel_path)
            report_paths['excel'] = excel_path
            
            # Generate PDF report
            pdf_path = os.path.join(output_dir, "rsi_comparison_report.pdf")
            self.report_generator.generate_pdf_report(comparison_results, summary, pdf_path)
            report_paths['pdf'] = pdf_path
            
            logger.info(f"Reports generated successfully in {output_dir}")
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            raise
        
        return report_paths
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get information about a PDF file"""
        return self.pdf_processor.get_pdf_info(pdf_path)

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='RSI Comparison Tool')
    parser.add_argument('comparator_pdf', help='Path to comparator RSI PDF file')
    parser.add_argument('our_pdf', help='Path to our RSI PDF file')
    parser.add_argument('--output-dir', default='output', help='Output directory for reports')
    parser.add_argument('--similarity-threshold', type=float, default=0.7, 
                       help='Similarity threshold (0.0 to 1.0)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input files
    if not os.path.exists(args.comparator_pdf):
        logger.error(f"Comparator PDF file not found: {args.comparator_pdf}")
        return 1
    
    if not os.path.exists(args.our_pdf):
        logger.error(f"Our PDF file not found: {args.our_pdf}")
        return 1
    
    try:
        # Initialize and run comparison
        tool = RSIComparisonTool(args.similarity_threshold)
        results = tool.compare_rsis(args.comparator_pdf, args.our_pdf, args.output_dir)
        
        # Print summary
        summary = results['summary']
        print("\n" + "="*50)
        print("RSI COMPARISON SUMMARY")
        print("="*50)
        print(f"Overall Similarity: {summary['overall_similarity']:.1%}")
        print(f"Total Sections Compared: {summary['total_sections_compared']}")
        print(f"Sections with Issues: {summary['sections_with_issues']}")
        print(f"Missing Sections: {len(summary['missing_sections'])}")
        
        if summary['missing_sections']:
            print("\nMissing Sections:")
            for section in summary['missing_sections']:
                print(f"  - {section}")
        
        if summary['sections_needing_attention']:
            print("\nSections Needing Attention:")
            for section_info in summary['sections_needing_attention']:
                print(f"  - {section_info['section']}: {section_info['similarity_score']:.1%} similarity")
        
        print(f"\nReports generated in: {args.output_dir}")
        for report_type, path in results['report_paths'].items():
            print(f"  - {report_type.upper()}: {path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
