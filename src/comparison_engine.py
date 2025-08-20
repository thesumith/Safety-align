"""
Comparison Engine Module for RSI Comparison Tool
Compares sections between two RSI documents using multiple comparison methods
"""

import difflib
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

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
    """Compares RSI documents section by section"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        # Removed sentence model initialization for speed
    
    def compare_documents(self, comparator_sections: Dict[str, Section], 
                         our_sections: Dict[str, Section]) -> Dict[str, ComparisonResult]:
        """
        Compare two RSI documents section by section
        
        Args:
            comparator_sections: Sections from the comparator RSI
            our_sections: Sections from our RSI
            
        Returns:
            Dictionary mapping section names to comparison results
        """
        results = {}
        
        # Compare each section in the comparator against our RSI
        for section_name, comparator_section in comparator_sections.items():
            our_section = our_sections.get(section_name)
            
            if our_section:
                # Both sections exist, compare them
                result = self._compare_sections(comparator_section, our_section)
            else:
                # Section missing from our RSI
                result = self._create_missing_section_result(section_name, comparator_section)
            
            results[section_name] = result
        
        # Check for sections in our RSI that are not in comparator
        for section_name in our_sections:
            if section_name not in comparator_sections:
                results[f"extra_{section_name}"] = self._create_extra_section_result(section_name, our_sections[section_name])
        
        return results
    
    def _compare_sections(self, comparator_section: Section, our_section: Section) -> ComparisonResult:
        """Compare two sections using optimized fast methods"""
        comparator_text = comparator_section.content
        our_text = our_section.content
        
        # Use fast fuzzy matching as primary method
        fuzzy_match = self._fuzzy_text_comparison(comparator_text, our_text)
        
        # Use sentence-level comparison for detailed analysis
        sentence_comparison = self._sentence_level_comparison(comparator_text, our_text)
        
        # Use the method with better results
        if sentence_comparison['score'] > fuzzy_match['score']:
            best_method = sentence_comparison
        else:
            best_method = fuzzy_match
        
        return ComparisonResult(
            section_name=comparator_section.name,
            similarity_score=best_method['score'],
            missing_content=best_method['missing'],
            present_content=best_method['present'],
            comparison_method=best_method['method'],
            details={
                'fuzzy_match': fuzzy_match,
                'sentence_comparison': sentence_comparison
            }
        )
    
    def _exact_text_comparison(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare texts using exact matching"""
        # Normalize texts for comparison
        norm_text1 = self._normalize_text(text1)
        norm_text2 = self._normalize_text(text2)
        
        # Calculate similarity
        similarity = 1.0 if norm_text1 == norm_text2 else 0.0
        
        # Find differences using difflib
        differ = difflib.Differ()
        diff = list(differ.compare(norm_text1.splitlines(), norm_text2.splitlines()))
        
        missing_lines = [line[2:] for line in diff if line.startswith('- ')]
        present_lines = [line[2:] for line in diff if line.startswith('+ ')]
        
        return {
            'method': 'exact_match',
            'score': similarity,
            'missing': missing_lines,
            'present': present_lines,
            'diff': diff
        }
    
    def _fuzzy_text_comparison(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare texts using fuzzy string matching"""
        # Calculate various fuzzy matching scores
        ratio = fuzz.ratio(text1, text2) / 100.0
        partial_ratio = fuzz.partial_ratio(text1, text2) / 100.0
        token_sort_ratio = fuzz.token_sort_ratio(text1, text2) / 100.0
        token_set_ratio = fuzz.token_set_ratio(text1, text2) / 100.0
        
        # Use the highest score
        similarity = max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
        
        # Extract sentences and compare them
        sentences1 = self._extract_sentences(text1)
        sentences2 = self._extract_sentences(text2)
        
        missing_sentences = []
        present_sentences = []
        
        for sent1 in sentences1:
            best_match = 0
            for sent2 in sentences2:
                match_score = fuzz.ratio(sent1, sent2) / 100.0
                best_match = max(best_match, match_score)
            
            if best_match < self.similarity_threshold:
                missing_sentences.append(sent1)
            else:
                present_sentences.append(sent1)
        
        return {
            'method': 'fuzzy_match',
            'score': similarity,
            'missing': missing_sentences,
            'present': present_sentences,
            'detailed_scores': {
                'ratio': ratio,
                'partial_ratio': partial_ratio,
                'token_sort_ratio': token_sort_ratio,
                'token_set_ratio': token_set_ratio
            }
        }
    
    def _semantic_similarity_comparison(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare texts using semantic similarity"""
        try:
            # Encode texts
            embedding1 = self.sentence_model.encode(text1)
            embedding2 = self.sentence_model.encode(text2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
            
            # Extract sentences and compare semantically
            sentences1 = self._extract_sentences(text1)
            sentences2 = self._extract_sentences(text2)
            
            missing_sentences = []
            present_sentences = []
            
            if sentences1 and sentences2:
                # Encode all sentences
                embeddings1 = self.sentence_model.encode(sentences1)
                embeddings2 = self.sentence_model.encode(sentences2)
                
                for i, sent1 in enumerate(sentences1):
                    best_match = 0
                    for j, sent2 in enumerate(sentences2):
                        sim = np.dot(embeddings1[i], embeddings2[j]) / (np.linalg.norm(embeddings1[i]) * np.linalg.norm(embeddings2[j]))
                        best_match = max(best_match, sim)
                    
                    if best_match < self.similarity_threshold:
                        missing_sentences.append(sent1)
                    else:
                        present_sentences.append(sent1)
            
            return {
                'method': 'semantic_similarity',
                'score': float(similarity),
                'missing': missing_sentences,
                'present': present_sentences
            }
            
        except Exception as e:
            logger.error(f"Error in semantic similarity comparison: {e}")
            return {
                'method': 'semantic_similarity',
                'score': 0.0,
                'missing': [],
                'present': [],
                'error': str(e)
            }
    
    def _sentence_level_comparison(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare texts at sentence level"""
        sentences1 = self._extract_sentences(text1)
        sentences2 = self._extract_sentences(text2)
        
        missing_sentences = []
        present_sentences = []
        matched_pairs = []
        
        # Find matching sentences
        for sent1 in sentences1:
            best_match = None
            best_score = 0
            
            for sent2 in sentences2:
                # Use fuzzy matching for sentence comparison
                score = fuzz.ratio(sent1, sent2) / 100.0
                if score > best_score and score >= self.similarity_threshold:
                    best_score = score
                    best_match = sent2
            
            if best_match:
                present_sentences.append(sent1)
                matched_pairs.append((sent1, best_match, best_score))
            else:
                missing_sentences.append(sent1)
        
        # Calculate overall similarity
        total_sentences = len(sentences1)
        matched_sentences = len(present_sentences)
        similarity = matched_sentences / total_sentences if total_sentences > 0 else 0.0
        
        return {
            'method': 'sentence_level',
            'score': similarity,
            'missing': missing_sentences,
            'present': present_sentences,
            'matched_pairs': matched_pairs,
            'total_sentences': total_sentences,
            'matched_sentences': matched_sentences
        }
    
    def _determine_best_method(self, exact_match: Dict, fuzzy_match: Dict, 
                             semantic_match: Optional[Dict], sentence_comparison: Dict) -> Dict[str, Any]:
        """Determine the best comparison method based on scores and content"""
        methods = [exact_match, fuzzy_match, sentence_comparison]
        if semantic_match:
            methods.append(semantic_match)
        
        # Find method with highest score
        best_method = max(methods, key=lambda x: x['score'])
        
        # If exact match is perfect, use it
        if exact_match['score'] == 1.0:
            return exact_match
        
        # If semantic similarity is available and has good score, prefer it
        if semantic_match and semantic_match['score'] > 0.8:
            return semantic_match
        
        # Otherwise use the method with highest score
        return best_method
    
    def _create_missing_section_result(self, section_name: str, comparator_section: Section) -> ComparisonResult:
        """Create result for a section that's missing from our RSI"""
        return ComparisonResult(
            section_name=section_name,
            similarity_score=0.0,
            missing_content=[comparator_section.content],
            present_content=[],
            comparison_method='missing_section',
            details={'reason': 'Section not found in our RSI'}
        )
    
    def _create_extra_section_result(self, section_name: str, our_section: Section) -> ComparisonResult:
        """Create result for a section that's extra in our RSI"""
        return ComparisonResult(
            section_name=f"extra_{section_name}",
            similarity_score=1.0,
            missing_content=[],
            present_content=[our_section.content],
            comparison_method='extra_section',
            details={'reason': 'Section not present in comparator RSI'}
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation (optional, depending on requirements)
        # text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences
    
    def generate_summary_report(self, comparison_results: Dict[str, ComparisonResult]) -> Dict[str, Any]:
        """Generate a summary report of all comparisons"""
        summary = {
            'total_sections_compared': len(comparison_results),
            'sections_with_issues': 0,
            'overall_similarity': 0.0,
            'missing_sections': [],
            'sections_needing_attention': [],
            'detailed_results': {}
        }
        
        total_similarity = 0.0
        
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
                
            total_similarity += result.similarity_score
            
            if result.similarity_score < self.similarity_threshold:
                summary['sections_with_issues'] += 1
                summary['sections_needing_attention'].append({
                    'section': section_name,
                    'similarity_score': result.similarity_score,
                    'missing_content_count': len(result.missing_content),
                    'comparison_method': result.comparison_method
                })
            
            if result.comparison_method == 'missing_section':
                summary['missing_sections'].append(section_name)
            
            summary['detailed_results'][section_name] = {
                'similarity_score': result.similarity_score,
                'missing_content_count': len(result.missing_content),
                'present_content_count': len(result.present_content),
                'comparison_method': result.comparison_method
            }
        
        if comparison_results:
            summary['overall_similarity'] = total_similarity / len([r for r in comparison_results if not r.startswith('extra_')])
        
        return summary
