"""
Compliance Preservation Analyzer for Legal AI Systems
Analyzes how much critical legal information is preserved in summaries
Based on research: "TL;DR vs. cumplimiento normativo"
"""

import spacy
import re
import numpy as np
from typing import Dict, Any, List, Tuple, Set
from dataclasses import dataclass
from collections import Counter
import logging
from enum import Enum

class EntityType(Enum):
    """Legal entity types for compliance analysis"""
    SANCION = "SANCION"           # Penalties and sanctions
    PLAZO = "PLAZO"               # Legal deadlines
    MONTO = "MONTO"               # Monetary amounts
    OBLIGACION = "OBLIGACION"     # Legal obligations
    DERECHO = "DERECHO"           # Rights
    PROCEDIMIENTO = "PROCEDIMIENTO" # Legal procedures
    RESPONSABILIDAD = "RESPONSABILIDAD" # Responsibilities
    EXCEPCION = "EXCEPCION"       # Exceptions and exemptions

@dataclass
class LegalEntity:
    """Represents a legal entity found in text"""
    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    context: str
    criticality_score: float  # 0-1, how critical this entity is

@dataclass
class ComplianceAnalysisResult:
    """Results of compliance preservation analysis"""
    overall_preservation: float
    entity_preservation: Dict[str, float]
    critical_losses: List[str]
    compression_ratio: float
    safety_threshold: float
    detailed_analysis: Dict[str, Any]

