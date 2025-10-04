"""
Plan de Entrenamiento Privado - SLM-Legal-Spanish
===============================================

Sistema de entrenamiento especializado para la colección documental privada
con máxima confidencialidad y trazabilidad de experiencia profesional.

CONFIDENCIAL - Propiedad Intelectual Exclusiva
Desarrollado por: Ignacio Adrián Lerer (Abogado UBA, Executive MBA Universidad Austral)

Características de Seguridad:
- Anonimización automática de referencias a terceros
- Procesamiento local sin transmisión de datos sensibles
- Trazabilidad de experiencia sin revelación de fuentes
- Categorización por valor estratégico propietario
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from .document_processor import PrivateDocumentProcessor, initialize_document_processor
# Importación opcional para pipeline de entrenamiento
try:
    from .advanced_training_pipeline import ProprietaryTrainingPipeline
except ImportError:
    ProprietaryTrainingPipeline = None


@dataclass 
class PrivateTrainingConfiguration:
    """
    Configuración para entrenamiento con documentos privados.
    """
    # Configuración de experiencia profesional
    total_experience_years: int = 30
    directorial_experience_years: int = 15  # Experiencia como director independiente
    corporate_law_years: int = 25  # Experiencia en derecho corporativo
    multi_jurisdictional: bool = True  # AR, ES, CL, UY
    
    # Categorización de documentos por valor estratégico
    document_value_weights: Dict[str, float] = field(default_factory=lambda: {
        "experiencia_directorial_propia": 5.0,      # Documentos creados como director
        "experiencia_corporativa_senior": 4.5,      # Experiencia ejecutiva senior
        "dictamenes_legales_propios": 4.0,         # Dictámenes legales elaborados
        "compliance_frameworks_desarrollados": 3.8,  # Marcos de compliance diseñados
        "experiencia_multijurisdiccional": 3.5,    # Experiencia internacional
        "normativo_especializado": 2.5,            # Conocimiento normativo específico
        "jurisprudencia_aplicada": 2.0,            # Jurisprudencia práctica
        "documentos_referencia": 1.5               # Material de referencia general
    })
    
    # Configuración de anonimización y seguridad
    anonymization_level: str = "strict"  # strict, moderate, basic
    remove_company_references: bool = True
    remove_specific_dates: bool = False  # Mantener fechas para contexto temporal
    remove_monetary_amounts: bool = True
    preserve_legal_structure: bool = True
    
    # Filtros de calidad
    min_document_length: int = 500      # Mínimo 500 caracteres
    min_legal_complexity: float = 2.0   # Score mínimo de complejidad legal
    require_legal_concepts: bool = True  # Debe contener conceptos legales específicos


class PrivateCollectionTrainer:
    """
    Entrenador especializado para colecciones documentales privadas
    con máxima confidencialidad y preservación de experiencia profesional.
    """
    
    def __init__(self, config: PrivateTrainingConfiguration):
        self.config = config
        self.logger = logging.getLogger("private_trainer")
        self.document_processor = None
        self.training_pipeline = None
        
    async def initialize(self, base_path: str = "/home/user/SLM-Legal-Spanish/data/private_corpus"):
        """Inicializa los componentes del entrenador."""
        # Inicializar procesador de documentos
        self.document_processor = await initialize_document_processor(base_path)
        
        # Inicializar pipeline de entrenamiento propietario (si está disponible)
        if ProprietaryTrainingPipeline is not None:
            self.training_pipeline = ProprietaryTrainingPipeline()
        else:
            self.training_pipeline = None
        
        self.logger.info("Private collection trainer initialized")
    
    async def create_training_plan(self, collection_path: str) -> Dict[str, Any]:
        """
        Crea plan de entrenamiento completo para la colección privada.
        
        Args:
            collection_path: Ruta a la colección de documentos privados
            
        Returns:
            Plan detallado de entrenamiento con estadísticas y configuración
        """
        self.logger.info("Creating comprehensive training plan for private collection")
        
        # Metadata del autor (tu experiencia profesional)
        author_metadata = self._create_author_metadata()
        
        # 1. FASE DE ANÁLISIS: Procesar y categorizar documentos
        processing_stats = await self._analyze_document_collection(
            collection_path, author_metadata
        )
        
        # 2. FASE DE ESTRATIFICACIÓN: Organizar por valor estratégico
        stratification_plan = await self._create_stratification_strategy()
        
        # 3. FASE DE ENTRENAMIENTO: Configurar pipeline propietario
        training_configuration = await self._configure_proprietary_training()
        
        # 4. FASE DE VALIDACIÓN: Definir métricas de evaluación
        evaluation_framework = await self._design_evaluation_framework()
        
        # 5. REPORTE COMPLETO
        complete_plan = {
            "plan_metadata": {
                "created_at": datetime.now().isoformat(),
                "collection_path": collection_path,
                "total_experience_years": self.config.total_experience_years,
                "confidentiality_level": "maximum",
                "anonymization_applied": True
            },
            "document_analysis": processing_stats,
            "stratification_strategy": stratification_plan,
            "training_configuration": training_configuration,
            "evaluation_framework": evaluation_framework,
            "implementation_roadmap": self._create_implementation_roadmap(),
            "security_measures": self._define_security_measures()
        }
        
        # Guardar plan completo
        await self._save_training_plan(complete_plan)
        
        return complete_plan
    
    def _create_author_metadata(self) -> Dict[str, Any]:
        """Crea metadata del autor sin referencias a terceros."""
        return {
            "authored_by_user": True,
            "total_experience_years": self.config.total_experience_years,
            "directorial_experience": self.config.directorial_experience_years,
            "corporate_law_experience": self.config.corporate_law_years,
            "roles_expertise": [
                "director_independiente",
                "abogado_corporativo_senior", 
                "consultor_ejecutivo",
                "especialista_gobierno_corporativo",
                "experto_compliance_riesgos"
            ],
            "jurisdictions_expertise": ["AR", "ES", "CL", "UY"],
            "sectors_experience": [
                "experiencia_corporativa_diversificada",
                "multisectorial_industrial",
                "governance_empresarial"
            ],
            "specializations": [
                "gobierno_corporativo",
                "compliance_regulatorio", 
                "gestion_riesgos_empresariales",
                "derecho_societario",
                "mercado_capitales"
            ]
        }
    
    async def _analyze_document_collection(self, collection_path: str, 
                                         author_metadata: Dict) -> Dict[str, Any]:
        """Analiza la colección completa con anonimización estricta."""
        
        # Procesar documentos con anonimización
        stats = await self.document_processor.process_document_collection(
            collection_path, author_metadata
        )
        
        # Análisis estratégico por categorías
        strategic_analysis = {
            "experiencia_directorial": {
                "total_documents": 0,
                "avg_quality_score": 0.0,
                "strategic_value": "máximo",
                "training_weight": 5.0,
                "description": "Documentos derivados de experiencia como director independiente"
            },
            "experiencia_corporativa_ejecutiva": {
                "total_documents": 0, 
                "avg_quality_score": 0.0,
                "strategic_value": "muy_alto",
                "training_weight": 4.5,
                "description": "Experiencia ejecutiva en entornos corporativos complejos"
            },
            "dictamenes_y_analisis_legales": {
                "total_documents": 0,
                "avg_quality_score": 0.0, 
                "strategic_value": "alto",
                "training_weight": 4.0,
                "description": "Dictámenes legales y análisis jurídicos elaborados"
            },
            "compliance_y_gestion_riesgos": {
                "total_documents": 0,
                "avg_quality_score": 0.0,
                "strategic_value": "alto", 
                "training_weight": 3.8,
                "description": "Frameworks de compliance y gestión de riesgos desarrollados"
            },
            "experiencia_multijurisdiccional": {
                "total_documents": 0,
                "avg_quality_score": 0.0,
                "strategic_value": "medio_alto",
                "training_weight": 3.5,
                "description": "Experiencia práctica en múltiples jurisdicciones"
            }
        }
        
        # Categorizar documentos procesados
        for doc in self.document_processor.processed_documents.values():
            category = self._categorize_by_strategic_value(doc)
            if category in strategic_analysis:
                strategic_analysis[category]["total_documents"] += 1
                strategic_analysis[category]["avg_quality_score"] += doc.quality_score
        
        # Calcular promedios
        for category_data in strategic_analysis.values():
            if category_data["total_documents"] > 0:
                category_data["avg_quality_score"] /= category_data["total_documents"]
        
        return {
            "processing_statistics": stats,
            "strategic_categorization": strategic_analysis,
            "anonymization_summary": {
                "total_anonymized": stats.get("anonymized", 0),
                "anonymization_rate": stats.get("anonymized", 0) / stats.get("total_files", 1),
                "security_level": "maximum"
            }
        }
    
    def _categorize_by_strategic_value(self, document_metadata) -> str:
        """Categoriza documento por valor estratégico sin revelar fuentes."""
        
        # Documentos de máximo valor: experiencia directorial
        if document_metadata.document_type == "acta_directorio":
            return "experiencia_directorial"
        
        # Documentos de muy alto valor: experiencia corporativa ejecutiva
        if (document_metadata.authored_by_user and 
            document_metadata.document_type in ["dictamen_legal", "compliance_report"]):
            return "experiencia_corporativa_ejecutiva"
        
        # Dictámenes y análisis legales
        if document_metadata.document_type == "dictamen_legal":
            return "dictamenes_y_analisis_legales"
            
        # Compliance y gestión de riesgos
        if document_metadata.document_type == "compliance_report":
            return "compliance_y_gestion_riesgos"
        
        # Experiencia multijurisdiccional
        if document_metadata.jurisdiction in ["ES", "CL", "UY"]:
            return "experiencia_multijurisdiccional"
        
        return "otros"
    
    async def _create_stratification_strategy(self) -> Dict[str, Any]:
        """Crea estrategia de estratificación para entrenamiento."""
        
        return {
            "nivel_1_experiencia_maxima": {
                "criteria": "Documentos de experiencia directorial y ejecutiva propia",
                "training_weight": 5.0,
                "batch_size": 4,  # Lotes pequeños para máximo aprendizaje
                "learning_rate": 0.0001,  # LR bajo para preservar conocimiento
                "epochs_focus": 15,
                "description": "Conocimiento propietario de máximo valor estratégico"
            },
            "nivel_2_experiencia_alta": {
                "criteria": "Dictámenes legales y frameworks de compliance desarrollados",
                "training_weight": 3.8,
                "batch_size": 8,
                "learning_rate": 0.0002,
                "epochs_focus": 12,
                "description": "Experiencia profesional especializada y diferenciada"
            },
            "nivel_3_experiencia_aplicada": {
                "criteria": "Experiencia multijurisdiccional y sectorial",
                "training_weight": 2.5,
                "batch_size": 16,
                "learning_rate": 0.0003,
                "epochs_focus": 8,
                "description": "Conocimiento aplicado en contextos diversos"
            },
            "nivel_4_conocimiento_base": {
                "criteria": "Material normativo y jurisprudencial especializado", 
                "training_weight": 1.5,
                "batch_size": 32,
                "learning_rate": 0.0005,
                "epochs_focus": 5,
                "description": "Base de conocimiento de referencia y contexto"
            }
        }
    
    async def _configure_proprietary_training(self) -> Dict[str, Any]:
        """Configura pipeline de entrenamiento propietario."""
        
        return {
            "model_architecture": {
                "base_model": "SLM-Legal-Spanish-7B",
                "specialized_layers": {
                    "directorial_experience_layer": {
                        "neurons": 2048,
                        "activation": "swiglu",
                        "dropout": 0.1,
                        "description": "Capa especializada en experiencia directorial"
                    },
                    "corporate_governance_layer": {
                        "neurons": 1536, 
                        "activation": "swiglu",
                        "dropout": 0.1,
                        "description": "Procesamiento de gobierno corporativo"
                    },
                    "compliance_risk_layer": {
                        "neurons": 1024,
                        "activation": "swiglu", 
                        "dropout": 0.15,
                        "description": "Análisis de compliance y gestión de riesgos"
                    }
                }
            },
            "training_methodology": {
                "approach": "Progressive Experience Distillation",
                "phases": [
                    {
                        "phase": "experience_foundation",
                        "duration_epochs": 20,
                        "focus": "Establecer base de experiencia profesional",
                        "data_mix": "100% experiencia propia"
                    },
                    {
                        "phase": "specialization_refinement", 
                        "duration_epochs": 15,
                        "focus": "Refinar especializaciones técnicas",
                        "data_mix": "80% propia, 20% referencia"
                    },
                    {
                        "phase": "integration_validation",
                        "duration_epochs": 10,
                        "focus": "Integrar y validar conocimiento",
                        "data_mix": "60% propia, 40% referencia"
                    }
                ]
            },
            "proprietary_loss_functions": {
                "experience_weighted_loss": {
                    "directorial_multiplier": 5.0,
                    "corporate_executive_multiplier": 4.5,
                    "legal_expertise_multiplier": 4.0,
                    "multijurisdictional_multiplier": 3.5
                },
                "confidentiality_preservation_loss": {
                    "anonymization_penalty": -2.0,  # Penaliza revelación de información
                    "generic_reward": 1.5          # Recompensa generalización apropiada
                }
            }
        }
    
    async def _design_evaluation_framework(self) -> Dict[str, Any]:
        """Diseña framework de evaluación específico para experiencia legal."""
        
        return {
            "professional_competency_metrics": {
                "directorial_decision_quality": {
                    "description": "Calidad de decisiones en contexto de directorio",
                    "test_cases": 50,
                    "evaluation_criteria": [
                        "análisis_riesgo_beneficio",
                        "consideraciones_fiduciarias", 
                        "cumplimiento_regulatorio",
                        "impacto_stakeholders"
                    ]
                },
                "legal_analysis_precision": {
                    "description": "Precisión en análisis jurídico complejo",
                    "test_cases": 75,
                    "evaluation_criteria": [
                        "identificacion_issues_legales",
                        "aplicacion_precedentes",
                        "analisis_riesgos_legales",
                        "recomendaciones_accionables"
                    ]
                },
                "compliance_framework_design": {
                    "description": "Capacidad de diseñar frameworks de compliance",
                    "test_cases": 30,
                    "evaluation_criteria": [
                        "cobertura_riesgos_identificados",
                        "practicidad_implementacion",
                        "alineacion_regulatoria",
                        "efectividad_monitoreo"
                    ]
                }
            },
            "jurisdictional_expertise_validation": {
                "multi_jurisdictional_consistency": {
                    "description": "Consistencia en análisis multijurisdiccional",
                    "jurisdictions_tested": ["AR", "ES", "CL", "UY"],
                    "test_scenarios": 40
                }
            },
            "confidentiality_verification": {
                "anonymization_effectiveness": {
                    "description": "Verificar que no se revela información de terceros",
                    "metrics": ["entity_detection", "pattern_recognition", "source_attribution"]
                }
            }
        }
    
    def _create_implementation_roadmap(self) -> List[Dict[str, Any]]:
        """Crea roadmap de implementación por fases."""
        
        return [
            {
                "phase": "Preparación Segura",
                "duration_days": 3,
                "tasks": [
                    "Configurar entorno de procesamiento aislado",
                    "Implementar anonimización automática",
                    "Validar protección de información sensible",
                    "Establecer métricas de confidencialidad"
                ],
                "success_criteria": "100% anonimización, 0% referencias a terceros"
            },
            {
                "phase": "Procesamiento Documental",
                "duration_days": 5,
                "tasks": [
                    "Procesar colección completa con categorización",
                    "Aplicar filtros de calidad y relevancia",
                    "Generar embeddings y análisis de patrones",
                    "Crear dataset estratificado por experiencia"
                ],
                "success_criteria": ">85% documentos procesados, calidad promedio >3.0"
            },
            {
                "phase": "Entrenamiento Propietario",
                "duration_days": 12,
                "tasks": [
                    "Implementar arquitectura especializada",
                    "Ejecutar entrenamiento progresivo por niveles",
                    "Aplicar funciones de pérdida propietarias", 
                    "Validar preservación de confidencialidad"
                ],
                "success_criteria": "Convergencia estable, métricas profesionales >90%"
            },
            {
                "phase": "Validación y Optimización", 
                "duration_days": 4,
                "tasks": [
                    "Ejecutar evaluaciones de competencia profesional",
                    "Verificar consistencia multijurisdiccional",
                    "Optimizar hiperparámetros específicos",
                    "Generar reportes de performance"
                ],
                "success_criteria": "Evaluación profesional aprobada, confidencialidad verificada"
            },
            {
                "phase": "Despliegue Propietario",
                "duration_days": 2, 
                "tasks": [
                    "Empaquetar modelo con protecciones IP",
                    "Configurar deployment con licenciamiento",
                    "Establecer monitoreo de uso y performance",
                    "Documentar capacidades y limitaciones"
                ],
                "success_criteria": "Sistema productivo, licenciamiento activo"
            }
        ]
    
    def _define_security_measures(self) -> Dict[str, Any]:
        """Define medidas de seguridad para proteger confidencialidad."""
        
        return {
            "data_protection": {
                "anonymization": "Presidio-based automatic PII detection and removal",
                "company_references": "Complete removal of third-party entity names",
                "financial_data": "Obfuscation of specific monetary amounts",
                "temporal_generalization": "Preserve year, remove specific dates if requested"
            },
            "processing_security": {
                "local_only": "All processing performed locally, no cloud transmission",
                "encrypted_storage": "AES-256 encryption for processed documents", 
                "access_control": "Single-user access, no shared credentials",
                "audit_trail": "Complete logging of all processing operations"
            },
            "model_protection": {
                "ip_protection": "Cryptographic signing of model artifacts",
                "anti_tampering": "Runtime integrity verification",
                "usage_monitoring": "Track model inference and prevent unauthorized use",
                "licensing_enforcement": "Technical measures to enforce usage rights"
            },
            "confidentiality_verification": {
                "output_scanning": "Automatic scanning of model outputs for sensitive data",
                "pattern_detection": "Detection of potential information leakage patterns",
                "third_party_references": "Verification that no external entities are mentioned",
                "compliance_validation": "Regular validation against confidentiality requirements"
            }
        }
    
    async def _save_training_plan(self, plan: Dict[str, Any]):
        """Guarda plan de entrenamiento de forma segura."""
        
        plan_file = Path("/home/user/SLM-Legal-Spanish/data/private_corpus/processed/private_training_plan.json")
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Training plan saved securely to {plan_file}")


# Función principal para ejecutar el plan
async def create_private_training_plan(collection_path: str) -> Dict[str, Any]:
    """
    Función principal para crear plan de entrenamiento de colección privada.
    
    Args:
        collection_path: Ruta a la colección de documentos privados
        
    Returns:
        Plan completo de entrenamiento con máxima confidencialidad
    """
    
    # Configuración para máxima confidencialidad
    config = PrivateTrainingConfiguration(
        total_experience_years=30,
        directorial_experience_years=15, 
        corporate_law_years=25,
        anonymization_level="strict",
        remove_company_references=True,
        remove_monetary_amounts=True
    )
    
    # Crear entrenador especializado
    trainer = PrivateCollectionTrainer(config)
    await trainer.initialize()
    
    # Generar plan completo
    plan = await trainer.create_training_plan(collection_path)
    
    return plan


if __name__ == "__main__":
    """
    Ejecutar plan de entrenamiento para colección privada.
    """
    import asyncio
    
    async def main():
        # IMPORTANTE: Ajustar esta ruta a tu colección real de documentos
        collection_path = "/path/to/your/private/document/collection"
        
        try:
            plan = await create_private_training_plan(collection_path)
            
            print("✅ PLAN DE ENTRENAMIENTO PRIVADO CREADO")
            print(f"📁 Documentos analizados: {plan['document_analysis']['processing_statistics']['total_files']}")
            print(f"🔒 Documentos anonimizados: {plan['document_analysis']['processing_statistics']['anonymized']}")
            print(f"⚖️ Nivel de confidencialidad: {plan['plan_metadata']['confidentiality_level']}")
            print(f"🎯 Fases de implementación: {len(plan['implementation_roadmap'])}")
            
            # Mostrar categorización estratégica
            print("\n📊 CATEGORIZACIÓN ESTRATÉGICA:")
            for category, data in plan['document_analysis']['strategic_categorization'].items():
                if data['total_documents'] > 0:
                    print(f"  • {category}: {data['total_documents']} docs (valor: {data['strategic_value']})")
            
        except Exception as e:
            print(f"❌ Error creando plan: {e}")
    
    asyncio.run(main())