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
        """Comprehensive document comparison ensuring all sections are analyzed in specified order"""
        results = {}
        
        # Define the specific order for SmPC sections as requested
        section_order = [
            'therapeutic_indications',      # 4.1 Therapeutic indications
            'contraindications',            # 4.3 Contraindications
            'special_warnings_precautions', # 4.4 Special warnings and precautions for use
            'interactions_medicinal_products', # 4.5 Interaction with other medicinal products
            'fertility_pregnancy_lactation', # 4.6 Fertility, pregnancy and lactation
            'effects_ability_drive_machines', # 4.7 Effects on ability to drive and use machines
            'undesirable_effects',          # 4.8 Undesirable effects
            'overdose'                      # 4.9 Overdose
        ]
        
        # Handle edge cases quickly
        if not comparator_sections and not our_sections:
            return {'no_content': self._create_empty_result()}
        
        if not comparator_sections:
            return {f"extra_{name}": self._create_extra_section_result(name, section) 
                   for name, section in our_sections.items()}
        
        if not our_sections:
            # Return missing sections in the specified order
            ordered_results = {}
            for section_name in section_order:
                if section_name in comparator_sections:
                    ordered_results[section_name] = self._create_missing_section_result(
                        section_name, comparator_sections[section_name])
            # Add any remaining sections not in the specified order
            for name, section in comparator_sections.items():
                if name not in ordered_results:
                    ordered_results[name] = self._create_missing_section_result(name, section)
            return ordered_results
        
        # Enhanced section matching with content-based fallback
        section_matches = self._comprehensive_section_matching(comparator_sections, our_sections)
        
        # Compare sections in the specified order first
        ordered_results = {}
        processed_sections = set()
        
        for section_name in section_order:
            if section_name in section_matches:
                # Found a matched section
                comp_name = section_name
                our_name = section_matches[section_name]
                comparator_section = comparator_sections[comp_name]
                our_section = our_sections[our_name]
                ordered_results[comp_name] = self._fast_compare_sections(comparator_section, our_section)
                processed_sections.add(comp_name)
            elif section_name in comparator_sections:
                # Section exists in comparator but not matched - try content-based matching
                comp_section = comparator_sections[section_name]
                unmatched_our = set(our_sections.keys()) - set(section_matches.values())
                best_match = self._find_best_content_match(comp_section, unmatched_our, our_sections)
                
                if best_match:
                    our_section = our_sections[best_match]
                    ordered_results[section_name] = self._fast_compare_sections(comp_section, our_section)
                    # Update section_matches to reflect this new match
                    section_matches[section_name] = best_match
                else:
                    # Truly missing section
                    ordered_results[section_name] = self._create_missing_section_result(
                        section_name, comp_section)
                processed_sections.add(section_name)
        
        # Handle remaining sections not in the specified order
        unmatched_comp = set(comparator_sections.keys()) - processed_sections
        unmatched_our = set(our_sections.keys()) - set(section_matches.values())
        
        # Compare remaining matched sections
        for comp_name, our_name in section_matches.items():
            if comp_name not in processed_sections:
                comparator_section = comparator_sections[comp_name]
                our_section = our_sections[our_name]
                ordered_results[comp_name] = self._fast_compare_sections(comparator_section, our_section)
        
        # For remaining unmatched comparator sections
        for comp_section_name in unmatched_comp:
            comp_section = comparator_sections[comp_section_name]
            best_match = self._find_best_content_match(comp_section, unmatched_our, our_sections)
            
            if best_match:
                # Found a content-based match
                our_section = our_sections[best_match]
                ordered_results[comp_section_name] = self._fast_compare_sections(comp_section, our_section)
                unmatched_our.remove(best_match)  # Remove from unmatched
            else:
                # Truly missing section
                ordered_results[comp_section_name] = self._create_missing_section_result(
                    comp_section_name, comp_section)
        
        # For remaining unmatched our sections, try to find best content match in comparator
        for our_section_name in unmatched_our:
            our_section = our_sections[our_section_name]
            
            # Check if this could match any critical section type
            if self._is_critical_section(our_section_name):
                # Try to find content-based match in all comparator sections
                best_match = self._find_best_content_match(our_section, comparator_sections.keys(), comparator_sections)
                
                if best_match and best_match not in section_matches and best_match not in ordered_results:
                    # Found content match - create comparison under our section name
                    comp_section = comparator_sections[best_match]
                    ordered_results[our_section_name] = self._fast_compare_sections(comp_section, our_section)
                else:
                    # This is a critical section missing from comparator - compare against full document
                    full_comparator_content = self._get_full_document_content(comparator_sections)
                    if full_comparator_content:
                        pseudo_comp_section = Section(
                            name=our_section_name,
                            content=full_comparator_content,
                            start_line=0,
                            end_line=1000,
                            confidence=0.3
                        )
                        ordered_results[our_section_name] = self._fast_compare_sections(pseudo_comp_section, our_section)
                    else:
                        # Fallback to extra section
                        ordered_results[f"extra_{our_section_name}"] = self._create_extra_section_result(
                            our_section_name, our_section)
            else:
                # Non-critical extra section
                ordered_results[f"extra_{our_section_name}"] = self._create_extra_section_result(
                    our_section_name, our_section)
        
        return self._ensure_section_order(ordered_results)
    
    def _ensure_section_order(self, results: Dict[str, ComparisonResult]) -> Dict[str, ComparisonResult]:
        """Ensure results are returned in the specified section order"""
        section_order = [
            'therapeutic_indications',      # 4.1 Therapeutic indications
            'contraindications',            # 4.3 Contraindications
            'special_warnings_precautions', # 4.4 Special warnings and precautions for use
            'interactions_medicinal_products', # 4.5 Interaction with other medicinal products
            'fertility_pregnancy_lactation', # 4.6 Fertility, pregnancy and lactation
            'effects_ability_drive_machines', # 4.7 Effects on ability to drive and use machines
            'undesirable_effects',          # 4.8 Undesirable effects
            'overdose'                      # 4.9 Overdose
        ]
        
        ordered_results = {}
        
        # First, add sections in the specified order
        for section_name in section_order:
            if section_name in results:
                ordered_results[section_name] = results[section_name]
        
        # Then add any remaining sections
        for section_name, result in results.items():
            if section_name not in ordered_results:
                ordered_results[section_name] = result
        
        return ordered_results
    
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
    
    def _comprehensive_section_matching(self, comp_sections: Dict[str, Section], 
                                       our_sections: Dict[str, Section]) -> Dict[str, str]:
        """Enhanced section matching with better content analysis"""
        # Start with the existing fast matching
        matches = self._fast_section_matching(comp_sections, our_sections)
        
        # For unmatched sections, try content-based matching
        unmatched_comp = set(comp_sections.keys()) - set(matches.keys())
        unmatched_our = set(our_sections.keys()) - set(matches.values())
        
        for comp_name in list(unmatched_comp):
            comp_section = comp_sections[comp_name]
            best_match = self._find_best_content_match(comp_section, unmatched_our, our_sections)
            
            if best_match:
                matches[comp_name] = best_match
                unmatched_our.remove(best_match)
                unmatched_comp.remove(comp_name)
        
        return matches
    
    def _find_best_content_match(self, target_section: Section, candidate_names: Set[str], 
                                candidate_sections: Dict[str, Section]) -> Optional[str]:
        """Find best content-based match for a section"""
        if not candidate_names:
            return None
        
        target_content = self._normalize_text(target_section.content).lower()
        target_words = set(self._get_words_fast(target_content))
        
        best_match = None
        best_score = 0.3  # Minimum threshold for content matching
        
        for candidate_name in candidate_names:
            candidate_section = candidate_sections[candidate_name]
            candidate_content = self._normalize_text(candidate_section.content).lower()
            candidate_words = set(self._get_words_fast(candidate_content))
            
            # Calculate word overlap score
            if target_words and candidate_words:
                overlap = len(target_words & candidate_words)
                union = len(target_words | candidate_words)
                jaccard_score = overlap / union if union > 0 else 0
                
                # Bonus for section type similarity
                type_bonus = self._calculate_section_type_similarity(target_section.name, candidate_name)
                final_score = jaccard_score + type_bonus
                
                if final_score > best_score:
                    best_score = final_score
                    best_match = candidate_name
        
        return best_match
    
    def _is_critical_section(self, section_name: str) -> bool:
        """Check if a section is critical for SmPC comparison (based on the specified order)"""
        critical_sections = {
            'therapeutic_indications',      # 4.1 Therapeutic indications
            'contraindications',            # 4.3 Contraindications
            'special_warnings_precautions', # 4.4 Special warnings and precautions for use
            'interactions_medicinal_products', # 4.5 Interaction with other medicinal products
            'fertility_pregnancy_lactation', # 4.6 Fertility, pregnancy and lactation
            'effects_ability_drive_machines', # 4.7 Effects on ability to drive and use machines
            'undesirable_effects',          # 4.8 Undesirable effects
            'overdose',                     # 4.9 Overdose
            # Also include posology for backward compatibility
            'posology_administration'
        }
        return section_name in critical_sections
    
    def _calculate_section_type_similarity(self, section1: str, section2: str) -> float:
        """Calculate similarity bonus based on section type"""
        # If sections are the same type, give a bonus
        if section1 == section2:
            return 0.2
        
        # Check for related section types
        related_groups = [
            {'therapeutic_indications', 'indications'},
            {'posology_administration', 'posology', 'dosage'},
            {'special_warnings_precautions', 'warnings_precautions', 'warnings', 'precautions'},
            {'interactions_medicinal_products', 'interactions', 'drug_interactions'},
            {'fertility_pregnancy_lactation', 'fertility_pregnancy', 'pregnancy'},
            {'effects_ability_drive_machines', 'driving_machines'},
            {'undesirable_effects', 'adverse_reactions'},
        ]
        
        for group in related_groups:
            if section1 in group and section2 in group:
                return 0.1
        
        return 0.0
    
    def _get_full_document_content(self, sections: Dict[str, Section]) -> str:
        """Get concatenated content from all sections for full document comparison"""
        all_content = []
        for section in sections.values():
            if section.content.strip():
                all_content.append(section.content.strip())
        return '\n\n'.join(all_content)
    
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