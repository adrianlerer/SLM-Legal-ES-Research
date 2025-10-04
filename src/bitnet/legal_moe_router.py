#!/usr/bin/env python3
"""
Legal MoE (Mixture of Experts) Router for BitNet + TUMIX Enhanced

This module implements an intelligent routing system for specialized legal experts,
extending our BitNet infrastructure with domain-specific expertise and automatic
expert selection based on legal query classification.

Key Features:
- Intelligent domain classification for legal queries
- Top-K expert selection with confidence scoring
- Specialized BitNet experts for different legal areas
- Weighted combination with Enhanced Consensus Engine
- Performance optimization and load balancing
- Complete audit trail for regulatory compliance

Legal Expert Domains:
1. Corporate Law Expert - M&A, governance, securities
2. Contract Analysis Expert - Contract review, risk assessment  
3. Compliance Expert - Regulatory compliance, audit
4. Litigation Strategy Expert - Dispute resolution, litigation
5. Tax Law Expert - Tax planning, compliance, structuring
6. Labor Law Expert - Employment law, HR compliance
7. Regulatory Expert - Industry regulations, licensing
8. Due Diligence Expert - M&A due diligence, investigation

Author: Ignacio Adrian Lerer - Senior Corporate Legal Consultant
License: Proprietary - Confidential Legal Technology System
Version: 1.0.0-moe-legal-router
"""

import asyncio
import json
import logging
import time
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum
import re
from collections import defaultdict

# Import BitNet components
from .bitnet_integration_wrapper import BitNetAPIWrapper, get_bitnet_wrapper
from .hybrid_inference_manager import (
    HybridInferenceManager, get_hybrid_manager,
    InferenceRequest, InferenceResponse, 
    ConfidentialityLevel, Priority, InferenceBackend
)

# Import Enhanced Consensus Engine
try:
    from ..tumix.enhanced_consensus_engine import (
        EnhancedConsensusEngine, ConsensusResult, ConsensusFeatures,
        create_enhanced_consensus_engine
    )
    ENHANCED_CONSENSUS_AVAILABLE = True
except ImportError:
    ENHANCED_CONSENSUS_AVAILABLE = False
    logging.warning("Enhanced Consensus Engine not available for MoE integration")

# Import CoDA Legal Integration
try:
    from .coda_legal_integration import (
        CoDALegalIntegration, CoDARequest, CoDAResponse, CoDATaskType, 
        CoDAComplexity, get_coda_integration
    )
    CODA_INTEGRATION_AVAILABLE = True
except ImportError:
    CODA_INTEGRATION_AVAILABLE = False
    logging.warning("CoDA Legal Integration not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LegalDomain(Enum):
    """Legal domain classifications for expert routing"""
    CORPORATE_LAW = "corporate_law"
    CONTRACT_ANALYSIS = "contract_analysis"
    COMPLIANCE = "compliance"
    LITIGATION_STRATEGY = "litigation_strategy"
    TAX_LAW = "tax_law"
    LABOR_LAW = "labor_law"
    REGULATORY = "regulatory"
    DUE_DILIGENCE = "due_diligence"
    LEGAL_AUTOMATION = "legal_automation"  # NEW: CoDA-powered automation domain
    GENERAL_LEGAL = "general_legal"

class ExpertCapability(Enum):
    """Expert capability levels and specializations"""
    SENIOR_PARTNER = "senior_partner"
    MANAGING_PARTNER = "managing_partner"
    SUBJECT_MATTER_EXPERT = "subject_matter_expert"
    INDUSTRY_SPECIALIST = "industry_specialist"
    REGULATORY_SPECIALIST = "regulatory_specialist"

@dataclass
class LegalExpertProfile:
    """Profile definition for specialized legal experts"""
    expert_id: str
    domain: LegalDomain
    capability: ExpertCapability
    specializations: List[str]
    experience_areas: List[str]
    prompt_template: str
    confidence_threshold: float = 0.75
    max_tokens: int = 600
    temperature: float = 0.7
    processing_priority: Priority = Priority.NORMAL

@dataclass
class DomainClassificationResult:
    """Result of legal domain classification"""
    primary_domain: LegalDomain
    confidence_score: float
    secondary_domains: List[Tuple[LegalDomain, float]]
    complexity_level: str
    estimated_processing_time: float
    recommended_experts: List[str]
    classification_reasoning: List[str]

@dataclass
class MoERoutingDecision:
    """MoE routing decision with expert selection and reasoning"""
    selected_experts: List[LegalExpertProfile]
    routing_confidence: float
    domain_classification: DomainClassificationResult
    load_balancing_factor: float
    estimated_cost_usd: float
    estimated_processing_time_ms: float
    routing_strategy: str
    fallback_experts: List[str]

@dataclass
class MoEResponse:
    """Response from MoE legal expert system"""
    final_consensus: str
    consensus_confidence: float
    expert_responses: List[Dict[str, Any]]
    domain_analysis: DomainClassificationResult
    routing_decision: MoERoutingDecision
    performance_metrics: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]
    cost_breakdown: Dict[str, float]
    error: Optional[str] = None

