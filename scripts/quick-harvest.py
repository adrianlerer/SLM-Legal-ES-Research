#!/usr/bin/env python3
"""
SCM Legal - Quick Emergency Harvesting
Immediate execution version - no complex dependencies
"""

import json
import time
import sqlite3
import gzip
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.parse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Create database for harvested data"""
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect("data/quick_harvest.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            authors TEXT,
            year INTEGER,
            source TEXT,
            url TEXT,
            keywords TEXT,
            language TEXT,
            harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def harvest_openalex_sample():
    """Quick harvest from OpenAlex (simplified version)"""
    logger.info("🔥 Quick harvesting from OpenAlex...")
    
    papers = []
    legal_keywords = ["derecho", "legal", "jurídico", "compliance", "governance"]
    
    for keyword in legal_keywords[:3]:  # Limit for quick execution
        try:
            # Simple OpenAlex search
            query = urllib.parse.quote(f'"{keyword}"')
            url = f"https://api.openalex.org/works?search={query}&filter=type:article,has_abstract:true&per_page=50&mailto=research@scm-legal.com"
            
            logger.info(f"Searching for: {keyword}")
            
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    for work in data.get('results', []):
                        if work.get('abstract') and len(work.get('abstract', '')) > 100:
                            paper = {
                                'id': work.get('id', '').split('/')[-1] if work.get('id') else f"oa_{len(papers)}",
                                'title': work.get('display_name', ''),
                                'abstract': work.get('abstract', ''),
                                'authors': json.dumps([a.get('author', {}).get('display_name', '') 
                                                     for a in work.get('authorships', [])]),
                                'year': work.get('publication_year', 0),
                                'source': 'OpenAlex',
                                'url': work.get('id', ''),
                                'keywords': keyword,
                                'language': 'es'
                            }
                            papers.append(paper)
                            
                            if len(papers) >= 200:  # Limit for quick harvest
                                break
                
                logger.info(f"Found {len([p for p in papers if p['keywords'] == keyword])} papers for {keyword}")
                
        except Exception as e:
            logger.error(f"Error with {keyword}: {e}")
        
        time.sleep(1)  # Rate limiting
        
        if len(papers) >= 200:
            break
    
    return papers

def harvest_arxiv_sample():
    """Quick harvest from arXiv"""
    logger.info("📄 Quick harvesting from arXiv...")
    
    papers = []
    legal_terms = ["legal", "law", "governance", "compliance"]
    
    for term in legal_terms[:2]:  # Limit for speed
        try:
            query = urllib.parse.quote(f"ti:{term} OR abs:{term}")
            url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                if response.status == 200:
                    xml_content = response.read().decode('utf-8')
                    
                    # Simple XML parsing for arXiv entries
                    entries = xml_content.split('<entry>')
                    
                    for i, entry in enumerate(entries[1:26]):  # Skip first split and limit to 25
                        try:
                            # Extract title
                            title_start = entry.find('<title>') + 7
                            title_end = entry.find('</title>')
                            title = entry[title_start:title_end].strip() if title_start > 6 else f"ArXiv Paper {i}"
                            
                            # Extract summary (abstract)
                            summary_start = entry.find('<summary>') + 9
                            summary_end = entry.find('</summary>')
                            summary = entry[summary_start:summary_end].strip() if summary_start > 8 else ""
                            
                            if summary and len(summary) > 100:
                                # Extract ID
                                id_start = entry.find('<id>') + 4
                                id_end = entry.find('</id>')
                                arxiv_id = entry[id_start:id_end].split('/')[-1] if id_start > 3 else f"arxiv_{i}"
                                
                                paper = {
                                    'id': f"arxiv_{arxiv_id}",
                                    'title': title,
                                    'abstract': summary,
                                    'authors': 'arXiv authors',  # Simplified
                                    'year': 2024,  # Default recent
                                    'source': 'arXiv',
                                    'url': f"https://arxiv.org/abs/{arxiv_id}",
                                    'keywords': term,
                                    'language': 'en'
                                }
                                papers.append(paper)
                        
                        except Exception as e:
                            logger.debug(f"Error parsing arXiv entry: {e}")
                            continue
            
            logger.info(f"Found {len([p for p in papers if p['keywords'] == term])} arXiv papers for {term}")
            
        except Exception as e:
            logger.error(f"arXiv error with {term}: {e}")
        
        time.sleep(2)  # arXiv rate limiting
    
    return papers

def save_papers(conn, papers):
    """Save papers to database"""
    if not papers:
        return 0
    
    conn.executemany("""
        INSERT OR REPLACE INTO papers (id, title, abstract, authors, year, source, url, keywords, language)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(
        p['id'], p['title'], p['abstract'], p['authors'], p['year'],
        p['source'], p['url'], p['keywords'], p['language']
    ) for p in papers])
    
    conn.commit()
    return len(papers)

