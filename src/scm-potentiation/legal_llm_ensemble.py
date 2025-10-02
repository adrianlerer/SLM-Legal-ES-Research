"""
SCM Legal 2.0 - Multi-LLM Ensemble Architecture
Implementación del Framework Rahul Agarwal para IA Legal
Arquitectura híbrida con múltiples modelos especializados
"""

import asyncio
import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMModelConfig:
    """Configuración para cada modelo LLM en el ensemble"""
    model_name: str
    provider: str  # "local", "groq", "together", "commercial"
    specialization: str
    max_tokens: int = 4096
    temperature: float = 0.1
    confidence_threshold: float = 0.7
    cost_per_token: float = 0.0
    latency_target_ms: int = 1000

@dataclass 
class LegalQuery:
    """Estructura de consulta legal estandarizada"""
    query_text: str
    jurisdiction: str = "argentina"
    legal_domain: str = "general"  # civil, comercial, laboral, etc.
    complexity_level: str = "medium"  # simple, medium, complex
    urgency: str = "normal"  # low, normal, high, emergency
    context_documents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalResponse:
    """Respuesta estructurada del ensemble legal"""
    response_text: str
    confidence_score: float
    model_used: str
    reasoning_chain: List[str]
    citations: List[Dict[str, str]]
    jurisdiction_compliance: bool
    risk_assessment: str  # low, medium, high
    processing_time_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class SCMLegalEnsemble:
    """
    Ensemble de múltiples LLMs especializados para consultas legales
    Basado en framework de Rahul Agarwal con optimizaciones para derecho hispanoamericano
    """
    
    def __init__(self):
        self.models = self._initialize_models()
        self.routing_strategy = "smart_routing"  # round_robin, specialization_based, smart_routing
        self.performance_metrics = {}
        self.active_models = []
        logger.info("SCM Legal Ensemble inicializado con {} modelos".format(len(self.models)))
    
    def _initialize_models(self) -> Dict[str, LLMModelConfig]:
        """Inicializar configuración de modelos del ensemble"""
        return {
            # Modelo principal SCM Legal
            "scm_legal_primary": LLMModelConfig(
                model_name="llama-2-7b-legal-spanish",
                provider="local",
                specialization="derecho_hispanoamericano",
                temperature=0.05,  # Muy conservador para legal
                confidence_threshold=0.8
            ),
            
            # Modelos de razonamiento especializado  
            "reasoning_engine": LLMModelConfig(
                model_name="mistral-7b-instruct",
                provider="groq",
                specialization="razonamiento_logico",
                temperature=0.1,
                latency_target_ms=500
            ),
            
            "multilingual_analyzer": LLMModelConfig(
                model_name="qwen-7b-chat",
                provider="together",
                specialization="analisis_multilingue", 
                temperature=0.15
            ),
            
            "mathematical_reasoning": LLMModelConfig(
                model_name="phi-4",
                provider="local", 
                specialization="calculo_legal_financiero",
                temperature=0.05
            ),
            
            # Modelos comerciales para casos complejos
            "complex_cases_handler": LLMModelConfig(
                model_name="claude-3-haiku",
                provider="commercial",
                specialization="casos_complejos_multijurisdiccionales",
                cost_per_token=0.0003,
                confidence_threshold=0.85
            ),
            
            "comparative_analysis": LLMModelConfig(
                model_name="gemini-pro",
                provider="commercial", 
                specialization="analisis_comparativo_jurisdiccional",
                cost_per_token=0.0002
            )
        }
    
    async def route_query(self, query: LegalQuery) -> str:
        """
        Enrutamiento inteligente de consultas basado en:
        - Dominio legal
        - Complejidad
        - Jurisdicción
        - Urgencia
        - Costos
        """
        
        # Routing simple por dominio (expandir con ML)
        routing_rules = {
            "derecho_civil": ["scm_legal_primary", "reasoning_engine"],
            "derecho_comercial": ["scm_legal_primary", "mathematical_reasoning"],
            "derecho_laboral": ["scm_legal_primary", "multilingual_analyzer"],
            "derecho_internacional": ["complex_cases_handler", "comparative_analysis"],
            "casos_complejos": ["complex_cases_handler", "scm_legal_primary"],
            "urgente": ["reasoning_engine", "scm_legal_primary"]  # Modelos más rápidos
        }
        
        # Selección basada en dominio legal
        domain_models = routing_rules.get(query.legal_domain, ["scm_legal_primary"])
        
        # Factor de urgencia - priorizar modelos locales para urgente
        if query.urgency == "emergency":
            local_models = [m for m in domain_models if self.models[m].provider == "local"]
            if local_models:
                return local_models[0]
        
        # Factor de complejidad - usar modelos comerciales para casos complejos
        if query.complexity_level == "complex":
            commercial_models = [m for m in domain_models if self.models[m].provider == "commercial"]
            if commercial_models:
                return commercial_models[0]
        
        # Default: primer modelo especializado disponible
        return domain_models[0] if domain_models else "scm_legal_primary"
    
    async def process_legal_query(self, query: LegalQuery) -> LegalResponse:
        """
        Procesamiento principal de consulta legal con ensemble routing
        """
        start_time = datetime.now()
        
        try:
            # 1. Enrutamiento inteligente
            selected_model = await self.route_query(query)
            model_config = self.models[selected_model]
            
            logger.info(f"Procesando consulta con modelo: {selected_model}")
            
            # 2. Preparación del contexto legal
            legal_context = await self._prepare_legal_context(query)
            
            # 3. Generación de respuesta (simulado - integrar con LLM real)
            response_data = await self._generate_legal_response(
                query, legal_context, model_config
            )
            
            # 4. Validación y compliance
            validated_response = await self._validate_legal_response(
                response_data, query.jurisdiction
            )
            
            # 5. Métricas y logging
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            await self._update_performance_metrics(selected_model, processing_time)
            
            return LegalResponse(
                response_text=validated_response["text"],
                confidence_score=validated_response["confidence"],
                model_used=selected_model,
                reasoning_chain=validated_response["reasoning"],
                citations=validated_response["citations"],
                jurisdiction_compliance=validated_response["compliant"],
                risk_assessment=validated_response["risk"],
                processing_time_ms=int(processing_time),
                metadata={
                    "model_config": model_config.model_name,
                    "routing_reason": "domain_specialization",
                    "context_size": len(legal_context)
                }
            )
            
        except Exception as e:
            logger.error(f"Error procesando consulta legal: {e}")
            # Fallback a modelo base
            return await self._fallback_response(query, str(e))
    
    async def _prepare_legal_context(self, query: LegalQuery) -> str:
        """
        Preparación del contexto legal específico
        Integrar con vector DB y RAG en implementación real
        """
        context_parts = []
        
        # Contexto jurisdiccional
        jurisdiction_context = f"""
        JURISDICCIÓN: {query.jurisdiction.upper()}
        DOMINIO LEGAL: {query.legal_domain}
        NIVEL DE COMPLEJIDAD: {query.complexity_level}
        """
        context_parts.append(jurisdiction_context)
        
        # Documentos de contexto (simulado)
        if query.context_documents:
            docs_context = "DOCUMENTOS DE REFERENCIA:\n"
            for i, doc in enumerate(query.context_documents[:3]):  # Límite por tokens
                docs_context += f"{i+1}. {doc}\n"
            context_parts.append(docs_context)
        
        # Precedentes relevantes (simulado - conectar con vector DB)
        precedents_context = """
        PRECEDENTES RELEVANTES:
        1. Código Civil y Comercial - Art. 1710-1780 (Responsabilidad Civil)
        2. Jurisprudencia CSJN - Fallos 341:611 (2018)
        3. Ley 24.240 - Defensa del Consumidor
        """
        context_parts.append(precedents_context)
        
        return "\n\n".join(context_parts)
    
    async def _generate_legal_response(self, query: LegalQuery, context: str, config: LLMModelConfig) -> Dict[str, Any]:
        """
        Generación de respuesta legal - Integrar con LLM real
        Por ahora simulamos respuesta basada en parámetros realistas
        """
        
        # Simulación realista de LLM response
        base_confidence = config.confidence_threshold
        
        # Ajuste de confianza basado en complejidad
        confidence_adjustments = {
            "simple": 0.1,
            "medium": 0.0, 
            "complex": -0.15
        }
        
        adjusted_confidence = min(0.95, max(0.45, 
            base_confidence + confidence_adjustments.get(query.complexity_level, 0.0)
        ))
        
        # Respuesta simulada con estructura legal real
        simulated_response = {
            "text": f"""
            ANÁLISIS LEGAL - {query.jurisdiction.upper()}
            
            CONSULTA: {query.query_text}
            
            FUNDAMENTOS LEGALES:
            En base al análisis del marco normativo vigente en {query.jurisdiction}, 
            y considerando la jurisprudencia aplicable en materia de {query.legal_domain},
            se desprende que...
            
            RECOMENDACIÓN:
            Se sugiere evaluar los siguientes aspectos:
            1. Cumplimiento normativo específico
            2. Precedentes jurisdiccionales relevantes  
            3. Riesgos potenciales identificados
            
            ADVERTENCIA LEGAL:
            Esta respuesta constituye una orientación general basada en IA legal.
            Se recomienda consultar con profesional habilitado para casos específicos.
            """.strip(),
            
            "confidence": round(adjusted_confidence, 3),
            
            "reasoning": [
                "Análisis de normativa aplicable",
                "Evaluación de precedentes jurisdiccionales", 
                f"Consideración de factores específicos en {query.legal_domain}",
                "Aplicación de filtros de realidad y limitaciones"
            ],
            
            "citations": [
                {
                    "source": "Código Civil y Comercial de la Nación",
                    "article": "Art. 1710-1780", 
                    "relevance": "alta"
                },
                {
                    "source": "Jurisprudencia CSJN",
                    "reference": "Fallos 341:611 (2018)",
                    "relevance": "media"
                }
            ]
        }
        
        return simulated_response
    
    async def _validate_legal_response(self, response_data: Dict[str, Any], jurisdiction: str) -> Dict[str, Any]:
        """
        Validación de compliance y calidad de respuesta legal
        """
        
        # Validaciones básicas
        compliance_checks = {
            "has_legal_disclaimer": "ADVERTENCIA LEGAL" in response_data["text"],
            "jurisdiction_specific": jurisdiction.lower() in response_data["text"].lower(),
            "has_citations": len(response_data["citations"]) > 0,
            "confidence_realistic": 0.45 <= response_data["confidence"] <= 0.85
        }
        
        compliance_score = sum(compliance_checks.values()) / len(compliance_checks)
        is_compliant = compliance_score >= 0.75
        
        # Risk assessment basado en confianza y compliance
        if response_data["confidence"] < 0.6 or not is_compliant:
            risk_level = "high"
        elif response_data["confidence"] < 0.7:
            risk_level = "medium"  
        else:
            risk_level = "low"
        
        return {
            **response_data,
            "compliant": is_compliant,
            "risk": risk_level,
            "validation_score": round(compliance_score, 3)
        }
    
    async def _update_performance_metrics(self, model_name: str, processing_time_ms: float):
        """Actualización de métricas de rendimiento por modelo"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {
                "total_queries": 0,
                "avg_latency_ms": 0,
                "success_rate": 0,
                "last_updated": datetime.now()
            }
        
        metrics = self.performance_metrics[model_name]
        metrics["total_queries"] += 1
        
        # Media móvil de latencia
        alpha = 0.1  # Factor de suavizado
        metrics["avg_latency_ms"] = (
            alpha * processing_time_ms + 
            (1 - alpha) * metrics["avg_latency_ms"]
        )
        
        metrics["last_updated"] = datetime.now()
    
    async def _fallback_response(self, query: LegalQuery, error_msg: str) -> LegalResponse:
        """Respuesta de fallback en caso de errores"""
        return LegalResponse(
            response_text=f"""
            SISTEMA DE RESPALDO ACTIVADO
            
            La consulta legal no pudo ser procesada completamente debido a limitaciones técnicas.
            
            CONSULTA ORIGINAL: {query.query_text}
            
            RECOMENDACIÓN:
            - Consulte con profesional legal habilitado
            - Revise normativa actualizada manualmente
            - Considere reformular la consulta con mayor especificidad
            
            ERROR TÉCNICO: Procesamiento no completado
            """.strip(),
            confidence_score=0.3,
            model_used="fallback_system",
            reasoning_chain=["Sistema de fallback activado", f"Error: {error_msg}"],
            citations=[],
            jurisdiction_compliance=False,
            risk_assessment="high",
            processing_time_ms=100,
            metadata={"fallback_reason": error_msg}
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Resumen de rendimiento del ensemble"""
        return {
            "active_models": len(self.models),
            "total_queries": sum(m.get("total_queries", 0) for m in self.performance_metrics.values()),
            "avg_latency": sum(m.get("avg_latency_ms", 0) for m in self.performance_metrics.values()) / max(1, len(self.performance_metrics)),
            "models_performance": self.performance_metrics,
            "last_updated": datetime.now().isoformat()
        }