class CompliancePreservationAnalyzer:
    """
    Analyzes preservation of critical legal information in summaries
    
    Key research question: ¿Qué % de obligaciones precisas se pierde en resumen de 150 palabras?
    
    Methods:
    - Legal Named Entity Recognition (NER)
    - False negative counting for critical entities
    - Safety threshold calculation for compression
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load Spanish legal NLP model
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except IOError:
            self.logger.warning("Spanish spaCy model not found. Using pattern-based extraction.")
            self.nlp = None
            
        # Legal entity patterns for Spanish legal text
        self.legal_patterns = {
            EntityType.SANCION: {
                'patterns': [
                    r'multa\s+de\s+([^\.]+)',
                    r'sanción\s+de\s+([^\.]+)',
                    r'penalidad\s+de\s+([^\.]+)',
                    r'será\s+sancionado\s+con\s+([^\.]+)',
                    r'se\s+aplicará\s+una\s+multa\s+([^\.]+)',
                    r'prisión\s+de\s+([^\.]+)',
                    r'inhabilitación\s+por\s+([^\.]+)'
                ],
                'criticality': 0.95
            },
            EntityType.PLAZO: {
                'patterns': [
                    r'plazo\s+de\s+(\d+)\s+días?',
                    r'dentro\s+de\s+(\d+)\s+días?',
                    r'en\s+el\s+término\s+de\s+(\d+)\s+días?',
                    r'hasta\s+el\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
                    r'antes\s+del\s+(\d{1,2}\s+de\s+\w+)',
                    r'vencimiento\s+el\s+([^\.]+)',
                    r'plazo\s+máximo\s+de\s+([^\.]+)'
                ],
                'criticality': 0.90
            },
            EntityType.MONTO: {
                'patterns': [
                    r'\$\s*(\d+(?:[\.,]\d+)*)',
                    r'pesos\s+(\d+(?:[\.,]\d+)*)',
                    r'suma\s+de\s+\$?\s*(\d+(?:[\.,]\d+)*)',
                    r'monto\s+de\s+\$?\s*(\d+(?:[\.,]\d+)*)',
                    r'importe\s+de\s+\$?\s*(\d+(?:[\.,]\d+)*)',
                    r'(\d+(?:[\.,]\d+)*)\s+UF',
                    r'salarios\s+mínimos?\s+(\d+)'
                ],
                'criticality': 0.85
            },
            EntityType.OBLIGACION: {
                'patterns': [
                    r'deberá\s+([^\.]+)',
                    r'tendrá\s+la\s+obligación\s+de\s+([^\.]+)',
                    r'es\s+obligatorio\s+([^\.]+)',
                    r'debe\s+([^\.]+)',
                    r'está\s+obligado\s+a\s+([^\.]+)',
                    r'corresponde\s+([^\.]+)',
                    r'se\s+requiere\s+([^\.]+)'
                ],
                'criticality': 0.88
            },
            EntityType.DERECHO: {
                'patterns': [
                    r'derecho\s+a\s+([^\.]+)',
                    r'tiene\s+derecho\s+([^\.]+)',
                    r'podrá\s+([^\.]+)',
                    r'facultad\s+de\s+([^\.]+)',
                    r'se\s+reconoce\s+el\s+derecho\s+([^\.]+)',
                    r'está\s+autorizado\s+([^\.]+)'
                ],
                'criticality': 0.80
            },
            EntityType.PROCEDIMIENTO: {
                'patterns': [
                    r'procedimiento\s+([^\.]+)',
                    r'trámite\s+([^\.]+)',
                    r'proceso\s+de\s+([^\.]+)',
                    r'gestión\s+([^\.]+)',
                    r'solicitud\s+([^\.]+)',
                    r'presentación\s+de\s+([^\.]+)'
                ],
                'criticality': 0.75
            },
            EntityType.RESPONSABILIDAD: {
                'patterns': [
                    r'responsabilidad\s+([^\.]+)',
                    r'responderá\s+([^\.]+)',
                    r'será\s+responsable\s+([^\.]+)',
                    r'liability\s+([^\.]+)',
                    r'a\s+cargo\s+de\s+([^\.]+)'
                ],
                'criticality': 0.82
            },
            EntityType.EXCEPCION: {
                'patterns': [
                    r'excepto\s+([^\.]+)',
                    r'salvo\s+([^\.]+)',
                    r'no\s+se\s+aplica\s+([^\.]+)',
                    r'exención\s+([^\.]+)',
                    r'excluye\s+([^\.]+)',
                    r'no\s+corresponde\s+([^\.]+)'
                ],
                'criticality': 0.78
            }
        }
        
    def analyze_information_loss(self, 
                               original_text: str, 
                               summary: str,
                               target_preservation_rate: float = 0.85) -> ComplianceAnalysisResult:
        """
        Analyzes information loss between original text and summary
        
        Args:
            original_text: Full legal document
            summary: Summarized version
            target_preservation_rate: Minimum acceptable preservation rate
            
        Returns:
            Comprehensive compliance analysis results
        """
        
        # Extract legal entities from both texts
        original_entities = self._extract_legal_entities(original_text)
        summary_entities = self._extract_legal_entities(summary)
        
        # Calculate preservation rates by entity type
        preservation_rates = self._calculate_preservation_rates(
            original_entities, summary_entities
        )
        
        # Identify critical losses
        critical_losses = self._identify_critical_losses(
            original_entities, summary_entities
        )
        
        # Calculate compression ratio
        compression_ratio = len(summary.split()) / len(original_text.split())
        
        # Calculate safety threshold
        safety_threshold = self._calculate_safety_threshold(
            preservation_rates, target_preservation_rate
        )
        
        # Detailed analysis
        detailed_analysis = self._perform_detailed_analysis(
            original_text, summary, original_entities, summary_entities
        )
        
        # Overall preservation score (weighted by criticality)
        overall_preservation = self._calculate_weighted_preservation(
            preservation_rates, original_entities
        )
        
        return ComplianceAnalysisResult(
            overall_preservation=overall_preservation,
            entity_preservation=preservation_rates,
            critical_losses=critical_losses,
            compression_ratio=compression_ratio,
            safety_threshold=safety_threshold,
            detailed_analysis=detailed_analysis
        )
        
    def _extract_legal_entities(self, text: str) -> List[LegalEntity]:
        """Extract legal entities from text using pattern matching and NLP"""
        
        entities = []
        
        # Pattern-based extraction
        for entity_type, config in self.legal_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entity = LegalEntity(
                        text=match.group(0),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=self._get_context(text, match.start(), match.end()),
                        criticality_score=config['criticality']
                    )
                    entities.append(entity)
                    
        # NLP-based extraction (if available)
        if self.nlp:
            entities.extend(self._extract_nlp_entities(text))
            
        # Remove duplicates and sort by position
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x.start_pos)
        
        return entities
        
    def _extract_nlp_entities(self, text: str) -> List[LegalEntity]:
        """Extract entities using spaCy NLP model"""
        
        entities = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            # Map spaCy entity types to legal entity types
            entity_type = self._map_spacy_to_legal_type(ent.label_)
            
            if entity_type:
                entity = LegalEntity(
                    text=ent.text,
                    entity_type=entity_type,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    context=self._get_context(text, ent.start_char, ent.end_char),
                    criticality_score=self._calculate_nlp_criticality(ent)
                )
                entities.append(entity)
                
        return entities
        
    def _map_spacy_to_legal_type(self, spacy_label: str) -> EntityType:
        """Map spaCy entity labels to legal entity types"""
        
        mapping = {
            'MONEY': EntityType.MONTO,
            'DATE': EntityType.PLAZO,
            'TIME': EntityType.PLAZO,
            'PERCENT': EntityType.MONTO,
            'QUANTITY': EntityType.MONTO
        }
        
        return mapping.get(spacy_label, None)
        
    def _calculate_nlp_criticality(self, entity) -> float:
        """Calculate criticality score for NLP-extracted entities"""
        
        # Base criticality by entity type
        base_scores = {
            'MONEY': 0.85,
            'DATE': 0.90,
            'TIME': 0.90,
            'PERCENT': 0.75,
            'QUANTITY': 0.70
        }
        
        return base_scores.get(entity.label_, 0.60)
        
    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Get context around entity mention"""
        
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        return text[context_start:context_end]
        
    def _deduplicate_entities(self, entities: List[LegalEntity]) -> List[LegalEntity]:
        """Remove duplicate entities based on position and type"""
        
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.entity_type, entity.start_pos, entity.end_pos)
            
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
                
        return unique_entities
        
    def _calculate_preservation_rates(self, 
                                   original_entities: List[LegalEntity],
                                   summary_entities: List[LegalEntity]) -> Dict[str, float]:
        """Calculate preservation rates by entity type"""
        
        preservation_rates = {}
        
        # Count entities by type in original text
        original_counts = Counter(entity.entity_type for entity in original_entities)
        summary_counts = Counter(entity.entity_type for entity in summary_entities)
        
        for entity_type in EntityType:
            original_count = original_counts.get(entity_type, 0)
            summary_count = summary_counts.get(entity_type, 0)
            
            if original_count > 0:
                preservation_rate = min(summary_count / original_count, 1.0)
            else:
                preservation_rate = 1.0  # No entities to preserve
                
            preservation_rates[entity_type.value] = preservation_rate
            
        return preservation_rates
        
    def _identify_critical_losses(self, 
                                original_entities: List[LegalEntity],
                                summary_entities: List[LegalEntity]) -> List[str]:
        """Identify specific critical information that was lost"""
        
        critical_losses = []
        
        # Create summary entity texts for matching
        summary_texts = {entity.text.lower().strip() for entity in summary_entities}
        
        for original_entity in original_entities:
            # Consider entity critical if criticality > 0.8
            if original_entity.criticality_score > 0.8:
                
                # Check if similar entity exists in summary
                if not self._find_similar_entity(original_entity, summary_entities):
                    loss_description = (
                        f"Pérdida crítica ({original_entity.entity_type.value}): "
                        f"{original_entity.text[:100]}..."
                        f" [Criticidad: {original_entity.criticality_score:.2f}]"
                    )
                    critical_losses.append(loss_description)
                    
        return critical_losses
        
    def _find_similar_entity(self, 
                           target_entity: LegalEntity,
                           entities_list: List[LegalEntity]) -> bool:
        """Find if similar entity exists in list"""
        
        target_text = target_entity.text.lower().strip()
        target_type = target_entity.entity_type
        
        for entity in entities_list:
            if entity.entity_type == target_type:
                
                # Exact match
                if entity.text.lower().strip() == target_text:
                    return True
                    
                # Partial match for longer entities
                if len(target_text) > 20:
                    similarity = self._calculate_text_similarity(target_text, entity.text.lower())
                    if similarity > 0.7:
                        return True
                        
        return False
        
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        
        # Simple Jaccard similarity for now
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
        
    def _calculate_safety_threshold(self, 
                                  preservation_rates: Dict[str, float],
                                  target_rate: float) -> float:
        """Calculate safe compression ratio to maintain target preservation rate"""
        
        # Find the compression ratio that maintains target preservation
        # This is a simplified model - could be enhanced with regression analysis
        
        critical_types = [EntityType.SANCION.value, EntityType.PLAZO.value, EntityType.MONTO.value]
        
        critical_preservation = np.mean([
            preservation_rates.get(entity_type, 1.0) 
            for entity_type in critical_types
        ])
        
        if critical_preservation >= target_rate:
            return 0.28  # Research suggests 28% compression maintains 95% entities
        else:
            # Need higher ratio to maintain quality
            adjustment_factor = target_rate / critical_preservation if critical_preservation > 0 else 1.0
            return min(0.28 * adjustment_factor, 0.8)  # Cap at 80%
            
    def _perform_detailed_analysis(self, 
                                 original_text: str,
                                 summary: str,
                                 original_entities: List[LegalEntity],
                                 summary_entities: List[LegalEntity]) -> Dict[str, Any]:
        """Perform detailed analysis of compliance preservation"""
        
        analysis = {}
        
        # Entity distribution analysis
        analysis['entity_distribution'] = {
            'original': {entity_type.value: len([e for e in original_entities if e.entity_type == entity_type]) 
                        for entity_type in EntityType},
            'summary': {entity_type.value: len([e for e in summary_entities if e.entity_type == entity_type]) 
                       for entity_type in EntityType}
        }
        
        # Criticality analysis
        high_criticality_original = [e for e in original_entities if e.criticality_score > 0.8]
        high_criticality_summary = [e for e in summary_entities if e.criticality_score > 0.8]
        
        analysis['criticality_analysis'] = {
            'high_criticality_original_count': len(high_criticality_original),
            'high_criticality_summary_count': len(high_criticality_summary),
            'high_criticality_preservation': (
                len(high_criticality_summary) / len(high_criticality_original) 
                if high_criticality_original else 1.0
            )
        }
        
        # Position analysis (beginning vs end of document)
        text_length = len(original_text)
        beginning_entities = [e for e in original_entities if e.start_pos < text_length * 0.3]
        end_entities = [e for e in original_entities if e.start_pos > text_length * 0.7]
        
        analysis['position_analysis'] = {
            'beginning_entities': len(beginning_entities),
            'end_entities': len(end_entities),
            'middle_entities': len(original_entities) - len(beginning_entities) - len(end_entities)
        }
        
        # Semantic density analysis
        analysis['semantic_density'] = {
            'original_entities_per_100_words': len(original_entities) / (len(original_text.split()) / 100),
            'summary_entities_per_100_words': len(summary_entities) / (len(summary.split()) / 100),
            'relative_density_change': (
                (len(summary_entities) / len(summary.split())) / 
                (len(original_entities) / len(original_text.split()))
                if len(original_entities) > 0 and len(original_text.split()) > 0 else 0
            )
        }
        
        return analysis
        
    def _calculate_weighted_preservation(self, 
                                       preservation_rates: Dict[str, float],
                                       original_entities: List[LegalEntity]) -> float:
        """Calculate overall preservation weighted by entity criticality"""
        
        if not original_entities:
            return 1.0
            
        total_weight = 0.0
        weighted_sum = 0.0
        
        for entity_type in EntityType:
            # Count entities of this type
            type_entities = [e for e in original_entities if e.entity_type == entity_type]
            
            if type_entities:
                # Average criticality for this type
                avg_criticality = np.mean([e.criticality_score for e in type_entities])
                
                # Preservation rate for this type
                preservation_rate = preservation_rates.get(entity_type.value, 0.0)
                
                # Weight by number of entities and criticality
                weight = len(type_entities) * avg_criticality
                
                weighted_sum += preservation_rate * weight
                total_weight += weight
                
        return weighted_sum / total_weight if total_weight > 0 else 1.0
        
    def generate_compliance_report(self, analysis_result: ComplianceAnalysisResult) -> str:
        """Generate human-readable compliance report"""
        
        report = []
        
        report.append("# INFORME DE PRESERVACIÓN DE CUMPLIMIENTO LEGAL")
        report.append("=" * 50)
        
        # Overall assessment
        if analysis_result.overall_preservation >= 0.85:
            status = "✅ EXCELENTE"
        elif analysis_result.overall_preservation >= 0.70:
            status = "⚠️ ACEPTABLE"
        else:
            status = "❌ INSUFICIENTE"
            
        report.append(f"\n**Estado General**: {status}")
        report.append(f"**Preservación Global**: {analysis_result.overall_preservation:.1%}")
        report.append(f"**Ratio de Compresión**: {analysis_result.compression_ratio:.1%}")
        
        # Entity preservation by type
        report.append("\n## Preservación por Tipo de Entidad")
        report.append("-" * 35)
        
        for entity_type, rate in analysis_result.entity_preservation.items():
            status_icon = "✅" if rate >= 0.85 else "⚠️" if rate >= 0.70 else "❌"
            report.append(f"{status_icon} {entity_type:15} {rate:6.1%}")
            
        # Critical losses
        if analysis_result.critical_losses:
            report.append(f"\n## Pérdidas Críticas ({len(analysis_result.critical_losses)})")
            report.append("-" * 25)
            for loss in analysis_result.critical_losses[:5]:  # Show first 5
                report.append(f"• {loss}")
            if len(analysis_result.critical_losses) > 5:
                report.append(f"• ... y {len(analysis_result.critical_losses) - 5} más")
                
        # Recommendations
        report.append("\n## Recomendaciones")
        report.append("-" * 15)
        
        if analysis_result.overall_preservation < 0.85:
            report.append("• Aumentar el ratio de compresión de seguridad")
            report.append(f"• Ratio recomendado: {analysis_result.safety_threshold:.1%}")
            
        if analysis_result.critical_losses:
            report.append("• Revisar manualmente las pérdidas críticas identificadas")
            report.append("• Considerar post-procesamiento para recuperar información crítica")
            
        if analysis_result.compression_ratio < 0.2:
            report.append("• El resumen es muy agresivo - considerar mayor longitud")
            
        return "\n".join(report)