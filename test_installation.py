"""
Test script to verify RSI Comparison Tool installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ pdfplumber import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False
    
    try:
        import pytesseract
        print("✅ pytesseract imported successfully")
    except ImportError as e:
        print(f"❌ pytesseract import failed: {e}")
        return False
    
    try:
        from fuzzywuzzy import fuzz
        print("✅ fuzzywuzzy imported successfully")
    except ImportError as e:
        print(f"❌ fuzzywuzzy import failed: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence_transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence_transformers import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    return True

def test_tesseract():
    """Test if Tesseract OCR is available"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract not available: {e}")
        print("   Please install Tesseract OCR:")
        print("   - macOS: brew install tesseract")
        print("   - Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def test_rsi_tool_import():
    """Test if the RSI tool can be imported"""
    print("\nTesting RSI Comparison Tool import...")
    
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from main import RSIComparisonTool
        print("✅ RSIComparisonTool imported successfully")
        
        # Test initialization
        tool = RSIComparisonTool()
        print("✅ RSIComparisonTool initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ RSI Comparison Tool import failed: {e}")
        return False

def test_sentence_transformer():
    """Test if sentence transformer model can be loaded"""
    print("\nTesting Sentence Transformer model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence Transformer model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Sentence Transformer model loading failed: {e}")
        print("   This is optional - the tool will work without it")
        return False

def main():
    """Main test function"""
    print("🔍 RSI Comparison Tool - Installation Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test Tesseract
    if not test_tesseract():
        all_tests_passed = False
    
    # Test RSI tool
    if not test_rsi_tool_import():
        all_tests_passed = False
    
    # Test sentence transformer (optional)
    test_sentence_transformer()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ All critical tests passed! The tool should work correctly.")
        print("\nYou can now:")
        print("1. Run the web interface: streamlit run app.py")
        print("2. Use the command line: python -m src.main comparator.pdf our.pdf")
        print("3. Try the sample: python examples/sample_usage.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nTo install missing dependencies:")
        print("pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
