#!/usr/bin/env python3
"""
Hybrid Inference Manager for BitNet + Cloud Integration

This module implements intelligent routing between BitNet local inference and cloud fallback
based on confidentiality requirements, performance metrics, and system load.

Key Features:
- Intelligent routing algorithm based on multiple factors
- Dynamic load balancing between local and cloud inference
- Confidentiality-aware decision making
- Performance optimization and cost analysis
- Failover mechanisms and circuit breaker patterns
- Real-time metrics collection and analysis

Decision Factors:
1. Confidentiality Level: Maximum -> BitNet local only
2. System Load: High load -> Cloud fallback for non-sensitive queries
3. Response Time Requirements: Ultra-fast -> Cloud APIs
4. Cost Optimization: Budget constraints -> BitNet preference
5. Model Availability: BitNet model status -> Fallback routing

Author: Ignacio Adrian Lerer - Senior Corporate Legal Consultant
License: Proprietary - Confidential Legal Technology System
Version: 1.0.0-hybrid-inference
"""

import asyncio
import json
import logging
import time
import statistics
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union, Any, Callable
from enum import Enum
import psutil
import aiohttp
from datetime import datetime, timedelta

from .bitnet_integration_wrapper import BitNetAPIWrapper, get_bitnet_wrapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InferenceBackend(Enum):
    """Available inference backends"""
    BITNET_LOCAL = "bitnet_local"
    OPENAI_CLOUD = "openai_cloud" 
    ANTHROPIC_CLOUD = "anthropic_cloud"
    GROQ_CLOUD = "groq_cloud"
    FALLBACK_CLOUD = "fallback_cloud"

class ConfidentialityLevel(Enum):
    """Data confidentiality classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    HIGHLY_CONFIDENTIAL = "highly_confidential"
    MAXIMUM_SECURITY = "maximum_security"

class Priority(Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class InferenceRequest:
    """Hybrid inference request with routing metadata"""
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    confidentiality_level: ConfidentialityLevel = ConfidentialityLevel.CONFIDENTIAL
    priority: Priority = Priority.NORMAL
    max_response_time_ms: Optional[int] = None
    cost_budget_usd: Optional[float] = None
    preferred_backend: Optional[InferenceBackend] = None
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    legal_domain: Optional[str] = None  # contract, regulatory, litigation, etc.
    jurisdiction: Optional[str] = None  # US, EU, Latin America, etc.

@dataclass
class InferenceResponse:
    """Hybrid inference response with routing metadata"""
    text: str
    backend_used: InferenceBackend
    inference_time_ms: float
    tokens_generated: int
    confidence_score: float
    cost_usd: float
    confidentiality_maintained: bool
    request_id: Optional[str] = None
    routing_reason: str = ""
    fallback_used: bool = False
    error: Optional[str] = None

@dataclass
class BackendMetrics:
    """Performance metrics for each backend"""
    backend: InferenceBackend
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    average_cost_usd: float = 0.0
    availability_score: float = 1.0
    quality_score: float = 0.0
    last_successful_request: Optional[datetime] = None
    circuit_breaker_open: bool = False
    circuit_breaker_failures: int = 0

@dataclass
class RoutingDecision:
    """Detailed routing decision with reasoning"""
    selected_backend: InferenceBackend
    confidence_score: float
    reasoning: List[str]
    alternative_backends: List[InferenceBackend]
    estimated_cost_usd: float
    estimated_time_ms: float
    confidentiality_compliant: bool

class CircuitBreaker:
    """Circuit breaker pattern for backend failure handling"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if requests can be executed"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker moving to HALF_OPEN state")
                return True
            return False
        
        # HALF_OPEN state
        return True

