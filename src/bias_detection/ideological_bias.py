"""
Ideological Bias Detection for Legal AI Systems
Implements research-based methodology for detecting political/ideological bias in legal summaries
"""

import numpy as np
from typing import Dict, Any, List
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass
import re

@dataclass
class IdeologicalAnalysis:
    """Results of ideological bias analysis"""
    sentiment_scores: Dict[str, float]
    ideological_markers: Dict[str, float]
    bias_indicators: Dict[str, Any]
    confidence_level: float
    risk_assessment: str

class IdeologicalBiasDetector:
    """
    Detects ideological bias in legal document summaries
    Based on multi-model comparison and lexical analysis
    """
    
    def __init__(self):
        self.sentiment_models = self._initialize_models()
        self.ideological_lexicon = self._load_ideological_lexicon()
        self.legal_context_markers = self._load_legal_context_markers()
        
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize different types of sentiment/bias detection models"""
        
        models = {}
        
        try:
            # Spanish legal sentiment model
            models['legal_sentiment'] = pipeline(
                "sentiment-analysis",
                model="finiteautomata/beto-sentiment-analysis",
                tokenizer="finiteautomata/beto-sentiment-analysis"
            )
            
            # General Spanish sentiment
            models['general_sentiment'] = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Political bias detection (if available)
            models['political_classifier'] = pipeline(
                "text-classification",
                model="unitary/toxic-bert"  # Placeholder - would use political bias model
            )
            
        except Exception as e:
            print(f"Warning: Some models not available: {e}")
            # Fallback to basic analysis
            models['fallback'] = True
            
        return models
        
    def _load_ideological_lexicon(self) -> Dict[str, List[str]]:
        """Load lexicon of ideologically-marked terms for legal contexts"""
        
        return {
            'progressive_legal': [
                'derechos humanos', 'inclusión', 'equidad de género', 'diversidad',
                'acceso a la justicia', 'protección social', 'medio ambiente',
                'consumidor', 'trabajador', 'minorías', 'transparencia'
            ],
            'conservative_legal': [
                'orden público', 'seguridad jurídica', 'tradición legal', 'estabilidad',
                'propiedad privada', 'libre mercado', 'autoridad', 'jerarquía',
                'familia tradicional', 'valores morales', 'disciplina'
            ],
            'libertarian_legal': [
                'libertad individual', 'desregulación', 'mercado libre', 'autonomía',
                'mínima intervención', 'derechos individuales', 'libre empresa',
                'competencia', 'innovación', 'eficiencia económica'
            ],
            'statist_legal': [
                'intervención estatal', 'regulación', 'control gubernamental', 'planificación',
                'servicio público', 'bienestar social', 'redistribución',
                'política pública', 'supervisión', 'administración central'
            ],
            'neutral_legal': [
                'normativa', 'procedimiento', 'artículo', 'disposición', 'vigencia',
                'aplicación', 'cumplimiento', 'interpretación', 'jurisprudencia'
            ]
        }
        
    def _load_legal_context_markers(self) -> Dict[str, List[str]]:
        """Load markers that indicate legal context and authority"""
        
        return {
            'authority_markers': [
                'el congreso', 'la legislatura', 'el poder ejecutivo', 'la corte',
                'tribunal', 'juzgado', 'ministerio', 'secretaría', 'organismo'
            ],
            'obligation_markers': [
                'debe', 'deberá', 'tiene que', 'está obligado', 'es responsable',
                'corresponde', 'incumbe', 'compete', 'se establece'
            ],
            'permission_markers': [
                'puede', 'podrá', 'está autorizado', 'tiene derecho', 'faculta',
                'permite', 'habilita', 'autoriza'
            ],
            'prohibition_markers': [
                'no puede', 'no podrá', 'prohibe', 'impide', 'veda', 'restringe'
            ]
        }
    
    def analyze_ideological_bias(self, 
                                text: str, 
                                reference_summaries: List[str] = None) -> IdeologicalAnalysis:
        """
        Analyze ideological bias in a legal text or summary
        
        Args:
            text: Text to analyze for bias
            reference_summaries: Optional list of reference summaries for comparison
            
        Returns:
            IdeologicalAnalysis object with detailed bias assessment
        """
        
        # 1. Sentiment analysis across models
        sentiment_scores = self._analyze_sentiment_across_models(text)
        
        # 2. Ideological marker detection
        ideological_markers = self._detect_ideological_markers(text)
        
        # 3. Legal framing analysis
        framing_analysis = self._analyze_legal_framing(text)
        
        # 4. Comparative analysis if references provided
        comparative_analysis = None
        if reference_summaries:
            comparative_analysis = self._comparative_bias_analysis(text, reference_summaries)
            
        # 5. Calculate bias indicators
        bias_indicators = self._calculate_bias_indicators(
            sentiment_scores, ideological_markers, framing_analysis, comparative_analysis
        )
        
        # 6. Risk assessment
        risk_assessment = self._assess_bias_risk(bias_indicators)
        
        # 7. Confidence calculation
        confidence_level = self._calculate_confidence(sentiment_scores, ideological_markers)
        
        return IdeologicalAnalysis(
            sentiment_scores=sentiment_scores,
            ideological_markers=ideological_markers,
            bias_indicators=bias_indicators,
            confidence_level=confidence_level,
            risk_assessment=risk_assessment
        )
    
    def _analyze_sentiment_across_models(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using multiple models to detect bias"""
        
        scores = {}
        
        for model_name, model in self.sentiment_models.items():
            if model_name == 'fallback':
                continue
                
            try:
                if 'sentiment' in model_name:
                    result = model(text[:512])  # Limit text length
                    
                    if isinstance(result, list) and len(result) > 0:
                        # Extract sentiment score
                        if result[0]['label'] in ['POSITIVE', 'POS']:
                            scores[model_name] = result[0]['score']
                        elif result[0]['label'] in ['NEGATIVE', 'NEG']:
                            scores[model_name] = -result[0]['score']
                        else:  # NEUTRAL
                            scores[model_name] = 0.0
                            
                elif 'political' in model_name:
                    result = model(text[:512])
                    # Extract political bias score (implementation depends on specific model)
                    scores[model_name] = self._extract_political_score(result)
                    
            except Exception as e:
                print(f"Error analyzing with {model_name}: {e}")
                scores[model_name] = 0.0
                
        # If no models worked, use lexicon-based fallback
        if not scores:
            scores['lexicon_sentiment'] = self._lexicon_based_sentiment(text)
            
        return scores
    
    def _detect_ideological_markers(self, text: str) -> Dict[str, float]:
        """Detect and quantify ideological markers in text"""
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        marker_scores = {}
        
        for ideology, markers in self.ideological_lexicon.items():
            score = 0
            matches = []
            
            for marker in markers:
                marker_count = text_lower.count(marker.lower())
                if marker_count > 0:
                    score += marker_count
                    matches.append((marker, marker_count))
                    
            # Normalize by text length
            normalized_score = (score / word_count) * 1000 if word_count > 0 else 0
            
            marker_scores[ideology] = {
                'raw_score': score,
                'normalized_score': normalized_score,
                'matches': matches
            }
            
        return marker_scores
    
    def _analyze_legal_framing(self, text: str) -> Dict[str, Any]:
        """Analyze how legal concepts are framed (positive/negative/neutral)"""
        
        text_lower = text.lower()
        framing_analysis = {}
        
        for frame_type, markers in self.legal_context_markers.items():
            frame_analysis = {
                'count': 0,
                'context_sentiment': [],
                'matches': []
            }
            
            for marker in markers:
                marker_positions = [m.start() for m in re.finditer(re.escape(marker.lower()), text_lower)]
                
                for pos in marker_positions:
                    frame_analysis['count'] += 1
                    frame_analysis['matches'].append(marker)
                    
                    # Analyze sentiment of surrounding context (±50 chars)
                    context_start = max(0, pos - 50)
                    context_end = min(len(text), pos + len(marker) + 50)
                    context = text[context_start:context_end]
                    
                    context_sentiment = self._get_context_sentiment(context)
                    frame_analysis['context_sentiment'].append(context_sentiment)
                    
            # Calculate average sentiment for this frame type
            if frame_analysis['context_sentiment']:
                frame_analysis['avg_sentiment'] = np.mean(frame_analysis['context_sentiment'])
            else:
                frame_analysis['avg_sentiment'] = 0.0
                
            framing_analysis[frame_type] = frame_analysis
            
        return framing_analysis
    
    def _comparative_bias_analysis(self, 
                                 target_text: str, 
                                 reference_summaries: List[str]) -> Dict[str, Any]:
        """Compare bias levels between target text and reference summaries"""
        
        # Analyze target
        target_analysis = {
            'sentiment': self._analyze_sentiment_across_models(target_text),
            'ideological': self._detect_ideological_markers(target_text)
        }
        
        # Analyze references
        reference_analyses = []
        for ref_summary in reference_summaries:
            ref_analysis = {
                'sentiment': self._analyze_sentiment_across_models(ref_summary),
                'ideological': self._detect_ideological_markers(ref_summary)
            }
            reference_analyses.append(ref_analysis)
            
        # Calculate variance and deviation
        sentiment_variance = self._calculate_sentiment_variance(
            target_analysis['sentiment'], 
            [ref['sentiment'] for ref in reference_analyses]
        )
        
        ideological_variance = self._calculate_ideological_variance(
            target_analysis['ideological'],
            [ref['ideological'] for ref in reference_analyses]
        )
        
        return {
            'sentiment_variance': sentiment_variance,
            'ideological_variance': ideological_variance,
            'outlier_score': self._calculate_outlier_score(sentiment_variance, ideological_variance),
            'consensus_deviation': self._calculate_consensus_deviation(
                target_analysis, reference_analyses
            )
        }
    
    def _calculate_bias_indicators(self, 
                                 sentiment_scores: Dict[str, float],
                                 ideological_markers: Dict[str, Any],
                                 framing_analysis: Dict[str, Any],
                                 comparative_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate comprehensive bias indicators"""
        
        indicators = {}
        
        # 1. Sentiment consistency across models
        sentiment_values = list(sentiment_scores.values())
        if len(sentiment_values) > 1:
            indicators['sentiment_variance'] = np.var(sentiment_values)
            indicators['sentiment_range'] = max(sentiment_values) - min(sentiment_values)
        else:
            indicators['sentiment_variance'] = 0.0
            indicators['sentiment_range'] = 0.0
            
        # 2. Ideological balance
        ideological_scores = {
            k: v['normalized_score'] for k, v in ideological_markers.items() 
            if k != 'neutral_legal'
        }
        
        if ideological_scores:
            max_ideology = max(ideological_scores.values())
            min_ideology = min(ideological_scores.values())
            indicators['ideological_imbalance'] = max_ideology - min_ideology
            
            # Dominant ideology
            dominant_ideology = max(ideological_scores.keys(), key=lambda k: ideological_scores[k])
            indicators['dominant_ideology'] = dominant_ideology
            indicators['dominance_strength'] = ideological_scores[dominant_ideology]
        else:
            indicators['ideological_imbalance'] = 0.0
            indicators['dominant_ideology'] = 'neutral'
            indicators['dominance_strength'] = 0.0
            
        # 3. Legal framing bias
        framing_sentiments = [
            frame['avg_sentiment'] for frame in framing_analysis.values()
            if 'avg_sentiment' in frame
        ]
        
        if framing_sentiments:
            indicators['framing_bias'] = np.std(framing_sentiments)
            indicators['avg_framing_sentiment'] = np.mean(framing_sentiments)
        else:
            indicators['framing_bias'] = 0.0
            indicators['avg_framing_sentiment'] = 0.0
            
        # 4. Comparative indicators
        if comparative_analysis:
            indicators['outlier_score'] = comparative_analysis['outlier_score']
            indicators['consensus_deviation'] = comparative_analysis['consensus_deviation']
        else:
            indicators['outlier_score'] = 0.0
            indicators['consensus_deviation'] = 0.0
            
        # 5. Overall bias score (0-1, where 1 is maximum bias)
        bias_components = [
            min(indicators['sentiment_variance'] * 2, 1.0),  # Sentiment inconsistency
            min(indicators['ideological_imbalance'] / 10.0, 1.0),  # Ideological imbalance
            min(indicators['framing_bias'], 1.0),  # Framing bias
            min(indicators['outlier_score'], 1.0)  # Comparative outlier
        ]
        
        indicators['overall_bias_score'] = np.mean(bias_components)
        
        return indicators
    
    def _assess_bias_risk(self, bias_indicators: Dict[str, Any]) -> str:
        """Assess overall bias risk level"""
        
        overall_score = bias_indicators['overall_bias_score']
        
        if overall_score <= 0.2:
            return "BAJO - Sesgo mínimo detectado"
        elif overall_score <= 0.4:
            return "MODERADO - Sesgo detectado, revisar análisis"
        elif overall_score <= 0.7:
            return "ALTO - Sesgo significativo, requiere intervención"
        else:
            return "CRÍTICO - Sesgo severo, no apto para producción"
    
    def _calculate_confidence(self, 
                            sentiment_scores: Dict[str, float],
                            ideological_markers: Dict[str, Any]) -> float:
        """Calculate confidence level of bias analysis"""
        
        # Confidence based on:
        # 1. Number of models that worked
        # 2. Consistency of results
        # 3. Amount of text analyzed
        
        model_confidence = len(sentiment_scores) / 3.0  # Assuming 3 models max
        
        # Consistency confidence
        if len(sentiment_scores) > 1:
            values = list(sentiment_scores.values())
            consistency = 1.0 - (np.std(values) / 2.0)  # Normalize std
            consistency_confidence = max(0.0, min(1.0, consistency))
        else:
            consistency_confidence = 0.5
            
        # Marker confidence (more markers = higher confidence)
        total_markers = sum(
            len(markers['matches']) for markers in ideological_markers.values()
        )
        marker_confidence = min(total_markers / 10.0, 1.0)  # Cap at 10 markers
        
        overall_confidence = np.mean([
            model_confidence, consistency_confidence, marker_confidence
        ])
        
        return overall_confidence
    
    # Helper methods
    def _extract_political_score(self, result: Any) -> float:
        """Extract political bias score from model result"""
        # Implementation depends on specific political bias model
        return 0.0
    
    def _lexicon_based_sentiment(self, text: str) -> float:
        """Fallback lexicon-based sentiment analysis"""
        positive_words = ['bueno', 'beneficio', 'protege', 'mejora', 'fortalece']
        negative_words = ['malo', 'daño', 'perjudica', 'debilita', 'reduce']
        
        text_lower = text.lower()
        pos_count = sum(text_lower.count(word) for word in positive_words)
        neg_count = sum(text_lower.count(word) for word in negative_words)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
            
        return (pos_count - neg_count) / total_words
    
    def _get_context_sentiment(self, context: str) -> float:
        """Get sentiment of a text context"""
        # Simple implementation - could use full sentiment model
        return self._lexicon_based_sentiment(context)
    
    def _calculate_sentiment_variance(self, 
                                   target_sentiment: Dict[str, float],
                                   reference_sentiments: List[Dict[str, float]]) -> float:
        """Calculate variance in sentiment scores"""
        
        all_scores = []
        
        # Add target scores
        all_scores.extend(target_sentiment.values())
        
        # Add reference scores
        for ref_sentiment in reference_sentiments:
            all_scores.extend(ref_sentiment.values())
            
        return np.var(all_scores) if all_scores else 0.0
    
    def _calculate_ideological_variance(self,
                                     target_markers: Dict[str, Any],
                                     reference_markers: List[Dict[str, Any]]) -> float:
        """Calculate variance in ideological markers"""
        
        # Extract normalized scores for each ideology
        ideologies = target_markers.keys()
        variance_scores = []
        
        for ideology in ideologies:
            scores = [target_markers[ideology]['normalized_score']]
            
            for ref_markers in reference_markers:
                if ideology in ref_markers:
                    scores.append(ref_markers[ideology]['normalized_score'])
                    
            if len(scores) > 1:
                variance_scores.append(np.var(scores))
                
        return np.mean(variance_scores) if variance_scores else 0.0
    
    def _calculate_outlier_score(self, 
                               sentiment_variance: float, 
                               ideological_variance: float) -> float:
        """Calculate how much the target is an outlier compared to references"""
        
        # Combine variances to get overall outlier score
        combined_variance = (sentiment_variance + ideological_variance) / 2.0
        
        # Normalize to 0-1 scale
        return min(combined_variance * 10, 1.0)
    
    def _calculate_consensus_deviation(self, 
                                    target_analysis: Dict[str, Any],
                                    reference_analyses: List[Dict[str, Any]]) -> float:
        """Calculate how much target deviates from consensus of references"""
        
        # Implementation for consensus calculation
        # This is a simplified version
        return 0.0  # Placeholder

# Usage example
if __name__ == "__main__":
    detector = IdeologicalBiasDetector()
    
    sample_text = """
    La nueva ley de transparencia fortalece los derechos de los ciudadanos
    y establece mecanismos efectivos de control sobre la administración pública.
    Se garantiza el acceso a la información y se protege el interés general.
    """
    
    analysis = detector.analyze_ideological_bias(sample_text)
    
    print(f"Bias Risk: {analysis.risk_assessment}")
    print(f"Confidence: {analysis.confidence_level:.2f}")
    print(f"Overall Bias Score: {analysis.bias_indicators['overall_bias_score']:.3f}")
    print(f"Dominant Ideology: {analysis.bias_indicators['dominant_ideology']}")