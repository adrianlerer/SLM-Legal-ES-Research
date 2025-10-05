"""
Procesador de Documentos Propietario - SLM-Legal-Spanish
======================================================

Sistema para procesar y preparar la base documental privada del usuario
con trazabilidad de experiencia profesional y anonimización automática.

CONFIDENCIAL - Propiedad Intelectual Exclusiva
Desarrollado por: Ignacio Adrián Lerer (Abogado UBA, Executive MBA Universidad Austral)

Características:
- Procesamiento seguro con anonimización automática
- Trazabilidad de experiencia profesional
- Categorización por valor estratégico
- Extracción de patrones legales únicos
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from collections import defaultdict
import logging

# Procesamiento de texto
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy

# Anonimización y seguridad
import presidio_analyzer
from presidio_anonymizer import AnonymizerEngine

# Machine Learning para categorización
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DocumentMetadata:
    """
    Metadata enriquecida de documentos con trazabilidad de experiencia profesional.
    """
    # Identificación básica
    document_id: str
    file_path: str
    original_filename: str
    file_size: int
    creation_date: datetime
    
    # Categorización profesional
    document_type: str  # acta_directorio, dictamen_legal, contrato, etc.
    experience_level: str  # maximo_valor, alto_valor, complementario
    sector: str  # manufactura, energia, mineria, general
    jurisdiction: str  # AR, ES, CL, UY
    
    # Experiencia del autor
    authored_by_user: bool = False  # Documentos creados por ti
    user_role_in_doc: str = ""  # director, abogado, consultor, etc.
    experience_years_when_created: Optional[int] = None
    
    # Contenido legal
    legal_concepts: List[str] = field(default_factory=list)
    precedents_referenced: List[str] = field(default_factory=list)
    regulatory_frameworks: List[str] = field(default_factory=list)
    
    # Calidad y confidencialidad
    quality_score: float = 0.0
    confidentiality_level: str = "public"  # public, internal, confidential
    anonymization_required: bool = True
    
    # Procesamiento
    text_length: int = 0
    processed_text: str = ""
    embedding_vector: Optional[np.ndarray] = None


class PrivateDocumentProcessor:
    """
    Procesador especializado para documentos privados con anonimización y trazabilidad.
    
    Funcionalidades:
    - Anonimización automática de datos sensibles
    - Categorización inteligente por experiencia
    - Extracción de patrones legales únicos
    - Trazabilidad de experiencia profesional
    """
    
    def __init__(self, base_path: str = "/home/user/SLM-Legal-Spanish/data/private_corpus"):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger("document_processor")
        
        # Crear estructura de directorios
        self._setup_directory_structure()
        
        # Inicializar herramientas de procesamiento
        self._initialize_nlp_tools()
        
        # Inicializar anonimizador
        self._initialize_anonymizer()
        
        # Base de datos de documentos procesados
        self.processed_documents: Dict[str, DocumentMetadata] = {}
        self.experience_index: Dict[str, List[str]] = defaultdict(list)
        
        # Configuración de categorización
        self.document_categories = self._initialize_document_categories()
        
    def _setup_directory_structure(self):
        """Crea estructura de directorios para organizar documentos."""
        directories = [
            "normativos/argentina", "normativos/chile", "normativos/uruguay", "normativos/españa",
            "jurisprudenciales/csjn", "jurisprudenciales/caf", "jurisprudenciales/comercial",
            "corporativos/actas_directorio", "corporativos/actas_asamblea", 
            "corporativos/dictamenes_legales", "corporativos/contratos",
            "experiencia_profesional/corporativo_ejecutivo", "experiencia_profesional/directorial", 
            "experiencia_profesional/sectores_especializados", "experiencia_profesional/multijurisdiccional",
            "gobierno_corporativo/politicas_internas", "gobierno_corporativo/procedimientos",
            "processed/anonymized", "processed/embeddings", "processed/metadata"
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Directory structure created at {self.base_path}")
    
    def _initialize_nlp_tools(self):
        """Inicializa herramientas de procesamiento de lenguaje natural."""
        try:
            # Descargar recursos de NLTK si no existen
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            
            # Cargar modelo de spaCy para español
            self.nlp = spacy.load('es_core_news_sm')
            
            # Stopwords en español
            self.spanish_stopwords = set(stopwords.words('spanish'))
            
            # Vectorizador TF-IDF
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words=list(self.spanish_stopwords),
                ngram_range=(1, 3)
            )
            
        except Exception as e:
            self.logger.warning(f"Some NLP tools not available: {e}")
            self.nlp = None
    
    def _initialize_anonymizer(self):
        """Inicializa motor de anonimización para proteger datos sensibles."""
        try:
            # Analizador de entidades para detectar PII
            self.analyzer = presidio_analyzer.AnalyzerEngine()
            
            # Motor de anonimización
            self.anonymizer = AnonymizerEngine()
            
            # Entidades a detectar y anonimizar
            self.pii_entities = [
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", 
                "CREDIT_CARD", "IBAN_CODE", "IP_ADDRESS",
                "DATE_TIME", "LOCATION", "ORGANIZATION"
            ]
            
        except Exception as e:
            self.logger.warning(f"Anonymizer not available: {e}")
            self.analyzer = None
            self.anonymizer = None
    
    def _initialize_document_categories(self) -> Dict[str, Dict]:
        """Define categorías y criterios de clasificación de documentos."""
        return {
            "acta_directorio": {
                "keywords": ["directorio", "consejo", "resolución", "decisión", "acta"],
                "experience_multiplier": 3.0,  # Máximo valor por experiencia directorial
                "confidentiality": "confidential",
                "legal_weight": 2.5
            },
            "dictamen_legal": {
                "keywords": ["dictamen", "opinión legal", "análisis jurídico", "recomendación"],
                "experience_multiplier": 2.8,
                "confidentiality": "confidential", 
                "legal_weight": 2.3
            },
            "contrato": {
                "keywords": ["contrato", "convenio", "acuerdo", "cláusula", "obligación"],
                "experience_multiplier": 2.0,
                "confidentiality": "internal",
                "legal_weight": 1.8
            },
            "compliance_report": {
                "keywords": ["compliance", "cumplimiento", "auditoría", "riesgo", "control"],
                "experience_multiplier": 2.5,
                "confidentiality": "internal",
                "legal_weight": 2.2
            },
            "normativo": {
                "keywords": ["ley", "decreto", "resolución", "regulación", "normativa"],
                "experience_multiplier": 1.5,
                "confidentiality": "public",
                "legal_weight": 1.5
            },
            "jurisprudencial": {
                "keywords": ["sentencia", "fallo", "precedente", "jurisprudencia", "tribunal"],
                "experience_multiplier": 2.0,
                "confidentiality": "public",
                "legal_weight": 2.0
            }
        }
    
    async def process_document_collection(self, input_path: str, 
                                        author_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Procesa una colección completa de documentos con metadata de experiencia.
        
        Args:
            input_path: Ruta a la colección de documentos
            author_metadata: Metadata del autor (años de experiencia, roles, etc.)
            
        Returns:
            Reporte completo del procesamiento
        """
        self.logger.info(f"Starting processing of document collection: {input_path}")
        
        input_path = Path(input_path)
        if not input_path.exists():
            raise ValueError(f"Input path does not exist: {input_path}")
        
        # Estadísticas de procesamiento
        stats = {
            "total_files": 0,
            "processed_successfully": 0,
            "failed": 0,
            "anonymized": 0,
            "categories": defaultdict(int),
            "experience_levels": defaultdict(int)
        }
        
        # Procesar todos los archivos
        for file_path in input_path.rglob("*"):
            if file_path.is_file() and self._is_processable_file(file_path):
                stats["total_files"] += 1
                
                try:
                    # Procesar documento individual
                    doc_metadata = await self._process_single_document(
                        file_path, author_metadata
                    )
                    
                    if doc_metadata:
                        self.processed_documents[doc_metadata.document_id] = doc_metadata
                        stats["processed_successfully"] += 1
                        stats["categories"][doc_metadata.document_type] += 1
                        stats["experience_levels"][doc_metadata.experience_level] += 1
                        
                        if doc_metadata.anonymization_required:
                            stats["anonymized"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    stats["failed"] += 1
        
        # Generar embeddings y análisis
        await self._generate_document_embeddings()
        await self._analyze_document_patterns()
        
        # Guardar resultados
        await self._save_processing_results()
        
        self.logger.info(f"Processing completed: {stats}")
        return stats
    
    async def _process_single_document(self, file_path: Path, 
                                     author_metadata: Optional[Dict] = None) -> Optional[DocumentMetadata]:
        """Procesa un documento individual con anonimización y análisis."""
        
        # Leer contenido del archivo
        try:
            content = self._read_document_content(file_path)
            if not content:
                return None
        except Exception as e:
            self.logger.error(f"Could not read {file_path}: {e}")
            return None
        
        # Crear metadata base
        doc_id = hashlib.md5(str(file_path).encode()).hexdigest()
        
        metadata = DocumentMetadata(
            document_id=doc_id,
            file_path=str(file_path),
            original_filename=file_path.name,
            file_size=file_path.stat().st_size,
            creation_date=datetime.fromtimestamp(file_path.stat().st_mtime),
            text_length=len(content)
        )
        
        # Categorización automática
        doc_type, confidence = self._classify_document_type(content)
        metadata.document_type = doc_type
        
        # Determinar nivel de experiencia
        metadata.experience_level = self._determine_experience_level(
            doc_type, file_path, author_metadata
        )
        
        # Extraer información legal
        metadata.legal_concepts = self._extract_legal_concepts(content)
        metadata.precedents_referenced = self._extract_precedents(content)
        metadata.regulatory_frameworks = self._extract_regulatory_frameworks(content)
        
        # Determinar jurisdicción y sector
        metadata.jurisdiction = self._detect_jurisdiction(content)
        metadata.sector = self._detect_sector(content, file_path)
        
        # Anonimización si es necesario
        if self._requires_anonymization(content, metadata):
            anonymized_content = await self._anonymize_document(content)
            metadata.processed_text = anonymized_content
            metadata.anonymization_required = True
        else:
            metadata.processed_text = content
        
        # Calcular score de calidad
        metadata.quality_score = self._calculate_quality_score(metadata)
        
        return metadata
    
    def _read_document_content(self, file_path: Path) -> str:
        """Lee el contenido de diferentes tipos de archivos."""
        ext = file_path.suffix.lower()
        
        if ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            # Requiere PyPDF2 o similar
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            except ImportError:
                self.logger.warning("PyPDF2 not available for PDF processing")
                return ""
        elif ext in ['.doc', '.docx']:
            # Requiere python-docx
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                self.logger.warning("python-docx not available for Word processing")
                return ""
        else:
            self.logger.warning(f"Unsupported file type: {ext}")
            return ""
    
    def _is_processable_file(self, file_path: Path) -> bool:
        """Determina si un archivo puede ser procesado."""
        supported_extensions = ['.txt', '.md', '.pdf', '.doc', '.docx']
        return file_path.suffix.lower() in supported_extensions
    
    def _classify_document_type(self, content: str) -> Tuple[str, float]:
        """Clasifica el tipo de documento basado en su contenido."""
        content_lower = content.lower()
        
        best_category = "general"
        best_score = 0.0
        
        for category, config in self.document_categories.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in content_lower:
                    score += 1
            
            # Normalizar score
            score = score / len(config["keywords"])
            
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category, best_score
    
    def _determine_experience_level(self, doc_type: str, file_path: Path, 
                                  author_metadata: Optional[Dict]) -> str:
        """Determina el nivel de experiencia del documento."""
        
        # Documentos de máximo valor (creados por el usuario)
        if author_metadata and author_metadata.get("authored_by_user", False):
            return "maximo_valor"
        
        # Documentos de alto valor (experiencia directa)
        if doc_type in ["acta_directorio", "dictamen_legal", "compliance_report"]:
            return "alto_valor"
        
        # Documentos complementarios
        return "complementario"
    
    def _extract_legal_concepts(self, content: str) -> List[str]:
        """Extrae conceptos legales del contenido."""
        if not self.nlp:
            return []
        
        doc = self.nlp(content)
        
        # Conceptos legales específicos del dominio corporativo
        legal_concepts = []
        
        # Patrones de conceptos legales
        legal_patterns = [
            r"responsabilidad\s+\w+",
            r"debido\s+proceso",
            r"buena\s+fe",
            r"conflicto\s+de\s+interés",
            r"deber\s+fiduciario",
            r"gobierno\s+corporativo",
            r"compliance\s+\w*",
            r"diligencia\s+debida"
        ]
        
        content_lower = content.lower()
        for pattern in legal_patterns:
            matches = re.findall(pattern, content_lower)
            legal_concepts.extend(matches)
        
        return list(set(legal_concepts))
    
    def _extract_precedents(self, content: str) -> List[str]:
        """Extrae referencias a precedentes jurisprudenciales."""
        precedent_patterns = [
            r"Fallos\s+\d+:\d+",
            r"CSJN\s+[\d/]+",
            r"CNCom\s+[\d/]+",
            r"Sent\.\s+\d+",
            r"Expte\.\s+[\w\d/-]+"
        ]
        
        precedents = []
        for pattern in precedent_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            precedents.extend(matches)
        
        return precedents
    
    def _extract_regulatory_frameworks(self, content: str) -> List[str]:
        """Extrae marcos regulatorios mencionados."""
        regulatory_patterns = [
            r"Ley\s+\d+\.?\d*",
            r"Decreto\s+\d+/\d+",
            r"Resolución\s+\d+/\d+",
            r"CNV\s+\d+",
            r"BCRA\s+\w+\d+"
        ]
        
        frameworks = []
        for pattern in regulatory_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            frameworks.extend(matches)
        
        return frameworks
    
    def _detect_jurisdiction(self, content: str) -> str:
        """Detecta la jurisdicción principal del documento."""
        jurisdiction_indicators = {
            "AR": ["argentina", "csjn", "cnv", "bcra", "afip", "buenos aires"],
            "ES": ["españa", "cnmv", "tribunal supremo", "madrid", "barcelona"],
            "CL": ["chile", "santiago", "svs", "cne", "sbif"],
            "UY": ["uruguay", "montevideo", "bcu", "bse"]
        }
        
        content_lower = content.lower()
        
        for jurisdiction, indicators in jurisdiction_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            if score > 0:
                return jurisdiction
        
        return "AR"  # Default a Argentina
    
    def _detect_sector(self, content: str, file_path: Path) -> str:
        """Detecta el sector económico del documento."""
        sector_indicators = {
            "energia": ["electricidad", "gas", "energía", "generación", "transmisión"],
            "mineria": ["minería", "extracción", "yacimiento", "concesión minera"],
            "manufactura": ["fabricación", "producción", "planta", "manufactura"],
            "financiero": ["banco", "financiero", "crédito", "inversión"]
        }
        
        content_lower = content.lower()
        path_lower = str(file_path).lower()
        
        for sector, indicators in sector_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower or indicator in path_lower)
            if score > 0:
                return sector
        
        return "general"
    
    def _requires_anonymization(self, content: str, metadata: DocumentMetadata) -> bool:
        """Determina si el documento requiere anonimización."""
        # Siempre anonimizar documentos confidenciales
        if metadata.document_type in ["acta_directorio", "dictamen_legal", "compliance_report"]:
            return True
        
        # Verificar si contiene información sensible
        if self.analyzer:
            results = self.analyzer.analyze(text=content, entities=self.pii_entities, language='es')
            return len(results) > 0
        
        return True  # Por seguridad, anonimizar por defecto
    
    async def _anonymize_document(self, content: str) -> str:
        """Anonimiza documento protegiendo información sensible."""
        if not self.anonymizer:
            # Anonimización básica sin presidio
            return self._basic_anonymization(content)
        
        try:
            # Analizar entidades sensibles
            results = self.analyzer.analyze(text=content, entities=self.pii_entities, language='es')
            
            # Anonimizar
            anonymized_result = self.anonymizer.anonymize(text=content, analyzer_results=results)
            
            return anonymized_result.text
            
        except Exception as e:
            self.logger.error(f"Anonymization failed: {e}")
            return self._basic_anonymization(content)
    
    def _basic_anonymization(self, content: str) -> str:
        """Anonimización básica usando patrones regulares."""
        # Patrones básicos para anonimizar
        patterns = [
            (r'\b\d{2}\.\d{3}\.\d{3}-\d\b', '[DNI]'),  # DNI argentino
            (r'\b\d{2}-\d{8}-\d\b', '[CUIT]'),          # CUIT argentino
            (r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]'), # Email
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]'),  # Tarjeta
            (r'\$\s*\d+(?:\.\d{3})*(?:,\d{2})?', '[AMOUNT]')  # Montos
        ]
        
        anonymized = content
        for pattern, replacement in patterns:
            anonymized = re.sub(pattern, replacement, anonymized, flags=re.IGNORECASE)
        
        return anonymized
    
    def _calculate_quality_score(self, metadata: DocumentMetadata) -> float:
        """Calcula score de calidad basado en múltiples factores."""
        score = 0.0
        
        # Factor por tipo de documento
        doc_config = self.document_categories.get(metadata.document_type, {})
        score += doc_config.get("legal_weight", 1.0)
        
        # Factor por nivel de experiencia
        experience_multiplier = {
            "maximo_valor": 3.0,
            "alto_valor": 2.0,
            "complementario": 1.0
        }
        score *= experience_multiplier.get(metadata.experience_level, 1.0)
        
        # Factor por longitud (documentos muy cortos o muy largos tienen menos valor)
        if 1000 <= metadata.text_length <= 50000:
            score *= 1.2
        elif metadata.text_length < 500:
            score *= 0.5
        
        # Factor por conceptos legales
        if len(metadata.legal_concepts) > 5:
            score *= 1.3
        
        # Factor por precedentes
        if len(metadata.precedents_referenced) > 0:
            score *= 1.2
        
        return min(score, 5.0)  # Máximo 5.0
    
    async def _generate_document_embeddings(self):
        """Genera embeddings para todos los documentos procesados."""
        if not self.processed_documents:
            return
        
        texts = [doc.processed_text for doc in self.processed_documents.values()]
        
        try:
            # Generar embeddings TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Asignar embeddings a documentos
            for i, (doc_id, doc_metadata) in enumerate(self.processed_documents.items()):
                doc_metadata.embedding_vector = tfidf_matrix[i].toarray().flatten()
            
            self.logger.info(f"Generated embeddings for {len(texts)} documents")
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
    
    async def _analyze_document_patterns(self):
        """Analiza patrones en la colección de documentos."""
        if not self.processed_documents:
            return
        
        # Agrupar por experiencia
        by_experience = defaultdict(list)
        for doc in self.processed_documents.values():
            by_experience[doc.experience_level].append(doc)
        
        # Estadísticas por experiencia
        for level, docs in by_experience.items():
            total_quality = sum(doc.quality_score for doc in docs)
            avg_quality = total_quality / len(docs) if docs else 0
            
            self.logger.info(f"Experience level {level}: {len(docs)} docs, avg quality: {avg_quality:.2f}")
    
    async def _save_processing_results(self):
        """Guarda resultados del procesamiento."""
        metadata_file = self.base_path / "processed/metadata/document_metadata.json"
        
        # Convertir a formato serializable
        serializable_docs = {}
        for doc_id, metadata in self.processed_documents.items():
            serializable_docs[doc_id] = {
                "document_id": metadata.document_id,
                "file_path": metadata.file_path,
                "document_type": metadata.document_type,
                "experience_level": metadata.experience_level,
                "sector": metadata.sector,
                "jurisdiction": metadata.jurisdiction,
                "quality_score": metadata.quality_score,
                "text_length": metadata.text_length,
                "legal_concepts": metadata.legal_concepts,
                "precedents_referenced": metadata.precedents_referenced,
                "creation_date": metadata.creation_date.isoformat()
            }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_docs, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved metadata for {len(serializable_docs)} documents")
    
    def get_training_dataset(self, min_quality_score: float = 2.0) -> List[Dict]:
        """
        Genera dataset de entrenamiento filtrado por calidad.
        
        Args:
            min_quality_score: Score mínimo de calidad para incluir documento
            
        Returns:
            Lista de documentos formateados para entrenamiento
        """
        training_data = []
        
        for doc in self.processed_documents.values():
            if doc.quality_score >= min_quality_score:
                training_sample = {
                    "text": doc.processed_text,
                    "metadata": {
                        "document_type": doc.document_type,
                        "experience_level": doc.experience_level,
                        "sector": doc.sector,
                        "jurisdiction": doc.jurisdiction,
                        "quality_score": doc.quality_score,
                        "legal_concepts": doc.legal_concepts,
                        "authored_by_user": doc.authored_by_user
                    }
                }
                training_data.append(training_sample)
        
        # Ordenar por calidad descendente
        training_data.sort(key=lambda x: x["metadata"]["quality_score"], reverse=True)
        
        return training_data


