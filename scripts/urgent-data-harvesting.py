#!/usr/bin/env python3
"""
SCM Legal - Urgent Academic Data Harvesting
Crisis Response: Extract academic data before OpenAlex/Semantic Scholar restrictions tighten
"""

import asyncio
import aiohttp
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import sqlite3
import gzip
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HarvestingConfig:
    """Configuration for urgent data harvesting"""
    # OpenAlex API (still has abstracts for some content)
    openalex_base_url: str = "https://api.openalex.org"
    openalex_email: str = "research@scm-legal.com"  # Polite API usage
    
    # Semantic Scholar API
    semantic_scholar_base_url: str = "https://api.semanticscholar.org/graph/v1"
    
    # Rate limiting (respect API limits)
    requests_per_second: int = 10
    batch_size: int = 200
    
    # Output paths
    output_dir: Path = Path("./data/harvested")
    database_path: Path = Path("./data/academic_corpus.db")
    
    # Time window for harvesting
    max_papers_per_source: int = 50000  # Reasonable limit for initial extraction
    
    def __post_init__(self):
        # Search parameters for legal domain
        self.legal_keywords: List[str] = [
            "derecho", "legal", "jurídico", "jurisprudencia", "normativa",
            "compliance", "regulación", "legislación", "contractual",
            "corporate governance", "gobierno corporativo", "due diligence",
            "riesgo legal", "legal risk", "civil law", "derecho civil"
        ]
        
        # Jurisdictions of interest
        self.countries: List[str] = ["Argentina", "España", "Chile", "Uruguay", "Spain"]

