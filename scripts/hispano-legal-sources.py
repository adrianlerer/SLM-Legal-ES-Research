#!/usr/bin/env python3
"""
SCM Legal - Hispano-American Legal Sources Harvester
Focus on Open Access sources in Spanish-speaking jurisdictions
Strategy: OA-first to avoid abstract restrictions
"""

import asyncio
import aiohttp
import json
import time
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import gzip
import hashlib
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HispanoLegalConfig:
    """Configuration for Hispano-American legal sources"""
    
    # SciELO (Open Access - High Priority)
    scielo_api_base: str = "https://search.scielo.org/api"
    scielo_countries: List[str] = ["ar", "cl", "es", "uy"]
    
    # LA Referencia (Latin America Open Access)
    lareferencia_api: str = "http://www.lareferencia.info/vufind/api/v1/search"
    
    # Institutional Repositories (Argentine focus)
    repositories: Dict[str, str] = {
        "SEDICI_UNLP": "http://sedici.unlp.edu.ar/oai",
        "UBA_Digital": "http://repositoriouba.sisbi.uba.ar/oai/request",
        "CONICET": "https://ri.conicet.gov.ar/oai",
        "UCA_Repositorio": "https://repositorio.uca.edu.ar/oai",
        "DIALNET": "https://dialnet.unirioja.es/servlet/oai"  # Spain
    }
    
    # Government Legal Sources (Public Domain)
    official_sources: Dict[str, str] = {
        "InfoLEG_AR": "http://servicios.infoleg.gob.ar",
        "BOE_ES": "https://www.boe.es/datosabiertos",
        "LeyChile": "https://www.leychile.cl/Consulta/api",
        "IMPO_UY": "https://www.impo.com.uy/api"
    }
    
    # Legal keywords with jurisdiction specifics
    legal_terms: Dict[str, List[str]] = {
        "corporate": ["gobierno corporativo", "corporate governance", "compliance", 
                     "due diligence", "directorio", "consejo administración"],
        "contracts": ["derecho contractual", "obligaciones", "contratos", 
                     "cláusulas", "rescisión", "incumplimiento"],
        "regulatory": ["derecho regulatorio", "normativa", "reglamentación",
                      "autoridad regulatoria", "compliance regulatorio"],
        "civil": ["derecho civil", "código civil", "responsabilidad civil",
                 "daños", "obligaciones civiles"],
        "commercial": ["derecho comercial", "sociedades", "ley sociedades",
                      "mercantil", "empresa", "negocio jurídico"]
    }
    
    output_dir: Path = Path("./data/hispano_legal")
    database_path: Path = Path("./data/hispano_legal.db")
    
    # Rate limiting for respectful harvesting
    requests_per_second: int = 5
    batch_size: int = 100
    max_records_per_source: int = 10000

