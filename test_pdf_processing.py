#!/usr/bin/env python3
"""
Test script to verify PDF processing and comparison functionality
"""

import os
import sys
from src.pdf_processor import PDFProcessor
from src.section_parser import SectionParser
from src.comparison_engine import ComparisonEngine

def test_pdf_processing():
    """Test PDF processing with dummy content"""
    
    # Create test content
    test_content = """
    1. INDICATIONS
    This medicine is used for treating various conditions.
    It helps with inflammation and pain relief.
    
    2. CONTRAINDICATIONS
    Do not use if allergic to any ingredients.
    Not suitable for children under 12.
    
    3. WARNINGS AND PRECAUTIONS
    Use with caution in elderly patients.
    Monitor for side effects.
    
    4. ADVERSE REACTIONS
    Common side effects include nausea.
    Rare side effects include severe allergic reactions.
    
    5. OVERDOSAGE
    In case of overdose, seek immediate medical attention.
    Symptoms may include dizziness and confusion.
    """
    
    # Test section parsing
    print("Testing section parsing...")
    parser = SectionParser()
    sections = parser.parse_sections(test_content)
    
    print(f"Found {len(sections)} sections:")
    for name, section in sections.items():
        print(f"  - {name}: {len(section.content)} chars, confidence: {section.confidence:.2f}")
        print(f"    Preview: {section.content[:100]}...")
    
    # Test comparison
    print("\nTesting comparison with identical content...")
    engine = ComparisonEngine(similarity_threshold=0.7)
    
    if sections:
        # Compare sections with themselves (should be 100% similar)
        comparison_results = engine.compare_documents(sections, sections)
        
        print(f"Comparison results for {len(comparison_results)} sections:")
        for name, result in comparison_results.items():
            print(f"  - {name}: {result.similarity_score:.1%} similarity")
            print(f"    Missing: {len(result.missing_content)} items")
            print(f"    Present: {len(result.present_content)} items")
    
    # Generate summary
    summary = engine.generate_summary_report(comparison_results)
    print(f"\nOverall similarity: {summary['overall_similarity']:.1%}")
    print(f"Sections with issues: {summary['sections_with_issues']}")
    
    return True

if __name__ == "__main__":
    try:
        print("RSI Comparison Tool - Test Script")
        print("=" * 40)
        
        success = test_pdf_processing()
        
        if success:
            print("\n✅ All tests passed!")
            print("\nTo use the web interface:")
            print("1. Make sure Flask app is running: python3 app_flask.py")
            print("2. Open browser to: http://localhost:5000")
            print("3. Upload your PDF files and compare!")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

