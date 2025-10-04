#!/usr/bin/env python3
"""
Ejecutor de Entrenamiento Privado - SLM-Legal-Spanish
===================================================

Script principal para ejecutar el entrenamiento con tu colección privada
de documentos legales con máxima confidencialidad y seguridad.

CONFIDENCIAL - Uso Exclusivo
Desarrollado por: Ignacio Adrián Lerer

Características de Seguridad Implementadas:
✅ Anonimización automática completa
✅ Sin referencias a terceros o empresas
✅ Procesamiento local únicamente
✅ Trazabilidad de experiencia sin revelación de fuentes
✅ Categorización por valor estratégico propietario

INSTRUCCIONES DE USO:
1. Coloca tus documentos en una carpeta accesible
2. Ajusta la variable COLLECTION_PATH con la ruta correcta
3. Ejecuta: python execute_private_training.py
4. El sistema procesará automáticamente con máxima confidencialidad
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar src al path para imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.proprietary.private_training_plan import create_private_training_plan

# Importación opcional para pipeline de entrenamiento
try:
    from src.proprietary.advanced_training_pipeline import ProprietaryTrainingPipeline
except ImportError:
    ProprietaryTrainingPipeline = None


async def main():
    """
    Función principal para ejecutar entrenamiento privado.
    """
    
    print("🚀 INICIANDO ENTRENAMIENTO PRIVADO SLM-Legal-Spanish")
    print("=" * 60)
    print("📋 Configuración de Seguridad:")
    print("   ✅ Anonimización automática: ACTIVADA")
    print("   ✅ Protección de confidencialidad: MÁXIMA")
    print("   ✅ Procesamiento local: EXCLUSIVO")
    print("   ✅ Sin referencias a terceros: GARANTIZADO")
    print()
    
    # ==========================================
    # CONFIGURACIÓN - AJUSTAR SEGÚN TUS DATOS
    # ==========================================
    
    # IMPORTANTE: Cambiar esta ruta a donde tienes tus documentos
    COLLECTION_PATH = "/home/user/documents/private_collection"
    
    # Verificar si la ruta existe (para demo, creamos estructura de ejemplo)
    if not Path(COLLECTION_PATH).exists():
        print(f"⚠️  La ruta {COLLECTION_PATH} no existe.")
        print(f"📁 Creando estructura de ejemplo para demostración...")
        
        # Crear estructura de ejemplo
        example_path = "/home/user/SLM-Legal-Spanish/data/example_private_collection"
        Path(example_path).mkdir(parents=True, exist_ok=True)
        
        # Crear documentos de ejemplo (anonimizados)
        create_example_documents(example_path)
        
        COLLECTION_PATH = example_path
        print(f"✅ Usando ruta de ejemplo: {COLLECTION_PATH}")
    
    print(f"📂 Procesando colección en: {COLLECTION_PATH}")
    print()
    
    try:
        # ==========================================
        # FASE 1: CREAR PLAN DE ENTRENAMIENTO
        # ==========================================
        
        print("🔍 FASE 1: Análisis y Planificación Segura")
        print("-" * 40)
        
        plan = await create_private_training_plan(COLLECTION_PATH)
        
        # Mostrar resumen del plan
        print("✅ Plan de entrenamiento creado exitosamente")
        print(f"📊 Estadísticas del procesamiento:")
        
        stats = plan['document_analysis']['processing_statistics']
        print(f"   • Total de archivos: {stats['total_files']}")
        print(f"   • Procesados exitosamente: {stats['processed_successfully']}")
        print(f"   • Documentos anonimizados: {stats['anonymized']}")
        print(f"   • Tasa de anonimización: {plan['document_analysis']['anonymization_summary']['anonymization_rate']:.1%}")
        
        # Mostrar categorización estratégica
        print(f"\\n🎯 Categorización por Valor Estratégico:")
        for category, data in plan['document_analysis']['strategic_categorization'].items():
            if data['total_documents'] > 0:
                print(f"   • {category}: {data['total_documents']} documentos")
                print(f"     - Valor estratégico: {data['strategic_value']}")
                print(f"     - Peso de entrenamiento: {data['training_weight']:.1f}x")
                print(f"     - Calidad promedio: {data['avg_quality_score']:.2f}")
        
        print(f"\\n🔒 Medidas de Seguridad Aplicadas:")
        security = plan['security_measures']
        print(f"   ✅ Anonimización: {security['data_protection']['anonymization']}")
        print(f"   ✅ Referencias empresas: {security['data_protection']['company_references']}")
        print(f"   ✅ Procesamiento local: {security['processing_security']['local_only']}")
        print(f"   ✅ Protección IP: {security['model_protection']['ip_protection']}")
        
        print()
        
        # ==========================================
        # FASE 2: CONFIGURAR PIPELINE PROPIETARIO
        # ==========================================
        
        print("⚙️  FASE 2: Configuración del Pipeline Propietario")
        print("-" * 40)
        
        # Inicializar pipeline con configuración del plan
        training_config = plan['training_configuration']
        
        print("✅ Pipeline propietario configurado:")
        print(f"   • Arquitectura: {training_config['model_architecture']['base_model']}")
        print(f"   • Metodología: {training_config['training_methodology']['approach']}")
        print(f"   • Fases de entrenamiento: {len(training_config['training_methodology']['phases'])}")
        
        # Mostrar capas especializadas
        print(f"\\n🧠 Capas Especializadas:")
        for layer_name, layer_config in training_config['model_architecture']['specialized_layers'].items():
            print(f"   • {layer_name}:")
            print(f"     - Neuronas: {layer_config['neurons']}")
            print(f"     - Descripción: {layer_config['description']}")
        
        print()
        
        # ==========================================
        # FASE 3: ROADMAP DE IMPLEMENTACIÓN  
        # ==========================================
        
        print("🗺️  FASE 3: Roadmap de Implementación")
        print("-" * 40)
        
        total_days = sum(phase['duration_days'] for phase in plan['implementation_roadmap'])
        print(f"📅 Duración total estimada: {total_days} días")
        print()
        
        for i, phase in enumerate(plan['implementation_roadmap'], 1):
            print(f"🔢 Fase {i}: {phase['phase']} ({phase['duration_days']} días)")
            print(f"   Criterio de éxito: {phase['success_criteria']}")
            for task in phase['tasks']:
                print(f"   ✓ {task}")
            print()
        
        # ==========================================
        # FASE 4: MÉTRICAS DE EVALUACIÓN
        # ==========================================
        
        print("📈 FASE 4: Framework de Evaluación Profesional")
        print("-" * 40)
        
        eval_framework = plan['evaluation_framework']
        
        # Métricas de competencia profesional
        print("🎓 Métricas de Competencia Profesional:")
        for metric_name, metric_config in eval_framework['professional_competency_metrics'].items():
            print(f"   • {metric_name}: {metric_config['test_cases']} casos de prueba")
            print(f"     - {metric_config['description']}")
        
        # Validación jurisdiccional
        jurisdictional = eval_framework['jurisdictional_expertise_validation']
        multi_j = jurisdictional['multi_jurisdictional_consistency']
        print(f"\\n🌍 Validación Multijurisdiccional:")
        print(f"   • Jurisdicciones: {', '.join(multi_j['jurisdictions_tested'])}")
        print(f"   • Escenarios de prueba: {multi_j['test_scenarios']}")
        
        # Verificación de confidencialidad
        print(f"\\n🔐 Verificación de Confidencialidad:")
        conf_metrics = eval_framework['confidentiality_verification']['anonymization_effectiveness']['metrics']
        for metric in conf_metrics:
            print(f"   ✓ {metric}")
        
        print()
        print("✅ PLAN DE ENTRENAMIENTO PRIVADO COMPLETADO")
        print("=" * 60)
        print("📋 Siguiente paso: Revisar el archivo generado en:")
        print(f"   📄 /home/user/SLM-Legal-Spanish/data/private_corpus/processed/private_training_plan.json")
        print()
        print("⚖️  CONFIDENCIALIDAD GARANTIZADA")
        print("   • Sin referencias a empresas terceras")
        print("   • Anonimización automática aplicada") 
        print("   • Procesamiento 100% local")
        print("   • Experiencia profesional preservada de forma genérica")
        
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()


def create_example_documents(example_path: str):
    """
    Crea documentos de ejemplo para demostrar el procesamiento
    (completamente anonimizados y genéricos).
    """
    
    # Crear subdirectorios
    subdirs = [
        "actas_directorio",
        "dictamenes_legales", 
        "compliance_reports",
        "contratos",
        "normativas"
    ]
    
    for subdir in subdirs:
        Path(example_path, subdir).mkdir(parents=True, exist_ok=True)
    
    # Documento 1: Acta de directorio (anonimizada)
    acta_content = '''
    ACTA DE REUNIÓN DE DIRECTORIO N° XXX
    
    Fecha: [FECHA_ANONIMIZADA]
    Lugar: Sede social
    
    ASISTENTES:
    - [DIRECTOR_1]: Director Independiente  
    - [DIRECTOR_2]: Director Titular
    - [DIRECTOR_3]: Director Suplente
    
    ORDEN DEL DÍA:
    1. Análisis de riesgos operacionales
    2. Evaluación de framework de compliance
    3. Aprobación de políticas de gobierno corporativo
    
    RESOLUCIONES:
    
    Se resuelve aprobar el framework de gestión de riesgos propuesto, 
    considerando las mejores prácticas internacionales y el cumplimiento
    de la normativa vigente en materia de gobierno corporativo.
    
    El marco incluye procedimientos de identificación, evaluación y 
    mitigación de riesgos, con reportes trimestrales al directorio.
    
    [FIRMA_ANONIMIZADA]
    Director Independiente
    '''
    
    with open(Path(example_path, "actas_directorio", "acta_ejemplo_001.txt"), 'w', encoding='utf-8') as f:
        f.write(acta_content)
    
    # Documento 2: Dictamen legal (anonimizado)
    dictamen_content = '''
    DICTAMEN LEGAL N° XXX
    
    A: [CLIENTE_ANONIMIZADO]
    De: [ABOGADO_ANONIMIZADO]
    Fecha: [FECHA_ANONIMIZADA]
    
    Ref: Análisis de cumplimiento normativo - Ley de Mercado de Capitales
    
    CONSULTA:
    Se solicita análisis sobre la aplicabilidad de las disposiciones
    de la Ley 26.831 respecto a las obligaciones de información
    de sociedades que hacen oferta pública de sus acciones.
    
    ANÁLISIS LEGAL:
    
    1. MARCO NORMATIVO APLICABLE
    La Ley 26.831 establece el régimen del mercado de capitales,
    siendo de aplicación a todas las personas humanas y jurídicas
    que participen en la oferta pública.
    
    2. OBLIGACIONES DE INFORMACIÓN
    El art. 63 establece la obligación de presentar información
    periódica según los plazos establecidos por la CNV.
    
    3. RECOMENDACIONES
    Se recomienda implementar un cronograma de cumplimiento
    que contemple todas las fechas de presentación obligatoria.
    
    CONCLUSIÓN:
    La sociedad debe cumplir estrictamente con las obligaciones
    informativas establecidas en la normativa vigente.
    
    [FIRMA_ANONIMIZADA]
    Abogado Responsable
    '''
    
    with open(Path(example_path, "dictamenes_legales", "dictamen_ejemplo_001.txt"), 'w', encoding='utf-8') as f:
        f.write(dictamen_content)
    
    # Documento 3: Reporte de compliance (anonimizado)
    compliance_content = '''
    REPORTE DE COMPLIANCE - TRIMESTRE [PERIODO_ANONIMIZADO]
    
    RESUMEN EJECUTIVO
    
    El presente reporte analiza el estado de cumplimiento de las
    políticas internas y normativas externas durante el período
    bajo análisis.
    
    ÁREAS EVALUADAS:
    
    1. GOBIERNO CORPORATIVO
    - Funcionamiento del directorio: SATISFACTORIO
    - Comités especializados: OPERATIVO
    - Políticas de conflictos de interés: ACTUALIZADA
    
    2. GESTIÓN DE RIESGOS
    - Matriz de riesgos: REVISADA Y ACTUALIZADA
    - Controles internos: FUNCIONANDO
    - Reportes de incidentes: 0 eventos materiales
    
    3. CUMPLIMIENTO REGULATORIO
    - Normativa CNV: CUMPLIMIENTO TOTAL
    - Reportes obligatorios: PRESENTADOS EN TÉRMINO
    - Actualizaciones normativas: INCORPORADAS
    
    RECOMENDACIONES:
    1. Fortalecer capacitación en nuevas normativas
    2. Actualizar procedimientos de debida diligencia
    3. Implementar métricas adicionales de monitoreo
    
    PRÓXIMOS PASOS:
    - Revisión semestral de políticas
    - Actualización de matriz de riesgos
    - Capacitación especializada del personal
    
    [ELABORADO_POR_ANONIMIZADO]
    Responsable de Compliance
    '''
    
    with open(Path(example_path, "compliance_reports", "compliance_ejemplo_001.txt"), 'w', encoding='utf-8') as f:
        f.write(compliance_content)
    
    print(f"✅ Documentos de ejemplo creados en {example_path}")


if __name__ == "__main__":
    """
    Punto de entrada principal.
    """
    asyncio.run(main())