"""
Legal Evaluation Metrics for SCM Legal - Comprehensive evaluation framework
Academic research implementation for paper publication

This module implements specialized evaluation metrics for legal AI systems,
focusing on concept-level accuracy, reasoning coherence, and domain expertise.
"""

import json
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import logging

logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    """Container for evaluation results"""
    metric_name: str
    score: float
    confidence_interval: Optional[Tuple[float, float]] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class ConceptEvaluationSample:
    """Sample for concept-level evaluation"""
    text: str
    predicted_concepts: List[str]
    ground_truth_concepts: List[str]
    predicted_reasoning: List[Dict[str, Any]]
    ground_truth_reasoning: List[Dict[str, Any]]
    jurisdiction: str
    legal_category: str
    
class LegalEvaluationMetrics:
    """
    Comprehensive evaluation metrics for legal AI systems
    
    Metrics include:
    - Concept extraction accuracy (Precision, Recall, F1)
    - Legal reasoning coherence
    - Multi-jurisdictional consistency
    - Regulatory compliance understanding
    - Analogical reasoning capability
    - Causal relationship detection
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_evaluation_framework()
        
    def setup_evaluation_framework(self):
        """Initialize evaluation components"""
        
        # ROUGE scorer for text similarity
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'], 
            use_stemmer=True
        )
        
        # BLEU smoothing function
        self.bleu_smoother = SmoothingFunction()
        
        # Legal domain knowledge for validation
        self.setup_legal_knowledge_base()
        
    def setup_legal_knowledge_base(self):
        """Set up legal knowledge base for validation"""
        
        # Legal concept categories and their relationships
        self.legal_categories = {
            'constitutional': {
                'concepts': ['derechos_fundamentales', 'debido_proceso', 'igualdad_ante_ley'],
                'weight': 0.95  # High importance
            },
            'civil': {
                'concepts': ['contrato_compraventa', 'responsabilidad_civil', 'consentimiento'],
                'weight': 0.85
            },
            'commercial': {
                'concepts': ['sociedad_anonima', 'gobierno_corporativo', 'capital_social'],
                'weight': 0.8
            },
            'labor': {
                'concepts': ['contrato_trabajo', 'subordinacion', 'proteccion_laboral'],
                'weight': 0.85
            },
            'administrative': {
                'concepts': ['acto_administrativo', 'procedimiento_administrativo', 'competencia'],
                'weight': 0.8
            },
            'compliance': {
                'concepts': ['compliance_normativo', 'gestion_riesgo', 'auditoria_compliance'],
                'weight': 0.88
            }
        }
        
        # Jurisdictional weights (some jurisdictions may be more represented)
        self.jurisdiction_weights = {
            'argentina': 1.0,
            'chile': 0.9,
            'uruguay': 0.85,
            'españa': 0.9
        }
        
        # Legal reasoning patterns for validation
        self.valid_reasoning_patterns = {
            'contract_formation': {
                'required_concepts': ['consentimiento', 'objeto_contractual'],
                'possible_conclusions': ['contrato_valido', 'contrato_nulo'],
                'logical_flow': ['premise_identification', 'rule_application', 'conclusion']
            },
            'civil_liability': {
                'required_concepts': ['dano', 'culpa', 'nexo_causal'],
                'possible_conclusions': ['responsabilidad_civil', 'exencion_responsabilidad'],
                'logical_flow': ['damage_assessment', 'fault_analysis', 'causation_link', 'liability_determination']
            },
            'corporate_governance': {
                'required_concepts': ['sociedad_anonima', 'directorio'],
                'possible_conclusions': ['gobierno_corporativo', 'estructura_organizacional'],
                'logical_flow': ['entity_identification', 'governance_structure', 'compliance_requirements']
            }
        }
        
    def evaluate_comprehensive(self, samples: List[ConceptEvaluationSample]) -> Dict[str, EvaluationResult]:
        """
        Comprehensive evaluation of legal AI system
        
        Args:
            samples: List of evaluation samples with predictions and ground truth
            
        Returns:
            Dictionary of evaluation results by metric name
        """
        
        logger.info(f"Starting comprehensive evaluation with {len(samples)} samples")
        
        results = {}
        
        # 1. Concept Extraction Metrics
        concept_results = self.evaluate_concept_extraction(samples)
        results.update(concept_results)
        
        # 2. Legal Reasoning Metrics  
        reasoning_results = self.evaluate_legal_reasoning(samples)
        results.update(reasoning_results)
        
        # 3. Multi-jurisdictional Consistency
        jurisdiction_results = self.evaluate_jurisdictional_consistency(samples)
        results.update(jurisdiction_results)
        
        # 4. Domain-Specific Accuracy
        domain_results = self.evaluate_domain_accuracy(samples)
        results.update(domain_results)
        
        # 5. Coherence and Consistency
        coherence_results = self.evaluate_coherence(samples)
        results.update(coherence_results)
        
        # 6. Generate overall score
        overall_result = self.compute_overall_score(results)
        results['overall_score'] = overall_result
        
        return results
    
    def evaluate_concept_extraction(self, samples: List[ConceptEvaluationSample]) -> Dict[str, EvaluationResult]:
        """Evaluate concept extraction accuracy"""
        
        logger.info("Evaluating concept extraction accuracy...")
        
        all_predicted = []
        all_ground_truth = []
        
        # Collect all concept predictions
        for sample in samples:
            pred_set = set(sample.predicted_concepts)
            truth_set = set(sample.ground_truth_concepts)
            
            # Convert to binary vectors for standard metrics
            all_concepts = list(pred_set.union(truth_set))
            
            pred_vector = [1 if concept in pred_set else 0 for concept in all_concepts]
            truth_vector = [1 if concept in truth_set else 0 for concept in all_concepts]
            
            all_predicted.extend(pred_vector)
            all_ground_truth.extend(truth_vector)
        
        # Calculate standard metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_ground_truth, 
            all_predicted, 
            average='binary'
        )
        
        accuracy = accuracy_score(all_ground_truth, all_predicted)
        
        # Calculate per-category metrics
        category_metrics = self._calculate_category_metrics(samples)
        
        # Calculate concept-level F1 (more detailed)
        concept_level_f1 = self._calculate_concept_level_f1(samples)
        
        return {
            'concept_extraction_precision': EvaluationResult(
                metric_name='Concept Extraction Precision',
                score=precision,
                details={'category_breakdown': category_metrics['precision']}
            ),
            'concept_extraction_recall': EvaluationResult(
                metric_name='Concept Extraction Recall', 
                score=recall,
                details={'category_breakdown': category_metrics['recall']}
            ),
            'concept_extraction_f1': EvaluationResult(
                metric_name='Concept Extraction F1',
                score=f1,
                details={
                    'category_breakdown': category_metrics['f1'],
                    'concept_level_f1': concept_level_f1
                }
            ),
            'concept_extraction_accuracy': EvaluationResult(
                metric_name='Concept Extraction Accuracy',
                score=accuracy,
                details={'category_breakdown': category_metrics['accuracy']}
            )
        }
    
    def evaluate_legal_reasoning(self, samples: List[ConceptEvaluationSample]) -> Dict[str, EvaluationResult]:
        """Evaluate legal reasoning quality"""
        
        logger.info("Evaluating legal reasoning quality...")
        
        reasoning_scores = []
        logical_flow_scores = []
        rule_application_scores = []
        
        for sample in samples:
            # Score reasoning chain quality
            reasoning_score = self._score_reasoning_chain(
                sample.predicted_reasoning,
                sample.ground_truth_reasoning
            )
            reasoning_scores.append(reasoning_score)
            
            # Score logical flow
            flow_score = self._score_logical_flow(
                sample.predicted_reasoning,
                sample.legal_category
            )
            logical_flow_scores.append(flow_score)
            
            # Score rule application accuracy
            rule_score = self._score_rule_application(
                sample.predicted_reasoning,
                sample.ground_truth_reasoning,
                sample.jurisdiction
            )
            rule_application_scores.append(rule_score)
        
        # Calculate average scores
        avg_reasoning = np.mean(reasoning_scores) if reasoning_scores else 0.0
        avg_flow = np.mean(logical_flow_scores) if logical_flow_scores else 0.0
        avg_rule = np.mean(rule_application_scores) if rule_application_scores else 0.0
        
        # Calculate confidence intervals
        reasoning_ci = self._calculate_confidence_interval(reasoning_scores)
        flow_ci = self._calculate_confidence_interval(logical_flow_scores)
        rule_ci = self._calculate_confidence_interval(rule_application_scores)
        
        return {
            'legal_reasoning_coherence': EvaluationResult(
                metric_name='Legal Reasoning Coherence',
                score=avg_reasoning,
                confidence_interval=reasoning_ci,
                details={
                    'individual_scores': reasoning_scores,
                    'score_distribution': self._get_score_distribution(reasoning_scores)
                }
            ),
            'logical_flow_accuracy': EvaluationResult(
                metric_name='Logical Flow Accuracy',
                score=avg_flow,
                confidence_interval=flow_ci,
                details={'score_distribution': self._get_score_distribution(logical_flow_scores)}
            ),
            'rule_application_accuracy': EvaluationResult(
                metric_name='Rule Application Accuracy', 
                score=avg_rule,
                confidence_interval=rule_ci,
                details={'score_distribution': self._get_score_distribution(rule_application_scores)}
            )
        }
    
    def evaluate_jurisdictional_consistency(self, samples: List[ConceptEvaluationSample]) -> Dict[str, EvaluationResult]:
        """Evaluate consistency across jurisdictions"""
        
        logger.info("Evaluating jurisdictional consistency...")
        
        # Group samples by jurisdiction
        jurisdiction_groups = defaultdict(list)
        for sample in samples:
            jurisdiction_groups[sample.jurisdiction].append(sample)
        
        # Calculate per-jurisdiction accuracy
        jurisdiction_accuracies = {}
        for jurisdiction, jurisdiction_samples in jurisdiction_groups.items():
            if len(jurisdiction_samples) > 0:
                # Calculate F1 for this jurisdiction
                jurisdiction_f1 = self._calculate_jurisdiction_f1(jurisdiction_samples)
                jurisdiction_accuracies[jurisdiction] = jurisdiction_f1
        
        # Calculate consistency (variance in performance across jurisdictions)
        if len(jurisdiction_accuracies) > 1:
            accuracies = list(jurisdiction_accuracies.values())
            consistency_score = 1.0 - np.std(accuracies)  # Lower std = higher consistency
        else:
            consistency_score = 1.0
        
        # Weight by jurisdiction importance
        weighted_accuracy = sum(
            acc * self.jurisdiction_weights.get(jur, 0.8)
            for jur, acc in jurisdiction_accuracies.items()
        ) / len(jurisdiction_accuracies) if jurisdiction_accuracies else 0.0
        
        return {
            'jurisdictional_consistency': EvaluationResult(
                metric_name='Multi-jurisdictional Consistency',
                score=consistency_score,
                details={
                    'per_jurisdiction_accuracy': jurisdiction_accuracies,
                    'weighted_average_accuracy': weighted_accuracy,
                    'coverage_by_jurisdiction': {
                        jur: len(samples) for jur, samples in jurisdiction_groups.items()
                    }
                }
            ),
            'weighted_jurisdictional_accuracy': EvaluationResult(
                metric_name='Weighted Jurisdictional Accuracy',
                score=weighted_accuracy,
                details=jurisdiction_accuracies
            )
        }
    
    def evaluate_domain_accuracy(self, samples: List[ConceptEvaluationSample]) -> Dict[str, EvaluationResult]:
        """Evaluate accuracy within specific legal domains"""
        
        logger.info("Evaluating domain-specific accuracy...")
        
        # Group by legal category
        category_groups = defaultdict(list)
        for sample in samples:
            category_groups[sample.legal_category].append(sample)
        
        # Calculate per-category metrics
        category_scores = {}
        for category, category_samples in category_groups.items():
            if len(category_samples) > 0:
                category_f1 = self._calculate_jurisdiction_f1(category_samples)  # Reuse function
                category_scores[category] = category_f1
        
        # Weight by category importance
        weighted_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.legal_categories.get(category, {}).get('weight', 0.8)
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            weighted_score /= total_weight
        
        # Identify strongest and weakest domains
        if category_scores:
            strongest_domain = max(category_scores.items(), key=lambda x: x[1])
            weakest_domain = min(category_scores.items(), key=lambda x: x[1])
        else:
            strongest_domain = ('unknown', 0.0)
            weakest_domain = ('unknown', 0.0)
        
        return {
            'domain_specific_accuracy': EvaluationResult(
                metric_name='Domain-Specific Accuracy',
                score=weighted_score,
                details={
                    'per_category_scores': category_scores,
                    'strongest_domain': strongest_domain,
                    'weakest_domain': weakest_domain,
                    'coverage_by_category': {
                        cat: len(samples) for cat, samples in category_groups.items()
                    }
                }
            )
        }
    
    def evaluate_coherence(self, samples: List[ConceptEvaluationSample]) -> Dict[str, EvaluationResult]:
        """Evaluate internal coherence of predictions"""
        
        logger.info("Evaluating prediction coherence...")
        
        coherence_scores = []
        consistency_scores = []
        
        for sample in samples:
            # Concept coherence (do concepts make sense together?)
            concept_coherence = self._calculate_concept_coherence(sample.predicted_concepts)
            coherence_scores.append(concept_coherence)
            
            # Reasoning consistency (does reasoning match concepts?)
            reasoning_consistency = self._calculate_reasoning_consistency(
                sample.predicted_concepts,
                sample.predicted_reasoning
            )
            consistency_scores.append(reasoning_consistency)
        
        avg_coherence = np.mean(coherence_scores) if coherence_scores else 0.0
        avg_consistency = np.mean(consistency_scores) if consistency_scores else 0.0
        
        return {
            'concept_coherence': EvaluationResult(
                metric_name='Concept Coherence',
                score=avg_coherence,
                details={'score_distribution': self._get_score_distribution(coherence_scores)}
            ),
            'reasoning_consistency': EvaluationResult(
                metric_name='Reasoning Consistency',
                score=avg_consistency,
                details={'score_distribution': self._get_score_distribution(consistency_scores)}
            )
        }
    
    def compute_overall_score(self, results: Dict[str, EvaluationResult]) -> EvaluationResult:
        """Compute weighted overall score"""
        
        # Define weights for different metric categories
        metric_weights = {
            'concept_extraction_f1': 0.25,
            'legal_reasoning_coherence': 0.25,
            'jurisdictional_consistency': 0.15,
            'domain_specific_accuracy': 0.20,
            'concept_coherence': 0.10,
            'reasoning_consistency': 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric_name, weight in metric_weights.items():
            if metric_name in results:
                weighted_score += results[metric_name].score * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score = weighted_score / total_weight
        else:
            overall_score = 0.0
        
        # Identify strengths and weaknesses
        sorted_results = sorted(
            [(name, result.score) for name, result in results.items() if name != 'overall_score'],
            key=lambda x: x[1],
            reverse=True
        )
        
        strengths = sorted_results[:3] if len(sorted_results) >= 3 else sorted_results
        weaknesses = sorted_results[-3:] if len(sorted_results) >= 3 else []
        
        return EvaluationResult(
            metric_name='Overall SCM Legal Score',
            score=overall_score,
            details={
                'component_scores': {name: result.score for name, result in results.items()},
                'strengths': strengths,
                'weaknesses': weaknesses,
                'scoring_weights': metric_weights
            }
        )
    
    # Helper methods
    
    def _calculate_category_metrics(self, samples: List[ConceptEvaluationSample]) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by legal category"""
        
        category_metrics = {
            'precision': {},
            'recall': {},
            'f1': {},
            'accuracy': {}
        }
        
        category_samples = defaultdict(list)
        for sample in samples:
            category_samples[sample.legal_category].append(sample)
        
        for category, cat_samples in category_samples.items():
            if len(cat_samples) == 0:
                continue
                
            # Calculate metrics for this category
            all_pred = []
            all_truth = []
            
            for sample in cat_samples:
                pred_set = set(sample.predicted_concepts)
                truth_set = set(sample.ground_truth_concepts)
                all_concepts = list(pred_set.union(truth_set))
                
                if all_concepts:  # Avoid empty concept lists
                    pred_vector = [1 if concept in pred_set else 0 for concept in all_concepts]
                    truth_vector = [1 if concept in truth_set else 0 for concept in all_concepts]
                    
                    all_pred.extend(pred_vector)
                    all_truth.extend(truth_vector)
            
            if all_pred and all_truth:
                precision, recall, f1, _ = precision_recall_fscore_support(
                    all_truth, all_pred, average='binary', zero_division=0
                )
                accuracy = accuracy_score(all_truth, all_pred)
                
                category_metrics['precision'][category] = precision
                category_metrics['recall'][category] = recall
                category_metrics['f1'][category] = f1
                category_metrics['accuracy'][category] = accuracy
        
        return category_metrics
    
    def _calculate_concept_level_f1(self, samples: List[ConceptEvaluationSample]) -> Dict[str, float]:
        """Calculate F1 score for each individual concept"""
        
        concept_predictions = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
        
        for sample in samples:
            pred_set = set(sample.predicted_concepts)
            truth_set = set(sample.ground_truth_concepts)
            
            # All concepts that appear in either prediction or truth
            all_concepts = pred_set.union(truth_set)
            
            for concept in all_concepts:
                if concept in pred_set and concept in truth_set:
                    concept_predictions[concept]['tp'] += 1
                elif concept in pred_set and concept not in truth_set:
                    concept_predictions[concept]['fp'] += 1
                elif concept not in pred_set and concept in truth_set:
                    concept_predictions[concept]['fn'] += 1
        
        # Calculate F1 for each concept
        concept_f1_scores = {}
        for concept, counts in concept_predictions.items():
            tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            concept_f1_scores[concept] = f1
        
        return concept_f1_scores
    
    def _score_reasoning_chain(self, predicted_reasoning: List[Dict], ground_truth_reasoning: List[Dict]) -> float:
        """Score the quality of a reasoning chain"""
        
        if not predicted_reasoning and not ground_truth_reasoning:
            return 1.0
        
        if not predicted_reasoning or not ground_truth_reasoning:
            return 0.0
        
        # Compare reasoning steps using ROUGE-L
        pred_text = " ".join([step.get('reasoning', '') for step in predicted_reasoning])
        truth_text = " ".join([step.get('reasoning', '') for step in ground_truth_reasoning])
        
        if not pred_text.strip() or not truth_text.strip():
            return 0.0
        
        rouge_scores = self.rouge_scorer.score(truth_text, pred_text)
        rouge_l_score = rouge_scores['rougeL'].fmeasure
        
        # Additional scoring based on logical structure
        structure_score = self._score_reasoning_structure(predicted_reasoning, ground_truth_reasoning)
        
        # Combine scores
        final_score = 0.7 * rouge_l_score + 0.3 * structure_score
        
        return final_score
    
    def _score_logical_flow(self, predicted_reasoning: List[Dict], legal_category: str) -> float:
        """Score the logical flow of reasoning"""
        
        if not predicted_reasoning:
            return 0.0
        
        # Check if reasoning follows expected pattern for legal category
        if legal_category in self.valid_reasoning_patterns:
            pattern = self.valid_reasoning_patterns[legal_category]
            expected_flow = pattern['logical_flow']
            
            # Extract reasoning step types from predicted reasoning
            actual_flow = [step.get('step_type', 'unknown') for step in predicted_reasoning]
            
            # Calculate similarity to expected flow
            flow_similarity = self._calculate_sequence_similarity(actual_flow, expected_flow)
            return flow_similarity
        
        return 0.5  # Default score if pattern not known
    
    def _score_rule_application(self, predicted_reasoning: List[Dict], ground_truth_reasoning: List[Dict], jurisdiction: str) -> float:
        """Score accuracy of legal rule application"""
        
        if not predicted_reasoning:
            return 0.0
        
        # Extract mentioned legal rules
        pred_rules = set()
        truth_rules = set()
        
        for step in predicted_reasoning:
            if 'legal_rule' in step:
                pred_rules.add(step['legal_rule'])
        
        for step in ground_truth_reasoning:
            if 'legal_rule' in step:
                truth_rules.add(step['legal_rule'])
        
        # Calculate rule overlap
        if not truth_rules:
            return 0.5  # No ground truth rules to compare
        
        intersection = pred_rules.intersection(truth_rules)
        union = pred_rules.union(truth_rules)
        
        jaccard_similarity = len(intersection) / len(union) if union else 1.0
        
        return jaccard_similarity
    
    def _calculate_jurisdiction_f1(self, samples: List[ConceptEvaluationSample]) -> float:
        """Calculate F1 score for a specific jurisdiction or category"""
        
        if not samples:
            return 0.0
        
        all_pred = []
        all_truth = []
        
        for sample in samples:
            pred_set = set(sample.predicted_concepts)
            truth_set = set(sample.ground_truth_concepts)
            all_concepts = list(pred_set.union(truth_set))
            
            if all_concepts:
                pred_vector = [1 if concept in pred_set else 0 for concept in all_concepts]
                truth_vector = [1 if concept in truth_set else 0 for concept in all_concepts]
                
                all_pred.extend(pred_vector)
                all_truth.extend(truth_vector)
        
        if all_pred and all_truth:
            _, _, f1, _ = precision_recall_fscore_support(
                all_truth, all_pred, average='binary', zero_division=0
            )
            return f1
        
        return 0.0
    
    def _calculate_concept_coherence(self, concepts: List[str]) -> float:
        """Calculate how coherent a set of concepts is"""
        
        if len(concepts) < 2:
            return 1.0
        
        # Check if concepts belong to related categories
        concept_categories = []
        for concept in concepts:
            for category, category_info in self.legal_categories.items():
                if concept in category_info['concepts']:
                    concept_categories.append(category)
                    break
        
        if not concept_categories:
            return 0.5  # Unknown concepts
        
        # Calculate category diversity (lower diversity = higher coherence)
        unique_categories = set(concept_categories)
        coherence_score = 1.0 - (len(unique_categories) - 1) / len(concept_categories)
        
        return max(0.0, coherence_score)
    
    def _calculate_reasoning_consistency(self, concepts: List[str], reasoning: List[Dict]) -> float:
        """Calculate consistency between concepts and reasoning"""
        
        if not concepts or not reasoning:
            return 1.0 if not concepts and not reasoning else 0.0
        
        # Extract concepts mentioned in reasoning
        reasoning_concepts = set()
        for step in reasoning:
            if 'premise_concepts' in step:
                reasoning_concepts.update(step['premise_concepts'])
            if 'conclusion_concept' in step:
                reasoning_concepts.add(step['conclusion_concept'])
        
        # Calculate overlap between extracted concepts and reasoning concepts
        concept_set = set(concepts)
        
        if not reasoning_concepts:
            return 0.5
        
        intersection = concept_set.intersection(reasoning_concepts)
        union = concept_set.union(reasoning_concepts)
        
        consistency_score = len(intersection) / len(union) if union else 1.0
        
        return consistency_score
    
    def _score_reasoning_structure(self, predicted: List[Dict], ground_truth: List[Dict]) -> float:
        """Score the structural similarity of reasoning chains"""
        
        if not predicted and not ground_truth:
            return 1.0
        
        if not predicted or not ground_truth:
            return 0.0
        
        # Compare number of steps (penalize significant differences)
        step_ratio = min(len(predicted), len(ground_truth)) / max(len(predicted), len(ground_truth))
        
        # Compare reasoning types if available
        pred_types = [step.get('reasoning_type', 'unknown') for step in predicted]
        truth_types = [step.get('reasoning_type', 'unknown') for step in ground_truth]
        
        type_similarity = self._calculate_sequence_similarity(pred_types, truth_types)
        
        # Combine scores
        structure_score = 0.6 * step_ratio + 0.4 * type_similarity
        
        return structure_score
    
    def _calculate_sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate similarity between two sequences"""
        
        if not seq1 and not seq2:
            return 1.0
        
        if not seq1 or not seq2:
            return 0.0
        
        # Use longest common subsequence approach
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[m][n]
        similarity = lcs_length / max(m, n)
        
        return similarity
    
    def _calculate_confidence_interval(self, scores: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for scores"""
        
        if len(scores) < 2:
            return (0.0, 1.0)
        
        mean_score = np.mean(scores)
        std_score = np.std(scores, ddof=1)
        
        # Use t-distribution for small samples
        from scipy import stats
        t_value = stats.t.ppf((1 + confidence) / 2, len(scores) - 1)
        margin_error = t_value * std_score / np.sqrt(len(scores))
        
        return (max(0.0, mean_score - margin_error), min(1.0, mean_score + margin_error))
    
    def _get_score_distribution(self, scores: List[float]) -> Dict[str, float]:
        """Get distribution statistics for scores"""
        
        if not scores:
            return {}
        
        return {
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'median': float(np.median(scores)),
            'q25': float(np.percentile(scores, 25)),
            'q75': float(np.percentile(scores, 75))
        }

