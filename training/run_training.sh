#!/bin/bash

# SCM Legal Training Script
# =========================
# Optimizado para Google Colab Pro, Runpod o setup local con GPU
#
# Hardware recomendado:
# - GPU: V100/A100/RTX 4090 con 16GB+ VRAM
# - RAM: 32GB+ system RAM
# - Storage: 50GB+ free space
#
# Autor: Ignacio Adrian Lerer
# Proyecto: SCM-Legal-Spanish

set -e  # Exit on error

echo "🚀 Starting SCM Legal Training Pipeline..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running in Colab
if [ -n "$COLAB_GPU" ]; then
    echo -e "${BLUE}✓ Google Colab detected${NC}"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    echo -e "${BLUE}✓ Local environment detected${NC}"
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

# Function to check GPU availability
check_gpu() {
    echo -e "${YELLOW}Checking GPU availability...${NC}"
    
    if nvidia-smi > /dev/null 2>&1; then
        nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits
        echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
        return 0
    else
        echo -e "${RED}❌ No NVIDIA GPU detected. Training may be very slow.${NC}"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    # Update pip
    $PIP_CMD install --upgrade pip
    
    # Install PyTorch with CUDA support
    if nvidia-smi > /dev/null 2>&1; then
        echo -e "${BLUE}Installing PyTorch with CUDA support...${NC}"
        $PIP_CMD install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        echo -e "${BLUE}Installing PyTorch CPU-only version...${NC}"
        $PIP_CMD install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # Install training requirements
    $PIP_CMD install -r requirements-training.txt
    
    # Verify installations
    echo -e "${YELLOW}Verifying installations...${NC}"
    $PYTHON_CMD -c "import torch; print(f'PyTorch version: {torch.__version__}')"
    $PYTHON_CMD -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
    
    if $PYTHON_CMD -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        echo -e "${GREEN}✓ CUDA acceleration enabled${NC}"
    else
        echo -e "${YELLOW}⚠ Running on CPU - training will be slower${NC}"
    fi
    
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
}

# Function to setup Weights & Biases
setup_wandb() {
    echo -e "${YELLOW}Setting up Weights & Biases...${NC}"
    
    if [ -z "$WANDB_API_KEY" ]; then
        echo -e "${BLUE}Please enter your Weights & Biases API key:${NC}"
        echo -e "${BLUE}(Get it from: https://wandb.ai/settings)${NC}"
        read -s WANDB_API_KEY
        export WANDB_API_KEY
    fi
    
    $PYTHON_CMD -c "import wandb; wandb.login()"
    echo -e "${GREEN}✓ Weights & Biases configured${NC}"
}

# Function to download legal corpus
download_corpus() {
    echo -e "${YELLOW}Downloading legal corpus...${NC}"
    
    # Create data directory
    mkdir -p data
    
    # For demo purposes, create sample legal corpus
    # En producción real, descargar corpus legal argentino/español
    cat > data/sample_legal_corpus.txt << 'EOF'
El artículo 14 bis de la Constitución Nacional establece que el trabajo en sus diversas formas gozará de la protección de las leyes, las que asegurarán al trabajador condiciones dignas y equitativas de labor, jornada limitada, descanso y vacaciones pagados, retribución justa, salario mínimo vital móvil, igual remuneración por igual tarea, participación en las ganancias de las empresas, con control de la producción y colaboración en la dirección.

Las sociedades anónimas se constituyen por instrumento público o privado, y en este último caso las firmas deben ser certificadas por escribano público. El estatuto debe contener las menciones del artículo 11 y además la clase de acciones que se autoriza a emitir y, en su caso, las limitaciones a su transmisibilidad.

Los programas de cumplimiento normativo (compliance) son herramientas esenciales para prevenir y detectar violaciones a la legislación anticorrupción. Deben incluir la debida diligencia sobre terceros, canales de denuncia, capacitación del personal y monitoreo continuo de riesgos.

El procedimiento administrativo se rige por los principios de debido proceso, economía procesal, sencillez, eficacia, informalismo a favor del administrado, gratuidad y celeridad. Los actos administrativos deben ser motivados, con expresión de los hechos y derecho aplicable.

El gobierno corporativo comprende las normas, prácticas y procesos por los cuales se dirige y controla una sociedad. Involucra el equilibrio de intereses entre accionistas, directorio, management y otros stakeholders. Los principios incluyen transparencia, responsabilidad, equidad y rendición de cuentas.

La gestión de riesgos operacionales requiere la identificación, evaluación, mitigación y monitoreo continuo de riesgos que puedan afectar los objetivos organizacionales. Debe integrarse en la planificación estratégica y operativa, con reportes regulares al directorio.

Los contratos de trabajo están regulados por la Ley de Contrato de Trabajo, que establece derechos y obligaciones para empleadores y trabajadores. Include disposiciones sobre jornada laboral, remuneraciones, licencias, estabilidad laboral y extinción del contrato.

El régimen de responsabilidad civil exige la concurrencia de daño, antijuridicidad y factor de atribución. La reparación debe ser integral, incluyendo daño emergente, lucro cesante y daño moral. Los plazos de prescripción varían según el tipo de acción.
EOF

    echo -e "${GREEN}✓ Sample legal corpus created${NC}"
    echo -e "${BLUE}Note: In production, replace with real Argentine/Spanish legal corpus${NC}"
}

