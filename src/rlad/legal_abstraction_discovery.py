#!/usr/bin/env python3
"""
RLAD Legal Abstraction Discovery System
Reinforcement Learning for Abstraction Discovery Applied to Legal Domain

This module implements the RLAD methodology specifically adapted for legal analysis:
- Automatic discovery of legal abstractions (procedural patterns)
- Two-model architecture: abstraction generator (π_abs) + solution generator (π_sol)  
- RL optimization for legal reasoning improvement
- Integration with BitNet MoE for expert routing

Based on: "RLAD: Training LLMs to Discover Abstractions for Solving Reasoning Problems"
Legal Adaptation by: Ignacio Adrian Lerer - Senior Corporate Legal Consultant

Key Legal Applications:
1. Contract analysis abstractions (risk patterns, clause templates)
2. Compliance workflow abstractions (regulatory checklists) 
3. Due diligence abstractions (investigation frameworks)
4. Legal reasoning patterns (argumentation structures)

Author: Ignacio Adrian Lerer - Senior Corporate Legal Consultant
License: Proprietary - Confidential Legal Technology System
Version: 1.0.0-rlad-legal
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LegalAbstractionType(Enum):
    """Types of legal abstractions that can be discovered"""
    CONTRACT_RISK_PATTERN = "contract_risk_pattern"
    COMPLIANCE_CHECKLIST = "compliance_checklist" 
    DUE_DILIGENCE_FRAMEWORK = "due_diligence_framework"
    CLAUSE_TEMPLATE = "clause_template"
    LEGAL_ARGUMENT_STRUCTURE = "legal_argument_structure"
    REGULATORY_WORKFLOW = "regulatory_workflow"
    RISK_MITIGATION_STRATEGY = "risk_mitigation_strategy"
    PRECEDENT_ANALYSIS_PATTERN = "precedent_analysis_pattern"

class LegalDomain(Enum):
    """Legal domains for abstraction specialization"""
    CORPORATE_LAW = "corporate_law"
    CONTRACT_LAW = "contract_law" 
    COMPLIANCE = "compliance"
    LITIGATION = "litigation"
    TAX_LAW = "tax_law"
    LABOR_LAW = "labor_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    REGULATORY = "regulatory"

@dataclass
class LegalAbstraction:
    """Legal abstraction structure discovered by RLAD"""
    abstraction_id: str
    abstraction_type: LegalAbstractionType
    domain: LegalDomain
    title: str
    content: str
    applicable_scenarios: List[str]
    confidence_score: float
    reusability_score: float
    utility_score: float  # Based on RL rewards
    legal_citations: List[str] = None
    risk_level: str = "medium"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.legal_citations is None:
            self.legal_citations = []

@dataclass 
class LegalReasoningRequest:
    """Request for legal reasoning with abstractions"""
    document_content: str
    legal_query: str
    domain: LegalDomain
    jurisdiction: str = "AR"
    complexity_level: str = "medium"
    confidentiality_level: str = "highly_confidential"
    use_abstractions: bool = True
    max_abstractions: int = 5

@dataclass
class LegalAbstractionGeneration:
    """Generated abstractions for a legal problem"""
    abstractions: List[LegalAbstraction]
    generation_confidence: float
    reasoning_strategy: str
    estimated_utility: float
    processing_time_ms: float

@dataclass
class LegalSolutionWithAbstractions:
    """Legal solution enhanced with abstractions"""
    solution_content: str
    used_abstractions: List[LegalAbstraction]
    solution_confidence: float
    legal_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    citations: List[str]
    processing_metadata: Dict[str, Any]

class LegalAbstractionGenerator:
    """
    π_abs: Legal Abstraction Generator
    Generates useful legal abstractions given a legal problem/document
    """
    
    def __init__(self):
        self.abstraction_templates = self._initialize_abstraction_templates()
        self.legal_patterns = self._initialize_legal_patterns()
        self.performance_cache = {}
        
    def _initialize_abstraction_templates(self) -> Dict[LegalAbstractionType, List[str]]:
        """Initialize templates for different types of legal abstractions"""
        return {
            LegalAbstractionType.CONTRACT_RISK_PATTERN: [
                "Para análisis de riesgo en {contract_type}, verificar: {risk_elements}",
                "Patrón de riesgo recurrente: {pattern_description} - Mitigación: {mitigation_strategy}",
                "Cláusula problemática identificada: {clause_type} - Riesgo: {risk_description}"
            ],
            
            LegalAbstractionType.COMPLIANCE_CHECKLIST: [
                "Checklist de cumplimiento {regulation}: {checklist_items}",
                "Requisitos regulatorios obligatorios: {mandatory_requirements}",
                "Proceso de verificación: {verification_steps}"
            ],
            
            LegalAbstractionType.DUE_DILIGENCE_FRAMEWORK: [
                "Framework de DD para {transaction_type}: {investigation_areas}",
                "Red flags en DD: {warning_indicators} - Acción requerida: {required_actions}",
                "Documentación crítica: {critical_documents} - Timeframe: {review_timeline}"
            ],
            
            LegalAbstractionType.CLAUSE_TEMPLATE: [
                "Template de cláusula {clause_type}: {template_structure}",
                "Elementos esenciales para {clause_purpose}: {essential_elements}",
                "Variaciones jurisdiccionales: {jurisdictional_differences}"
            ],
            
            LegalAbstractionType.LEGAL_ARGUMENT_STRUCTURE: [
                "Estructura argumental para {legal_issue}: {argument_framework}",
                "Precedentes aplicables: {relevant_precedents} - Distinctions: {key_distinctions}",
                "Contra-argumentos anticipados: {counter_arguments} - Refutación: {refutation_strategy}"
            ]
        }
    
    def _initialize_legal_patterns(self) -> Dict[LegalDomain, Dict[str, List[str]]]:
        """Initialize legal reasoning patterns by domain"""
        return {
            LegalDomain.CORPORATE_LAW: {
                "risk_indicators": [
                    "falta de autorización societaria", "conflicts de interés",
                    "incumplimiento fiduciario", "violación de estatutos"
                ],
                "verification_steps": [
                    "revisar actas de directorio", "verificar poderes vigentes",
                    "confirmar quórum y mayorías", "validar autorizaciones especiales"
                ]
            },
            
            LegalDomain.CONTRACT_LAW: {
                "essential_elements": [
                    "objeto determinado", "causa lícita", "consentimiento válido",
                    "capacidad de las partes", "forma requerida por ley"
                ],
                "risk_patterns": [
                    "ambigüedad en términos", "falta de cláusula de terminación",
                    "indemnización ilimitada", "ausencia de force majeure"
                ]
            },
            
            LegalDomain.COMPLIANCE: {
                "regulatory_frameworks": [
                    "ley 27.401 (compliance)", "UIF (lavado de dinero)", 
                    "GDPR (protección datos)", "SOX (controles internos)"
                ],
                "control_mechanisms": [
                    "políticas y procedimientos", "capacitación obligatoria",
                    "canal de denuncias", "monitoreo continuo"
                ]
            }
        }
    
    async def generate_abstractions(self, request: LegalReasoningRequest) -> LegalAbstractionGeneration:
        """
        Generate legal abstractions for a given legal problem
        π_abs(z|x): abstractions given legal document/query
        """
        start_time = time.time()
        
        # Analyze the legal document and query
        domain_analysis = self._analyze_legal_domain(request)
        complexity_assessment = self._assess_complexity(request)
        
        # Generate relevant abstractions
        candidate_abstractions = []
        
        # 1. Contract Risk Pattern Abstractions
        if request.domain in [LegalDomain.CORPORATE_LAW, LegalDomain.CONTRACT_LAW]:
            risk_abstractions = await self._generate_risk_pattern_abstractions(request, domain_analysis)
            candidate_abstractions.extend(risk_abstractions)
        
        # 2. Compliance Checklist Abstractions  
        if "compliance" in request.legal_query.lower() or request.domain == LegalDomain.COMPLIANCE:
            compliance_abstractions = await self._generate_compliance_abstractions(request, domain_analysis)
            candidate_abstractions.extend(compliance_abstractions)
            
        # 3. Due Diligence Framework Abstractions
        if "due diligence" in request.legal_query.lower() or "fusión" in request.legal_query.lower():
            dd_abstractions = await self._generate_due_diligence_abstractions(request, domain_analysis)
            candidate_abstractions.extend(dd_abstractions)
            
        # 4. Legal Argument Structure Abstractions
        if request.domain == LegalDomain.LITIGATION:
            argument_abstractions = await self._generate_argument_abstractions(request, domain_analysis)
            candidate_abstractions.extend(argument_abstractions)
        
        # Rank and select best abstractions
        ranked_abstractions = self._rank_abstractions(candidate_abstractions, request)
        selected_abstractions = ranked_abstractions[:request.max_abstractions]
        
        # Calculate generation metrics
        processing_time = (time.time() - start_time) * 1000
        generation_confidence = self._calculate_generation_confidence(selected_abstractions)
        estimated_utility = self._estimate_utility(selected_abstractions, request)
        
        return LegalAbstractionGeneration(
            abstractions=selected_abstractions,
            generation_confidence=generation_confidence,
            reasoning_strategy=self._determine_reasoning_strategy(selected_abstractions),
            estimated_utility=estimated_utility,
            processing_time_ms=processing_time
        )
    
    async def _generate_risk_pattern_abstractions(self, 
                                                  request: LegalReasoningRequest,
                                                  domain_analysis: Dict) -> List[LegalAbstraction]:
        """Generate contract risk pattern abstractions"""
        abstractions = []
        
        # Identify potential risk patterns in the document
        risk_patterns = self._identify_risk_patterns(request.document_content, request.domain)
        
        for risk_pattern in risk_patterns:
            abstraction = LegalAbstraction(
                abstraction_id=f"risk_{len(abstractions)}_" + str(int(time.time())),
                abstraction_type=LegalAbstractionType.CONTRACT_RISK_PATTERN,
                domain=request.domain,
                title=f"Patrón de Riesgo: {risk_pattern['type']}",
                content=f"""
