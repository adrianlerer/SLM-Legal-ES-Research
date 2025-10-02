"""
MLOps module for Legal SCM system
Implements world-class ML engineering patterns for legal AI
"""

from .model_registry import LegalModelRegistry, LegalModelMetadata, LegalModelDeployment

__all__ = [
    'LegalModelRegistry',
    'LegalModelMetadata', 
    'LegalModelDeployment'
]