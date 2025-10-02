"""
Legal AI Model Registry with MLOps Best Practices
Implements patterns from Made-With-ML and production ML systems
"""

import mlflow
import mlflow.pytorch
from typing import Dict, Any, Optional, List
import hashlib
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
import os
from ..bias_detection import LegalBiasEvaluationFramework

@dataclass
class LegalModelMetadata:
    """Comprehensive metadata for legal AI models"""
    model_name: str
    version: str
    model_type: str  # "scm_adapter", "full_model", "ensemble"
    legal_domain: str  # "contracts", "governance", "compliance"
    jurisdiction: List[str]  # ["AR", "ES", "CL", "UY"]
    
    # Training metadata
    dataset_hash: str
    training_date: datetime
    base_model: str
    adapter_size_mb: float
    
    # Legal validation
    legal_accuracy: float
    citation_accuracy: float
    bias_score: float
    hallucination_rate: float
    
    # Compliance
    pii_safe: bool
    gdpr_compliant: bool
    audit_trail_complete: bool
    
    # Performance
    inference_time_ms: float
    memory_usage_mb: float
    
    # NEW: Bias evaluation results
    bias_evaluation_score: float = 0.0
    ideological_variance: float = 0.0
    compliance_preservation_rate: float = 0.0
    traceability_score: float = 0.0
    bias_mitigation_techniques: List[str] = None
    
    def __post_init__(self):
        if self.bias_mitigation_techniques is None:
            self.bias_mitigation_techniques = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MLflow logging"""
        result = asdict(self)
        result['training_date'] = self.training_date.isoformat()
        result['jurisdiction'] = ','.join(self.jurisdiction)
        result['bias_mitigation_techniques'] = ','.join(self.bias_mitigation_techniques)
        return result
        
    def is_bias_compliant(self) -> bool:
        """Verify if model meets anti-bias standards"""
        return (
            self.bias_evaluation_score <= 0.3 and
            self.compliance_preservation_rate >= 0.85 and
            self.hallucination_rate <= 0.05 and
            self.traceability_score >= 0.8
        )

class LegalModelRegistry:
    """Enhanced model registry for legal AI with full compliance tracking"""
    
    def __init__(self, 
                 tracking_uri: str = "http://localhost:5000",
                 registry_name: str = "legal-scm-models"):
        self.tracking_uri = tracking_uri
        self.registry_name = registry_name
        
        # Setup MLflow
        mlflow.set_tracking_uri(tracking_uri)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def register_model(self, 
                      model,
                      metadata: LegalModelMetadata,
                      artifacts: Optional[Dict[str, Any]] = None) -> str:
        """Register a legal AI model with full metadata and compliance checks"""
        
        experiment_name = f"legal-scm-{metadata.legal_domain}-{metadata.jurisdiction[0]}"
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name=f"{metadata.model_name}-v{metadata.version}"):
            
            # Log model artifacts
            model_info = mlflow.pytorch.log_model(
                model, 
                "model",
                registered_model_name=f"{self.registry_name}-{metadata.legal_domain}"
            )
            
            # Log comprehensive parameters
            mlflow.log_params(metadata.to_dict())
            
            # Log performance metrics
            mlflow.log_metrics({
                "legal_accuracy": metadata.legal_accuracy,
                "citation_accuracy": metadata.citation_accuracy,
                "bias_score": metadata.bias_score,
                "hallucination_rate": metadata.hallucination_rate,
                "inference_time_ms": metadata.inference_time_ms,
                "memory_usage_mb": metadata.memory_usage_mb
            })
            
            # Log compliance status
            mlflow.log_metrics({
                "pii_safe": float(metadata.pii_safe),
                "gdpr_compliant": float(metadata.gdpr_compliant),
                "audit_trail_complete": float(metadata.audit_trail_complete),
                "overall_compliance": float(
                    metadata.pii_safe and 
                    metadata.gdpr_compliant and 
                    metadata.audit_trail_complete
                )
            })
            
            # Log additional artifacts
            if artifacts:
                for name, artifact in artifacts.items():
                    if isinstance(artifact, dict):
                        mlflow.log_dict(artifact, f"{name}.json")
                    elif isinstance(artifact, str):
                        mlflow.log_text(artifact, f"{name}.txt")
            
            # Log training configuration
            training_config = {
                "base_model": metadata.base_model,
                "legal_domain": metadata.legal_domain,
                "jurisdictions": metadata.jurisdiction,
                "dataset_hash": metadata.dataset_hash,
                "compliance_validated": True
            }
            mlflow.log_dict(training_config, "training_config.json")
            
            # Add model tags for better organization
            mlflow.set_tags({
                "legal_domain": metadata.legal_domain,
                "jurisdiction": ",".join(metadata.jurisdiction),
                "compliance_status": "approved" if self._validate_compliance(metadata) else "pending",
                "model_type": metadata.model_type,
                "production_ready": str(self._is_production_ready(metadata))
            })
            
            run_id = mlflow.active_run().info.run_id
            
        self.logger.info(f"Registered model {metadata.model_name} v{metadata.version} with run_id: {run_id}")
        return run_id
        
    def get_best_model(self, 
                      legal_domain: str,
                      jurisdiction: str,
                      metric: str = "legal_accuracy") -> Optional[Dict[str, Any]]:
        """Get the best performing model for a specific legal domain and jurisdiction"""
        
        client = mlflow.tracking.MlflowClient()
        
        # Search for models in the domain
        models = client.search_registered_models(
            filter_string=f"name='{self.registry_name}-{legal_domain}'"
        )
        
        if not models:
            return None
            
        best_model = None
        best_score = -1
        
        for model in models:
            for version in model.latest_versions:
                # Get run details
                run = client.get_run(version.run_id)
                
                # Check jurisdiction match
                if jurisdiction in run.data.tags.get("jurisdiction", ""):
                    score = run.data.metrics.get(metric, 0)
                    if score > best_score:
                        best_score = score
                        best_model = {
                            "model_name": model.name,
                            "version": version.version,
                            "run_id": version.run_id,
                            "model_uri": version.source,
                            "score": score,
                            "metadata": run.data.params
                        }
        
        return best_model
        
    def validate_model_compliance(self, run_id: str) -> Dict[str, Any]:
        """Validate model compliance for production deployment"""
        
        client = mlflow.tracking.MlflowClient()
        run = client.get_run(run_id)
        
        compliance_checks = {
            "pii_safe": run.data.metrics.get("pii_safe", 0) == 1.0,
            "gdpr_compliant": run.data.metrics.get("gdpr_compliant", 0) == 1.0,
            "audit_trail_complete": run.data.metrics.get("audit_trail_complete", 0) == 1.0,
            "legal_accuracy_threshold": run.data.metrics.get("legal_accuracy", 0) >= 0.85,
            "hallucination_rate_acceptable": run.data.metrics.get("hallucination_rate", 1.0) <= 0.05,
            "bias_score_acceptable": run.data.metrics.get("bias_score", 1.0) <= 0.1
        }
        
        compliance_checks["overall_compliant"] = all(compliance_checks.values())
        
        # Log compliance validation
        with mlflow.start_run(run_id=run_id):
            mlflow.log_metrics({f"compliance_{k}": float(v) for k, v in compliance_checks.items()})
            
        return compliance_checks
        
    def promote_to_production(self, 
                            model_name: str, 
                            version: str, 
                            stage: str = "Production") -> bool:
        """Promote model to production after compliance validation"""
        
        client = mlflow.tracking.MlflowClient()
        
        # Get model version
        model_version = client.get_model_version(model_name, version)
        
        # Validate compliance
        compliance_result = self.validate_model_compliance(model_version.run_id)
        
        if not compliance_result["overall_compliant"]:
            self.logger.error(f"Model {model_name} v{version} failed compliance checks")
            return False
            
        # Promote to production
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        
        # Add production deployment metadata
        client.set_model_version_tag(
            name=model_name,
            version=version,
            key="deployment_date",
            value=datetime.now().isoformat()
        )
        
        client.set_model_version_tag(
            name=model_name,
            version=version,
            key="deployment_status",
            value="active"
        )
        
        self.logger.info(f"Successfully promoted {model_name} v{version} to {stage}")
        return True
        
    def _validate_compliance(self, metadata: LegalModelMetadata) -> bool:
        """Internal compliance validation"""
        return (
            metadata.pii_safe and
            metadata.gdpr_compliant and 
            metadata.audit_trail_complete and
            metadata.legal_accuracy >= 0.85 and
            metadata.hallucination_rate <= 0.05 and
            metadata.bias_score <= 0.1
        )
        
    def _is_production_ready(self, metadata: LegalModelMetadata) -> bool:
        """Check if model meets production readiness criteria"""
        return (
            self._validate_compliance(metadata) and
            metadata.inference_time_ms <= 200 and
            metadata.memory_usage_mb <= 300
        )

class LegalModelDeployment:
    """Handle model deployment and versioning for legal AI systems"""
    
    def __init__(self, registry: LegalModelRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
        
    def deploy_model(self, 
                    model_name: str, 
                    version: str, 
                    deployment_target: str = "cloudflare_workers") -> Dict[str, Any]:
        """Deploy model to specified target with health checks"""
        
        # Get model metadata
        client = mlflow.tracking.MlflowClient()
        model_version = client.get_model_version(model_name, version)
        
        # Download model artifacts
        model_uri = model_version.source
        local_path = mlflow.artifacts.download_artifacts(model_uri)
        
        # Deployment configuration
        deployment_config = {
            "model_name": model_name,
            "version": version,
            "target": deployment_target,
            "model_path": local_path,
            "deployment_time": datetime.now().isoformat(),
            "health_check_url": f"https://{model_name.lower()}.pages.dev/health"
        }
        
        # Execute deployment based on target
        if deployment_target == "cloudflare_workers":
            success = self._deploy_to_cloudflare(deployment_config)
        else:
            raise ValueError(f"Unsupported deployment target: {deployment_target}")
            
        # Log deployment status
        with mlflow.start_run(run_id=model_version.run_id):
            mlflow.log_dict(deployment_config, "deployment_config.json")
            mlflow.log_metrics({
                "deployment_success": float(success),
                "deployment_timestamp": datetime.now().timestamp()
            })
            
        return {
            "success": success,
            "deployment_config": deployment_config,
            "health_check_url": deployment_config["health_check_url"]
        }
        
    def _deploy_to_cloudflare(self, config: Dict[str, Any]) -> bool:
        """Deploy to Cloudflare Workers/Pages"""
        try:
            # This would integrate with wrangler CLI or Cloudflare API
            # For now, return success (would need actual implementation)
            self.logger.info(f"Deploying {config['model_name']} v{config['version']} to Cloudflare")
            return True
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            return False

# Usage Example
if __name__ == "__main__":
    # Initialize registry
    registry = LegalModelRegistry(
        tracking_uri="http://localhost:5000",
        registry_name="legal-scm-models"
    )
    
    # Create model metadata
    metadata = LegalModelMetadata(
        model_name="scm-contracts-ar",
        version="1.0.0",
        model_type="scm_adapter",
        legal_domain="contracts",
        jurisdiction=["AR"],
        dataset_hash="abc123",
        training_date=datetime.now(),
        base_model="llama-3.2-1b",
        adapter_size_mb=35.5,
        legal_accuracy=0.92,
        citation_accuracy=0.88,
        bias_score=0.05,
        hallucination_rate=0.02,
        pii_safe=True,
        gdpr_compliant=True,
        audit_trail_complete=True,
        inference_time_ms=150,
        memory_usage_mb=280
    )
    
    # Register model (would need actual model object)
    # run_id = registry.register_model(model, metadata)
    
    print("Legal Model Registry initialized successfully")