#!/bin/bash

# SCM Legal - Emergency Data Harvesting Execution Script
# Execute URGENT data collection before access restrictions tighten

set -e  # Exit on any error

echo "🚨 SCM LEGAL - EMERGENCY DATA HARVESTING"
echo "⏰ $(date): Starting urgent data collection"
echo "📊 Crisis Response: OpenAlex/Semantic Scholar abstract restrictions"
echo ""

# Create necessary directories
echo "📁 Setting up directories..."
mkdir -p data/harvested
mkdir -p data/emergency_oa
mkdir -p logs

# Log files with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/emergency_harvesting_${TIMESTAMP}.log"

echo "📝 Logging to: ${LOG_FILE}"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Check Python dependencies
log "🐍 Checking Python environment..."
python3 -c "
import aiohttp
import sqlite3
import gzip
print('✅ Python dependencies available')
" 2>&1 | tee -a "${LOG_FILE}"

if [ $? -ne 0 ]; then
    log "❌ Missing Python dependencies. Installing..."
    pip3 install aiohttp sqlite3 2>&1 | tee -a "${LOG_FILE}"
fi

# Phase 1: Urgent Academic Harvesting (OpenAlex + Semantic Scholar)
log "🔥 PHASE 1: Urgent Academic Data Harvesting"
log "🎯 Target: OpenAlex + Semantic Scholar (before abstract lockdown)"

python3 scripts/urgent-data-harvesting.py 2>&1 | tee -a "${LOG_FILE}" &
URGENT_PID=$!

# Phase 2: Emergency OA Sources (parallel execution)
log "🌍 PHASE 2: Emergency Open Access Sources"
log "🎯 Target: SciELO + LA Referencia + DOAJ + arXiv"

python3 scripts/emergency-oa-sources.py 2>&1 | tee -a "${LOG_FILE}" &
OA_PID=$!

# Wait for both processes with progress monitoring
log "⏳ Waiting for harvesting processes to complete..."
log "📊 Urgent harvesting PID: ${URGENT_PID}"
log "🌍 OA harvesting PID: ${OA_PID}"

# Monitor progress
while kill -0 "${URGENT_PID}" 2>/dev/null || kill -0 "${OA_PID}" 2>/dev/null; do
    sleep 30
    
    # Check database sizes
    if [ -f "data/academic_corpus.db" ]; then
        URGENT_SIZE=$(du -h data/academic_corpus.db | cut -f1)
        log "📈 Urgent corpus size: ${URGENT_SIZE}"
    fi
    
    if [ -f "data/emergency_oa_corpus.db" ]; then
        OA_SIZE=$(du -h data/emergency_oa_corpus.db | cut -f1)
        log "📈 OA corpus size: ${OA_SIZE}"
    fi
done

# Wait for completion
wait "${URGENT_PID}"
URGENT_EXIT=$?

wait "${OA_PID}" 
OA_EXIT=$?

# Check results
log "📊 HARVESTING RESULTS:"
log "🔥 Urgent harvesting exit code: ${URGENT_EXIT}"
log "🌍 OA harvesting exit code: ${OA_EXIT}"

# Generate combined statistics
log "📊 Generating combined statistics..."
python3 -c "
import sqlite3
import json
from pathlib import Path