Patrón de riesgo identificado en {risk_pattern['type']}:

ELEMENTOS DE RIESGO:
{self._format_risk_elements(risk_pattern['elements'])}

INDICADORES:
{self._format_risk_indicators(risk_pattern['indicators'])}

ESTRATEGIA DE MITIGACIÓN:
{self._format_mitigation_strategy(risk_pattern['mitigation'])}

PRECEDENTES RELEVANTES:
{self._format_relevant_precedents(risk_pattern.get('precedents', []))}
""",
                applicable_scenarios=risk_pattern.get('scenarios', []),
                confidence_score=risk_pattern.get('confidence', 0.85),
                reusability_score=0.9,  # High reusability for risk patterns
                utility_score=0.85,     # Will be updated by RL
                legal_citations=risk_pattern.get('citations', []),
                risk_level=risk_pattern.get('risk_level', 'medium')
            )
            abstractions.append(abstraction)
        
        return abstractions
    
    async def _generate_compliance_abstractions(self, 
                                                request: LegalReasoningRequest,
                                                domain_analysis: Dict) -> List[LegalAbstraction]:
        """Generate compliance checklist abstractions"""
        abstractions = []
        
        # Identify applicable regulatory frameworks
        applicable_regulations = self._identify_applicable_regulations(request)
        
        for regulation in applicable_regulations:
            abstraction = LegalAbstraction(
                abstraction_id=f"compliance_{len(abstractions)}_" + str(int(time.time())),
                abstraction_type=LegalAbstractionType.COMPLIANCE_CHECKLIST,
                domain=LegalDomain.COMPLIANCE,
                title=f"Checklist de Cumplimiento: {regulation['name']}",
                content=f"""