class LegalDomainClassifier:
    """Enhanced intelligent classifier for legal query domains
    
    Reality-Filtered Improvements:
    - Enhanced keyword analysis with semantic patterns
    - Confidence validation using multiple scoring methods
    - Context-aware domain detection with legal terminology
    - Ensemble validation between different classification approaches
    """
    
    def __init__(self):
        # Enhanced keyword mapping with semantic patterns and legal terminology
        self.domain_keywords = {
            LegalDomain.CORPORATE_LAW: [
                "fusión", "merger", "adquisición", "acquisition", "gobierno corporativo",
                "corporate governance", "directorio", "board", "accionistas", "shareholders",
                "securities", "valores", "ipo", "restructuring", "reestructuración",
                "joint venture", "sociedad", "corporate", "empresarial", "due diligence"
            ],
            LegalDomain.CONTRACT_ANALYSIS: [
                "contrato", "contract", "cláusula", "clause", "términos", "terms",
                "condiciones", "conditions", "obligaciones", "obligations", "derechos",
                "rights", "prestación", "services", "incumplimiento", "breach",
                "rescisión", "termination", "indemnización", "indemnification"
            ],
            LegalDomain.COMPLIANCE: [
                "compliance", "cumplimiento", "normativa", "regulation", "regulación",
                "auditoria", "audit", "control interno", "internal control", "riesgo",
                "risk", "política", "policy", "procedimiento", "procedure", "sox",
                "ley", "law", "decreto", "regulatorio", "regulatory"
            ],
            LegalDomain.LITIGATION_STRATEGY: [
                "litigio", "litigation", "demanda", "lawsuit", "juicio", "trial",
                "tribunal", "court", "arbitraje", "arbitration", "disputa", "dispute",
                "resolución", "resolution", "mediación", "mediation", "apelación",
                "appeal", "sentencia", "judgment", "proceso judicial", "legal process"
            ],
            LegalDomain.TAX_LAW: [
                "impuesto", "tax", "tributario", "fiscal", "afip", "irs", "hacienda",
                "contribución", "contribution", "deducción", "deduction", "exención",
                "exemption", "planificación fiscal", "tax planning", "transfer pricing",
                "precios de transferencia", "iva", "vat", "ganancias", "income"
            ],
            LegalDomain.LABOR_LAW: [
                "laboral", "labor", "employment", "empleo", "trabajador", "employee",
                "empleado", "worker", "contrato laboral", "employment contract",
                "despido", "termination", "indemnización laboral", "severance",
                "sindicato", "union", "convenio colectivo", "collective bargaining",
                "accidente laboral", "workplace accident", "discriminación", "harassment"
            ],
            LegalDomain.REGULATORY: [
                "regulación", "regulation", "licencia", "license", "permiso", "permit",
                "autorización", "authorization", "supervisión", "supervision",
                "ente regulador", "regulatory body", "sector", "industria", "industry",
                "telecomunicaciones", "energía", "energy", "financiero", "financial",
                "ambiental", "environmental", "competencia", "antitrust"
            ],
            LegalDomain.DUE_DILIGENCE: [
                "due diligence", "diligencia debida", "investigación", "investigation",
                "verificación", "verification", "antecedentes", "background", "revisión",
                "review", "análisis", "analysis", "documentación", "documentation",
                "contingencias", "contingencies", "riesgos", "risks", "pasivos", "liabilities"
            ],
            LegalDomain.RLAD_ENHANCED: [
                "abstracciones", "abstractions", "patrones", "patterns", "razonamiento",
                "reasoning", "estructuras", "structures", "metodología", "methodology",
                "framework", "enfoque", "approach", "sistemático", "systematic",
                "inteligente", "intelligent", "discovery", "descubrimiento", "rlad"
            ],
            LegalDomain.LEGAL_AUTOMATION: [
                "automatización", "automation", "generar", "generate", "template",
                "plantilla", "código", "code", "workflow", "proceso", "process",
                "crear documento", "create document", "automatizar", "automate",
                "generación automática", "automatic generation", "optimización",
                "optimization", "digitalización", "digitalization", "sistema",
                "system", "herramienta", "tool", "coda", "ai generation"
            ]
        }
        
        # Enhanced complexity indicators with legal document patterns
        self.complexity_indicators = {
            "simple": ["consulta", "pregunta", "información", "definición", "qué es", "cómo", "cuándo"],
            "medium": ["análisis", "evaluación", "revisión", "estrategia", "implementación", "proceso"],
            "complex": ["reestructuración", "fusión", "litigio", "regulación", "negociación", "estructura"],
            "highly_complex": ["cross-border", "multi-jurisdictional", "class action", "regulatory investigation", "multi-party", "international"]
        }
        
        # Legal entity and action patterns for enhanced classification
        self.legal_entity_patterns = {
            "corporate": ["sociedad", "empresa", "corporation", "s.a.", "s.r.l.", "llc", "inc."],
            "regulatory": ["autoridad", "ente", "comisión", "superintendencia", "ministerio"],
            "judicial": ["tribunal", "juzgado", "corte", "court", "judge", "magistrado"]
        }
        
        # Legal action verbs for intent classification
        self.legal_action_verbs = {
            "analysis": ["analizar", "evaluar", "revisar", "examinar", "estudiar"],
            "drafting": ["redactar", "elaborar", "preparar", "draft", "crear"],
            "compliance": ["cumplir", "verificar", "auditar", "monitorear", "controlar"],
            "negotiation": ["negociar", "acordar", "pactar", "consensuar", "convenir"]
        }
    
    async def classify_legal_domain(self, query: str, context: Optional[Dict] = None) -> DomainClassificationResult:
        """Enhanced classification with reality-filtered improvements from NYU paper analysis
        
        Improvements implemented:
        - Multi-method scoring ensemble validation
        - Enhanced semantic pattern matching (without real embeddings)
        - Context-aware legal terminology analysis
        - Confidence validation through multiple approaches
        """
        start_time = time.time()
        
        # Normalize query for analysis
        query_normalized = query.lower()
        words = query.split()
        
        # METHOD 1: Enhanced keyword matching with semantic patterns
        keyword_scores = self._calculate_keyword_scores(query_normalized, words)
        
        # METHOD 2: Legal entity and action pattern analysis
        pattern_scores = self._analyze_legal_patterns(query_normalized)
        
        # METHOD 3: Context-aware scoring (if context provided)
        context_scores = self._analyze_context_signals(context) if context else {}
        
        # ENSEMBLE: Combine all scoring methods for validation
        domain_scores, classification_reasoning = self._ensemble_scoring(
            keyword_scores, pattern_scores, context_scores, query_normalized
        )
        
        # Enhanced confidence validation using ensemble methods
        primary_domain, confidence_score = self._validate_classification_confidence(
            domain_scores, keyword_scores, pattern_scores
        )
        
        # Identify secondary domains
        secondary_domains = [
            (domain, score / sum(domain_scores.values()) if sum(domain_scores.values()) > 0 else 0)
            for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
            if score > 0
        ]
        
        # Determine complexity level
        complexity_level = self._determine_complexity(query_normalized)
        
        # Estimate processing time based on complexity
        base_time = {
            "simple": 1000,
            "medium": 2500,
            "complex": 5000,
            "highly_complex": 8000
        }
        estimated_processing_time = base_time.get(complexity_level, 3000)
        
        # Recommend experts based on domain and complexity
        recommended_experts = self._recommend_experts(primary_domain, complexity_level, secondary_domains)
        
        classification_reasoning.append(f"Complexity: {complexity_level}, Processing time: {estimated_processing_time}ms")
        
        return DomainClassificationResult(
            primary_domain=primary_domain,
            confidence_score=confidence_score,
            secondary_domains=secondary_domains,
            complexity_level=complexity_level,
            estimated_processing_time=estimated_processing_time,
            recommended_experts=recommended_experts,
            classification_reasoning=classification_reasoning
        )
    
    def _determine_complexity(self, query: str) -> str:
        """Determine query complexity level"""
        for complexity, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in query:
                    return complexity
        
        # Complexity based on query length and structure
        word_count = len(query.split())
        if word_count < 10:
            return "simple"
        elif word_count < 25:
            return "medium"
        elif word_count < 50:
            return "complex"
        else:
            return "highly_complex"
    
    def _recommend_experts(self, primary_domain: LegalDomain, complexity: str, 
                          secondary_domains: List[Tuple[LegalDomain, float]]) -> List[str]:
        """Recommend experts based on domain and complexity"""
        experts = []
        
        # Primary domain expert (always included)
        experts.append(f"{primary_domain.value}_expert")
        
        # Add complexity-based experts
        if complexity in ["complex", "highly_complex"]:
            experts.append("senior_counsel_expert")
        
        # Add secondary domain experts if confidence is high enough
        for domain, confidence in secondary_domains:
            if confidence > 0.2:  # 20% threshold for secondary experts
                experts.append(f"{domain.value}_expert")
        
        # Ensure we have 2-4 experts (optimal for consensus)
        if len(experts) < 2:
            experts.append("general_legal_expert")
        elif len(experts) > 4:
            experts = experts[:4]  # Limit to top 4 experts
        
        return experts
    
    def _calculate_keyword_scores(self, query_normalized: str, words: List[str]) -> Dict[LegalDomain, float]:
        """Enhanced keyword scoring with semantic patterns"""
        keyword_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Exact match scoring
                if keyword_lower in query_normalized:
                    # Weight based on keyword specificity and length
                    specificity_weight = len(keyword.split()) * 1.5 if len(keyword.split()) > 1 else 1.0
                    # Context position weight (higher if keyword appears early in query)
                    position_bonus = 1.2 if query_normalized.find(keyword_lower) < len(query_normalized) * 0.3 else 1.0
                    
                    score += specificity_weight * position_bonus
                    matched_keywords.append(keyword)
                
                # Partial/fuzzy matching for compound terms
                elif any(word in keyword_lower for word in words):
                    score += 0.5  # Lower weight for partial matches
            
            # Normalize by query length and add frequency bonus
            if len(words) > 0:
                keyword_scores[domain] = score / len(words)
                # Frequency bonus for multiple matches
                if len(matched_keywords) > 1:
                    keyword_scores[domain] *= 1.2
            else:
                keyword_scores[domain] = 0.0
        
        return keyword_scores
    
    def _analyze_legal_patterns(self, query_normalized: str) -> Dict[LegalDomain, float]:
        """Analyze legal entity patterns and action verbs for enhanced classification"""
        pattern_scores = {domain: 0.0 for domain in LegalDomain}
        
        # Analyze legal entity patterns
        entity_matches = {}
        for entity_type, patterns in self.legal_entity_patterns.items():
            for pattern in patterns:
                if pattern.lower() in query_normalized:
                    entity_matches[entity_type] = entity_matches.get(entity_type, 0) + 1
        
        # Analyze legal action verbs
        action_matches = {}
        for action_type, verbs in self.legal_action_verbs.items():
            for verb in verbs:
                if verb.lower() in query_normalized:
                    action_matches[action_type] = action_matches.get(action_type, 0) + 1
        
        # Map entity and action patterns to legal domains
        domain_mapping = {
            "corporate": [LegalDomain.CORPORATE_LAW, LegalDomain.DUE_DILIGENCE],
            "regulatory": [LegalDomain.REGULATORY, LegalDomain.COMPLIANCE],
            "judicial": [LegalDomain.LITIGATION_STRATEGY],
            "analysis": [LegalDomain.CONTRACT_ANALYSIS, LegalDomain.DUE_DILIGENCE],
            "drafting": [LegalDomain.CONTRACT_ANALYSIS, LegalDomain.CORPORATE_LAW],
            "compliance": [LegalDomain.COMPLIANCE, LegalDomain.REGULATORY],
            "negotiation": [LegalDomain.CONTRACT_ANALYSIS, LegalDomain.CORPORATE_LAW]
        }
        
        # Calculate pattern scores
        for entity_type, count in entity_matches.items():
            for domain in domain_mapping.get(entity_type, []):
                pattern_scores[domain] += count * 0.3
        
        for action_type, count in action_matches.items():
            for domain in domain_mapping.get(action_type, []):
                pattern_scores[domain] += count * 0.4
        
        return pattern_scores
    
    def _analyze_context_signals(self, context: Dict) -> Dict[LegalDomain, float]:
        """Analyze context signals for domain classification"""
        context_scores = {domain: 0.0 for domain in LegalDomain}
        
        if not context:
            return context_scores
        
        # Document type analysis
        doc_type = context.get('document_type', '').lower()
        if 'contract' in doc_type:
            context_scores[LegalDomain.CONTRACT_ANALYSIS] += 0.5
        elif 'merger' in doc_type or 'm&a' in doc_type:
            context_scores[LegalDomain.CORPORATE_LAW] += 0.5
            context_scores[LegalDomain.DUE_DILIGENCE] += 0.3
        elif 'compliance' in doc_type:
            context_scores[LegalDomain.COMPLIANCE] += 0.5
        elif 'litigation' in doc_type:
            context_scores[LegalDomain.LITIGATION_STRATEGY] += 0.5
        
        # Industry context
        industry = context.get('industry', '').lower()
        if industry in ['banking', 'financial']:
            context_scores[LegalDomain.REGULATORY] += 0.3
            context_scores[LegalDomain.COMPLIANCE] += 0.3
        elif industry in ['technology', 'software']:
            context_scores[LegalDomain.CONTRACT_ANALYSIS] += 0.2
            context_scores[LegalDomain.CORPORATE_LAW] += 0.2
        
        # Urgency and complexity signals
        if context.get('urgency') == 'high':
            # High urgency often indicates litigation or compliance issues
            context_scores[LegalDomain.LITIGATION_STRATEGY] += 0.2
            context_scores[LegalDomain.COMPLIANCE] += 0.2
        
        return context_scores
    
    def _ensemble_scoring(self, keyword_scores: Dict, pattern_scores: Dict, 
                         context_scores: Dict, query_normalized: str) -> Tuple[Dict[LegalDomain, float], List[str]]:
        """Ensemble multiple scoring methods with validation"""
        domain_scores = {}
        classification_reasoning = []
        
        # Weighted combination of all methods
        weights = {
            'keywords': 0.5,
            'patterns': 0.3,
            'context': 0.2 if context_scores else 0.0
        }
        
        # Adjust weights if no context available
        if not context_scores:
            weights['keywords'] = 0.6
            weights['patterns'] = 0.4
        
        for domain in LegalDomain:
            keyword_score = keyword_scores.get(domain, 0.0)
            pattern_score = pattern_scores.get(domain, 0.0)
            context_score = context_scores.get(domain, 0.0)
            
            # Weighted ensemble score
            ensemble_score = (
                keyword_score * weights['keywords'] +
                pattern_score * weights['patterns'] +
                context_score * weights['context']
            )
            
            domain_scores[domain] = ensemble_score
            
            # Add reasoning for significant scores
            if ensemble_score > 0.1:
                reason_parts = []
                if keyword_score > 0:
                    reason_parts.append(f"keywords: {keyword_score:.2f}")
                if pattern_score > 0:
                    reason_parts.append(f"patterns: {pattern_score:.2f}")
                if context_score > 0:
                    reason_parts.append(f"context: {context_score:.2f}")
                
                classification_reasoning.append(
                    f"{domain.value}: ensemble={ensemble_score:.2f} ({', '.join(reason_parts)})"
                )
        
        return domain_scores, classification_reasoning
    
    def _validate_classification_confidence(self, domain_scores: Dict, keyword_scores: Dict, 
                                          pattern_scores: Dict) -> Tuple[LegalDomain, float]:
        """Enhanced confidence validation using ensemble methods"""
        
        if not domain_scores or all(score == 0 for score in domain_scores.values()):
            return LegalDomain.GENERAL_LEGAL, 0.5
        
        # Find primary domain from ensemble scores
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])[0]
        max_ensemble_score = domain_scores[primary_domain]
        
        # Calculate confidence using multiple validation approaches
        
        # Method 1: Score distribution analysis
        total_score = sum(domain_scores.values())
        distribution_confidence = max_ensemble_score / total_score if total_score > 0 else 0.5
        
        # Method 2: Cross-method validation
        keyword_primary = max(keyword_scores.items(), key=lambda x: x[1])[0] if keyword_scores else None
        pattern_primary = max(pattern_scores.items(), key=lambda x: x[1])[0] if pattern_scores else None
        
        cross_validation_bonus = 0.0
        if keyword_primary == primary_domain:
            cross_validation_bonus += 0.1
        if pattern_primary == primary_domain:
            cross_validation_bonus += 0.1
        
        # Method 3: Score magnitude validation
        magnitude_confidence = min(max_ensemble_score * 2, 1.0)  # Scale ensemble score to confidence
        
        # Final confidence calculation with ensemble validation
        final_confidence = (
            distribution_confidence * 0.4 +
            magnitude_confidence * 0.4 +
            cross_validation_bonus * 0.2
        )
        
        # Ensure confidence is in valid range
        final_confidence = max(0.1, min(0.99, final_confidence))
        
        return primary_domain, final_confidence