class UrgentDataHarvester:
    """Urgent harvesting of academic legal data before access restrictions"""
    
    def __init__(self, config: HarvestingConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.harvested_count = 0
        self.errors_count = 0
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for harvested data"""
        conn = sqlite3.connect(self.config.database_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT,
                authors TEXT,
                year INTEGER,
                venue TEXT,
                citations INTEGER,
                source TEXT,
                url TEXT,
                keywords TEXT,
                language TEXT,
                country TEXT,
                harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                has_abstract BOOLEAN,
                full_text_available BOOLEAN
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_abstract_available ON papers(has_abstract) 
            WHERE has_abstract = 1
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_country ON papers(country)
        """)
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.config.database_path}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'SCM-Legal Academic Harvester (research@scm-legal.com)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def harvest_openalex_legal(self) -> AsyncGenerator[Dict, None]:
        """
        Harvest legal papers from OpenAlex (URGENT - before abstract restrictions)
        """
        logger.info("🚨 URGENT: Starting OpenAlex harvesting before abstract lockdown")
        
        for keyword in self.config.legal_keywords:
            for country in self.config.countries:
                # Build search query
                search_params = {
                    'search': f'"{keyword}" "{country}"',
                    'filter': 'type:article,has_abstract:true,language:es|en',
                    'per_page': 200,
                    'mailto': self.config.openalex_email,
                    'sort': 'cited_by_count:desc'  # Prioritize high-impact papers
                }
                
                page = 1
                papers_found = 0
                
                while papers_found < self.config.max_papers_per_source and page < 250:  # OpenAlex limit
                    search_params['page'] = page
                    
                    try:
                        url = f"{self.config.openalex_base_url}/works"
                        async with self.session.get(url, params=search_params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                for work in data.get('results', []):
                                    if self._has_useful_abstract(work):
                                        processed_paper = self._process_openalex_work(work, keyword, country)
                                        if processed_paper:
                                            yield processed_paper
                                            papers_found += 1
                                
                                # Check if we have more pages
                                if len(data.get('results', [])) < 200:
                                    break
                                    
                            elif response.status == 429:
                                logger.warning("Rate limited by OpenAlex, waiting...")
                                await asyncio.sleep(2)
                                continue
                            else:
                                logger.error(f"OpenAlex error {response.status} for {keyword}/{country}")
                                break
                    
                    except Exception as e:
                        logger.error(f"Error harvesting OpenAlex {keyword}/{country}: {e}")
                        self.errors_count += 1
                        break
                    
                    page += 1
                    await asyncio.sleep(1 / self.config.requests_per_second)  # Rate limiting
                
                logger.info(f"OpenAlex: {papers_found} papers for {keyword}/{country}")
    
    async def harvest_semantic_scholar_legal(self) -> AsyncGenerator[Dict, None]:
        """
        Harvest legal papers from Semantic Scholar (URGENT - while abstracts available)
        """
        logger.info("🚨 URGENT: Starting Semantic Scholar harvesting")
        
        for keyword in self.config.legal_keywords:
            search_params = {
                'query': f'{keyword} legal',
                'limit': 100,
                'fields': 'paperId,title,abstract,authors,year,venue,citationCount,url,fieldsOfStudy'
            }
            
            try:
                url = f"{self.config.semantic_scholar_base_url}/paper/search"
                async with self.session.get(url, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for paper in data.get('data', []):
                            if self._has_useful_abstract_s2(paper):
                                processed_paper = self._process_semantic_scholar_paper(paper, keyword)
                                if processed_paper:
                                    yield processed_paper
                                    
                    elif response.status == 429:
                        logger.warning("Rate limited by Semantic Scholar")
                        await asyncio.sleep(5)
                    else:
                        logger.error(f"Semantic Scholar error {response.status}")
            
            except Exception as e:
                logger.error(f"Error harvesting Semantic Scholar {keyword}: {e}")
                self.errors_count += 1
            
            await asyncio.sleep(1)  # Be respectful to S2 API
    
    def _has_useful_abstract(self, work: Dict) -> bool:
        """Check if OpenAlex work has a useful abstract"""
        abstract = work.get('abstract')
        if not abstract or len(abstract.strip()) < 100:
            return False
        
        # Check if it's legal domain relevant
        abstract_lower = abstract.lower()
        legal_terms = ['legal', 'law', 'derecho', 'jurídico', 'regulatory', 'compliance']
        return any(term in abstract_lower for term in legal_terms)
    
    def _has_useful_abstract_s2(self, paper: Dict) -> bool:
        """Check if Semantic Scholar paper has useful abstract"""
        abstract = paper.get('abstract')
        if not abstract or len(abstract.strip()) < 100:
            return False
        return True
    
    def _process_openalex_work(self, work: Dict, keyword: str, country: str) -> Optional[Dict]:
        """Process OpenAlex work into standardized format"""
        try:
            return {
                'id': work.get('id', '').split('/')[-1],
                'title': work.get('display_name', ''),
                'abstract': work.get('abstract', ''),
                'authors': json.dumps([author.get('author', {}).get('display_name', '') 
                                     for author in work.get('authorships', [])]),
                'year': work.get('publication_year', 0),
                'venue': work.get('primary_location', {}).get('source', {}).get('display_name', ''),
                'citations': work.get('cited_by_count', 0),
                'source': 'OpenAlex',
                'url': work.get('id', ''),
                'keywords': keyword,
                'language': 'es' if country in ['Argentina', 'España', 'Chile', 'Uruguay'] else 'en',
                'country': country,
                'has_abstract': bool(work.get('abstract')),
                'full_text_available': bool(work.get('open_access', {}).get('is_oa', False))
            }
        except Exception as e:
            logger.error(f"Error processing OpenAlex work: {e}")
            return None
    
    def _process_semantic_scholar_paper(self, paper: Dict, keyword: str) -> Optional[Dict]:
        """Process Semantic Scholar paper into standardized format"""
        try:
            return {
                'id': f"s2_{paper.get('paperId', '')}",
                'title': paper.get('title', ''),
                'abstract': paper.get('abstract', ''),
                'authors': json.dumps([author.get('name', '') for author in paper.get('authors', [])]),
                'year': paper.get('year', 0),
                'venue': paper.get('venue', ''),
                'citations': paper.get('citationCount', 0),
                'source': 'Semantic Scholar',
                'url': paper.get('url', ''),
                'keywords': keyword,
                'language': 'en',  # Most S2 content is English
                'country': 'International',
                'has_abstract': bool(paper.get('abstract')),
                'full_text_available': False  # Unknown from API
            }
        except Exception as e:
            logger.error(f"Error processing Semantic Scholar paper: {e}")
            return None
    
    async def save_papers_batch(self, papers: List[Dict]):
        """Save batch of papers to database"""
        if not papers:
            return
        
        conn = sqlite3.connect(self.config.database_path)
        try:
            conn.executemany("""
                INSERT OR REPLACE INTO papers (
                    id, title, abstract, authors, year, venue, citations, 
                    source, url, keywords, language, country, has_abstract, full_text_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [(
                paper['id'], paper['title'], paper['abstract'], paper['authors'],
                paper['year'], paper['venue'], paper['citations'], paper['source'],
                paper['url'], paper['keywords'], paper['language'], paper['country'],
                paper['has_abstract'], paper['full_text_available']
            ) for paper in papers])
            
            conn.commit()
            self.harvested_count += len(papers)
            logger.info(f"Saved batch of {len(papers)} papers. Total: {self.harvested_count}")
            
        except Exception as e:
            logger.error(f"Error saving papers batch: {e}")
            self.errors_count += len(papers)
        finally:
            conn.close()
    
    async def export_corpus_for_training(self):
        """Export harvested corpus in format suitable for LoRA training"""
        logger.info("📤 Exporting corpus for SCM training...")
        
        conn = sqlite3.connect(self.config.database_path)
        
        # Export papers with abstracts
        cursor = conn.execute("""
            SELECT id, title, abstract, keywords, country, year, citations
            FROM papers 
            WHERE has_abstract = 1 AND length(abstract) > 100
            ORDER BY citations DESC, year DESC
        """)
        
        training_data = []
        for row in cursor.fetchall():
            training_data.append({
                'id': row[0],
                'title': row[1],
                'abstract': row[2],
                'keywords': row[3],
                'country': row[4],
                'year': row[5],
                'citations': row[6],
                'text': f"Title: {row[1]}\n\nAbstract: {row[2]}\n\nKeywords: {row[3]}"
            })
        
        # Export to compressed JSON
        output_file = self.config.output_dir / f"legal_corpus_{datetime.now().strftime('%Y%m%d_%H%M')}.json.gz"
        with gzip.open(output_file, 'wt', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Exported {len(training_data)} papers with abstracts to {output_file}")
        
        # Generate stats
        stats = {
            'total_papers': len(training_data),
            'papers_with_abstracts': len(training_data),
            'avg_abstract_length': sum(len(p['abstract']) for p in training_data) / len(training_data),
            'by_country': {},
            'by_year': {},
            'top_cited': sorted(training_data, key=lambda x: x['citations'], reverse=True)[:10]
        }
        
        for paper in training_data:
            country = paper['country']
            year = paper['year']
            
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
            stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
        
        stats_file = self.config.output_dir / f"corpus_stats_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        conn.close()
        return output_file, stats_file

async def main():
    """Main urgent harvesting execution"""
    logger.info("🚨 STARTING URGENT ACADEMIC DATA HARVESTING")
    logger.info("⏰ Crisis Response: OpenAlex/Semantic Scholar abstract restrictions")
    
    config = HarvestingConfig()
    
    async with UrgentDataHarvester(config) as harvester:
        papers_batch = []
        
        # Harvest from both sources concurrently
        async for paper in harvester.harvest_openalex_legal():
            papers_batch.append(paper)
            
            if len(papers_batch) >= config.batch_size:
                await harvester.save_papers_batch(papers_batch)
                papers_batch = []
        
        async for paper in harvester.harvest_semantic_scholar_legal():
            papers_batch.append(paper)
            
            if len(papers_batch) >= config.batch_size:
                await harvester.save_papers_batch(papers_batch)
                papers_batch = []
        
        # Save remaining papers
        if papers_batch:
            await harvester.save_papers_batch(papers_batch)
        
        # Export for training
        corpus_file, stats_file = await harvester.export_corpus_for_training()
        
        logger.info("🎯 URGENT HARVESTING COMPLETED")
        logger.info(f"✅ Papers harvested: {harvester.harvested_count}")
        logger.info(f"❌ Errors: {harvester.errors_count}")
        logger.info(f"📁 Corpus: {corpus_file}")
        logger.info(f"📊 Stats: {stats_file}")

if __name__ == "__main__":
    asyncio.run(main())