Checklist de cumplimiento para {regulation['name']}:

REQUISITOS OBLIGATORIOS:
{self._format_mandatory_requirements(regulation['mandatory'])}

DOCUMENTACIÓN REQUERIDA:
{self._format_required_documentation(regulation['documentation'])}

PLAZOS Y PROCEDIMIENTOS:
{self._format_deadlines_procedures(regulation['procedures'])}

CONTROLES DE VERIFICACIÓN:
{self._format_verification_controls(regulation['controls'])}

CONSECUENCIAS DE INCUMPLIMIENTO:
{self._format_non_compliance_consequences(regulation['consequences'])}
""",
                applicable_scenarios=regulation.get('scenarios', []),
                confidence_score=regulation.get('confidence', 0.9),
                reusability_score=0.95,  # Very high reusability for compliance
                utility_score=0.9,
                legal_citations=regulation.get('citations', []),
                risk_level=regulation.get('risk_level', 'high')  # Compliance is typically high risk
            )
            abstractions.append(abstraction)
        
        return abstractions
    
    def _identify_risk_patterns(self, document: str, domain: LegalDomain) -> List[Dict]:
        """Identify risk patterns in legal document"""
        risk_patterns = []
        document_lower = document.lower()
        
        # Corporate law risk patterns
        if domain == LegalDomain.CORPORATE_LAW:
            if any(keyword in document_lower for keyword in ["fusión", "merger", "adquisición", "acquisition"]):
                risk_patterns.append({
                    'type': 'Riesgo de Fusión/Adquisición',
                    'elements': [
                        'Autorización de accionistas', 'Due diligence completa',
                        'Valoración independiente', 'Disclosure a reguladores'
                    ],
                    'indicators': [
                        'Falta de resolución de directorio', 'DD incompleta',
                        'Valuación desactualizada', 'Regulatory approval pendiente'
                    ],
                    'mitigation': [
                        'Obtener todas las autorizaciones societarias',
                        'Completar due diligence integral',
                        'Actualizar valuación con expertos independientes',
                        'Solicitar aprobaciones regulatorias necesarias'
                    ],
                    'confidence': 0.87,
                    'scenarios': ['M&A', 'Corporate restructuring', 'Joint ventures'],
                    'risk_level': 'high'
                })
        
        # Contract law risk patterns
        if domain == LegalDomain.CONTRACT_LAW:
            if any(keyword in document_lower for keyword in ["indemnización", "indemnity", "liability"]):
                risk_patterns.append({
                    'type': 'Riesgo de Indemnización Ilimitada',
                    'elements': [
                        'Caps de indemnización', 'Exclusiones específicas',
                        'Seguro de responsabilidad', 'Mutual indemnification'
                    ],
                    'indicators': [
                        'Ausencia de caps', 'Indemnización unilateral',
                        'Sin exclusión de daños indirectos', 'Falta de seguro'
                    ],
                    'mitigation': [
                        'Establecer caps de indemnización',
                        'Incluir exclusiones de daños indirectos',
                        'Requerir mutual indemnification',
                        'Exigir seguro de responsabilidad adecuado'
                    ],
                    'confidence': 0.91,
                    'scenarios': ['Service agreements', 'Supply contracts', 'License agreements'],
                    'risk_level': 'high'
                })
        
        return risk_patterns
    
    def _identify_applicable_regulations(self, request: LegalReasoningRequest) -> List[Dict]:
        """Identify applicable regulatory frameworks"""
        regulations = []
        query_lower = request.legal_query.lower()
        document_lower = request.document_content.lower()
        
        # Argentine compliance regulations
        if request.jurisdiction == "AR":
            if any(keyword in query_lower + document_lower for keyword in ["compliance", "lavado", "uif"]):
                regulations.append({
                    'name': 'Ley 27.401 - Régimen de Responsabilidad Penal Empresaria',
                    'mandatory': [
                        'Programa de Integridad implementado',
                        'Código de Ética aprobado por directorio',
                        'Canal de denuncias funcionando',
                        'Capacitación anual obligatoria',
                        'Due diligence de terceros'
                    ],
                    'documentation': [
                        'Políticas y procedimientos documentados',
                        'Registros de capacitación',
                        'Reportes de investigaciones internas',
                        'Evaluaciones de riesgo anuales'
                    ],
                    'procedures': [
                        'Aprobación de directorio: dentro de 90 días',
                        'Capacitación: al menos una vez por año',
                        'Revisión de políticas: cada 2 años',
                        'Reportes a UIF: según corresponda'
                    ],
                    'controls': [
                        'Auditoría interna del programa',
                        'Monitoreo de transacciones',
                        'Background checks de empleados',
                        'Revisión periódica de terceros'
                    ],
                    'consequences': [
                        'Multa hasta $500M pesos',
                        'Inhabilitación para contratar con el Estado',
                        'Publicación de sanción',
                        'Responsabilidad penal de directivos'
                    ],
                    'confidence': 0.93,
                    'scenarios': ['Corporate compliance', 'Anti-corruption', 'Third-party management'],
                    'risk_level': 'high'
                })
        
        return regulations
    
    def _format_risk_elements(self, elements: List[str]) -> str:
        return "\\n".join([f"• {element}" for element in elements])
    
    def _format_risk_indicators(self, indicators: List[str]) -> str:
        return "\\n".join([f"⚠️ {indicator}" for indicator in indicators])
    
    def _format_mitigation_strategy(self, strategies: List[str]) -> str:
        return "\\n".join([f"✅ {strategy}" for strategy in strategies])
    
    def _format_relevant_precedents(self, precedents: List[str]) -> str:
        if not precedents:
            return "• Análisis de precedentes pendiente"
        return "\\n".join([f"📚 {precedent}" for precedent in precedents])
    
    def _format_mandatory_requirements(self, requirements: List[str]) -> str:
        return "\\n".join([f"✓ {req}" for req in requirements])
    
    def _format_required_documentation(self, docs: List[str]) -> str:
        return "\\n".join([f"📄 {doc}" for doc in docs])
    
    def _format_deadlines_procedures(self, procedures: List[str]) -> str:
        return "\\n".join([f"⏰ {proc}" for proc in procedures])
    
    def _format_verification_controls(self, controls: List[str]) -> str:
        return "\\n".join([f"🔍 {control}" for control in controls])
    
    def _format_non_compliance_consequences(self, consequences: List[str]) -> str:
        return "\\n".join([f"⚖️ {consequence}" for consequence in consequences])
    
    def _analyze_legal_domain(self, request: LegalReasoningRequest) -> Dict[str, Any]:
        """Analyze the legal domain and context"""
        return {
            'primary_domain': request.domain,
            'complexity': request.complexity_level,
            'jurisdiction': request.jurisdiction,
            'document_length': len(request.document_content),
            'query_type': self._classify_query_type(request.legal_query)
        }
    
    def _assess_complexity(self, request: LegalReasoningRequest) -> str:
        """Assess the complexity of the legal problem"""
        complexity_indicators = 0
        
        query_lower = request.legal_query.lower()
        doc_lower = request.document_content.lower()
        
        # Complexity indicators
        if len(request.document_content) > 5000:
            complexity_indicators += 1
        if any(word in query_lower for word in ["fusión", "merger", "compliance", "due diligence"]):
            complexity_indicators += 1
        if request.domain in [LegalDomain.CORPORATE_LAW, LegalDomain.COMPLIANCE]:
            complexity_indicators += 1
        
        if complexity_indicators >= 2:
            return "high"
        elif complexity_indicators == 1:
            return "medium"
        else:
            return "low"
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of legal query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["riesgo", "risk", "peligro"]):
            return "risk_analysis"
        elif any(word in query_lower for word in ["compliance", "cumplimiento", "regulatorio"]):
            return "compliance_check"
        elif any(word in query_lower for word in ["contrato", "contract", "cláusula"]):
            return "contract_review"
        elif any(word in query_lower for word in ["due diligence", "investigación"]):
            return "due_diligence"
        else:
            return "general_legal"
    
    def _rank_abstractions(self, abstractions: List[LegalAbstraction], request: LegalReasoningRequest) -> List[LegalAbstraction]:
        """Rank abstractions by relevance and utility"""
        
        def calculate_score(abstraction: LegalAbstraction) -> float:
            score = 0.0
            
            # Domain relevance (40%)
            if abstraction.domain == request.domain:
                score += 0.4
            
            # Confidence score (30%)
            score += abstraction.confidence_score * 0.3
            
            # Utility score (20%)
            score += abstraction.utility_score * 0.2
            
            # Reusability (10%)
            score += abstraction.reusability_score * 0.1
            
            return score
        
        return sorted(abstractions, key=calculate_score, reverse=True)
    
    def _calculate_generation_confidence(self, abstractions: List[LegalAbstraction]) -> float:
        """Calculate confidence in the generated abstractions"""
        if not abstractions:
            return 0.0
        
        confidence_scores = [abs.confidence_score for abs in abstractions]
        return sum(confidence_scores) / len(confidence_scores)
    
    def _estimate_utility(self, abstractions: List[LegalAbstraction], request: LegalReasoningRequest) -> float:
        """Estimate utility of abstractions for the legal problem"""
        if not abstractions:
            return 0.0
        
        utility_scores = [abs.utility_score for abs in abstractions]
        return sum(utility_scores) / len(utility_scores)
    
    def _determine_reasoning_strategy(self, abstractions: List[LegalAbstraction]) -> str:
        """Determine the reasoning strategy based on abstractions"""
        abstraction_types = [abs.abstraction_type for abs in abstractions]
        
        if LegalAbstractionType.CONTRACT_RISK_PATTERN in abstraction_types:
            return "risk_focused_analysis"
        elif LegalAbstractionType.COMPLIANCE_CHECKLIST in abstraction_types:
            return "compliance_verification"
        elif LegalAbstractionType.DUE_DILIGENCE_FRAMEWORK in abstraction_types:
            return "systematic_investigation"
        else:
            return "general_legal_analysis"

class LegalSolutionGenerator:
    """
    π_sol: Legal Solution Generator
    Generates legal solutions conditioned on abstractions
    """
    
    def __init__(self):
        self.solution_templates = self._initialize_solution_templates()
    
    def _initialize_solution_templates(self) -> Dict[str, str]:
        """Initialize templates for different reasoning strategies"""
        return {
            "risk_focused_analysis": """
