#!/usr/bin/env python3
"""
Test script to verify the new comparison logic with updated section boundaries
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from section_parser import SectionParser
from comparison_engine import ComparisonEngine

def test_section_parsing():
    """Test the new section parsing logic"""
    
    # Sample text with sections 4.1, 4.2, 4.3, 4.4
    test_text = """
4.1 Therapeutic indications
This medicine is used to treat various conditions.
It is indicated for the treatment of pain and inflammation.

4.2 Posology and method of administration
The recommended dose is 500mg twice daily.
Take with food to reduce stomach upset.

4.3 Contraindications
This medicine should not be used in patients with hypersensitivity.
Do not use in patients with severe liver disease.

4.4 Special warnings and precautions for use
Use with caution in elderly patients.
Monitor liver function during treatment.
    """
    
    parser = SectionParser()
    sections = parser.parse_sections(test_text)
    
    print("=== Section Parsing Test ===")
    print(f"Found {len(sections)} sections:")
    
    for section_name, section in sections.items():
        print(f"\n{section_name}:")
        print(f"  Lines: {section.start_line}-{section.end_line}")
        print(f"  Content length: {len(section.content)}")
        print(f"  Content preview: {section.content[:100]}...")
    
    # Verify that therapeutic_indications includes content from 4.1 and 4.2
    if 'therapeutic_indications' in sections:
        content = sections['therapeutic_indications'].content
        if '4.2 Posology' in content:
            print("\n✅ SUCCESS: therapeutic_indications includes 4.2 content")
        else:
            print("\n❌ FAILURE: therapeutic_indications does not include 4.2 content")
    
    return sections

def test_comparison_engine():
    """Test the comparison engine with the new section structure"""
    
    # Create sample comparator document
    comparator_text = """
4.1 Therapeutic indications
This medicine is used to treat various conditions.
It is indicated for the treatment of pain and inflammation.

4.2 Posology and method of administration
The recommended dose is 500mg twice daily.
Take with food to reduce stomach upset.

4.3 Contraindications
This medicine should not be used in patients with hypersensitivity.
Do not use in patients with severe liver disease.

4.4 Special warnings and precautions for use
Use with caution in elderly patients.
Monitor liver function during treatment.
    """
    
    # Create sample our document (slightly different)
    our_text = """
4.1 Therapeutic indications
This medicine is used to treat various conditions.
It is indicated for the treatment of pain and inflammation.

4.2 Posology and method of administration
The recommended dose is 600mg twice daily.
Take with food to reduce stomach upset.

4.3 Contraindications
This medicine should not be used in patients with hypersensitivity.
Do not use in patients with severe liver disease.

4.4 Special warnings and precautions for use
Use with caution in elderly patients.
Monitor liver function during treatment.
    """
    
    parser = SectionParser()
    comparator_sections = parser.parse_sections(comparator_text)
    our_sections = parser.parse_sections(our_text)
    
    engine = ComparisonEngine()
    results = engine.compare_documents(comparator_sections, our_sections)
    
    print("\n=== Comparison Engine Test ===")
    print(f"Comparator sections: {list(comparator_sections.keys())}")
    print(f"Our sections: {list(our_sections.keys())}")
    print(f"Comparison results: {list(results.keys())}")
    
    for section_name, result in results.items():
        print(f"\n{section_name}:")
        print(f"  Similarity: {result.similarity_score:.2f}")
        print(f"  Method: {result.comparison_method}")
        if result.missing_content:
            print(f"  Missing: {len(result.missing_content)} items")
        if result.present_content:
            print(f"  Present: {len(result.present_content)} items")
    
    return results

if __name__ == "__main__":
    print("Testing new comparison logic with updated section boundaries...")
    
    # Test section parsing
    sections = test_section_parsing()
    
    # Test comparison engine
    results = test_comparison_engine()
    
    print("\n=== Test Summary ===")
    print("The new comparison logic should:")
    print("1. Include 4.2 content within therapeutic_indications (4.1)")
    print("2. Include content from each section until the next section")
    print("3. Compare sections in the correct order: 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9")
    
    print("\nTest completed!")