def export_training_corpus(conn):
    """Export corpus for LoRA training"""
    cursor = conn.execute("""
        SELECT id, title, abstract, keywords, year, source
        FROM papers 
        WHERE length(abstract) > 100
        ORDER BY length(abstract) DESC, year DESC
    """)
    
    training_data = []
    for row in cursor.fetchall():
        training_data.append({
            'id': row[0],
            'title': row[1],
            'abstract': row[2],
            'keywords': row[3],
            'year': row[4],
            'source': row[5],
            'text': f"Title: {row[1]}\n\nAbstract: {row[2]}\n\nKeywords: {row[3]}"
        })
    
    if not training_data:
        logger.warning("No training data to export")
        return None
    
    # Export compressed corpus
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = f"data/quick_harvest_corpus_{timestamp}.json.gz"
    
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    # Generate stats
    stats = {
        'total_papers': len(training_data),
        'avg_abstract_length': sum(len(p['abstract']) for p in training_data) / len(training_data),
        'by_source': {},
        'by_year': {},
        'corpus_file': output_file,
        'ready_for_training': True
    }
    
    for paper in training_data:
        source = paper['source']
        year = paper['year']
        stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
    
    stats_file = f"data/quick_harvest_stats_{timestamp}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Exported {len(training_data)} papers to {output_file}")
    logger.info(f"📊 Stats saved to {stats_file}")
    
    return output_file, stats_file

def main():
    """Execute quick emergency harvesting"""
    logger.info("🚨 QUICK EMERGENCY HARVESTING STARTED")
    logger.info("⏰ Collecting critical legal data before further restrictions")
    
    # Setup
    conn = setup_database()
    all_papers = []
    
    try:
        # Harvest from available sources
        logger.info("Phase 1: OpenAlex harvesting...")
        openalex_papers = harvest_openalex_sample()
        all_papers.extend(openalex_papers)
        
        logger.info("Phase 2: arXiv harvesting...")
        arxiv_papers = harvest_arxiv_sample()
        all_papers.extend(arxiv_papers)
        
        # Save to database
        saved_count = save_papers(conn, all_papers)
        logger.info(f"💾 Saved {saved_count} papers to database")
        
        # Export for training
        if saved_count > 0:
            corpus_file, stats_file = export_training_corpus(conn)
            
            logger.info("🎯 QUICK HARVESTING COMPLETED")
            logger.info(f"✅ Total papers collected: {saved_count}")
            logger.info(f"📁 Training corpus: {corpus_file}")
            logger.info(f"📊 Statistics: {stats_file}")
            
            # Show breakdown
            openalex_count = len([p for p in all_papers if p['source'] == 'OpenAlex'])
            arxiv_count = len([p for p in all_papers if p['source'] == 'arXiv'])
            
            logger.info(f"📊 Breakdown:")
            logger.info(f"  🔥 OpenAlex: {openalex_count} papers")
            logger.info(f"  📄 arXiv: {arxiv_count} papers")
            
            abstracts_count = len([p for p in all_papers if len(p.get('abstract', '')) > 100])
            logger.info(f"  📝 With good abstracts: {abstracts_count} papers")
            
            return True
        else:
            logger.warning("❌ No papers collected - check API access")
            return False
            
    except Exception as e:
        logger.error(f"Critical error during harvesting: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🔥 READY FOR IMMEDIATE LORA TRAINING")
        print("📋 Next steps:")
        print("1. Open SCM_Legal_Training.ipynb in Colab Pro")
        print("2. Upload the generated corpus file")
        print("3. Execute LoRA training with harvested data")
        print("4. Deploy trained models before more restrictions hit")
    else:
        print("\n⚠️ Harvesting encountered issues - check logs")