ANÁLISIS DE RIESGOS LEGAL

Basado en las abstracciones identificadas, se realiza el siguiente análisis:

{abstraction_guidance}

RIESGOS IDENTIFICADOS:
{identified_risks}

ANÁLISIS DETALLADO:
{detailed_analysis}

RECOMENDACIONES:
{recommendations}

CITAS LEGALES:
{legal_citations}
""",
            
            "compliance_verification": """
VERIFICACIÓN DE CUMPLIMIENTO

Checklist de cumplimiento aplicado:

{abstraction_guidance}

ESTADO DE CUMPLIMIENTO:
{compliance_status}

GAPS IDENTIFICADOS:
{compliance_gaps}

PLAN DE REMEDIACIÓN:
{remediation_plan}

MARCO REGULATORIO:
{regulatory_framework}
""",
            
            "systematic_investigation": """
INVESTIGACIÓN SISTEMÁTICA

Framework de investigación aplicado:

{abstraction_guidance}

ÁREAS DE INVESTIGACIÓN:
{investigation_areas}

HALLAZGOS:
{findings}

RED FLAGS:
{red_flags}

PRÓXIMOS PASOS:
{next_steps}
"""
        }
    
    async def generate_solution(self, 
                                request: LegalReasoningRequest,
                                abstractions: LegalAbstractionGeneration) -> LegalSolutionWithAbstractions:
        """
        Generate legal solution conditioned on abstractions
        π_sol(y|x,z): solution given document and abstractions
        """
        start_time = time.time()
        
        # Select the reasoning strategy
        strategy = abstractions.reasoning_strategy
        template = self.solution_templates.get(strategy, self.solution_templates["risk_focused_analysis"])
        
        # Generate solution content using abstractions
        solution_content = await self._generate_solution_content(
            request, abstractions.abstractions, strategy, template
        )
        
        # Perform legal analysis
        legal_analysis = self._perform_legal_analysis(request, abstractions.abstractions)
        
        # Assess risks
        risk_assessment = self._assess_risks(request, abstractions.abstractions)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(request, abstractions.abstractions)
        
        # Collect citations
        citations = self._collect_citations(abstractions.abstractions)
        
        # Calculate solution confidence
        solution_confidence = self._calculate_solution_confidence(
            abstractions, legal_analysis, risk_assessment
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return LegalSolutionWithAbstractions(
            solution_content=solution_content,
            used_abstractions=abstractions.abstractions,
            solution_confidence=solution_confidence,
            legal_analysis=legal_analysis,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            citations=citations,
            processing_metadata={
                'strategy': strategy,
                'processing_time_ms': processing_time,
                'abstractions_used': len(abstractions.abstractions),
                'generation_confidence': abstractions.generation_confidence
            }
        )
    
    async def _generate_solution_content(self, 
                                         request: LegalReasoningRequest,
                                         abstractions: List[LegalAbstraction],
                                         strategy: str,
                                         template: str) -> str:
        """Generate the main solution content"""
        
        # Prepare abstraction guidance
        abstraction_guidance = self._format_abstraction_guidance(abstractions)
        
        if strategy == "risk_focused_analysis":
            return template.format(
                abstraction_guidance=abstraction_guidance,
                identified_risks=self._format_identified_risks(abstractions),
                detailed_analysis=self._generate_detailed_risk_analysis(request, abstractions),
                recommendations=self._format_risk_recommendations(abstractions),
                legal_citations=self._format_legal_citations(abstractions)
            )
        
        elif strategy == "compliance_verification":
            return template.format(
                abstraction_guidance=abstraction_guidance,
                compliance_status=self._assess_compliance_status(request, abstractions),
                compliance_gaps=self._identify_compliance_gaps(request, abstractions),
                remediation_plan=self._generate_remediation_plan(abstractions),
                regulatory_framework=self._format_regulatory_framework(abstractions)
            )
        
        elif strategy == "systematic_investigation":
            return template.format(
                abstraction_guidance=abstraction_guidance,
                investigation_areas=self._define_investigation_areas(abstractions),
                findings=self._summarize_findings(request, abstractions),
                red_flags=self._identify_red_flags(request, abstractions),
                next_steps=self._define_next_steps(abstractions)
            )
        
        else:
            # Default general analysis
            return f"""