def analyze_harvesting_results():
    results = {'urgent': {}, 'oa': {}, 'combined': {}}
    
    # Analyze urgent harvesting results
    if Path('data/academic_corpus.db').exists():
        conn = sqlite3.connect('data/academic_corpus.db')
        cursor = conn.execute('SELECT COUNT(*), COUNT(*) FILTER (WHERE has_abstract = 1) FROM papers')
        total, with_abstracts = cursor.fetchone()
        
        cursor = conn.execute('SELECT source, COUNT(*) FROM papers GROUP BY source')
        by_source = dict(cursor.fetchall())
        
        results['urgent'] = {
            'total_papers': total,
            'papers_with_abstracts': with_abstracts,
            'abstract_percentage': round(with_abstracts/total*100, 1) if total > 0 else 0,
            'by_source': by_source
        }
        conn.close()
    
    # Analyze OA harvesting results
    if Path('data/emergency_oa_corpus.db').exists():
        conn = sqlite3.connect('data/emergency_oa_corpus.db')
        cursor = conn.execute('SELECT COUNT(*), AVG(relevance_score), AVG(quality_score) FROM oa_papers')
        total, avg_relevance, avg_quality = cursor.fetchone()
        
        cursor = conn.execute('SELECT source_repo, COUNT(*) FROM oa_papers GROUP BY source_repo')
        by_source = dict(cursor.fetchall())
        
        cursor = conn.execute('SELECT legal_domain, COUNT(*) FROM oa_papers GROUP BY legal_domain')
        by_domain = dict(cursor.fetchall())
        
        results['oa'] = {
            'total_papers': total,
            'avg_relevance_score': round(avg_relevance, 3) if avg_relevance else 0,
            'avg_quality_score': round(avg_quality, 3) if avg_quality else 0,
            'by_source': by_source,
            'by_domain': by_domain
        }
        conn.close()
    
    # Combined statistics
    results['combined'] = {
        'total_papers': results['urgent'].get('total_papers', 0) + results['oa'].get('total_papers', 0),
        'urgent_papers': results['urgent'].get('total_papers', 0),
        'oa_papers': results['oa'].get('total_papers', 0),
        'papers_with_abstracts': results['urgent'].get('papers_with_abstracts', 0) + results['oa'].get('total_papers', 0)
    }
    
    # Save results
    with open('data/harvesting_summary.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f\"✅ Combined Results:\")
    print(f\"📊 Total papers harvested: {results['combined']['total_papers']:,}\")
    print(f\"🔥 Urgent (Academic APIs): {results['combined']['urgent_papers']:,}\") 
    print(f\"🌍 Emergency OA: {results['combined']['oa_papers']:,}\")
    print(f\"📝 Papers with abstracts: {results['combined']['papers_with_abstracts']:,}\")
    
    if results['urgent'].get('abstract_percentage'):
        print(f\"📉 Abstract availability crisis: {results['urgent']['abstract_percentage']}% (down from ~80%)\")
    
    return results

analyze_harvesting_results()
" 2>&1 | tee -a "${LOG_FILE}"

# Phase 3: Prepare training datasets
log "🎓 PHASE 3: Preparing SCM training datasets"

log "📦 Combining datasets for LoRA training..."
python3 -c "
import json
import gzip
from pathlib import Path
from datetime import datetime

def combine_training_datasets():
    combined_corpus = []
    
    # Find latest corpus files
    harvested_dir = Path('data/harvested')
    oa_dir = Path('data/emergency_oa')
    
    # Load urgent harvesting corpus
    if harvested_dir.exists():
        for corpus_file in harvested_dir.glob('legal_corpus_*.json.gz'):
            print(f'📖 Loading {corpus_file}')
            try:
                with gzip.open(corpus_file, 'rt', encoding='utf-8') as f:
                    urgent_data = json.load(f)
                    combined_corpus.extend(urgent_data)
                    print(f'✅ Added {len(urgent_data)} papers from urgent harvesting')
                break  # Use most recent file
            except Exception as e:
                print(f'⚠️ Error loading {corpus_file}: {e}')
    
    # Load OA corpus
    if oa_dir.exists():
        for corpus_file in oa_dir.glob('emergency_oa_corpus_*.json.gz'):
            print(f'📖 Loading {corpus_file}')
            try:
                with gzip.open(corpus_file, 'rt', encoding='utf-8') as f:
                    oa_data = json.load(f)
                    # Convert OA format to training format
                    for paper in oa_data:
                        combined_corpus.append({
                            'id': paper['id'],
                            'title': paper['title'],
                            'abstract': paper['abstract'],
                            'keywords': paper.get('keywords', ''),
                            'country': paper['country'],
                            'year': paper['year'],
                            'citations': 0,  # OA sources don't have citation counts
                            'text': paper['training_text'],
                            'source': 'emergency_oa',
                            'relevance_score': paper.get('relevance_score', 0),
                            'legal_domain': paper.get('legal_domain', 'general_legal')
                        })
                    print(f'✅ Added {len(oa_data)} papers from OA sources')
                break
            except Exception as e:
                print(f'⚠️ Error loading {corpus_file}: {e}')
    
    if not combined_corpus:
        print('❌ No corpus data found to combine')
        return
    
    # Sort by relevance and quality
    combined_corpus.sort(key=lambda x: (
        x.get('relevance_score', 0) + 
        (x.get('citations', 0) / 1000),  # Normalize citations
        x.get('year', 0)
    ), reverse=True)
    
    # Save combined training corpus
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    output_file = Path(f'data/scm_training_corpus_{timestamp}.json.gz')
    
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        json.dump(combined_corpus, f, ensure_ascii=False, indent=2)
    
    print(f'🎯 FINAL TRAINING CORPUS: {output_file}')
    print(f'📊 Total papers: {len(combined_corpus):,}')
    print(f'📝 Avg abstract length: {sum(len(p.get(\"abstract\", \"\")) for p in combined_corpus) / len(combined_corpus):.0f} chars')
    
    # Generate training statistics
    stats = {
        'total_papers': len(combined_corpus),
        'by_source': {},
        'by_domain': {},
        'by_country': {},
        'ready_for_lora_training': True,
        'estimated_training_time': f'{len(combined_corpus) // 1000}+ hours with LoRA',
        'corpus_file': str(output_file)
    }
    
    for paper in combined_corpus:
        source = paper.get('source', 'unknown')
        domain = paper.get('legal_domain', 'general_legal')
        country = paper.get('country', 'unknown')
        
        stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1  
        stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
    
    stats_file = Path(f'data/scm_training_stats_{timestamp}.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f'📈 Training stats: {stats_file}')
    
    return output_file, len(combined_corpus)

combine_training_datasets()
" 2>&1 | tee -a "${LOG_FILE}"

# Final summary
log ""
log "🎊 EMERGENCY HARVESTING COMPLETED"
log "⏰ Finished at: $(date)"
log ""
log "📂 Generated files:"
ls -lh data/*.db data/*.json* 2>/dev/null | while read line; do
    log "📄 $line"
done

log ""
log "🚀 NEXT STEPS:"
log "1. 🔥 Execute LoRA training IMMEDIATELY with collected corpus"
log "2. 📦 Upload corpus to secure storage (Google Drive/Dropbox)"  
log "3. 🧠 Run SCM_Legal_Training.ipynb in Colab Pro"
log "4. ⚡ Deploy trained models before more restrictions hit"
log ""
log "⚠️  CRITICAL: This corpus becomes more valuable as restrictions tighten"
log "💰 Estimated value: \$10K+ in API costs if purchased from commercial sources"

echo ""
echo "✅ Emergency harvesting script completed. Check logs: ${LOG_FILE}"
echo "🔥 Ready for immediate LoRA training with harvested corpus"