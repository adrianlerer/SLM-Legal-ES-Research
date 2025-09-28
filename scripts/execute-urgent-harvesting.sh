#!/bin/bash

# SCM Legal - Execute Urgent Data Harvesting
# Crisis response script for academic data extraction before access restrictions

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Project paths
PROJECT_ROOT="/home/user/SLM-Legal-Spanish"
DATA_DIR="$PROJECT_ROOT/data"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
LOGS_DIR="$DATA_DIR/logs"

# Create necessary directories
mkdir -p "$DATA_DIR"/{harvested,hispano_legal,logs,corpus}
mkdir -p "$LOGS_DIR"

# Log file with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOGS_DIR/urgent_harvesting_$TIMESTAMP.log"

log "🚨 STARTING URGENT ACADEMIC DATA HARVESTING"
log "📁 Project root: $PROJECT_ROOT"
log "📊 Data directory: $DATA_DIR"
log "📝 Log file: $LOG_FILE"

# Function to check if Python is available and install dependencies
setup_python_environment() {
    log "🐍 Setting up Python environment..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.8+"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    log "Python version: $python_version"
    
    # Install required packages
    log "📦 Installing required Python packages..."
    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user aiohttp requests beautifulsoup4 lxml sqlite3 gzip pandas
    
    success "Python environment ready"
}

# Function to execute urgent academic harvesting
execute_urgent_harvesting() {
    log "🚨 Executing urgent academic data harvesting..."
    
    cd "$PROJECT_ROOT"
    
    # Run the urgent harvesting script
    python3 "$SCRIPTS_DIR/urgent-data-harvesting.py" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        success "Urgent academic harvesting completed successfully"
        return 0
    else
        error "Urgent academic harvesting failed"
        return 1
    fi
}

# Function to execute Hispanic legal sources harvesting
execute_hispano_harvesting() {
    log "🌎 Executing Hispanic legal sources harvesting..."
    
    cd "$PROJECT_ROOT"
    
    # Run the Hispanic legal sources script
    python3 "$SCRIPTS_DIR/hispano-legal-sources.py" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        success "Hispanic legal harvesting completed successfully"
        return 0
    else
        error "Hispanic legal harvesting failed"
        return 1
    fi
}

# Function to combine and process harvested data
process_harvested_data() {
    log "🔄 Processing and combining harvested data..."
    
    cd "$DATA_DIR"
    
    # Create combined corpus directory
    mkdir -p combined_corpus
    
    # Count harvested files
    academic_files=$(find harvested/ -name "*.json.gz" 2>/dev/null | wc -l || echo "0")
    hispano_files=$(find hispano_legal/ -name "*.json.gz" 2>/dev/null | wc -l || echo "0")
    
    log "📊 Academic files harvested: $academic_files"
    log "📊 Hispanic legal files harvested: $hispano_files"
    
    if [ "$academic_files" -gt 0 ] || [ "$hispano_files" -gt 0 ]; then
        # Create metadata file
        cat > combined_corpus/harvesting_metadata.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "harvesting_session": "$TIMESTAMP",
    "crisis_response": {
        "reason": "OpenAlex/Semantic Scholar abstract restrictions",
        "urgency": "high",
        "strategy": "extract_before_lockdown"
    },
    "sources": {
        "academic_international": {
            "files": $academic_files,
            "sources": ["OpenAlex", "Semantic Scholar"]
        },
        "hispanic_legal": {
            "files": $hispano_files,
            "sources": ["SciELO", "Institutional Repositories", "Government Databases"]
        }
    },
    "next_steps": [
        "Combine datasets for SCM training",
        "Apply quality filters",
        "Generate training configurations",
        "Execute LoRA fine-tuning"
    ]
}
EOF
        success "Harvesting metadata created"
    else
        warning "No files harvested - check error logs"
    fi
}