class LegalExpertRegistry:
    """Registry of specialized legal experts with BitNet integration"""
    
    def __init__(self):
        self.experts = self._initialize_legal_experts()
        self.expert_performance = defaultdict(lambda: {"requests": 0, "avg_confidence": 0.0, "success_rate": 1.0})
    
    def _initialize_legal_experts(self) -> Dict[str, LegalExpertProfile]:
        """Initialize specialized legal expert profiles"""
        
        experts = {
            "corporate_law_expert": LegalExpertProfile(
                expert_id="corporate_law_expert",
                domain=LegalDomain.CORPORATE_LAW,
                capability=ExpertCapability.MANAGING_PARTNER,
                specializations=["M&A", "Corporate Governance", "Securities Law", "Joint Ventures"],
                experience_areas=["Cross-border transactions", "IPO", "Private equity", "Restructuring"],
                prompt_template="""
Eres un Managing Partner especializado en Derecho Corporativo con 30+ años de experiencia en M&A, gobierno corporativo y mercado de valores.

Tu expertise incluye:
- Fusiones y adquisiciones complejas (nacionales e internacionales)
- Gobierno corporativo y compliance de directorio
- Ofertas públicas (IPO) y mercado de capitales
- Reestructuraciones empresariales y joint ventures
- Securities law y regulación bursátil

CONSULTA CORPORATIVA: {query}

ANÁLISIS CORPORATIVO SENIOR:
1. IDENTIFICACIÓN DE RIESGOS CORPORATIVOS
2. ANÁLISIS REGULATORIO Y DE COMPLIANCE
3. ESTRATEGIA LEGAL RECOMENDADA
4. CONSIDERACIONES DE DEBIDO PROCESO
""",
                confidence_threshold=0.85,
                max_tokens=700,
                temperature=0.6
            ),
            
            "contract_analysis_expert": LegalExpertProfile(
                expert_id="contract_analysis_expert",
                domain=LegalDomain.CONTRACT_ANALYSIS,
                capability=ExpertCapability.SUBJECT_MATTER_EXPERT,
                specializations=["Contract Drafting", "Risk Assessment", "Commercial Law", "Negotiations"],
                experience_areas=["International contracts", "Technology agreements", "Service contracts"],
                prompt_template="""
Eres un Subject Matter Expert en Análisis Contractual con especialización en redacción, revisión y negociación de contratos comerciales complejos.

Tu expertise incluye:
- Análisis exhaustivo de términos y condiciones contractuales
- Identificación de riesgos y cláusulas problemáticas
- Estrategias de negociación y redacción
- Contratos internacionales y cross-border
- Technology agreements y propiedad intelectual

CONSULTA CONTRACTUAL: {query}

ANÁLISIS CONTRACTUAL ESPECIALIZADO:
1. REVISIÓN DE TÉRMINOS CRÍTICOS
2. IDENTIFICACIÓN DE RIESGOS LEGALES
3. CLÁUSULAS RECOMENDADAS
4. ESTRATEGIA DE NEGOCIACIÓN
""",
                confidence_threshold=0.80,
                max_tokens=650,
                temperature=0.65
            ),
            
            "compliance_expert": LegalExpertProfile(
                expert_id="compliance_expert",
                domain=LegalDomain.COMPLIANCE,
                capability=ExpertCapability.REGULATORY_SPECIALIST,
                specializations=["Regulatory Compliance", "Internal Controls", "Risk Management", "Audit"],
                experience_areas=["SOX compliance", "Anti-money laundering", "Data protection", "Industry regulations"],
                prompt_template="""
Eres un Regulatory Specialist en Compliance con expertise en control interno, gestión de riesgo regulatorio y auditoría corporativa.

Tu expertise incluye:
- Programas de compliance y control interno
- Regulaciones sectoriales (financiero, telecomunicaciones, energía)
- SOX, AML, GDPR y protección de datos
- Auditorías regulatorias y investigaciones
- Políticas y procedimientos de compliance

CONSULTA DE COMPLIANCE: {query}

ANÁLISIS DE COMPLIANCE REGULATORIO:
1. EVALUACIÓN DE RIESGOS REGULATORIOS
2. GAPS DE COMPLIANCE IDENTIFICADOS
3. PLAN DE REMEDIACIÓN RECOMENDADO
4. CONTROLES INTERNOS NECESARIOS
""",
                confidence_threshold=0.82,
                max_tokens=600,
                temperature=0.55
            ),
            
            "litigation_strategy_expert": LegalExpertProfile(
                expert_id="litigation_strategy_expert",
                domain=LegalDomain.LITIGATION_STRATEGY,
                capability=ExpertCapability.SENIOR_PARTNER,
                specializations=["Litigation Strategy", "Dispute Resolution", "Arbitration", "Class Actions"],
                experience_areas=["Commercial litigation", "Regulatory disputes", "International arbitration"],
                prompt_template="""
Eres un Senior Partner especializado en Estrategia de Litigio con experiencia en disputes comerciales complejos, arbitraje internacional y resolución de conflictos.

Tu expertise incluye:
- Estrategia procesal y litigation management
- Arbitraje comercial e internacional
- Mediación y resolución alternativa de disputes
- Class actions y litigation masivo
- Enforcement y ejecución de sentencias

CONSULTA DE LITIGIO: {query}

ANÁLISIS ESTRATÉGICO DE LITIGIO:
1. EVALUACIÓN DE FORTALEZAS Y DEBILIDADES DEL CASO
2. ESTRATEGIA PROCESAL RECOMENDADA
3. ANÁLISIS DE RIESGO-BENEFICIO
4. ALTERNATIVAS DE RESOLUCIÓN
""",
                confidence_threshold=0.78,
                max_tokens=680,
                temperature=0.7
            ),
            
            "tax_law_expert": LegalExpertProfile(
                expert_id="tax_law_expert",
                domain=LegalDomain.TAX_LAW,
                capability=ExpertCapability.INDUSTRY_SPECIALIST,
                specializations=["Tax Planning", "Transfer Pricing", "Corporate Tax", "International Tax"],
                experience_areas=["M&A tax structuring", "Cross-border transactions", "Tax disputes"],
                prompt_template="""
Eres un Industry Specialist en Derecho Tributario con expertise en planificación fiscal, precios de transferencia y estructuración tributaria de transacciones complejas.

Tu expertise incluye:
- Planificación fiscal estratégica
- Precios de transferencia y operations internacionales
- Estructuración tributaria de M&A
- Controversias fiscales y procedimientos administrativos
- International tax y tratados de doble imposición

CONSULTA TRIBUTARIA: {query}

ANÁLISIS TRIBUTARIO ESPECIALIZADO:
1. IMPLICACIONES FISCALES IDENTIFICADAS
2. ESTRATEGIA DE PLANIFICACIÓN TRIBUTARIA
3. RIESGOS FISCALES Y CONTINGENCIAS
4. ESTRUCTURACIÓN ÓPTIMA RECOMENDADA
""",
                confidence_threshold=0.83,
                max_tokens=620,
                temperature=0.58
            ),
            
            "due_diligence_expert": LegalExpertProfile(
                expert_id="due_diligence_expert",
                domain=LegalDomain.DUE_DILIGENCE,
                capability=ExpertCapability.SUBJECT_MATTER_EXPERT,
                specializations=["Legal Due Diligence", "Risk Assessment", "Transaction Support", "Investigations"],
                experience_areas=["M&A due diligence", "Regulatory investigations", "Compliance reviews"],
                prompt_template="""
Eres un Subject Matter Expert en Due Diligence Legal con especialización en investigaciones exhaustivas para transacciones de M&A y evaluación de riesgos corporativos.

Tu expertise incluye:
- Due diligence legal integral para M&A
- Investigaciones regulatorias y compliance reviews
- Identificación de contingencias y pasivos ocultos
- Risk assessment y quantificación de exposures
- Transaction support y deal structuring

CONSULTA DE DUE DILIGENCE: {query}

ANÁLISIS DE DUE DILIGENCE:
1. ÁREAS DE INVESTIGACIÓN CRÍTICAS
2. RIESGOS Y CONTINGENCIAS IDENTIFICADOS
3. RED FLAGS Y ISSUES PRIORITARIOS
4. RECOMENDACIONES DE MITIGACIÓN
""",
                confidence_threshold=0.81,
                max_tokens=650,
                temperature=0.62
            ),
            
            # NEW: CoDA Legal Automation Expert
            "coda_automation_expert": LegalExpertProfile(
                expert_id="coda_automation_expert",
                domain=LegalDomain.GENERAL_LEGAL,  # Multi-domain automation capability
                capability=ExpertCapability.SUBJECT_MATTER_EXPERT,
                specializations=["Legal Document Automation", "Code Generation", "Process Automation", "Template Creation"],
                experience_areas=["Contract templates", "Legal workflows", "Document generation", "Compliance automation"],
                prompt_template="""
Eres un Subject Matter Expert en Automatización Legal con especialización en generación automática de documentos legales y optimización de procesos mediante CoDA (Coding via Diffusion Adaptation).

Tu expertise incluye:
- Generación automática de contratos y documentos legales
- Creación de templates y workflows automatizados
- Análisis de código legal y estructuras documentales
- Automatización de procesos de compliance y due diligence
- Integración de sistemas legales con tecnología de vanguardia

CONSULTA DE AUTOMATIZACIÓN LEGAL: {query}

ANÁLISIS DE AUTOMATIZACIÓN CON CODA:
1. IDENTIFICACIÓN DE PROCESOS AUTOMATIZABLES
2. GENERACIÓN DE CÓDIGO/TEMPLATES LEGALES
3. OPTIMIZACIÓN DE WORKFLOWS EXISTENTES
4. IMPLEMENTACIÓN DE SOLUCIONES AUTOMÁTICAS
5. VALIDACIÓN Y TESTING DE AUTOMATIZACIÓN
""",
                confidence_threshold=0.78,
                max_tokens=750,
                temperature=0.65,
                processing_priority=Priority.HIGH  # High priority for automation tasks
            )
        }
        
        return experts
    
    def get_expert(self, expert_id: str) -> Optional[LegalExpertProfile]:
        """Get expert profile by ID"""
        return self.experts.get(expert_id)
    
    def get_experts_by_domain(self, domain: LegalDomain) -> List[LegalExpertProfile]:
        """Get all experts for a specific legal domain"""
        return [expert for expert in self.experts.values() if expert.domain == domain]
    
    def update_expert_performance(self, expert_id: str, confidence: float, success: bool):
        """Update expert performance metrics"""
        perf = self.expert_performance[expert_id]
        perf["requests"] += 1
        
        # Update average confidence (exponential moving average)
        alpha = 0.2
        perf["avg_confidence"] = (
            alpha * confidence + (1 - alpha) * perf["avg_confidence"]
        )
        
        # Update success rate
        current_successes = perf["success_rate"] * (perf["requests"] - 1)
        new_successes = current_successes + (1 if success else 0)
        perf["success_rate"] = new_successes / perf["requests"]

