"""
PDF Processing Module for RSI Comparison Tool
Handles PDF text extraction, OCR, and noise removal
"""

import pdfplumber
import PyPDF2
import pytesseract
from PIL import Image
import re
import io
import logging
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self):
        self.noise_patterns = [
            r'^\s*\d+\s*$',  # Page numbers
            r'^\s*Page\s+\d+\s*$',  # "Page X" headers
            r'^\s*Confidential\s*$',  # Confidentiality notices
            r'^\s*Draft\s*$',  # Draft notices
            r'^\s*[A-Z\s]+\s*$',  # All caps headers/footers
            r'^\s*[©®™]\s*[\w\s]+\s*$',  # Copyright notices
        ]
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file, handling both digital and scanned PDFs
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted and cleaned text
        """
        try:
            # First try with pdfplumber for digital PDFs
            text = self._extract_with_pdfplumber(pdf_path)
            
            # If no text found, try OCR
            if not text.strip():
                logger.info(f"No text found in {pdf_path}, attempting OCR...")
                text = self._extract_with_ocr(pdf_path)
            
            # Clean the extracted text
            cleaned_text = self._clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        return text
    
    def _extract_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR for scanned PDFs"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Convert page to image
                    img = page.to_image()
                    if img:
                        # Extract text using OCR
                        page_text = pytesseract.image_to_string(img.original)
                        text += page_text + "\n"
                        logger.info(f"OCR completed for page {page_num + 1}")
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing noise and normalizing
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that match noise patterns
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in self.noise_patterns):
                continue
            
            # Clean the line
            cleaned_line = self._clean_line(line)
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)
        
        # Join lines and normalize whitespace
        cleaned_text = '\n'.join(cleaned_lines)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # Remove excessive line breaks
        
        return cleaned_text.strip()
    
    def _clean_line(self, line: str) -> str:
        """Clean individual line of text"""
        # Remove extra whitespace
        line = re.sub(r'\s+', ' ', line.strip())
        
        # Remove common PDF artifacts
        line = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}\%\$\#\@\&\*\+\=\/\|\\]', '', line)
        
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