# Función demo para testing
async def demo_scm_legal_ensemble():
    """Demo del ensemble SCM Legal con casos de prueba"""
    
    ensemble = SCMLegalEnsemble()
    
    # Casos de prueba realistas
    test_cases = [
        LegalQuery(
            query_text="¿Cuáles son los requisitos para la constitución de una sociedad anónima en Argentina?",
            jurisdiction="argentina",
            legal_domain="derecho_comercial",
            complexity_level="medium",
            urgency="normal"
        ),
        
        LegalQuery(
            query_text="Análisis de responsabilidad civil en accidente de tránsito con múltiples jurisdicciones",
            jurisdiction="argentina", 
            legal_domain="derecho_civil",
            complexity_level="complex",
            urgency="high"
        ),
        
        LegalQuery(
            query_text="Cálculo de indemnización por despido sin causa en convenio metalúrgico",
            jurisdiction="argentina",
            legal_domain="derecho_laboral", 
            complexity_level="simple",
            urgency="normal"
        )
    ]
    
    print("🚀 SCM Legal Ensemble - Demo de Funcionamiento\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"📋 CASO {i}: {query.legal_domain.upper()}")
        print(f"Consulta: {query.query_text[:80]}...")
        
        try:
            response = await ensemble.process_legal_query(query)
            
            print(f"✅ Modelo usado: {response.model_used}")
            print(f"⭐ Confianza: {response.confidence_score:.1%}")
            print(f"⚡ Tiempo: {response.processing_time_ms}ms")
            print(f"🛡️ Riesgo: {response.risk_assessment}")
            print(f"📖 Respuesta: {response.response_text[:150]}...\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # Resumen de rendimiento
    performance = ensemble.get_performance_summary()
    print("📊 RESUMEN DE RENDIMIENTO:")
    print(f"Modelos activos: {performance['active_models']}")
    print(f"Consultas totales: {performance['total_queries']}")
    print(f"Latencia promedio: {performance['avg_latency']:.0f}ms")

# Ejecutar demo si se llama directamente
if __name__ == "__main__":
    asyncio.run(demo_scm_legal_ensemble())