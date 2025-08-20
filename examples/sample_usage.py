"""
Sample Usage Script for RSI Comparison Tool
Demonstrates how to use the tool programmatically
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import RSIComparisonTool

def create_sample_pdf():
    """Create a sample PDF for demonstration purposes"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            doc = SimpleDocTemplate(tmp_file.name, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add sample RSI content
            story.append(Paragraph("SAMPLE RSI DOCUMENT", styles['Title']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("1. INDICATIONS", styles['Heading1']))
            story.append(Paragraph("This medication is indicated for the treatment of hypertension in adults.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("2. CONTRAINDICATIONS", styles['Heading1']))
            story.append(Paragraph("Contraindicated in patients with known hypersensitivity to the active substance.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("3. WARNINGS AND PRECAUTIONS", styles['Heading1']))
            story.append(Paragraph("Monitor blood pressure regularly. Use with caution in patients with renal impairment.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("4. ADVERSE REACTIONS", styles['Heading1']))
            story.append(Paragraph("Common adverse reactions include headache, dizziness, and fatigue.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("5. DRUG INTERACTIONS", styles['Heading1']))
            story.append(Paragraph("May interact with other antihypertensive medications.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("6. DOSAGE AND ADMINISTRATION", styles['Heading1']))
            story.append(Paragraph("Recommended starting dose is 10mg once daily.", styles['Normal']))
            
            doc.build(story)
            return tmp_file.name
            
    except ImportError:
        print("ReportLab not available. Creating a simple text file instead.")
        # Create a simple text file as fallback
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            content = """
SAMPLE RSI DOCUMENT

1. INDICATIONS
This medication is indicated for the treatment of hypertension in adults.

2. CONTRAINDICATIONS
Contraindicated in patients with known hypersensitivity to the active substance.

3. WARNINGS AND PRECAUTIONS
Monitor blood pressure regularly. Use with caution in patients with renal impairment.

4. ADVERSE REACTIONS
Common adverse reactions include headache, dizziness, and fatigue.

5. DRUG INTERACTIONS
May interact with other antihypertensive medications.

6. DOSAGE AND ADMINISTRATION
Recommended starting dose is 10mg once daily.
"""
            tmp_file.write(content.encode('utf-8'))
            return tmp_file.name

def create_comparator_pdf():
    """Create a comparator PDF with more comprehensive content"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            doc = SimpleDocTemplate(tmp_file.name, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            story.append(Paragraph("COMPARATOR RSI DOCUMENT", styles['Title']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("1. INDICATIONS", styles['Heading1']))
            story.append(Paragraph("This medication is indicated for the treatment of hypertension in adults. It may also be used for the management of heart failure in certain patient populations.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("2. CONTRAINDICATIONS", styles['Heading1']))
            story.append(Paragraph("Contraindicated in patients with known hypersensitivity to the active substance or any of the excipients. Not recommended in pregnant women during the first trimester.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("3. WARNINGS AND PRECAUTIONS", styles['Heading1']))
            story.append(Paragraph("Monitor blood pressure regularly. Use with caution in patients with renal impairment. Monitor liver function tests in patients with hepatic disease. Risk of angioedema in patients with history of ACE inhibitor use.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("4. ADVERSE REACTIONS", styles['Heading1']))
            story.append(Paragraph("Common adverse reactions include headache, dizziness, fatigue, and cough. Serious adverse reactions may include angioedema, hyperkalemia, and acute kidney injury.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("5. DRUG INTERACTIONS", styles['Heading1']))
            story.append(Paragraph("May interact with other antihypertensive medications, potassium-sparing diuretics, lithium, and NSAIDs. Monitor closely when co-administered with CYP3A4 inhibitors.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("6. DOSAGE AND ADMINISTRATION", styles['Heading1']))
            story.append(Paragraph("Recommended starting dose is 10mg once daily. May be titrated up to 40mg daily based on patient response and tolerability. Take with or without food.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("7. OVERDOSAGE", styles['Heading1']))
            story.append(Paragraph("In case of overdose, provide supportive care and monitor vital signs. Consider activated charcoal if ingestion was recent.", styles['Normal']))
            story.append(Spacer(1, 12))
            
            story.append(Paragraph("8. STORAGE AND HANDLING", styles['Heading1']))
            story.append(Paragraph("Store at room temperature (20-25°C). Keep container tightly closed. Protect from light and moisture.", styles['Normal']))
            
            doc.build(story)
            return tmp_file.name
            
    except ImportError:
        print("ReportLab not available. Creating a simple text file instead.")
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            content = """
COMPARATOR RSI DOCUMENT

1. INDICATIONS
This medication is indicated for the treatment of hypertension in adults. It may also be used for the management of heart failure in certain patient populations.

2. CONTRAINDICATIONS
Contraindicated in patients with known hypersensitivity to the active substance or any of the excipients. Not recommended in pregnant women during the first trimester.

3. WARNINGS AND PRECAUTIONS
Monitor blood pressure regularly. Use with caution in patients with renal impairment. Monitor liver function tests in patients with hepatic disease. Risk of angioedema in patients with history of ACE inhibitor use.

4. ADVERSE REACTIONS
Common adverse reactions include headache, dizziness, fatigue, and cough. Serious adverse reactions may include angioedema, hyperkalemia, and acute kidney injury.

5. DRUG INTERACTIONS
May interact with other antihypertensive medications, potassium-sparing diuretics, lithium, and NSAIDs. Monitor closely when co-administered with CYP3A4 inhibitors.

6. DOSAGE AND ADMINISTRATION
Recommended starting dose is 10mg once daily. May be titrated up to 40mg daily based on patient response and tolerability. Take with or without food.

7. OVERDOSAGE
In case of overdose, provide supportive care and monitor vital signs. Consider activated charcoal if ingestion was recent.

8. STORAGE AND HANDLING
Store at room temperature (20-25°C). Keep container tightly closed. Protect from light and moisture.
"""
            tmp_file.write(content.encode('utf-8'))
            return tmp_file.name

def main():
    """Main demonstration function"""
    print("🚀 RSI Comparison Tool - Sample Usage")
    print("=" * 50)
    
    # Create sample PDFs
    print("Creating sample PDFs...")
    comparator_pdf = create_comparator_pdf()
    our_pdf = create_sample_pdf()
    
    print(f"Comparator PDF: {comparator_pdf}")
    print(f"Our PDF: {our_pdf}")
    
    try:
        # Initialize the tool
        print("\nInitializing RSI Comparison Tool...")
        tool = RSIComparisonTool(similarity_threshold=0.7)
        
        # Run comparison
        print("Running comparison...")
        results = tool.compare_rsis(
            comparator_pdf_path=comparator_pdf,
            our_pdf_path=our_pdf,
            output_dir="sample_output"
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("COMPARISON RESULTS")
        print("=" * 50)
        
        summary = results['summary']
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
        
        # Show detailed results for each section
        print("\nDetailed Section Analysis:")
        for section_name, result in results['comparison_results'].items():
            if section_name.startswith('extra_'):
                continue
                
            print(f"\n{section_name.replace('_', ' ').title()}:")
            print(f"  Similarity: {result.similarity_score:.1%}")
            print(f"  Method: {result.comparison_method}")
            print(f"  Missing items: {len(result.missing_content)}")
            print(f"  Present items: {len(result.present_content)}")
            
            if result.missing_content:
                print("  Missing content examples:")
                for item in result.missing_content[:2]:  # Show first 2 items
                    print(f"    - {item[:100]}...")
        
        # Show report paths
        print(f"\nReports generated in: sample_output")
        for report_type, path in results['report_paths'].items():
            print(f"  - {report_type.upper()}: {path}")
        
        print("\n✅ Sample usage completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temporary files
        try:
            os.unlink(comparator_pdf)
            os.unlink(our_pdf)
        except:
            pass

if __name__ == "__main__":
    main()
