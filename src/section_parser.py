"""
Section Parser Module for RSI Comparison Tool
Identifies and extracts different sections from RSI documents
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Section:
    """Represents a section in an RSI document"""
    name: str
    content: str
    start_line: int
    end_line: int
    confidence: float

class SectionParser:
    """Parses RSI documents into structured sections"""
    
    def __init__(self):
        # Define section patterns with keywords and regex
        self.section_patterns = {
            'indications': {
                'keywords': ['indications', 'indication', 'use', 'uses', 'clinical use'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*INDICATIONS?\s*$',
                    r'^\s*INDICATIONS?\s*$',
                    r'^\s*\d+\.?\s*CLINICAL\s+USE\s*$',
                    r'^\s*USE\s*$',
                ],
                'stop_keywords': ['contraindications', 'warnings', 'precautions', 'adverse']
            },
            'contraindications': {
                'keywords': ['contraindications', 'contraindication', 'contra-indications'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*CONTRAINDICATIONS?\s*$',
                    r'^\s*CONTRAINDICATIONS?\s*$',
                    r'^\s*\d+\.?\s*CONTRA-INDICATIONS?\s*$',
                ],
                'stop_keywords': ['warnings', 'precautions', 'adverse', 'dosage']
            },
            'warnings_precautions': {
                'keywords': ['warnings', 'warning', 'precautions', 'precaution', 'special warnings'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*WARNINGS?\s*$',
                    r'^\s*WARNINGS?\s*$',
                    r'^\s*\d+\.?\s*PRECAUTIONS?\s*$',
                    r'^\s*PRECAUTIONS?\s*$',
                    r'^\s*\d+\.?\s*SPECIAL\s+WARNINGS?\s*$',
                    r'^\s*\d+\.?\s*WARNINGS?\s+AND\s+PRECAUTIONS?\s*$',
                ],
                'stop_keywords': ['adverse', 'reactions', 'dosage', 'administration']
            },
            'adverse_reactions': {
                'keywords': ['adverse', 'reactions', 'effects', 'side effects', 'adverse events'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*ADVERSE\s+REACTIONS?\s*$',
                    r'^\s*ADVERSE\s+REACTIONS?\s*$',
                    r'^\s*\d+\.?\s*SIDE\s+EFFECTS?\s*$',
                    r'^\s*SIDE\s+EFFECTS?\s*$',
                    r'^\s*\d+\.?\s*ADVERSE\s+EVENTS?\s*$',
                    r'^\s*ADVERSE\s+EVENTS?\s*$',
                ],
                'stop_keywords': ['drug', 'interactions', 'dosage', 'administration']
            },
            'drug_interactions': {
                'keywords': ['drug interactions', 'interactions', 'drug-drug', 'drug interactions'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*DRUG\s+INTERACTIONS?\s*$',
                    r'^\s*DRUG\s+INTERACTIONS?\s*$',
                    r'^\s*\d+\.?\s*INTERACTIONS?\s*$',
                    r'^\s*INTERACTIONS?\s*$',
                ],
                'stop_keywords': ['dosage', 'administration', 'overdosage']
            },
            'dosage_administration': {
                'keywords': ['dosage', 'administration', 'dose', 'dosing', 'posology'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*DOSAGE\s*$',
                    r'^\s*DOSAGE\s*$',
                    r'^\s*\d+\.?\s*ADMINISTRATION\s*$',
                    r'^\s*ADMINISTRATION\s*$',
                    r'^\s*\d+\.?\s*DOSAGE\s+AND\s+ADMINISTRATION\s*$',
                    r'^\s*DOSAGE\s+AND\s+ADMINISTRATION\s*$',
                    r'^\s*\d+\.?\s*POSOLOGY\s*$',
                    r'^\s*POSOLOGY\s*$',
                ],
                'stop_keywords': ['overdosage', 'storage', 'handling']
            },
            'overdosage': {
                'keywords': ['overdosage', 'overdose', 'over dose'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*OVERDOSAGE\s*$',
                    r'^\s*OVERDOSAGE\s*$',
                    r'^\s*\d+\.?\s*OVERDOSE\s*$',
                    r'^\s*OVERDOSE\s*$',
                ],
                'stop_keywords': ['storage', 'handling', 'description']
            },
            'storage_handling': {
                'keywords': ['storage', 'handling', 'stability'],
                'regex_patterns': [
                    r'^\s*\d+\.?\s*STORAGE\s*$',
                    r'^\s*STORAGE\s*$',
                    r'^\s*\d+\.?\s*HANDLING\s*$',
                    r'^\s*HANDLING\s*$',
                    r'^\s*\d+\.?\s*STORAGE\s+AND\s+HANDLING\s*$',
                    r'^\s*STORAGE\s+AND\s+HANDLING\s*$',
                ],
                'stop_keywords': ['description', 'pharmaceutical', 'form']
            }
        }
    
    def parse_sections(self, text: str) -> Dict[str, Section]:
        """
        Parse text into structured sections
        
        Args:
            text: The full text of the RSI document
            
        Returns:
            Dictionary mapping section names to Section objects
        """
        lines = text.split('\n')
        sections = {}
        
        # First pass: find section boundaries using regex patterns
        section_boundaries = self._find_section_boundaries(lines)
        
        # Second pass: extract content for each section
        for section_name, (start_line, end_line) in section_boundaries.items():
            if start_line < end_line:
                content = '\n'.join(lines[start_line:end_line]).strip()
                if content:
                    confidence = self._calculate_section_confidence(section_name, lines[start_line])
                    sections[section_name] = Section(
                        name=section_name,
                        content=content,
                        start_line=start_line,
                        end_line=end_line,
                        confidence=confidence
                    )
        
        # Third pass: try to find missing sections using keyword search
        missing_sections = self._find_missing_sections(text, sections.keys())
        sections.update(missing_sections)
        
        return sections
    
    def _find_section_boundaries(self, lines: List[str]) -> Dict[str, Tuple[int, int]]:
        """Find the start and end lines for each section"""
        boundaries = {}
        current_section = None
        current_start = 0
        
        for i, line in enumerate(lines):
            line_upper = line.upper().strip()
            
            # Check if this line starts a new section
            for section_name, pattern_info in self.section_patterns.items():
                if self._matches_section_pattern(line_upper, pattern_info):
                    # End the previous section if exists
                    if current_section and current_section not in boundaries:
                        boundaries[current_section] = (current_start, i)
                    
                    # Start new section
                    current_section = section_name
                    current_start = i
                    break
            
            # Check if we've reached the end of current section
            if current_section and self._is_section_end(line_upper, current_section):
                if current_section not in boundaries:
                    boundaries[current_section] = (current_start, i)
                current_section = None
        
        # Handle the last section
        if current_section and current_section not in boundaries:
            boundaries[current_section] = (current_start, len(lines))
        
        return boundaries
    
    def _matches_section_pattern(self, line: str, pattern_info: Dict) -> bool:
        """Check if a line matches a section pattern"""
        # Check regex patterns
        for pattern in pattern_info['regex_patterns']:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # Check keyword patterns
        for keyword in pattern_info['keywords']:
            if keyword.lower() in line.lower():
                return True
        
        return False
    
    def _is_section_end(self, line: str, current_section: str) -> bool:
        """Check if a line indicates the end of the current section"""
        if current_section in self.section_patterns:
            stop_keywords = self.section_patterns[current_section]['stop_keywords']
            for keyword in stop_keywords:
                if keyword.lower() in line.lower():
                    return True
        
        # Check if line starts with a number (likely next section)
        if re.match(r'^\s*\d+\.?\s*[A-Z]', line):
            return True
        
        return False
    
    def _calculate_section_confidence(self, section_name: str, first_line: str) -> float:
        """Calculate confidence score for section identification"""
        if section_name not in self.section_patterns:
            return 0.0
        
        pattern_info = self.section_patterns[section_name]
        confidence = 0.0
        
        # Check regex patterns (highest confidence)
        for pattern in pattern_info['regex_patterns']:
            if re.match(pattern, first_line, re.IGNORECASE):
                confidence = max(confidence, 0.9)
        
        # Check keyword patterns
        for keyword in pattern_info['keywords']:
            if keyword.lower() in first_line.lower():
                confidence = max(confidence, 0.7)
        
        return confidence
    
    def _find_missing_sections(self, text: str, found_sections: set) -> Dict[str, Section]:
        """Find sections that might have been missed using keyword search"""
        missing_sections = {}
        lines = text.split('\n')
        
        for section_name, pattern_info in self.section_patterns.items():
            if section_name in found_sections:
                continue
            
            # Search for keywords in the text
            for keyword in pattern_info['keywords']:
                if keyword.lower() in text.lower():
                    # Find the line containing the keyword
                    for i, line in enumerate(lines):
                        if keyword.lower() in line.lower():
                            # Extract content around this line
                            start_line = max(0, i - 5)
                            end_line = min(len(lines), i + 50)  # Extract reasonable amount of content
                            
                            content = '\n'.join(lines[start_line:end_line]).strip()
                            if content:
                                missing_sections[section_name] = Section(
                                    name=section_name,
                                    content=content,
                                    start_line=start_line,
                                    end_line=end_line,
                                    confidence=0.5  # Lower confidence for keyword-based detection
                                )
                            break
                    break
        
        return missing_sections
    
    def get_section_summary(self, sections: Dict[str, Section]) -> Dict[str, dict]:
        """Get a summary of found sections"""
        summary = {}
        for section_name, section in sections.items():
            summary[section_name] = {
                'confidence': section.confidence,
                'content_length': len(section.content),
                'line_count': section.end_line - section.start_line,
                'preview': section.content[:200] + '...' if len(section.content) > 200 else section.content
            }
        return summary
