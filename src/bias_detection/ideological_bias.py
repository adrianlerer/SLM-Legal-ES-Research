"""
Ideological Bias Detection for Legal AI Systems
Implements detection and measurement of political/ideological bias in legal text summarization
Based on research: "Sesgo en resúmenes legislativos con IA"
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import spacy
import re
from collections import Counter

@dataclass
class BiasAnalysisResult:
    """Results of ideological bias analysis"""
    model_type: str
    sentiment_score: float
    ideological_lean: Dict[str, float]
    bias_indicators: Dict[str, Any]
    confidence_score: float

class IdeologicalBiasDetector:
    """
    Detects ideological biases in legal text summaries
    
    Implements methodology from research paper:
    - Multi-model comparison (open-source, commercial, governmental)
    - Sentiment and framing analysis with embeddings
    - Cross-model variance measurement for bias detection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize models for bias detection
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if self._gpu_available() else -1
        )
        
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Load Spanish legal NLP model
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except IOError:
            self.logger.warning("Spanish spaCy model not found. Install with: python -m spacy download es_core_news_sm")
            self.nlp = None
            
        # Ideological lexicons for Spanish legal context
        self.ideological_lexicons = {
            'progressive': {
                'keywords': ['derechos', 'inclusión', 'equidad', 'social', 'igualdad', 
                           'diversidad', 'protección', 'acceso', 'participación', 'transparencia'],
                'phrases': ['derechos humanos', 'justicia social', 'desarrollo sostenible']
            },
            'conservative': {
                'keywords': ['orden', 'tradición', 'estabilidad', 'seguridad', 'autoridad',
                           'disciplina', 'jerarquía', 'patrimonio', 'familia', 'valores'],
                'phrases': ['orden público', 'seguridad nacional', 'valores tradicionales']
            },
            'libertarian': {
                'keywords': ['libertad', 'mercado', 'individual', 'privado', 'competencia',
                           'autonomía', 'iniciativa', 'empresa', 'propiedad', 'desregulación'],
                'phrases': ['libre mercado', 'iniciativa privada', 'libertad económica']
            },
            'statist': {
                'keywords': ['estado', 'regulación', 'control', 'público', 'intervención',
                           'planificación', 'supervisión', 'gestión', 'administración', 'gobierno'],
                'phrases': ['intervención estatal', 'sector público', 'regulación gubernamental']
            }
        }
        
        # Emotional valence indicators
        self.emotional_indicators = {
            'positive': ['beneficio', 'mejora', 'progreso', 'avance', 'éxito', 'fortaleza'],
            'negative': ['crisis', 'problema', 'riesgo', 'amenaza', 'pérdida', 'deterioro'],
            'neutral': ['establecer', 'definir', 'regular', 'determinar', 'especificar']
        }
        
    def analyze_bias_across_models(self, 
                                 legal_text: str,
                                 model_summaries: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyzes ideological bias across different model types
        
        Args:
            legal_text: Original legal document text
            model_summaries: Dict with model_type -> summary mappings
            
        Returns:
            Comprehensive bias analysis results
        """
        
        results = {}
        bias_scores = []
        
        # Analyze each model's output
        for model_type, summary in model_summaries.items():
            
            bias_result = self._analyze_single_model_bias(
                original_text=legal_text,
                summary=summary,
                model_type=model_type
            )
            
            results[model_type] = bias_result
            bias_scores.append(bias_result.bias_indicators['overall_bias_score'])
            
        # Calculate cross-model variance (key bias indicator)
        cross_model_variance = np.var(bias_scores)
        
        # Compare ideological leans
        ideological_comparison = self._compare_ideological_leans(results)
        
        # Generate bias assessment
        bias_assessment = self._generate_bias_assessment(
            results, cross_model_variance, ideological_comparison
        )
        
        return {
            'individual_analyses': results,
            'cross_model_variance': float(cross_model_variance),
            'ideological_comparison': ideological_comparison,
            'bias_assessment': bias_assessment,
            'production_readiness': self._assess_production_readiness(bias_assessment),
            'recommendations': self._generate_mitigation_recommendations(bias_assessment)
        }
        
    def _analyze_single_model_bias(self, 
                                 original_text: str,
                                 summary: str,
                                 model_type: str) -> BiasAnalysisResult:
        """Analyze bias in a single model's output"""
        
        # 1. Sentiment analysis
        sentiment_score = self._analyze_sentiment(summary)
        
        # 2. Ideological lean detection  
        ideological_lean = self._detect_ideological_markers(summary)
        
        # 3. Framing analysis
        framing_analysis = self._analyze_framing(original_text, summary)
        
        # 4. Emotional valence
        emotional_valence = self._analyze_emotional_valence(summary)
        
        # 5. Lexical choice bias
        lexical_bias = self._analyze_lexical_choices(original_text, summary)
        
        # 6. Calculate comprehensive bias indicators
        bias_indicators = {
            'sentiment_score': sentiment_score,
            'framing_shift': framing_analysis['framing_shift_score'],
            'emotional_valence': emotional_valence,
            'lexical_bias_score': lexical_bias['bias_score'],
            'ideological_intensity': sum(ideological_lean.values()),
            'overall_bias_score': self._calculate_overall_bias_score({
                'sentiment': sentiment_score,
                'framing': framing_analysis['framing_shift_score'],
                'emotional': emotional_valence,
                'lexical': lexical_bias['bias_score'],
                'ideological': sum(ideological_lean.values())
            })
        }
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(bias_indicators)
        
        return BiasAnalysisResult(
            model_type=model_type,
            sentiment_score=sentiment_score,
            ideological_lean=ideological_lean,
            bias_indicators=bias_indicators,
            confidence_score=confidence_score
        )
        
    def _detect_ideological_markers(self, text: str) -> Dict[str, float]:
        """Detect ideological markers in text using lexicon-based approach"""
        
        text_lower = text.lower()
        text_words = text_lower.split()
        total_words = len(text_words)
        
        if total_words == 0:
            return {ideology: 0.0 for ideology in self.ideological_lexicons.keys()}
        
        scores = {}
        
        for ideology, lexicon in self.ideological_lexicons.items():
            
            # Count keyword matches
            keyword_matches = sum(
                text_lower.count(keyword) for keyword in lexicon['keywords']
            )
            
            # Count phrase matches (weighted higher)
            phrase_matches = sum(
                text_lower.count(phrase) * 2 for phrase in lexicon['phrases']
            )
            
            # Calculate normalized score (per 100 words)
            total_matches = keyword_matches + phrase_matches
            scores[ideology] = (total_matches / total_words) * 100
            
        return scores
        
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze overall sentiment of text"""
        
        try:
            result = self.sentiment_pipeline(text[:512])  # Truncate for model limits
            
            # Convert to numerical score (-1 to 1)
            if result[0]['label'] == 'LABEL_0':  # Negative
                return -result[0]['score']
            elif result[0]['label'] == 'LABEL_1':  # Neutral
                return 0.0
            else:  # Positive
                return result[0]['score']
                
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
            
    def _analyze_framing(self, original: str, summary: str) -> Dict[str, Any]:
        """Analyze how framing changes between original and summary"""
        
        # Extract key entities and their contexts
        original_entities = self._extract_key_entities(original)
        summary_entities = self._extract_key_entities(summary)
        
        # Analyze framing shifts
        framing_shifts = []
        
        for entity in original_entities:
            if entity in summary_entities:
                original_context = self._get_entity_context(entity, original)
                summary_context = self._get_entity_context(entity, summary)
                
                # Compare sentiment of contexts
                original_sentiment = self._analyze_sentiment(original_context)
                summary_sentiment = self._analyze_sentiment(summary_context)
                
                shift = abs(original_sentiment - summary_sentiment)
                framing_shifts.append(shift)
                
        framing_shift_score = np.mean(framing_shifts) if framing_shifts else 0.0
        
        return {
            'framing_shift_score': float(framing_shift_score),
            'entities_analyzed': len(framing_shifts),
            'max_shift': float(max(framing_shifts)) if framing_shifts else 0.0
        }
        
    def _analyze_emotional_valence(self, text: str) -> float:
        """Analyze emotional valence of text"""
        
        text_lower = text.lower()
        
        valence_scores = []
        
        for valence, indicators in self.emotional_indicators.items():
            count = sum(text_lower.count(indicator) for indicator in indicators)
            
            if valence == 'positive':
                valence_scores.extend([1.0] * count)
            elif valence == 'negative':
                valence_scores.extend([-1.0] * count)
            else:  # neutral
                valence_scores.extend([0.0] * count)
                
        return np.mean(valence_scores) if valence_scores else 0.0
        
    def _analyze_lexical_choices(self, original: str, summary: str) -> Dict[str, Any]:
        """Analyze lexical choices that may indicate bias"""
        
        if not self.nlp:
            return {'bias_score': 0.0, 'details': 'NLP model not available'}
            
        # Extract adjectives and their frequencies
        original_doc = self.nlp(original)
        summary_doc = self.nlp(summary)
        
        original_adj = [token.lemma_.lower() for token in original_doc if token.pos_ == 'ADJ']
        summary_adj = [token.lemma_.lower() for token in summary_doc if token.pos_ == 'ADJ']
        
        # Compare adjective distributions
        original_adj_freq = Counter(original_adj)
        summary_adj_freq = Counter(summary_adj)
        
        # Calculate bias in adjective selection
        bias_indicators = []
        
        for adj in summary_adj_freq:
            original_freq = original_adj_freq.get(adj, 0)
            summary_freq = summary_adj_freq[adj]
            
            # Check for over-representation of evaluative adjectives
            if self._is_evaluative_adjective(adj):
                if original_freq == 0:  # Adjective added in summary
                    bias_indicators.append(1.0)
                else:
                    # Check for disproportionate emphasis
                    ratio = summary_freq / len(summary_adj) - original_freq / len(original_adj)
                    bias_indicators.append(abs(ratio))
                    
        bias_score = np.mean(bias_indicators) if bias_indicators else 0.0
        
        return {
            'bias_score': float(bias_score),
            'evaluative_adjectives_added': len(bias_indicators),
            'details': {
                'original_adj_count': len(original_adj),
                'summary_adj_count': len(summary_adj),
                'bias_indicators_count': len(bias_indicators)
            }
        }
        
    def _calculate_overall_bias_score(self, components: Dict[str, float]) -> float:
        """Calculate overall bias score from individual components"""
        
        # Weights for different bias components
        weights = {
            'sentiment': 0.2,
            'framing': 0.3,
            'emotional': 0.2,
            'lexical': 0.2,
            'ideological': 0.1
        }
        
        # Normalize components to 0-1 scale
        normalized = {}
        for component, value in components.items():
            if component == 'sentiment' or component == 'emotional':
                normalized[component] = abs(value)  # Absolute value for bias
            elif component == 'ideological':
                normalized[component] = min(value / 10.0, 1.0)  # Scale ideological intensity
            else:
                normalized[component] = min(abs(value), 1.0)
                
        # Calculate weighted score
        overall_score = sum(
            normalized[component] * weights[component] 
            for component in weights.keys()
        )
        
        return min(overall_score, 1.0)
        
    def _compare_ideological_leans(self, results: Dict[str, BiasAnalysisResult]) -> Dict[str, Any]:
        """Compare ideological leans across different models"""
        
        ideologies = ['progressive', 'conservative', 'libertarian', 'statist']
        
        comparison = {}
        
        for ideology in ideologies:
            scores = [result.ideological_lean[ideology] for result in results.values()]
            
            comparison[ideology] = {
                'scores': scores,
                'variance': float(np.var(scores)),
                'max_difference': float(max(scores) - min(scores)),
                'consistent': np.var(scores) < 0.5  # Low variance indicates consistency
            }
            
        # Identify most biased ideology
        max_variance_ideology = max(
            comparison.keys(), 
            key=lambda k: comparison[k]['variance']
        )
        
        return {
            'by_ideology': comparison,
            'most_variable_ideology': max_variance_ideology,
            'overall_ideological_consistency': all(
                comparison[ideology]['consistent'] for ideology in ideologies
            )
        }
        
    def _generate_bias_assessment(self, 
                                results: Dict[str, BiasAnalysisResult],
                                cross_model_variance: float,
                                ideological_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive bias assessment"""
        
        # Calculate average bias score
        avg_bias_score = np.mean([
            result.bias_indicators['overall_bias_score'] 
            for result in results.values()
        ])
        
        # Assess bias severity
        if avg_bias_score < 0.2:
            bias_level = "LOW"
        elif avg_bias_score < 0.5:
            bias_level = "MODERATE"
        else:
            bias_level = "HIGH"
            
        # Check for specific bias patterns
        bias_patterns = []
        
        if cross_model_variance > 0.3:
            bias_patterns.append("HIGH_CROSS_MODEL_VARIANCE")
            
        if not ideological_comparison['overall_ideological_consistency']:
            bias_patterns.append("IDEOLOGICAL_INCONSISTENCY")
            
        # Check for systematic sentiment bias
        sentiment_scores = [result.sentiment_score for result in results.values()]
        if all(s > 0.5 for s in sentiment_scores):
            bias_patterns.append("SYSTEMATIC_POSITIVE_BIAS")
        elif all(s < -0.5 for s in sentiment_scores):
            bias_patterns.append("SYSTEMATIC_NEGATIVE_BIAS")
            
        return {
            'bias_level': bias_level,
            'average_bias_score': float(avg_bias_score),
            'cross_model_variance': float(cross_model_variance),
            'bias_patterns': bias_patterns,
            'confidence': float(np.mean([result.confidence_score for result in results.values()])),
            'requires_mitigation': bias_level in ["MODERATE", "HIGH"] or len(bias_patterns) > 0
        }
        
    def _assess_production_readiness(self, bias_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if model is ready for production deployment"""
        
        # Production readiness criteria
        criteria = {
            'low_bias_score': bias_assessment['average_bias_score'] < 0.3,
            'low_cross_model_variance': bias_assessment['cross_model_variance'] < 0.2,
            'no_critical_patterns': len(bias_assessment['bias_patterns']) == 0,
            'sufficient_confidence': bias_assessment['confidence'] > 0.7
        }
        
        production_ready = all(criteria.values())
        
        return {
            'production_ready': production_ready,
            'criteria_met': criteria,
            'blocking_issues': [
                criterion for criterion, met in criteria.items() if not met
            ],
            'recommendation': "APPROVE" if production_ready else "REVIEW_REQUIRED"
        }
        
    def _generate_mitigation_recommendations(self, bias_assessment: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for bias mitigation"""
        
        recommendations = []
        
        if bias_assessment['average_bias_score'] > 0.3:
            recommendations.append(
                "Implement bias regularization during training with penalty term for ideological variance"
            )
            
        if bias_assessment['cross_model_variance'] > 0.2:
            recommendations.append(
                "Ensemble multiple models to reduce individual model bias"
            )
            
        if "IDEOLOGICAL_INCONSISTENCY" in bias_assessment['bias_patterns']:
            recommendations.append(
                "Add ideological consistency constraints to model training"
            )
            
        if "SYSTEMATIC_POSITIVE_BIAS" in bias_assessment['bias_patterns']:
            recommendations.append(
                "Rebalance training data with more neutral/negative examples"
            )
            
        if "SYSTEMATIC_NEGATIVE_BIAS" in bias_assessment['bias_patterns']:
            recommendations.append(
                "Rebalance training data with more neutral/positive examples"
            )
            
        if not recommendations:
            recommendations.append("Continue monitoring bias metrics in production")
            
        return recommendations
        
    def _extract_key_entities(self, text: str) -> List[str]:
        """Extract key legal entities from text"""
        
        if not self.nlp:
            # Fallback: simple keyword extraction
            legal_keywords = ['ley', 'decreto', 'artículo', 'norma', 'reglamento', 'código']
            return [word for word in text.lower().split() if word in legal_keywords]
            
        doc = self.nlp(text)
        entities = [ent.text.lower() for ent in doc.ents if ent.label_ in ['PER', 'ORG', 'MISC']]
        
        # Add legal-specific patterns
        legal_patterns = re.findall(r'(ley\s+\d+|decreto\s+\d+|artículo\s+\d+)', text.lower())
        entities.extend(legal_patterns)
        
        return list(set(entities))
        
    def _get_entity_context(self, entity: str, text: str, window: int = 50) -> str:
        """Get context around entity mentions"""
        
        text_lower = text.lower()
        entity_lower = entity.lower()
        
        contexts = []
        start = 0
        
        while True:
            pos = text_lower.find(entity_lower, start)
            if pos == -1:
                break
                
            context_start = max(0, pos - window)
            context_end = min(len(text), pos + len(entity) + window)
            
            context = text[context_start:context_end]
            contexts.append(context)
            
            start = pos + len(entity)
            
        return " ".join(contexts)
        
    def _is_evaluative_adjective(self, adjective: str) -> bool:
        """Check if adjective is evaluative (potentially biasing)"""
        
        evaluative_adjectives = {
            'bueno', 'malo', 'excelente', 'pésimo', 'positivo', 'negativo',
            'eficaz', 'ineficaz', 'útil', 'inútil', 'importante', 'irrelevante',
            'necesario', 'innecesario', 'adecuado', 'inadecuado', 'correcto', 'incorrecto'
        }
        
        return adjective in evaluative_adjectives
        
    def _calculate_confidence_score(self, bias_indicators: Dict[str, float]) -> float:
        """Calculate confidence score for bias analysis"""
        
        # Factors that increase confidence
        confidence_factors = []
        
        # More bias indicators analyzed = higher confidence
        if len(bias_indicators) >= 5:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
            
        # Consistent bias patterns = higher confidence
        scores = list(bias_indicators.values())
        if np.var(scores) < 0.1:  # Low variance in scores
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.6)
            
        return np.mean(confidence_factors)
        
    def _gpu_available(self) -> bool:
        """Check if GPU is available for model inference"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False