# Function to generate training preparation script
generate_training_prep() {
    log "📋 Generating training preparation script..."
    
    cat > "$DATA_DIR/prepare_training_data.py" << 'EOF'
#!/usr/bin/env python3
"""
Prepare harvested data for SCM LoRA training
Combines academic and Hispanic legal sources with quality filtering
"""

import json
import gzip
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def combine_harvested_data():
    """Combine all harvested datasets for training"""
    data_dir = Path(".")
    combined_texts = []
    
    # Process compressed JSON files
    for json_file in data_dir.glob("**/*.json.gz"):
        logger.info(f"Processing: {json_file}")
        try:
            with gzip.open(json_file, 'rt', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    for item in data:
                        if 'text' in item or 'abstract' in item:
                            combined_texts.append({
                                'text': item.get('text', item.get('abstract', '')),
                                'source': str(json_file.name),
                                'metadata': item.get('metadata', {})
                            })
        except Exception as e:
            logger.error(f"Error processing {json_file}: {e}")
    
    # Process SQLite databases
    for db_file in data_dir.glob("**/*.db"):
        logger.info(f"Processing database: {db_file}")
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.execute("""
                SELECT title, abstract, full_text, jurisdiction, legal_area, confidence_score
                FROM papers 
                WHERE (abstract IS NOT NULL AND length(abstract) > 100)
                   OR (full_text IS NOT NULL AND length(full_text) > 200)
            """)
            
            for row in cursor.fetchall():
                title, abstract, full_text, jurisdiction, legal_area, confidence = row
                text_content = f"Title: {title}\n"
                if abstract:
                    text_content += f"Abstract: {abstract}\n"
                if full_text:
                    text_content += f"Content: {full_text[:1000]}...\n"
                
                combined_texts.append({
                    'text': text_content,
                    'source': str(db_file.name),
                    'metadata': {
                        'jurisdiction': jurisdiction,
                        'legal_area': legal_area,
                        'confidence': confidence
                    }
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error processing database {db_file}: {e}")
    
    # Export combined dataset
    output_file = f"combined_legal_corpus_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_texts, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Combined corpus saved: {output_file}")
    logger.info(f"📊 Total texts: {len(combined_texts)}")
    
    return output_file, len(combined_texts)

if __name__ == "__main__":
    combine_harvested_data()
EOF

    chmod +x "$DATA_DIR/prepare_training_data.py"
    success "Training preparation script created"
}

# Function to create emergency backup
create_emergency_backup() {
    log "💾 Creating emergency backup of harvested data..."
    
    cd "$PROJECT_ROOT"
    
    backup_name="emergency_legal_corpus_$TIMESTAMP.tar.gz"
    
    # Create compressed backup
    tar -czf "$backup_name" \
        data/harvested/ \
        data/hispano_legal/ \
        data/*.db \
        data/combined_corpus/ \
        scripts/ \
        2>/dev/null || true
    
    if [ -f "$backup_name" ]; then
        backup_size=$(du -h "$backup_name" | cut -f1)
        success "Emergency backup created: $backup_name ($backup_size)"
        
        # Move to data directory
        mv "$backup_name" "$DATA_DIR/"
        
        log "💡 Backup location: $DATA_DIR/$backup_name"
    else
        warning "Emergency backup creation failed or no data to backup"
    fi
}

# Function to display summary
display_summary() {
    log "📊 HARVESTING SESSION SUMMARY"
    echo ""
    echo "Timestamp: $TIMESTAMP"
    echo "Log file: $LOG_FILE"
    echo ""
    
    # Count files in data directories
    if [ -d "$DATA_DIR/harvested" ]; then
        academic_count=$(find "$DATA_DIR/harvested" -name "*.json.gz" | wc -l)
        echo "📚 Academic files: $academic_count"
    fi
    
    if [ -d "$DATA_DIR/hispano_legal" ]; then
        hispano_count=$(find "$DATA_DIR/hispano_legal" -name "*.json.gz" | wc -l)
        echo "🌎 Hispanic legal files: $hispano_count"
    fi
    
    if [ -d "$DATA_DIR" ]; then
        db_count=$(find "$DATA_DIR" -name "*.db" | wc -l)
        echo "🗃️ Database files: $db_count"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Review harvested data in $DATA_DIR"
    echo "2. Run: cd $DATA_DIR && python3 prepare_training_data.py"
    echo "3. Execute LoRA training with combined corpus"
    echo "4. Deploy trained SCM model"
    echo ""
}

# Main execution
main() {
    log "🚀 Starting urgent harvesting workflow..."
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/package.json" ]; then
        error "Not in SCM Legal project directory. Expected: $PROJECT_ROOT"
        exit 1
    fi
    
    # Execute harvesting workflow
    {
        setup_python_environment
        
        # Execute both harvesting strategies in parallel for speed
        log "⚡ Running harvesting processes..."
        
        # Start academic harvesting in background
        execute_urgent_harvesting &
        academic_pid=$!
        
        # Start Hispanic legal harvesting in background  
        execute_hispano_harvesting &
        hispano_pid=$!
        
        # Wait for both processes
        wait $academic_pid
        academic_result=$?
        
        wait $hispano_pid  
        hispano_result=$?
        
        # Process results
        if [ $academic_result -eq 0 ] || [ $hispano_result -eq 0 ]; then
            success "At least one harvesting process completed successfully"
            process_harvested_data
            generate_training_prep
            create_emergency_backup
        else
            error "All harvesting processes failed"
        fi
        
    } 2>&1 | tee -a "$LOG_FILE"
    
    display_summary
}

# Error handling
trap 'error "Script interrupted"; exit 1' INT TERM

# Execute main function
main "$@"

success "🎉 Urgent harvesting workflow completed!"
log "Check $LOG_FILE for detailed logs"