"""
Legal Concept Extractor - Advanced concept identification for SCM Legal
Real implementation for academic research publication

This module implements sophisticated legal concept extraction that goes beyond
simple keyword matching to semantic concept identification and hierarchical reasoning.
"""

import re
import json
import spacy
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Union
from dataclasses import dataclass
from collections import defaultdict, Counter
import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

@dataclass
class LegalConcept:
    """Enhanced legal concept with hierarchical relationships"""
    id: str
    name: str
    category: str
    subcategory: str
    definition: str
    keywords: List[str]
    synonyms: List[str]
    related_concepts: List[str]
    parent_concepts: List[str]
    child_concepts: List[str]
    jurisdiction: List[str]
    confidence_threshold: float
    semantic_embedding: Optional[np.ndarray] = None
    legal_weight: float = 1.0
    frequency_score: float = 0.0

@dataclass  
class ConceptMatch:
    """Result of concept matching in text"""
    concept_id: str
    concept_name: str
    text_span: str
    start_pos: int
    end_pos: int
    confidence: float
    matching_method: str  # 'exact', 'semantic', 'pattern', 'contextual'
    context: str
    legal_relevance: float

class LegalConceptExtractor:
    """
    Advanced Legal Concept Extractor for SCM training
    
    Features:
    - Multi-jurisdictional concept recognition (AR, CL, UY, ES)
    - Hierarchical concept relationships
    - Semantic similarity matching
    - Contextual legal reasoning
    - Concept graph construction
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_nlp_models()
        self.load_legal_ontology()
        self.build_concept_graph()
        
    def setup_nlp_models(self):
        """Initialize NLP models for concept processing"""
        
        logger.info("Loading NLP models...")
        
        # SpaCy model for Spanish legal text
        try:
            self.nlp = spacy.load("es_core_news_lg")
        except OSError:
            logger.warning("Spanish model not found, using small model")
            self.nlp = spacy.load("es_core_news_sm")
            
        # Sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Legal entity recognition patterns
        self.setup_legal_patterns()
        
    def setup_legal_patterns(self):
        """Set up regex patterns for legal entity recognition"""
        
        self.legal_patterns = {
            'codigo_civil': [
                r'C[óo]digo Civil',
                r'CC(?:\s+Art[íi]culo)?\s*\d+',
                r'Art[íi]culo\s+\d+\s+del\s+C[óo]digo\s+Civil'
            ],
            'ley_sociedades': [
                r'Ley\s+(?:de\s+)?Sociedades?\s+Comerciales?',
                r'LSC\s+Art[íi]culo\s*\d+',
                r'Ley\s+19\.550'
            ],
            'contrato': [
                r'contrato\s+de\s+\w+',
                r'acuerdo\s+contractual',
                r'cl[áa]usula\s+\d+'
            ],
            'sociedad_anonima': [
                r'[Ss]ociedad\s+An[óo]nima',
                r'S\.A\.',
                r'SA\b'
            ],
            'responsabilidad_civil': [
                r'responsabilidad\s+civil',
                r'da[ñn]os?\s+y\s+perjuicios?',
                r'reparaci[óo]n\s+del\s+da[ñn]o'
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {}
        for concept, patterns in self.legal_patterns.items():
            self.compiled_patterns[concept] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def load_legal_ontology(self):
        """Load comprehensive legal ontology"""
        
        logger.info("Loading legal ontology...")
        
        # Expanded legal ontology based on Argentine, Chilean, Uruguayan, and Spanish law
        self.legal_ontology = {
            # Constitutional Law
            'derechos_fundamentales': LegalConcept(
                id='const_001',
                name='Derechos Fundamentales',
                category='constitutional',
                subcategory='derechos_humanos',
                definition='Derechos inherentes a la persona humana reconocidos constitucionalmente',
                keywords=['derechos fundamentales', 'garantías constitucionales', 'derechos humanos'],
                synonyms=['derechos constitucionales', 'garantías individuales'],
                related_concepts=['debido_proceso', 'igualdad_ante_ley'],
                parent_concepts=[],
                child_concepts=['derecho_vida', 'libertad_expresion', 'propiedad_privada'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.8,
                legal_weight=0.95
            ),
            
            'debido_proceso': LegalConcept(
                id='const_002',
                name='Debido Proceso',
                category='constitutional',
                subcategory='garantias_procesales',
                definition='Garantía de un proceso judicial justo y equitativo',
                keywords=['debido proceso', 'garantías procesales', 'defensa en juicio'],
                synonyms=['proceso justo', 'tutela judicial efectiva'],
                related_concepts=['derechos_fundamentales', 'defensa_tecnica'],
                parent_concepts=['derechos_fundamentales'],
                child_concepts=['derecho_defensa', 'presuncion_inocencia'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.85,
                legal_weight=0.9
            ),
            
            # Civil Law
            'contrato_compraventa': LegalConcept(
                id='civil_001', 
                name='Contrato de Compraventa',
                category='civil',
                subcategory='contratos',
                definition='Contrato por el cual una parte se obliga a transferir la propiedad de una cosa y la otra a pagar un precio',
                keywords=['compraventa', 'contrato compraventa', 'venta', 'compra'],
                synonyms=['contrato de venta', 'venta'],
                related_concepts=['consentimiento', 'objeto_contractual', 'precio'],
                parent_concepts=['contrato'],
                child_concepts=['tradicion', 'entrega_cosa', 'pago_precio'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.8,
                legal_weight=0.85
            ),
            
            'consentimiento': LegalConcept(
                id='civil_002',
                name='Consentimiento',
                category='civil', 
                subcategory='elementos_contractuales',
                definition='Acuerdo de voluntades libre y consciente para la formación del contrato',
                keywords=['consentimiento', 'voluntad', 'acuerdo', 'consenso'],
                synonyms=['acuerdo de voluntades', 'consenso mutuo'],
                related_concepts=['capacidad', 'vicios_voluntad', 'objeto_contractual'],
                parent_concepts=['elementos_esenciales_contrato'],
                child_concepts=['oferta', 'aceptacion'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.75,
                legal_weight=0.9
            ),
            
            'responsabilidad_civil': LegalConcept(
                id='civil_003',
                name='Responsabilidad Civil',
                category='civil',
                subcategory='obligaciones',
                definition='Obligación de reparar el daño causado por acción u omisión',
                keywords=['responsabilidad civil', 'daños perjuicios', 'reparación', 'indemnización'],
                synonyms=['responsabilidad extracontractual', 'reparación civil'],
                related_concepts=['dano', 'culpa', 'nexo_causal', 'factor_atribucion'],
                parent_concepts=['obligaciones'],
                child_concepts=['dano_moral', 'dano_material', 'lucro_cesante'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.8,
                legal_weight=0.88
            ),
            
            # Commercial Law
            'sociedad_anonima': LegalConcept(
                id='comm_001',
                name='Sociedad Anónima',
                category='commercial',
                subcategory='tipos_societarios',
                definition='Sociedad de capital donde la responsabilidad se limita al capital aportado',
                keywords=['sociedad anónima', 'SA', 'sociedad de capital'],
                synonyms=['compañía anónima', 'corporación'],
                related_concepts=['capital_social', 'accionistas', 'directorio'],
                parent_concepts=['persona_juridica'],
                child_concepts=['acciones', 'dividendos', 'junta_accionistas'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.85,
                legal_weight=0.9
            ),
            
            'gobierno_corporativo': LegalConcept(
                id='comm_002',
                name='Gobierno Corporativo',
                category='commercial',
                subcategory='administracion_societaria',
                definition='Sistema de dirección y control de las sociedades comerciales',
                keywords=['gobierno corporativo', 'corporate governance', 'administración societaria'],
                synonyms=['gobernanza empresarial', 'control corporativo'],
                related_concepts=['directorio', 'sindicos', 'auditoria_interna'],
                parent_concepts=['administracion_societaria'],
                child_concepts=['comite_auditoria', 'politicas_corporativas'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.8,
                legal_weight=0.85
            ),
            
            # Labor Law
            'contrato_trabajo': LegalConcept(
                id='labor_001',
                name='Contrato de Trabajo',
                category='labor',
                subcategory='relacion_laboral',
                definition='Acuerdo por el cual una persona se obliga a prestar servicios bajo dependencia',
                keywords=['contrato trabajo', 'relación laboral', 'empleado', 'trabajador'],
                synonyms=['contrato laboral', 'vínculo laboral'],
                related_concepts=['subordinacion', 'remuneracion', 'prestacion_servicios'],
                parent_concepts=['derecho_trabajo'],
                child_concepts=['salario', 'jornada_laboral', 'descansos'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.8,
                legal_weight=0.85
            ),
            
            # Administrative Law
            'acto_administrativo': LegalConcept(
                id='admin_001',
                name='Acto Administrativo',
                category='administrative',
                subcategory='procedimiento_administrativo',
                definition='Declaración unilateral de voluntad de la Administración Pública',
                keywords=['acto administrativo', 'resolución administrativa', 'decisión administrativa'],
                synonyms=['resolución estatal', 'decisión pública'],
                related_concepts=['procedimiento_administrativo', 'debido_proceso_adm'],
                parent_concepts=['derecho_administrativo'],
                child_concepts=['notificacion', 'recursos_administrativos'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.82,
                legal_weight=0.8
            ),
            
            # Compliance and Risk Management
            'compliance_normativo': LegalConcept(
                id='comp_001',
                name='Compliance Normativo',
                category='compliance',
                subcategory='cumplimiento_regulatorio',
                definition='Cumplimiento de normativas y regulaciones aplicables a la organización',
                keywords=['compliance', 'cumplimiento normativo', 'programa integridad'],
                synonyms=['cumplimiento regulatorio', 'programa de compliance'],
                related_concepts=['riesgo_regulatorio', 'auditoria_compliance'],
                parent_concepts=['gestion_riesgo'],
                child_concepts=['politicas_compliance', 'monitoreo_cumplimiento'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.85,
                legal_weight=0.88
            ),
            
            'gestion_riesgo': LegalConcept(
                id='risk_001',
                name='Gestión de Riesgo',
                category='compliance',
                subcategory='risk_management',
                definition='Proceso sistemático de identificación, evaluación y tratamiento de riesgos',
                keywords=['gestión riesgo', 'risk management', 'administración riesgos'],
                synonyms=['manejo de riesgos', 'control de riesgos'],
                related_concepts=['identificacion_riesgo', 'evaluacion_riesgo', 'mitigacion_riesgo'],
                parent_concepts=['governance'],
                child_concepts=['matriz_riesgo', 'controles_internos'],
                jurisdiction=['argentina', 'chile', 'uruguay', 'españa'],
                confidence_threshold=0.8,
                legal_weight=0.82
            )
        }
        
        # Pre-compute semantic embeddings for all concepts
        self._compute_concept_embeddings()
        
    def _compute_concept_embeddings(self):
        """Pre-compute semantic embeddings for all legal concepts"""
        
        logger.info("Computing concept embeddings...")
        
        for concept_id, concept in self.legal_ontology.items():
            # Create comprehensive text representation
            concept_text = f"{concept.name} {concept.definition} {' '.join(concept.keywords)} {' '.join(concept.synonyms)}"
            
            # Compute embedding
            embedding = self.sentence_model.encode([concept_text])[0]
            concept.semantic_embedding = embedding
            
    def build_concept_graph(self):
        """Build hierarchical concept relationship graph"""
        
        logger.info("Building concept relationship graph...")
        
        self.concept_graph = nx.DiGraph()
        
        # Add all concepts as nodes
        for concept_id, concept in self.legal_ontology.items():
            self.concept_graph.add_node(
                concept_id,
                name=concept.name,
                category=concept.category,
                weight=concept.legal_weight
            )
            
        # Add relationships as edges
        for concept_id, concept in self.legal_ontology.items():
            # Parent-child relationships
            for parent_id in concept.parent_concepts:
                if parent_id in self.legal_ontology:
                    self.concept_graph.add_edge(parent_id, concept_id, relation='parent_child')
                    
            # Related concept relationships  
            for related_id in concept.related_concepts:
                if related_id in self.legal_ontology:
                    self.concept_graph.add_edge(concept_id, related_id, relation='related')
    
    def extract_concepts(self, text: str, jurisdiction: str = 'argentina') -> List[ConceptMatch]:
        """
        Extract legal concepts from text using multiple methods
        
        Args:
            text: Legal text to analyze
            jurisdiction: Legal jurisdiction context
            
        Returns:
            List of concept matches with confidence scores
        """
        
        concept_matches = []
        
        # Method 1: Exact keyword matching
        keyword_matches = self._extract_by_keywords(text, jurisdiction)
        concept_matches.extend(keyword_matches)
        
        # Method 2: Regex pattern matching
        pattern_matches = self._extract_by_patterns(text, jurisdiction)
        concept_matches.extend(pattern_matches)
        
        # Method 3: Semantic similarity matching
        semantic_matches = self._extract_by_semantics(text, jurisdiction)
        concept_matches.extend(semantic_matches)
        
        # Method 4: Contextual NLP analysis
        contextual_matches = self._extract_by_context(text, jurisdiction)
        concept_matches.extend(contextual_matches)
        
        # Deduplicate and rank matches
        final_matches = self._deduplicate_and_rank(concept_matches, text)
        
        return final_matches
    
    def _extract_by_keywords(self, text: str, jurisdiction: str) -> List[ConceptMatch]:
        """Extract concepts using exact keyword matching"""
        
        matches = []
        text_lower = text.lower()
        
        for concept_id, concept in self.legal_ontology.items():
            # Skip if jurisdiction doesn't match
            if jurisdiction not in concept.jurisdiction:
                continue
                
            # Check all keywords and synonyms
            all_terms = concept.keywords + concept.synonyms
            
            for term in all_terms:
                term_lower = term.lower()
                
                # Find all occurrences
                start = 0
                while True:
                    pos = text_lower.find(term_lower, start)
                    if pos == -1:
                        break
                        
                    # Extract context around match
                    context_start = max(0, pos - 50)
                    context_end = min(len(text), pos + len(term) + 50)
                    context = text[context_start:context_end]
                    
                    match = ConceptMatch(
                        concept_id=concept_id,
                        concept_name=concept.name,
                        text_span=text[pos:pos+len(term)],
                        start_pos=pos,
                        end_pos=pos + len(term),
                        confidence=0.9,  # High confidence for exact matches
                        matching_method='exact',
                        context=context,
                        legal_relevance=concept.legal_weight
                    )
                    
                    matches.append(match)
                    start = pos + 1
                    
        return matches
    
    def _extract_by_patterns(self, text: str, jurisdiction: str) -> List[ConceptMatch]:
        """Extract concepts using regex patterns"""
        
        matches = []
        
        for concept_id, patterns in self.compiled_patterns.items():
            # Check if concept exists in ontology and matches jurisdiction
            if concept_id not in self.legal_ontology:
                continue
                
            concept = self.legal_ontology[concept_id]
            if jurisdiction not in concept.jurisdiction:
                continue
                
            for pattern in patterns:
                for match in pattern.finditer(text):
                    # Extract context
                    start_pos = match.start()
                    end_pos = match.end()
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(text), end_pos + 50)
                    context = text[context_start:context_end]
                    
                    concept_match = ConceptMatch(
                        concept_id=concept_id,
                        concept_name=concept.name,
                        text_span=match.group(),
                        start_pos=start_pos,
                        end_pos=end_pos,
                        confidence=0.85,  # Good confidence for pattern matches
                        matching_method='pattern',
                        context=context,
                        legal_relevance=concept.legal_weight
                    )
                    
                    matches.append(concept_match)
                    
        return matches
    
    def _extract_by_semantics(self, text: str, jurisdiction: str) -> List[ConceptMatch]:
        """Extract concepts using semantic similarity"""
        
        matches = []
        
        # Split text into sentences for better semantic analysis
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        
        if not sentences:
            return matches
            
        # Compute sentence embeddings
        sentence_embeddings = self.sentence_model.encode(sentences)
        
        for concept_id, concept in self.legal_ontology.items():
            # Skip if jurisdiction doesn't match
            if jurisdiction not in concept.jurisdiction:
                continue
                
            if concept.semantic_embedding is None:
                continue
                
            # Compute similarity with each sentence
            similarities = cosine_similarity(
                [concept.semantic_embedding], 
                sentence_embeddings
            )[0]
            
            # Find sentences above threshold
            threshold = concept.confidence_threshold
            
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    sentence = sentences[i]
                    
                    # Find sentence position in original text
                    sentence_pos = text.find(sentence)
                    if sentence_pos == -1:
                        continue
                        
                    match = ConceptMatch(
                        concept_id=concept_id,
                        concept_name=concept.name,
                        text_span=sentence,
                        start_pos=sentence_pos,
                        end_pos=sentence_pos + len(sentence),
                        confidence=float(similarity),
                        matching_method='semantic',
                        context=sentence,
                        legal_relevance=concept.legal_weight
                    )
                    
                    matches.append(match)
                    
        return matches
    
    def _extract_by_context(self, text: str, jurisdiction: str) -> List[ConceptMatch]:
        """Extract concepts using contextual NLP analysis"""
        
        matches = []
        
        # Process text with SpaCy
        doc = self.nlp(text)
        
        # Look for legal entities and noun phrases
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PERSON', 'MISC']:
                # Check if entity matches any concept
                entity_text = ent.text.lower()
                
                for concept_id, concept in self.legal_ontology.items():
                    if jurisdiction not in concept.jurisdiction:
                        continue
                        
                    # Check if entity matches concept keywords
                    for keyword in concept.keywords:
                        if keyword.lower() in entity_text or entity_text in keyword.lower():
                            # Extract broader context
                            sent = ent.sent
                            
                            match = ConceptMatch(
                                concept_id=concept_id,
                                concept_name=concept.name,
                                text_span=ent.text,
                                start_pos=ent.start_char,
                                end_pos=ent.end_char,
                                confidence=0.7,  # Lower confidence for contextual matches
                                matching_method='contextual',
                                context=sent.text,
                                legal_relevance=concept.legal_weight
                            )
                            
                            matches.append(match)
                            break
                            
        return matches
    
    def _deduplicate_and_rank(self, matches: List[ConceptMatch], text: str) -> List[ConceptMatch]:
        """Remove duplicates and rank matches by relevance"""
        
        if not matches:
            return []
            
        # Group matches by concept and overlapping positions
        concept_groups = defaultdict(list)
        
        for match in matches:
            key = f"{match.concept_id}_{match.start_pos//10}"  # Group nearby positions
            concept_groups[key].append(match)
            
        # Select best match from each group
        final_matches = []
        
        for group_matches in concept_groups.values():
            # Sort by confidence * legal_relevance
            group_matches.sort(
                key=lambda x: x.confidence * x.legal_relevance, 
                reverse=True
            )
            
            # Take the best match
            final_matches.append(group_matches[0])
            
        # Sort final matches by position in text
        final_matches.sort(key=lambda x: x.start_pos)
        
        # Limit to max concepts per text
        max_concepts = self.config.get('max_concepts_per_text', 20)
        
        return final_matches[:max_concepts]
    
    def get_concept_relationships(self, concept_ids: List[str]) -> Dict[str, List[str]]:
        """Get relationships between extracted concepts"""
        
        relationships = {
            'hierarchical': [],
            'related': [], 
            'conflicting': []
        }
        
        for i, concept1_id in enumerate(concept_ids):
            for concept2_id in concept_ids[i+1:]:
                
                # Check direct relationships in graph
                if self.concept_graph.has_edge(concept1_id, concept2_id):
                    edge_data = self.concept_graph.get_edge_data(concept1_id, concept2_id)
                    relation_type = edge_data.get('relation', 'related')
                    
                    if relation_type == 'parent_child':
                        relationships['hierarchical'].append((concept1_id, concept2_id))
                    else:
                        relationships['related'].append((concept1_id, concept2_id))
                        
                elif self.concept_graph.has_edge(concept2_id, concept1_id):
                    edge_data = self.concept_graph.get_edge_data(concept2_id, concept1_id)
                    relation_type = edge_data.get('relation', 'related')
                    
                    if relation_type == 'parent_child':
                        relationships['hierarchical'].append((concept2_id, concept1_id))
                    else:
                        relationships['related'].append((concept2_id, concept1_id))
                        
        return relationships
    
    def analyze_concept_coherence(self, matches: List[ConceptMatch]) -> Dict[str, float]:
        """Analyze coherence and consistency of extracted concepts"""
        
        if len(matches) < 2:
            return {'coherence_score': 1.0, 'consistency_score': 1.0}
            
        concept_ids = [match.concept_id for match in matches]
        
        # Calculate semantic coherence using embeddings
        embeddings = []
        for concept_id in concept_ids:
            if concept_id in self.legal_ontology:
                concept = self.legal_ontology[concept_id]
                if concept.semantic_embedding is not None:
                    embeddings.append(concept.semantic_embedding)
                    
        if len(embeddings) < 2:
            return {'coherence_score': 1.0, 'consistency_score': 1.0}
            
        # Compute pairwise similarities
        similarity_matrix = cosine_similarity(embeddings)
        
        # Average similarity (excluding diagonal)
        mask = np.ones_like(similarity_matrix, dtype=bool)
        np.fill_diagonal(mask, False)
        coherence_score = np.mean(similarity_matrix[mask])
        
        # Consistency score based on jurisdictional alignment
        jurisdictions = []
        for concept_id in concept_ids:
            if concept_id in self.legal_ontology:
                jurisdictions.extend(self.legal_ontology[concept_id].jurisdiction)
                
        jurisdiction_counter = Counter(jurisdictions)
        most_common_jurisdiction = jurisdiction_counter.most_common(1)[0][1] if jurisdiction_counter else 0
        consistency_score = most_common_jurisdiction / len(jurisdictions) if jurisdictions else 1.0
        
        return {
            'coherence_score': float(coherence_score),
            'consistency_score': float(consistency_score),
            'dominant_jurisdiction': jurisdiction_counter.most_common(1)[0][0] if jurisdiction_counter else 'unknown'
        }

def main():
    """Test the concept extractor"""
    
    # Example configuration
    config = {
        'min_concept_frequency': 5,
        'max_concepts_per_text': 20,
        'concept_similarity_threshold': 0.75
    }
    
    # Initialize extractor
    extractor = LegalConceptExtractor(config)
    
    # Test text
    test_text = """
    El contrato de compraventa requiere el consentimiento libre y consciente de ambas partes 
    para ser considerado válido según el Código Civil argentino. La sociedad anónima debe 
    constituir reservas legales conforme a la Ley de Sociedades Comerciales. El debido proceso 
    es una garantía fundamental que debe respetarse en todo procedimiento judicial o administrativo.
    """
    
    # Extract concepts
    matches = extractor.extract_concepts(test_text, jurisdiction='argentina')
    
    # Print results
    print("Conceptos extraídos:")
    for match in matches:
        print(f"- {match.concept_name} (Confianza: {match.confidence:.2f}, Método: {match.matching_method})")
        print(f"  Texto: '{match.text_span}'")
        print(f"  Contexto: ...{match.context}...")
        print()
        
    # Analyze coherence
    coherence = extractor.analyze_concept_coherence(matches)
    print(f"Coherencia conceptual: {coherence}")

if __name__ == "__main__":
    main()