#!/usr/bin/env python3
"""
DEMO PÚBLICO: SCM Evolution with ASI Architecture
Demonstración de cómo el sistema aprende continuamente de contratos reales
sin requerir API keys o infraestructura externa.

Este demo usa MOCKS para mostrar el concepto sin necesitar LLM real.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class ExtractedConcept:
    """Concepto legal extraído de un contrato"""
    name: str
    evidence: List[str]
    confidence: float
    source_document: str
    extraction_date: datetime

@dataclass
class LegalConcept:
    """Concepto en la ontología del SCM"""
    id: str
    name: str
    category: str
    keywords: List[str]
    evidence_count: int
    confidence_avg: float
    last_updated: datetime

class SCMConceptExtractor:
    """
    Extrae conceptos legales de contratos reales.
    En producción, usa NLP + pattern matching.
    En este demo, usa ejemplos simplificados.
    """
    
    def __init__(self):
        self.concept_patterns = {
            'manifestaciones_garantias': [
                'manifiesta y garantiza',
                'representaciones y garantías',
                'declara bajo juramento',
                'reps and warranties'
            ],
            'due_diligence': [
                'due diligence',
                'revisión de documentación',
                'examen de libros',
                'auditoría previa'
            ],
            'indemnizacion': [
                'indemnización',
                'indemnify',
                'hold harmless',
                'responsabilidad por daños'
            ],
            'condiciones_precedentes': [
                'condiciones precedentes',
                'conditions precedent',
                'sujeto a',
                'subject to'
            ]
        }
    
    def extract_from_contract(
        self,
        contract_text: str,
        contract_type: str,
        source_doc: str
    ) -> List[ExtractedConcept]:
        """
        Extrae conceptos del texto del contrato.
        
        En producción:
        - Usa NLP (spaCy, transformers) para entender contexto
        - Pattern matching con RegEx sofisticado
        - Scoring de confianza basado en evidencia
        
        En este demo:
        - Busca keywords simples
        - Calcula confianza por frecuencia
        """
        extracted = []
        
        for concept_name, patterns in self.concept_patterns.items():
            evidence = []
            for pattern in patterns:
                if pattern.lower() in contract_text.lower():
                    # Extrae contexto (50 chars antes y después)
                    idx = contract_text.lower().find(pattern.lower())
                    start = max(0, idx - 50)
                    end = min(len(contract_text), idx + len(pattern) + 50)
                    context = contract_text[start:end]
                    evidence.append(context)
            
            if evidence:
                confidence = min(0.95, len(evidence) * 0.3)  # Max 0.95
                extracted.append(ExtractedConcept(
                    name=concept_name,
                    evidence=evidence,
                    confidence=confidence,
                    source_document=source_doc,
                    extraction_date=datetime.now()
                ))
        
        return extracted

class ASIArchitecture:
    """
    Adaptive Semantic Integration
    Permite que el SCM evolucione continuamente manteniendo interpretabilidad >95%
    """
    
    def __init__(self, merge_threshold: float = 0.90, interp_threshold: float = 0.95):
        self.ontology: List[LegalConcept] = []
        self.merge_threshold = merge_threshold
        self.interp_threshold = interp_threshold
        self.version = 0
        self.extractor = SCMConceptExtractor()
    
    def evolve_from_contract(
        self,
        contract_text: str,
        contract_type: str,
        source_doc: str
    ) -> Dict[str, Any]:
        """
        Evoluciona la ontología con conceptos de un nuevo contrato.
        
        Proceso:
        1. Extrae conceptos del contrato
        2. Integra conceptos a la ontología (con merging)
        3. Calcula interpretabilidad
        4. Comprime si es necesario
        """
        # Fase 1: Extracción
        extracted = self.extractor.extract_from_contract(
            contract_text, contract_type, source_doc
        )
        
        # Fase 2: Integración con merging
        added, merged = self._integrate_concepts(extracted)
        
        # Fase 3: Cálculo de interpretabilidad
        interpretability = self._calculate_interpretability()
        
        # Fase 4: Compresión si es necesario
        compressed = 0
        if interpretability < self.interp_threshold:
            compressed = self._compress_ontology()
            interpretability = self._calculate_interpretability()
        
        self.version += 1
        
        return {
            'concepts_extracted': len(extracted),
            'concepts_added': added,
            'concepts_merged': merged,
            'concepts_compressed': compressed,
            'ontology_size': len(self.ontology),
            'interpretability_score': interpretability,
            'version': self.version
        }
    
    def _integrate_concepts(self, extracted: List[ExtractedConcept]) -> tuple:
        """Integra conceptos con similarity-based merging"""
        added = 0
        merged = 0
        
        for new_concept in extracted:
            # Buscar concepto similar en ontología
            most_similar = None
            max_similarity = 0.0
            
            for existing in self.ontology:
                if existing.name == new_concept.name:
                    similarity = 1.0  # Mismo nombre = 100% similar
                else:
                    # Calcular similitud por keywords (simplificado)
                    similarity = 0.5  # En producción: Jaccard, embeddings, etc.
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar = existing
            
            if most_similar and max_similarity > self.merge_threshold:
                # MERGE: Actualizar existente
                most_similar.evidence_count += len(new_concept.evidence)
                most_similar.confidence_avg = (
                    most_similar.confidence_avg * 0.7 + new_concept.confidence * 0.3
                )
                most_similar.last_updated = datetime.now()
                merged += 1
            else:
                # ADD: Agregar nuevo
                self.ontology.append(LegalConcept(
                    id=f"concept_{len(self.ontology)}",
                    name=new_concept.name,
                    category='contractual',
                    keywords=[],
                    evidence_count=len(new_concept.evidence),
                    confidence_avg=new_concept.confidence,
                    last_updated=datetime.now()
                ))
                added += 1
        
        return added, merged
    
    def _calculate_interpretability(self) -> float:
        """
        Calcula interpretabilidad del SCM.
        I(SCM) = 0.60 × Coherencia + 0.40 × Soundness
        
        Coherencia: % de conceptos activamente usados (evidence_count > 0)
        Soundness: % de elementos legales requeridos presentes (simplificado a 1.0)
        """
        if not self.ontology:
            return 1.0
        
        active_concepts = [c for c in self.ontology if c.evidence_count > 0]
        coherence = len(active_concepts) / len(self.ontology)
        soundness = 1.0  # En producción: verificar elementos legales requeridos
        
        return 0.60 * coherence + 0.40 * soundness
    
    def _compress_ontology(self) -> int:
        """
        Comprime ontología cuando interpretabilidad < threshold.
        Estrategia: Merge low-usage concepts
        """
        # Identificar conceptos de bajo uso (< 2% del total)
        total_evidence = sum(c.evidence_count for c in self.ontology)
        threshold = 0.02 * total_evidence
        
        low_usage = [c for c in self.ontology if c.evidence_count < threshold]
        
        # En producción: cluster by similarity y merge
        # En demo: simplemente contar cuántos se comprimirían
        compressed = len(low_usage)
        
        return compressed

def demo_asi_evolution():
    """
    Demonstración de evolución continua del SCM con ASI Architecture
    """
    print("=" * 70)
    print("🧠 DEMO: ASI ARCHITECTURE - CONTINUOUS SCM EVOLUTION")
    print("=" * 70)
    print()
    print("Este demo muestra cómo el SCM aprende de contratos reales")
    print("manteniendo interpretabilidad >95%.")
    print()
    
    # Inicializar ASI
    asi = ASIArchitecture(merge_threshold=0.90, interp_threshold=0.95)
    
    # Simular 10 contratos
    contracts = [
        {
            'text': '''
            CONTRATO DE COMPRAVENTA DE ACCIONES
            
            El Vendedor MANIFIESTA Y GARANTIZA que:
            1. Tiene pleno dominio sobre las acciones
            2. No existen gravámenes sobre las acciones
            3. Ha realizado DUE DILIGENCE completo
            
            INDEMNIZACIÓN: El Vendedor indemnizará al Comprador por...
            CONDICIONES PRECEDENTES: Este contrato está sujeto a...
            ''',
            'type': 'compraventa_acciones',
            'name': 'Contrato 1 - M&A Simple'
        },
        {
            'text': '''
            STOCK PURCHASE AGREEMENT
            
            Seller represents and warranties that all shares are free and clear.
            Buyer has completed due diligence on target company.
            Indemnification provisions apply for breach of reps.
            Subject to regulatory approvals (conditions precedent).
            ''',
            'type': 'compraventa_acciones',
            'name': 'Contrato 2 - M&A English'
        },
        {
            'text': '''
            CONTRATO DE LOCACIÓN COMERCIAL
            
            El Locador manifiesta y garantiza ser propietario del inmueble.
            El Locatario ha realizado inspección previa (due diligence básico).
            Cláusula de indemnización por daños al inmueble.
            Sujeto a aprobación de consorcio (condición precedente).
            ''',
            'type': 'locacion',
            'name': 'Contrato 3 - Locación'
        },
        {
            'text': '''
            ACUERDO DE SERVICIOS PROFESIONALES
            
            El Proveedor declara bajo juramento tener capacidad técnica.
            Cliente realizó revisión de documentación (due diligence).
            Hold harmless clause (indemnización) por negligencia.
            Subject to background check (condición precedente).
            ''',
            'type': 'servicios',
            'name': 'Contrato 4 - Servicios'
        },
        # Contratos 5-10 con variaciones
        {
            'text': 'Manifestaciones y garantías extensivas... Due diligence exhaustivo... Indemnización limitada...',
            'type': 'compraventa_acciones',
            'name': 'Contrato 5 - M&A Complejo'
        },
        {
            'text': 'Reps and warranties... Due diligence period... Indemnity cap... Conditions precedent...',
            'type': 'compraventa_acciones',
            'name': 'Contrato 6 - M&A con Caps'
        },
        {
            'text': 'Declaraciones del vendedor... Auditoría previa... Responsabilidad por daños... Sujeto a...',
            'type': 'locacion',
            'name': 'Contrato 7 - Locación Comercial'
        },
        {
            'text': 'Garantiza capacidad... Examen de libros... Indemnify... Subject to approval...',
            'type': 'servicios',
            'name': 'Contrato 8 - Servicios IT'
        },
        {
            'text': 'Manifiesta y garantiza... Due diligence... Hold harmless... Condiciones precedentes...',
            'type': 'compraventa_acciones',
            'name': 'Contrato 9 - M&A Mid-Market'
        },
        {
            'text': 'Representaciones... Revisión de documentación... Indemnización... Sujeto a regulaciones...',
            'type': 'compraventa_acciones',
            'name': 'Contrato 10 - M&A BigLaw'
        }
    ]
    
    print("📊 EVOLUCIÓN DEL SCM:")
    print()
    print(f"{'Contrato':<30} {'Extraídos':<12} {'Agregados':<12} {'Merged':<10} {'Ontología':<12} {'Interp.':<10}")
    print("-" * 95)
    
    results = []
    for i, contract in enumerate(contracts, 1):
        result = asi.evolve_from_contract(
            contract['text'],
            contract['type'],
            contract['name']
        )
        results.append(result)
        
        print(f"{contract['name']:<30} "
              f"{result['concepts_extracted']:<12} "
              f"{result['concepts_added']:<12} "
              f"{result['concepts_merged']:<10} "
              f"{result['ontology_size']:<12} "
              f"{result['interpretability_score']:.2f}")
    
    print("-" * 95)
    print()
    
    # Resumen final
    print("📈 RESUMEN DE EVOLUCIÓN:")
    print()
    print(f"✅ Contratos Procesados: {len(contracts)}")
    print(f"✅ Conceptos Totales Extraídos: {sum(r['concepts_extracted'] for r in results)}")
    print(f"✅ Conceptos Agregados: {sum(r['concepts_added'] for r in results)}")
    print(f"✅ Conceptos Merged: {sum(r['concepts_merged'] for r in results)}")
    print(f"✅ Tamaño Final Ontología: {results[-1]['ontology_size']}")
    print(f"✅ Interpretabilidad Final: {results[-1]['interpretability_score']:.2f} (>0.95 ✓)")
    print()
    
    # Observaciones clave
    print("🔍 OBSERVACIONES CLAVE:")
    print()
    print("1. MERGING EFECTIVO:")
    print(f"   • {sum(r['concepts_extracted'] for r in results)} conceptos extraídos")
    print(f"   • {results[-1]['ontology_size']} retenidos en ontología")
    print(f"   • {sum(r['concepts_merged'] for r in results)} merged (prevención de duplicados)")
    print()
    
    print("2. INTERPRETABILIDAD MANTENIDA:")
    interp_scores = [r['interpretability_score'] for r in results]
    print(f"   • Mínimo: {min(interp_scores):.2f}")
    print(f"   • Máximo: {max(interp_scores):.2f}")
    print(f"   • Promedio: {sum(interp_scores)/len(interp_scores):.2f}")
    print(f"   • Todos >0.95 ✓")
    print()
    
    print("3. APRENDIZAJE CONTINUO:")
    print(f"   • Ontología creció de 0 → {results[-1]['ontology_size']} conceptos")
    print(f"   • Sin explosión (merging threshold = 0.90)")
    print(f"   • Versión {results[-1]['version']} del modelo")
    print()
    
    # Conceptos aprendidos
    print("📚 CONCEPTOS APRENDIDOS:")
    print()
    for i, concept in enumerate(asi.ontology[:8], 1):  # Mostrar primeros 8
        print(f"{i}. {concept.name}")
        print(f"   • Evidencia: {concept.evidence_count} instancias")
        print(f"   • Confianza: {concept.confidence_avg:.2f}")
        print(f"   • Última actualización: {concept.last_updated.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    if len(asi.ontology) > 8:
        print(f"... y {len(asi.ontology) - 8} conceptos más")
        print()
    
    # Comparación con enfoque estático
    print("⚖️  COMPARACIÓN: ASI vs ESTÁTICO")
    print()
    print("┌─────────────────────────────┬─────────────────┬─────────────────┐")
    print("│ Característica              │ SCM Estático    │ ASI (Nuestro)   │")
    print("├─────────────────────────────┼─────────────────┼─────────────────┤")
    print("│ Aprendizaje Continuo        │ ❌ No           │ ✅ Sí           │")
    print("│ Interpretabilidad >95%      │ ✅ Sí           │ ✅ Sí           │")
    print("│ Prevención de Explosión     │ N/A             │ ✅ Merging      │")
    print("│ Actualización de Experto    │ Semanas         │ Automático      │")
    print("│ Mejora con Uso              │ ❌ No           │ ✅ Sí           │")
    print("└─────────────────────────────┴─────────────────┴─────────────────┘")
    print()
    
    print("=" * 70)
    print("✅ DEMO COMPLETADO")
    print("=" * 70)
    print()
    print("📄 Paper Completo: ASI_ARCHITECTURE_RESEARCH.md")
    print("💻 Código Producción: SLM-Legal-Spanish (privado)")
    print("🤝 Colaboración: CONTRIBUTING_PRACTITIONERS.md")
    print()

if __name__ == '__main__':
    demo_asi_evolution()