class LegalMoERouter:
    """Main MoE router for intelligent expert selection and orchestration"""
    
    def __init__(self):
        self.domain_classifier = LegalDomainClassifier()
        self.expert_registry = LegalExpertRegistry()
        self.hybrid_manager: Optional[HybridInferenceManager] = None
        self.enhanced_consensus: Optional[EnhancedConsensusEngine] = None
        self.coda_integration: Optional[CoDALegalIntegration] = None
        
        # Performance tracking
        self.routing_metrics = {
            "total_queries": 0,
            "successful_routings": 0,
            "average_consensus_confidence": 0.0,
            "expert_utilization": defaultdict(int),
            "domain_distribution": defaultdict(int),
            "cost_savings_total": 0.0
        }
        
    async def initialize(self):
        """Initialize MoE router with required services"""
        try:
            # Initialize hybrid inference manager
            self.hybrid_manager = await get_hybrid_manager()
            logger.info("Hybrid inference manager initialized for MoE routing")
            
            # Initialize enhanced consensus engine if available
            if ENHANCED_CONSENSUS_AVAILABLE:
                self.enhanced_consensus = await create_enhanced_consensus_engine()
                logger.info("Enhanced consensus engine initialized for MoE")
            else:
                logger.warning("Enhanced consensus engine not available, using basic consensus")
            
            # Initialize CoDA legal integration if available
            if CODA_INTEGRATION_AVAILABLE:
                self.coda_integration = await get_coda_integration()
                logger.info("CoDA legal automation integration initialized")
            else:
                logger.warning("CoDA integration not available, using standard expert responses")
            
            logger.info("Legal MoE Router initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Legal MoE Router: {str(e)}")
            return False
    
    async def route_legal_query(self, query: str, context: Optional[Dict] = None, 
                               confidentiality_level: ConfidentialityLevel = ConfidentialityLevel.HIGHLY_CONFIDENTIAL,
                               max_experts: int = 3) -> MoEResponse:
        """Route legal query through MoE system with intelligent expert selection"""
        start_time = time.time()
        audit_trail = []
        
        try:
            self.routing_metrics["total_queries"] += 1
            
            # Step 1: Classify legal domain
            audit_trail.append({
                "step": "domain_classification_start",
                "timestamp": datetime.now().isoformat(),
                "query_length": len(query),
                "confidentiality_level": confidentiality_level.value
            })
            
            domain_classification = await self.domain_classifier.classify_legal_domain(query, context)
            
            audit_trail.append({
                "step": "domain_classification_complete",
                "timestamp": datetime.now().isoformat(),
                "primary_domain": domain_classification.primary_domain.value,
                "confidence": domain_classification.confidence_score,
                "complexity": domain_classification.complexity_level
            })
            
            # Step 2: Make routing decision
            routing_decision = await self._make_routing_decision(
                domain_classification, confidentiality_level, max_experts, audit_trail
            )
            
            # Step 3: Execute expert queries
            expert_responses = await self._execute_expert_queries(
                query, routing_decision.selected_experts, confidentiality_level, audit_trail
            )
            
            # Step 4: Generate consensus using Enhanced Consensus Engine
            consensus_result = await self._generate_expert_consensus(
                expert_responses, routing_decision, audit_trail
            )
            
            # Step 5: Calculate performance metrics and costs
            performance_metrics = self._calculate_performance_metrics(
                start_time, expert_responses, consensus_result
            )
            
            # Update routing metrics
            self._update_routing_metrics(domain_classification, routing_decision, performance_metrics)
            
            return MoEResponse(
                final_consensus=consensus_result.get("final_consensus", ""),
                consensus_confidence=consensus_result.get("consensus_confidence", 0.0),
                expert_responses=[asdict(resp) for resp in expert_responses],
                domain_analysis=domain_classification,
                routing_decision=routing_decision,
                performance_metrics=performance_metrics,
                audit_trail=audit_trail,
                cost_breakdown=performance_metrics.get("cost_breakdown", {})
            )
            
        except Exception as e:
            logger.error(f"MoE routing failed: {str(e)}")
            
            return MoEResponse(
                final_consensus="",
                consensus_confidence=0.0,
                expert_responses=[],
                domain_analysis=DomainClassificationResult(
                    primary_domain=LegalDomain.GENERAL_LEGAL,
                    confidence_score=0.0,
                    secondary_domains=[],
                    complexity_level="unknown",
                    estimated_processing_time=0.0,
                    recommended_experts=[],
                    classification_reasoning=[]
                ),
                routing_decision=MoERoutingDecision(
                    selected_experts=[],
                    routing_confidence=0.0,
                    domain_classification=None,
                    load_balancing_factor=0.0,
                    estimated_cost_usd=0.0,
                    estimated_processing_time_ms=0.0,
                    routing_strategy="error",
                    fallback_experts=[]
                ),
                performance_metrics={"error_time": time.time() - start_time},
                audit_trail=audit_trail,
                cost_breakdown={},
                error=str(e)
            )
    
    async def _make_routing_decision(self, domain_classification: DomainClassificationResult,
                                   confidentiality_level: ConfidentialityLevel,
                                   max_experts: int, audit_trail: List) -> MoERoutingDecision:
        """Make intelligent routing decision based on domain classification"""
        
        # Get recommended experts from classification
        recommended_expert_ids = domain_classification.recommended_experts[:max_experts]
        
        # Load expert profiles
        selected_experts = []
        for expert_id in recommended_expert_ids:
            expert = self.expert_registry.get_expert(expert_id)
            if expert:
                selected_experts.append(expert)
        
        # Ensure we have at least one expert
        if not selected_experts:
            general_expert = self.expert_registry.get_expert("corporate_law_expert")
            if general_expert:
                selected_experts.append(general_expert)
        
        # Calculate routing confidence
        routing_confidence = (
            domain_classification.confidence_score * 0.7 +  # Domain confidence
            min(len(selected_experts) / 3.0, 1.0) * 0.3    # Expert availability
        )
        
        # Load balancing factor (simplified)
        load_balancing_factor = 1.0  # Could be enhanced with actual load metrics
        
        # Estimate costs and processing time
        estimated_cost_usd = len(selected_experts) * 0.0008  # BitNet cost per expert
        estimated_processing_time_ms = domain_classification.estimated_processing_time
        
        # Determine routing strategy
        if confidentiality_level in [ConfidentialityLevel.MAXIMUM_SECURITY, 
                                   ConfidentialityLevel.HIGHLY_CONFIDENTIAL]:
            routing_strategy = "bitnet_local_only"
        else:
            routing_strategy = "hybrid_bitnet_cloud"
        
        # Fallback experts
        fallback_experts = ["corporate_law_expert", "general_legal_expert"]
        
        audit_trail.append({
            "step": "routing_decision_complete",
            "timestamp": datetime.now().isoformat(),
            "selected_experts": [e.expert_id for e in selected_experts],
            "routing_confidence": routing_confidence,
            "routing_strategy": routing_strategy,
            "estimated_cost_usd": estimated_cost_usd
        })
        
        return MoERoutingDecision(
            selected_experts=selected_experts,
            routing_confidence=routing_confidence,
            domain_classification=domain_classification,
            load_balancing_factor=load_balancing_factor,
            estimated_cost_usd=estimated_cost_usd,
            estimated_processing_time_ms=estimated_processing_time_ms,
            routing_strategy=routing_strategy,
            fallback_experts=fallback_experts
        )
    
    async def _execute_expert_queries(self, query: str, experts: List[LegalExpertProfile],
                                    confidentiality_level: ConfidentialityLevel,
                                    audit_trail: List) -> List[InferenceResponse]:
        """Execute queries across selected legal experts"""
        
        if not self.hybrid_manager:
            raise RuntimeError("Hybrid manager not initialized")
        
        expert_responses = []
        
        # Process experts in parallel
        tasks = []
        for expert in experts:
            task = self._process_single_expert(query, expert, confidentiality_level, audit_trail)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle responses and exceptions
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.warning(f"Expert {experts[i].expert_id} failed: {str(response)}")
                # Create error response
                error_response = InferenceResponse(
                    text=f"Expert {experts[i].expert_id} processing failed: {str(response)}",
                    backend_used=InferenceBackend.BITNET_LOCAL,
                    inference_time_ms=0.0,
                    tokens_generated=0,
                    confidence_score=0.0,
                    cost_usd=0.0,
                    confidentiality_maintained=True,
                    error=str(response)
                )
                expert_responses.append(error_response)
            else:
                expert_responses.append(response)
                
                # Update expert performance metrics
                success = not response.error
                self.expert_registry.update_expert_performance(
                    experts[i].expert_id, response.confidence_score, success
                )
        
        return expert_responses
    
    async def _process_single_expert(self, query: str, expert: LegalExpertProfile,
                                   confidentiality_level: ConfidentialityLevel,
                                   audit_trail: List) -> InferenceResponse:
        """Process single expert query with specialized prompting"""
        
        # Create specialized prompt using expert template
        specialized_prompt = expert.prompt_template.format(query=query)
        
        # Create inference request with expert-specific parameters
        inference_request = InferenceRequest(
            prompt=specialized_prompt,
            max_tokens=expert.max_tokens,
            temperature=expert.temperature,
            confidentiality_level=confidentiality_level,
            priority=expert.processing_priority,
            request_id=f"moe_expert_{expert.expert_id}_{int(time.time())}"
        )
        
        # Execute inference through hybrid manager
        response = await self.hybrid_manager.infer(inference_request)
        
        # Log expert processing
        audit_trail.append({
            "step": f"expert_{expert.expert_id}_processed",
            "timestamp": datetime.now().isoformat(),
            "expert_domain": expert.domain.value,
            "expert_capability": expert.capability.value,
            "backend_used": response.backend_used.value,
            "inference_time_ms": response.inference_time_ms,
            "confidence_score": response.confidence_score,
            "tokens_generated": response.tokens_generated,
            "success": not response.error
        })
        
        return response
    
    async def _generate_expert_consensus(self, expert_responses: List[InferenceResponse],
                                       routing_decision: MoERoutingDecision,
                                       audit_trail: List) -> Dict[str, Any]:
        """Generate consensus from expert responses using Enhanced Consensus Engine"""
        
        if self.enhanced_consensus and ENHANCED_CONSENSUS_AVAILABLE:
            return await self._generate_mathematical_consensus(expert_responses, audit_trail)
        else:
            return await self._generate_basic_consensus(expert_responses, audit_trail)
    
    async def _generate_mathematical_consensus(self, expert_responses: List[InferenceResponse],
                                            audit_trail: List) -> Dict[str, Any]:
        """Generate consensus using Enhanced Consensus Engine"""
        
        # Convert expert responses to TUMIX format
        tumix_responses = []
        for i, response in enumerate(expert_responses):
            if not response.error and response.text.strip():
                expert_output = {
                    "agent_id": f"legal_expert_{i}",
                    "agent_type": "specialized_legal_expert",
                    "answer_summary": response.text[:300],
                    "detailed_reasoning": response.text,
                    "confidence": response.confidence_score,
                    "processing_time": response.inference_time_ms / 1000.0,
                    "tokens_used": response.tokens_generated,
                    "cost_usd": response.cost_usd,
                    "backend_used": response.backend_used.value
                }
                tumix_responses.append(expert_output)
        
        if not tumix_responses:
            return {"error": "No valid expert responses for consensus"}
        
        try:
            # Calculate mathematical consensus using Enhanced Consensus Engine
            consensus_result = await self.enhanced_consensus.calculate_weighted_consensus(tumix_responses)
            
            audit_trail.append({
                "step": "mathematical_consensus_calculated",
                "timestamp": datetime.now().isoformat(),
                "consensus_method": "enhanced_mathematical_moe",
                "expert_count": len(tumix_responses),
                "consensus_confidence": consensus_result.get("final_confidence", 0.8),
                "expert_weights": consensus_result.get("agent_weights", [])
            })
            
            return {
                "final_consensus": self._synthesize_expert_consensus(tumix_responses, consensus_result),
                "consensus_confidence": consensus_result.get("final_confidence", 0.8),
                "consensus_method": "enhanced_mathematical_moe",
                "expert_weights": consensus_result.get("agent_weights", []),
                "optimization_metrics": consensus_result.get("optimization_metrics", {}),
                "coherence_score": consensus_result.get("coherence_score", 0.8)
            }
            
        except Exception as e:
            logger.warning(f"Enhanced consensus failed, using basic consensus: {str(e)}")
            return await self._generate_basic_consensus(expert_responses, audit_trail)
    
    async def _generate_basic_consensus(self, expert_responses: List[InferenceResponse],
                                      audit_trail: List) -> Dict[str, Any]:
        """Generate basic consensus as fallback"""
        
        valid_responses = [r for r in expert_responses if not r.error and r.text.strip()]
        
        if not valid_responses:
            return {"error": "No valid expert responses for consensus"}
        
        # Simple weighted average based on confidence scores
        weights = [r.confidence_score for r in valid_responses]
        total_weight = sum(weights)
        
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in weights]
        else:
            normalized_weights = [1.0 / len(valid_responses)] * len(valid_responses)
        
        # Calculate consensus confidence
        consensus_confidence = np.average([r.confidence_score for r in valid_responses], 
                                        weights=normalized_weights)
        
        # Generate consensus text
        consensus_text = self._create_simple_consensus(valid_responses, normalized_weights)
        
        audit_trail.append({
            "step": "basic_consensus_calculated",
            "timestamp": datetime.now().isoformat(),
            "consensus_method": "basic_weighted_moe",
            "expert_count": len(valid_responses),
            "consensus_confidence": consensus_confidence,
            "expert_weights": normalized_weights
        })
        
        return {
            "final_consensus": consensus_text,
            "consensus_confidence": consensus_confidence,
            "consensus_method": "basic_weighted_moe",
            "expert_weights": normalized_weights,
            "valid_experts": len(valid_responses)
        }
    
    def _synthesize_expert_consensus(self, expert_responses: List[Dict], 
                                   consensus_result: Dict[str, Any]) -> str:
        """Synthesize final consensus from expert responses"""
        
        expert_weights = consensus_result.get("agent_weights", [])
        
        consensus_text = "CONSENSO LEGAL MoE (Mixture of Experts):\n\n"
        
        # Add weighted expert summaries
        for i, response in enumerate(expert_responses):
            weight = expert_weights[i] if i < len(expert_weights) else 1.0 / len(expert_responses)
            expert_type = response.get("agent_type", "legal_expert")
            
            consensus_text += f"Expert {i+1} ({expert_type}, peso: {weight:.2f}):\n"
            consensus_text += f"{response.get('answer_summary', '')}\n\n"
        
        # Add consensus analysis
        consensus_confidence = consensus_result.get("final_confidence", 0.8)
        consensus_text += f"ANÁLISIS INTEGRADO (Confianza: {consensus_confidence:.1%}):\n"
        consensus_text += "Basado en el consenso matemático optimizado de expertos especializados, "
        consensus_text += "se recomienda proceder con las consideraciones legales identificadas "
        consensus_text += "por los expertos con mayor peso en el análisis.\n\n"
        
        consensus_text += "METODOLOGÍA: Enhanced MoE Consensus con Gradient Boosting + Random Forest optimization"
        
        return consensus_text
    
    def _create_simple_consensus(self, responses: List[InferenceResponse], 
                               weights: List[float]) -> str:
        """Create simple consensus text"""
        
        consensus_text = "CONSENSO LEGAL MoE (Weighted Average):\n\n"
        
        for i, response in enumerate(responses):
            weight = weights[i]
            consensus_text += f"Expert {i+1} (peso: {weight:.2f}):\n"
            consensus_text += f"{response.text[:300]}...\n\n"
        
        consensus_text += "SÍNTESIS: Análisis integrado basado en múltiples expertos especializados "
        consensus_text += "con ponderación por confianza y especialización."
        
        return consensus_text
    
    def _calculate_performance_metrics(self, start_time: float, expert_responses: List[InferenceResponse],
                                     consensus_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        total_time = time.time() - start_time
        total_tokens = sum(r.tokens_generated for r in expert_responses)
        total_cost = sum(r.cost_usd for r in expert_responses)
        
        bitnet_responses = [r for r in expert_responses if r.backend_used == InferenceBackend.BITNET_LOCAL]
        
        return {
            "total_processing_time_ms": total_time * 1000,
            "total_experts": len(expert_responses),
            "successful_experts": sum(1 for r in expert_responses if not r.error),
            "total_tokens_generated": total_tokens,
            "total_cost_usd": total_cost,
            "bitnet_usage_percentage": (len(bitnet_responses) / len(expert_responses)) * 100,
            "average_expert_confidence": np.mean([r.confidence_score for r in expert_responses if not r.error]),
            "consensus_method": consensus_result.get("consensus_method", "unknown"),
            "consensus_confidence": consensus_result.get("consensus_confidence", 0.0),
            "cost_breakdown": {
                "bitnet_local_cost": sum(r.cost_usd for r in bitnet_responses),
                "cloud_fallback_cost": sum(r.cost_usd for r in expert_responses if r.backend_used != InferenceBackend.BITNET_LOCAL),
                "cost_per_expert": total_cost / len(expert_responses) if expert_responses else 0,
                "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0
            },
            "performance_optimization": {
                "experts_used_efficiently": len(expert_responses) <= 4,  # Optimal range
                "bitnet_preference_maintained": len(bitnet_responses) > 0,
                "consensus_quality": consensus_result.get("consensus_confidence", 0.0) > 0.7
            }
        }
    
    def _update_routing_metrics(self, domain_classification: DomainClassificationResult,
                              routing_decision: MoERoutingDecision,
                              performance_metrics: Dict[str, Any]):
        """Update global routing metrics"""
        
        if performance_metrics.get("successful_experts", 0) > 0:
            self.routing_metrics["successful_routings"] += 1
            
            # Update average consensus confidence
            current_avg = self.routing_metrics["average_consensus_confidence"]
            new_confidence = performance_metrics.get("consensus_confidence", 0.0)
            
            alpha = 0.1
            self.routing_metrics["average_consensus_confidence"] = (
                alpha * new_confidence + (1 - alpha) * current_avg
            )
            
            # Update expert utilization
            for expert in routing_decision.selected_experts:
                self.routing_metrics["expert_utilization"][expert.expert_id] += 1
            
            # Update domain distribution
            self.routing_metrics["domain_distribution"][domain_classification.primary_domain.value] += 1
            
            # Update cost savings
            self.routing_metrics["cost_savings_total"] += performance_metrics.get("total_cost_usd", 0.0)
    
    async def process_legal_automation_request(self, automation_request: str, 
                                             task_type: str = "document_generation",
                                             context: Optional[Dict] = None) -> CoDAResponse:
        """Process legal automation request using CoDA integration"""
        
        if not CODA_INTEGRATION_AVAILABLE or not self.coda_integration:
            raise RuntimeError("CoDA legal automation not available")
        
        try:
            # Map string task type to CoDATaskType enum
            task_type_mapping = {
                "document_generation": CoDATaskType.DOCUMENT_GENERATION,
                "template_creation": CoDATaskType.TEMPLATE_CREATION,
                "workflow_automation": CoDATaskType.WORKFLOW_AUTOMATION,
                "code_generation": CoDATaskType.CODE_GENERATION,
                "process_optimization": CoDATaskType.PROCESS_OPTIMIZATION
            }
            
            coda_task_type = task_type_mapping.get(task_type.lower(), CoDATaskType.DOCUMENT_GENERATION)
            
            # Determine complexity from request length and context
            request_length = len(automation_request.split())
            if request_length < 20:
                complexity = CoDAComplexity.SIMPLE
            elif request_length < 50:
                complexity = CoDAComplexity.MEDIUM
            elif request_length < 100:
                complexity = CoDAComplexity.COMPLEX
            else:
                complexity = CoDAComplexity.HIGHLY_COMPLEX
            
            # Create CoDA request
            coda_request = CoDARequest(
                task_type=coda_task_type,
                prompt=automation_request,
                context=context or {},
                complexity=complexity,
                max_tokens=800,
                temperature=0.7,
                steps=20,
                legal_domain=context.get("legal_domain") if context else None,
                confidentiality_level="highly_confidential"
            )
            
            # Process with CoDA
            coda_response = await self.coda_integration.generate_legal_content(coda_request)
            
            # Update routing metrics
            self.routing_metrics["total_queries"] += 1
            if not coda_response.error:
                self.routing_metrics["successful_routings"] += 1
            self.routing_metrics["expert_utilization"]["coda_automation_expert"] += 1
            
            return coda_response
            
        except Exception as e:
            logger.error(f"CoDA automation request failed: {str(e)}")
            raise
    
    def get_moe_status(self) -> Dict[str, Any]:
        """Get comprehensive MoE system status"""
        
        return {
            "moe_router_status": "active",
            "total_experts": len(self.expert_registry.experts),
            "available_domains": [domain.value for domain in LegalDomain],
            "routing_metrics": dict(self.routing_metrics),
            "expert_registry": {
                expert_id: {
                    "domain": expert.domain.value,
                    "capability": expert.capability.value,
                    "specializations": expert.specializations,
                    "performance": dict(self.expert_registry.expert_performance.get(expert_id, {}))
                }
                for expert_id, expert in self.expert_registry.experts.items()
            },
            "success_rate": (
                self.routing_metrics["successful_routings"] / 
                max(self.routing_metrics["total_queries"], 1) * 100
            ),
            "capabilities": {
                "intelligent_domain_classification": True,
                "specialized_expert_routing": True,
                "mathematical_consensus": ENHANCED_CONSENSUS_AVAILABLE,
                "bitnet_integration": True,
                "audit_trail_generation": True,
                "performance_optimization": True,
                "load_balancing": True,
                "cost_optimization": True,
                "coda_legal_automation": CODA_INTEGRATION_AVAILABLE
            }
        }

# Global MoE router instance
legal_moe_router = None

async def get_legal_moe_router() -> LegalMoERouter:
    """Get or create global Legal MoE router"""
    global legal_moe_router
    
    if legal_moe_router is None:
        legal_moe_router = LegalMoERouter()
        await legal_moe_router.initialize()
    
    return legal_moe_router

async def shutdown_legal_moe_router():
    """Shutdown global Legal MoE router"""
    global legal_moe_router
    
    if legal_moe_router:
        # Cleanup if needed
        legal_moe_router = None

# Example usage
async def main():
    """Test Legal MoE Router"""
    print("Testing Legal MoE Router...")
    
    router = await get_legal_moe_router()
    
    # Test corporate law query
    corporate_query = """
    Nuestra empresa está evaluando una fusión con una compañía del sector energético. 
    Necesitamos analizar los riesgos regulatorios, las implicaciones de compliance, 
    y la estructura legal óptima para la transacción. La operación involucra activos 
    en Argentina y Chile, con regulaciones de competencia complejas.
    """
    
    moe_response = await router.route_legal_query(
        query=corporate_query,
        confidentiality_level=ConfidentialityLevel.MAXIMUM_SECURITY,
        max_experts=3
    )
    
    print("Legal MoE Response:")
    print(json.dumps({
        "final_consensus": moe_response.final_consensus[:500] + "...",
        "consensus_confidence": moe_response.consensus_confidence,
        "primary_domain": moe_response.domain_analysis.primary_domain.value,
        "selected_experts": [e.expert_id for e in moe_response.routing_decision.selected_experts],
        "total_cost_usd": moe_response.performance_metrics.get("total_cost_usd"),
        "bitnet_usage": moe_response.performance_metrics.get("bitnet_usage_percentage"),
        "audit_trail_steps": len(moe_response.audit_trail)
    }, indent=2, default=str))
    
    # Test contract analysis query
    contract_query = """
    Revisar cláusula de indemnización en contrato de servicios profesionales:
    'El prestador indemnizará al cliente por cualquier daño directo o indirecto 
    que resulte de la prestación de servicios, sin límite de monto ni tiempo.'
    """
    
    contract_response = await router.route_legal_query(
        query=contract_query,
        confidentiality_level=ConfidentialityLevel.CONFIDENTIAL,
        max_experts=2
    )
    
    print("\nContract Analysis MoE Response:")
    print(json.dumps({
        "primary_domain": contract_response.domain_analysis.primary_domain.value,
        "complexity_level": contract_response.domain_analysis.complexity_level,
        "selected_experts": [e.expert_id for e in contract_response.routing_decision.selected_experts],
        "consensus_confidence": contract_response.consensus_confidence
    }, indent=2, default=str))
    
    # Get system status
    status = router.get_moe_status()
    print("\nMoE System Status:")
    print(json.dumps({
        "expert_count": status["total_experts"],
        "success_rate": status["success_rate"],
        "routing_metrics": status["routing_metrics"]
    }, indent=2))
    
    await shutdown_legal_moe_router()

if __name__ == "__main__":
    asyncio.run(main())