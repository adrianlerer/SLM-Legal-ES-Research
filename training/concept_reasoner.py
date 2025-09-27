"""
Conceptual Reasoning Engine for SCM Legal - Advanced legal reasoning capabilities
Real implementation for academic research publication

This module implements sophisticated legal reasoning that operates at the concept level,
enabling multi-step legal inference, analogical reasoning, and jurisdictional analysis.
"""

import json
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import networkx as nx
from itertools import combinations
import logging

logger = logging.getLogger(__name__)

class ReasoningType(Enum):
    """Types of legal reasoning supported by the engine"""
    DEDUCTIVE = "deductive"        # From general principles to specific cases
    INDUCTIVE = "inductive"        # From specific cases to general principles  
    ANALOGICAL = "analogical"      # Comparison with similar cases
    ABDUCTIVE = "abductive"        # Best explanation inference
    CAUSAL = "causal"             # Cause-effect relationships
    TELEOLOGICAL = "teleological"  # Purpose-based reasoning

@dataclass
class ReasoningStep:
    """Individual step in a reasoning chain"""
    step_id: str
    reasoning_type: ReasoningType
    premise_concepts: List[str]
    conclusion_concept: str
    confidence: float
    legal_rule: Optional[str] = None
    jurisdiction: Optional[str] = None
    explanation: str = ""
    supporting_evidence: List[str] = field(default_factory=list)
    
@dataclass
class ReasoningChain:
    """Complete reasoning chain for a legal problem"""
    chain_id: str
    initial_concepts: List[str]
    final_conclusion: str
    steps: List[ReasoningStep]
    overall_confidence: float
    reasoning_path: List[str] = field(default_factory=list)
    alternative_paths: List[List[str]] = field(default_factory=list)
    
@dataclass
class LegalRule:
    """Representation of a legal rule for reasoning"""
    rule_id: str
    name: str
    premise_pattern: List[str]  # Required concepts
    conclusion_pattern: str     # Resulting concept
    jurisdiction: List[str]
    confidence_weight: float
    rule_text: str
    exceptions: List[str] = field(default_factory=list)
    