ANÁLISIS LEGAL GENERAL

Abstracciones aplicadas:
{abstraction_guidance}

ANÁLISIS DEL DOCUMENTO:
{self._analyze_document_content(request)}

CONSIDERACIONES LEGALES:
{self._generate_legal_considerations(request, abstractions)}

RECOMENDACIONES:
{self._format_general_recommendations(abstractions)}
"""
    
    def _format_abstraction_guidance(self, abstractions: List[LegalAbstraction]) -> str:
        """Format the abstractions as guidance"""
        if not abstractions:
            return "• Análisis general sin abstracciones específicas"
        
        formatted = []
        for i, abs in enumerate(abstractions, 1):
            formatted.append(f"""
{i}. {abs.title}
   Tipo: {abs.abstraction_type.value}
   Confianza: {abs.confidence_score:.2f}
   
   {abs.content[:200]}{"..." if len(abs.content) > 200 else ""}
""")
        
        return "\\n".join(formatted)
    
    def _format_identified_risks(self, abstractions: List[LegalAbstraction]) -> str:
        """Format identified risks from abstractions"""
        risks = []
        for abs in abstractions:
            if abs.abstraction_type == LegalAbstractionType.CONTRACT_RISK_PATTERN:
                risks.append(f"• {abs.title} (Nivel: {abs.risk_level})")
        
        return "\\n".join(risks) if risks else "• No se identificaron riesgos específicos mediante abstracciones"
    
    def _generate_detailed_risk_analysis(self, 
                                         request: LegalReasoningRequest, 
                                         abstractions: List[LegalAbstraction]) -> str:
        """Generate detailed risk analysis"""
        analysis_parts = []
        
        for abs in abstractions:
            if abs.abstraction_type == LegalAbstractionType.CONTRACT_RISK_PATTERN:
                analysis_parts.append(f"""
{abs.title}:
- Elementos de riesgo identificados en el documento
- Probabilidad: {'Alta' if abs.risk_level == 'high' else 'Media' if abs.risk_level == 'medium' else 'Baja'}
- Impacto potencial: Requiere atención {abs.risk_level}
- Mitigación sugerida según abstracción aplicada
""")
        
        return "\\n".join(analysis_parts) if analysis_parts else "Análisis de riesgo general aplicado."
    
    def _format_risk_recommendations(self, abstractions: List[LegalAbstraction]) -> str:
        """Format risk-based recommendations"""
        recommendations = []
        
        for abs in abstractions:
            if abs.abstraction_type == LegalAbstractionType.CONTRACT_RISK_PATTERN:
                if abs.risk_level == "high":
                    recommendations.append(f"🔴 URGENTE: {abs.title} - Requiere acción inmediata")
                elif abs.risk_level == "medium":
                    recommendations.append(f"🟡 MODERADO: {abs.title} - Revisar y mitigar")
                else:
                    recommendations.append(f"🟢 BAJO: {abs.title} - Monitorear")
        
        return "\\n".join(recommendations) if recommendations else "• Seguir análisis de riesgo estándar"
    
    def _format_legal_citations(self, abstractions: List[LegalAbstraction]) -> str:
        """Format legal citations from abstractions"""
        all_citations = []
        for abs in abstractions:
            all_citations.extend(abs.legal_citations)
        
        unique_citations = list(set(all_citations))
        return "\\n".join([f"• {citation}" for citation in unique_citations]) if unique_citations else "• Citas legales pendientes de verificación"
    
    def _perform_legal_analysis(self, 
                                request: LegalReasoningRequest,
                                abstractions: List[LegalAbstraction]) -> Dict[str, Any]:
        """Perform comprehensive legal analysis"""
        return {
            'domain': request.domain.value,
            'jurisdiction': request.jurisdiction,
            'complexity_assessment': request.complexity_level,
            'abstractions_applied': len(abstractions),
            'risk_level': self._determine_overall_risk_level(abstractions),
            'compliance_status': self._assess_overall_compliance(abstractions),
            'recommendations_count': len(self._generate_recommendations(request, abstractions))
        }
    
    def _assess_risks(self, 
                      request: LegalReasoningRequest,
                      abstractions: List[LegalAbstraction]) -> Dict[str, Any]:
        """Assess risks based on abstractions"""
        risk_abstractions = [
            abs for abs in abstractions 
            if abs.abstraction_type == LegalAbstractionType.CONTRACT_RISK_PATTERN
        ]
        
        high_risk_count = sum(1 for abs in risk_abstractions if abs.risk_level == "high")
        medium_risk_count = sum(1 for abs in risk_abstractions if abs.risk_level == "medium")
        low_risk_count = sum(1 for abs in risk_abstractions if abs.risk_level == "low")
        
        return {
            'total_risks_identified': len(risk_abstractions),
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'overall_risk_score': self._calculate_overall_risk_score(risk_abstractions),
            'requires_immediate_attention': high_risk_count > 0
        }
    
    def _generate_recommendations(self, 
                                  request: LegalReasoningRequest,
                                  abstractions: List[LegalAbstraction]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        for abs in abstractions:
            if abs.abstraction_type == LegalAbstractionType.CONTRACT_RISK_PATTERN:
                if abs.risk_level == "high":
                    recommendations.append(f"Atender inmediatamente: {abs.title}")
                elif abs.risk_level == "medium":
                    recommendations.append(f"Revisar y mitigar: {abs.title}")
        
        # Compliance recommendations
        for abs in abstractions:
            if abs.abstraction_type == LegalAbstractionType.COMPLIANCE_CHECKLIST:
                recommendations.append(f"Verificar cumplimiento: {abs.title}")
        
        # Due diligence recommendations
        for abs in abstractions:
            if abs.abstraction_type == LegalAbstractionType.DUE_DILIGENCE_FRAMEWORK:
                recommendations.append(f"Investigar sistemáticamente: {abs.title}")
        
        # Default recommendations if none from abstractions
        if not recommendations:
            recommendations = [
                "Realizar revisión legal integral del documento",
                "Consultar con experto en la materia específica",
                "Documentar todos los hallazgos para auditoría"
            ]
        
        return recommendations
    
    def _collect_citations(self, abstractions: List[LegalAbstraction]) -> List[str]:
        """Collect all legal citations from abstractions"""
        all_citations = []
        for abs in abstractions:
            all_citations.extend(abs.legal_citations)
        
        return list(set(all_citations))  # Remove duplicates
    
    def _calculate_solution_confidence(self, 
                                       abstractions: LegalAbstractionGeneration,
                                       legal_analysis: Dict[str, Any],
                                       risk_assessment: Dict[str, Any]) -> float:
        """Calculate overall solution confidence"""
        
        # Base confidence from abstractions
        abstraction_confidence = abstractions.generation_confidence
        
        # Adjust based on risk assessment
        risk_adjustment = 0.0
        if risk_assessment['total_risks_identified'] > 0:
            # Lower confidence if high risks are present
            if risk_assessment['high_risk_count'] > 0:
                risk_adjustment -= 0.1
            # Increase confidence if risks are well-identified
            risk_adjustment += 0.05
        
        # Adjust based on number of abstractions used
        abstraction_count_adjustment = min(0.1, len(abstractions.abstractions) * 0.02)
        
        final_confidence = min(1.0, abstraction_confidence + risk_adjustment + abstraction_count_adjustment)
        return max(0.0, final_confidence)
    
    def _determine_overall_risk_level(self, abstractions: List[LegalAbstraction]) -> str:
        """Determine overall risk level"""
        risk_abstractions = [
            abs for abs in abstractions 
            if abs.abstraction_type == LegalAbstractionType.CONTRACT_RISK_PATTERN
        ]
        
        if any(abs.risk_level == "high" for abs in risk_abstractions):
            return "high"
        elif any(abs.risk_level == "medium" for abs in risk_abstractions):
            return "medium"
        else:
            return "low"
    
    def _assess_overall_compliance(self, abstractions: List[LegalAbstraction]) -> str:
        """Assess overall compliance status"""
        compliance_abstractions = [
            abs for abs in abstractions 
            if abs.abstraction_type == LegalAbstractionType.COMPLIANCE_CHECKLIST
        ]
        
        if compliance_abstractions:
            return "requires_verification"
        else:
            return "unknown"
    
    def _calculate_overall_risk_score(self, risk_abstractions: List[LegalAbstraction]) -> float:
        """Calculate numerical risk score"""
        if not risk_abstractions:
            return 0.5  # Medium risk by default
        
        risk_scores = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3
        }
        
        scores = [risk_scores.get(abs.risk_level, 0.5) for abs in risk_abstractions]
        return sum(scores) / len(scores)

class RLADLegalSystem:
    """
    Complete RLAD Legal System
    Integrates π_abs and π_sol with RL optimization for legal reasoning
    """
    
    def __init__(self):
        self.abstraction_generator = LegalAbstractionGenerator()
        self.solution_generator = LegalSolutionGenerator()
        self.performance_metrics = defaultdict(list)
        
    async def process_legal_request(self, request: LegalReasoningRequest) -> Dict[str, Any]:
        """
        Process complete legal request using RLAD methodology
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate abstractions (π_abs)
            logger.info(f"Generating legal abstractions for {request.domain.value} query")
            abstractions = await self.abstraction_generator.generate_abstractions(request)
            
            # Step 2: Generate solution conditioned on abstractions (π_sol)
            logger.info(f"Generating legal solution using {len(abstractions.abstractions)} abstractions")
            solution = await self.solution_generator.generate_solution(request, abstractions)
            
            # Step 3: Performance tracking for RL
            total_processing_time = (time.time() - start_time) * 1000
            self._track_performance(request, abstractions, solution, total_processing_time)
            
            # Step 4: Prepare comprehensive response
            response = {
                'status': 'success',
                'legal_analysis': solution.solution_content,
                'abstractions_used': [
                    {
                        'title': abs.title,
                        'type': abs.abstraction_type.value,
                        'domain': abs.domain.value,
                        'confidence': abs.confidence_score,
                        'reusability': abs.reusability_score,
                        'utility': abs.utility_score,
                        'risk_level': abs.risk_level
                    }
                    for abs in solution.used_abstractions
                ],
                'legal_analysis_metadata': solution.legal_analysis,
                'risk_assessment': solution.risk_assessment,
                'recommendations': solution.recommendations,
                'legal_citations': solution.citations,
                'performance_metrics': {
                    'total_processing_time_ms': total_processing_time,
                    'abstraction_generation_time_ms': abstractions.processing_time_ms,
                    'solution_generation_time_ms': solution.processing_metadata['processing_time_ms'],
                    'abstractions_generated': len(abstractions.abstractions),
                    'generation_confidence': abstractions.generation_confidence,
                    'solution_confidence': solution.solution_confidence,
                    'estimated_utility': abstractions.estimated_utility
                },
                'rlad_metadata': {
                    'methodology': 'RLAD Legal Abstraction Discovery',
                    'abstraction_strategy': abstractions.reasoning_strategy,
                    'solution_strategy': solution.processing_metadata['strategy'],
                    'domain': request.domain.value,
                    'jurisdiction': request.jurisdiction,
                    'complexity': request.complexity_level
                }
            }
            
            logger.info(f"RLAD legal processing completed in {total_processing_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error in RLAD legal processing: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'fallback_analysis': 'Error en el procesamiento con abstracciones. Se requiere análisis manual.'
            }
    
    def _track_performance(self, 
                           request: LegalReasoningRequest,
                           abstractions: LegalAbstractionGeneration,
                           solution: LegalSolutionWithAbstractions,
                           total_time: float):
        """Track performance metrics for RL optimization"""
        
        performance_entry = {
            'timestamp': datetime.now().isoformat(),
            'domain': request.domain.value,
            'complexity': request.complexity_level,
            'abstractions_count': len(abstractions.abstractions),
            'generation_confidence': abstractions.generation_confidence,
            'solution_confidence': solution.solution_confidence,
            'estimated_utility': abstractions.estimated_utility,
            'total_processing_time_ms': total_time,
            'abstraction_time_ms': abstractions.processing_time_ms,
            'solution_time_ms': solution.processing_metadata['processing_time_ms'],
            'risks_identified': solution.risk_assessment['total_risks_identified'],
            'high_risks': solution.risk_assessment['high_risk_count'],
            'recommendations_count': len(solution.recommendations)
        }
        
        # Store for future RL training
        self.performance_metrics[request.domain.value].append(performance_entry)
        
        # Keep only recent entries (for memory efficiency)
        if len(self.performance_metrics[request.domain.value]) > 100:
            self.performance_metrics[request.domain.value] = self.performance_metrics[request.domain.value][-100:]
    
    def get_performance_summary(self, domain: Optional[LegalDomain] = None) -> Dict[str, Any]:
        """Get performance summary for RL analysis"""
        
        if domain:
            metrics = self.performance_metrics[domain.value]
        else:
            all_metrics = []
            for domain_metrics in self.performance_metrics.values():
                all_metrics.extend(domain_metrics)
            metrics = all_metrics
        
        if not metrics:
            return {'status': 'no_data'}
        
        # Calculate aggregate statistics
        avg_confidence = np.mean([m['solution_confidence'] for m in metrics])
        avg_utility = np.mean([m['estimated_utility'] for m in metrics])
        avg_processing_time = np.mean([m['total_processing_time_ms'] for m in metrics])
        total_risks_identified = sum([m['risks_identified'] for m in metrics])
        
        return {
            'total_requests': len(metrics),
            'avg_solution_confidence': avg_confidence,
            'avg_estimated_utility': avg_utility,
            'avg_processing_time_ms': avg_processing_time,
            'total_risks_identified': total_risks_identified,
            'domains_analyzed': len(set(m['domain'] for m in metrics)),
            'performance_trend': self._calculate_performance_trend(metrics)
        }
    
    def _calculate_performance_trend(self, metrics: List[Dict]) -> str:
        """Calculate performance trend for RL feedback"""
        if len(metrics) < 5:
            return 'insufficient_data'
        
        recent_metrics = metrics[-5:]
        older_metrics = metrics[-10:-5] if len(metrics) >= 10 else metrics[:-5]
        
        recent_avg_confidence = np.mean([m['solution_confidence'] for m in recent_metrics])
        older_avg_confidence = np.mean([m['solution_confidence'] for m in older_metrics]) if older_metrics else recent_avg_confidence
        
        if recent_avg_confidence > older_avg_confidence + 0.05:
            return 'improving'
        elif recent_avg_confidence < older_avg_confidence - 0.05:
            return 'declining'
        else:
            return 'stable'

