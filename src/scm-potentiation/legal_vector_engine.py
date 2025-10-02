"""
SCM Legal 2.0 - Vector Database Engine
Implementación de arquitectura vectorial especializada para corpus legal hispanoamericano
Basado en Step 3 del Framework Rahul Agarwal
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDocumentType(Enum):
    """Tipos de documentos legales para clasificación vectorial"""
    CONSTITUTION = "constitucion"
    CIVIL_CODE = "codigo_civil"
    COMMERCIAL_CODE = "codigo_comercial"
    LABOR_LAW = "ley_laboral"
    JURISPRUDENCE = "jurisprudencia"
    REGULATION = "regulacion"
    DECREE = "decreto"
    RESOLUTION = "resolucion"
    DOCTRINE = "doctrina"

class JurisdictionType(Enum):
    """Jurisdicciones soportadas en el sistema"""
    ARGENTINA = "argentina"
    CHILE = "chile"
    COLOMBIA = "colombia"
    MEXICO = "mexico"
    PERU = "peru"
    URUGUAY = "uruguay"
    VENEZUELA = "venezuela"

@dataclass
class LegalDocument:
    """Estructura de documento legal para indexación vectorial"""
    doc_id: str
    title: str
    content: str
    doc_type: LegalDocumentType
    jurisdiction: JurisdictionType
    publication_date: datetime
    legal_hierarchy: int  # 1=Constitución, 2=Código, 3=Ley, 4=Decreto, 5=Resolución
    articles: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VectorSearchResult:
    """Resultado de búsqueda vectorial con contexto legal"""
    doc_id: str
    title: str
    content_snippet: str
    similarity_score: float
    doc_type: str
    jurisdiction: str
    legal_hierarchy: int
    articles_matched: List[str]
    citation_count: int
    relevance_factors: Dict[str, float]

@dataclass
class LegalEmbeddingConfig:
    """Configuración para generación de embeddings legales"""
    model_name: str = "legal-bert-base"
    dimension: int = 768
    chunk_size: int = 512
    overlap: int = 50
    normalize: bool = True
    legal_context_weight: float = 0.3
    jurisdiction_weight: float = 0.2

class LegalVectorEngine:
    """
    Motor vectorial especializado para búsqueda semántica en corpus legal
    Implementa arquitectura híbrida con múltiples proveedores de embeddings
    """
    
    def __init__(self, config: LegalEmbeddingConfig = None):
        self.config = config or LegalEmbeddingConfig()
        self.vector_stores = {}
        self.embedding_models = {}
        self.legal_index = {}
        self.jurisdiction_filters = {}
        
        # Inicialización de proveedores vectoriales
        self._initialize_vector_stores()
        self._initialize_embedding_models()
        
        logger.info(f"Legal Vector Engine inicializado con {len(self.embedding_models)} modelos")
    
    def _initialize_vector_stores(self):
        """Inicializar proveedores de bases vectoriales"""
        
        # Configuración multi-provider para redundancia y optimización
        self.vector_stores = {
            "primary": {
                "provider": "pinecone",
                "index_name": "scm-legal-hispanoamerica",
                "dimension": 1536,
                "metric": "cosine",
                "replicas": 1,
                "pods": 1
            },
            
            "local_fallback": {
                "provider": "chroma",
                "collection_name": "legal-corpus-local", 
                "dimension": 768,
                "distance_function": "cosine",
                "hnsw_config": {"M": 16, "ef_construction": 200}
            },
            
            "specialized": {
                "provider": "weaviate",
                "class_name": "LegalDocument",
                "dimension": 1536, 
                "distance_metric": "cosine",
                "vectorizer": "none"  # Usamos embeddings custom
            }
        }
        
        logger.info("Configuración vectorial multi-provider inicializada")
    
    def _initialize_embedding_models(self):
        """Inicializar modelos de embeddings especializados"""
        
        self.embedding_models = {
            # Embeddings específicos para legal
            "legal_bert": {
                "model": "nlpaueb/legal-bert-base-uncased",
                "dimension": 768,
                "specialization": "legal_concepts",
                "language": "en",
                "local": True
            },
            
            # Embeddings multilingües para hispanoamérica
            "multilingual_legal": {
                "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "dimension": 384,
                "specialization": "multilingual_legal",
                "language": "es",
                "local": True
            },
            
            # Embeddings comerciales para casos complejos
            "openai_legal": {
                "model": "text-embedding-3-large", 
                "dimension": 1536,
                "specialization": "general_legal",
                "language": "multilingual",
                "local": False,
                "cost_per_1k": 0.00013
            },
            
            # Embeddings especializados en derecho hispanoamericano
            "voyage_legal": {
                "model": "voyage-law-2",
                "dimension": 1024,
                "specialization": "hispanoamerican_law",
                "language": "es",
                "local": False,
                "cost_per_1k": 0.00012
            },
            
            # Embeddings explicables para auditoría
            "nomic_legal": {
                "model": "nomic-embed-text-v1.5",
                "dimension": 768,
                "specialization": "explainable_legal",
                "language": "multilingual", 
                "local": True
            }
        }
        
        logger.info(f"Modelos de embeddings configurados: {list(self.embedding_models.keys())}")
    
    async def index_legal_document(self, document: LegalDocument) -> Dict[str, Any]:
        """
        Indexación de documento legal con múltiples estrategias vectoriales
        """
        
        try:
            # 1. Chunking inteligente por artículos/secciones
            document_chunks = await self._intelligent_legal_chunking(document)
            
            # 2. Generación de embeddings multi-modelo
            embeddings_results = await self._generate_multi_embeddings(document_chunks)
            
            # 3. Enriquecimiento con metadatos legales
            enriched_vectors = await self._enrich_legal_metadata(
                document, embeddings_results
            )
            
            # 4. Indexación en múltiples stores
            indexing_results = await self._index_to_vector_stores(enriched_vectors)
            
            # 5. Actualización de índices auxiliares
            await self._update_auxiliary_indexes(document)
            
            logger.info(f"Documento indexado exitosamente: {document.doc_id}")
            
            return {
                "doc_id": document.doc_id,
                "chunks_created": len(document_chunks),
                "embeddings_generated": len(embeddings_results),
                "stores_indexed": len(indexing_results),
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error indexando documento {document.doc_id}: {e}")
            return {
                "doc_id": document.doc_id,
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _intelligent_legal_chunking(self, document: LegalDocument) -> List[Dict[str, Any]]:
        """
        Chunking inteligente que respeta estructura legal (artículos, incisos, etc.)
        """
        
        chunks = []
        
        # Estrategia 1: Chunking por artículos (si están disponibles)
        if document.articles:
            for i, article in enumerate(document.articles):
                chunks.append({
                    "chunk_id": f"{document.doc_id}_art_{i+1}",
                    "content": article,
                    "type": "article",
                    "position": i + 1,
                    "parent_doc": document.doc_id
                })
        
        # Estrategia 2: Chunking semántico por párrafos legales
        else:
            content = document.content
            
            # Dividir por indicadores legales comunes
            legal_separators = [
                "Artículo", "ARTÍCULO", "Art.", "ART.",
                "Inciso", "INCISO", "Inc.", "INC.", 
                "Capítulo", "CAPÍTULO", "Cap.", "CAP.",
                "Sección", "SECCIÓN", "Sec.", "SEC."
            ]
            
            # Chunking básico con overlap
            chunk_size = self.config.chunk_size
            overlap = self.config.overlap
            
            for i in range(0, len(content), chunk_size - overlap):
                chunk_content = content[i:i + chunk_size]
                
                if chunk_content.strip():
                    chunks.append({
                        "chunk_id": f"{document.doc_id}_chunk_{i//chunk_size + 1}",
                        "content": chunk_content,
                        "type": "semantic_chunk",
                        "position": i // chunk_size + 1,
                        "parent_doc": document.doc_id
                    })
        
        logger.info(f"Creados {len(chunks)} chunks para documento {document.doc_id}")
        return chunks
    
    async def _generate_multi_embeddings(self, chunks: List[Dict[str, Any]]) -> Dict[str, List[np.ndarray]]:
        """
        Generación de embeddings con múltiples modelos especializados
        """
        
        embeddings_results = {}
        
        for model_name, model_config in self.embedding_models.items():
            try:
                # Simulación de embeddings (integrar con modelos reales)
                model_embeddings = []
                
                for chunk in chunks:
                    # Embedding simulado basado en configuración del modelo
                    embedding = await self._simulate_embedding(
                        chunk["content"], 
                        model_config["dimension"]
                    )
                    model_embeddings.append(embedding)
                
                embeddings_results[model_name] = model_embeddings
                logger.info(f"Embeddings generados con {model_name}: {len(model_embeddings)} vectores")
                
            except Exception as e:
                logger.warning(f"Error generando embeddings con {model_name}: {e}")
                continue
        
        return embeddings_results
    
    async def _simulate_embedding(self, text: str, dimension: int) -> np.ndarray:
        """
        Simulación de embedding (reemplazar con modelos reales)
        """
        # Simulación básica basada en hash del texto
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.normal(0, 1, dimension)
        
        # Normalización si está configurada
        if self.config.normalize:
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    async def _enrich_legal_metadata(self, document: LegalDocument, embeddings: Dict[str, List[np.ndarray]]) -> Dict[str, Any]:
        """
        Enriquecimiento con metadatos legales específicos
        """
        
        enriched_data = {
            "document": document,
            "embeddings": embeddings,
            "legal_metadata": {
                "hierarchy_score": self._calculate_hierarchy_score(document),
                "jurisdiction_vector": self._create_jurisdiction_vector(document.jurisdiction),
                "temporal_relevance": self._calculate_temporal_relevance(document.publication_date),
                "citation_authority": len(document.citations) / max(1, len(document.content.split())),
                "document_complexity": self._estimate_document_complexity(document)
            }
        }
        
        return enriched_data
    
    def _calculate_hierarchy_score(self, document: LegalDocument) -> float:
        """Cálculo de score jerárquico legal"""
        hierarchy_weights = {
            1: 1.0,    # Constitución
            2: 0.9,    # Código  
            3: 0.8,    # Ley
            4: 0.6,    # Decreto
            5: 0.4     # Resolución
        }
        return hierarchy_weights.get(document.legal_hierarchy, 0.2)
    
    def _create_jurisdiction_vector(self, jurisdiction: JurisdictionType) -> List[float]:
        """Vector de jurisdicción para filtrado geográfico"""
        jurisdictions = list(JurisdictionType)
        vector = [0.0] * len(jurisdictions)
        
        try:
            idx = jurisdictions.index(jurisdiction)
            vector[idx] = 1.0
        except ValueError:
            pass
        
        return vector
    
    def _calculate_temporal_relevance(self, pub_date: datetime) -> float:
        """Relevancia temporal del documento legal"""
        years_old = (datetime.now() - pub_date).days / 365.25
        
        # Decaimiento exponencial suave
        temporal_score = np.exp(-years_old * 0.05)  # 5% decay por año
        return max(0.1, min(1.0, temporal_score))
    
    def _estimate_document_complexity(self, document: LegalDocument) -> float:
        """Estimación de complejidad del documento"""
        
        complexity_factors = {
            "length": len(document.content.split()) / 10000,  # Normalizado por 10k palabras
            "articles": len(document.articles) / 100,  # Normalizado por 100 artículos
            "citations": len(document.citations) / 50,  # Normalizado por 50 citas
            "keywords": len(document.keywords) / 20   # Normalizado por 20 keywords
        }
        
        # Promedio ponderado de factores
        weights = [0.4, 0.3, 0.2, 0.1]
        complexity = sum(f * w for f, w in zip(complexity_factors.values(), weights))
        
        return max(0.1, min(1.0, complexity))
    
    async def _index_to_vector_stores(self, enriched_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Indexación en múltiples stores vectoriales
        """
        
        results = {}
        
        for store_name, store_config in self.vector_stores.items():
            try:
                # Simulación de indexación (integrar con stores reales)
                success = await self._simulate_vector_store_index(
                    store_config, enriched_data
                )
                results[store_name] = success
                
                if success:
                    logger.info(f"Indexado exitosamente en {store_name}")
                else:
                    logger.warning(f"Falló indexación en {store_name}")
                    
            except Exception as e:
                logger.error(f"Error indexando en {store_name}: {e}")
                results[store_name] = False
        
        return results
    
    async def _simulate_vector_store_index(self, store_config: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Simulación de indexación vectorial"""
        
        # Validaciones básicas
        if not data.get("embeddings"):
            return False
        
        if not data.get("document"):
            return False
        
        # Simulación de tiempo de procesamiento
        await asyncio.sleep(0.1)
        
        return True
    
    async def _update_auxiliary_indexes(self, document: LegalDocument):
        """Actualización de índices auxiliares para filtrado rápido"""
        
        # Índice por jurisdicción
        jurisdiction_key = document.jurisdiction.value
        if jurisdiction_key not in self.jurisdiction_filters:
            self.jurisdiction_filters[jurisdiction_key] = []
        self.jurisdiction_filters[jurisdiction_key].append(document.doc_id)
        
        # Índice por tipo de documento
        doc_type_key = document.doc_type.value
        if doc_type_key not in self.legal_index:
            self.legal_index[doc_type_key] = []
        self.legal_index[doc_type_key].append(document.doc_id)
        
        logger.info(f"Índices auxiliares actualizados para {document.doc_id}")
    
    async def semantic_search(self, 
                            query: str, 
                            jurisdiction: Optional[JurisdictionType] = None,
                            doc_types: Optional[List[LegalDocumentType]] = None,
                            top_k: int = 10,
                            similarity_threshold: float = 0.7) -> List[VectorSearchResult]:
        """
        Búsqueda semántica avanzada en corpus legal
        """
        
        try:
            # 1. Generación de embeddings para query
            query_embeddings = await self._generate_query_embeddings(query)
            
            # 2. Búsqueda vectorial con filtros
            search_results = await self._vector_search_with_filters(
                query_embeddings, jurisdiction, doc_types, top_k * 2  # Buscar más para filtrar
            )
            
            # 3. Re-ranking con factores legales específicos
            reranked_results = await self._legal_reranking(
                search_results, query, similarity_threshold
            )
            
            # 4. Filtrado final y limitación a top_k
            final_results = reranked_results[:top_k]
            
            logger.info(f"Búsqueda completada: {len(final_results)} resultados para '{query[:50]}...'")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    async def _generate_query_embeddings(self, query: str) -> Dict[str, np.ndarray]:
        """Generación de embeddings para query con múltiples modelos"""
        
        query_embeddings = {}
        
        for model_name, model_config in self.embedding_models.items():
            try:
                embedding = await self._simulate_embedding(query, model_config["dimension"])
                query_embeddings[model_name] = embedding
                
            except Exception as e:
                logger.warning(f"Error generando embedding de query con {model_name}: {e}")
                continue
        
        return query_embeddings
    
    async def _vector_search_with_filters(self, 
                                        query_embeddings: Dict[str, np.ndarray],
                                        jurisdiction: Optional[JurisdictionType],
                                        doc_types: Optional[List[LegalDocumentType]],
                                        top_k: int) -> List[VectorSearchResult]:
        """Búsqueda vectorial con filtros jurisdiccionales y de tipo"""
        
        # Simulación de resultados de búsqueda vectorial
        simulated_results = []
        
        # Generar resultados simulados realistas
        for i in range(top_k):
            doc_id = f"doc_{i+1:03d}"
            similarity = max(0.5, 0.95 - (i * 0.03) + np.random.normal(0, 0.02))
            
            result = VectorSearchResult(
                doc_id=doc_id,
                title=f"Documento Legal Simulado {i+1}",
                content_snippet=f"Extracto relevante del documento {i+1} relacionado con la consulta legal...",
                similarity_score=round(similarity, 3),
                doc_type=LegalDocumentType.CIVIL_CODE.value if i % 3 == 0 else LegalDocumentType.JURISPRUDENCE.value,
                jurisdiction=jurisdiction.value if jurisdiction else JurisdictionType.ARGENTINA.value,
                legal_hierarchy=2 if i % 3 == 0 else 4,
                articles_matched=[f"Art. {10+i}", f"Art. {20+i}"],
                citation_count=max(1, 15 - i),
                relevance_factors={
                    "semantic_similarity": similarity,
                    "hierarchy_boost": 0.1 if i % 3 == 0 else 0.0,
                    "temporal_relevance": 0.9 - (i * 0.02),
                    "jurisdiction_match": 0.2 if jurisdiction else 0.0
                }
            )
            
            simulated_results.append(result)
        
        return simulated_results
    
    async def _legal_reranking(self, 
                             results: List[VectorSearchResult], 
                             query: str, 
                             threshold: float) -> List[VectorSearchResult]:
        """Re-ranking con factores específicos legales"""
        
        reranked = []
        
        for result in results:
            # Cálculo de score compuesto
            legal_score = self._calculate_legal_relevance_score(result, query)
            
            # Filtrar por umbral
            if legal_score >= threshold:
                # Actualizar score en el resultado
                result.similarity_score = legal_score
                reranked.append(result)
        
        # Ordenar por score legal compuesto
        reranked.sort(key=lambda r: r.similarity_score, reverse=True)
        
        return reranked
    
    def _calculate_legal_relevance_score(self, result: VectorSearchResult, query: str) -> float:
        """Cálculo de relevancia legal compuesta"""
        
        # Factores de relevancia legal
        factors = result.relevance_factors
        
        # Ponderación de factores
        weights = {
            "semantic_similarity": 0.4,
            "hierarchy_boost": 0.25,
            "temporal_relevance": 0.15,
            "jurisdiction_match": 0.1,
            "citation_authority": 0.1
        }
        
        # Score compuesto
        legal_score = sum(
            factors.get(factor, 0) * weight 
            for factor, weight in weights.items()
        )
        
        # Boost por coincidencias exactas en título
        if any(word.lower() in result.title.lower() for word in query.split()):
            legal_score += 0.1
        
        # Penalty por documentos muy antiguos o de baja jerarquía
        if result.legal_hierarchy > 3:
            legal_score *= 0.9
        
        return max(0.0, min(1.0, legal_score))
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Estadísticas del índice vectorial legal"""
        
        total_docs = sum(len(docs) for docs in self.jurisdiction_filters.values())
        
        return {
            "total_documents": total_docs,
            "jurisdictions": list(self.jurisdiction_filters.keys()),
            "document_types": list(self.legal_index.keys()),
            "embedding_models": len(self.embedding_models),
            "vector_stores": len(self.vector_stores),
            "index_health": "healthy" if total_docs > 0 else "empty",
            "last_updated": datetime.now().isoformat()
        }

# Función demo para testing
async def demo_legal_vector_engine():
    """Demo del motor vectorial legal"""
    
    print("🔍 SCM Legal Vector Engine - Demo\n")
    
    # Inicializar motor
    vector_engine = LegalVectorEngine()
    
    # Documento de prueba
    test_document = LegalDocument(
        doc_id="test_001",
        title="Código Civil y Comercial de la Nación - Responsabilidad Civil",
        content="La responsabilidad civil se configura cuando se dan los elementos: daño, antijuridicidad, factor de atribución y nexo causal. El daño debe ser cierto, personal y subsistente...",
        doc_type=LegalDocumentType.CIVIL_CODE,
        jurisdiction=JurisdictionType.ARGENTINA,
        publication_date=datetime(2015, 8, 1),
        legal_hierarchy=2,
        articles=["Art. 1710", "Art. 1711", "Art. 1712"],
        keywords=["responsabilidad civil", "daño", "nexo causal"],
        citations=["Fallos 341:611", "Fallos 325:2275"]
    )
    
    # 1. Indexación
    print("📚 Indexando documento legal...")
    index_result = await vector_engine.index_legal_document(test_document)
    print(f"✅ Indexación: {index_result['status']}")
    print(f"📊 Chunks creados: {index_result['chunks_created']}")
    
    # 2. Búsqueda semántica
    print("\n🔍 Realizando búsqueda semántica...")
    search_results = await vector_engine.semantic_search(
        query="responsabilidad por daños en accidente de tránsito",
        jurisdiction=JurisdictionType.ARGENTINA,
        top_k=5
    )
    
    print(f"📋 Resultados encontrados: {len(search_results)}")
    for i, result in enumerate(search_results[:3], 1):
        print(f"\n{i}. {result.title}")
        print(f"   Similitud: {result.similarity_score:.1%}")
        print(f"   Tipo: {result.doc_type}")
        print(f"   Artículos: {', '.join(result.articles_matched)}")
    
    # 3. Estadísticas
    print(f"\n📊 Estadísticas del índice:")
    stats = vector_engine.get_index_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

# Ejecutar demo
if __name__ == "__main__":
    asyncio.run(demo_legal_vector_engine())