class ConceptualReasoningEngine:
    """
    Advanced conceptual reasoning engine for legal analysis
    
    Features:
    - Multi-step legal inference
    - Analogical reasoning across jurisdictions
    - Causal relationship analysis
    - Conflict detection and resolution
    - Probabilistic confidence scoring
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_reasoning_steps = config.get('max_inference_steps', 10)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.multi_jurisdictional = config.get('multi_jurisdictional', True)
        
        self.load_legal_rules()
        self.build_reasoning_graph()
        
    def load_legal_rules(self):
        """Load legal rules for automated reasoning"""
        
        logger.info("Loading legal reasoning rules...")
        
        # Comprehensive set of legal rules for different jurisdictions
        self.legal_rules = {
            # Contract Law Rules
            'contract_formation_rule': LegalRule(
                rule_id='contract_001',
                name='Formación de Contrato',
                premise_pattern=['consentimiento', 'objeto_contractual', 'causa_licita'],
                conclusion_pattern='contrato_valido',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.95,
                rule_text='Para la formación válida de un contrato se requiere consentimiento, objeto y causa lícita',
                exceptions=['vicios_consentimiento', 'objeto_ilicito', 'causa_ilicita']
            ),
            
            'contract_nullity_rule': LegalRule(
                rule_id='contract_002', 
                name='Nulidad Contractual',
                premise_pattern=['vicios_consentimiento'],
                conclusion_pattern='contrato_nulo',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.9,
                rule_text='Los vicios del consentimiento producen la nulidad del contrato'
            ),
            
            # Civil Liability Rules
            'civil_liability_rule': LegalRule(
                rule_id='liability_001',
                name='Responsabilidad Civil Extracontractual',
                premise_pattern=['dano', 'culpa', 'nexo_causal'],
                conclusion_pattern='responsabilidad_civil',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'], 
                confidence_weight=0.92,
                rule_text='La responsabilidad civil requiere daño, culpa y nexo causal'
            ),
            
            'strict_liability_rule': LegalRule(
                rule_id='liability_002',
                name='Responsabilidad Objetiva',
                premise_pattern=['dano', 'actividad_riesgosa', 'nexo_causal'],
                conclusion_pattern='responsabilidad_objetiva',
                jurisdiction=['argentina', 'chile'],
                confidence_weight=0.88,
                rule_text='En actividades riesgosas la responsabilidad es objetiva'
            ),
            
            # Corporate Law Rules
            'corporate_governance_rule': LegalRule(
                rule_id='corporate_001',
                name='Gobierno Corporativo SA',
                premise_pattern=['sociedad_anonima', 'directorio'],
                conclusion_pattern='gobierno_corporativo',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.85,
                rule_text='Las sociedades anónimas requieren órganos de gobierno corporativo'
            ),
            
            'shareholder_rights_rule': LegalRule(
                rule_id='corporate_002',
                name='Derechos de Accionistas',
                premise_pattern=['accionista', 'sociedad_anonima'],
                conclusion_pattern='derechos_societarios',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.9,
                rule_text='Los accionistas tienen derechos específicos en las sociedades anónimas'
            ),
            
            # Constitutional Law Rules
            'due_process_rule': LegalRule(
                rule_id='constitutional_001',
                name='Debido Proceso',
                premise_pattern=['procedimiento_judicial', 'derechos_fundamentales'],
                conclusion_pattern='debido_proceso',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.95,
                rule_text='Todo procedimiento debe respetar las garantías del debido proceso'
            ),
            
            'constitutional_rights_rule': LegalRule(
                rule_id='constitutional_002',
                name='Supremacía Constitucional',
                premise_pattern=['norma_constitucional', 'norma_legal'],
                conclusion_pattern='jerarquia_normativa',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.98,
                rule_text='La Constitución prevalece sobre leyes ordinarias'
            ),
            
            # Labor Law Rules
            'employment_protection_rule': LegalRule(
                rule_id='labor_001',
                name='Protección del Trabajador',
                premise_pattern=['contrato_trabajo', 'subordinacion'],
                conclusion_pattern='proteccion_laboral',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.9,
                rule_text='El contrato de trabajo genera protección especial al trabajador'
            ),
            
            # Administrative Law Rules
            'administrative_act_rule': LegalRule(
                rule_id='admin_001',
                name='Validez Acto Administrativo',
                premise_pattern=['competencia', 'procedimiento_administrativo', 'motivacion'],
                conclusion_pattern='acto_administrativo_valido',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.87,
                rule_text='Los actos administrativos requieren competencia, procedimiento y motivación'
            ),
            
            # Compliance Rules
            'compliance_obligation_rule': LegalRule(
                rule_id='compliance_001',
                name='Obligación de Compliance',
                premise_pattern=['actividad_regulada', 'riesgo_regulatorio'],
                conclusion_pattern='programa_compliance',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.85,
                rule_text='Las actividades reguladas requieren programas de compliance'
            ),
            
            'risk_management_rule': LegalRule(
                rule_id='risk_001',
                name='Gestión de Riesgos',
                premise_pattern=['identificacion_riesgo', 'evaluacion_riesgo'],
                conclusion_pattern='mitigacion_riesgo',
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_weight=0.8,
                rule_text='La gestión de riesgos requiere identificación y evaluación previa'
            )
        }
        
    def build_reasoning_graph(self):
        """Build directed graph of conceptual relationships for reasoning"""
        
        logger.info("Building conceptual reasoning graph...")
        
        self.reasoning_graph = nx.DiGraph()
        
        # Add rules as nodes and create reasoning paths
        for rule_id, rule in self.legal_rules.items():
            # Add rule node
            self.reasoning_graph.add_node(
                rule_id,
                rule_type='inference_rule',
                confidence=rule.confidence_weight
            )
            
            # Create edges from premises to conclusion through rule
            for premise in rule.premise_pattern:
                premise_node = f"concept_{premise}"
                if not self.reasoning_graph.has_node(premise_node):
                    self.reasoning_graph.add_node(premise_node, rule_type='concept')
                    
                self.reasoning_graph.add_edge(
                    premise_node, 
                    rule_id,
                    relation='premise',
                    weight=1.0
                )
                
            # Edge from rule to conclusion
            conclusion_node = f"concept_{rule.conclusion_pattern}"
            if not self.reasoning_graph.has_node(conclusion_node):
                self.reasoning_graph.add_node(conclusion_node, rule_type='concept')
                
            self.reasoning_graph.add_edge(
                rule_id,
                conclusion_node, 
                relation='conclusion',
                weight=rule.confidence_weight
            )
            
    def reason(
        self, 
        initial_concepts: List[str],
        target_concept: Optional[str] = None,
        jurisdiction: str = 'argentina',
        reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE
    ) -> List[ReasoningChain]:
        """
        Perform conceptual reasoning from initial concepts
        
        Args:
            initial_concepts: Starting legal concepts
            target_concept: Optional target concept to reach
            jurisdiction: Legal jurisdiction for reasoning
            reasoning_type: Type of reasoning to employ
            
        Returns:
            List of possible reasoning chains
        """
        
        logger.info(f"Starting {reasoning_type.value} reasoning from {initial_concepts}")
        
        if reasoning_type == ReasoningType.DEDUCTIVE:
            return self._deductive_reasoning(initial_concepts, target_concept, jurisdiction)
        elif reasoning_type == ReasoningType.INDUCTIVE:
            return self._inductive_reasoning(initial_concepts, target_concept, jurisdiction)
        elif reasoning_type == ReasoningType.ANALOGICAL:
            return self._analogical_reasoning(initial_concepts, target_concept, jurisdiction)
        elif reasoning_type == ReasoningType.ABDUCTIVE:
            return self._abductive_reasoning(initial_concepts, target_concept, jurisdiction)
        elif reasoning_type == ReasoningType.CAUSAL:
            return self._causal_reasoning(initial_concepts, target_concept, jurisdiction)
        else:
            return self._deductive_reasoning(initial_concepts, target_concept, jurisdiction)
    
    def _deductive_reasoning(
        self, 
        initial_concepts: List[str],
        target_concept: Optional[str],
        jurisdiction: str
    ) -> List[ReasoningChain]:
        """Deductive reasoning from general rules to specific conclusions"""
        
        reasoning_chains = []
        visited_concepts = set(initial_concepts)
        
        # Find applicable rules
        applicable_rules = self._find_applicable_rules(initial_concepts, jurisdiction)
        
        for rule in applicable_rules:
            # Check if all premises are satisfied
            premises_satisfied = all(
                premise in initial_concepts or f"concept_{premise}" in visited_concepts
                for premise in rule.premise_pattern
            )
            
            if premises_satisfied:
                # Create reasoning step
                step = ReasoningStep(
                    step_id=f"deductive_{rule.rule_id}",
                    reasoning_type=ReasoningType.DEDUCTIVE,
                    premise_concepts=rule.premise_pattern,
                    conclusion_concept=rule.conclusion_pattern,
                    confidence=rule.confidence_weight,
                    legal_rule=rule.name,
                    jurisdiction=jurisdiction,
                    explanation=f"Aplicando regla: {rule.rule_text}",
                    supporting_evidence=[rule.rule_text]
                )
                
                # Create reasoning chain
                chain = ReasoningChain(
                    chain_id=f"deductive_chain_{len(reasoning_chains)}",
                    initial_concepts=initial_concepts,
                    final_conclusion=rule.conclusion_pattern,
                    steps=[step],
                    overall_confidence=rule.confidence_weight,
                    reasoning_path=[rule.rule_id]
                )
                
                reasoning_chains.append(chain)
                
                # If we haven't reached target, continue reasoning
                if target_concept and rule.conclusion_pattern != target_concept:
                    new_concepts = initial_concepts + [rule.conclusion_pattern]
                    extended_chains = self._deductive_reasoning(
                        new_concepts, target_concept, jurisdiction
                    )
                    
                    # Combine chains
                    for extended_chain in extended_chains:
                        combined_chain = ReasoningChain(
                            chain_id=f"combined_chain_{len(reasoning_chains)}",
                            initial_concepts=initial_concepts,
                            final_conclusion=extended_chain.final_conclusion,
                            steps=[step] + extended_chain.steps,
                            overall_confidence=min(chain.overall_confidence, extended_chain.overall_confidence),
                            reasoning_path=chain.reasoning_path + extended_chain.reasoning_path
                        )
                        reasoning_chains.append(combined_chain)
        
        return reasoning_chains[:5]  # Limit to top 5 chains
    
    def _inductive_reasoning(
        self,
        initial_concepts: List[str], 
        target_concept: Optional[str],
        jurisdiction: str
    ) -> List[ReasoningChain]:
        """Inductive reasoning from specific cases to general principles"""
        
        reasoning_chains = []
        
        # Look for patterns in initial concepts
        concept_patterns = self._identify_concept_patterns(initial_concepts)
        
        for pattern, confidence in concept_patterns:
            # Find rules that could explain this pattern
            explaining_rules = self._find_explaining_rules(pattern, jurisdiction)
            
            for rule in explaining_rules:
                step = ReasoningStep(
                    step_id=f"inductive_{rule.rule_id}",
                    reasoning_type=ReasoningType.INDUCTIVE,
                    premise_concepts=initial_concepts,
                    conclusion_concept=rule.conclusion_pattern,
                    confidence=confidence * 0.8,  # Lower confidence for inductive
                    legal_rule=rule.name,
                    jurisdiction=jurisdiction,
                    explanation=f"Patrón inducido sugiere aplicación de: {rule.rule_text}",
                    supporting_evidence=[f"Patrón detectado: {pattern}"]
                )
                
                chain = ReasoningChain(
                    chain_id=f"inductive_chain_{len(reasoning_chains)}",
                    initial_concepts=initial_concepts,
                    final_conclusion=rule.conclusion_pattern,
                    steps=[step],
                    overall_confidence=step.confidence,
                    reasoning_path=[rule.rule_id]
                )
                
                reasoning_chains.append(chain)
        
        return reasoning_chains
    
    def _analogical_reasoning(
        self,
        initial_concepts: List[str],
        target_concept: Optional[str], 
        jurisdiction: str
    ) -> List[ReasoningChain]:
        """Analogical reasoning by comparing with similar cases"""
        
        reasoning_chains = []
        
        # Find similar concept combinations in other jurisdictions
        if self.multi_jurisdictional:
            other_jurisdictions = ['argentina', 'chile', 'uruguay', 'españa']
            other_jurisdictions.remove(jurisdiction) if jurisdiction in other_jurisdictions else None
            
            for other_jurisdiction in other_jurisdictions:
                # Find rules in other jurisdiction with similar patterns
                similar_rules = self._find_similar_rules(initial_concepts, other_jurisdiction)
                
                for rule, similarity_score in similar_rules:
                    step = ReasoningStep(
                        step_id=f"analogical_{rule.rule_id}",
                        reasoning_type=ReasoningType.ANALOGICAL,
                        premise_concepts=initial_concepts,
                        conclusion_concept=rule.conclusion_pattern,
                        confidence=similarity_score * 0.7,  # Reduced for cross-jurisdictional
                        legal_rule=rule.name,
                        jurisdiction=other_jurisdiction,
                        explanation=f"Por analogía con {other_jurisdiction}: {rule.rule_text}",
                        supporting_evidence=[f"Regla análoga en {other_jurisdiction}"]
                    )
                    
                    chain = ReasoningChain(
                        chain_id=f"analogical_chain_{len(reasoning_chains)}",
                        initial_concepts=initial_concepts,
                        final_conclusion=rule.conclusion_pattern,
                        steps=[step],
                        overall_confidence=step.confidence,
                        reasoning_path=[rule.rule_id]
                    )
                    
                    reasoning_chains.append(chain)
        
        return reasoning_chains
    
    def _abductive_reasoning(
        self,
        initial_concepts: List[str],
        target_concept: Optional[str],
        jurisdiction: str
    ) -> List[ReasoningChain]:
        """Abductive reasoning - inference to best explanation"""
        
        reasoning_chains = []
        
        if not target_concept:
            return reasoning_chains
            
        # Find rules that could lead to target concept
        target_rules = self._find_rules_with_conclusion(target_concept, jurisdiction)
        
        for rule in target_rules:
            # Calculate how many premises are satisfied
            satisfied_premises = [p for p in rule.premise_pattern if p in initial_concepts]
            missing_premises = [p for p in rule.premise_pattern if p not in initial_concepts]
            
            if satisfied_premises:  # At least some premises satisfied
                satisfaction_ratio = len(satisfied_premises) / len(rule.premise_pattern)
                
                step = ReasoningStep(
                    step_id=f"abductive_{rule.rule_id}",
                    reasoning_type=ReasoningType.ABDUCTIVE,
                    premise_concepts=satisfied_premises,
                    conclusion_concept=target_concept,
                    confidence=satisfaction_ratio * rule.confidence_weight * 0.6,
                    legal_rule=rule.name,
                    jurisdiction=jurisdiction,
                    explanation=f"Mejor explicación para '{target_concept}': {rule.rule_text}",
                    supporting_evidence=[
                        f"Premisas satisfechas: {satisfied_premises}",
                        f"Premisas faltantes: {missing_premises}"
                    ]
                )
                
                chain = ReasoningChain(
                    chain_id=f"abductive_chain_{len(reasoning_chains)}",
                    initial_concepts=initial_concepts,
                    final_conclusion=target_concept,
                    steps=[step],
                    overall_confidence=step.confidence,
                    reasoning_path=[rule.rule_id]
                )
                
                reasoning_chains.append(chain)
        
        # Sort by confidence
        reasoning_chains.sort(key=lambda x: x.overall_confidence, reverse=True)
        
        return reasoning_chains[:3]  # Best 3 explanations
    
    def _causal_reasoning(
        self,
        initial_concepts: List[str],
        target_concept: Optional[str],
        jurisdiction: str
    ) -> List[ReasoningChain]:
        """Causal reasoning - cause and effect relationships"""
        
        reasoning_chains = []
        
        # Identify causal relationships in legal rules
        causal_rules = [
            rule for rule in self.legal_rules.values()
            if jurisdiction in rule.jurisdiction and 
            any(causal_term in rule.rule_text.lower() 
                for causal_term in ['causa', 'efecto', 'produce', 'genera', 'resulta'])
        ]
        
        for rule in causal_rules:
            # Check if initial concepts could be causes
            potential_causes = [c for c in initial_concepts if c in rule.premise_pattern]
            
            if potential_causes:
                step = ReasoningStep(
                    step_id=f"causal_{rule.rule_id}",
                    reasoning_type=ReasoningType.CAUSAL,
                    premise_concepts=potential_causes,
                    conclusion_concept=rule.conclusion_pattern,
                    confidence=rule.confidence_weight * 0.8,
                    legal_rule=rule.name,
                    jurisdiction=jurisdiction,
                    explanation=f"Relación causal: {rule.rule_text}",
                    supporting_evidence=[f"Causas identificadas: {potential_causes}"]
                )
                
                chain = ReasoningChain(
                    chain_id=f"causal_chain_{len(reasoning_chains)}",
                    initial_concepts=initial_concepts,
                    final_conclusion=rule.conclusion_pattern,
                    steps=[step],
                    overall_confidence=step.confidence,
                    reasoning_path=[rule.rule_id]
                )
                
                reasoning_chains.append(chain)
        
        return reasoning_chains
    
    def _find_applicable_rules(self, concepts: List[str], jurisdiction: str) -> List[LegalRule]:
        """Find legal rules applicable to given concepts"""
        
        applicable_rules = []
        
        for rule in self.legal_rules.values():
            if jurisdiction in rule.jurisdiction:
                # Check if any rule premises match concepts
                matching_premises = set(rule.premise_pattern).intersection(set(concepts))
                if matching_premises:
                    applicable_rules.append(rule)
        
        # Sort by number of matching premises and confidence
        applicable_rules.sort(
            key=lambda r: (
                len(set(r.premise_pattern).intersection(set(concepts))),
                r.confidence_weight
            ),
            reverse=True
        )
        
        return applicable_rules
    
    def _identify_concept_patterns(self, concepts: List[str]) -> List[Tuple[str, float]]:
        """Identify patterns in concept combinations"""
        
        patterns = []
        
        # Look for common legal patterns
        concept_set = set(concepts)
        
        # Contract formation pattern
        if {'consentimiento', 'objeto_contractual'}.issubset(concept_set):
            patterns.append(('contract_formation_pattern', 0.9))
            
        # Liability pattern  
        if {'dano', 'culpa'}.issubset(concept_set):
            patterns.append(('liability_pattern', 0.85))
            
        # Corporate governance pattern
        if {'sociedad_anonima', 'directorio'}.issubset(concept_set):
            patterns.append(('corporate_governance_pattern', 0.8))
            
        # Due process pattern
        if {'procedimiento_judicial', 'derechos_fundamentales'}.issubset(concept_set):
            patterns.append(('due_process_pattern', 0.9))
            
        return patterns
    
    def _find_explaining_rules(self, pattern: str, jurisdiction: str) -> List[LegalRule]:
        """Find rules that could explain observed patterns"""
        
        explaining_rules = []
        
        pattern_rule_mapping = {
            'contract_formation_pattern': ['contract_formation_rule'],
            'liability_pattern': ['civil_liability_rule', 'strict_liability_rule'],
            'corporate_governance_pattern': ['corporate_governance_rule'],
            'due_process_pattern': ['due_process_rule']
        }
        
        rule_ids = pattern_rule_mapping.get(pattern, [])
        
        for rule_id in rule_ids:
            if rule_id in self.legal_rules:
                rule = self.legal_rules[rule_id]
                if jurisdiction in rule.jurisdiction:
                    explaining_rules.append(rule)
        
        return explaining_rules
    
    def _find_similar_rules(self, concepts: List[str], jurisdiction: str) -> List[Tuple[LegalRule, float]]:
        """Find rules in other jurisdictions with similar concept patterns"""
        
        similar_rules = []
        
        for rule in self.legal_rules.values():
            if jurisdiction in rule.jurisdiction:
                # Calculate similarity based on concept overlap
                rule_concepts = set(rule.premise_pattern)
                input_concepts = set(concepts)
                
                if rule_concepts and input_concepts:
                    intersection = rule_concepts.intersection(input_concepts)
                    union = rule_concepts.union(input_concepts)
                    
                    jaccard_similarity = len(intersection) / len(union)
                    
                    if jaccard_similarity > 0.3:  # Minimum similarity threshold
                        similar_rules.append((rule, jaccard_similarity))
        
        # Sort by similarity
        similar_rules.sort(key=lambda x: x[1], reverse=True)
        
        return similar_rules[:3]  # Top 3 similar rules
    
    def _find_rules_with_conclusion(self, target_concept: str, jurisdiction: str) -> List[LegalRule]:
        """Find rules that conclude with target concept"""
        
        target_rules = []
        
        for rule in self.legal_rules.values():
            if (rule.conclusion_pattern == target_concept and 
                jurisdiction in rule.jurisdiction):
                target_rules.append(rule)
        
        return target_rules
    
    def detect_conflicts(self, reasoning_chains: List[ReasoningChain]) -> List[Dict[str, Any]]:
        """Detect conflicts between different reasoning chains"""
        
        conflicts = []
        
        # Group chains by conclusion
        conclusion_groups = defaultdict(list)
        for chain in reasoning_chains:
            conclusion_groups[chain.final_conclusion].append(chain)
        
        # Look for contradictory conclusions
        conclusions = list(conclusion_groups.keys())
        
        for i, conclusion1 in enumerate(conclusions):
            for conclusion2 in conclusions[i+1:]:
                # Check if conclusions are contradictory
                if self._are_contradictory(conclusion1, conclusion2):
                    conflict = {
                        'type': 'contradictory_conclusions',
                        'conclusion1': conclusion1,
                        'conclusion2': conclusion2,
                        'chains1': conclusion_groups[conclusion1],
                        'chains2': conclusion_groups[conclusion2],
                        'severity': 'high'
                    }
                    conflicts.append(conflict)
        
        # Look for jurisdictional conflicts
        for chains in conclusion_groups.values():
            if len(chains) > 1:
                jurisdictions = set()
                for chain in chains:
                    for step in chain.steps:
                        if step.jurisdiction:
                            jurisdictions.add(step.jurisdiction)
                
                if len(jurisdictions) > 1:
                    conflict = {
                        'type': 'jurisdictional_conflict',
                        'conclusion': chains[0].final_conclusion,
                        'jurisdictions': list(jurisdictions),
                        'chains': chains,
                        'severity': 'medium'
                    }
                    conflicts.append(conflict)
        
        return conflicts
    
    def _are_contradictory(self, conclusion1: str, conclusion2: str) -> bool:
        """Check if two conclusions are contradictory"""
        
        # Define contradictory concept pairs
        contradictory_pairs = [
            ('contrato_valido', 'contrato_nulo'),
            ('responsabilidad_civil', 'exencion_responsabilidad'),
            ('acto_administrativo_valido', 'acto_administrativo_nulo'),
            ('derecho_reconocido', 'derecho_negado')
        ]
        
        for pair in contradictory_pairs:
            if (conclusion1 in pair and conclusion2 in pair and 
                conclusion1 != conclusion2):
                return True
        
        return False
    
    def generate_explanation(self, reasoning_chain: ReasoningChain) -> str:
        """Generate human-readable explanation of reasoning chain"""
        
        explanation_parts = [
            f"Análisis conceptual iniciado con: {', '.join(reasoning_chain.initial_concepts)}\n"
        ]
        
        for i, step in enumerate(reasoning_chain.steps, 1):
            explanation_parts.append(f"Paso {i} ({step.reasoning_type.value}):")
            explanation_parts.append(f"  - Premisas: {', '.join(step.premise_concepts)}")
            explanation_parts.append(f"  - Conclusión: {step.conclusion_concept}")
            explanation_parts.append(f"  - Confianza: {step.confidence:.2f}")
            explanation_parts.append(f"  - Explicación: {step.explanation}")
            
            if step.legal_rule:
                explanation_parts.append(f"  - Regla aplicada: {step.legal_rule}")
            
            if step.jurisdiction:
                explanation_parts.append(f"  - Jurisdicción: {step.jurisdiction}")
            
            explanation_parts.append("")
        
        explanation_parts.append(f"Conclusión final: {reasoning_chain.final_conclusion}")
        explanation_parts.append(f"Confianza general: {reasoning_chain.overall_confidence:.2f}")
        
        return "\n".join(explanation_parts)

def main():
    """Test the reasoning engine"""
    
    # Configuration
    config = {
        'max_inference_steps': 10,
        'confidence_threshold': 0.7,
        'multi_jurisdictional': True
    }
    
    # Initialize reasoning engine
    reasoner = ConceptualReasoningEngine(config)
    
    # Test reasoning scenarios
    test_scenarios = [
        {
            'name': 'Contract Formation',
            'concepts': ['consentimiento', 'objeto_contractual', 'causa_licita'],
            'target': 'contrato_valido',
            'jurisdiction': 'argentina'
        },
        {
            'name': 'Civil Liability',
            'concepts': ['dano', 'culpa', 'nexo_causal'],
            'target': 'responsabilidad_civil',
            'jurisdiction': 'chile'  
        },
        {
            'name': 'Corporate Governance',
            'concepts': ['sociedad_anonima', 'directorio'],
            'target': None,
            'jurisdiction': 'argentina'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*50}")
        print(f"ESCENARIO: {scenario['name']}")
        print(f"{'='*50}")
        
        # Test different reasoning types
        for reasoning_type in [ReasoningType.DEDUCTIVE, ReasoningType.ANALOGICAL, ReasoningType.ABDUCTIVE]:
            chains = reasoner.reason(
                initial_concepts=scenario['concepts'],
                target_concept=scenario['target'],
                jurisdiction=scenario['jurisdiction'],
                reasoning_type=reasoning_type
            )
            
            print(f"\n--- Razonamiento {reasoning_type.value.upper()} ---")
            
            for i, chain in enumerate(chains[:2], 1):
                print(f"\nCadena {i}:")
                explanation = reasoner.generate_explanation(chain)
                print(explanation)
        
        # Detect conflicts
        all_chains = []
        for reasoning_type in [ReasoningType.DEDUCTIVE, ReasoningType.ANALOGICAL]:
            chains = reasoner.reason(
                initial_concepts=scenario['concepts'],
                target_concept=scenario['target'],
                jurisdiction=scenario['jurisdiction'],
                reasoning_type=reasoning_type
            )
            all_chains.extend(chains)
        
        conflicts = reasoner.detect_conflicts(all_chains)
        if conflicts:
            print(f"\n--- CONFLICTOS DETECTADOS ---")
            for conflict in conflicts:
                print(f"Tipo: {conflict['type']}")
                print(f"Severidad: {conflict['severity']}")
                if 'conclusion1' in conflict:
                    print(f"Conclusiones contradictorias: {conflict['conclusion1']} vs {conflict['conclusion2']}")

if __name__ == "__main__":
    main()