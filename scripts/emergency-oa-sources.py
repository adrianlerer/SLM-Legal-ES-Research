#!/usr/bin/env python3
"""
SCM Legal - Emergency Open Access Sources Harvesting
Focus on Hispanic-American OA repositories that remain fully accessible
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import gzip
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmergencyOAConfig:
    """Configuration for emergency OA harvesting"""
    
    # SciELO - Full text + abstracts available
    scielo_api_base: str = "https://api.scielo.org"
    
    # LA Referencia - Regional repository network
    la_referencia_oai: str = "https://www.lareferencia.info/vufind/OAI/Server"
    
    # DOAJ - Directory of Open Access Journals
    doaj_api: str = "https://doaj.org/api/search/articles"
    
    # arXiv for legal/policy papers
    arxiv_api: str = "http://export.arxiv.org/api/query"
    
    # SSRN - Social Science Research Network (some OA content)
    ssrn_search_base: str = "https://www.ssrn.com"
    
    # Local configuration
    output_dir: Path = Path("./data/emergency_oa")
    database_path: Path = Path("./data/emergency_oa_corpus.db")
    
    def __post_init__(self):
        self.scielo_countries: List[str] = ["ar", "cl", "uy", "es"]  # Argentina, Chile, Uruguay, España
        
        # Legal domain keywords in Spanish
        self.legal_keywords_es: List[str] = [
            "derecho constitucional", "derecho administrativo", "derecho civil",
            "derecho comercial", "derecho laboral", "derecho tributario",
            "gobierno corporativo", "compliance", "due diligence",
            "responsabilidad civil", "contratos", "sociedades comerciales",
            "mercado de capitales", "regulación financiera", "BCRA", "CNV",
            "código civil", "ley de sociedades", "normativa"
        ]
        
        # English keywords for international sources
        self.legal_keywords_en: List[str] = [
            "corporate governance", "legal compliance", "contract law",
            "corporate law", "financial regulation", "securities law",
            "due diligence", "legal risk management", "regulatory compliance"
        ]

class EmergencyOAHarvester:
    """Emergency harvester for Open Access legal content"""
    
    def __init__(self, config: EmergencyOAConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.harvested_count = 0
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize emergency OA database"""
        conn = sqlite3.connect(self.config.database_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oa_papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT,
                full_text TEXT,
                authors TEXT,
                year INTEGER,
                journal TEXT,
                doi TEXT,
                url TEXT,
                pdf_url TEXT,
                source_repo TEXT,
                country TEXT,
                language TEXT,
                keywords TEXT,
                legal_domain TEXT,
                relevance_score REAL,
                harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                full_text_available BOOLEAN DEFAULT 0,
                quality_score REAL DEFAULT 0.0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relevance ON oa_papers(relevance_score DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_full_text ON oa_papers(full_text_available)")
        conn.commit()
        conn.close()
        logger.info("Emergency OA database initialized")
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=50, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=45)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'SCM-Legal Emergency OA Harvester (academic research)'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def harvest_scielo_legal(self) -> AsyncGenerator[Dict, None]:
        """
        Harvest legal papers from SciELO (fully open, abstracts + full text)
        Priority: Argentina, Chile, Uruguay, España
        """
        logger.info("🇦🇷🇨🇱🇺🇾🇪🇸 PRIORITY: Harvesting SciELO legal content")
        
        for country in self.config.scielo_countries:
            for keyword in self.config.legal_keywords_es:
                try:
                    # SciELO search API
                    search_params = {
                        'q': keyword,
                        'wt': 'json',
                        'start': 0,
                        'rows': 100,
                        'fq': f'in:{country}' if country != 'es' else 'in:scl'
                    }
                    
                    url = f"{self.config.scielo_api_base}/search"
                    async with self.session.get(url, params=search_params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for doc in data.get('response', {}).get('docs', []):
                                if self._is_legal_relevant(doc.get('ti_es', []) + doc.get('ti_en', [])):
                                    paper = await self._process_scielo_document(doc, keyword, country)
                                    if paper:
                                        yield paper
                        
                        elif response.status == 429:
                            await asyncio.sleep(2)
                            continue
                            
                except Exception as e:
                    logger.error(f"SciELO error {country}/{keyword}: {e}")
                
                await asyncio.sleep(0.5)  # Respectful rate limiting
    
    async def harvest_la_referencia_legal(self) -> AsyncGenerator[Dict, None]:
        """
        Harvest legal content from LA Referencia network
        Network of Latin American institutional repositories
        """
        logger.info("🌎 Harvesting LA Referencia institutional repositories")
        
        for keyword in self.config.legal_keywords_es[:5]:  # Limit for speed
            try:
                # OAI-PMH harvesting
                oai_params = {
                    'verb': 'ListRecords',
                    'metadataPrefix': 'oai_dc',
                    'set': 'openaire_cris_publications',
                    'from': '2020-01-01',  # Recent papers only
                }
                
                async with self.session.get(self.config.la_referencia_oai, params=oai_params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        
                        # Parse OAI-PMH XML
                        root = ET.fromstring(xml_content)
                        
                        for record in root.findall('.//{http://www.openarchives.org/OAI/2.0/}record'):
                            try:
                                paper = self._process_oai_record(record, keyword)
                                if paper and self._is_legal_relevant([paper.get('title', '')]):
                                    yield paper
                            except Exception as e:
                                logger.debug(f"Error processing OAI record: {e}")
                                continue
            
            except Exception as e:
                logger.error(f"LA Referencia error {keyword}: {e}")
            
            await asyncio.sleep(1)
    
    async def harvest_doaj_legal(self) -> AsyncGenerator[Dict, None]:
        """
        Harvest legal articles from DOAJ (Directory of Open Access Journals)
        """
        logger.info("📚 Harvesting DOAJ legal journals")
        
        for keyword in self.config.legal_keywords_en[:10]:  # English keywords for DOAJ
            try:
                search_params = {
                    'q': keyword,
                    'pageSize': 50,
                    'page': 1
                }
                
                async with self.session.get(self.config.doaj_api, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for article in data.get('results', []):
                            paper = self._process_doaj_article(article, keyword)
                            if paper:
                                yield paper
            
            except Exception as e:
                logger.error(f"DOAJ error {keyword}: {e}")
            
            await asyncio.sleep(0.8)
    
    async def harvest_arxiv_legal_policy(self) -> AsyncGenerator[Dict, None]:
        """
        Harvest legal/policy papers from arXiv
        Categories: econ.GN (General Economics), cs.CY (Computers and Society)
        """
        logger.info("📄 Harvesting arXiv legal/policy papers")
        
        categories = ['cat:econ.GN', 'cat:cs.CY', 'cat:q-fin.GN']
        
        for keyword in self.config.legal_keywords_en[:8]:
            for category in categories:
                try:
                    query = f'({category}) AND (ti:{keyword} OR abs:{keyword})'
                    params = {
                        'search_query': query,
                        'start': 0,
                        'max_results': 50,
                        'sortBy': 'submittedDate',
                        'sortOrder': 'descending'
                    }
                    
                    async with self.session.get(self.config.arxiv_api, params=params) as response:
                        if response.status == 200:
                            xml_content = await response.text()
                            root = ET.fromstring(xml_content)
                            
                            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                                paper = self._process_arxiv_entry(entry, keyword)
                                if paper:
                                    yield paper
                
                except Exception as e:
                    logger.error(f"arXiv error {keyword}/{category}: {e}")
                
                await asyncio.sleep(1)  # arXiv rate limiting
    
    def _is_legal_relevant(self, titles: List[str]) -> bool:
        """Check if titles indicate legal relevance"""
        if not titles:
            return False
        
        text = ' '.join(titles).lower()
        legal_indicators = [
            'derecho', 'legal', 'law', 'jurídico', 'jurisprudence', 'normative',
            'contract', 'compliance', 'regulation', 'governance', 'tribunal',
            'court', 'judicial', 'legislation', 'statute', 'código'
        ]
        
        return any(indicator in text for indicator in legal_indicators)
    
    async def _process_scielo_document(self, doc: Dict, keyword: str, country: str) -> Optional[Dict]:
        """Process SciELO document into standard format"""
        try:
            # Get multilingual fields
            titles = doc.get('ti_es', []) + doc.get('ti_en', []) + doc.get('ti_pt', [])
            abstracts = doc.get('ab_es', []) + doc.get('ab_en', []) + doc.get('ab_pt', [])
            
            title = titles[0] if titles else 'Sin título'
            abstract = abstracts[0] if abstracts else ''
            
            # Calculate relevance score
            relevance_score = self._calculate_legal_relevance(title, abstract, keyword)
            
            return {
                'id': f"scielo_{country}_{doc.get('id', '')}",
                'title': title,
                'abstract': abstract,
                'authors': ', '.join(doc.get('au', [])),
                'year': int(doc.get('da', ['0'])[0][:4]) if doc.get('da') else 0,
                'journal': doc.get('ta', [''])[0],
                'doi': doc.get('doi', ''),
                'url': doc.get('url', ''),
                'pdf_url': doc.get('pdf_url', ''),
                'source_repo': f'SciELO-{country.upper()}',
                'country': self._country_code_to_name(country),
                'language': 'es',
                'keywords': keyword,
                'legal_domain': self._classify_legal_domain(title, abstract),
                'relevance_score': relevance_score,
                'full_text_available': True,  # SciELO provides full text
                'quality_score': self._calculate_quality_score(doc)
            }
        
        except Exception as e:
            logger.debug(f"Error processing SciELO doc: {e}")
            return None
    
    def _process_oai_record(self, record, keyword: str) -> Optional[Dict]:
        """Process OAI-PMH record from LA Referencia"""
        try:
            header = record.find('.//{http://www.openarchives.org/OAI/2.0/}header')
            metadata = record.find('.//{http://www.openarchives.org/OAI/2.0/}metadata')
            
            if header is None or metadata is None:
                return None
            
            # Extract Dublin Core metadata
            dc = metadata.find('.//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc')
            if dc is None:
                return None
            
            title_elem = dc.find('.//{http://purl.org/dc/elements/1.1/}title')
            description_elem = dc.find('.//{http://purl.org/dc/elements/1.1/}description')
            creator_elem = dc.find('.//{http://purl.org/dc/elements/1.1/}creator')
            date_elem = dc.find('.//{http://purl.org/dc/elements/1.1/}date')
            identifier_elem = dc.find('.//{http://purl.org/dc/elements/1.1/}identifier')
            
            title = title_elem.text if title_elem is not None else 'Sin título'
            abstract = description_elem.text if description_elem is not None else ''
            
            return {
                'id': f"lareferencia_{hash(title) % 1000000}",
                'title': title,
                'abstract': abstract,
                'authors': creator_elem.text if creator_elem is not None else '',
                'year': int(date_elem.text[:4]) if date_elem is not None and date_elem.text else 0,
                'url': identifier_elem.text if identifier_elem is not None else '',
                'source_repo': 'LA Referencia',
                'country': 'Latin America',
                'language': 'es',
                'keywords': keyword,
                'legal_domain': self._classify_legal_domain(title, abstract),
                'relevance_score': self._calculate_legal_relevance(title, abstract, keyword),
                'full_text_available': True
            }
        
        except Exception as e:
            logger.debug(f"Error processing OAI record: {e}")
            return None
    
    def _process_doaj_article(self, article: Dict, keyword: str) -> Optional[Dict]:
        """Process DOAJ article"""
        try:
            bibjson = article.get('bibjson', {})
            
            title = bibjson.get('title', 'Sin título')
            abstract = bibjson.get('abstract', '')
            
            return {
                'id': f"doaj_{article.get('id', '')}",
                'title': title,
                'abstract': abstract,
                'authors': ', '.join([a.get('name', '') for a in bibjson.get('author', [])]),
                'year': int(bibjson.get('year', 0)) if bibjson.get('year') else 0,
                'journal': bibjson.get('journal', {}).get('title', ''),
                'doi': next((id['id'] for id in bibjson.get('identifier', []) if id.get('type') == 'doi'), ''),
                'url': next((link.get('url') for link in bibjson.get('link', []) if link.get('type') == 'fulltext'), ''),
                'source_repo': 'DOAJ',
                'country': 'International',
                'language': 'en',
                'keywords': keyword,
                'legal_domain': self._classify_legal_domain(title, abstract),
                'relevance_score': self._calculate_legal_relevance(title, abstract, keyword),
                'full_text_available': True
            }
        
        except Exception as e:
            logger.debug(f"Error processing DOAJ article: {e}")
            return None
    
    def _process_arxiv_entry(self, entry, keyword: str) -> Optional[Dict]:
        """Process arXiv entry"""
        try:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            published = entry.find('atom:published', ns).text
            year = int(published[:4]) if published else 0
            
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
            pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            return {
                'id': f"arxiv_{arxiv_id}",
                'title': title,
                'abstract': summary,
                'authors': ', '.join(authors),
                'year': year,
                'journal': 'arXiv preprint',
                'url': entry.find('atom:id', ns).text,
                'pdf_url': pdf_link,
                'source_repo': 'arXiv',
                'country': 'International',
                'language': 'en',
                'keywords': keyword,
                'legal_domain': self._classify_legal_domain(title, summary),
                'relevance_score': self._calculate_legal_relevance(title, summary, keyword),
                'full_text_available': True
            }
        
        except Exception as e:
            logger.debug(f"Error processing arXiv entry: {e}")
            return None
    
    def _calculate_legal_relevance(self, title: str, abstract: str, keyword: str) -> float:
        """Calculate legal relevance score (0-1)"""
        text = f"{title} {abstract}".lower()
        
        # Base score for keyword presence
        score = 0.0
        if keyword.lower() in text:
            score += 0.4
        
        # Legal domain indicators
        legal_terms = {
            'derecho': 0.3, 'legal': 0.3, 'jurídico': 0.3, 'law': 0.3,
            'compliance': 0.2, 'governance': 0.2, 'regulation': 0.2,
            'contract': 0.15, 'tribunal': 0.15, 'judicial': 0.15,
            'normative': 0.1, 'statute': 0.1, 'código': 0.1
        }
        
        for term, weight in legal_terms.items():
            if term in text:
                score += weight
        
        return min(score, 1.0)
    
    def _classify_legal_domain(self, title: str, abstract: str) -> str:
        """Classify legal domain based on content"""
        text = f"{title} {abstract}".lower()
        
        domains = {
            'corporate_governance': ['governance', 'gobierno corporativo', 'directorio', 'board'],
            'contract_law': ['contract', 'contrato', 'agreement', 'acuerdo'],
            'financial_regulation': ['financial', 'financier', 'securities', 'mercado de capitales'],
            'civil_law': ['civil', 'responsabilidad civil', 'damages', 'daños'],
            'administrative_law': ['administrative', 'administrativo', 'regulatory', 'regulación'],
            'constitutional_law': ['constitutional', 'constitucional', 'fundamental rights'],
            'commercial_law': ['commercial', 'comercial', 'business', 'empresa'],
        }
        
        for domain, terms in domains.items():
            if any(term in text for term in terms):
                return domain
        
        return 'general_legal'
    
    def _calculate_quality_score(self, doc: Dict) -> float:
        """Calculate quality score based on metadata completeness"""
        score = 0.0
        
        # Check for complete metadata
        if doc.get('ti_es') or doc.get('ti_en'):
            score += 0.2
        if doc.get('ab_es') or doc.get('ab_en'):
            score += 0.3
        if doc.get('au'):
            score += 0.1
        if doc.get('da'):
            score += 0.1
        if doc.get('doi'):
            score += 0.2
        if doc.get('url'):
            score += 0.1
        
        return score
    
    def _country_code_to_name(self, code: str) -> str:
        """Convert country code to name"""
        mapping = {
            'ar': 'Argentina',
            'cl': 'Chile', 
            'uy': 'Uruguay',
            'es': 'España'
        }
        return mapping.get(code, code.upper())
    
    async def save_papers_batch(self, papers: List[Dict]):
        """Save batch of OA papers to database"""
        if not papers:
            return
        
        conn = sqlite3.connect(self.config.database_path)
        try:
            conn.executemany("""
                INSERT OR REPLACE INTO oa_papers (
                    id, title, abstract, authors, year, journal, doi, url, pdf_url,
                    source_repo, country, language, keywords, legal_domain, 
                    relevance_score, full_text_available, quality_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [(
                p['id'], p['title'], p['abstract'], p['authors'], p['year'], 
                p.get('journal', ''), p.get('doi', ''), p['url'], p.get('pdf_url', ''),
                p['source_repo'], p['country'], p['language'], p['keywords'],
                p['legal_domain'], p['relevance_score'], p.get('full_text_available', True),
                p.get('quality_score', 0.0)
            ) for p in papers])
            
            conn.commit()
            self.harvested_count += len(papers)
            logger.info(f"💾 Saved {len(papers)} OA papers. Total: {self.harvested_count}")
            
        except Exception as e:
            logger.error(f"Error saving OA papers: {e}")
        finally:
            conn.close()
    
    async def export_high_quality_corpus(self):
        """Export high-quality OA corpus for training"""
        logger.info("📤 Exporting high-quality OA corpus...")
        
        conn = sqlite3.connect(self.config.database_path)
        
        # Select high-quality papers with abstracts
        cursor = conn.execute("""
            SELECT id, title, abstract, legal_domain, country, year, relevance_score, quality_score,
                   authors, journal, source_repo, url
            FROM oa_papers 
            WHERE relevance_score >= 0.5 
            AND length(abstract) > 150
            AND quality_score >= 0.3
            ORDER BY relevance_score DESC, quality_score DESC
        """)
        
        training_corpus = []
        for row in cursor.fetchall():
            training_corpus.append({
                'id': row[0],
                'title': row[1],
                'abstract': row[2],
                'legal_domain': row[3],
                'country': row[4],
                'year': row[5],
                'relevance_score': row[6],
                'quality_score': row[7],
                'authors': row[8],
                'journal': row[9],
                'source_repo': row[10],
                'url': row[11],
                'training_text': f"Domain: {row[3]}\nTitle: {row[1]}\nAbstract: {row[2]}\nCountry: {row[4]}"
            })
        
        # Export compressed corpus
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        corpus_file = self.config.output_dir / f"emergency_oa_corpus_{timestamp}.json.gz"
        
        with gzip.open(corpus_file, 'wt', encoding='utf-8') as f:
            json.dump(training_corpus, f, ensure_ascii=False, indent=2)
        
        # Generate corpus statistics
        stats = {
            'total_papers': len(training_corpus),
            'avg_relevance': sum(p['relevance_score'] for p in training_corpus) / len(training_corpus),
            'avg_quality': sum(p['quality_score'] for p in training_corpus) / len(training_corpus),
            'by_source': {},
            'by_domain': {},
            'by_country': {},
            'by_year': {}
        }
        
        for paper in training_corpus:
            source = paper['source_repo']
            domain = paper['legal_domain']
            country = paper['country']
            year = paper['year']
            
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
            stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
        
        stats_file = self.config.output_dir / f"emergency_oa_stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        conn.close()
        
        logger.info(f"✅ Emergency OA corpus exported: {len(training_corpus)} papers")
        logger.info(f"📁 Corpus file: {corpus_file}")
        logger.info(f"📊 Stats file: {stats_file}")
        
        return corpus_file, stats_file

async def main():
    """Execute emergency OA harvesting"""
    logger.info("🚨 EMERGENCY OPEN ACCESS HARVESTING INITIATED")
    logger.info("🎯 Strategy: Harvest fully accessible OA sources while they remain open")
    
    config = EmergencyOAConfig()
    
    async with EmergencyOAHarvester(config) as harvester:
        papers_batch = []
        batch_size = 50
        
        # Harvest from all OA sources
        sources = [
            harvester.harvest_scielo_legal(),
            harvester.harvest_la_referencia_legal(),
            harvester.harvest_doaj_legal(),
            harvester.harvest_arxiv_legal_policy()
        ]
        
        for source in sources:
            async for paper in source:
                papers_batch.append(paper)
                
                if len(papers_batch) >= batch_size:
                    await harvester.save_papers_batch(papers_batch)
                    papers_batch = []
        
        # Save remaining papers
        if papers_batch:
            await harvester.save_papers_batch(papers_batch)
        
        # Export corpus for training
        corpus_file, stats_file = await harvester.export_high_quality_corpus()
        
        logger.info("🎊 EMERGENCY OA HARVESTING COMPLETED")
        logger.info(f"✅ Total papers: {harvester.harvested_count}")
        logger.info(f"🔥 Ready for SCM training: {corpus_file}")

if __name__ == "__main__":
    asyncio.run(main())