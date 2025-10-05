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

# Importar solo módulos existentes
from .document_processor import PrivateDocumentProcessor, initialize_document_processor
from .private_training_plan import PrivateCollectionTrainer, create_private_training_plan

try:
    from .advanced_training_pipeline import ProprietaryTrainer, initialize_proprietary_training
except ImportError:
    ProprietaryTrainer = None
    initialize_proprietary_training = None

__all__ = [
    'PrivateDocumentProcessor',
    'initialize_document_processor', 
    'PrivateCollectionTrainer',
    'create_private_training_plan'
]

# Agregar módulos opcionales si están disponibles
if ProprietaryTrainer is not None:
    __all__.extend(['ProprietaryTrainer', 'initialize_proprietary_training'])