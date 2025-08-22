"""
Fast Comparison Engine Module for RSI Comparison Tool
Lightning-fast document comparison with high accuracy
"""

import difflib
from fuzzywuzzy import fuzz, process
import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComparisonResult:
    """Represents the result of comparing two sections"""
    section_name: str
    similarity_score: float
    missing_content: List[str]
    present_content: List[str]
    comparison_method: str
    details: Dict[str, Any]

class Section:
    """Represents a section in an RSI document"""
    def __init__(self, name: str, content: str, start_line: int, end_line: int, confidence: float):
        self.name = name
        self.content = content
        self.start_line = start_line
        self.end_line = end_line
        self.confidence = confidence

class ComparisonEngine:
    """Ultra-fast RSI comparison engine"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        # Pre-compile common patterns for speed
        self.sentence_splitter = re.compile(r'[.!?]+\s+')
        self.word_extractor = re.compile(r'\b\w+\b')
        self.number_pattern = re.compile(r'\d+')
        
        # Cache for word frequency analysis
        self._word_cache = {}
    
    def compare_documents(self, comparator_sections: Dict[str, Section], 
                         our_sections: Dict[str, Section]) -> Dict[str, ComparisonResult]:
        """Lightning-fast document comparison"""
        results = {}
        
        # Handle edge cases quickly
        if not comparator_sections and not our_sections:
            return {'no_content': self._create_empty_result()}
        
        if not comparator_sections:
            return {f"extra_{name}": self._create_extra_section_result(name, section) 
                   for name, section in our_sections.items()}
        
        if not our_sections:
            return {name: self._create_missing_section_result(name, section) 
                   for name, section in comparator_sections.items()}
        
        # Fast section matching and comparison
        section_matches = self._fast_section_matching(comparator_sections, our_sections)
        
        # Compare matched sections
        for comp_name, our_name in section_matches.items():
            comparator_section = comparator_sections[comp_name]
            our_section = our_sections[our_name]
            results[comp_name] = self._fast_compare_sections(comparator_section, our_section)
        
        # Handle unmatched sections
        unmatched_comp = set(comparator_sections.keys()) - set(section_matches.keys())
        unmatched_our = set(our_sections.keys()) - set(section_matches.values())
        
        for section_name in unmatched_comp:
            results[section_name] = self._create_missing_section_result(
                section_name, comparator_sections[section_name])
        
        for section_name in unmatched_our:
            results[f"extra_{section_name}"] = self._create_extra_section_result(
                section_name, our_sections[section_name])
        
        return results
    
    def _fast_section_matching(self, comp_sections: Dict[str, Section], 
                              our_sections: Dict[str, Section]) -> Dict[str, str]:
        """Fast fuzzy matching of section names with SmPC-aware logic"""
        matches = {}
        our_names = list(our_sections.keys())
        
        # SmPC section equivalents mapping
        section_equivalents = {
            'therapeutic_indications': ['indications', 'therapeutic_indications'],
            'posology_administration': ['posology', 'posology_administration', 'dosage'],
            'contraindications': ['contraindications'],
            'special_warnings_precautions': ['warnings_precautions', 'special_warnings_precautions', 'warnings', 'precautions'],
            'interactions_medicinal_products': ['interactions', 'interactions_medicinal_products', 'drug_interactions'],
            'fertility_pregnancy_lactation': ['fertility_pregnancy', 'fertility_pregnancy_lactation', 'pregnancy'],
            'effects_ability_drive_machines': ['driving_machines', 'effects_ability_drive_machines'],
            'undesirable_effects': ['undesirable_effects', 'adverse_reactions'],
            'overdose': ['overdose', 'overdosage']
        }
        
        for comp_name in comp_sections.keys():
            # Try exact match first
            if comp_name in our_sections:
                matches[comp_name] = comp_name
                continue
            
            # Try equivalent section names
            matched = False
            if comp_name in section_equivalents:
                for equivalent in section_equivalents[comp_name]:
                    if equivalent in our_names:
                        matches[comp_name] = equivalent
                        our_names.remove(equivalent)
                        matched = True
                        break
            
            if not matched:
                # Also check reverse mapping
                for our_name in our_names:
                    if our_name in section_equivalents:
                        if comp_name in section_equivalents[our_name]:
                            matches[comp_name] = our_name
                            our_names.remove(our_name)
                            matched = True
                            break
            
            if not matched:
                # Fast fuzzy matching as fallback
                best_match = process.extractOne(comp_name, our_names, scorer=fuzz.ratio)
                if best_match and best_match[1] > 60:  # 60% similarity threshold
                    matches[comp_name] = best_match[0]
                    our_names.remove(best_match[0])  # Avoid duplicate matches
        
        return matches
    
    def _fast_compare_sections(self, comparator_section: Section, our_section: Section) -> ComparisonResult:
        """Ultra-fast section comparison using optimized algorithms"""
        comp_text = self._normalize_text(comparator_section.content)
        our_text = self._normalize_text(our_section.content)
        
        # Quick length check
        if len(comp_text) < 10 and len(our_text) < 10:
            return self._create_minimal_result(comparator_section.name, 0.8 if comp_text == our_text else 0.2)
        
        # Fast similarity check
        similarity = self._calculate_fast_similarity(comp_text, our_text)
        
        if similarity > 0.95:
            # Very similar, minimal analysis needed
            return ComparisonResult(
                section_name=comparator_section.name,
                similarity_score=similarity,
                missing_content=[],
                present_content=[comp_text[:100] + '...'] if len(comp_text) > 100 else [comp_text],
                comparison_method='high_similarity',
                details={'fast_match': True}
            )
        
        # More detailed analysis for lower similarity
        missing, present = self._find_missing_content_fast(comp_text, our_text)
        
        return ComparisonResult(
            section_name=comparator_section.name,
            similarity_score=similarity,
            missing_content=missing,
            present_content=present,
            comparison_method='fast_analysis',
            details={'similarity_method': 'word_overlap'}
        )
    
    def _calculate_fast_similarity(self, text1: str, text2: str) -> float:
        """Fast similarity calculation using word overlap"""
        if not text1 or not text2:
            return 0.0
        
        # Get word sets for fast comparison
        words1 = set(self._get_words_fast(text1))
        words2 = set(self._get_words_fast(text2))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity (fast)
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # Boost with fuzzy matching for final score
        if jaccard > 0.3:  # Only if reasonable overlap
            fuzzy_score = fuzz.ratio(text1[:500], text2[:500]) / 100.0  # Limit length for speed
            return (jaccard + fuzzy_score) / 2.0
        
        return jaccard
    
    def _find_missing_content_fast(self, comp_text: str, our_text: str) -> Tuple[List[str], List[str]]:
        """Fast missing content detection"""
        comp_sentences = self._split_sentences_fast(comp_text)
        our_sentences = self._split_sentences_fast(our_text)
        
        if len(comp_sentences) > 20:  # Too many sentences, use sampling
            comp_sentences = comp_sentences[::max(1, len(comp_sentences)//10)]  # Sample every nth
        
        missing = []
        present = []
        
        our_text_lower = our_text.lower()
        
        for sentence in comp_sentences[:10]:  # Limit to first 10 sentences for speed
            sentence_clean = sentence.strip()
            if len(sentence_clean) < 20:  # Skip very short sentences
                continue
            
            # Fast keyword matching
            key_words = self._extract_key_words(sentence_clean)
            word_match_count = sum(1 for word in key_words if word.lower() in our_text_lower)
            
            if word_match_count / max(len(key_words), 1) > 0.6:  # 60% of key words found
                present.append(sentence_clean)
            else:
                missing.append(sentence_clean)
        
        return missing[:5], present[:3]  # Limit results for performance
    
    def _split_sentences_fast(self, text: str) -> List[str]:
        """Fast sentence splitting"""
        if not text:
            return []
        
        # Simple sentence split - much faster than complex parsing
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _extract_key_words(self, text: str) -> List[str]:
        """Extract key words for comparison"""
        # Remove common words and extract meaningful terms
        words = self.word_extractor.findall(text.lower())
        
        # Filter out very common words and short words
        key_words = [w for w in words if len(w) > 3 and w not in {
            'this', 'that', 'with', 'have', 'they', 'been', 'their', 'said', 'each', 'which',
            'them', 'than', 'many', 'some', 'time', 'very', 'when', 'much', 'from', 'about'
        }]
        
        return key_words[:10]  # Limit for speed
    
    def _get_words_fast(self, text: str) -> List[str]:
        """Fast word extraction with caching"""
        text_hash = hash(text[:200])  # Hash first 200 chars for speed
        if text_hash in self._word_cache:
            return self._word_cache[text_hash]
        
        words = [w.lower() for w in self.word_extractor.findall(text) if len(w) > 2]
        self._word_cache[text_hash] = words
        
        # Limit cache size
        if len(self._word_cache) > 100:
            self._word_cache.clear()
        
        return words
    
    def _normalize_text(self, text: str) -> str:
        """Fast text normalization"""
        if not text:
            return ""
        
        # Fast normalization - only essential changes
        text = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove numbers that might vary between documents
        text = self.number_pattern.sub('NUM', text)
        return text
    
    def _create_empty_result(self) -> ComparisonResult:
        """Create result for empty comparison"""
        return ComparisonResult(
            section_name='no_content',
            similarity_score=1.0,
            missing_content=[],
            present_content=[],
            comparison_method='empty',
            details={'note': 'No content to compare'}
        )
    
    def _create_minimal_result(self, section_name: str, similarity: float) -> ComparisonResult:
        """Create minimal result for short content"""
        return ComparisonResult(
            section_name=section_name,
            similarity_score=similarity,
            missing_content=[] if similarity > 0.5 else ['Content too short to analyze'],
            present_content=['Short content'] if similarity > 0.5 else [],
            comparison_method='minimal',
            details={'note': 'Very short content'}
        )
    
    def _create_missing_section_result(self, section_name: str, comparator_section: Section) -> ComparisonResult:
        """Create result for missing section"""
        # Extract first few sentences as missing content
        content = comparator_section.content
        sentences = self._split_sentences_fast(content)
        missing_items = sentences[:3] if sentences else [content[:200] + '...' if len(content) > 200 else content]
        
        return ComparisonResult(
            section_name=section_name,
            similarity_score=0.0,
            missing_content=missing_items,
            present_content=[],
            comparison_method='missing_section',
            details={'reason': 'Section not found in our RSI'}
        )
    
    def _create_extra_section_result(self, section_name: str, our_section: Section) -> ComparisonResult:
        """Create result for extra section"""
        content = our_section.content
        sentences = self._split_sentences_fast(content)
        present_items = sentences[:2] if sentences else [content[:100] + '...' if len(content) > 100 else content]
        
        return ComparisonResult(
            section_name=f"extra_{section_name}",
            similarity_score=1.0,
            missing_content=[],
            present_content=present_items,
            comparison_method='extra_section',
            details={'reason': 'Section not present in comparator RSI'}
        )
    
    def generate_summary_report(self, comparison_results: Dict[str, ComparisonResult]) -> Dict[str, Any]:
        """Generate fast summary report"""
        if not comparison_results:
            return {
                'overall_similarity': 0.0,
                'total_sections_compared': 0,
                'sections_with_issues': 0,
                'missing_sections': [],
                'sections_needing_attention': []
            }
        
        # Fast summary calculation
        similarities = []
        missing_sections = []
        sections_needing_attention = []
        
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
                
            similarities.append(result.similarity_score)
            
            if result.similarity_score < 0.1:
                missing_sections.append(section_name)
            elif result.similarity_score < self.similarity_threshold:
                sections_needing_attention.append({
                    'section': section_name,
                    'similarity_score': result.similarity_score,
                    'issues': len(result.missing_content)
                })
        
        overall_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        sections_with_issues = len([s for s in similarities if s < self.similarity_threshold])
        
        return {
            'overall_similarity': overall_similarity,
            'total_sections_compared': len(similarities),
            'sections_with_issues': sections_with_issues,
            'missing_sections': missing_sections,
            'sections_needing_attention': sections_needing_attention
        }