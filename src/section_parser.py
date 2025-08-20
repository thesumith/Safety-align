"""
Section Parser Module for RSI Comparison Tool
Identifies and extracts different sections from RSI documents
Optimized for speed and specific section ordering
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
    """Parses RSI documents into structured sections with optimized speed"""
    
    def __init__(self):
        # Define section patterns in the exact order specified by user
        # Optimized regex patterns for faster matching
        self.section_patterns = {
            'indications': {
                'keywords': ['indications', 'indication', 'use', 'uses', 'clinical use'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*INDICATIONS?\s*$',
                    r'^\s*INDICATIONS?\s*$',
                    r'^\s*\d*\.?\s*CLINICAL\s+USE\s*$',
                    r'^\s*USE\s*$',
                ],
                'stop_keywords': ['contraindications', 'warnings', 'precautions', 'adverse']
            },
            'contraindications': {
                'keywords': ['contraindications', 'contraindication', 'contra-indications'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*CONTRAINDICATIONS?\s*$',
                    r'^\s*CONTRAINDICATIONS?\s*$',
                    r'^\s*\d*\.?\s*CONTRA-INDICATIONS?\s*$',
                ],
                'stop_keywords': ['warnings', 'precautions', 'adverse', 'dosage']
            },
            'warnings_precautions': {
                'keywords': ['warnings', 'warning', 'precautions', 'precaution', 'special warnings'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*WARNINGS?\s*$',
                    r'^\s*WARNINGS?\s*$',
                    r'^\s*\d*\.?\s*PRECAUTIONS?\s*$',
                    r'^\s*PRECAUTIONS?\s*$',
                    r'^\s*\d*\.?\s*SPECIAL\s+WARNINGS?\s*$',
                    r'^\s*\d*\.?\s*WARNINGS?\s+AND\s+PRECAUTIONS?\s*$',
                ],
                'stop_keywords': ['adverse', 'reactions', 'dosage', 'administration', 'drug']
            },
            'drug_interactions': {
                'keywords': ['drug interactions', 'interactions', 'drug-drug', 'drug interactions'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*DRUG\s+INTERACTIONS?\s*$',
                    r'^\s*DRUG\s+INTERACTIONS?\s*$',
                    r'^\s*\d*\.?\s*INTERACTIONS?\s*$',
                    r'^\s*INTERACTIONS?\s*$',
                ],
                'stop_keywords': ['dosage', 'administration', 'overdosage', 'fertility']
            },
            'fertility': {
                'keywords': ['fertility', 'fertile', 'reproductive'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*FERTILITY\s*$',
                    r'^\s*FERTILITY\s*$',
                    r'^\s*\d*\.?\s*FERTILITY,\s+PREGNANCY\s*$',
                ],
                'stop_keywords': ['pregnancy', 'lactation', 'dosage']
            },
            'pregnancy_lactation': {
                'keywords': ['pregnancy', 'lactation', 'breastfeeding', 'pregnant'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*PREGNANCY\s*$',
                    r'^\s*PREGNANCY\s*$',
                    r'^\s*\d*\.?\s*LACTATION\s*$',
                    r'^\s*LACTATION\s*$',
                    r'^\s*\d*\.?\s*PREGNANCY\s+AND\s+LACTATION\s*$',
                    r'^\s*PREGNANCY\s+AND\s+LACTATION\s*$',
                ],
                'stop_keywords': ['driving', 'machines', 'adverse', 'reactions']
            },
            'driving_machines': {
                'keywords': ['driving', 'machines', 'vehicle', 'operating'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*ABILITY\s+TO\s+DRIVE\s*$',
                    r'^\s*ABILITY\s+TO\s+DRIVE\s*$',
                    r'^\s*\d*\.?\s*DRIVING\s*$',
                    r'^\s*DRIVING\s*$',
                    r'^\s*\d*\.?\s*USE\s+OF\s+MACHINES\s*$',
                    r'^\s*USE\s+OF\s+MACHINES\s*$',
                    r'^\s*\d*\.?\s*ABILITY\s+TO\s+DRIVE\s+AND\s+USE\s+MACHINES\s*$',
                ],
                'stop_keywords': ['adverse', 'reactions', 'overdosage']
            },
            'adverse_reactions': {
                'keywords': ['adverse', 'reactions', 'effects', 'side effects', 'adverse events'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*ADVERSE\s+REACTIONS?\s*$',
                    r'^\s*ADVERSE\s+REACTIONS?\s*$',
                    r'^\s*\d*\.?\s*SIDE\s+EFFECTS?\s*$',
                    r'^\s*SIDE\s+EFFECTS?\s*$',
                    r'^\s*\d*\.?\s*ADVERSE\s+EVENTS?\s*$',
                    r'^\s*ADVERSE\s+EVENTS?\s*$',
                ],
                'stop_keywords': ['overdosage', 'overdose', 'dosage']
            },
            'overdosage': {
                'keywords': ['overdosage', 'overdose', 'over dose'],
                'regex_patterns': [
                    r'^\s*\d*\.?\s*OVERDOSAGE\s*$',
                    r'^\s*OVERDOSAGE\s*$',
                    r'^\s*\d*\.?\s*OVERDOSE\s*$',
                    r'^\s*OVERDOSE\s*$',
                ],
                'stop_keywords': ['storage', 'handling', 'description']
            }
        }
        
        # Pre-compile regex patterns for speed
        self.compiled_patterns = {}
        for section_name, pattern_info in self.section_patterns.items():
            self.compiled_patterns[section_name] = [
                re.compile(pattern, re.IGNORECASE) for pattern in pattern_info['regex_patterns']
            ]
    
    def parse_sections(self, text: str) -> Dict[str, Section]:
        """
        Parse text into structured sections with optimized speed
        
        Args:
            text: The full text of the RSI document
            
        Returns:
            Dictionary mapping section names to Section objects
        """
        lines = text.split('\n')
        sections = {}
        
        # Single pass: find section boundaries and extract content
        section_boundaries = self._find_section_boundaries_optimized(lines)
        
        # Extract content for each section
        for section_name, (start_line, end_line) in section_boundaries.items():
            if start_line < end_line:
                content = '\n'.join(lines[start_line:end_line]).strip()
                if content:
                    confidence = self._calculate_section_confidence_fast(section_name, lines[start_line])
                    sections[section_name] = Section(
                        name=section_name,
                        content=content,
                        start_line=start_line,
                        end_line=end_line,
                        confidence=confidence
                    )
        
        return sections
    
    def _find_section_boundaries_optimized(self, lines: List[str]) -> Dict[str, Tuple[int, int]]:
        """Find section boundaries using optimized single-pass algorithm"""
        boundaries = {}
        current_section = None
        current_start = 0
        
        # Pre-process lines for faster matching
        processed_lines = [(i, line.upper().strip()) for i, line in enumerate(lines)]
        
        for i, line_upper in processed_lines:
            # Check if this line starts a new section
            for section_name, pattern_info in self.section_patterns.items():
                if self._matches_section_pattern_fast(line_upper, section_name):
                    # End the previous section if exists
                    if current_section and current_section not in boundaries:
                        boundaries[current_section] = (current_start, i)
                    
                    # Start new section
                    current_section = section_name
                    current_start = i
                    break
            
            # Check if we've reached the end of current section
            if current_section and self._is_section_end_fast(line_upper, current_section):
                if current_section not in boundaries:
                    boundaries[current_section] = (current_start, i)
                current_section = None
        
        # Handle the last section
        if current_section and current_section not in boundaries:
            boundaries[current_section] = (current_start, len(lines))
        
        return boundaries
    
    def _matches_section_pattern_fast(self, line: str, section_name: str) -> bool:
        """Fast section pattern matching using pre-compiled regex"""
        if section_name not in self.compiled_patterns:
            return False
        
        # Check compiled regex patterns first (fastest)
        for pattern in self.compiled_patterns[section_name]:
            if pattern.match(line):
                return True
        
        # Fallback to keyword matching
        pattern_info = self.section_patterns[section_name]
        for keyword in pattern_info['keywords']:
            if keyword.lower() in line.lower():
                return True
        
        return False
    
    def _is_section_end_fast(self, line: str, current_section: str) -> bool:
        """Fast section end detection"""
        if current_section in self.section_patterns:
            stop_keywords = self.section_patterns[current_section]['stop_keywords']
            for keyword in stop_keywords:
                if keyword.lower() in line.lower():
                    return True
        
        # Check if line starts with a number (likely next section)
        if re.match(r'^\s*\d+\.?\s*[A-Z]', line):
            return True
        
        return False
    
    def _calculate_section_confidence_fast(self, section_name: str, first_line: str) -> float:
        """Fast confidence calculation"""
        if section_name not in self.compiled_patterns:
            return 0.0
        
        # Check compiled regex patterns (highest confidence)
        for pattern in self.compiled_patterns[section_name]:
            if pattern.match(first_line, re.IGNORECASE):
                return 0.9
        
        # Check keyword patterns
        pattern_info = self.section_patterns[section_name]
        for keyword in pattern_info['keywords']:
            if keyword.lower() in first_line.lower():
                return 0.7
        
        return 0.5
    
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