# Global RLAD system instance
_global_rlad_system = None

def get_rlad_legal_system() -> RLADLegalSystem:
    """Get or create the global RLAD legal system instance"""
    global _global_rlad_system
    if _global_rlad_system is None:
        _global_rlad_system = RLADLegalSystem()
    return _global_rlad_system

# Convenience functions for external use
async def process_legal_request_with_rlad(
    document: str,
    query: str,
    domain: str = "contract_law",
    jurisdiction: str = "AR",
    complexity: str = "medium"
) -> Dict[str, Any]:
    """
    Convenience function to process legal request with RLAD
    """
    
    # Convert string domain to enum
    domain_enum = LegalDomain(domain.lower())
    
    request = LegalReasoningRequest(
        document_content=document,
        legal_query=query,
        domain=domain_enum,
        jurisdiction=jurisdiction,
        complexity_level=complexity,
        confidentiality_level="highly_confidential",
        use_abstractions=True,
        max_abstractions=5
    )
    
    rlad_system = get_rlad_legal_system()
    return await rlad_system.process_legal_request(request)

if __name__ == "__main__":
    # Example usage and testing
    async def test_rlad_legal():
        """Test the RLAD legal system"""
        
        sample_contract = """
        CONTRATO DE SERVICIOS PROFESIONALES
        
        Entre EMPRESA ABC S.A. y CONSULTOR LEGAL, se acuerda:
        
        1. OBJETO: Prestación de servicios de asesoramiento legal corporativo
        2. HONORARIOS: USD 10,000 mensuales
        3. INDEMNIZACIÓN: El Consultor indemnizará a la Empresa por todos los daños
        4. CONFIDENCIALIDAD: Información confidencial por tiempo indefinido
        5. TERMINACIÓN: Cualquier parte puede terminar sin causa con 30 días de aviso
        """
        
        sample_query = "Analizar riesgos contractuales y problemas de indemnización"
        
        print("🚀 Testing RLAD Legal Abstraction Discovery System")
        print("=" * 60)
        
        result = await process_legal_request_with_rlad(
            document=sample_contract,
            query=sample_query,
            domain="contract_law",
            jurisdiction="AR",
            complexity="medium"
        )
        
        print("📊 RLAD Legal Analysis Results:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Test performance summary
        rlad_system = get_rlad_legal_system()
        performance = rlad_system.get_performance_summary()
        
        print("\\n📈 Performance Summary:")
        print(json.dumps(performance, indent=2, ensure_ascii=False))
    
    # Run the test
    asyncio.run(test_rlad_legal())