# Función de inicialización para uso fácil
async def initialize_document_processor(base_path: str = None) -> PrivateDocumentProcessor:
    """
    Inicializa procesador de documentos privados.
    
    Args:
        base_path: Ruta base para almacenar documentos procesados
        
    Returns:
        Procesador configurado y listo para uso
    """
    if base_path is None:
        base_path = "/home/user/SLM-Legal-Spanish/data/private_corpus"
    
    processor = PrivateDocumentProcessor(base_path)
    
    return processor


if __name__ == "__main__":
    """
    Ejemplo de uso del procesador de documentos privados.
    """
    import asyncio
    
    async def main():
        # Inicializar procesador
        processor = await initialize_document_processor()
        
        # Ejemplo de metadata del autor (tus datos)
        author_metadata = {
            "authored_by_user": True,
            "experience_years": 30,
            "roles": ["director_independiente", "abogado_corporativo", "consultor_ejecutivo"],
            "sectors_expertise": ["experiencia_corporativa_diversificada", "multisectorial"],
            "jurisdictions_expertise": ["AR", "ES", "CL", "UY"]
        }
        
        # Procesar colección (ajusta la ruta a tus documentos)
        input_path = "/path/to/your/document/collection"
        
        try:
            stats = await processor.process_document_collection(input_path, author_metadata)
            print("Processing completed:", stats)
            
            # Generar dataset de entrenamiento
            training_data = processor.get_training_dataset(min_quality_score=2.5)
            print(f"Generated training dataset with {len(training_data)} high-quality documents")
            
        except Exception as e:
            print(f"Processing failed: {e}")
    
    asyncio.run(main())