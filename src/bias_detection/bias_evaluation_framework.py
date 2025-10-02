"""
Comprehensive Bias Evaluation Framework for Legal AI Systems
Integrates all bias detection components into unified evaluation system
Based on research: "Sesgo en resúmenes legislativos con IA pautas a investigar"
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import json
from datetime import datetime
from pathlib import Path

from .ideological_bias import IdeologicalBiasDetector, BiasAnalysisResult
from .compliance_preservation import CompliancePreservationAnalyzer, ComplianceAnalysisResult
from .traceability import LegalTraceabilityEngine, TraceabilityReport

@dataclass
class ComprehensiveBiasReport:
    """Complete bias evaluation report combining all analysis types"""
    timestamp: str
    input_metadata: Dict[str, Any]
    model_results: Dict[str, Dict[str, Any]]
    comparative_analysis: Dict[str, Any]
    production_readiness: Dict[str, Any]
    recommendations: List[str]
    compliance_status: str
    overall_bias_score: float

@dataclass 
class BiasEvaluationConfig:
    """Configuration for bias evaluation framework"""
    target_preservation_rate: float = 0.85
    max_bias_score: float = 0.3
    max_hallucination_risk: float = 0.05
    min_traceability_score: float = 0.8
    enable_detailed_logging: bool = True
    generate_audit_reports: bool = True

class LegalBiasEvaluationFramework:
    """
    Comprehensive framework for evaluating biases in legal AI systems
    
    Integrates:
    - Ideological bias detection
    - Compliance preservation analysis  
    - Traceability and explainability assessment
    - Multi-model comparative analysis
    - Production readiness evaluation
    """
    
    def __init__(self, config: Optional[BiasEvaluationConfig] = None):
        self.config = config or BiasEvaluationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize component analyzers
        self.ideological_detector = IdeologicalBiasDetector()
        self.compliance_analyzer = CompliancePreservationAnalyzer()
        self.traceability_engine = LegalTraceabilityEngine()
        
        # Evaluation history for trend analysis
        self.evaluation_history: List[ComprehensiveBiasReport] = []
        
    def comprehensive_bias_evaluation(self, 
                                    legal_text: str,
                                    model_summaries: Dict[str, str],
                                    human_reference: Optional[str] = None,
                                    evaluation_id: Optional[str] = None) -> ComprehensiveBiasReport:
        """
        Perform comprehensive bias evaluation across all dimensions
        
        Args:
            legal_text: Original legal document
            model_summaries: Dict mapping model_name -> summary
            human_reference: Optional human-written reference summary
            evaluation_id: Optional ID for tracking evaluations
            
        Returns:
            Complete bias evaluation report
        """
        
        evaluation_id = evaluation_id or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Starting comprehensive bias evaluation: {evaluation_id}")
        
        # Input metadata
        input_metadata = self._generate_input_metadata(legal_text, model_summaries, human_reference)
        
        # Evaluate each model
        model_results = {}
        
        for model_name, summary in model_summaries.items():
            self.logger.info(f"Evaluating model: {model_name}")
            
            model_evaluation = self._evaluate_single_model(
                legal_text=legal_text,
                summary=summary,
                model_name=model_name,
                human_reference=human_reference
            )
            
            model_results[model_name] = model_evaluation
            
        # Comparative analysis across models
        comparative_analysis = self._perform_comparative_analysis(model_results)
        
        # Production readiness assessment
        production_readiness = self._assess_overall_production_readiness(model_results, comparative_analysis)
        
        # Generate recommendations
        recommendations = self._generate_comprehensive_recommendations(
            model_results, comparative_analysis, production_readiness
        )
        
        # Determine compliance status
        compliance_status = self._determine_compliance_status(production_readiness)
        
        # Calculate overall bias score
        overall_bias_score = self._calculate_overall_bias_score(model_results)
        
        # Create comprehensive report
        report = ComprehensiveBiasReport(
            timestamp=datetime.now().isoformat(),
            input_metadata=input_metadata,
            model_results=model_results,
            comparative_analysis=comparative_analysis,
            production_readiness=production_readiness,
            recommendations=recommendations,
            compliance_status=compliance_status,
            overall_bias_score=overall_bias_score
        )
        
        # Store in history
        self.evaluation_history.append(report)
        
        # Generate audit reports if enabled
        if self.config.generate_audit_reports:
            self._generate_audit_reports(report, evaluation_id)
            
        self.logger.info(f"Bias evaluation completed: {evaluation_id}")
        
        return report
        
    def _evaluate_single_model(self, 
                             legal_text: str,
                             summary: str,
                             model_name: str,
                             human_reference: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate a single model across all bias dimensions"""
        
        results = {}
        
        # 1. Ideological Bias Analysis
        try:
            # Create dummy multi-model dict for ideological analysis
            model_summaries = {model_name: summary}
            ideological_analysis = self.ideological_detector.analyze_bias_across_models(
                legal_text, model_summaries
            )
            results['ideological_bias'] = ideological_analysis
            
        except Exception as e:
            self.logger.error(f"Ideological bias analysis failed for {model_name}: {e}")
            results['ideological_bias'] = {'error': str(e)}
            
        # 2. Compliance Preservation Analysis
        try:
            compliance_analysis = self.compliance_analyzer.analyze_information_loss(
                legal_text, summary, self.config.target_preservation_rate
            )
            results['compliance_preservation'] = asdict(compliance_analysis)
            
        except Exception as e:
            self.logger.error(f"Compliance analysis failed for {model_name}: {e}")
            results['compliance_preservation'] = {'error': str(e)}
            
        # 3. Traceability Analysis
        try:
            traceability_analysis = self.traceability_engine.create_attribution_map(
                legal_text, summary, enable_audit=True
            )
            
            # Convert dataclass to dict for JSON serialization
            traceability_dict = {
                'overall_traceability': traceability_analysis.overall_traceability,
                'hallucination_risk': traceability_analysis.hallucination_risk,
                'coverage_analysis': traceability_analysis.coverage_analysis,
                'explainability_available': len(traceability_analysis.explainability_api) > 0,
                'audit_metadata': traceability_analysis.audit_metadata
            }
            
            results['traceability'] = traceability_dict
            
        except Exception as e:
            self.logger.error(f"Traceability analysis failed for {model_name}: {e}")
            results['traceability'] = {'error': str(e)}
            
        # 4. Additional Quality Metrics
        results['additional_metrics'] = self._calculate_additional_metrics(
            legal_text, summary, human_reference
        )
        
        # 5. Model-specific bias score
        results['model_bias_score'] = self._calculate_model_bias_score(results)
        
        # 6. Production readiness for this model
        results['production_readiness'] = self._assess_model_production_readiness(results)
        
        return results
        
    def _generate_input_metadata(self, 
                               legal_text: str,
                               model_summaries: Dict[str, str],
                               human_reference: Optional[str] = None) -> Dict[str, Any]:
        """Generate metadata about the input texts"""
        
        metadata = {
            'original_text': {
                'length_chars': len(legal_text),
                'length_words': len(legal_text.split()),
                'legal_domain': self._classify_legal_domain(legal_text),
                'jurisdiction': self._detect_jurisdiction(legal_text),
                'complexity_score': self._calculate_text_complexity(legal_text)
            },
            'summaries': {},
            'evaluation_config': asdict(self.config)
        }
        
        for model_name, summary in model_summaries.items():
            metadata['summaries'][model_name] = {
                'length_chars': len(summary),
                'length_words': len(summary.split()),
                'compression_ratio': len(summary.split()) / len(legal_text.split())
            }
            
        if human_reference:
            metadata['human_reference'] = {
                'length_chars': len(human_reference),
                'length_words': len(human_reference.split()),
                'compression_ratio': len(human_reference.split()) / len(legal_text.split())
            }
            
        return metadata
        
    def _classify_legal_domain(self, text: str) -> str:
        """Classify the legal domain of the text"""
        
        text_lower = text.lower()
        
        domain_indicators = {
            'contracts': ['contrato', 'cláusula', 'prestación', 'obligación contractual'],
            'governance': ['directorio', 'asamblea', 'gobierno corporativo', 'consejo'],
            'compliance': ['cumplimiento', 'normativa', 'regulación', 'infracción'],
            'civil': ['código civil', 'derechos civiles', 'responsabilidad civil'],
            'commercial': ['comercial', 'mercantil', 'sociedad anónima', 'empresa'],
            'labor': ['laboral', 'trabajador', 'empleador', 'contrato de trabajo'],
            'tax': ['tributario', 'impuesto', 'fiscal', 'hacienda'],
            'administrative': ['administrativo', 'procedimiento administrativo', 'resolución']
        }
        
        domain_scores = {}
        for domain, indicators in domain_indicators.items():
            score = sum(text_lower.count(indicator) for indicator in indicators)
            domain_scores[domain] = score
            
        return max(domain_scores, key=domain_scores.get) if any(domain_scores.values()) else 'general'
        
    def _detect_jurisdiction(self, text: str) -> str:
        """Detect the legal jurisdiction"""
        
        text_lower = text.lower()
        
        jurisdiction_indicators = {
            'AR': ['argentina', 'código civil y comercial', 'bcra', 'afip'],
            'ES': ['españa', 'código civil español', 'tribunal supremo'],
            'CL': ['chile', 'código civil chileno', 'superintendencia'],
            'UY': ['uruguay', 'código civil uruguayo', 'brou'],
            'MX': ['méxico', 'código civil federal', 'sat'],
            'CO': ['colombia', 'código civil colombiano', 'superfinanciera']
        }
        
        for jurisdiction, indicators in jurisdiction_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return jurisdiction
                
        return 'MULTI'  # Multi-jurisdictional or unclear
        
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1)"""
        
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return 0.0
            
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Legal term density
        legal_terms = ['artículo', 'inciso', 'párrafo', 'cláusula', 'disposición', 
                      'normativa', 'reglamento', 'decreto', 'resolución']
        legal_density = sum(text.lower().count(term) for term in legal_terms) / len(words)
        
        # Combine factors (normalized to 0-1)
        complexity = (
            min(avg_sentence_length / 25, 1.0) * 0.4 +  # Sentence complexity
            min(avg_word_length / 10, 1.0) * 0.3 +      # Word complexity
            min(legal_density * 100, 1.0) * 0.3         # Legal density
        )
        
        return complexity
        
    def _calculate_additional_metrics(self, 
                                    legal_text: str,
                                    summary: str,
                                    human_reference: Optional[str] = None) -> Dict[str, Any]:
        """Calculate additional quality metrics"""
        
        metrics = {}
        
        # Readability metrics
        metrics['readability'] = self._calculate_readability_metrics(summary)
        
        # Factual consistency (basic)
        metrics['factual_consistency'] = self._estimate_factual_consistency(legal_text, summary)
        
        # Information density
        metrics['information_density'] = self._calculate_information_density(summary)
        
        # Legal terminology preservation
        metrics['legal_terminology'] = self._analyze_legal_terminology_preservation(legal_text, summary)
        
        # If human reference available, compare
        if human_reference:
            metrics['human_comparison'] = self._compare_with_human_reference(summary, human_reference)
            
        return metrics
        
    def _calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics for Spanish text"""
        
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return {'avg_sentence_length': 0, 'avg_word_length': 0, 'readability_score': 0}
            
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word.strip('.,;:')) for word in words) / len(words)
        
        # Simplified readability score (similar to Flesch)
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / 4.7))
        readability_score = max(0, min(100, readability_score)) / 100  # Normalize to 0-1
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'readability_score': readability_score
        }
        
    def _estimate_factual_consistency(self, original: str, summary: str) -> float:
        """Estimate factual consistency between original and summary"""
        
        # Extract key facts (numbers, dates, names)
        import re
        
        def extract_facts(text):
            facts = set()
            # Numbers
            facts.update(re.findall(r'\d+(?:[.,]\d+)*', text))
            # Dates
            facts.update(re.findall(r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', text))
            # Legal references
            facts.update(re.findall(r'artículo\s+\d+', text.lower()))
            facts.update(re.findall(r'ley\s+\d+', text.lower()))
            return facts
            
        original_facts = extract_facts(original)
        summary_facts = extract_facts(summary)
        
        if not summary_facts:
            return 1.0  # No facts to check
            
        # Calculate consistency
        consistent_facts = summary_facts.intersection(original_facts)
        consistency = len(consistent_facts) / len(summary_facts)
        
        return consistency
        
    def _calculate_information_density(self, text: str) -> float:
        """Calculate information density (content words per total words)"""
        
        words = text.lower().split()
        
        # Spanish stop words (basic set)
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 
            'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las',
            'una', 'está', 'fue', 'han', 'más', 'pero', 'sus', 'me', 'ya', 'muy'
        }
        
        content_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return len(content_words) / len(words) if words else 0
        
    def _analyze_legal_terminology_preservation(self, original: str, summary: str) -> Dict[str, Any]:
        """Analyze how well legal terminology is preserved"""
        
        legal_terms = [
            'artículo', 'inciso', 'párrafo', 'cláusula', 'disposición',
            'normativa', 'reglamento', 'decreto', 'resolución', 'ley',
            'derecho', 'obligación', 'responsabilidad', 'sanción', 'multa'
        ]
        
        original_lower = original.lower()
        summary_lower = summary.lower()
        
        original_terms = {}
        summary_terms = {}
        
        for term in legal_terms:
            original_terms[term] = original_lower.count(term)
            summary_terms[term] = summary_lower.count(term)
            
        # Calculate preservation rates
        preservation_rates = {}
        for term in legal_terms:
            if original_terms[term] > 0:
                preservation_rates[term] = min(summary_terms[term] / original_terms[term], 1.0)
            else:
                preservation_rates[term] = 1.0  # No term to preserve
                
        overall_preservation = np.mean(list(preservation_rates.values()))
        
        return {
            'original_term_counts': original_terms,
            'summary_term_counts': summary_terms,
            'preservation_rates': preservation_rates,
            'overall_preservation': overall_preservation
        }
        
    def _compare_with_human_reference(self, summary: str, human_reference: str) -> Dict[str, float]:
        """Compare model summary with human reference"""
        
        # Simple comparison metrics
        summary_words = set(summary.lower().split())
        reference_words = set(human_reference.lower().split())
        
        # Jaccard similarity
        intersection = summary_words.intersection(reference_words)
        union = summary_words.union(reference_words)
        jaccard = len(intersection) / len(union) if union else 0
        
        # Length similarity
        length_ratio = min(len(summary), len(human_reference)) / max(len(summary), len(human_reference))
        
        return {
            'jaccard_similarity': jaccard,
            'length_similarity': length_ratio,
            'word_overlap': len(intersection) / len(summary_words) if summary_words else 0
        }
        
    def _calculate_model_bias_score(self, model_results: Dict[str, Any]) -> float:
        """Calculate overall bias score for a single model"""
        
        bias_components = {}
        
        # Ideological bias component
        if 'ideological_bias' in model_results and 'error' not in model_results['ideological_bias']:
            ideological_data = model_results['ideological_bias']
            if 'bias_assessment' in ideological_data:
                bias_components['ideological'] = ideological_data['bias_assessment']['average_bias_score']
            
        # Compliance bias component (information loss as bias)
        if 'compliance_preservation' in model_results and 'error' not in model_results['compliance_preservation']:
            compliance_data = model_results['compliance_preservation']
            compliance_loss = 1 - compliance_data['overall_preservation']
            bias_components['compliance'] = compliance_loss
            
        # Traceability bias component (hallucination risk as bias)  
        if 'traceability' in model_results and 'error' not in model_results['traceability']:
            traceability_data = model_results['traceability']
            bias_components['traceability'] = traceability_data['hallucination_risk']
            
        # Calculate weighted average
        if not bias_components:
            return 0.5  # Unknown/error state
            
        weights = {'ideological': 0.4, 'compliance': 0.4, 'traceability': 0.2}
        
        weighted_score = 0
        total_weight = 0
        
        for component, score in bias_components.items():
            weight = weights.get(component, 0.33)
            weighted_score += score * weight
            total_weight += weight
            
        return weighted_score / total_weight if total_weight > 0 else 0.5
        
    def _assess_model_production_readiness(self, model_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess production readiness for a single model"""
        
        criteria = {}
        
        # Bias score threshold
        model_bias = model_results.get('model_bias_score', 1.0)
        criteria['acceptable_bias'] = model_bias <= self.config.max_bias_score
        
        # Compliance preservation threshold
        if 'compliance_preservation' in model_results and 'error' not in model_results['compliance_preservation']:
            preservation = model_results['compliance_preservation']['overall_preservation']
            criteria['sufficient_compliance'] = preservation >= self.config.target_preservation_rate
        else:
            criteria['sufficient_compliance'] = False
            
        # Traceability threshold
        if 'traceability' in model_results and 'error' not in model_results['traceability']:
            traceability = model_results['traceability']['overall_traceability']
            hallucination_risk = model_results['traceability']['hallucination_risk']
            
            criteria['sufficient_traceability'] = traceability >= self.config.min_traceability_score
            criteria['acceptable_hallucination_risk'] = hallucination_risk <= self.config.max_hallucination_risk
        else:
            criteria['sufficient_traceability'] = False
            criteria['acceptable_hallucination_risk'] = False
            
        # Overall readiness
        production_ready = all(criteria.values())
        
        return {
            'production_ready': production_ready,
            'criteria_met': criteria,
            'blocking_issues': [criterion for criterion, met in criteria.items() if not met]
        }
        
    def _perform_comparative_analysis(self, model_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comparative analysis across models"""
        
        if len(model_results) < 2:
            return {'note': 'Comparative analysis requires at least 2 models'}
            
        analysis = {}
        
        # Compare bias scores
        bias_scores = {model: results['model_bias_score'] for model, results in model_results.items()}
        analysis['bias_score_comparison'] = {
            'scores': bias_scores,
            'best_model': min(bias_scores, key=bias_scores.get),
            'worst_model': max(bias_scores, key=bias_scores.get),
            'score_variance': float(np.var(list(bias_scores.values())))
        }
        
        # Compare compliance preservation
        compliance_scores = {}
        for model, results in model_results.items():
            if 'compliance_preservation' in results and 'error' not in results['compliance_preservation']:
                compliance_scores[model] = results['compliance_preservation']['overall_preservation']
                
        if compliance_scores:
            analysis['compliance_comparison'] = {
                'scores': compliance_scores,
                'best_model': max(compliance_scores, key=compliance_scores.get),
                'worst_model': min(compliance_scores, key=compliance_scores.get),
                'score_variance': float(np.var(list(compliance_scores.values())))
            }
            
        # Compare traceability
        traceability_scores = {}
        for model, results in model_results.items():
            if 'traceability' in results and 'error' not in results['traceability']:
                traceability_scores[model] = results['traceability']['overall_traceability']
                
        if traceability_scores:
            analysis['traceability_comparison'] = {
                'scores': traceability_scores,
                'best_model': max(traceability_scores, key=traceability_scores.get),
                'worst_model': min(traceability_scores, key=traceability_scores.get),
                'score_variance': float(np.var(list(traceability_scores.values())))
            }
            
        # Cross-model consistency analysis
        analysis['consistency_analysis'] = self._analyze_cross_model_consistency(model_results)
        
        return analysis
        
    def _analyze_cross_model_consistency(self, model_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consistency across different models"""
        
        consistency_metrics = {}
        
        # Ideological consistency
        ideological_leans = {}
        for model, results in model_results.items():
            if 'ideological_bias' in results and 'error' not in results['ideological_bias']:
                # Extract ideological scores if available
                if 'individual_analyses' in results['ideological_bias']:
                    for analysis in results['ideological_bias']['individual_analyses'].values():
                        if hasattr(analysis, 'ideological_lean'):
                            ideological_leans[model] = analysis.ideological_lean
                            
        if len(ideological_leans) > 1:
            # Calculate variance in ideological scores
            ideologies = ['progressive', 'conservative', 'libertarian', 'statist']
            ideology_variances = {}
            
            for ideology in ideologies:
                scores = [lean.get(ideology, 0) for lean in ideological_leans.values()]
                ideology_variances[ideology] = float(np.var(scores))
                
            consistency_metrics['ideological_consistency'] = {
                'ideology_variances': ideology_variances,
                'max_variance': max(ideology_variances.values()) if ideology_variances else 0,
                'consistent': max(ideology_variances.values()) < 0.5 if ideology_variances else True
            }
            
        return consistency_metrics
        
    def _assess_overall_production_readiness(self, 
                                           model_results: Dict[str, Dict[str, Any]],
                                           comparative_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall production readiness across all models"""
        
        readiness_summary = {}
        
        # Individual model readiness
        model_readiness = {}
        for model, results in model_results.items():
            model_readiness[model] = results['production_readiness']
            
        readiness_summary['individual_models'] = model_readiness
        
        # Count production-ready models
        ready_models = [model for model, readiness in model_readiness.items() 
                       if readiness['production_ready']]
        
        readiness_summary['ready_models'] = ready_models
        readiness_summary['ready_model_count'] = len(ready_models)
        readiness_summary['total_models'] = len(model_readiness)
        
        # Overall recommendation
        if len(ready_models) == 0:
            recommendation = "NO_DEPLOY"
        elif len(ready_models) == 1:
            recommendation = "DEPLOY_SINGLE"
        else:
            recommendation = "DEPLOY_ENSEMBLE"
            
        readiness_summary['deployment_recommendation'] = recommendation
        
        # Cross-model consistency check
        if 'consistency_analysis' in comparative_analysis:
            consistency = comparative_analysis['consistency_analysis']
            if 'ideological_consistency' in consistency:
                ideological_consistent = consistency['ideological_consistency']['consistent']
                readiness_summary['ideological_consistency_ok'] = ideological_consistent
            else:
                readiness_summary['ideological_consistency_ok'] = True
        else:
            readiness_summary['ideological_consistency_ok'] = True
            
        return readiness_summary
        
    def _generate_comprehensive_recommendations(self, 
                                              model_results: Dict[str, Dict[str, Any]],
                                              comparative_analysis: Dict[str, Any],
                                              production_readiness: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations based on analysis"""
        
        recommendations = []
        
        # Deployment recommendations
        deployment_rec = production_readiness['deployment_recommendation']
        
        if deployment_rec == "NO_DEPLOY":
            recommendations.append("🚫 CRÍTICO: Ningún modelo cumple estándares de producción. Revisar entrenamiento.")
        elif deployment_rec == "DEPLOY_SINGLE":
            ready_model = production_readiness['ready_models'][0]
            recommendations.append(f"✅ Desplegar modelo único: {ready_model}")
        elif deployment_rec == "DEPLOY_ENSEMBLE":
            ready_models = production_readiness['ready_models']
            recommendations.append(f"🎯 RECOMENDADO: Ensemble con modelos: {', '.join(ready_models)}")
            
        # Bias-specific recommendations
        for model, results in model_results.items():
            model_bias = results['model_bias_score']
            
            if model_bias > self.config.max_bias_score:
                recommendations.append(
                    f"⚠️ {model}: Implementar regularización anti-sesgo (score actual: {model_bias:.3f})"
                )
                
        # Compliance recommendations
        low_compliance_models = []
        for model, results in model_results.items():
            if 'compliance_preservation' in results and 'error' not in results['compliance_preservation']:
                compliance = results['compliance_preservation']['overall_preservation']
                if compliance < self.config.target_preservation_rate:
                    low_compliance_models.append(model)
                    
        if low_compliance_models:
            recommendations.append(
                f"📋 Mejorar preservación de cumplimiento en: {', '.join(low_compliance_models)}"
            )
            
        # Traceability recommendations
        high_hallucination_models = []
        for model, results in model_results.items():
            if 'traceability' in results and 'error' not in results['traceability']:
                hallucination_risk = results['traceability']['hallucination_risk']
                if hallucination_risk > self.config.max_hallucination_risk:
                    high_hallucination_models.append(model)
                    
        if high_hallucination_models:
            recommendations.append(
                f"🔍 Reducir riesgo de alucinación en: {', '.join(high_hallucination_models)}"
            )
            
        # Consistency recommendations
        if not production_readiness.get('ideological_consistency_ok', True):
            recommendations.append("⚖️ Mejorar consistencia ideológica entre modelos")
            
        # Monitoring recommendations
        recommendations.append("📊 Implementar monitoreo continuo de métricas de sesgo en producción")
        recommendations.append("🔄 Programar re-evaluación cada 30 días o tras cambios en el modelo")
        
        return recommendations
        
    def _determine_compliance_status(self, production_readiness: Dict[str, Any]) -> str:
        """Determine overall compliance status"""
        
        ready_count = production_readiness['ready_model_count']
        total_count = production_readiness['total_models']
        
        if ready_count == 0:
            return "NON_COMPLIANT"
        elif ready_count < total_count:
            return "PARTIALLY_COMPLIANT"
        else:
            return "FULLY_COMPLIANT"
            
    def _calculate_overall_bias_score(self, model_results: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall bias score across all models"""
        
        bias_scores = [results['model_bias_score'] for results in model_results.values()]
        return float(np.mean(bias_scores))
        
    def _generate_audit_reports(self, report: ComprehensiveBiasReport, evaluation_id: str):
        """Generate detailed audit reports"""
        
        # Create reports directory
        reports_dir = Path("bias_evaluation_reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Generate JSON report
        json_report_path = reports_dir / f"{evaluation_id}_bias_evaluation.json"
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
            
        # Generate human-readable report
        readable_report_path = reports_dir / f"{evaluation_id}_bias_report.md"
        readable_content = self._generate_readable_report(report)
        
        with open(readable_report_path, 'w', encoding='utf-8') as f:
            f.write(readable_content)
            
        self.logger.info(f"Audit reports generated: {json_report_path}, {readable_report_path}")
        
    def _generate_readable_report(self, report: ComprehensiveBiasReport) -> str:
        """Generate human-readable bias evaluation report"""
        
        lines = []
        
        lines.append("# REPORTE DE EVALUACIÓN DE SESGO - IA LEGAL")
        lines.append("=" * 55)
        lines.append(f"\n**Fecha**: {report.timestamp}")
        lines.append(f"**Estado de Cumplimiento**: {report.compliance_status}")
        lines.append(f"**Score de Sesgo General**: {report.overall_bias_score:.3f}")
        
        # Executive summary
        lines.append(f"\n## Resumen Ejecutivo")
        
        if report.compliance_status == "FULLY_COMPLIANT":
            lines.append("✅ **APROBADO**: Todos los modelos cumplen estándares anti-sesgo")
        elif report.compliance_status == "PARTIALLY_COMPLIANT":
            lines.append("⚠️ **REVISIÓN PARCIAL**: Algunos modelos requieren mejoras")
        else:
            lines.append("❌ **NO APROBADO**: Los modelos no cumplen estándares mínimos")
            
        # Model results summary
        lines.append(f"\n## Resultados por Modelo")
        lines.append("-" * 25)
        
        for model_name, results in report.model_results.items():
            bias_score = results['model_bias_score']
            ready = results['production_readiness']['production_ready']
            
            status_icon = "✅" if ready else "❌"
            lines.append(f"\n### {status_icon} {model_name}")
            lines.append(f"- **Score de Sesgo**: {bias_score:.3f}")
            lines.append(f"- **Listo para Producción**: {'Sí' if ready else 'No'}")
            
            if not ready:
                blocking_issues = results['production_readiness']['blocking_issues']
                lines.append(f"- **Problemas**: {', '.join(blocking_issues)}")
                
        # Recommendations
        lines.append(f"\n## Recomendaciones")
        lines.append("-" * 15)
        
        for i, recommendation in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {recommendation}")
            
        # Technical details
        lines.append(f"\n## Detalles Técnicos")
        lines.append(f"- **Modelos Evaluados**: {len(report.model_results)}")
        lines.append(f"- **Texto Original**: {report.input_metadata['original_text']['length_words']} palabras")
        lines.append(f"- **Dominio Legal**: {report.input_metadata['original_text']['legal_domain']}")
        lines.append(f"- **Jurisdicción**: {report.input_metadata['original_text']['jurisdiction']}")
        
        lines.append(f"\n---")
        lines.append(f"*Reporte generado por Legal Bias Evaluation Framework v1.0*")
        
        return "\n".join(lines)
        
    def get_evaluation_trends(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get trends from evaluation history"""
        
        if not self.evaluation_history:
            return {'note': 'No evaluation history available'}
            
        trends = {}
        
        # Overall bias score trend
        bias_scores = [report.overall_bias_score for report in self.evaluation_history]
        trends['overall_bias_trend'] = {
            'scores': bias_scores,
            'trend_direction': 'improving' if len(bias_scores) > 1 and bias_scores[-1] < bias_scores[0] else 'stable_or_worsening'
        }
        
        # Model-specific trends
        if model_name:
            model_scores = []
            for report in self.evaluation_history:
                if model_name in report.model_results:
                    model_scores.append(report.model_results[model_name]['model_bias_score'])
                    
            trends['model_specific_trend'] = {
                'model': model_name,
                'scores': model_scores,
                'trend_direction': 'improving' if len(model_scores) > 1 and model_scores[-1] < model_scores[0] else 'stable_or_worsening'
            }
            
        return trends