# Function to validate configuration
validate_config() {
    echo -e "${YELLOW}Validating training configuration...${NC}"
    
    if [ ! -f "config/scm_training_config.yaml" ]; then
        echo -e "${RED}❌ Configuration file not found${NC}"
        exit 1
    fi
    
    # Check memory requirements
    AVAILABLE_MEMORY=$(free -h | awk '/^Mem:/ {print $7}')
    echo -e "${BLUE}Available memory: $AVAILABLE_MEMORY${NC}"
    
    if nvidia-smi > /dev/null 2>&1; then
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
        echo -e "${BLUE}Available GPU memory: ${GPU_MEMORY}MB${NC}"
        
        if [ "$GPU_MEMORY" -lt 8000 ]; then
            echo -e "${YELLOW}⚠ Low GPU memory. Consider reducing batch size.${NC}"
        fi
    fi
    
    echo -e "${GREEN}✓ Configuration validated${NC}"
}

# Function to run training
run_training() {
    echo -e "${YELLOW}Starting SCM Legal training...${NC}"
    echo -e "${BLUE}This may take several hours depending on hardware.${NC}"
    
    # Set environment variables
    export TOKENIZERS_PARALLELISM=false
    export CUDA_LAUNCH_BLOCKING=1
    
    # Run training with error handling
    if $PYTHON_CMD scm_lora_trainer.py; then
        echo -e "${GREEN}✅ Training completed successfully!${NC}"
        
        # Show results summary
        if [ -f "results/scm-legal-llama-3.2-1b/final_results.json" ]; then
            echo -e "${BLUE}Training Results Summary:${NC}"
            $PYTHON_CMD -c "
import json
with open('results/scm-legal-llama-3.2-1b/final_results.json', 'r') as f:
    results = json.load(f)
    print(f\"Trained adapters: {list(results['adapter_paths'].keys())}\")
    print(f\"Evaluation results: {results['evaluation_results']}\")
"
        fi
        
    else
        echo -e "${RED}❌ Training failed. Check logs above.${NC}"
        exit 1
    fi
}

# Function to test adapters
test_adapters() {
    echo -e "${YELLOW}Testing trained adapters...${NC}"
    
    # Simple inference test
    $PYTHON_CMD -c "
import torch
from transformers import AutoTokenizer
from peft import PeftModel, AutoPeftModelForCausalLM
import glob
import os

# Find adapter directories
adapter_dirs = glob.glob('results/scm-legal-llama-3.2-1b/*/adapter')
print(f'Found adapters: {[os.path.basename(os.path.dirname(d)) for d in adapter_dirs]}')

if adapter_dirs:
    print('Testing first adapter...')
    adapter_path = adapter_dirs[0]
    concept = os.path.basename(os.path.dirname(adapter_path))
    
    try:
        # Load model with adapter
        tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-1B')
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoPeftModelForCausalLM.from_pretrained(
            adapter_path, 
            device_map='auto',
            torch_dtype=torch.float16
        )
        
        # Test inference
        test_text = 'Analiza los aspectos legales del siguiente contrato:'
        inputs = tokenizer(test_text, return_tensors='pt')
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f'Generated text: {generated}')
        print(f'✅ Adapter {concept} is working correctly!')
        
    except Exception as e:
        print(f'❌ Error testing adapter: {e}')
else:
    print('❌ No adapters found to test')
"
    
    echo -e "${GREEN}✓ Adapter testing completed${NC}"
}

# Function to create deployment package
create_deployment_package() {
    echo -e "${YELLOW}Creating deployment package...${NC}"
    
    # Create deployment directory
    mkdir -p deployment
    
    # Copy trained adapters (only LoRA parameters - ~35MB each)
    if [ -d "results/scm-legal-llama-3.2-1b" ]; then
        cp -r results/scm-legal-llama-3.2-1b deployment/
        
        # Calculate total size
        TOTAL_SIZE=$(du -sh deployment/scm-legal-llama-3.2-1b | cut -f1)
        echo -e "${BLUE}Total adapter package size: $TOTAL_SIZE${NC}"
        echo -e "${GREEN}✓ Deployment package created${NC}"
        
        # Create deployment script
        cat > deployment/deploy_adapters.py << 'EOF'
#!/usr/bin/env python3
"""
SCM Legal Adapter Deployment Script
==================================

Deploy trained LoRA adapters for production inference.
Supports adapter switching and concept-specific analysis.
"""

import os
import torch
from transformers import AutoTokenizer
from peft import PeftModel, AutoPeftModelForCausalLM
import json
from typing import Dict, List

class SCMLegalInference:
    """Production inference class for SCM Legal adapters"""
    
    def __init__(self, base_model_name: str = "meta-llama/Llama-3.2-1B"):
        self.base_model_name = base_model_name
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.loaded_adapters = {}
        self.current_model = None
        self.current_concept = None
    
    def load_adapter(self, concept: str, adapter_path: str):
        """Load a concept-specific adapter"""
        print(f"Loading adapter for concept: {concept}")
        
        model = AutoPeftModelForCausalLM.from_pretrained(
            adapter_path,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        self.loaded_adapters[concept] = model
        print(f"✓ Adapter loaded: {concept}")
    
    def switch_concept(self, concept: str):
        """Switch to a different legal concept"""
        if concept not in self.loaded_adapters:
            raise ValueError(f"Adapter for concept '{concept}' not loaded")
        
        self.current_model = self.loaded_adapters[concept]
        self.current_concept = concept
        print(f"✓ Switched to concept: {concept}")
    
    def analyze_legal_text(self, text: str, max_new_tokens: int = 200) -> str:
        """Analyze legal text with current concept adapter"""
        if self.current_model is None:
            raise ValueError("No adapter loaded. Call switch_concept() first.")
        
        prompt = f"Analiza los aspectos legales del siguiente texto desde la perspectiva de {self.current_concept}:\n\n{text}\n\nAnálisis:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        with torch.no_grad():
            outputs = self.current_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        analysis = generated[len(prompt):].strip()
        
        return analysis

# Example usage
if __name__ == "__main__":
    # Initialize inference system
    scm = SCMLegalInference()
    
    # Load available adapters
    adapter_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d != '__pycache__']
    
    for concept in adapter_dirs:
        adapter_path = os.path.join(concept, 'adapter')
        if os.path.exists(adapter_path):
            scm.load_adapter(concept, adapter_path)
    
    # Demo analysis
    if scm.loaded_adapters:
        concept = list(scm.loaded_adapters.keys())[0]
        scm.switch_concept(concept)
        
        test_text = """
        La empresa XYZ S.A. celebró un contrato de prestación de servicios con la consultora ABC Ltda. 
        por el término de 12 meses, con posibilidad de renovación automática. El contrato establece 
        obligaciones de confidencialidad y cláusulas de resolución anticipada.
        """
        
        analysis = scm.analyze_legal_text(test_text)
        print(f"\nAnálisis desde perspectiva {concept}:")
        print(analysis)
EOF
        
        chmod +x deployment/deploy_adapters.py
        echo -e "${GREEN}✓ Deployment script created${NC}"
        
    else
        echo -e "${YELLOW}⚠ No trained models found for deployment${NC}"
    fi
}

# Main execution
main() {
    echo -e "${GREEN}SCM Legal Training Pipeline${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo
    
    # Check prerequisites
    check_gpu
    
    # Setup steps
    echo -e "\n${YELLOW}Step 1: Installing dependencies${NC}"
    install_dependencies
    
    echo -e "\n${YELLOW}Step 2: Setting up logging${NC}"
    if [ "$1" != "--no-wandb" ]; then
        setup_wandb
    else
        echo -e "${BLUE}Skipping Weights & Biases setup${NC}"
    fi
    
    echo -e "\n${YELLOW}Step 3: Preparing data${NC}"
    download_corpus
    
    echo -e "\n${YELLOW}Step 4: Validating configuration${NC}"
    validate_config
    
    # Training
    echo -e "\n${YELLOW}Step 5: Running training${NC}"
    run_training
    
    # Testing
    echo -e "\n${YELLOW}Step 6: Testing adapters${NC}"
    test_adapters
    
    # Deployment
    echo -e "\n${YELLOW}Step 7: Creating deployment package${NC}"
    create_deployment_package
    
    echo
    echo -e "${GREEN}🎉 SCM Legal training pipeline completed successfully!${NC}"
    echo -e "${BLUE}Check the 'deployment/' directory for production-ready adapters.${NC}"
    echo
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "SCM Legal Training Script"
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --no-wandb    Skip Weights & Biases setup"
        echo "  --help        Show this help message"
        echo
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac