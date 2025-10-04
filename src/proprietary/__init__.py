"""
Sistema Propietario SLM-Legal-Spanish
===================================

Módulos propietarios con experiencia profesional de 30+ años integrada.

CONFIDENCIAL - Propiedad Intelectual Exclusiva
Desarrollado por: Ignacio Adrián Lerer (Abogado UBA, Executive MBA Universidad Austral)
"""

__version__ = "2.0.0-enterprise"
__author__ = "Ignacio Adrián Lerer"
__copyright__ = "© 2025 SLM-Legal-Spanish. All rights reserved."

from .advanced_legal_reasoning import ProprietaryLegalReasoning
from .advanced_training_pipeline import ProprietaryTrainer, initialize_proprietary_training
from .enterprise_deployment import EnterpriseDeploymentOrchestrator
from .monetization_licensing import ProprietaryLicenseManager, ProprietaryPricingEngine
from .continuous_evaluation_system import ProfessionalEvaluationEngine, ContinuousImprovementOrchestrator

__all__ = [
    'ProprietaryLegalReasoning',
    'ProprietaryTrainer', 
    'initialize_proprietary_training',
    'EnterpriseDeploymentOrchestrator',
    'ProprietaryLicenseManager',
    'ProprietaryPricingEngine', 
    'ProfessionalEvaluationEngine',
    'ContinuousImprovementOrchestrator'
]