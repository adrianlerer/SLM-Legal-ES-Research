"""
BitNet Integration Module for TUMIX Enhanced Legal Multi-Agent System

This module provides BitNet 1.58-bit quantized inference capabilities for ultra-efficient
local processing with maximum confidentiality and 80% cost reduction.

Key Components:
- BitNetAPIWrapper: Main interface for BitNet integration
- BitNetInferenceEngine: Core inference processing
- BitNetModelManager: Model lifecycle management
- HybridInferenceManager: Intelligent routing between local and cloud

Author: Ignacio Adrian Lerer - Senior Corporate Legal Consultant
License: Proprietary - Confidential Legal Technology System
Version: 1.0.0-bitnet-integration
"""

from .bitnet_integration_wrapper import (
    BitNetAPIWrapper,
    BitNetInferenceEngine,
    BitNetModelManager,
    BitNetRequest,
    BitNetResponse,
    BitNetMetrics,
    get_bitnet_wrapper,
    shutdown_bitnet_wrapper
)

from .hybrid_inference_manager import (
    HybridInferenceManager,
    InferenceRequest,
    InferenceResponse,
    ConfidentialityLevel,
    Priority,
    InferenceBackend,
    get_hybrid_manager,
    shutdown_hybrid_manager
)

from .bitnet_consensus_integration import (
    BitNetConsensusEngine,
    BitNetConsensusRequest,
    BitNetConsensusResponse,
    BitNetAgentConfig,
    get_bitnet_consensus_engine,
    shutdown_bitnet_consensus_engine
)

from .legal_moe_router import (
    LegalMoERouter,
    LegalExpertRegistry,
    LegalDomainClassifier,
    LegalExpertProfile,
    LegalDomain,
    ExpertCapability,
    DomainClassificationResult,
    MoERoutingDecision,
    MoEResponse,
    get_legal_moe_router,
    shutdown_legal_moe_router
)

from .coda_legal_integration import (
    CoDALegalIntegration,
    CoDARequest,
    CoDAResponse,
    CoDATaskType,
    CoDAComplexity,
    get_coda_integration
)

__version__ = "1.0.0-bitnet-integration"
__author__ = "Ignacio Adrian Lerer"
__license__ = "Proprietary"

__all__ = [
    "BitNetAPIWrapper",
    "BitNetInferenceEngine", 
    "BitNetModelManager",
    "BitNetRequest",
    "BitNetResponse",
    "BitNetMetrics",
    "get_bitnet_wrapper",
    "shutdown_bitnet_wrapper",
    "HybridInferenceManager",
    "InferenceRequest",
    "InferenceResponse",
    "ConfidentialityLevel",
    "Priority", 
    "InferenceBackend",
    "get_hybrid_manager",
    "shutdown_hybrid_manager",
    "BitNetConsensusEngine",
    "BitNetConsensusRequest",
    "BitNetConsensusResponse",
    "BitNetAgentConfig",
    "get_bitnet_consensus_engine",
    "shutdown_bitnet_consensus_engine",
    "LegalMoERouter",
    "LegalExpertRegistry",
    "LegalDomainClassifier",
    "LegalExpertProfile",
    "LegalDomain",
    "ExpertCapability",
    "DomainClassificationResult",
    "MoERoutingDecision",
    "MoEResponse",
    "get_legal_moe_router",
    "shutdown_legal_moe_router",
    "CoDALegalIntegration",
    "CoDARequest",
    "CoDAResponse",
    "CoDATaskType",
    "CoDAComplexity",
    "get_coda_integration"
]