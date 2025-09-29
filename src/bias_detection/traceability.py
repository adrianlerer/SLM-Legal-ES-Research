"""
Legal Traceability Engine for SCM Legal System
Implements "cadena de custodia" for legal text summarization
Based on research: "Trazabilidad: cadena de custodia del párrafo"
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import logging
import json
from datetime import datetime

@dataclass
class AttributionResult:
    """Result of attribution analysis for a summary sentence"""
    summary_sentence: str
    source_sentences: List[Dict[str, Any]]
    attribution_score: float
    potential_hallucination: bool
    confidence_level: str

@dataclass
class TraceabilityReport:
    """Complete traceability analysis report"""
    overall_traceability: float
    hallucination_risk: float
    coverage_analysis: Dict[str, Any]
    attribution_map: Dict[str, AttributionResult]
    explainability_api: Dict[str, str]
    audit_metadata: Dict[str, Any]

class LegalTraceabilityEngine:
    """
    System for creating complete traceability between legal summaries and source text
    
    Key capabilities:
    - Sentence-level attribution mapping
    - Hallucination detection
    - Explainability API generation
    - Audit trail creation
    - Legal-specific context analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentence transformer for semantic similarity
        self.similarity_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Legal-specific patterns for enhanced context
        self.legal_markers = {
            'articles': r'artículo\s+\d+',
            'laws': r'ley\s+\d+',
            'decrees': r'decreto\s+\d+',
            'sections': r'sección\s+\d+',
            'paragraphs': r'párrafo\s+\d+',
            'clauses': r'cláusula\s+\d+'
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'hallucination': 0.3
        }
        
    def create_attribution_map(self, 
                             original_text: str, 
                             summary: str,
                             enable_audit: bool = True) -> TraceabilityReport:
        """
        Creates comprehensive attribution map between summary and original text
        
        Args:
            original_text: Full legal document
            summary: Generated summary
            enable_audit: Whether to generate audit metadata
            
        Returns:
            Complete traceability analysis report
        """
        
        # Segment texts into sentences
        original_sentences = self._segment_legal_text(original_text)
        summary_sentences = self._segment_legal_text(summary)
        
        # Generate embeddings
        self.logger.info("Generating embeddings for traceability analysis")
        original_embeddings = self.similarity_model.encode(original_sentences)
        summary_embeddings = self.similarity_model.encode(summary_sentences)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(summary_embeddings, original_embeddings)
        
        # Create attribution map
        attribution_map = {}
        
        for i, summary_sent in enumerate(summary_sentences):
            attribution_result = self._create_sentence_attribution(
                summary_sent, i, original_sentences, similarity_matrix[i]
            )
            attribution_map[f"summary_sent_{i}"] = attribution_result
            
        # Calculate overall metrics
        overall_traceability = self._calculate_overall_traceability(similarity_matrix)
        hallucination_risk = self._calculate_hallucination_risk(similarity_matrix)
        coverage_analysis = self._analyze_coverage(similarity_matrix, original_sentences)
        
        # Generate explainability API
        explainability_api = self._generate_explainability_api(attribution_map)
        
        # Generate audit metadata if enabled
        audit_metadata = {}
        if enable_audit:
            audit_metadata = self._generate_audit_metadata(
                original_text, summary, similarity_matrix, attribution_map
            )
            
        return TraceabilityReport(
            overall_traceability=overall_traceability,
            hallucination_risk=hallucination_risk,
            coverage_analysis=coverage_analysis,
            attribution_map=attribution_map,
            explainability_api=explainability_api,
            audit_metadata=audit_metadata
        )
        
    def _segment_legal_text(self, text: str) -> List[str]:
        """
        Segment legal text into meaningful sentences
        Handles legal-specific punctuation and formatting
        """
        
        # Clean text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Legal-specific sentence boundaries
        # Account for articles, sections, and legal numbering
        sentence_boundaries = [
            r'\.(?=\s+[A-Z])',  # Period followed by capitalized word
            r'\.(?=\s+Art)',     # Period before Article
            r'\.(?=\s+Artículo)', # Period before Artículo  
            r'\.(?=\s+\d+\.)',   # Period before numbered item
            r';(?=\s+[A-Z])',    # Semicolon before capital (legal lists)
        ]
        
        # Split text using legal boundaries
        sentences = [text]
        for boundary in sentence_boundaries:
            new_sentences = []
            for sent in sentences:
                new_sentences.extend(re.split(boundary, sent))
            sentences = new_sentences
            
        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
        
    def _create_sentence_attribution(self, 
                                   summary_sentence: str,
                                   sentence_index: int,
                                   original_sentences: List[str],
                                   similarity_scores: np.ndarray) -> AttributionResult:
        """Create attribution analysis for a single summary sentence"""
        
        # Find top 3 most similar source sentences
        top_indices = np.argsort(similarity_scores)[-3:][::-1]
        
        source_sentences = []
        for idx in top_indices:
            similarity_score = float(similarity_scores[idx])
            
            source_info = {
                'text': original_sentences[idx],
                'similarity': similarity_score,
                'position': int(idx),
                'confidence': self._calculate_attribution_confidence(similarity_score),
                'legal_markers': self._identify_legal_markers(original_sentences[idx]),
                'context_type': self._classify_legal_context(original_sentences[idx])
            }
            
            source_sentences.append(source_info)
            
        # Overall attribution score (best match)
        attribution_score = float(np.max(similarity_scores))
        
        # Determine if potential hallucination
        potential_hallucination = attribution_score < self.confidence_thresholds['hallucination']
        
        # Determine confidence level
        if attribution_score >= self.confidence_thresholds['high']:
            confidence_level = 'high'
        elif attribution_score >= self.confidence_thresholds['medium']:
            confidence_level = 'medium'
        elif attribution_score >= self.confidence_thresholds['low']:
            confidence_level = 'low'
        else:
            confidence_level = 'very_low'
            
        return AttributionResult(
            summary_sentence=summary_sentence,
            source_sentences=source_sentences,
            attribution_score=attribution_score,
            potential_hallucination=potential_hallucination,
            confidence_level=confidence_level
        )
        
    def _calculate_attribution_confidence(self, similarity_score: float) -> str:
        """Calculate human-readable confidence description"""
        
        if similarity_score >= self.confidence_thresholds['high']:
            return "Alta confianza - Correspondencia directa identificada"
        elif similarity_score >= self.confidence_thresholds['medium']:
            return "Confianza media - Parafraseo identificado"
        elif similarity_score >= self.confidence_thresholds['low']:
            return "Confianza baja - Relación temática identificada"
        else:
            return "Confianza muy baja - Posible alucinación"
            
    def _identify_legal_markers(self, text: str) -> List[str]:
        """Identify legal markers in text (articles, laws, etc.)"""
        
        markers = []
        
        for marker_type, pattern in self.legal_markers.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                markers.append(f"{marker_type}: {match}")
                
        return markers
        
    def _classify_legal_context(self, text: str) -> str:
        """Classify the type of legal content"""
        
        text_lower = text.lower()
        
        # Legal context patterns
        context_patterns = {
            'definition': ['define', 'entiende por', 'significa', 'comprende'],
            'obligation': ['deberá', 'obligación', 'debe', 'tendrá que'],
            'right': ['derecho', 'podrá', 'facultad', 'autorizado'],
            'sanction': ['sanción', 'multa', 'penalidad', 'infracción'],
            'procedure': ['procedimiento', 'trámite', 'proceso', 'solicitud'],
            'exception': ['excepto', 'salvo', 'excluye', 'no se aplica']
        }
        
        for context_type, patterns in context_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return context_type
                
        return 'general'
        
    def _calculate_overall_traceability(self, similarity_matrix: np.ndarray) -> float:
        """Calculate overall traceability score"""
        
        # Average of best matches for each summary sentence
        best_matches = np.max(similarity_matrix, axis=1)
        return float(np.mean(best_matches))
        
    def _calculate_hallucination_risk(self, similarity_matrix: np.ndarray) -> float:
        """Calculate risk of hallucination in summary"""
        
        # Percentage of sentences below hallucination threshold
        best_matches = np.max(similarity_matrix, axis=1)
        hallucinations = np.sum(best_matches < self.confidence_thresholds['hallucination'])
        
        return float(hallucinations / len(best_matches))
        
    def _analyze_coverage(self, 
                        similarity_matrix: np.ndarray,
                        original_sentences: List[str]) -> Dict[str, Any]:
        """Analyze how well the summary covers the original text"""
        
        # Which original sentences are covered by summary
        max_similarities_per_original = np.max(similarity_matrix, axis=0)
        covered_threshold = 0.5
        
        covered_sentences = np.sum(max_similarities_per_original >= covered_threshold)
        coverage_percentage = float(covered_sentences / len(original_sentences))
        
        # Distribution analysis
        coverage_distribution = {
            'high_coverage': np.sum(max_similarities_per_original >= 0.7),
            'medium_coverage': np.sum((max_similarities_per_original >= 0.5) & 
                                    (max_similarities_per_original < 0.7)),
            'low_coverage': np.sum((max_similarities_per_original >= 0.3) & 
                                 (max_similarities_per_original < 0.5)),
            'no_coverage': np.sum(max_similarities_per_original < 0.3)
        }
        
        # Identify uncovered critical sections
        uncovered_indices = np.where(max_similarities_per_original < covered_threshold)[0]
        uncovered_critical = []
        
        for idx in uncovered_indices:
            sentence = original_sentences[idx]
            if self._is_critical_legal_content(sentence):
                uncovered_critical.append({
                    'sentence': sentence[:100] + "...",
                    'position': int(idx),
                    'criticality_reason': self._explain_criticality(sentence)
                })
                
        return {
            'coverage_percentage': coverage_percentage,
            'covered_sentences': int(covered_sentences),
            'total_sentences': len(original_sentences),
            'coverage_distribution': coverage_distribution,
            'uncovered_critical_content': uncovered_critical,
            'coverage_gaps': self._identify_coverage_gaps(max_similarities_per_original)
        }
        
    def _is_critical_legal_content(self, sentence: str) -> bool:
        """Determine if sentence contains critical legal content"""
        
        critical_patterns = [
            r'artículo\s+\d+',
            r'deberá',
            r'obligación',
            r'sanción',
            r'multa',
            r'plazo',
            r'derecho',
            r'responsabilidad'
        ]
        
        sentence_lower = sentence.lower()
        return any(re.search(pattern, sentence_lower) for pattern in critical_patterns)
        
    def _explain_criticality(self, sentence: str) -> str:
        """Explain why sentence is considered critical"""
        
        sentence_lower = sentence.lower()
        
        if 'sanción' in sentence_lower or 'multa' in sentence_lower:
            return "Contiene información sobre sanciones"
        elif 'obligación' in sentence_lower or 'deberá' in sentence_lower:
            return "Define obligaciones legales"
        elif 'derecho' in sentence_lower:
            return "Establece derechos"
        elif 'plazo' in sentence_lower:
            return "Especifica plazos legales"
        elif 'artículo' in sentence_lower:
            return "Referencia a artículo específico"
        else:
            return "Contenido legal relevante"
            
    def _identify_coverage_gaps(self, similarities: np.ndarray) -> List[Dict[str, Any]]:
        """Identify significant gaps in coverage"""
        
        gaps = []
        gap_threshold = 0.3
        min_gap_length = 3
        
        # Find consecutive sequences of low coverage
        low_coverage_indices = np.where(similarities < gap_threshold)[0]
        
        if len(low_coverage_indices) == 0:
            return gaps
            
        # Group consecutive indices
        gap_start = low_coverage_indices[0]
        gap_end = gap_start
        
        for i in range(1, len(low_coverage_indices)):
            if low_coverage_indices[i] == low_coverage_indices[i-1] + 1:
                gap_end = low_coverage_indices[i]
            else:
                # End of current gap
                if gap_end - gap_start + 1 >= min_gap_length:
                    gaps.append({
                        'start_sentence': int(gap_start),
                        'end_sentence': int(gap_end),
                        'gap_length': int(gap_end - gap_start + 1),
                        'avg_similarity': float(np.mean(similarities[gap_start:gap_end+1]))
                    })
                    
                # Start new gap
                gap_start = low_coverage_indices[i]
                gap_end = gap_start
                
        # Check final gap
        if gap_end - gap_start + 1 >= min_gap_length:
            gaps.append({
                'start_sentence': int(gap_start),
                'end_sentence': int(gap_end),
                'gap_length': int(gap_end - gap_start + 1),
                'avg_similarity': float(np.mean(similarities[gap_start:gap_end+1]))
            })
            
        return gaps
        
    def _generate_explainability_api(self, 
                                   attribution_map: Dict[str, AttributionResult]) -> Dict[str, str]:
        """Generate human-readable explanations for each summary sentence"""
        
        explanations = {}
        
        for sentence_id, attribution in attribution_map.items():
            explanation = self._create_sentence_explanation(attribution)
            explanations[sentence_id] = explanation
            
        return explanations
        
    def _create_sentence_explanation(self, attribution: AttributionResult) -> str:
        """Create explanation for a single sentence attribution"""
        
        if attribution.potential_hallucination:
            return (
                f"⚠️ ADVERTENCIA: Esta oración puede contener información no respaldada "
                f"por el texto original (confianza: {attribution.attribution_score:.2f}). "
                f"Se recomienda revisión manual."
            )
            
        # Get top 2 sources
        sources = attribution.source_sentences[:2]
        
        explanation_parts = [
            f"📄 **Trazabilidad ({attribution.confidence_level.upper()}):**",
            f"Esta información se basa en {len(sources)} fuente(s):\n"
        ]
        
        for i, source in enumerate(sources, 1):
            similarity_pct = source['similarity'] * 100
            
            # Add legal markers if present
            markers_text = ""
            if source['legal_markers']:
                markers_text = f" [{', '.join(source['legal_markers'])}]"
                
            explanation_parts.append(
                f"{i}. **Posición {source['position']}** "
                f"(similitud: {similarity_pct:.1f}%){markers_text}\n"
                f"   \"{source['text'][:150]}...\"\n"
            )
            
        # Add context information
        if sources:
            context_type = sources[0]['context_type']
            explanation_parts.append(
                f"**Tipo de contenido:** {context_type.title()}"
            )
            
        return "\n".join(explanation_parts)
        
    def _generate_audit_metadata(self, 
                               original_text: str,
                               summary: str,
                               similarity_matrix: np.ndarray,
                               attribution_map: Dict[str, AttributionResult]) -> Dict[str, Any]:
        """Generate comprehensive audit metadata"""
        
        metadata = {
            'analysis_timestamp': datetime.now().isoformat(),
            'model_version': 'paraphrase-multilingual-MiniLM-L12-v2',
            'input_metadata': {
                'original_length_chars': len(original_text),
                'original_length_words': len(original_text.split()),
                'summary_length_chars': len(summary),
                'summary_length_words': len(summary.split()),
                'compression_ratio': len(summary.split()) / len(original_text.split())
            },
            'traceability_statistics': {
                'total_summary_sentences': similarity_matrix.shape[0],
                'total_original_sentences': similarity_matrix.shape[1],
                'high_confidence_attributions': sum(
                    1 for attr in attribution_map.values() 
                    if attr.confidence_level == 'high'
                ),
                'potential_hallucinations': sum(
                    1 for attr in attribution_map.values() 
                    if attr.potential_hallucination
                ),
                'average_attribution_score': float(np.mean([
                    attr.attribution_score for attr in attribution_map.values()
                ]))
            },
            'legal_content_analysis': self._analyze_legal_content_preservation(attribution_map),
            'quality_indicators': {
                'traceability_threshold_met': all(
                    attr.attribution_score >= self.confidence_thresholds['low']
                    for attr in attribution_map.values()
                ),
                'hallucination_risk_acceptable': sum(
                    1 for attr in attribution_map.values() 
                    if attr.potential_hallucination
                ) / len(attribution_map) < 0.1,
                'legal_markers_preserved': self._check_legal_markers_preservation(attribution_map)
            }
        }
        
        return metadata
        
    def _analyze_legal_content_preservation(self, 
                                          attribution_map: Dict[str, AttributionResult]) -> Dict[str, Any]:
        """Analyze preservation of different types of legal content"""
        
        content_types = {
            'definition': 0,
            'obligation': 0,
            'right': 0,
            'sanction': 0,
            'procedure': 0,
            'exception': 0,
            'general': 0
        }
        
        preserved_content = {content_type: 0 for content_type in content_types}
        
        for attribution in attribution_map.values():
            if attribution.source_sentences:
                source = attribution.source_sentences[0]
                content_type = source['context_type']
                
                content_types[content_type] += 1
                
                # Consider preserved if attribution score is acceptable
                if attribution.attribution_score >= self.confidence_thresholds['low']:
                    preserved_content[content_type] += 1
                    
        preservation_rates = {}
        for content_type in content_types:
            if content_types[content_type] > 0:
                preservation_rates[content_type] = (
                    preserved_content[content_type] / content_types[content_type]
                )
            else:
                preservation_rates[content_type] = 1.0
                
        return {
            'content_distribution': content_types,
            'preservation_rates': preservation_rates,
            'overall_legal_preservation': np.mean(list(preservation_rates.values()))
        }
        
    def _check_legal_markers_preservation(self, 
                                        attribution_map: Dict[str, AttributionResult]) -> Dict[str, Any]:
        """Check if legal markers (articles, laws) are properly preserved"""
        
        markers_found = 0
        markers_preserved = 0
        
        for attribution in attribution_map.values():
            for source in attribution.source_sentences:
                if source['legal_markers']:
                    markers_found += len(source['legal_markers'])
                    
                    # Check if attribution is strong enough
                    if attribution.attribution_score >= self.confidence_thresholds['medium']:
                        markers_preserved += len(source['legal_markers'])
                        
        preservation_rate = markers_preserved / markers_found if markers_found > 0 else 1.0
        
        return {
            'total_markers_found': markers_found,
            'markers_preserved': markers_preserved,
            'preservation_rate': preservation_rate,
            'preservation_acceptable': preservation_rate >= 0.8
        }
        
    def generate_audit_report(self, traceability_report: TraceabilityReport) -> str:
        """Generate comprehensive audit report"""
        
        report_lines = []
        
        report_lines.append("# INFORME DE AUDITORÍA - TRAZABILIDAD LEGAL")
        report_lines.append("=" * 55)
        
        # Executive summary
        report_lines.append(f"\n## Resumen Ejecutivo")
        report_lines.append(f"**Trazabilidad General**: {traceability_report.overall_traceability:.1%}")
        report_lines.append(f"**Riesgo de Alucinación**: {traceability_report.hallucination_risk:.1%}")
        
        # Quality assessment
        if traceability_report.overall_traceability >= 0.8:
            quality_status = "✅ EXCELENTE"
        elif traceability_report.overall_traceability >= 0.6:
            quality_status = "⚠️ ACEPTABLE"
        else:
            quality_status = "❌ INSUFICIENTE"
            
        report_lines.append(f"**Estado de Calidad**: {quality_status}")
        
        # Coverage analysis
        coverage = traceability_report.coverage_analysis
        report_lines.append(f"\n## Análisis de Cobertura")
        report_lines.append(f"**Cobertura del Texto Original**: {coverage['coverage_percentage']:.1%}")
        report_lines.append(f"**Oraciones Cubiertas**: {coverage['covered_sentences']}/{coverage['total_sentences']}")
        
        # Critical content not covered
        if coverage['uncovered_critical_content']:
            report_lines.append(f"\n### Contenido Crítico No Cubierto ({len(coverage['uncovered_critical_content'])} elementos)")
            for item in coverage['uncovered_critical_content'][:3]:
                report_lines.append(f"• **Posición {item['position']}**: {item['criticality_reason']}")
                report_lines.append(f"  \"{item['sentence']}\"")
                
        # Hallucination alerts
        hallucinations = [
            attr for attr in traceability_report.attribution_map.values() 
            if attr.potential_hallucination
        ]
        
        if hallucinations:
            report_lines.append(f"\n## ⚠️ Alertas de Posibles Alucinaciones ({len(hallucinations)})")
            for i, attr in enumerate(hallucinations[:3], 1):
                report_lines.append(f"{i}. \"{attr.summary_sentence[:100]}...\"")
                report_lines.append(f"   Confianza: {attr.attribution_score:.2f}")
                
        # Recommendations
        report_lines.append(f"\n## Recomendaciones")
        
        if traceability_report.hallucination_risk > 0.1:
            report_lines.append("• **CRÍTICO**: Revisar manualmente oraciones con baja trazabilidad")
            
        if traceability_report.overall_traceability < 0.7:
            report_lines.append("• Considerar métodos de resumen más conservadores")
            
        if coverage['coverage_percentage'] < 0.6:
            report_lines.append("• Aumentar longitud del resumen para mejor cobertura")
            
        if not coverage['uncovered_critical_content']:
            report_lines.append("• ✅ Todo el contenido crítico está adecuadamente cubierto")
            
        report_lines.append(f"\n---")
        report_lines.append(f"*Informe generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(report_lines)