class HispanoLegalHarvester:
    """Harvester for Hispanic legal sources (OA focus)"""
    
    def __init__(self, config: HispanoLegalConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.harvested_count = 0
        self.sources_stats = {}
        
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database for legal sources"""
        conn = sqlite3.connect(self.config.database_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS legal_documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT,
                full_text TEXT,
                authors TEXT,
                institution TEXT,
                publication_date DATE,
                document_type TEXT,
                jurisdiction TEXT,
                legal_area TEXT,
                source TEXT NOT NULL,
                url TEXT,
                language TEXT,
                citations INTEGER DEFAULT 0,
                is_open_access BOOLEAN DEFAULT 1,
                confidence_score REAL DEFAULT 0.0,
                harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_jurisdiction ON legal_documents(jurisdiction)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_legal_area ON legal_documents(legal_area)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_open_access ON legal_documents(is_open_access)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.config.database_path}")
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=50, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'SCM-Legal Hispano Harvester (research@scm-legal.com)'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def harvest_scielo_legal(self) -> AsyncGenerator[Dict, None]:
        """Harvest legal documents from SciELO (High priority OA source)"""
        logger.info("🔍 Harvesting SciELO legal documents...")
        
        for country in self.config.scielo_countries:
            for legal_area, terms in self.config.legal_terms.items():
                for term in terms[:3]:  # Limit terms to avoid over-querying
                    
                    search_params = {
                        'q': term,
                        'lang': 'es',
                        'filter[db][]': country,
                        'filter[subject_area][]': 'Human Sciences',
                        'format': 'json',
                        'count': 200
                    }
                    
                    try:
                        url = f"{self.config.scielo_api_base}/search"
                        async with self.session.get(url, params=search_params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                for doc in data.get('docs', []):
                                    if self._is_legal_relevant(doc, term):
                                        processed_doc = self._process_scielo_document(
                                            doc, country, legal_area, term
                                        )
                                        if processed_doc:
                                            yield processed_doc
                            
                            elif response.status == 429:
                                logger.warning(f"Rate limited by SciELO {country}")
                                await asyncio.sleep(5)
                                continue
                    
                    except Exception as e:
                        logger.error(f"Error harvesting SciELO {country}/{term}: {e}")
                    
                    await asyncio.sleep(1 / self.config.requests_per_second)
        
        logger.info("✅ SciELO harvesting completed")
    
    async def harvest_institutional_repositories(self) -> AsyncGenerator[Dict, None]:
        """Harvest from institutional repositories (OAI-PMH)"""
        logger.info("🏛️ Harvesting institutional repositories...")
        
        for repo_name, oai_url in self.config.repositories.items():
            jurisdiction = self._get_jurisdiction_from_repo(repo_name)
            
            for legal_area, terms in self.config.legal_terms.items():
                # Use Dublin Core metadata format for broader compatibility
                oai_params = {
                    'verb': 'ListRecords',
                    'metadataPrefix': 'oai_dc',
                    'set': 'hdl_123456789_1',  # Adjust per repository structure
                }
                
                try:
                    async with self.session.get(oai_url, params=oai_params) as response:
                        if response.status == 200:
                            xml_content = await response.text()
                            
                            # Parse OAI-PMH XML response
                            async for doc in self._parse_oai_response(
                                xml_content, repo_name, jurisdiction, legal_area
                            ):
                                if doc:
                                    yield doc
                        
                        elif response.status == 503:  # Service temporarily unavailable
                            logger.warning(f"Repository {repo_name} temporarily unavailable")
                            continue
                
                except Exception as e:
                    logger.error(f"Error harvesting repository {repo_name}: {e}")
                
                await asyncio.sleep(2)  # Be respectful to institutional repositories
        
        logger.info("✅ Institutional repositories harvesting completed")
    
    async def harvest_government_sources(self) -> AsyncGenerator[Dict, None]:
        """Harvest from government legal databases (public domain)"""
        logger.info("🏛️ Harvesting government legal sources...")
        
        # InfoLEG Argentina
        await self._harvest_infoleg()
        
        # BOE España  
        await self._harvest_boe()
        
        # Additional government sources can be added here
        logger.info("✅ Government sources harvesting completed")
    
    async def _harvest_infoleg(self) -> AsyncGenerator[Dict, None]:
        """Harvest from InfoLEG Argentina"""
        logger.info("📜 Harvesting InfoLEG (Argentina)...")
        
        # InfoLEG search endpoints (simplified approach)
        search_terms = ["sociedades", "contratos", "obligaciones", "compliance", "directorio"]
        
        for term in search_terms:
            try:
                # Note: This is a simplified approach. Real InfoLEG API might differ
                search_url = f"http://servicios.infoleg.gob.ar/infolegInternet/anexos/normativas/search"
                params = {
                    'q': term,
                    'format': 'json',
                    'limit': 100
                }
                
                # This would need actual InfoLEG API implementation
                logger.info(f"InfoLEG search for: {term}")
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"InfoLEG harvesting error for {term}: {e}")
    
    async def _harvest_boe(self) -> AsyncGenerator[Dict, None]:
        """Harvest from BOE España"""
        logger.info("📰 Harvesting BOE (España)...")
        
        # BOE API implementation would go here
        # This is a placeholder for the actual implementation
        logger.info("BOE harvesting placeholder - implement actual API")
    
    def _is_legal_relevant(self, doc: Dict, search_term: str) -> bool:
        """Check if document is relevant to legal domain"""
        title = doc.get('title', '').lower()
        abstract = doc.get('abstract', '').lower()
        
        legal_indicators = [
            'derecho', 'legal', 'jurídico', 'ley', 'normativa', 'reglamento',
            'código', 'constitución', 'tribunal', 'corte', 'sentencia',
            'contract', 'compliance', 'governance', 'regulatory'
        ]
        
        text_to_check = f"{title} {abstract}"
        return any(indicator in text_to_check for indicator in legal_indicators)
    
    def _process_scielo_document(self, doc: Dict, country: str, legal_area: str, term: str) -> Optional[Dict]:
        """Process SciELO document into standardized format"""
        try:
            return {
                'id': hashlib.md5(f"scielo_{doc.get('id', '')}".encode()).hexdigest(),
                'title': doc.get('title', ''),
                'abstract': doc.get('abstract', ''),
                'full_text': '',  # Would need additional fetching
                'authors': json.dumps(doc.get('authors', [])),
                'institution': doc.get('affiliation', ''),
                'publication_date': doc.get('publication_date', ''),
                'document_type': 'article',
                'jurisdiction': self._map_country_to_jurisdiction(country),
                'legal_area': legal_area,
                'source': f'SciELO_{country.upper()}',
                'url': doc.get('url', ''),
                'language': 'es',
                'citations': doc.get('citation_count', 0),
                'is_open_access': True,
                'confidence_score': self._calculate_confidence_score(doc, term)
            }
        except Exception as e:
            logger.error(f"Error processing SciELO document: {e}")
            return None
    
    async def _parse_oai_response(self, xml_content: str, repo_name: str, 
                                jurisdiction: str, legal_area: str) -> AsyncGenerator[Dict, None]:
        """Parse OAI-PMH XML response"""
        try:
            root = ET.fromstring(xml_content)
            
            # Find all record elements
            records = root.findall('.//{http://www.openarchives.org/OAI/2.0/}record')
            
            for record in records:
                metadata = record.find('.//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc')
                if metadata is None:
                    continue
                
                # Extract Dublin Core elements
                title = self._get_dc_element(metadata, 'title')
                description = self._get_dc_element(metadata, 'description') 
                creator = self._get_dc_element(metadata, 'creator')
                date = self._get_dc_element(metadata, 'date')
                identifier = self._get_dc_element(metadata, 'identifier')
                
                if title and self._is_legal_relevant({'title': title, 'abstract': description}, ''):
                    yield {
                        'id': hashlib.md5(f"{repo_name}_{identifier}".encode()).hexdigest(),
                        'title': title,
                        'abstract': description or '',
                        'full_text': '',
                        'authors': creator or '',
                        'institution': repo_name,
                        'publication_date': date or '',
                        'document_type': 'repository',
                        'jurisdiction': jurisdiction,
                        'legal_area': legal_area,
                        'source': repo_name,
                        'url': identifier or '',
                        'language': 'es',
                        'citations': 0,
                        'is_open_access': True,
                        'confidence_score': 0.7  # Medium confidence for repository content
                    }
        
        except ET.ParseError as e:
            logger.error(f"XML parsing error for {repo_name}: {e}")
        except Exception as e:
            logger.error(f"Error parsing OAI response for {repo_name}: {e}")
    
    def _get_dc_element(self, metadata, element_name: str) -> Optional[str]:
        """Extract Dublin Core element from metadata"""
        element = metadata.find(f'.//{{{metadata.nsmap.get("dc", "http://purl.org/dc/elements/1.1/")}}}{element_name}')
        return element.text if element is not None else None
    
    def _map_country_to_jurisdiction(self, country_code: str) -> str:
        """Map country codes to jurisdiction names"""
        mapping = {
            'ar': 'Argentina',
            'cl': 'Chile', 
            'es': 'España',
            'uy': 'Uruguay'
        }
        return mapping.get(country_code, 'Unknown')
    
    def _get_jurisdiction_from_repo(self, repo_name: str) -> str:
        """Get jurisdiction from repository name"""
        if 'UBA' in repo_name or 'CONICET' in repo_name or 'UNLP' in repo_name or 'UCA' in repo_name:
            return 'Argentina'
        elif 'DIALNET' in repo_name:
            return 'España'
        else:
            return 'International'
    
    def _calculate_confidence_score(self, doc: Dict, search_term: str) -> float:
        """Calculate confidence score for legal relevance"""
        score = 0.5  # Base score
        
        title = doc.get('title', '').lower()
        abstract = doc.get('abstract', '').lower()
        
        # Boost for legal terms in title
        if any(term in title for term in ['derecho', 'legal', 'jurídico', 'ley']):
            score += 0.3
        
        # Boost for search term in abstract
        if search_term.lower() in abstract:
            score += 0.2
        
        # Boost for citation count
        citations = doc.get('citation_count', 0)
        if citations > 10:
            score += 0.1
        
        return min(score, 1.0)
    
    async def save_documents_batch(self, documents: List[Dict]):
        """Save batch of documents to database"""
        if not documents:
            return
        
        conn = sqlite3.connect(self.config.database_path)
        try:
            conn.executemany("""
                INSERT OR REPLACE INTO legal_documents (
                    id, title, abstract, full_text, authors, institution, 
                    publication_date, document_type, jurisdiction, legal_area,
                    source, url, language, citations, is_open_access, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [(
                doc['id'], doc['title'], doc['abstract'], doc['full_text'],
                doc['authors'], doc['institution'], doc['publication_date'],
                doc['document_type'], doc['jurisdiction'], doc['legal_area'],
                doc['source'], doc['url'], doc['language'], doc['citations'],
                doc['is_open_access'], doc['confidence_score']
            ) for doc in documents])
            
            conn.commit()
            self.harvested_count += len(documents)
            logger.info(f"💾 Saved {len(documents)} documents. Total: {self.harvested_count}")
            
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
        finally:
            conn.close()
    
    async def export_training_corpus(self):
        """Export corpus optimized for SCM legal training"""
        logger.info("📤 Exporting Hispanic legal corpus for training...")
        
        conn = sqlite3.connect(self.config.database_path)
        
        # Priority: high confidence, open access, with abstracts
        cursor = conn.execute("""
            SELECT id, title, abstract, full_text, jurisdiction, legal_area, 
                   confidence_score, source, publication_date
            FROM legal_documents 
            WHERE is_open_access = 1 AND confidence_score > 0.6
            AND (length(abstract) > 100 OR length(full_text) > 200)
            ORDER BY confidence_score DESC, publication_date DESC
        """)
        
        training_corpus = []
        jurisdiction_stats = {}
        
        for row in cursor.fetchall():
            doc_id, title, abstract, full_text, jurisdiction, legal_area, confidence, source, pub_date = row
            
            # Combine available text
            combined_text = f"Título: {title}\n\n"
            if abstract:
                combined_text += f"Resumen: {abstract}\n\n"
            if full_text:
                combined_text += f"Texto: {full_text[:2000]}..."  # Limit full text
            
            training_corpus.append({
                'id': doc_id,
                'text': combined_text,
                'jurisdiction': jurisdiction,
                'legal_area': legal_area,
                'confidence': confidence,
                'source': source,
                'metadata': {
                    'title': title,
                    'publication_date': pub_date,
                    'has_abstract': bool(abstract),
                    'has_full_text': bool(full_text)
                }
            })
            
            # Update stats
            jurisdiction_stats[jurisdiction] = jurisdiction_stats.get(jurisdiction, 0) + 1
        
        # Export corpus
        output_file = self.config.output_dir / f"hispano_legal_corpus_{datetime.now().strftime('%Y%m%d_%H%M')}.json.gz"
        with gzip.open(output_file, 'wt', encoding='utf-8') as f:
            json.dump(training_corpus, f, ensure_ascii=False, indent=2)
        
        # Export statistics
        stats = {
            'total_documents': len(training_corpus),
            'by_jurisdiction': jurisdiction_stats,
            'avg_confidence': sum(doc['confidence'] for doc in training_corpus) / len(training_corpus),
            'sources': list(set(doc['source'] for doc in training_corpus)),
            'legal_areas': list(set(doc['legal_area'] for doc in training_corpus))
        }
        
        stats_file = self.config.output_dir / f"hispano_stats_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        conn.close()
        
        logger.info(f"✅ Exported {len(training_corpus)} documents to {output_file}")
        logger.info(f"📊 Statistics: {stats_file}")
        
        return output_file, stats_file

async def main():
    """Execute Hispanic legal sources harvesting"""
    logger.info("🌎 STARTING HISPANIC LEGAL SOURCES HARVESTING")
    logger.info("🎯 Strategy: OA-first to avoid abstract restrictions")
    
    config = HispanoLegalConfig()
    
    async with HispanoLegalHarvester(config) as harvester:
        documents_batch = []
        
        # Harvest from all sources
        sources = [
            harvester.harvest_scielo_legal(),
            harvester.harvest_institutional_repositories(),
            harvester.harvest_government_sources()
        ]
        
        for source in sources:
            async for document in source:
                documents_batch.append(document)
                
                if len(documents_batch) >= config.batch_size:
                    await harvester.save_documents_batch(documents_batch)
                    documents_batch = []
        
        # Save remaining documents
        if documents_batch:
            await harvester.save_documents_batch(documents_batch)
        
        # Export training corpus
        corpus_file, stats_file = await harvester.export_training_corpus()
        
        logger.info("🎉 HISPANIC LEGAL HARVESTING COMPLETED")
        logger.info(f"📊 Total documents: {harvester.harvested_count}")
        logger.info(f"📁 Corpus: {corpus_file}")
        logger.info(f"📈 Statistics: {stats_file}")

if __name__ == "__main__":
    asyncio.run(main())