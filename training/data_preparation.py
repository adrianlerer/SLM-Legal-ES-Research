"""
Legal Data Preparation Pipeline for SCM Training
Academic research implementation for paper publication

This module implements comprehensive data preprocessing for legal corpus,
including concept annotation, reasoning chain generation, and multi-jurisdictional dataset creation.
"""

import os
import json
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import logging
from collections import defaultdict, Counter
import spacy
from sklearn.model_selection import train_test_split
import requests
from bs4 import BeautifulSoup
import time
import random

# Custom imports
from concept_extractor import LegalConceptExtractor, LegalConcept, ConceptMatch
from concept_reasoner import ConceptualReasoningEngine, ReasoningChain, ReasoningType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegalDocument:
    """Legal document structure for processing"""
    doc_id: str
    title: str
    content: str
    source: str
    jurisdiction: str
    legal_category: str
    date_created: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnnotatedSample:
    """Annotated training sample with concepts and reasoning"""
    text: str
    concepts: List[str]
    reasoning_chain: List[Dict[str, str]]
    jurisdiction: str
    legal_category: str
    ground_truth_answer: Optional[str] = None
    confidence_score: float = 1.0
    source_document: str = ""

class LegalCorpusBuilder:
    """
    Comprehensive legal corpus builder for SCM training
    
    Features:
    - Multi-jurisdictional legal text collection
    - Automated concept annotation
    - Reasoning chain generation  
    - Data augmentation techniques
    - Quality validation and filtering
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'data'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize NLP components
        self.setup_nlp_components()
        
        # Legal sources for each jurisdiction
        self.setup_legal_sources()
        
        # Initialize statistics
        self.stats = {
            'documents_processed': 0,
            'samples_generated': 0,
            'concepts_annotated': 0,
            'reasoning_chains_created': 0
        }
        
    def setup_nlp_components(self):
        """Initialize NLP processing components"""
        
        logger.info("Setting up NLP components...")
        
        # Concept extractor
        extractor_config = {
            'min_concept_frequency': 5,
            'max_concepts_per_text': 20,
            'concept_similarity_threshold': 0.75
        }
        self.concept_extractor = LegalConceptExtractor(extractor_config)
        
        # Reasoning engine
        reasoner_config = {
            'max_inference_steps': 10,
            'confidence_threshold': 0.7,
            'multi_jurisdictional': True
        }
        self.reasoning_engine = ConceptualReasoningEngine(reasoner_config)
        
        # SpaCy for text processing
        try:
            self.nlp = spacy.load("es_core_news_lg")
        except OSError:
            logger.warning("Large Spanish model not found, using small model")
            self.nlp = spacy.load("es_core_news_sm")
            
    def setup_legal_sources(self):
        """Setup legal document sources by jurisdiction"""
        
        self.legal_sources = {
            'argentina': {
                'codigo_civil': {
                    'url_base': 'http://servicios.infoleg.gob.ar/infolegInternet/anexos/',
                    'patterns': ['codigo civil', 'cciv', 'ley 340'],
                    'category': 'civil'
                },
                'ley_sociedades': {
                    'patterns': ['ley 19550', 'ley sociedades comerciales', 'LSC'],
                    'category': 'commercial'
                },
                'codigo_procesal': {
                    'patterns': ['codigo procesal civil', 'CPCCN'],
                    'category': 'procedural'
                }
            },
            'chile': {
                'codigo_civil': {
                    'patterns': ['codigo civil chileno', 'cc chile'],
                    'category': 'civil'
                },
                'ley_sociedades_anonimas': {
                    'patterns': ['ley 18046', 'ley sociedades anonimas'],
                    'category': 'commercial'
                }
            },
            'uruguay': {
                'codigo_civil': {
                    'patterns': ['codigo civil uruguayo'],
                    'category': 'civil'
                },
                'codigo_comercio': {
                    'patterns': ['codigo comercio uruguay'],
                    'category': 'commercial'
                }
            },
            'españa': {
                'codigo_civil': {
                    'patterns': ['codigo civil español', 'cc españa'],
                    'category': 'civil'
                },
                'ley_sociedades_capital': {
                    'patterns': ['ley sociedades capital', 'LSC españa'],
                    'category': 'commercial'
                }
            }
        }
        
    def build_corpus(self) -> Tuple[List[AnnotatedSample], List[AnnotatedSample], List[AnnotatedSample]]:
        """
        Build complete legal corpus with train/val/test splits
        
        Returns:
            Tuple of (train_samples, val_samples, test_samples)
        """
        
        logger.info("Starting legal corpus construction...")
        
        # Step 1: Collect legal documents
        documents = self.collect_legal_documents()
        
        # Step 2: Process documents into training samples
        samples = self.process_documents_to_samples(documents)
        
        # Step 3: Augment data if needed
        if self.config.get('data_augmentation', {}).get('enable', False):
            augmented_samples = self.augment_data(samples)
            samples.extend(augmented_samples)
        
        # Step 4: Quality filtering
        filtered_samples = self.filter_samples_by_quality(samples)
        
        # Step 5: Create train/val/test splits
        train_samples, val_samples, test_samples = self.create_data_splits(filtered_samples)
        
        # Step 6: Save datasets
        self.save_datasets(train_samples, val_samples, test_samples)
        
        # Step 7: Generate statistics
        self.generate_corpus_statistics(train_samples, val_samples, test_samples)
        
        logger.info(f"Corpus building completed:")
        logger.info(f"  Train samples: {len(train_samples)}")
        logger.info(f"  Validation samples: {len(val_samples)}")
        logger.info(f"  Test samples: {len(test_samples)}")
        
        return train_samples, val_samples, test_samples
    
    def collect_legal_documents(self) -> List[LegalDocument]:
        """Collect legal documents from various sources"""
        
        logger.info("Collecting legal documents...")
        
        documents = []
        
        # For demo purposes, create synthetic legal documents
        # In real implementation, this would scrape from official sources
        synthetic_docs = self.create_synthetic_legal_documents()
        documents.extend(synthetic_docs)
        
        # Add real document collection here
        # real_docs = self.scrape_official_legal_sources()
        # documents.extend(real_docs)
        
        logger.info(f"Collected {len(documents)} legal documents")
        
        return documents
    
    def create_synthetic_legal_documents(self) -> List[LegalDocument]:
        """Create synthetic legal documents for training"""
        
        logger.info("Creating synthetic legal documents...")
        
        synthetic_docs = []
        
        # Contract law documents
        contract_docs = [
            {
                'title': 'Formación del Contrato de Compraventa',
                'content': '''
                El contrato de compraventa se perfecciona mediante el consentimiento de las partes 
                sobre la cosa y el precio. Para que el consentimiento sea válido, debe ser libre, 
                consciente y exteriorizado. El objeto del contrato debe ser lícito, posible y 
                determinado o determinable. El precio debe ser cierto y expresado en dinero.
                
                La tradición de la cosa vendida es requisito para la transferencia del dominio.
                Sin tradición, el comprador solo tiene derecho personal contra el vendedor.
                El vendedor debe entregar la cosa en el estado en que se encontraba al celebrarse
                el contrato, respondiendo por los vicios ocultos que impidan el uso normal.
                ''',
                'jurisdiction': 'argentina',
                'category': 'civil',
                'source': 'codigo_civil_arg'
            },
            {
                'title': 'Nulidad de los Contratos por Vicios del Consentimiento',
                'content': '''
                Los vicios del consentimiento que pueden acarrear la nulidad del contrato son
                el error, el dolo y la violencia. El error debe ser esencial y excusable para
                viciar el consentimiento. El dolo consiste en la maquinación fraudulenta destinada
                a obtener el consentimiento. La violencia puede ser física o moral.
                
                La nulidad puede ser absoluta o relativa según la naturaleza del vicio.
                Los contratos nulos no producen efectos jurídicos, mientras que los anulables
                son válidos hasta que se declare su nulidad por sentencia judicial.
                ''',
                'jurisdiction': 'argentina',
                'category': 'civil',
                'source': 'codigo_civil_arg'
            }
        ]
        
        # Corporate law documents  
        corporate_docs = [
            {
                'title': 'Gobierno Corporativo en Sociedades Anónimas',
                'content': '''
                Las sociedades anónimas deben contar con órganos de gobierno y administración
                claramente definidos. El directorio es el órgano de administración, cuyos
                miembros son elegidos por la asamblea de accionistas. La sindicatura ejerce
                funciones de control y fiscalización.
                
                El gobierno corporativo incluye políticas de transparencia, gestión de riesgos
                y protección de minoritarios. Las sociedades que hacen oferta pública deben
                cumplir estándares adicionales de gobierno corporativo y reportar regularmente
                a los organismos de control.
                ''',
                'jurisdiction': 'argentina', 
                'category': 'commercial',
                'source': 'ley_sociedades_arg'
            },
            {
                'title': 'Responsabilidad de Directores y Administradores',
                'content': '''
                Los directores y administradores de sociedades anónimas deben actuar con
                lealtad y diligencia del buen hombre de negocios. Responden solidaria e
                ilimitadamente por los daños causados por su accionar culposo o doloso.
                
                La responsabilidad se extiende a las decisiones del directorio que violen
                la ley, el estatuto o el reglamento. Los directores pueden eximirse de
                responsabilidad dejando constancia de su oposición y comunicándolo a los
                síndicos.
                ''',
                'jurisdiction': 'argentina',
                'category': 'commercial', 
                'source': 'ley_sociedades_arg'
            }
        ]
        
        # Labor law documents
        labor_docs = [
            {
                'title': 'Elementos del Contrato de Trabajo',
                'content': '''
                El contrato de trabajo se caracteriza por la prestación personal de servicios
                bajo dependencia a cambio de una remuneración. La subordinación técnica,
                económica y jurídica distingue la relación laboral de otras formas contractuales.
                
                La prestación debe ser personal e indelegable por parte del trabajador.
                La dependencia implica que el empleador dirige y organiza la actividad laboral.
                La remuneración debe ser suficiente para asegurar una vida digna al trabajador
                y su familia.
                ''',
                'jurisdiction': 'argentina',
                'category': 'labor',
                'source': 'ley_contrato_trabajo_arg'
            }
        ]
        
        # Administrative law documents
        admin_docs = [
            {
                'title': 'Validez del Acto Administrativo',
                'content': '''
                Para la validez del acto administrativo se requiere competencia del órgano,
                procedimiento regular y motivación suficiente. La competencia debe estar
                expresamente otorgada por la norma. El procedimiento debe respetar el
                debido proceso administrativo.
                
                La motivación debe explicar los fundamentos fácticos y jurídicos del acto.
                Los actos administrativos gozan de presunción de legitimidad y fuerza
                ejecutoria, pero pueden ser impugnados mediante los recursos administrativos
                correspondientes.
                ''',
                'jurisdiction': 'argentina',
                'category': 'administrative',
                'source': 'ley_procedimientos_adm_arg'
            }
        ]
        
        # Constitutional law documents
        constitutional_docs = [
            {
                'title': 'Garantías del Debido Proceso',
                'content': '''
                El debido proceso comprende el derecho a ser oído, a ofrecer y producir prueba,
                a la defensa técnica y a la decisión fundada. Toda persona tiene derecho a
                ser juzgada por tribunales independientes e imparciales establecidos por ley.
                
                La garantía del debido proceso se aplica tanto en sede judicial como administrativa.
                Incluye el derecho a conocer la imputación, a contradecir la prueba de cargo
                y a recurrir la decisión ante un tribunal superior. La violación del debido
                proceso acarrea la nulidad del procedimiento.
                ''',
                'jurisdiction': 'argentina',
                'category': 'constitutional',
                'source': 'constitucion_argentina'
            }
        ]
        
        # Compliance documents
        compliance_docs = [
            {
                'title': 'Programas de Integridad y Compliance',
                'content': '''
                Los programas de compliance tienen por objeto prevenir, detectar y corregir
                irregularidades y actos de corrupción. Deben incluir un código de ética,
                políticas y procedimientos, capacitación del personal y canales de denuncia.
                
                La efectiva implementación del programa puede atenuar la responsabilidad
                de las personas jurídicas por actos de corrupción. El programa debe ser
                actualizado periódicamente y supervisado por la alta dirección de la organización.
                La autoridad de aplicación puede requerir auditorías independientes del programa.
                ''',
                'jurisdiction': 'argentina',
                'category': 'compliance', 
                'source': 'ley_responsabilidad_penal_empresas_arg'
            }
        ]
        
        # Combine all documents
        all_docs_data = contract_docs + corporate_docs + labor_docs + admin_docs + constitutional_docs + compliance_docs
        
        # Create LegalDocument objects
        for i, doc_data in enumerate(all_docs_data):
            doc = LegalDocument(
                doc_id=f"synthetic_{i:03d}",
                title=doc_data['title'],
                content=doc_data['content'],
                source=doc_data['source'],
                jurisdiction=doc_data['jurisdiction'],
                legal_category=doc_data['category'],
                metadata={'synthetic': True, 'word_count': len(doc_data['content'].split())}
            )
            synthetic_docs.append(doc)
        
        # Replicate documents for other jurisdictions with variations
        extended_docs = synthetic_docs.copy()
        
        for jurisdiction in ['chile', 'uruguay', 'españa']:
            for base_doc in synthetic_docs:
                # Create adapted version for other jurisdiction
                adapted_doc = LegalDocument(
                    doc_id=f"{base_doc.doc_id}_{jurisdiction}",
                    title=f"{base_doc.title} - {jurisdiction.title()}",
                    content=self._adapt_content_for_jurisdiction(base_doc.content, jurisdiction),
                    source=f"{base_doc.source}_{jurisdiction}",
                    jurisdiction=jurisdiction,
                    legal_category=base_doc.legal_category,
                    metadata={**base_doc.metadata, 'adapted_from': base_doc.doc_id}
                )
                extended_docs.append(adapted_doc)
        
        return extended_docs
    
    def _adapt_content_for_jurisdiction(self, content: str, jurisdiction: str) -> str:
        """Adapt legal content for different jurisdictions"""
        
        # Simple adaptations - in real implementation this would be more sophisticated
        adaptations = {
            'chile': {
                'código civil': 'Código Civil chileno',
                'argentina': 'Chile',
                'argentino': 'chileno'
            },
            'uruguay': {
                'código civil': 'Código Civil uruguayo', 
                'argentina': 'Uruguay',
                'argentino': 'uruguayo'
            },
            'españa': {
                'código civil': 'Código Civil español',
                'argentina': 'España', 
                'argentino': 'español'
            }
        }
        
        adapted_content = content
        
        if jurisdiction in adaptations:
            for original, replacement in adaptations[jurisdiction].items():
                adapted_content = adapted_content.replace(original, replacement)
        
        return adapted_content
    
    def process_documents_to_samples(self, documents: List[LegalDocument]) -> List[AnnotatedSample]:
        """Process legal documents into annotated training samples"""
        
        logger.info(f"Processing {len(documents)} documents into training samples...")
        
        samples = []
        
        for doc in documents:
            # Split document into passages
            passages = self._split_document_into_passages(doc.content)
            
            for i, passage in enumerate(passages):
                if len(passage.strip()) < 50:  # Skip very short passages
                    continue
                
                # Extract concepts from passage
                concept_matches = self.concept_extractor.extract_concepts(
                    passage, 
                    jurisdiction=doc.jurisdiction
                )
                
                if not concept_matches:  # Skip if no concepts found
                    continue
                
                # Generate concept list
                concepts = [match.concept_name.lower().replace(' ', '_') for match in concept_matches]
                
                # Generate reasoning chain
                reasoning_chains = self.reasoning_engine.reason(
                    initial_concepts=concepts,
                    jurisdiction=doc.jurisdiction,
                    reasoning_type=ReasoningType.DEDUCTIVE
                )
                
                # Convert reasoning chain to training format
                reasoning_chain = []
                if reasoning_chains:
                    best_chain = reasoning_chains[0]  # Take best reasoning chain
                    
                    for j, step in enumerate(best_chain.steps):
                        reasoning_step = {
                            'step': str(j + 1),
                            'concept': step.conclusion_concept,
                            'reasoning': step.explanation,
                            'legal_rule': step.legal_rule or '',
                            'confidence': str(step.confidence)
                        }
                        reasoning_chain.append(reasoning_step)
                
                # Generate ground truth answer (simplified)
                ground_truth = self._generate_ground_truth_answer(concepts, reasoning_chain, doc.legal_category)
                
                # Create annotated sample
                sample = AnnotatedSample(
                    text=passage,
                    concepts=concepts,
                    reasoning_chain=reasoning_chain,
                    jurisdiction=doc.jurisdiction,
                    legal_category=doc.legal_category,
                    ground_truth_answer=ground_truth,
                    confidence_score=self._calculate_sample_confidence(concept_matches, reasoning_chains),
                    source_document=doc.doc_id
                )
                
                samples.append(sample)
                
                # Update statistics
                self.stats['concepts_annotated'] += len(concepts)
                if reasoning_chain:
                    self.stats['reasoning_chains_created'] += 1
            
            self.stats['documents_processed'] += 1
        
        self.stats['samples_generated'] = len(samples)
        
        logger.info(f"Generated {len(samples)} annotated samples")
        
        return samples
    
    def _split_document_into_passages(self, content: str, max_length: int = 500) -> List[str]:
        """Split document into smaller passages for training"""
        
        # Clean content
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        passages = []
        current_passage = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max_length, start new passage
            if len(current_passage) + len(paragraph) > max_length and current_passage:
                passages.append(current_passage.strip())
                current_passage = paragraph
            else:
                current_passage += " " + paragraph if current_passage else paragraph
        
        # Add the last passage
        if current_passage.strip():
            passages.append(current_passage.strip())
        
        # If passages are still too long, split by sentences
        final_passages = []
        for passage in passages:
            if len(passage) <= max_length:
                final_passages.append(passage)
            else:
                # Split by sentences using spaCy
                doc = self.nlp(passage)
                sentences = [sent.text.strip() for sent in doc.sents]
                
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > max_length and current_chunk:
                        final_passages.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
                
                if current_chunk.strip():
                    final_passages.append(current_chunk.strip())
        
        return final_passages
    
    def _generate_ground_truth_answer(self, concepts: List[str], reasoning_chain: List[Dict], legal_category: str) -> str:
        """Generate ground truth answer based on concepts and reasoning"""
        
        if not concepts:
            return "No se identificaron conceptos legales relevantes."
        
        # Create answer based on legal category and concepts
        category_templates = {
            'civil': "En materia civil, los conceptos {concepts} sugieren que {conclusion}.",
            'commercial': "En el ámbito societario, la presencia de {concepts} indica que {conclusion}.",
            'labor': "En materia laboral, los elementos {concepts} determinan que {conclusion}.",
            'administrative': "En derecho administrativo, {concepts} llevan a concluir que {conclusion}.",
            'constitutional': "Desde la perspectiva constitucional, {concepts} implican que {conclusion}.",
            'compliance': "En términos de compliance, {concepts} requieren que {conclusion}."
        }
        
        template = category_templates.get(legal_category, "Los conceptos {concepts} sugieren que {conclusion}.")
        
        # Generate conclusion based on reasoning chain
        if reasoning_chain:
            last_step = reasoning_chain[-1]
            conclusion = f"se aplica {last_step.get('concept', 'la normativa correspondiente')}"
        else:
            conclusion = "se debe analizar la normativa aplicable"
        
        # Format concepts nicely
        concept_list = ", ".join(concepts[:3])  # Limit to first 3 concepts
        if len(concepts) > 3:
            concept_list += f" y otros {len(concepts) - 3} conceptos"
        
        answer = template.format(concepts=concept_list, conclusion=conclusion)
        
        return answer
    
    def _calculate_sample_confidence(self, concept_matches: List[ConceptMatch], reasoning_chains: List[ReasoningChain]) -> float:
        """Calculate confidence score for a sample"""
        
        if not concept_matches:
            return 0.0
        
        # Average concept confidence
        concept_confidence = np.mean([match.confidence for match in concept_matches])
        
        # Reasoning confidence (if available)
        reasoning_confidence = 0.0
        if reasoning_chains:
            reasoning_confidence = reasoning_chains[0].overall_confidence
        
        # Combined confidence
        if reasoning_chains:
            final_confidence = 0.6 * concept_confidence + 0.4 * reasoning_confidence
        else:
            final_confidence = concept_confidence
        
        return final_confidence
    
    def augment_data(self, samples: List[AnnotatedSample]) -> List[AnnotatedSample]:
        """Data augmentation for legal training samples"""
        
        logger.info("Performing data augmentation...")
        
        augmented_samples = []
        
        augmentation_config = self.config.get('data_augmentation', {})
        
        # Paraphrasing augmentation
        if augmentation_config.get('enable_paraphrasing', True):
            paraphrased = self._augment_by_paraphrasing(samples)
            augmented_samples.extend(paraphrased)
        
        # Concept substitution
        if augmentation_config.get('enable_concept_substitution', True):
            substituted = self._augment_by_concept_substitution(samples)
            augmented_samples.extend(substituted)
        
        # Cross-jurisdictional adaptation
        if augmentation_config.get('enable_cross_jurisdictional', True):
            cross_jurisdictional = self._augment_cross_jurisdictional(samples)
            augmented_samples.extend(cross_jurisdictional)
        
        logger.info(f"Generated {len(augmented_samples)} augmented samples")
        
        return augmented_samples
    
    def _augment_by_paraphrasing(self, samples: List[AnnotatedSample]) -> List[AnnotatedSample]:
        """Augment data by paraphrasing legal text"""
        
        paraphrased_samples = []
        
        # Simple paraphrasing patterns for legal text
        paraphrasing_patterns = [
            (r'El contrato de (\w+)', r'El acuerdo de \1'),
            (r'se requiere', r'es necesario'),
            (r'debe ser', r'tiene que ser'),
            (r'la ley establece', r'la normativa dispone'),
            (r'según el código', r'conforme al código'),
            (r'por lo tanto', r'en consecuencia'),
            (r'es válido', r'tiene validez'),
            (r'responsabilidad', r'responsabilidad legal')
        ]
        
        # Apply paraphrasing to a subset of samples
        for sample in samples[:len(samples)//4]:  # Paraphrase 25% of samples
            paraphrased_text = sample.text
            
            # Apply paraphrasing patterns
            for pattern, replacement in paraphrasing_patterns:
                if random.random() < 0.3:  # 30% chance to apply each pattern
                    paraphrased_text = re.sub(pattern, replacement, paraphrased_text, flags=re.IGNORECASE)
            
            # Only create new sample if text actually changed
            if paraphrased_text != sample.text:
                paraphrased_sample = AnnotatedSample(
                    text=paraphrased_text,
                    concepts=sample.concepts.copy(),
                    reasoning_chain=sample.reasoning_chain.copy(),
                    jurisdiction=sample.jurisdiction,
                    legal_category=sample.legal_category,
                    ground_truth_answer=sample.ground_truth_answer,
                    confidence_score=sample.confidence_score * 0.9,  # Slightly lower confidence
                    source_document=f"{sample.source_document}_paraphrased"
                )
                paraphrased_samples.append(paraphrased_sample)
        
        return paraphrased_samples
    
    def _augment_by_concept_substitution(self, samples: List[AnnotatedSample]) -> List[AnnotatedSample]:
        """Augment data by substituting similar concepts"""
        
        substituted_samples = []
        
        # Define concept substitution groups
        concept_substitutions = {
            'contrato_compraventa': ['contrato_venta', 'acuerdo_compraventa', 'convenio_venta'],
            'responsabilidad_civil': ['responsabilidad_extracontractual', 'obligacion_reparatoria'],
            'sociedad_anonima': ['compania_anonima', 'corporacion'],
            'debido_proceso': ['garantias_procesales', 'tutela_judicial_efectiva'],
            'consentimiento': ['acuerdo_voluntades', 'consenso_mutuo']
        }
        
        for sample in samples[:len(samples)//5]:  # Substitute in 20% of samples
            # Find concepts that can be substituted
            substitutable_concepts = [c for c in sample.concepts if c in concept_substitutions]
            
            if substitutable_concepts:
                # Select one concept to substitute
                target_concept = random.choice(substitutable_concepts)
                substitute_concept = random.choice(concept_substitutions[target_concept])
                
                # Update text, concepts, and reasoning
                new_text = sample.text.replace(target_concept.replace('_', ' '), substitute_concept.replace('_', ' '))
                new_concepts = [substitute_concept if c == target_concept else c for c in sample.concepts]
                
                # Update reasoning chain
                new_reasoning_chain = []
                for step in sample.reasoning_chain:
                    new_step = step.copy()
                    if step.get('concept') == target_concept:
                        new_step['concept'] = substitute_concept
                    new_reasoning_chain.append(new_step)
                
                substituted_sample = AnnotatedSample(
                    text=new_text,
                    concepts=new_concepts,
                    reasoning_chain=new_reasoning_chain,
                    jurisdiction=sample.jurisdiction,
                    legal_category=sample.legal_category,
                    ground_truth_answer=sample.ground_truth_answer,
                    confidence_score=sample.confidence_score * 0.95,
                    source_document=f"{sample.source_document}_substituted"
                )
                substituted_samples.append(substituted_sample)
        
        return substituted_samples
    
    def _augment_cross_jurisdictional(self, samples: List[AnnotatedSample]) -> List[AnnotatedSample]:
        """Create cross-jurisdictional variations of samples"""
        
        cross_jurisdictional_samples = []
        
        # Jurisdiction mappings for legal concepts
        jurisdiction_adaptations = {
            'argentina': {
                'target_jurisdictions': ['chile', 'uruguay'],
                'adaptations': {
                    'codigo_civil': 'código_civil_local',
                    'ley_sociedades': 'ley_sociedades_local'
                }
            },
            'chile': {
                'target_jurisdictions': ['argentina', 'uruguay'], 
                'adaptations': {
                    'codigo_civil_chileno': 'código_civil_local'
                }
            }
        }
        
        for sample in samples[:len(samples)//6]:  # Cross-jurisdictional for 16% of samples
            source_jurisdiction = sample.jurisdiction
            
            if source_jurisdiction in jurisdiction_adaptations:
                adaptation_info = jurisdiction_adaptations[source_jurisdiction]
                target_jurisdiction = random.choice(adaptation_info['target_jurisdictions'])
                
                # Adapt text for target jurisdiction
                adapted_text = sample.text
                for original, replacement in adaptation_info['adaptations'].items():
                    adapted_text = adapted_text.replace(original, replacement)
                
                cross_sample = AnnotatedSample(
                    text=adapted_text,
                    concepts=sample.concepts.copy(),
                    reasoning_chain=sample.reasoning_chain.copy(),
                    jurisdiction=target_jurisdiction,
                    legal_category=sample.legal_category,
                    ground_truth_answer=sample.ground_truth_answer,
                    confidence_score=sample.confidence_score * 0.8,  # Lower confidence for cross-jurisdictional
                    source_document=f"{sample.source_document}_cross_{target_jurisdiction}"
                )
                cross_jurisdictional_samples.append(cross_sample)
        
        return cross_jurisdictional_samples
    
    def filter_samples_by_quality(self, samples: List[AnnotatedSample]) -> List[AnnotatedSample]:
        """Filter samples based on quality criteria"""
        
        logger.info(f"Filtering {len(samples)} samples by quality...")
        
        filtered_samples = []
        
        quality_criteria = self.config.get('quality_criteria', {})
        min_confidence = quality_criteria.get('min_confidence', 0.5)
        min_concepts = quality_criteria.get('min_concepts', 1)
        min_text_length = quality_criteria.get('min_text_length', 50)
        max_text_length = quality_criteria.get('max_text_length', 2000)
        
        for sample in samples:
            # Check quality criteria
            if (sample.confidence_score >= min_confidence and 
                len(sample.concepts) >= min_concepts and
                min_text_length <= len(sample.text) <= max_text_length and
                sample.text.strip() and
                sample.concepts):  # Must have non-empty text and concepts
                
                filtered_samples.append(sample)
        
        logger.info(f"Retained {len(filtered_samples)} samples after quality filtering")
        
        return filtered_samples
    
    def create_data_splits(self, samples: List[AnnotatedSample]) -> Tuple[List[AnnotatedSample], List[AnnotatedSample], List[AnnotatedSample]]:
        """Create train/validation/test splits"""
        
        logger.info("Creating train/validation/test splits...")
        
        # Stratify by jurisdiction and legal category
        stratify_labels = [f"{sample.jurisdiction}_{sample.legal_category}" for sample in samples]
        
        # First split: separate test set (20%)
        train_val_samples, test_samples, train_val_labels, test_labels = train_test_split(
            samples, 
            stratify_labels,
            test_size=0.2,
            random_state=42,
            stratify=stratify_labels
        )
        
        # Second split: separate validation from train (25% of remaining = 20% of total)
        train_samples, val_samples, _, _ = train_test_split(
            train_val_samples,
            train_val_labels, 
            test_size=0.25,
            random_state=42,
            stratify=train_val_labels
        )
        
        logger.info(f"Data splits created:")
        logger.info(f"  Train: {len(train_samples)} samples ({len(train_samples)/len(samples)*100:.1f}%)")
        logger.info(f"  Validation: {len(val_samples)} samples ({len(val_samples)/len(samples)*100:.1f}%)")
        logger.info(f"  Test: {len(test_samples)} samples ({len(test_samples)/len(samples)*100:.1f}%)")
        
        return train_samples, val_samples, test_samples
    
    def save_datasets(self, train_samples: List[AnnotatedSample], val_samples: List[AnnotatedSample], test_samples: List[AnnotatedSample]):
        """Save datasets to JSONL files"""
        
        logger.info("Saving datasets to files...")
        
        # Convert samples to JSON format
        datasets = {
            'train': train_samples,
            'validation': val_samples,
            'test': test_samples
        }
        
        for split_name, samples in datasets.items():
            output_file = self.output_dir / f"legal_corpus_{split_name}.jsonl"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for sample in samples:
                    sample_dict = {
                        'text': sample.text,
                        'concepts': sample.concepts,
                        'reasoning_chain': sample.reasoning_chain,
                        'jurisdiction': sample.jurisdiction,
                        'legal_category': sample.legal_category,
                        'answer': sample.ground_truth_answer,
                        'confidence': sample.confidence_score,
                        'source': sample.source_document
                    }
                    
                    f.write(json.dumps(sample_dict, ensure_ascii=False) + '\n')
            
            logger.info(f"Saved {len(samples)} {split_name} samples to {output_file}")
        
        # Save metadata
        metadata_file = self.output_dir / "corpus_metadata.json"
        metadata = {
            'total_samples': len(train_samples) + len(val_samples) + len(test_samples),
            'train_samples': len(train_samples),
            'validation_samples': len(val_samples),
            'test_samples': len(test_samples),
            'statistics': self.stats,
            'config': self.config,
            'jurisdictions': list(set(sample.jurisdiction for sample in train_samples + val_samples + test_samples)),
            'legal_categories': list(set(sample.legal_category for sample in train_samples + val_samples + test_samples))
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved corpus metadata to {metadata_file}")
    
    def generate_corpus_statistics(self, train_samples: List[AnnotatedSample], val_samples: List[AnnotatedSample], test_samples: List[AnnotatedSample]):
        """Generate detailed corpus statistics"""
        
        logger.info("Generating corpus statistics...")
        
        all_samples = train_samples + val_samples + test_samples
        
        # Basic statistics
        stats = {
            'total_samples': len(all_samples),
            'train_samples': len(train_samples),
            'val_samples': len(val_samples),
            'test_samples': len(test_samples),
        }
        
        # Distribution by jurisdiction
        jurisdiction_counts = Counter(sample.jurisdiction for sample in all_samples)
        stats['jurisdiction_distribution'] = dict(jurisdiction_counts)
        
        # Distribution by legal category
        category_counts = Counter(sample.legal_category for sample in all_samples)
        stats['category_distribution'] = dict(category_counts)
        
        # Concept statistics
        all_concepts = []
        for sample in all_samples:
            all_concepts.extend(sample.concepts)
        
        concept_counts = Counter(all_concepts)
        stats['total_unique_concepts'] = len(concept_counts)
        stats['most_common_concepts'] = dict(concept_counts.most_common(10))
        
        # Text length statistics
        text_lengths = [len(sample.text) for sample in all_samples]
        stats['text_length_stats'] = {
            'mean': np.mean(text_lengths),
            'median': np.median(text_lengths),
            'min': np.min(text_lengths),
            'max': np.max(text_lengths),
            'std': np.std(text_lengths)
        }
        
        # Reasoning chain statistics
        reasoning_chain_lengths = [len(sample.reasoning_chain) for sample in all_samples if sample.reasoning_chain]
        if reasoning_chain_lengths:
            stats['reasoning_chain_stats'] = {
                'mean': np.mean(reasoning_chain_lengths),
                'median': np.median(reasoning_chain_lengths),
                'min': np.min(reasoning_chain_lengths),
                'max': np.max(reasoning_chain_lengths)
            }
        
        # Confidence score statistics
        confidence_scores = [sample.confidence_score for sample in all_samples]
        stats['confidence_stats'] = {
            'mean': np.mean(confidence_scores),
            'median': np.median(confidence_scores),
            'min': np.min(confidence_scores),
            'max': np.max(confidence_scores),
            'std': np.std(confidence_scores)
        }
        
        # Save statistics
        stats_file = self.output_dir / "corpus_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved detailed statistics to {stats_file}")
        
        # Print summary
        print("\nCORPUS STATISTICS SUMMARY")
        print("=" * 40)
        print(f"Total samples: {stats['total_samples']:,}")
        print(f"Unique concepts: {stats['total_unique_concepts']:,}")
        print(f"Average text length: {stats['text_length_stats']['mean']:.0f} characters")
        print(f"Average confidence: {stats['confidence_stats']['mean']:.2f}")
        
        print("\nJurisdiction Distribution:")
        for jurisdiction, count in jurisdiction_counts.items():
            print(f"  {jurisdiction}: {count:,} ({count/len(all_samples)*100:.1f}%)")
        
        print("\nLegal Category Distribution:")
        for category, count in category_counts.items():
            print(f"  {category}: {count:,} ({count/len(all_samples)*100:.1f}%)")

def main():
    """Main function to build legal corpus"""
    
    # Configuration
    config = {
        'output_dir': '/home/user/SLM-Legal-Spanish/training/data',
        'data_augmentation': {
            'enable': True,
            'enable_paraphrasing': True,
            'enable_concept_substitution': True,
            'enable_cross_jurisdictional': True,
            'augmentation_ratio': 0.2
        },
        'quality_criteria': {
            'min_confidence': 0.5,
            'min_concepts': 1,
            'min_text_length': 50,
            'max_text_length': 2000
        }
    }
    
    # Initialize corpus builder
    corpus_builder = LegalCorpusBuilder(config)
    
    # Build corpus
    train_samples, val_samples, test_samples = corpus_builder.build_corpus()
    
    print(f"\nCorpus building completed successfully!")
    print(f"Generated datasets saved to: {config['output_dir']}")
    print(f"Ready for SCM legal model training.")

if __name__ == "__main__":
    main()