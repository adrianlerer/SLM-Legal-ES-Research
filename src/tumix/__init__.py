"""
TUMIX Legal Multi-Agent System
=============================

Implementación de arquitectura TUMIX adaptada para razonamiento jurídico profesional.
Basado en Paper: TUMIX (Tool-Use Mixture) - arXiv:2510.01279

CONFIDENCIAL - Propiedad Intelectual Exclusiva
Desarrollado por: Ignacio Adrián Lerer (Abogado UBA, Executive MBA Universidad Austral)

Características:
- Multi-agentes heterogéneos especializados en derecho
- Early stopping con consenso ponderado
- Verificación automática de citas legales
- Trazabilidad completa para auditabilidad regulatoria
- Integración de 30+ años de experiencia jurídica
"""

__version__ = "1.0.0-tumix"
__author__ = "Ignacio Adrián Lerer"

from .legal_multi_agent_system import (
    # Clases principales
    LegalMultiAgentOrchestrator,
    LegalQuery,
    AgentOutput,
    LegalCitation,
    
    # Tipos de agentes
    AgentType,
    CoTJuridicoAgent,
    SearchJurisprudencialAgent, 
    CodeComplianceAgent,
    
    # Función principal
    process_legal_query_tumix
)

__all__ = [
    'LegalMultiAgentOrchestrator',
    'LegalQuery',
    'AgentOutput',
    'LegalCitation',
    'AgentType',
    'CoTJuridicoAgent',
    'SearchJurisprudencialAgent',
    'CodeComplianceAgent',
    'process_legal_query_tumix'
]