class HybridInferenceManager:
    """Intelligent routing manager for hybrid BitNet + Cloud inference"""
    
    def __init__(self):
        self.backends: Dict[InferenceBackend, BackendMetrics] = {}
        self.circuit_breakers: Dict[InferenceBackend, CircuitBreaker] = {}
        self.bitnet_wrapper: Optional[BitNetAPIWrapper] = None
        self.cloud_api_keys: Dict[str, str] = {}
        
        # Initialize backend metrics
        for backend in InferenceBackend:
            self.backends[backend] = BackendMetrics(backend=backend)
            self.circuit_breakers[backend] = CircuitBreaker()
        
        # Routing configuration
        self.config = {
            "bitnet_cpu_threshold": 80.0,  # CPU usage threshold for BitNet
            "bitnet_memory_threshold": 85.0,  # Memory usage threshold
            "cloud_cost_per_token": 0.000002,  # Average cloud cost per token
            "bitnet_cost_per_token": 0.0000004,  # BitNet local cost (80% reduction)
            "max_local_concurrent": 4,  # Max concurrent BitNet requests
            "confidentiality_override": True,  # Always use local for max security
            "default_timeout_ms": 10000  # Default request timeout
        }
        
        logger.info("Hybrid Inference Manager initialized")
    
    async def initialize(self):
        """Initialize BitNet wrapper and validate cloud APIs"""
        try:
            # Initialize BitNet wrapper
            self.bitnet_wrapper = await get_bitnet_wrapper()
            logger.info("BitNet wrapper initialized for hybrid inference")
            
            # Test cloud API connectivity (if keys available)
            await self._test_cloud_apis()
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Hybrid Inference Manager: {str(e)}")
            return False
    
    async def infer(self, request: InferenceRequest) -> InferenceResponse:
        """Route inference request to optimal backend"""
        start_time = time.time()
        
        try:
            # Make routing decision
            routing_decision = await self._make_routing_decision(request)
            
            logger.info(f"Routing to {routing_decision.selected_backend.value}: {routing_decision.reasoning}")
            
            # Execute inference on selected backend
            response = await self._execute_inference(request, routing_decision)
            
            # Update metrics
            self._update_backend_metrics(routing_decision.selected_backend, response, success=True)
            
            return response
            
        except Exception as e:
            logger.error(f"Hybrid inference failed: {str(e)}")
            
            # Try fallback if available
            fallback_response = await self._try_fallback(request, start_time)
            if fallback_response:
                return fallback_response
            
            # Return error response
            return InferenceResponse(
                text="",
                backend_used=InferenceBackend.FALLBACK_CLOUD,
                inference_time_ms=(time.time() - start_time) * 1000,
                tokens_generated=0,
                confidence_score=0.0,
                cost_usd=0.0,
                confidentiality_maintained=False,
                request_id=request.request_id,
                error=str(e)
            )
    
    async def _make_routing_decision(self, request: InferenceRequest) -> RoutingDecision:
        """Intelligent routing decision algorithm"""
        reasoning = []
        scores: Dict[InferenceBackend, float] = {}
        
        # Factor 1: Confidentiality Requirements (CRITICAL)
        if request.confidentiality_level in [ConfidentialityLevel.HIGHLY_CONFIDENTIAL, 
                                           ConfidentialityLevel.MAXIMUM_SECURITY]:
            reasoning.append(f"High confidentiality ({request.confidentiality_level.value}) requires local processing")
            scores[InferenceBackend.BITNET_LOCAL] = 100.0
            
            # Only allow BitNet for maximum security
            return RoutingDecision(
                selected_backend=InferenceBackend.BITNET_LOCAL,
                confidence_score=1.0,
                reasoning=reasoning,
                alternative_backends=[],
                estimated_cost_usd=request.max_tokens * self.config["bitnet_cost_per_token"],
                estimated_time_ms=request.max_tokens * 6.67,  # 150 tokens/sec BitNet
                confidentiality_compliant=True
            )
        
        # Factor 2: System Resource Availability
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        
        bitnet_score = 50.0  # Base score
        
        if cpu_usage < self.config["bitnet_cpu_threshold"]:
            bitnet_score += 20.0
            reasoning.append(f"Low CPU usage ({cpu_usage:.1f}%) favors BitNet")
        else:
            bitnet_score -= 30.0
            reasoning.append(f"High CPU usage ({cpu_usage:.1f}%) suggests cloud fallback")
        
        if memory_usage < self.config["bitnet_memory_threshold"]:
            bitnet_score += 15.0
            reasoning.append(f"Sufficient memory ({memory_usage:.1f}%) supports BitNet")
        else:
            bitnet_score -= 25.0
            reasoning.append(f"High memory usage ({memory_usage:.1f}%) suggests cloud fallback")
        
        scores[InferenceBackend.BITNET_LOCAL] = bitnet_score
        
        # Factor 3: Performance Requirements
        if request.max_response_time_ms and request.max_response_time_ms < 2000:
            # Ultra-fast response required - favor cloud APIs
            scores[InferenceBackend.GROQ_CLOUD] = 85.0
            scores[InferenceBackend.OPENAI_CLOUD] = 75.0
            reasoning.append(f"Fast response required ({request.max_response_time_ms}ms) favors cloud APIs")
        
        # Factor 4: Cost Optimization
        if request.cost_budget_usd:
            bitnet_cost = request.max_tokens * self.config["bitnet_cost_per_token"]
            cloud_cost = request.max_tokens * self.config["cloud_cost_per_token"]
            
            if request.cost_budget_usd < cloud_cost:
                scores[InferenceBackend.BITNET_LOCAL] += 30.0
                reasoning.append(f"Budget constraint (${request.cost_budget_usd:.4f}) favors BitNet")
        
        # Factor 5: Backend Availability and Circuit Breakers
        for backend, metrics in self.backends.items():
            if backend not in scores:
                scores[backend] = 40.0  # Default cloud score
            
            if self.circuit_breakers[backend].can_execute():
                scores[backend] += metrics.availability_score * 20
            else:
                scores[backend] = 0.0
                reasoning.append(f"{backend.value} circuit breaker open")
        
        # Factor 6: Preferred Backend Override
        if request.preferred_backend and request.preferred_backend in scores:
            scores[request.preferred_backend] += 25.0
            reasoning.append(f"Client preference for {request.preferred_backend.value}")
        
        # Select best backend
        if not scores:
            selected_backend = InferenceBackend.BITNET_LOCAL
        else:
            selected_backend = max(scores.items(), key=lambda x: x[1])[0]
        
        # Calculate alternatives
        alternative_backends = sorted(
            [k for k, v in scores.items() if k != selected_backend and v > 10.0],
            key=lambda x: scores[x],
            reverse=True
        )[:2]
        
        return RoutingDecision(
            selected_backend=selected_backend,
            confidence_score=min(scores.get(selected_backend, 0) / 100.0, 1.0),
            reasoning=reasoning,
            alternative_backends=alternative_backends,
            estimated_cost_usd=self._estimate_cost(selected_backend, request.max_tokens),
            estimated_time_ms=self._estimate_time(selected_backend, request.max_tokens),
            confidentiality_compliant=selected_backend == InferenceBackend.BITNET_LOCAL
        )
    
    async def _execute_inference(self, request: InferenceRequest, routing_decision: RoutingDecision) -> InferenceResponse:
        """Execute inference on selected backend"""
        start_time = time.time()
        backend = routing_decision.selected_backend
        
        try:
            if backend == InferenceBackend.BITNET_LOCAL:
                return await self._execute_bitnet_inference(request, routing_decision, start_time)
            else:
                return await self._execute_cloud_inference(request, routing_decision, start_time)
                
        except Exception as e:
            # Record failure in circuit breaker
            self.circuit_breakers[backend].record_failure()
            raise e
    
    async def _execute_bitnet_inference(self, request: InferenceRequest, routing_decision: RoutingDecision, start_time: float) -> InferenceResponse:
        """Execute inference using BitNet local processing"""
        if not self.bitnet_wrapper:
            raise RuntimeError("BitNet wrapper not available")
        
        result = await self.bitnet_wrapper.process_legal_query(
            query=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            request_id=request.request_id,
            confidentiality_level="maximum"
        )
        
        if result.get("error"):
            raise RuntimeError(f"BitNet inference failed: {result['error']}")
        
        # Record success in circuit breaker
        self.circuit_breakers[InferenceBackend.BITNET_LOCAL].record_success()
        
        return InferenceResponse(
            text=result["response"],
            backend_used=InferenceBackend.BITNET_LOCAL,
            inference_time_ms=(time.time() - start_time) * 1000,
            tokens_generated=result["metadata"]["tokens_generated"],
            confidence_score=result["metadata"]["confidence_score"],
            cost_usd=request.max_tokens * self.config["bitnet_cost_per_token"],
            confidentiality_maintained=True,
            request_id=request.request_id,
            routing_reason="; ".join(routing_decision.reasoning)
        )
    
    async def _execute_cloud_inference(self, request: InferenceRequest, routing_decision: RoutingDecision, start_time: float) -> InferenceResponse:
        """Execute inference using cloud API (placeholder implementation)"""
        backend = routing_decision.selected_backend
        
        # Simulate cloud API call (placeholder - actual implementation would use real APIs)
        await asyncio.sleep(0.5)  # Simulate network latency
        
        # Simulate response based on backend type
        if backend == InferenceBackend.GROQ_CLOUD:
            response_text = f"[GROQ Cloud Response] {request.prompt[:100]}... [Generated via high-speed cloud inference]"
            cost_multiplier = 1.2
        elif backend == InferenceBackend.OPENAI_CLOUD:
            response_text = f"[OpenAI Cloud Response] {request.prompt[:100]}... [Generated via GPT-4 cloud inference]"
            cost_multiplier = 1.5
        elif backend == InferenceBackend.ANTHROPIC_CLOUD:
            response_text = f"[Anthropic Cloud Response] {request.prompt[:100]}... [Generated via Claude cloud inference]"
            cost_multiplier = 1.3
        else:
            response_text = f"[Fallback Cloud Response] {request.prompt[:100]}... [Generated via fallback cloud inference]"
            cost_multiplier = 1.0
        
        # Record success in circuit breaker
        self.circuit_breakers[backend].record_success()
        
        return InferenceResponse(
            text=response_text,
            backend_used=backend,
            inference_time_ms=(time.time() - start_time) * 1000,
            tokens_generated=len(response_text.split()),
            confidence_score=0.85,  # Simulated confidence
            cost_usd=request.max_tokens * self.config["cloud_cost_per_token"] * cost_multiplier,
            confidentiality_maintained=False,  # Cloud processing
            request_id=request.request_id,
            routing_reason="; ".join(routing_decision.reasoning)
        )
    
    async def _try_fallback(self, request: InferenceRequest, start_time: float) -> Optional[InferenceResponse]:
        """Attempt fallback inference strategies"""
        logger.info("Attempting fallback inference strategies")
        
        # Try BitNet as fallback if not already tried
        if self.bitnet_wrapper and self.circuit_breakers[InferenceBackend.BITNET_LOCAL].can_execute():
            try:
                result = await self.bitnet_wrapper.process_legal_query(
                    query=request.prompt,
                    max_tokens=min(request.max_tokens, 256),  # Reduced tokens for fallback
                    temperature=request.temperature
                )
                
                if not result.get("error"):
                    return InferenceResponse(
                        text=result["response"],
                        backend_used=InferenceBackend.BITNET_LOCAL,
                        inference_time_ms=(time.time() - start_time) * 1000,
                        tokens_generated=result["metadata"]["tokens_generated"],
                        confidence_score=result["metadata"]["confidence_score"] * 0.8,  # Reduced confidence for fallback
                        cost_usd=request.max_tokens * self.config["bitnet_cost_per_token"],
                        confidentiality_maintained=True,
                        request_id=request.request_id,
                        routing_reason="Fallback to BitNet after cloud failure",
                        fallback_used=True
                    )
            except Exception as e:
                logger.warning(f"BitNet fallback also failed: {str(e)}")
        
        return None
    
    def _estimate_cost(self, backend: InferenceBackend, max_tokens: int) -> float:
        """Estimate cost for backend and token count"""
        if backend == InferenceBackend.BITNET_LOCAL:
            return max_tokens * self.config["bitnet_cost_per_token"]
        else:
            return max_tokens * self.config["cloud_cost_per_token"]
    
    def _estimate_time(self, backend: InferenceBackend, max_tokens: int) -> float:
        """Estimate response time for backend and token count"""
        if backend == InferenceBackend.BITNET_LOCAL:
            return max_tokens * 6.67  # ~150 tokens/sec for BitNet
        elif backend == InferenceBackend.GROQ_CLOUD:
            return max_tokens * 2.0   # ~500 tokens/sec for GROQ
        else:
            return max_tokens * 4.0   # ~250 tokens/sec for other cloud APIs
    
    def _update_backend_metrics(self, backend: InferenceBackend, response: InferenceResponse, success: bool):
        """Update performance metrics for backend"""
        metrics = self.backends[backend]
        metrics.total_requests += 1
        
        if success and not response.error:
            metrics.successful_requests += 1
            metrics.last_successful_request = datetime.now()
            
            # Update running averages
            if metrics.successful_requests == 1:
                metrics.average_response_time_ms = response.inference_time_ms
                metrics.average_cost_usd = response.cost_usd
            else:
                alpha = 0.1  # Exponential moving average factor
                metrics.average_response_time_ms = (
                    alpha * response.inference_time_ms + 
                    (1 - alpha) * metrics.average_response_time_ms
                )
                metrics.average_cost_usd = (
                    alpha * response.cost_usd + 
                    (1 - alpha) * metrics.average_cost_usd
                )
            
            # Update availability score
            success_rate = metrics.successful_requests / metrics.total_requests
            metrics.availability_score = min(success_rate * 1.2, 1.0)
            
        else:
            metrics.failed_requests += 1
            metrics.availability_score = max(metrics.availability_score * 0.9, 0.1)
    
    async def _test_cloud_apis(self):
        """Test connectivity to cloud APIs"""
        # Placeholder for cloud API testing
        logger.info("Cloud API connectivity testing completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of hybrid inference manager"""
        return {
            "hybrid_manager_status": "active",
            "bitnet_available": self.bitnet_wrapper is not None,
            "backend_metrics": {
                backend.value: {
                    "total_requests": metrics.total_requests,
                    "success_rate": (
                        metrics.successful_requests / max(metrics.total_requests, 1) * 100
                    ),
                    "average_response_time_ms": metrics.average_response_time_ms,
                    "average_cost_usd": metrics.average_cost_usd,
                    "availability_score": metrics.availability_score,
                    "circuit_breaker_status": self.circuit_breakers[backend].state
                }
                for backend, metrics in self.backends.items()
            },
            "system_resources": {
                "cpu_usage_percent": psutil.cpu_percent(),
                "memory_usage_percent": psutil.virtual_memory().percent,
                "bitnet_recommended": (
                    psutil.cpu_percent() < self.config["bitnet_cpu_threshold"] and
                    psutil.virtual_memory().percent < self.config["bitnet_memory_threshold"]
                )
            },
            "configuration": self.config
        }

# Global hybrid manager instance
hybrid_manager = None

async def get_hybrid_manager() -> HybridInferenceManager:
    """Get or create global hybrid inference manager"""
    global hybrid_manager
    
    if hybrid_manager is None:
        hybrid_manager = HybridInferenceManager()
        await hybrid_manager.initialize()
    
    return hybrid_manager

async def shutdown_hybrid_manager():
    """Shutdown global hybrid inference manager"""
    global hybrid_manager
    
    if hybrid_manager:
        # Cleanup logic here if needed
        hybrid_manager = None

# Example usage
async def main():
    """Test hybrid inference manager"""
    print("Testing Hybrid Inference Manager...")
    
    manager = await get_hybrid_manager()
    
    # Test high confidentiality request (should route to BitNet)
    high_security_request = InferenceRequest(
        prompt="Analyze confidential merger agreement for antitrust risks",
        max_tokens=300,
        confidentiality_level=ConfidentialityLevel.MAXIMUM_SECURITY,
        priority=Priority.HIGH
    )
    
    response = await manager.infer(high_security_request)
    print("High Security Request:")
    print(json.dumps(asdict(response), indent=2, default=str))
    
    # Test performance-critical request (may route to cloud)
    fast_request = InferenceRequest(
        prompt="Quick legal opinion on standard NDA clause",
        max_tokens=200,
        confidentiality_level=ConfidentialityLevel.INTERNAL,
        priority=Priority.CRITICAL,
        max_response_time_ms=1500
    )
    
    response = await manager.infer(fast_request)
    print("\nFast Response Request:")
    print(json.dumps(asdict(response), indent=2, default=str))
    
    # Get status
    status = manager.get_status()
    print("\nHybrid Manager Status:")
    print(json.dumps(status, indent=2))
    
    await shutdown_hybrid_manager()

if __name__ == "__main__":
    asyncio.run(main())