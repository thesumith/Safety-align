"""
Fast Section Parser Module for RSI Comparison Tool
High-performance section detection with improved accuracy for real RSI documents
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
    """Ultra-fast RSI section parser with improved pattern matching"""
    
    def __init__(self):
        # Complete SmPC sections with enhanced patterns for comprehensive detection
        self.section_patterns = {
            # Basic product information sections
            'name_composition': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\s*name\s+of.*medicinal.*product',
                    r'(?i)^\s*\d*\.?\s*qualitative.*quantitative.*composition',
                    r'(?i)^\s*1\.?\s*name.*medicinal',
                    r'(?i)^\s*2\.?\s*qualitative.*composition'
                ],
                'keywords': ['name of the medicinal product', 'qualitative and quantitative composition', 
                           'active substance', 'excipients'],
                'min_chars': 50
            },
            'pharmaceutical_form': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\s*pharmaceutical\s+form',
                    r'(?i)^\s*3\.?\s*pharmaceutical.*form'
                ],
                'keywords': ['pharmaceutical form', 'film-coated tablets', 'capsules', 'solution'],
                'min_chars': 30
            },
            'clinical_particulars': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\s*clinical\s+particulars',
                    r'(?i)^\s*4\.?\s*clinical.*particulars'
                ],
                'keywords': ['clinical particulars'],
                'min_chars': 50
            },
            
            # Main therapeutic sections (the core SmPC sections you mentioned)
            'therapeutic_indications': {
                'patterns': [
                    r'(?i)^\s*4\.1\.?\s*therapeutic\s+indications?',
                    r'(?i)^\s*4\.1\.?\s*indications?',
                    r'(?i)^\s*\d*\.?\d*\.?\s*therapeutic\s+indications?',
                    r'(?i)^\s*\d*\.?\s*indications?',
                    r'(?i)^\s*indications?\s*$'
                ],
                'keywords': ['therapeutic indications', 'indications', 'treatment of', 'indicated for', 'what is used for', 'used to treat'],
                'min_chars': 50
            },
            'posology_administration': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\d*\.?\s*posology.*method.*administration',
                    r'(?i)^\s*4\.2\.?\s*posology.*administration',
                    r'(?i)^\s*\d*\.?\s*dosage.*administration',
                    r'(?i)^\s*posology.*administration'
                ],
                'keywords': ['posology and method of administration', 'dosage', 'recommended dose', 'administration', 'how to take', 'dose'],
                'min_chars': 50
            },
            'contraindications': {
                'patterns': [
                    r'(?i)^\s*4\.3\.?\s*contraindications?',
                    r'(?i)^\s*\d*\.?\d*\.?\s*contraindications?',
                    r'(?i)^\s*contraindications?\s*$'
                ],
                'keywords': ['contraindications', 'hypersensitivity', 'should not be used'],
                'min_chars': 20
            },
            'special_warnings_precautions': {
                'patterns': [
                    r'(?i)^\s*4\.4\.?\s*special\s+warnings?.*precautions?.*use',
                    r'(?i)^\s*4\.4\.?\s*special.*warnings?.*precautions?',
                    r'(?i)^\s*\d*\.?\d*\.?\s*special\s+warnings?.*precautions?.*use',
                    r'(?i)^\s*\d*\.?\s*warnings?.*precautions?',
                    r'(?i)^\s*special.*warnings?.*precautions?'
                ],
                'keywords': ['special warnings and precautions for use', 'warnings', 'precautions', 'caution'],
                'min_chars': 50
            },
            'interactions_medicinal_products': {
                'patterns': [
                    r'(?i)^\s*4\.5\.?\s*interaction.*other.*medicinal.*products?',
                    r'(?i)^\s*4\.5\.?\s*interaction.*medicinal.*products?',
                    r'(?i)^\s*\d*\.?\d*\.?\s*interaction.*other.*medicinal.*products?',
                    r'(?i)^\s*\d*\.?\s*drug.*interactions?',
                    r'(?i)^\s*interactions?.*other.*forms'
                ],
                'keywords': ['interaction with other medicinal products', 'drug interactions', 'concomitant use'],
                'min_chars': 30
            },
            'fertility_pregnancy_lactation': {
                'patterns': [
                    r'(?i)^\s*4\.6\.?\s*fertility.*pregnancy.*lactation',
                    r'(?i)^\s*4\.6\.?\s*pregnancy.*lactation',
                    r'(?i)^\s*\d*\.?\d*\.?\s*fertility.*pregnancy.*lactation',
                    r'(?i)^\s*\d*\.?\s*pregnancy.*lactation',
                    r'(?i)^\s*fertility.*pregnancy'
                ],
                'keywords': ['fertility, pregnancy and lactation', 'pregnancy', 'lactation', 'women of childbearing potential'],
                'min_chars': 30
            },
            'effects_ability_drive_machines': {
                'patterns': [
                    r'(?i)^\s*4\.7\.?\s*effects?.*ability.*drive.*use.*machines?',
                    r'(?i)^\s*4\.7\.?\s*effects?.*ability.*drive',
                    r'(?i)^\s*\d*\.?\d*\.?\s*effects?.*ability.*drive.*use.*machines?',
                    r'(?i)^\s*\d*\.?\s*driving.*machines?',
                    r'(?i)^\s*ability.*drive.*machines?'
                ],
                'keywords': ['effects on ability to drive and use machines', 'driving', 'operating machinery'],
                'min_chars': 20
            },
            'undesirable_effects': {
                'patterns': [
                    r'(?i)^\s*4\.8\.?\s*undesirable\s+effects?',
                    r'(?i)^\s*4\.8\.?\s*undesirable.*effects?',
                    r'(?i)^\s*\d*\.?\d*\.?\s*undesirable\s+effects?',
                    r'(?i)^\s*\d*\.?\s*adverse.*reactions?',
                    r'(?i)^\s*\d*\.?\s*side\s+effects?'
                ],
                'keywords': ['undesirable effects', 'adverse reactions', 'side effects', 'adverse events'],
                'min_chars': 50
            },
            'overdose': {
                'patterns': [
                    r'(?i)^\s*4\.9\.?\s*overdose',
                    r'(?i)^\s*4\.9\.?\s*overdosage',
                    r'(?i)^\s*\d*\.?\d*\.?\s*overdose',
                    r'(?i)^\s*\d*\.?\s*overdosage',
                    r'(?i)^\s*overdose\s*$'
                ],
                'keywords': ['overdose', 'overdosage', 'symptoms of overdose', 'treatment of overdose'],
                'min_chars': 20
            },
            
            # Additional SmPC sections for completeness
            'pharmacological_properties': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\s*pharmacological\s+properties',
                    r'(?i)^\s*5\.?\s*pharmacological.*properties'
                ],
                'keywords': ['pharmacological properties', 'pharmacodynamic properties', 'pharmacokinetic properties'],
                'min_chars': 100
            },
            'pharmaceutical_particulars': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\s*pharmaceutical\s+particulars',
                    r'(?i)^\s*6\.?\s*pharmaceutical.*particulars'
                ],
                'keywords': ['pharmaceutical particulars', 'incompatibilities', 'shelf life', 'storage conditions'],
                'min_chars': 100
            },
            'marketing_authorisation': {
                'patterns': [
                    r'(?i)^\s*\d*\.?\s*marketing.*authorisation',
                    r'(?i)^\s*7\.?\s*marketing.*authorisation.*holder'
                ],
                'keywords': ['marketing authorisation holder', 'licence holder'],
                'min_chars': 50
            }
        }
        
        # Compile patterns for speed
        self.compiled_patterns = {}
        for section_name, pattern_info in self.section_patterns.items():
            self.compiled_patterns[section_name] = [
                re.compile(pattern) for pattern in pattern_info['patterns']
            ]
    
    def parse_sections(self, text: str) -> Dict[str, Section]:
        """Ultra-fast section parsing with aggressive SmPC detection for the 8 core sections"""
        if not text.strip():
            return {}
        
        lines = text.split('\n')
        sections = {}
        
        # First pass: Detect the 8 core SmPC sections with proper boundary handling
        core_sections = self._detect_eight_core_sections(lines)
        sections.update(core_sections)
        
        # Second pass: SmPC-specific numbered sections (4.1, 4.2, etc.) for any missed sections
        if len(sections) < 5:
            smpc_sections = self._detect_smpc_numbered_sections(lines)
            # Only add sections that we don't already have
            for name, section in smpc_sections.items():
                if name not in sections:
                    sections[name] = section
        
        # Third pass: General numbered sections for any still missing
        if len(sections) < 5:
            numbered_sections = self._detect_numbered_sections(lines)
            for name, section in numbered_sections.items():
                if name not in sections:
                    sections[name] = section
        
        # Fourth pass: Aggressive keyword-based detection
        keyword_sections = self._detect_keyword_sections_aggressive(lines, sections.keys())
        sections.update(keyword_sections)
        
        # Fifth pass: Content-based detection for missing critical sections
        if len(sections) < 8:  # Target the 8 core sections
            content_sections = self._detect_content_sections_targeted(text, sections.keys())
            sections.update(content_sections)
        
        # Sixth pass: Ultra-aggressive detection for still missing sections
        if len(sections) < 8:
            ultra_aggressive_sections = self._ultra_aggressive_detection(text, sections.keys())
            sections.update(ultra_aggressive_sections)
        
        return sections
    
    def _detect_eight_core_sections(self, lines: List[str]) -> Dict[str, Section]:
        """Detect the 8 core SmPC sections with proper boundary handling"""
        sections = {}
        
        # Define the 8 core sections with their exact section numbers
        core_sections = {
            '4.1': 'therapeutic_indications',
            '4.3': 'contraindications',
            '4.4': 'special_warnings_precautions',
            '4.5': 'interactions_medicinal_products',
            '4.6': 'fertility_pregnancy_lactation',
            '4.7': 'effects_ability_drive_machines',
            '4.8': 'undesirable_effects',
            '4.9': 'overdose'
        }
        
        # Find all potential section headers by looking for exact section numbers
        section_candidates = []
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Look for exact section numbers (4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9)
            for section_number, section_name in core_sections.items():
                # Create specific pattern for each section number
                section_pattern = rf'^\s*{re.escape(section_number)}\.?\s+'
                
                if re.match(section_pattern, line_clean):
                    # Double-check with the section-specific patterns to ensure content match
                    if section_name in self.section_patterns:
                        for pattern in self.compiled_patterns[section_name]:
                            if pattern.search(line_clean):
                                section_candidates.append((i, section_name, line_clean, section_number))
                                break
        
        # Remove duplicates and sort by line number
        seen_sections = set()
        unique_candidates = []
        for line_num, section_name, header, section_number in section_candidates:
            if section_name not in seen_sections:
                unique_candidates.append((line_num, section_name, header, section_number))
                seen_sections.add(section_name)
        
        # Sort by line number to maintain document order
        unique_candidates.sort(key=lambda x: x[0])
        
        # Extract content with proper boundary handling
        for i, (start_line, section_name, header, section_number) in enumerate(unique_candidates):
            # Find the end of this section
            if i + 1 < len(unique_candidates):
                # Next section starts where this one ends
                end_line = unique_candidates[i + 1][0]
            else:
                # This is the last section, find a reasonable end point
                end_line = self._find_section_end_smart(lines, start_line, section_name)
            
            # Extract content (excluding the header line)
            content_lines = lines[start_line + 1:end_line]
            content = '\n'.join(content_lines).strip()
            
            # Check minimum content requirements
            min_chars = self.section_patterns[section_name].get('min_chars', 20)
            if len(content) >= min_chars:
                sections[section_name] = Section(
                    name=section_name,
                    content=content,
                    start_line=start_line + 1,
                    end_line=end_line,
                    confidence=0.98  # Very high confidence for exact number match
                )
                
                # Log the successful detection with section number
                logger.info(f"Detected section {section_number} ({section_name}) at lines {start_line+1}-{end_line}")
        
        return sections
    
    def _find_section_end_smart(self, lines: List[str], start_line: int, current_section: str) -> int:
        """Smart section end detection that looks for the next core section or document end"""
        
        # Define the 8 core sections
        core_sections = [
            'therapeutic_indications', 'contraindications', 'special_warnings_precautions',
            'interactions_medicinal_products', 'fertility_pregnancy_lactation',
            'effects_ability_drive_machines', 'undesirable_effects', 'overdose'
        ]
        
        # Look ahead for the next section
        for i in range(start_line + 3, min(len(lines), start_line + 200)):  # Increased search range
            line = lines[i].strip()
            if not line:
                continue
            
            # Check if this line matches any of the core section patterns
            for other_section in core_sections:
                if other_section != current_section and other_section in self.section_patterns:
                    for pattern in self.compiled_patterns[other_section]:
                        if pattern.search(line):
                            return i
            
            # Also check for other numbered section patterns that might indicate document structure
            if re.match(r'^\s*\d+\.\d*\.?\s+[A-Z]', line):
                # This looks like a new numbered section
                return i
            
            # Check for major section breaks (like "5. PHARMACOLOGICAL PROPERTIES")
            if re.match(r'^\s*[5-9]\.\s+[A-Z][A-Z\s]+$', line):
                return i
        
        # If no clear end found, return a reasonable default
        return min(len(lines), start_line + 100)
    
    def _detect_smpc_numbered_sections(self, lines: List[str]) -> Dict[str, Section]:
        """Detect SmPC-specific numbered sections (4.1, 4.2, 4.3, etc.)"""
        sections = {}
        section_starts = []
        
        # Look for SmPC section patterns
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Check for the specific SmPC section numbers (4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9)
            valid_section_numbers = ['4.1', '4.3', '4.4', '4.5', '4.6', '4.7', '4.8', '4.9']
            section_found = False
            
            for section_num in valid_section_numbers:
                section_pattern = rf'^\s*{re.escape(section_num)}\.?\s+'
                if re.match(section_pattern, line_clean):
                    for section_name, pattern_info in self.section_patterns.items():
                        for pattern in self.compiled_patterns[section_name]:
                            if pattern.search(line_clean):
                                section_starts.append((i, section_name, line_clean))
                                section_found = True
                                break
                    if section_found:
                        break  # Found a match, no need to check other numbers
            
            # Also check for other numbered sections (1., 2., 3., etc.) if no specific section found
            # BUT exclude 4.2 as we only want 4.1, 4.3-4.9
            if not section_found and re.match(r'^\s*[1-9]\d*\.?\s+', line_clean):
                # Skip section 4.2 (posology) as it's not in our target list
                if not re.match(r'^\s*4\.2\.?\s+', line_clean):
                    for section_name, pattern_info in self.section_patterns.items():
                        for pattern in self.compiled_patterns[section_name]:
                            if pattern.search(line_clean):
                                section_starts.append((i, section_name, line_clean))
                                break
        
        # Extract content between section headers
        for i, (start_line, section_name, header) in enumerate(section_starts):
            end_line = section_starts[i + 1][0] if i + 1 < len(section_starts) else len(lines)
            
            content_lines = lines[start_line + 1:end_line]
            content = '\n'.join(content_lines).strip()
            
            if len(content) >= self.section_patterns[section_name].get('min_chars', 20):
                sections[section_name] = Section(
                    name=section_name,
                    content=content,
                    start_line=start_line + 1,
                    end_line=end_line,
                    confidence=0.9
                )
        
        return sections
    
    def _detect_numbered_sections(self, lines: List[str]) -> Dict[str, Section]:
        """Detect numbered sections (e.g., '4.1 Indications', '4.2 Posology')"""
        sections = {}
        section_starts = []
        
        # Find section headers
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Look for numbered headers
            if re.match(r'^\d+\.?\d*\.?\s+', line_clean):
                for section_name, pattern_info in self.section_patterns.items():
                    for pattern in self.compiled_patterns[section_name]:
                        if pattern.search(line_clean):
                            section_starts.append((i, section_name, line_clean))
                            break
        
        # Extract content between headers
        for i, (start_line, section_name, header) in enumerate(section_starts):
            end_line = section_starts[i + 1][0] if i + 1 < len(section_starts) else len(lines)
            
            content_lines = lines[start_line + 1:end_line]
            content = '\n'.join(content_lines).strip()
            
            if len(content) >= self.section_patterns[section_name].get('min_chars', 20):
                sections[section_name] = Section(
                    name=section_name,
                    content=content,
                    start_line=start_line + 1,
                    end_line=end_line,
                    confidence=0.9
                )
        
        return sections
    
    def _detect_keyword_sections_aggressive(self, lines: List[str], existing_sections: set) -> Dict[str, Section]:
        """Aggressive keyword-based section detection for SmPC"""
        sections = {}
        text_lower = '\n'.join(lines).lower()
        
        # Priority order for SmPC sections (the 8 target sections: 4.1, 4.3-4.9)
        priority_sections = [
            'therapeutic_indications',      # 4.1 Therapeutic indications
            'contraindications',            # 4.3 Contraindications
            'special_warnings_precautions', # 4.4 Special warnings and precautions for use
            'interactions_medicinal_products', # 4.5 Interaction with other medicinal products
            'fertility_pregnancy_lactation', # 4.6 Fertility, pregnancy and lactation
            'effects_ability_drive_machines', # 4.7 Effects on ability to drive and use machines
            'undesirable_effects',          # 4.8 Undesirable effects
            'overdose'                      # 4.9 Overdose
        ]
        
        # First, try to find priority sections (the 8 target sections: 4.1, 4.3-4.9)
        for section_name in priority_sections:
            if section_name in existing_sections:
                continue
                
            pattern_info = self.section_patterns[section_name]
            
            # Look for keywords with context
            for keyword in pattern_info['keywords']:
                keyword_lower = keyword.lower()
                
                # Find all occurrences of the keyword
                start_pos = 0
                while True:
                    pos = text_lower.find(keyword_lower, start_pos)
                    if pos == -1:
                        break
                    
                    # Check if this is likely a section header (near line start)
                    line_start = text_lower.rfind('\n', 0, pos) + 1
                    chars_before = pos - line_start
                    
                    if chars_before < 20:  # Keyword is near start of line
                        lines_before = text_lower[:pos].count('\n')
                        start_line = max(0, lines_before - 1)
                        
                        # Find next section or end of document
                        end_line = self._find_section_end(lines, start_line, section_name)
                        
                        if end_line > start_line + 2:
                            content = '\n'.join(lines[start_line + 1:end_line]).strip()
                            
                            if len(content) >= pattern_info.get('min_chars', 20):
                                sections[section_name] = Section(
                                    name=section_name,
                                    content=content,
                                    start_line=start_line + 1,
                                    end_line=end_line,
                                    confidence=0.8
                                )
                                break
                    
                    start_pos = pos + 1
                
                if section_name in sections:
                    break
        
        # Then try other sections
        for section_name, pattern_info in self.section_patterns.items():
            if section_name in existing_sections or section_name in sections:
                continue
            
            # Skip posology_administration as it's not in our target 8 sections
            if section_name == 'posology_administration':
                continue
            
            for keyword in pattern_info['keywords']:
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    pos = text_lower.find(keyword_lower)
                    lines_before = text_lower[:pos].count('\n')
                    start_line = max(0, lines_before)
                    
                    end_line = min(len(lines), start_line + 30)
                    content = '\n'.join(lines[start_line + 1:end_line]).strip()
                    
                    if len(content) >= pattern_info.get('min_chars', 20):
                        sections[section_name] = Section(
                            name=section_name,
                            content=content,
                            start_line=start_line + 1,
                            end_line=end_line,
                            confidence=0.6
                        )
                        break
        
        return sections
    
    def _find_section_end(self, lines: List[str], start_line: int, current_section: str) -> int:
        """Find where a section ends by looking for next section header"""
        for i in range(start_line + 3, min(len(lines), start_line + 100)):
            line = lines[i].strip()
            
            # Check if this line looks like a new section header
            if re.match(r'^\s*\d+\.\d*\.?\s+[A-Z]', line):
                return i
            
            # Check for section keywords that indicate new section
            for other_section, pattern_info in self.section_patterns.items():
                if other_section != current_section:
                    for keyword in pattern_info['keywords']:
                        if keyword.lower() in line.lower() and len(line) < 100:
                            return i
        
        return min(len(lines), start_line + 50)
    
    def _detect_content_sections_targeted(self, text: str, existing_sections: set) -> Dict[str, Section]:
        """Targeted content detection for missing critical SmPC sections"""
        sections = {}
        text_lower = text.lower()
        
        # Target missing critical sections (the 8 sections: 4.1, 4.3-4.9)
        critical_sections = [
            'therapeutic_indications',      # 4.1 Therapeutic indications
            'contraindications',            # 4.3 Contraindications
            'special_warnings_precautions', # 4.4 Special warnings and precautions for use
            'interactions_medicinal_products', # 4.5 Interaction with other medicinal products
            'fertility_pregnancy_lactation', # 4.6 Fertility, pregnancy and lactation
            'effects_ability_drive_machines', # 4.7 Effects on ability to drive and use machines
            'undesirable_effects',          # 4.8 Undesirable effects
            'overdose'                      # 4.9 Overdose
        ]
        
        missing_critical = [s for s in critical_sections if s not in existing_sections]
        
        if not missing_critical:
            return sections
        
        # Split text into meaningful chunks
        chunks = self._split_text_intelligently(text)
        
        for chunk_start, chunk_text in chunks:
            chunk_lower = chunk_text.lower()
            
            for section_name in missing_critical:
                if section_name in sections:  # Already found
                    continue
                    
                pattern_info = self.section_patterns[section_name]
                score = 0
                
                # Score based on keyword presence
                for keyword in pattern_info['keywords']:
                    if keyword.lower() in chunk_lower:
                        score += len(keyword) * 2  # Weight by keyword length
                
                # Bonus for multiple keywords
                keyword_count = sum(1 for kw in pattern_info['keywords'] if kw.lower() in chunk_lower)
                if keyword_count > 1:
                    score += keyword_count * 10
                
                # Must meet minimum threshold and length
                if score > 20 and len(chunk_text) >= pattern_info.get('min_chars', 50):
                    sections[section_name] = Section(
                        name=section_name,
                        content=chunk_text.strip(),
                        start_line=chunk_start,
                        end_line=chunk_start + len(chunk_text.split('\n')),
                        confidence=min(0.8, score / 100.0)
                    )
        
        return sections
    
    def _split_text_intelligently(self, text: str) -> List[Tuple[int, str]]:
        """Split text into meaningful chunks based on content structure"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_start = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this might be a section boundary
            is_boundary = (
                re.match(r'^\s*\d+\.\d*\.?\s+[A-Z]', line_stripped) or  # Numbered section
                (len(line_stripped) < 100 and 
                 any(kw in line_stripped.lower() for section_info in self.section_patterns.values() 
                     for kw in section_info['keywords'][:2]))  # Contains section keywords
            )
            
            if is_boundary and current_chunk and len('\n'.join(current_chunk)) > 100:
                # Save current chunk
                chunks.append((current_start, '\n'.join(current_chunk)))
                current_chunk = []
                current_start = i
            
            current_chunk.append(line)
            
            # Also create chunks for very long sections
            if len(current_chunk) > 100:  # Max 100 lines per chunk
                chunks.append((current_start, '\n'.join(current_chunk)))
                current_chunk = []
                current_start = i + 1
        
        # Add final chunk
        if current_chunk:
            chunks.append((current_start, '\n'.join(current_chunk)))
        
        return chunks
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size // 10):  # Overlap for continuity
            chunk_words = words[i:i + chunk_size // 5]  # Average 5 chars per word
            if chunk_words:
                chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def _ultra_aggressive_detection(self, text: str, existing_sections: set) -> Dict[str, Section]:
        """Ultra-aggressive section detection with very low thresholds"""
        sections = {}
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Target the 9 core SmPC sections with very loose matching
        target_sections = {
            'contraindications': ['contraindic', 'hypersensitivity', 'allerg', 'should not', 'do not use'],
            'interactions_medicinal_products': ['interaction', 'concomitant', 'drug', 'medicinal', 'co-administration'],
            'effects_ability_drive_machines': ['drive', 'driving', 'machine', 'ability', 'operate'],
            'overdose': ['overdos', 'overdo', 'too much', 'excess', 'antidote'],
            'therapeutic_indications': ['indicat', 'treatment', 'used for', 'therapy'],
            'posology_administration': ['dosage', 'dose', 'posology', 'administration', 'how to'],
            'special_warnings_precautions': ['warning', 'precaution', 'caution', 'careful'],
            'fertility_pregnancy_lactation': ['pregnan', 'lactation', 'fertility', 'breast', 'women'],
            'undesirable_effects': ['adverse', 'undesirable', 'side effect', 'reaction']
        }
        
        for section_name, keywords in target_sections.items():
            if section_name in existing_sections:
                continue
            
            best_match_pos = -1
            best_score = 0
            
            # Search for any of the keywords
            for keyword in keywords:
                pos = text_lower.find(keyword)
                if pos != -1:
                    # Score based on keyword strength and position
                    score = len(keyword) + (1000 - pos // 100)  # Prefer earlier occurrences
                    if score > best_score:
                        best_score = score
                        best_match_pos = pos
            
            if best_match_pos != -1 and best_score > 5:  # Very low threshold
                # Find line number
                lines_before = text_lower[:best_match_pos].count('\n')
                start_line = max(0, lines_before - 1)
                
                # Take a reasonable chunk
                end_line = min(len(lines), start_line + 20)  # Smaller chunks
                content = '\n'.join(lines[start_line:end_line]).strip()
                
                if len(content) > 30:  # Very low content threshold
                    sections[section_name] = Section(
                        name=section_name,
                        content=content,
                        start_line=start_line,
                        end_line=end_line,
                        confidence=0.5  # Lower confidence but still valid
                    )
        
        return sections
    
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
