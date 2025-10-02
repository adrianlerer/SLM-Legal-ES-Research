"""
Bias Detection and Mitigation Module for Legal SCM System
Implements comprehensive anti-bias framework based on 2025 legal AI research
"""

from .ideological_bias import IdeologicalBiasDetector
from .compliance_preservation import CompliancePreservationAnalyzer
from .traceability import LegalTraceabilityEngine
from .bias_evaluation_framework import LegalBiasEvaluationFramework

__all__ = [
    'IdeologicalBiasDetector',
    'CompliancePreservationAnalyzer', 
    'LegalTraceabilityEngine',
    'LegalBiasEvaluationFramework'
]