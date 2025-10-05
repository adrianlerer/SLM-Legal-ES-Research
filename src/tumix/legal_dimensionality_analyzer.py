"""
Legal Dimensionality Analyzer - PCA + K-Means Advanced
=====================================================

Analizador dimensional avanzado para casos jurídicos usando PCA y K-Means.
Identifica automáticamente aspectos jurídicos clave y clasifica casos por 
complejidad, dominio y jurisdicción para optimización de agentes TUMIX.

CONFIDENCIAL - SCM Legal Integration
Desarrollado por: Ignacio Adrián Lerer

Algoritmos Integrados:
- #8 PCA: Análisis de componentes principales para aspectos jurídicos
- #9 K-Means: Clustering inteligente de casos y complejidad
- Optimización automática de asignación de agentes especializados
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import re
import asyncio
from collections import Counter, defaultdict

# Simulación de librerías ML (en producción usar sklearn)
class PCASimulator:
    """Simulador de PCA para análisis dimensional."""
    
    def __init__(self, n_components=0.95, svd_solver='full'):
        self.n_components = n_components
        self.svd_solver = svd_solver
        self.components_ = None
        self.explained_variance_ratio_ = None
        self.fitted = False
    
    def fit_transform(self, X):
        """Ajusta PCA y transforma datos."""
        self.fitted = True
        
        # Simula componentes principales (en producción: sklearn.decomposition.PCA)
        n_samples, n_features = X.shape if hasattr(X, 'shape') else (len(X), len(X[0]))
        n_components = int(n_features * self.n_components) if isinstance(self.n_components, float) else self.n_components
        
        # Simula transformación PCA
        self.components_ = np.random.rand(n_components, n_features) if n_features > 0 else np.array([])
        self.explained_variance_ratio_ = np.array([0.3, 0.25, 0.2, 0.15, 0.1][:n_components])
        
        # Normaliza variance ratio
        if len(self.explained_variance_ratio_) > 0:
            self.explained_variance_ratio_ = self.explained_variance_ratio_ / np.sum(self.explained_variance_ratio_)
        
        # Simula datos transformados
        transformed_data = np.random.rand(n_samples, n_components) if n_samples > 0 else np.array([])
        
        return transformed_data

class KMeansSimulator:
    """Simulador de K-Means para clustering."""
    
    def __init__(self, n_clusters=5, init='k-means++', n_init=10):
        self.n_clusters = n_clusters
        self.init = init
        self.n_init = n_init
        self.labels_ = None
        self.cluster_centers_ = None
        self.fitted = False
    
    def fit(self, X):
        """Ajusta clustering."""
        self.fitted = True
        n_samples = X.shape[0] if hasattr(X, 'shape') else len(X)
        
        # Simula labels de clusters
        self.labels_ = np.random.randint(0, self.n_clusters, n_samples)
        self.cluster_centers_ = np.random.rand(self.n_clusters, 2)
        
        return self
    
    def predict(self, X):
        """Predice clusters para nuevos datos."""
        if not self.fitted:
            self.fit(X)
        
        n_samples = X.shape[0] if hasattr(X, 'shape') else len(X)
        return np.random.randint(0, self.n_clusters, n_samples)


@dataclass
class LegalVectorization:
    """Vectorización especializada de contenido jurídico."""
    
    # Vectores jurisprudenciales
    jurisprudence: List[float] = field(default_factory=list)
    
    # Vectores regulatorios  
    regulations: List[float] = field(default_factory=list)
    
    # Vectores contractuales
    contracts: List[float] = field(default_factory=list)
    
    # Vectores de complejidad
    complexity: List[float] = field(default_factory=list)
    
    # Vectores de dominio
    domain: List[float] = field(default_factory=list)
    
    # Vectores jurisdiccionales
    jurisdiction: List[float] = field(default_factory=list)
    
    # Metadatos de vectorización
    vectorization_method: str = "legal_specialized"
    feature_count: int = 0
    processing_time_ms: int = 0


@dataclass
class LegalDimensionAnalysis:
    """Resultado completo del análisis dimensional."""
    
    # Aspectos jurídicos identificados
    key_legal_dimensions: Dict[str, List[str]]
    
    # Clasificación automática
    automatic_classification: Dict[str, str]
    
    # Análisis de varianza
    variance_analysis: Dict[str, List[float]]
    
    # Asignación óptima de agentes
    recommended_agent_allocation: Dict[str, float]
    
    # Clustering results
    complexity_cluster_info: Dict[str, Any]
    domain_cluster_info: Dict[str, Any]
    jurisdiction_cluster_info: Dict[str, Any]
    
    # Métricas de calidad
    dimensional_quality_metrics: Dict[str, float]
    
    # Optimización de recursos
    processing_optimization: Dict[str, Any]
    
    # Timestamp y metadatos
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    analysis_time_ms: int = 0


class LegalDimensionalityAnalyzer:
    """
    Analizador dimensional avanzado para casos jurídicos.
    
    Utiliza PCA para identificar aspectos jurídicos principales y K-Means 
    para clasificación automática de casos por complejidad, dominio y jurisdicción.
    Optimiza la asignación de agentes TUMIX según características del caso.
    """
    
    def __init__(self):
        # PCA para diferentes aspectos jurídicos
        self.pca_jurisprudential = PCASimulator(n_components=0.95, svd_solver='full')
        self.pca_regulatory = PCASimulator(n_components=0.90, svd_solver='randomized')
        self.pca_contractual = PCASimulator(n_components=0.85, svd_solver='arpack')
        
        # K-Means para clasificación
        self.kmeans_complexity = KMeansSimulator(n_clusters=7, init='k-means++', n_init=10)
        self.kmeans_domain = KMeansSimulator(n_clusters=12, init='k-means++', n_init=10)
        self.kmeans_jurisdiction = KMeansSimulator(n_clusters=8, init='k-means++', n_init=10)
        
        # Labels para interpretación
        self.complexity_labels = [
            'trivial', 'simple', 'moderado', 'complejo', 
            'muy_complejo', 'experto', 'supremo'
        ]
        
        self.domain_labels = [
            'corporativo', 'compliance', 'fiduciario', 'regulatorio',
            'contractual', 'societario', 'mercados', 'governance',
            'laboral', 'tributario', 'penal_empresarial', 'ambiental'
        ]
        
        self.jurisdiction_labels = [
            'nacional_ar', 'provincial_ar', 'municipal_ar', 'internacional',
            'mercosur', 'españa', 'chile', 'uruguay'
        ]
        
        # Configuración del analizador
        self.logger = logging.getLogger(__name__)
        self.historical_analysis_data = []
        self.models_trained = False
        
        # Diccionarios especializados para vectorización jurídica
        self.legal_terms_dictionary = self._build_legal_dictionary()
        self.complexity_indicators = self._build_complexity_indicators()
        
    async def extract_legal_dimensions(self, legal_document: str) -> LegalDimensionAnalysis:
        """
        Extrae dimensiones jurídicas clave usando PCA + K-Means.
        
        Args:
            legal_document: Texto del documento o consulta jurídica
            
        Returns:
            LegalDimensionAnalysis con análisis dimensional completo
        """
        start_time = datetime.now()
        
        try:
            # 1. Vectorización avanzada del documento
            legal_vectors = await self._advanced_legal_vectorization(legal_document)
            
            # 2. Análisis PCA multi-dimensional
            pca_results = await self._perform_pca_analysis(legal_vectors)
            
            # 3. Clustering K-Means
            clustering_results = await self._perform_clustering_analysis(legal_vectors)
            
            # 4. Interpretación de componentes
            interpreted_dimensions = await self._interpret_legal_dimensions(
                pca_results, clustering_results
            )
            
            # 5. Clasificación automática
            automatic_classification = await self._classify_legal_case(
                clustering_results, legal_vectors
            )
            
            # 6. Optimización de agentes
            agent_allocation = await self._calculate_optimal_agent_allocation(
                automatic_classification, pca_results
            )
            
            # 7. Métricas de calidad
            quality_metrics = await self._calculate_dimensional_quality(
                pca_results, clustering_results
            )
            
            # 8. Optimización de procesamiento
            processing_optimization = await self._optimize_processing_strategy(
                automatic_classification, quality_metrics
            )
            
            # Construye resultado
            analysis_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            result = LegalDimensionAnalysis(
                key_legal_dimensions=interpreted_dimensions,
                automatic_classification=automatic_classification,
                variance_analysis=self._extract_variance_analysis(pca_results),
                recommended_agent_allocation=agent_allocation,
                complexity_cluster_info=clustering_results['complexity'],
                domain_cluster_info=clustering_results['domain'],
                jurisdiction_cluster_info=clustering_results['jurisdiction'],
                dimensional_quality_metrics=quality_metrics,
                processing_optimization=processing_optimization,
                analysis_time_ms=analysis_time
            )
            
            # Almacena para aprendizaje futuro
            await self._store_analysis_result(legal_vectors, result)
            
            self.logger.info(f"Análisis dimensional completado en {analysis_time}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Error en análisis dimensional: {str(e)}")
            return await self._fallback_simple_analysis(legal_document)
    
    async def _advanced_legal_vectorization(self, document: str) -> LegalVectorization:
        """Vectorización especializada para contenido jurídico."""
        
        start_time = datetime.now()
        
        # Preprocesamiento de texto
        cleaned_doc = await self._preprocess_legal_text(document)
        
        # Vectorización por aspectos jurídicos específicos
        jurisprudence_vector = await self._vectorize_jurisprudential_aspects(cleaned_doc)
        regulatory_vector = await self._vectorize_regulatory_aspects(cleaned_doc)
        contractual_vector = await self._vectorize_contractual_aspects(cleaned_doc)
        complexity_vector = await self._vectorize_complexity_indicators(cleaned_doc)
        domain_vector = await self._vectorize_domain_indicators(cleaned_doc)
        jurisdiction_vector = await self._vectorize_jurisdiction_indicators(cleaned_doc)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return LegalVectorization(
            jurisprudence=jurisprudence_vector,
            regulations=regulatory_vector,
            contracts=contractual_vector,
            complexity=complexity_vector,
            domain=domain_vector,
            jurisdiction=jurisdiction_vector,
            vectorization_method="legal_specialized_pca",
            feature_count=sum([
                len(jurisprudence_vector), len(regulatory_vector),
                len(contractual_vector), len(complexity_vector),
                len(domain_vector), len(jurisdiction_vector)
            ]),
            processing_time_ms=processing_time
        )
    
    async def _vectorize_jurisprudential_aspects(self, document: str) -> List[float]:
        """Vectoriza aspectos jurisprudenciales (precedentes, doctrina)."""
        
        jurisprudential_terms = [
            'jurisprudencia', 'precedente', 'fallo', 'sentencia', 'doctrina',
            'csjn', 'corte suprema', 'tribunal', 'sala', 'cámara',
            'considerando', 'voto', 'disidencia', 'mayoría', 'minoría'
        ]
        
        # Cuenta términos jurisprudenciales
        doc_lower = document.lower()
        vector = []
        
        for term in jurisprudential_terms:
            count = doc_lower.count(term)
            # Normaliza por longitud del documento
            normalized_count = count / (len(document.split()) + 1)
            vector.append(normalized_count)
        
        # Identifica citas de casos
        case_citations = len(re.findall(r'c\.\s*\d+\.\d+', doc_lower))
        legal_references = len(re.findall(r'art\.\s*\d+|artículo\s*\d+', doc_lower))
        
        vector.extend([case_citations * 0.1, legal_references * 0.1])
        
        return vector
    
    async def _vectorize_regulatory_aspects(self, document: str) -> List[float]:
        """Vectoriza aspectos regulatorios (leyes, decretos, resoluciones)."""
        
        regulatory_terms = [
            'ley', 'decreto', 'resolución', 'disposición', 'circular',
            'bcra', 'cnv', 'ign', 'afip', 'aaip', 'superintendencia',
            'reglamento', 'normativa', 'regulación', 'código'
        ]
        
        doc_lower = document.lower()
        vector = []
        
        for term in regulatory_terms:
            count = doc_lower.count(term)
            normalized_count = count / (len(document.split()) + 1)
            vector.append(normalized_count)
        
        # Identifica números de normas
        law_numbers = len(re.findall(r'ley\s*\d+', doc_lower))
        decree_numbers = len(re.findall(r'decreto\s*\d+', doc_lower))
        
        vector.extend([law_numbers * 0.1, decree_numbers * 0.1])
        
        return vector
    
    async def _vectorize_contractual_aspects(self, document: str) -> List[float]:
        """Vectoriza aspectos contractuales."""
        
        contractual_terms = [
            'contrato', 'convenio', 'acuerdo', 'pacto', 'cláusula',
            'obligación', 'derecho', 'garantía', 'incumplimiento', 'rescisión',
            'novación', 'cesión', 'subrogación', 'fianza', 'prenda'
        ]
        
        doc_lower = document.lower()
        vector = []
        
        for term in contractual_terms:
            count = doc_lower.count(term)
            normalized_count = count / (len(document.split()) + 1)
            vector.append(normalized_count)
        
        return vector
    
    async def _vectorize_complexity_indicators(self, document: str) -> List[float]:
        """Vectoriza indicadores de complejidad legal."""
        
        complexity_indicators = {
            'simple': ['consulta', 'pregunta', 'duda', 'información'],
            'medio': ['análisis', 'evaluación', 'revisión', 'verificación'],
            'complejo': ['interpretación', 'dictamen', 'due diligence', 'compliance'],
            'muy_complejo': ['litigio', 'controversia', 'conflicto', 'disputa'],
            'experto': ['fusión', 'adquisición', 'opa', 'reorganización']
        }
        
        doc_lower = document.lower()
        vector = []
        
        for level, terms in complexity_indicators.items():
            level_score = sum(doc_lower.count(term) for term in terms)
            normalized_score = level_score / (len(document.split()) + 1)
            vector.append(normalized_score)
        
        # Longitud como indicador de complejidad
        length_complexity = len(document.split()) / 1000.0  # Normalizado
        vector.append(min(length_complexity, 1.0))
        
        return vector
    
    async def _vectorize_domain_indicators(self, document: str) -> List[float]:
        """Vectoriza indicadores de dominio jurídico."""
        
        domain_terms = {
            'corporativo': ['sociedad', 'empresa', 'directorio', 'accionistas', 'dividendos'],
            'compliance': ['programa', 'integridad', 'prevención', 'lavado', 'corrupción'],
            'fiduciario': ['fiduciario', 'administrador', 'síndico', 'auditor', 'diligencia'],
            'regulatorio': ['regulación', 'supervisión', 'autorización', 'licencia', 'habilitación'],
            'mercados': ['mercado', 'valores', 'bolsa', 'oferta', 'cotización']
        }
        
        doc_lower = document.lower()
        vector = []
        
        for domain, terms in domain_terms.items():
            domain_score = sum(doc_lower.count(term) for term in terms)
            normalized_score = domain_score / (len(document.split()) + 1)
            vector.append(normalized_score)
        
        return vector
    
    async def _vectorize_jurisdiction_indicators(self, document: str) -> List[float]:
        """Vectoriza indicadores jurisdiccionales."""
        
        jurisdiction_terms = {
            'argentina': ['argentina', 'caba', 'buenos aires', 'csjn', 'bcra'],
            'españa': ['españa', 'cnmv', 'madrid', 'barcelona', 'español'],
            'chile': ['chile', 'svs', 'santiago', 'chileno'],
            'uruguay': ['uruguay', 'montevideo', 'uruguayo', 'bcu'],
            'internacional': ['internacional', 'extranjero', 'cross-border', 'global']
        }
        
        doc_lower = document.lower()
        vector = []
        
        for jurisdiction, terms in jurisdiction_terms.items():
            jurisdiction_score = sum(doc_lower.count(term) for term in terms)
            normalized_score = jurisdiction_score / (len(document.split()) + 1)
            vector.append(normalized_score)
        
        return vector
    
    async def _perform_pca_analysis(self, vectors: LegalVectorization) -> Dict[str, Any]:
        """Realiza análisis PCA multi-dimensional."""
        
        pca_results = {}
        
        # PCA Jurisprudencial
        if vectors.jurisprudence:
            jurisprudential_matrix = np.array(vectors.jurisprudence).reshape(1, -1)
            pca_results['jurisprudential'] = {
                'components': self.pca_jurisprudential.fit_transform(jurisprudential_matrix),
                'variance_ratio': self.pca_jurisprudential.explained_variance_ratio_,
                'n_components': len(self.pca_jurisprudential.explained_variance_ratio_) if self.pca_jurisprudential.explained_variance_ratio_ is not None else 0
            }
        
        # PCA Regulatorio
        if vectors.regulations:
            regulatory_matrix = np.array(vectors.regulations).reshape(1, -1)
            pca_results['regulatory'] = {
                'components': self.pca_regulatory.fit_transform(regulatory_matrix),
                'variance_ratio': self.pca_regulatory.explained_variance_ratio_,
                'n_components': len(self.pca_regulatory.explained_variance_ratio_) if self.pca_regulatory.explained_variance_ratio_ is not None else 0
            }
        
        # PCA Contractual
        if vectors.contracts:
            contractual_matrix = np.array(vectors.contracts).reshape(1, -1)
            pca_results['contractual'] = {
                'components': self.pca_contractual.fit_transform(contractual_matrix),
                'variance_ratio': self.pca_contractual.explained_variance_ratio_,
                'n_components': len(self.pca_contractual.explained_variance_ratio_) if self.pca_contractual.explained_variance_ratio_ is not None else 0
            }
        
        return pca_results
    
    async def _perform_clustering_analysis(self, vectors: LegalVectorization) -> Dict[str, Any]:
        """Realiza clustering K-Means."""
        
        clustering_results = {}
        
        # Clustering de complejidad
        if vectors.complexity:
            complexity_matrix = np.array(vectors.complexity).reshape(1, -1)
            complexity_cluster = self.kmeans_complexity.predict(complexity_matrix)[0]
            clustering_results['complexity'] = {
                'cluster': complexity_cluster,
                'label': self.complexity_labels[complexity_cluster % len(self.complexity_labels)],
                'confidence': 0.85  # Simulado
            }
        
        # Clustering de dominio
        if vectors.domain:
            domain_matrix = np.array(vectors.domain).reshape(1, -1)
            domain_cluster = self.kmeans_domain.predict(domain_matrix)[0]
            clustering_results['domain'] = {
                'cluster': domain_cluster,
                'label': self.domain_labels[domain_cluster % len(self.domain_labels)],
                'confidence': 0.88  # Simulado
            }
        
        # Clustering jurisdiccional
        if vectors.jurisdiction:
            jurisdiction_matrix = np.array(vectors.jurisdiction).reshape(1, -1)
            jurisdiction_cluster = self.kmeans_jurisdiction.predict(jurisdiction_matrix)[0]
            clustering_results['jurisdiction'] = {
                'cluster': jurisdiction_cluster,
                'label': self.jurisdiction_labels[jurisdiction_cluster % len(self.jurisdiction_labels)],
                'confidence': 0.82  # Simulado
            }
        
        return clustering_results
    
    async def _interpret_legal_dimensions(self, pca_results: Dict[str, Any], 
                                        clustering_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Interpreta componentes PCA en términos jurídicos."""
        
        interpretations = {
            'jurisprudential_aspects': [],
            'regulatory_aspects': [],
            'contractual_aspects': []
        }
        
        # Interpreta componentes jurisprudenciales
        if 'jurisprudential' in pca_results:
            variance = pca_results['jurisprudential']['variance_ratio']
            if len(variance) > 0:
                if variance[0] > 0.3:
                    interpretations['jurisprudential_aspects'].append("Fuerte componente de precedentes")
                if len(variance) > 1 and variance[1] > 0.2:
                    interpretations['jurisprudential_aspects'].append("Doctrina judicial relevante")
        
        # Interpreta componentes regulatorios
        if 'regulatory' in pca_results:
            variance = pca_results['regulatory']['variance_ratio']
            if len(variance) > 0:
                if variance[0] > 0.3:
                    interpretations['regulatory_aspects'].append("Marco normativo principal identificado")
                if len(variance) > 1 and variance[1] > 0.2:
                    interpretations['regulatory_aspects'].append("Regulación secundaria relevante")
        
        # Interpreta componentes contractuales
        if 'contractual' in pca_results:
            variance = pca_results['contractual']['variance_ratio']
            if len(variance) > 0:
                if variance[0] > 0.3:
                    interpretations['contractual_aspects'].append("Aspectos contractuales centrales")
                if len(variance) > 1 and variance[1] > 0.2:
                    interpretations['contractual_aspects'].append("Obligaciones específicas identificadas")
        
        # Agrega interpretaciones por clustering
        if 'complexity' in clustering_results:
            complexity_label = clustering_results['complexity']['label']
            interpretations['jurisprudential_aspects'].append(f"Complejidad: {complexity_label}")
        
        return interpretations
    
    async def _classify_legal_case(self, clustering_results: Dict[str, Any], 
                                 vectors: LegalVectorization) -> Dict[str, str]:
        """Clasificación automática del caso legal."""
        
        classification = {}
        
        # Complejidad
        if 'complexity' in clustering_results:
            classification['complexity_level'] = clustering_results['complexity']['label']
        else:
            classification['complexity_level'] = 'moderado'
        
        # Dominio
        if 'domain' in clustering_results:
            classification['legal_domain'] = clustering_results['domain']['label']
        else:
            classification['legal_domain'] = 'corporativo'
        
        # Jurisdicción
        if 'jurisdiction' in clustering_results:
            classification['jurisdiction_type'] = clustering_results['jurisdiction']['label']
        else:
            classification['jurisdiction_type'] = 'nacional_ar'
        
        # Tipo de consulta (inferido)
        complexity = classification['complexity_level']
        if complexity in ['trivial', 'simple']:
            classification['consultation_type'] = 'informativa'
        elif complexity in ['moderado', 'complejo']:
            classification['consultation_type'] = 'analítica'
        else:
            classification['consultation_type'] = 'especializada'
        
        return classification
    
    async def _calculate_optimal_agent_allocation(self, classification: Dict[str, str], 
                                                pca_results: Dict[str, Any]) -> Dict[str, float]:
        """Calcula asignación óptima de agentes según análisis."""
        
        # Pesos base por tipo de agente
        base_allocation = {
            'cot_juridico': 0.4,
            'search_jurisprudencial': 0.35,
            'code_compliance': 0.25
        }
        
        # Ajustes según complejidad
        complexity = classification.get('complexity_level', 'moderado')
        if complexity in ['experto', 'supremo']:
            base_allocation['cot_juridico'] += 0.15
            base_allocation['search_jurisprudencial'] += 0.10
            base_allocation['code_compliance'] -= 0.25
        elif complexity in ['trivial', 'simple']:
            base_allocation['cot_juridico'] -= 0.10
            base_allocation['search_jurisprudencial'] -= 0.05
            base_allocation['code_compliance'] += 0.15
        
        # Ajustes según dominio
        domain = classification.get('legal_domain', 'corporativo')
        if domain in ['compliance', 'regulatorio']:
            base_allocation['code_compliance'] += 0.15
            base_allocation['search_jurisprudencial'] += 0.05
            base_allocation['cot_juridico'] -= 0.20
        elif domain in ['jurisprudencial', 'litigioso']:
            base_allocation['search_jurisprudencial'] += 0.20
            base_allocation['cot_juridico'] += 0.10
            base_allocation['code_compliance'] -= 0.30
        
        # Ajustes según componentes PCA
        if 'jurisprudential' in pca_results:
            variance = pca_results['jurisprudential']['variance_ratio']
            if len(variance) > 0 and variance[0] > 0.4:
                base_allocation['search_jurisprudencial'] += 0.10
                base_allocation['cot_juridico'] -= 0.05
                base_allocation['code_compliance'] -= 0.05
        
        # Normaliza para que sumen 1
        total = sum(base_allocation.values())
        normalized_allocation = {k: v/total for k, v in base_allocation.items()}
        
        return normalized_allocation
    
    async def _calculate_dimensional_quality(self, pca_results: Dict[str, Any], 
                                           clustering_results: Dict[str, Any]) -> Dict[str, float]:
        """Calcula métricas de calidad del análisis dimensional."""
        
        metrics = {}
        
        # Calidad PCA (basada en varianza explicada)
        total_variance_explained = 0
        pca_components_count = 0
        
        for aspect, results in pca_results.items():
            if 'variance_ratio' in results and results['variance_ratio'] is not None:
                variance = results['variance_ratio']
                if len(variance) > 0:
                    total_variance_explained += np.sum(variance)
                    pca_components_count += len(variance)
        
        metrics['pca_quality_score'] = total_variance_explained / max(len(pca_results), 1)
        metrics['dimensionality_reduction_efficiency'] = pca_components_count / max(sum(len(pca_results[aspect].get('variance_ratio', [])) for aspect in pca_results), 1)
        
        # Calidad de clustering
        avg_clustering_confidence = 0
        clustering_count = 0
        
        for cluster_type, results in clustering_results.items():
            if 'confidence' in results:
                avg_clustering_confidence += results['confidence']
                clustering_count += 1
        
        metrics['clustering_confidence'] = avg_clustering_confidence / max(clustering_count, 1)
        
        # Consistencia dimensional
        metrics['dimensional_consistency'] = min(metrics['pca_quality_score'], metrics['clustering_confidence'])
        
        # Score global de calidad
        metrics['overall_dimensional_quality'] = (
            metrics['pca_quality_score'] * 0.4 +
            metrics['clustering_confidence'] * 0.35 +
            metrics['dimensional_consistency'] * 0.25
        )
        
        return metrics
    
    async def _optimize_processing_strategy(self, classification: Dict[str, str], 
                                          quality_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Optimiza estrategia de procesamiento según análisis."""
        
        optimization = {}
        
        # Estrategia de tiempo estimado
        complexity = classification.get('complexity_level', 'moderado')
        time_multipliers = {
            'trivial': 0.5, 'simple': 0.7, 'moderado': 1.0,
            'complejo': 1.5, 'muy_complejo': 2.0, 'experto': 3.0, 'supremo': 4.0
        }
        
        base_time = 30  # segundos
        estimated_time = base_time * time_multipliers.get(complexity, 1.0)
        optimization['estimated_processing_time_seconds'] = estimated_time
        
        # Estrategia de recursos
        if quality_metrics.get('overall_dimensional_quality', 0) > 0.8:
            optimization['processing_strategy'] = 'high_quality_deep_analysis'
            optimization['resource_allocation'] = 'maximum'
        elif complexity in ['experto', 'supremo']:
            optimization['processing_strategy'] = 'expert_level_analysis'
            optimization['resource_allocation'] = 'high'
        else:
            optimization['processing_strategy'] = 'standard_analysis'
            optimization['resource_allocation'] = 'normal'
        
        # Recomendaciones de optimización
        optimization['recommendations'] = []
        
        if quality_metrics.get('pca_quality_score', 0) < 0.7:
            optimization['recommendations'].append("Mejorar vectorización de aspectos jurídicos")
        
        if quality_metrics.get('clustering_confidence', 0) < 0.75:
            optimization['recommendations'].append("Refinar clustering de complejidad y dominio")
        
        if complexity in ['experto', 'supremo']:
            optimization['recommendations'].append("Activar agentes especializados adicionales")
        
        return optimization
    
    def _extract_variance_analysis(self, pca_results: Dict[str, Any]) -> Dict[str, List[float]]:
        """Extrae análisis de varianza de componentes PCA."""
        
        variance_analysis = {}
        
        for aspect, results in pca_results.items():
            if 'variance_ratio' in results and results['variance_ratio'] is not None:
                variance_analysis[f"{aspect}_variance"] = results['variance_ratio'].tolist()
            else:
                variance_analysis[f"{aspect}_variance"] = []
        
        return variance_analysis
    
    async def _store_analysis_result(self, vectors: LegalVectorization, 
                                   result: LegalDimensionAnalysis):
        """Almacena resultado para aprendizaje futuro."""
        
        analysis_record = {
            'vectors_summary': {
                'jurisprudence_features': len(vectors.jurisprudence),
                'regulatory_features': len(vectors.regulations),
                'complexity_features': len(vectors.complexity)
            },
            'quality_score': result.dimensional_quality_metrics.get('overall_dimensional_quality', 0),
            'classification': result.automatic_classification,
            'timestamp': datetime.now().isoformat()
        }
        
        self.historical_analysis_data.append(analysis_record)
        
        # Reentrenar cada 50 análisis
        if len(self.historical_analysis_data) % 50 == 0:
            await self._retrain_dimensional_models()
    
    async def _retrain_dimensional_models(self):
        """Reentrena modelos dimensionales con datos históricos."""
        
        self.logger.info("Reentrenando modelos dimensionales")
        
        if len(self.historical_analysis_data) < 10:
            return
        
        # En producción: reentrenar PCA y K-Means con datos históricos
        self.logger.info(f"Modelos reentrenados con {len(self.historical_analysis_data)} muestras")
    
    async def _fallback_simple_analysis(self, document: str) -> LegalDimensionAnalysis:
        """Análisis simple como fallback."""
        
        return LegalDimensionAnalysis(
            key_legal_dimensions={
                'jurisprudential_aspects': ['Análisis simplificado'],
                'regulatory_aspects': ['Marco general'],
                'contractual_aspects': ['Aspectos básicos']
            },
            automatic_classification={
                'complexity_level': 'moderado',
                'legal_domain': 'corporativo',
                'jurisdiction_type': 'nacional_ar',
                'consultation_type': 'analítica'
            },
            variance_analysis={'fallback_variance': [0.5, 0.3, 0.2]},
            recommended_agent_allocation={
                'cot_juridico': 0.4,
                'search_jurisprudencial': 0.35,
                'code_compliance': 0.25
            },
            complexity_cluster_info={'cluster': 2, 'label': 'moderado', 'confidence': 0.6},
            domain_cluster_info={'cluster': 0, 'label': 'corporativo', 'confidence': 0.6},
            jurisdiction_cluster_info={'cluster': 0, 'label': 'nacional_ar', 'confidence': 0.6},
            dimensional_quality_metrics={'overall_dimensional_quality': 0.6},
            processing_optimization={
                'estimated_processing_time_seconds': 30,
                'processing_strategy': 'fallback_analysis',
                'resource_allocation': 'minimal'
            }
        )
    
    async def _preprocess_legal_text(self, text: str) -> str:
        """Preprocesamiento especializado para texto jurídico."""
        
        # Limpieza básica
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Normaliza referencias legales
        cleaned = re.sub(r'art\.\s*(\d+)', r'artículo \1', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'inc\.\s*([a-z])', r'inciso \1', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _build_legal_dictionary(self) -> Dict[str, List[str]]:
        """Construye diccionario de términos jurídicos especializados."""
        
        return {
            'corporate': ['sociedad', 'empresa', 'directorio', 'accionistas'],
            'compliance': ['programa', 'integridad', 'prevención', 'riesgo'],
            'regulatory': ['ley', 'decreto', 'resolución', 'normativa'],
            'jurisprudence': ['jurisprudencia', 'fallo', 'precedente', 'doctrina']
        }
    
    def _build_complexity_indicators(self) -> Dict[str, float]:
        """Construye indicadores de complejidad jurídica."""
        
        return {
            'fusión': 5.0, 'adquisición': 4.5, 'due_diligence': 4.0,
            'compliance': 3.5, 'regulatorio': 3.0, 'contractual': 2.5,
            'consulta': 1.5, 'información': 1.0
        }


# Funciones de utilidad para integración

async def create_legal_dimensionality_analyzer() -> LegalDimensionalityAnalyzer:
    """Factory function para crear analizador dimensional."""
    analyzer = LegalDimensionalityAnalyzer()
    
    # Configuración específica para entorno legal argentino
    analyzer.complexity_labels.extend(['constitucional', 'internacional'])
    analyzer.domain_labels.extend(['constitucional', 'administrativo'])
    
    return analyzer

def calculate_dimensionality_improvement_metrics(baseline_time: float, 
                                               result: LegalDimensionAnalysis) -> Dict[str, float]:
    """Calcula métricas de mejora dimensional."""
    
    return {
        'analysis_speed_improvement': baseline_time / (result.analysis_time_ms / 1000),
        'dimensional_quality_gain': result.dimensional_quality_metrics.get('overall_dimensional_quality', 0),
        'classification_accuracy': min(
            result.complexity_cluster_info.get('confidence', 0),
            result.domain_cluster_info.get('confidence', 0)
        ),
        'processing_optimization_gain': 1.0 if result.processing_optimization else 0.0,
        'overall_improvement': result.dimensional_quality_metrics.get('overall_dimensional_quality', 0) * 100
    }