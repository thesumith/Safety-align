"""
Enhanced PDF Processing Module for RSI Comparison Tool
Fast, accurate text extraction optimized for pharmaceutical documents
"""

import pdfplumber
import PyPDF2
import pytesseract
from PIL import Image
import re
import io
import logging
from typing import List, Tuple, Optional, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Enhanced PDF processor optimized for RSI documents"""
    
    def __init__(self):
        # Enhanced noise patterns for pharmaceutical documents
        self.noise_patterns = [
            r'^\s*\d+\s*$',  # Page numbers
            r'^\s*Page\s+\d+.*$',  # Page headers
            r'^\s*Confidential.*$',  # Confidentiality notices
            r'^\s*CONFIDENTIAL.*$',
            r'^\s*Draft.*$',  # Draft notices
            r'^\s*DRAFT.*$',
            r'^\s*[©®™]\s*.*$',  # Copyright notices
            r'^\s*EMA/\d+.*$',  # EMA reference numbers
            r'^\s*CHMP/\d+.*$',  # CHMP reference numbers
            r'^\s*\w{2,4}/\d{4}/\d+.*$',  # Regulatory reference patterns
            r'^\s*Version \d+.*$',  # Version information
            r'^\s*Date:.*$',  # Date stamps
            r'^\s*[A-Z\s]{20,}\s*$',  # Very long all-caps headers (likely noise)
        ]
        
        # Patterns that help identify section boundaries
        self.section_indicators = [
            r'^\s*\d+\.?\d*\.?\s+[A-Z]',  # Numbered sections
            r'^\s*[A-Z][A-Z\s]{10,}$',  # All caps section headers
            r'^\s*\d+\.\s*[A-Z]',  # Simple numbered sections
        ]
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Enhanced text extraction optimized for RSI documents
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted and cleaned text with preserved structure
        """
        try:
            # Fast extraction with pdfplumber (optimized)
            text = self._extract_with_pdfplumber_enhanced(pdf_path)
            
            # If minimal text found, try OCR (only if necessary)
            if len(text.strip()) < 500:  # Threshold for meaningful content
                logger.info(f"Limited text found in {pdf_path}, attempting OCR...")
                ocr_text = self._extract_with_ocr_fast(pdf_path)
                if len(ocr_text) > len(text):
                    text = ocr_text
            
            # Enhanced cleaning with structure preservation
            cleaned_text = self._clean_text_enhanced(text)
            
            logger.info(f"Extracted {len(cleaned_text)} characters from {pdf_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            # Return empty string instead of raising to keep the app functional
            return ""
    
    def _extract_with_pdfplumber_enhanced(self, pdf_path: str) -> str:
        """Enhanced text extraction with structure preservation"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Extract text with layout preservation
                        page_text = page.extract_text(layout=True, x_tolerance=2, y_tolerance=2)
                        
                        if not page_text and page.chars:
                            # Fallback: extract without layout if layout fails
                            page_text = page.extract_text()
                        
                        if page_text:
                            # Add page markers for better section detection
                            if page_num > 0:
                                text += "\n--- PAGE BREAK ---\n"
                            text += page_text + "\n"
                    except Exception as page_error:
                        logger.warning(f"Failed to extract page {page_num + 1}: {page_error}")
                        continue
                        
        except Exception as e:
            logger.warning(f"Enhanced pdfplumber extraction failed: {str(e)}")
            # Fallback to simple extraction
            text = self._extract_with_pdfplumber_simple(pdf_path)
        
        return text
    
    def _extract_with_pdfplumber_simple(self, pdf_path: str) -> str:
        """Simple fallback extraction"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"Simple pdfplumber extraction failed: {str(e)}")
        return text
    
    def _extract_with_ocr_fast(self, pdf_path: str) -> str:
        """Fast OCR extraction (limited pages for speed)"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Limit OCR to first 10 pages for speed
                pages_to_process = min(10, len(pdf.pages))
                
                for page_num in range(pages_to_process):
                    page = pdf.pages[page_num]
                    try:
                        # Convert page to image with reasonable resolution
                        img = page.to_image(resolution=150)  # Lower resolution for speed
                        if img:
                            # OCR with optimized settings
                            page_text = pytesseract.image_to_string(
                                img.original, 
                                config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()[]{}+-=/*%$#@&|\\<>\"\'_'
                            )
                            text += page_text + "\n"
                            logger.info(f"OCR completed for page {page_num + 1}")
                    except Exception as page_error:
                        logger.warning(f"OCR failed for page {page_num + 1}: {page_error}")
                        continue
        except Exception as e:
            logger.error(f"Fast OCR extraction failed: {str(e)}")
        
        return text
    
    def _clean_text_enhanced(self, text: str) -> str:
        """
        Enhanced text cleaning with structure preservation for RSI documents
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text with preserved structure
        """
        if not text:
            return ""
        
        # Remove page markers but preserve structure
        text = re.sub(r'\n---\s*PAGE BREAK\s*---\n', '\n\n', text)
        
        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []
        consecutive_empty = 0
        
        for i, line in enumerate(lines):
            # Track empty lines to avoid too many consecutive ones
            if not line.strip():
                consecutive_empty += 1
                if consecutive_empty <= 2:  # Allow max 2 consecutive empty lines
                    cleaned_lines.append('')
                continue
            else:
                consecutive_empty = 0
            
            # Skip lines that match noise patterns
            if self._is_noise_line(line):
                continue
            
            # Check if this might be a section header
            is_section_header = any(re.match(pattern, line) for pattern in self.section_indicators)
            
            # Clean the line
            cleaned_line = self._clean_line_enhanced(line)
            
            if cleaned_line.strip():
                # Add extra space before section headers for better parsing
                if is_section_header and cleaned_lines and cleaned_lines[-1].strip():
                    cleaned_lines.append('')
                
                cleaned_lines.append(cleaned_line)
                
                # Add space after section headers
                if is_section_header:
                    cleaned_lines.append('')
        
        # Join lines and do final cleanup
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Normalize whitespace within lines but preserve line structure
        lines = cleaned_text.split('\n')
        normalized_lines = []
        for line in lines:
            if line.strip():
                # Normalize spaces within the line
                normalized_line = re.sub(r'\s+', ' ', line.strip())
                normalized_lines.append(normalized_line)
            else:
                normalized_lines.append('')
        
        cleaned_text = '\n'.join(normalized_lines)
        
        # Remove excessive empty lines (more than 2 consecutive)
        cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def _is_noise_line(self, line: str) -> bool:
        """Check if a line is noise and should be removed"""
        line_clean = line.strip()
        
        # Skip very short lines that are likely noise
        if len(line_clean) <= 2:
            return True
            
        # Check against noise patterns
        for pattern in self.noise_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Check for repetitive characters (often formatting artifacts)
        if len(set(line_clean)) <= 2 and len(line_clean) > 10:
            return True
        
        # Check for lines with only numbers and spaces
        if re.match(r'^[\d\s\-\.]+$', line_clean) and len(line_clean) < 20:
            return True
            
        return False
    
    def _clean_line_enhanced(self, line: str) -> str:
        """Enhanced line cleaning for pharmaceutical documents"""
        # Remove extra whitespace
        line = re.sub(r'\s+', ' ', line.strip())
        
        # Remove common PDF artifacts but preserve important characters
        # Keep more characters that are common in pharmaceutical documents
        line = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\%\$\#\@\&\*\+\=\/\|\\°µ≥≤™®©]', '', line)
        
        # Fix common OCR errors in pharmaceutical text
        replacements = {
            ' mg ': ' mg ',  # Normalize mg spacing
            ' mcg ': ' mcg ',  # Normalize mcg spacing
            ' kg ': ' kg ',  # Normalize kg spacing
            '°C': '°C',  # Preserve temperature
            '±': '±',  # Preserve plus/minus
        }
        
        for old, new in replacements.items():
            line = line.replace(old, new)
        
        return line
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get basic information about the PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                info = {
                    'num_pages': len(reader.pages),
                    'title': reader.metadata.get('/Title', 'Unknown'),
                    'author': reader.metadata.get('/Author', 'Unknown'),
                    'subject': reader.metadata.get('/Subject', 'Unknown'),
                    'creator': reader.metadata.get('/Creator', 'Unknown'),
                }
            return info
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return {'error': str(e)}
