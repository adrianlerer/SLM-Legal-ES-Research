"""
TUMIX Legal Multi-Agent System ENHANCED 2025
============================================

Sistema de múltiples agentes especializados para análisis jurídico profesional.
Integra algoritmos de IA de vanguardia: Gradient Boosting, PCA, K-Means, XGBoost.

NUEVAS CAPACIDADES 2025:
- Enhanced Consensus Engine: Consenso matemáticamente optimizado
- Legal Dimensionality Analyzer: Clasificación automática de casos  
- Optimización inteligente de recursos y asignación de agentes

Basado en Paper: TUMIX (Tool-Use Mixture) - arXiv:2510.01279
Integra: Top 20 Algoritmos de IA 2025 para dominio jurídico profesional

CONFIDENCIAL - Propiedad Intelectual Exclusiva
Desarrollado por: Ignacio Adrián Lerer (Abogado UBA, Executive MBA Universidad Austral)

Características ORIGINALES:
- Multi-agentes heterogéneos especializados en derecho
- Early stopping con consenso ponderado
- Verificación automática de citas legales
- Trazabilidad completa para auditabilidad regulatoria
- Integración de 30+ años de experiencia jurídica

CARACTERÍSTICAS NUEVAS 2025:
- Consenso Gradient Boosting + Random Forest + XGBoost
- Análisis dimensional PCA para clasificación automática
- K-Means clustering para optimización de recursos
- Métricas matemáticas de auditabilidad regulatoria
- Auto-optimización de estrategias por agente
"""

__version__ = "2.0.0-enhanced-2025"
__author__ = "Ignacio Adrián Lerer"

from .legal_multi_agent_system import (
    # Clases principales mejoradas
    LegalMultiAgentOrchestrator,
    LegalQuery,
    AgentOutput,
    LegalCitation,
    
    # Tipos de agentes
    AgentType,
    CoTJuridicoAgent,
    SearchJurisprudencialAgent, 
    CodeComplianceAgent,
    
    # Función principal mejorada
    process_legal_query_tumix,
    
    # Flag de engines mejorados
    ENHANCED_ENGINES_AVAILABLE
)

# Importar engines mejorados si están disponibles
try:
    from .enhanced_consensus_engine import (
        EnhancedConsensusEngine,
        ConsensusResult,
        ConsensusFeatures,
        create_enhanced_consensus_engine,
        calculate_consensus_improvement_metrics
    )
    from .legal_dimensionality_analyzer import (
        LegalDimensionalityAnalyzer,
        LegalDimensionAnalysis,
        LegalVectorization,
        create_legal_dimensionality_analyzer,
        calculate_dimensionality_improvement_metrics
    )
    
    # Exports completos con engines mejorados
    __all__ = [
        # Core TUMIX
        'LegalMultiAgentOrchestrator',
        'LegalQuery',
        'AgentOutput',
        'LegalCitation',
        'AgentType',
        'CoTJuridicoAgent',
        'SearchJurisprudencialAgent',
        'CodeComplianceAgent',
        'process_legal_query_tumix',
        'ENHANCED_ENGINES_AVAILABLE',
        
        # Enhanced Engines 2025
        'EnhancedConsensusEngine',
        'ConsensusResult',
        'ConsensusFeatures',
        'create_enhanced_consensus_engine',
        'calculate_consensus_improvement_metrics',
        'LegalDimensionalityAnalyzer',
        'LegalDimensionAnalysis',
        'LegalVectorization',
        'create_legal_dimensionality_analyzer',
        'calculate_dimensionality_improvement_metrics'
    ]
    
    print("✅ TUMIX Enhanced 2025: Todos los engines mejorados cargados correctamente")
    
except ImportError as e:
    # Fallback sin engines mejorados
    print(f"⚠️ TUMIX Enhanced 2025: Engines mejorados no disponibles: {e}")
    
    __all__ = [
        'LegalMultiAgentOrchestrator',
        'LegalQuery',
        'AgentOutput',
        'LegalCitation',
        'AgentType',
        'CoTJuridicoAgent',
        'SearchJurisprudencialAgent',
        'CodeComplianceAgent',
        'process_legal_query_tumix',
        'ENHANCED_ENGINES_AVAILABLE'
    ]

# Información del sistema para debugging
def get_system_info():
    """Retorna información del sistema TUMIX Enhanced."""
    return {
        "version": __version__,
        "enhanced_engines_available": ENHANCED_ENGINES_AVAILABLE,
        "author": __author__,
        "capabilities": [
            "Multi-Agent Legal Analysis",
            "Gradient Boosting Consensus",
            "PCA Legal Dimensionality",
            "K-Means Case Clustering", 
            "XGBoost Regulatory Audit",
            "Mathematical Consensus Proof",
            "Automatic Agent Optimization"
        ] if ENHANCED_ENGINES_AVAILABLE else [
            "Multi-Agent Legal Analysis",
            "Basic Consensus",
            "Manual Agent Selection"
        ]
    }