def main():
    """Test evaluation metrics"""
    
    # Configuration
    config = {
        'metrics': ['concept_extraction_f1', 'legal_reasoning_coherence', 'jurisdictional_consistency']
    }
    
    # Initialize evaluator
    evaluator = LegalEvaluationMetrics(config)
    
    # Create test samples
    test_samples = [
        ConceptEvaluationSample(
            text="El contrato requiere consentimiento para ser válido.",
            predicted_concepts=['contrato_compraventa', 'consentimiento'],
            ground_truth_concepts=['contrato_compraventa', 'consentimiento', 'validez_contractual'],
            predicted_reasoning=[
                {
                    'step_type': 'premise_identification',
                    'reasoning': 'Se identifica un contrato',
                    'premise_concepts': ['contrato_compraventa'],
                    'legal_rule': 'formacion_contractual'
                }
            ],
            ground_truth_reasoning=[
                {
                    'step_type': 'premise_identification', 
                    'reasoning': 'Se identifica un contrato de compraventa',
                    'premise_concepts': ['contrato_compraventa'],
                    'legal_rule': 'formacion_contractual'
                }
            ],
            jurisdiction='argentina',
            legal_category='civil'
        ),
        ConceptEvaluationSample(
            text="La sociedad anónima requiere gobierno corporativo.",
            predicted_concepts=['sociedad_anonima', 'gobierno_corporativo'],
            ground_truth_concepts=['sociedad_anonima', 'gobierno_corporativo', 'directorio'],
            predicted_reasoning=[
                {
                    'step_type': 'entity_identification',
                    'reasoning': 'Identificación de sociedad anónima',
                    'premise_concepts': ['sociedad_anonima'],
                    'legal_rule': 'ley_sociedades'
                }
            ],
            ground_truth_reasoning=[
                {
                    'step_type': 'entity_identification',
                    'reasoning': 'Identificación de sociedad anónima',
                    'premise_concepts': ['sociedad_anonima'],
                    'legal_rule': 'ley_sociedades'
                }
            ],
            jurisdiction='argentina',
            legal_category='commercial'
        )
    ]
    
    # Run comprehensive evaluation
    results = evaluator.evaluate_comprehensive(test_samples)
    
    # Print results
    print("RESULTADOS DE EVALUACIÓN SCM LEGAL")
    print("=" * 50)
    
    for metric_name, result in results.items():
        print(f"\n{result.metric_name}")
        print(f"Puntuación: {result.score:.3f}")
        
        if result.confidence_interval:
            ci_low, ci_high = result.confidence_interval
            print(f"Intervalo de confianza (95%): [{ci_low:.3f}, {ci_high:.3f}]")
        
        if result.details:
            print("Detalles:")
            for key, value in result.details.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for subkey, subvalue in value.items():
                        print(f"    {subkey}: {subvalue}")
                else:
                    print(f"  {key}: {value}")
    
    # Print overall assessment
    if 'overall_score' in results:
        overall = results['overall_score']
        print(f"\n{'='*50}")
        print(f"PUNTUACIÓN GENERAL: {overall.score:.3f}")
        
        if 'strengths' in overall.details:
            print(f"\nFortalezas:")
            for strength, score in overall.details['strengths']:
                print(f"  - {strength}: {score:.3f}")
        
        if 'weaknesses' in overall.details:
            print(f"\nÁreas de mejora:")
            for weakness, score in overall.details['weaknesses']:
                print(f"  - {weakness}: {score:.3f}")

if __name__ == "__main__":
    main()