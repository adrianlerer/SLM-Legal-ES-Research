"""
Comprehensive Bias Evaluation Framework for Legal AI Systems
Integrates all bias detection components into unified evaluation system
Based on research: Complete anti-bias framework for legal AI
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import json
from pathlib import Path

from .ideological_bias import IdeologicalBiasDetector
from .compliance_preservation import CompliancePreservationAnalyzer  
from .traceability import LegalTraceabilityEngine

@dataclass
class ComprehensiveBiasReport:
    """Complete bias evaluation report"""
    evaluation_id: str
    timestamp: str
    input_metadata: Dict[str, Any]
    ideological_analysis: Dict[str, Any]
    compliance_analysis: Dict[str, Any]
    traceability_analysis: Dict[str, Any]
    overall_bias_assessment: Dict[str, Any]
    production_readiness: Dict[str, Any]
    recommendations: List[str]
    audit_trail: Dict[str, Any]

class LegalBiasEvaluationFramework:
    """
    Comprehensive framework for evaluating biases in legal AI systems
    
    Integrates:
    - Ideological bias detection
    - Compliance information preservation
    - Traceability and explainability analysis
    - Production readiness assessment
    - Automated recommendations
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 enable_logging: bool = True):
        
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        if enable_logging:
            self._setup_logging()
            
        # Initialize bias detection components
        self.ideological_detector = IdeologicalBiasDetector()
        self.compliance_analyzer = CompliancePreservationAnalyzer()
        self.traceability_engine = LegalTraceabilityEngine()
        
        # Evaluation thresholds
        self.thresholds = self.config.get('thresholds', {
            'max_bias_score': 0.3,
            'min_compliance_preservation': 0.85,
            'max_hallucination_risk': 0.05,
            'min_traceability_score': 0.8,
            'min_overall_score': 0.75
        })
        
    def comprehensive_bias_evaluation(self, 
                                    legal_text: str,
                                    model_summaries: Dict[str, str],
                                    human_reference: Optional[str] = None,
                                    evaluation_context: Optional[Dict[str, Any]] = None) -> ComprehensiveBiasReport:
        """
        Perform comprehensive bias evaluation across all dimensions
        
        Args:
            legal_text: Original legal document
            model_summaries: Dictionary of model_name -> summary pairs
            human_reference: Optional human-generated reference summary
            evaluation_context: Additional context (jurisdiction, document type, etc.)
            
        Returns:
            Complete bias evaluation report
        """
        
        evaluation_id = self._generate_evaluation_id()
        
        self.logger.info(f"Starting comprehensive bias evaluation: {evaluation_id}")
        
        # Prepare input metadata
        input_metadata = self._prepare_input_metadata(
            legal_text, model_summaries, evaluation_context
        )
        
        try:
            # 1. Ideological Bias Analysis
            self.logger.info("Performing ideological bias analysis...")
            ideological_analysis = self.ideological_detector.analyze_bias_across_models(
                legal_text, model_summaries
            )
            
            # 2. Compliance Preservation Analysis
            self.logger.info("Performing compliance preservation analysis...")
            compliance_results = {}
            for model_name, summary in model_summaries.items():
                compliance_result = self.compliance_analyzer.analyze_information_loss(
                    legal_text, summary
                )
                compliance_results[model_name] = asdict(compliance_result)
                
            # 3. Traceability Analysis
            self.logger.info("Performing traceability analysis...")
            traceability_results = {}
            for model_name, summary in model_summaries.items():
                traceability_result = self.traceability_engine.create_attribution_map(
                    legal_text, summary
                )
                traceability_results[model_name] = asdict(traceability_result)
                
            # 4. Cross-analysis integration
            self.logger.info("Integrating cross-analysis results...")
            integrated_analysis = self._integrate_analyses(
                ideological_analysis, compliance_results, traceability_results
            )
            
            # 5. Overall bias assessment
            overall_bias_assessment = self._calculate_overall_bias_assessment(
                ideological_analysis, compliance_results, traceability_results,
                human_reference, model_summaries
            )
            
            # 6. Production readiness assessment
            production_readiness = self._assess_comprehensive_production_readiness(
                overall_bias_assessment, integrated_analysis
            )
            
            # 7. Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                overall_bias_assessment, production_readiness, integrated_analysis
            )
            
            # 8. Create audit trail
            audit_trail = self._create_audit_trail(
                evaluation_id, input_metadata, ideological_analysis,
                compliance_results, traceability_results
            )
            
            # Compile comprehensive report
            report = ComprehensiveBiasReport(
                evaluation_id=evaluation_id,
                timestamp=datetime.now().isoformat(),
                input_metadata=input_metadata,
                ideological_analysis=ideological_analysis,
                compliance_analysis=compliance_results,
                traceability_analysis=traceability_results,
                overall_bias_assessment=overall_bias_assessment,
                production_readiness=production_readiness,
                recommendations=recommendations,
                audit_trail=audit_trail
            )
            
            self.logger.info(f"Bias evaluation completed successfully: {evaluation_id}")
            
            # Save report if configured
            if self.config.get('save_reports', True):
                self._save_evaluation_report(report)
                
            return report
            
        except Exception as e:
            self.logger.error(f"Bias evaluation failed: {str(e)}")
            raise
            
    def _prepare_input_metadata(self, 
                              legal_text: str,
                              model_summaries: Dict[str, str],
                              evaluation_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare comprehensive input metadata"""
        
        metadata = {
            'text_statistics': {
                'original_length_chars': len(legal_text),
                'original_length_words': len(legal_text.split()),
                'original_length_sentences': len(self._count_sentences(legal_text))
            },
            'model_summaries': {},
            'evaluation_context': evaluation_context or {},
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Analyze each model summary
        for model_name, summary in model_summaries.items():
            metadata['model_summaries'][model_name] = {
                'length_chars': len(summary),
                'length_words': len(summary.split()),
                'length_sentences': len(self._count_sentences(summary)),
                'compression_ratio': len(summary.split()) / len(legal_text.split()),
                'legal_domain': self._classify_legal_domain(legal_text),
                'jurisdiction': self._detect_jurisdiction(legal_text, evaluation_context)
            }
            
        return metadata
        
    def _integrate_analyses(self, 
                          ideological: Dict[str, Any],
                          compliance: Dict[str, Any],
                          traceability: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate results from different bias analyses"""
        
        integration = {
            'cross_model_consistency': {},
            'bias_correlation_analysis': {},
            'critical_issues_summary': [],
            'strengths_summary': []
        }
        
        # Analyze cross-model consistency
        for model_name in ideological['individual_analyses'].keys():
            
            ideological_score = ideological['individual_analyses'][model_name].bias_indicators['overall_bias_score']
            compliance_score = 1 - compliance[model_name]['overall_preservation']  # Convert to bias score
            traceability_score = 1 - traceability[model_name]['overall_traceability']  # Convert to bias score
            
            integration['cross_model_consistency'][model_name] = {
                'ideological_bias': ideological_score,
                'compliance_bias': compliance_score,
                'traceability_bias': traceability_score,
                'consistency_variance': np.var([ideological_score, compliance_score, traceability_score]),
                'overall_consistency': 'high' if np.var([ideological_score, compliance_score, traceability_score]) < 0.05 else 'low'
            }
            
        # Identify correlated bias patterns
        integration['bias_correlation_analysis'] = self._analyze_bias_correlations(
            ideological, compliance, traceability
        )
        
        # Summarize critical issues
        for model_name in ideological['individual_analyses'].keys():
            issues = []
            
            if ideological['individual_analyses'][model_name].bias_indicators['overall_bias_score'] > 0.5:
                issues.append("High ideological bias detected")
                
            if compliance[model_name]['overall_preservation'] < 0.7:
                issues.append("Significant information loss")
                
            if traceability[model_name]['hallucination_risk'] > 0.1:
                issues.append("High hallucination risk")
                
            if issues:
                integration['critical_issues_summary'].append({
                    'model': model_name,
                    'issues': issues
                })
                
        return integration
        
    def _calculate_overall_bias_assessment(self, 
                                         ideological: Dict[str, Any],
                                         compliance: Dict[str, Any], 
                                         traceability: Dict[str, Any],
                                         human_reference: Optional[str],
                                         model_summaries: Dict[str, str]) -> Dict[str, Any]:
        """Calculate comprehensive overall bias assessment"""
        
        assessment = {
            'model_scores': {},
            'aggregate_metrics': {},
            'bias_severity_classification': {},
            'human_comparison': {}
        }
        
        # Calculate scores per model
        for model_name in model_summaries.keys():
            
            # Individual component scores
            ideological_score = ideological['individual_analyses'][model_name].bias_indicators['overall_bias_score']
            compliance_score = 1 - compliance[model_name]['overall_preservation']  
            traceability_score = traceability[model_name]['hallucination_risk']
            
            # Weighted overall score
            weights = self.config.get('bias_weights', {
                'ideological': 0.35,
                'compliance': 0.40, 
                'traceability': 0.25
            })
            
            overall_score = (
                ideological_score * weights['ideological'] +
                compliance_score * weights['compliance'] +
                traceability_score * weights['traceability']
            )
            
            assessment['model_scores'][model_name] = {
                'ideological_bias_score': float(ideological_score),
                'compliance_bias_score': float(compliance_score),
                'traceability_bias_score': float(traceability_score),
                'overall_bias_score': float(overall_score),
                'bias_severity': self._classify_bias_severity(overall_score)
            }
            
        # Aggregate metrics across all models
        all_scores = [scores['overall_bias_score'] for scores in assessment['model_scores'].values()]
        
        assessment['aggregate_metrics'] = {
            'mean_bias_score': float(np.mean(all_scores)),
            'bias_score_variance': float(np.var(all_scores)),
            'max_bias_score': float(np.max(all_scores)),
            'min_bias_score': float(np.min(all_scores)),
            'model_consistency': 'high' if np.var(all_scores) < 0.05 else 'medium' if np.var(all_scores) < 0.15 else 'low'
        }
        
        # Overall bias severity classification
        mean_score = assessment['aggregate_metrics']['mean_bias_score']
        assessment['bias_severity_classification'] = {
            'overall_severity': self._classify_bias_severity(mean_score),
            'consistent_across_models': assessment['aggregate_metrics']['model_consistency'] == 'high',
            'requires_intervention': mean_score > self.thresholds['max_bias_score']
        }
        
        # Human comparison if reference provided
        if human_reference:
            assessment['human_comparison'] = self._compare_with_human_reference(
                model_summaries, human_reference, ideological, compliance, traceability
            )
            
        return assessment
        
    def _classify_bias_severity(self, bias_score: float) -> str:
        """Classify bias severity level"""
        
        if bias_score <= 0.2:
            return "LOW"
        elif bias_score <= 0.4:
            return "MODERATE"
        elif bias_score <= 0.6:
            return "HIGH"
        else:
            return "CRITICAL"
            
    def _assess_comprehensive_production_readiness(self, 
                                                 bias_assessment: Dict[str, Any],
                                                 integrated_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive production readiness assessment"""
        
        readiness = {
            'overall_ready': False,
            'model_readiness': {},
            'blocking_issues': [],
            'warning_issues': [],
            'approval_recommendations': {}
        }
        
        # Assess each model
        models_ready = 0
        
        for model_name, scores in bias_assessment['model_scores'].items():
            
            model_checks = {
                'bias_score_acceptable': scores['overall_bias_score'] <= self.thresholds['max_bias_score'],
                'severity_acceptable': scores['bias_severity'] in ['LOW', 'MODERATE'],
                'no_critical_issues': model_name not in [
                    issue['model'] for issue in integrated_analysis['critical_issues_summary']
                ]
            }
            
            model_ready = all(model_checks.values())
            
            readiness['model_readiness'][model_name] = {
                'ready': model_ready,
                'checks': model_checks,
                'recommendation': 'APPROVE' if model_ready else 'REJECT'
            }
            
            if model_ready:
                models_ready += 1
            else:
                # Identify specific blocking issues
                if not model_checks['bias_score_acceptable']:
                    readiness['blocking_issues'].append(
                        f"{model_name}: Bias score too high ({scores['overall_bias_score']:.3f} > {self.thresholds['max_bias_score']})"
                    )
                    
                if not model_checks['severity_acceptable']:
                    readiness['blocking_issues'].append(
                        f"{model_name}: Bias severity unacceptable ({scores['bias_severity']})"
                    )
                    
        # Overall readiness
        readiness['overall_ready'] = models_ready > 0
        
        # Generate approval recommendations
        if models_ready == len(bias_assessment['model_scores']):
            readiness['approval_recommendations']['status'] = 'APPROVE_ALL'
            readiness['approval_recommendations']['message'] = 'All models meet bias criteria'
        elif models_ready > 0:
            readiness['approval_recommendations']['status'] = 'APPROVE_PARTIAL'
            readiness['approval_recommendations']['message'] = f'{models_ready}/{len(bias_assessment["model_scores"])} models ready'
        else:
            readiness['approval_recommendations']['status'] = 'REJECT_ALL'
            readiness['approval_recommendations']['message'] = 'No models meet bias criteria'
            
        return readiness
        
    def _generate_comprehensive_recommendations(self, 
                                             bias_assessment: Dict[str, Any],
                                             production_readiness: Dict[str, Any],
                                             integrated_analysis: Dict[str, Any]) -> List[str]:
        """Generate comprehensive improvement recommendations"""
        
        recommendations = []
        
        # High-level recommendations
        if not production_readiness['overall_ready']:
            recommendations.append(
                "🚨 CRITICAL: No models meet production bias criteria. Complete bias mitigation required."
            )
            
        # Specific bias type recommendations
        mean_bias = bias_assessment['aggregate_metrics']['mean_bias_score']
        
        if mean_bias > self.thresholds['max_bias_score']:
            recommendations.append(
                f"📊 Reduce overall bias score from {mean_bias:.3f} to below {self.thresholds['max_bias_score']}"
            )
            
        # Model consistency recommendations
        if bias_assessment['aggregate_metrics']['model_consistency'] == 'low':
            recommendations.append(
                "🔄 High variance between models detected. Consider ensemble approaches or model selection criteria."
            )
            
        # Specific component recommendations
        for model_name, scores in bias_assessment['model_scores'].items():
            
            model_recs = []
            
            if scores['ideological_bias_score'] > 0.3:
                model_recs.append("ideological bias regularization")
                
            if scores['compliance_bias_score'] > 0.3:
                model_recs.append("compliance preservation training")
                
            if scores['traceability_bias_score'] > 0.1:
                model_recs.append("attribution enhancement")
                
            if model_recs:
                recommendations.append(
                    f"🔧 {model_name}: Implement {', '.join(model_recs)}"
                )
                
        # Cross-analysis recommendations
        if integrated_analysis['critical_issues_summary']:
            recommendations.append(
                "⚠️ Critical issues identified across multiple bias dimensions. Comprehensive review required."
            )
            
        # Production deployment recommendations
        if production_readiness['overall_ready']:
            if production_readiness['approval_recommendations']['status'] == 'APPROVE_PARTIAL':
                recommendations.append(
                    "✅ Deploy only approved models. Continue development on rejected models."
                )
            else:
                recommendations.append(
                    "✅ All models approved for production deployment with continued monitoring."
                )
                
        # Monitoring recommendations
        recommendations.append(
            "📈 Implement continuous bias monitoring in production with automated alerts."
        )
        
        recommendations.append(
            "👥 Schedule regular expert review sessions for bias assessment validation."
        )
        
        return recommendations
        
    def _analyze_bias_correlations(self, 
                                 ideological: Dict[str, Any],
                                 compliance: Dict[str, Any], 
                                 traceability: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations between different types of bias"""
        
        correlations = {
            'ideological_compliance_correlation': 0.0,
            'ideological_traceability_correlation': 0.0,
            'compliance_traceability_correlation': 0.0,
            'correlation_patterns': []
        }
        
        # Extract bias scores for correlation analysis
        ideological_scores = []
        compliance_scores = []
        traceability_scores = []
        
        for model_name in ideological['individual_analyses'].keys():
            ideological_scores.append(
                ideological['individual_analyses'][model_name].bias_indicators['overall_bias_score']
            )
            compliance_scores.append(1 - compliance[model_name]['overall_preservation'])
            traceability_scores.append(traceability[model_name]['hallucination_risk'])
            
        # Calculate correlations if we have multiple models
        if len(ideological_scores) > 1:
            correlations['ideological_compliance_correlation'] = float(
                np.corrcoef(ideological_scores, compliance_scores)[0, 1]
            )
            correlations['ideological_traceability_correlation'] = float(
                np.corrcoef(ideological_scores, traceability_scores)[0, 1]
            )
            correlations['compliance_traceability_correlation'] = float(
                np.corrcoef(compliance_scores, traceability_scores)[0, 1]
            )
            
            # Identify correlation patterns
            if abs(correlations['ideological_compliance_correlation']) > 0.7:
                correlations['correlation_patterns'].append(
                    "Strong correlation between ideological bias and compliance preservation"
                )
                
            if abs(correlations['ideological_traceability_correlation']) > 0.7:
                correlations['correlation_patterns'].append(
                    "Strong correlation between ideological bias and traceability"
                )
                
            if abs(correlations['compliance_traceability_correlation']) > 0.7:
                correlations['correlation_patterns'].append(
                    "Strong correlation between compliance preservation and traceability"
                )
                
        return correlations
        
    def _compare_with_human_reference(self, 
                                    model_summaries: Dict[str, str],
                                    human_reference: str,
                                    ideological: Dict[str, Any],
                                    compliance: Dict[str, Any],
                                    traceability: Dict[str, Any]) -> Dict[str, Any]:
        """Compare model outputs with human reference"""
        
        # This would include similarity analysis, bias comparison with human reference
        # Simplified implementation for now
        comparison = {
            'human_reference_length': len(human_reference.split()),
            'model_vs_human_similarity': {},
            'bias_deviation_from_human': {}
        }
        
        # Calculate similarity between each model and human reference
        for model_name, summary in model_summaries.items():
            # Simple word overlap similarity (could be enhanced with semantic similarity)
            model_words = set(summary.lower().split())
            human_words = set(human_reference.lower().split())
            
            overlap = len(model_words.intersection(human_words))
            union = len(model_words.union(human_words))
            
            similarity = overlap / union if union > 0 else 0.0
            
            comparison['model_vs_human_similarity'][model_name] = similarity
            
        return comparison
        
    def _create_audit_trail(self, 
                          evaluation_id: str,
                          input_metadata: Dict[str, Any],
                          ideological_analysis: Dict[str, Any],
                          compliance_results: Dict[str, Any],
                          traceability_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive audit trail"""
        
        audit_trail = {
            'evaluation_id': evaluation_id,
            'framework_version': '1.0.0',
            'analysis_components': {
                'ideological_bias_detector': 'IdeologicalBiasDetector v1.0',
                'compliance_analyzer': 'CompliancePreservationAnalyzer v1.0',  
                'traceability_engine': 'LegalTraceabilityEngine v1.0'
            },
            'configuration': self.config,
            'thresholds_used': self.thresholds,
            'processing_metadata': {
                'start_time': input_metadata['analysis_timestamp'],
                'end_time': datetime.now().isoformat(),
                'total_models_analyzed': len(ideological_analysis['individual_analyses']),
                'analysis_successful': True
            },
            'data_lineage': {
                'input_text_hash': hash(str(input_metadata)),
                'model_outputs_hash': hash(str(ideological_analysis)),
                'configuration_hash': hash(str(self.config))
            }
        }
        
        return audit_trail
        
    def _save_evaluation_report(self, report: ComprehensiveBiasReport) -> None:
        """Save evaluation report to disk"""
        
        output_dir = Path(self.config.get('output_dir', './bias_evaluations'))
        output_dir.mkdir(exist_ok=True)
        
        filename = f"bias_evaluation_{report.evaluation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
                
            self.logger.info(f"Bias evaluation report saved: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save evaluation report: {e}")
            
    def _generate_evaluation_id(self) -> str:
        """Generate unique evaluation ID"""
        return f"bias_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now()) % 10000:04d}"
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        
        return {
            'thresholds': {
                'max_bias_score': 0.3,
                'min_compliance_preservation': 0.85,
                'max_hallucination_risk': 0.05,
                'min_traceability_score': 0.8
            },
            'bias_weights': {
                'ideological': 0.35,
                'compliance': 0.40,
                'traceability': 0.25
            },
            'save_reports': True,
            'output_dir': './bias_evaluations'
        }
        
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def _count_sentences(self, text: str) -> List[str]:
        """Count sentences in text"""
        
        # Simple sentence splitting
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        return sentences
        
    def _classify_legal_domain(self, text: str) -> str:
        """Classify legal domain of text"""
        
        text_lower = text.lower()
        
        domain_keywords = {
            'contracts': ['contrato', 'cláusula', 'obligación', 'prestación'],
            'corporate': ['sociedad', 'directorio', 'accionista', 'corporativo'],
            'compliance': ['cumplimiento', 'regulación', 'normativa', 'infracción'],
            'governance': ['gobierno', 'gobernanza', 'gestión', 'administración']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
                
        return 'general'
        
    def _detect_jurisdiction(self, 
                           text: str, 
                           context: Optional[Dict[str, Any]] = None) -> str:
        """Detect legal jurisdiction"""
        
        if context and 'jurisdiction' in context:
            return context['jurisdiction']
            
        # Simple jurisdiction detection based on text patterns
        text_lower = text.lower()
        
        if 'argentina' in text_lower or 'ccyc' in text_lower:
            return 'AR'
        elif 'chile' in text_lower or 'código civil chileno' in text_lower:
            return 'CL'
        elif 'uruguay' in text_lower:
            return 'UY'
        elif 'españa' in text_lower or 'código civil español' in text_lower:
            return 'ES'
        else:
            return 'UNKNOWN'