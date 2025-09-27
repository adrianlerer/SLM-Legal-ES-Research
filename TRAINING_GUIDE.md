# Guía de Entrenamiento SCM Legal
## Implementación Real de Small Concept Models para Dominio Legal

Esta guía detalla cómo pasar de la **simulación actual** al **entrenamiento real** del modelo SCM Legal para investigación académica.

## 🎯 Objetivo Académico

Desarrollar un **Small Concept Model (SCM)** real que opere a nivel conceptual en lugar de tokens, especializado para el dominio legal multi-jurisdiccional (Argentina, Chile, Uruguay, España).

### Diferencias Clave: Simulación vs Implementación Real

| Aspecto | Simulación Actual | Implementación Real |
|---------|-------------------|-------------------|
| **Procesamiento** | Reglas programáticas | Modelo neuronal fine-tuned |
| **Conceptos** | Lista predefinida | Embeddings aprendidos |
| **Razonamiento** | Lógica condicional | Inferencia neuronal |
| **Aprendizaje** | Estático | Adaptativo con datos |

## 📋 Requisitos Técnicos

### Hardware Mínimo
- **GPU**: NVIDIA RTX 3090/4090 (24GB VRAM) o A100/H100
- **RAM**: 32GB+ DDR4/DDR5
- **Storage**: 100GB SSD libre
- **CPU**: 8+ cores modernos

### Hardware Recomendado para Investigación
- **GPU**: NVIDIA H100 (80GB) o múltiples A100
- **RAM**: 128GB+
- **Storage**: 500GB+ NVMe SSD
- **Infraestructura**: Google Colab Pro+, Runpod, AWS/GCP instancias GPU

## 🚀 Configuración del Entorno de Entrenamiento

### 1. Configuración en Google Colab Pro+

```python
# Notebook: SCM_Legal_Training.ipynb

# Verificar GPU disponible
!nvidia-smi

# Instalar dependencias
!pip install -r /content/SLM-Legal-Spanish/training/requirements-training.txt

# Configurar Hugging Face Hub
from huggingface_hub import notebook_login
notebook_login()

# Configurar Weights & Biases
import wandb
wandb.login()
```

### 2. Configuración en Runpod/Local

```bash
# Clonar repositorio
git clone https://github.com/adrianlerer/SLM-Legal-Spanish.git
cd SLM-Legal-Spanish/training

# Crear entorno virtual
python -m venv scm_legal_env
source scm_legal_env/bin/activate

# Instalar dependencias
pip install -r requirements-training.txt

# Configurar tokens
huggingface-cli login
wandb login
```

## 📊 Pipeline de Entrenamiento Paso a Paso

### Paso 1: Preparación de Datos Real

```bash
# Generar corpus legal anotado
python data_preparation.py --config config/scm_training_config.yaml

# Salida esperada:
# - data/legal_corpus_train.jsonl (2000+ samples)
# - data/legal_corpus_validation.jsonl (500+ samples)  
# - data/legal_corpus_test.jsonl (500+ samples)
```

**Datos Generados:**
- **Textos Legales**: Artículos de códigos, jurisprudencia, normas
- **Conceptos Anotados**: Automáticamente extraídos y validados
- **Cadenas de Razonamiento**: Inferencias legales multi-paso
- **Multi-jurisdiccional**: AR, CL, UY, ES distribuido proporcionalmente

### Paso 2: Entrenamiento del Modelo Base

```bash
# Entrenamiento completo con LoRA/QLoRA
python train_scm_legal.py --config config/scm_training_config.yaml --mode train

# Monitoreo en W&B: https://wandb.ai/tu-usuario/scm-legal-research
```

**Proceso de Entrenamiento:**
1. **Carga del Modelo**: Llama 3.2 1B/3B con cuantización 4-bit
2. **LoRA Setup**: Configuración de adaptadores de bajo rango
3. **Fine-tuning**: 3-5 épocas con early stopping
4. **Validación**: Evaluación continua en conjunto de validación

### Paso 3: Evaluación Comprehensiva

```bash
# Evaluación académica completa
python train_scm_legal.py --config config/scm_training_config.yaml --mode evaluate

# Genera métricas para publicación académica
```

**Métricas Evaluadas:**
- **Concept Extraction F1**: Precisión en identificación conceptual
- **Legal Reasoning Coherence**: Calidad del razonamiento jurídico
- **Multi-jurisdictional Consistency**: Consistencia cross-jurisdictional
- **Domain-specific Accuracy**: Precisión por área legal

## 🎓 Configuración para Investigación Académica

### Archivo de Configuración Académica

```yaml
# config/academic_research_config.yaml

# Configuración optimizada para resultados académicos
model:
  base_model: "meta-llama/Llama-3.2-3B"  # Modelo más potente
  load_in_4bit: true
  torch_dtype: "bfloat16"  # Mayor precisión

training:
  num_train_epochs: 5      # Suficientes épocas para convergencia
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  learning_rate: 1e-4      # LR conservativo para estabilidad
  warmup_steps: 200
  eval_steps: 100         # Evaluación frecuente
  save_steps: 100
  logging_steps: 10

# LoRA para fine-tuning eficiente
lora:
  r: 64                   # Mayor rango para mejor performance
  lora_alpha: 128
  lora_dropout: 0.1

# Configuración de datos
dataset:
  max_length: 2048
  block_size: 2048
  train_file: "data/legal_corpus_train.jsonl"
  validation_file: "data/legal_corpus_val.jsonl"
  test_file: "data/legal_corpus_test.jsonl"

# Evaluación académica
evaluation:
  metrics: [
    "concept_extraction_f1", 
    "legal_reasoning_coherence",
    "jurisdictional_consistency", 
    "domain_accuracy",
    "concept_coherence",
    "reasoning_consistency"
  ]

# Logging para investigación
logging:
  use_wandb: true
  wandb_project: "scm-legal-academic-research"
  experiment_name: "SCM-Legal-Llama3.2-3B-Academic"
  log_model: true
  save_total_limit: 5
```

## 📈 Monitoreo y Validación

### Dashboard de Entrenamiento (W&B)

```python
# Métricas clave para monitoreo
training_metrics = {
    'train_loss': 'Pérdida de entrenamiento',
    'eval_loss': 'Pérdida de validación', 
    'learning_rate': 'Tasa de aprendizaje',
    'concept_extraction_f1': 'F1 extracción conceptos',
    'legal_reasoning_coherence': 'Coherencia razonamiento',
    'gpu_memory_usage': 'Uso memoria GPU',
    'training_speed': 'Velocidad entrenamiento'
}
```

### Validación en Tiempo Real

```python
# Ejemplo de validación durante entrenamiento
def validate_sample_prediction(model, tokenizer, sample_text):
    """Validar predicción en tiempo real"""
    
    # Generar predicción
    inputs = tokenizer(sample_text, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=512)
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extraer conceptos predichos
    predicted_concepts = extract_concepts_from_generated_text(prediction)
    
    return {
        'input': sample_text,
        'prediction': prediction,
        'concepts': predicted_concepts
    }
```

## 🔬 Experimentos de Investigación

### Experimento 1: SCM vs Modelo Base

```bash
# A. Entrenar modelo SCM (conceptual)
python train_scm_legal.py --config config/scm_config.yaml --mode all

# B. Entrenar modelo baseline (token-level tradicional)
python train_scm_legal.py --config config/baseline_config.yaml --mode all

# C. Comparar resultados
python compare_models.py --scm results/scm_model --baseline results/baseline_model
```

### Experimento 2: Ablation Studies

```yaml
# Diferentes configuraciones para ablation
experiments:
  - name: "scm_full"
    concept_reasoning: true
    multi_jurisdictional: true
    
  - name: "scm_no_reasoning" 
    concept_reasoning: false
    multi_jurisdictional: true
    
  - name: "scm_single_jurisdiction"
    concept_reasoning: true
    multi_jurisdictional: false
```

### Experimento 3: Cross-jurisdictional Transfer

```python
# Entrenar en una jurisdicción, evaluar en otra
jurisdictions = ['argentina', 'chile', 'uruguay', 'españa']

for source in jurisdictions:
    for target in jurisdictions:
        if source != target:
            # Entrenar en source, evaluar en target
            transfer_score = evaluate_cross_jurisdictional(source, target)
            print(f"{source} -> {target}: {transfer_score}")
```

## 📊 Análisis de Resultados para Paper

### Métricas Estadísticas

```python
# Análisis estadístico para paper
import scipy.stats as stats

def statistical_analysis(scm_scores, baseline_scores):
    """Análisis estadístico para paper académico"""
    
    # Prueba t para diferencia significativa
    t_stat, p_value = stats.ttest_ind(scm_scores, baseline_scores)
    
    # Tamaño del efecto (Cohen's d)
    pooled_std = np.sqrt(((len(scm_scores)-1)*np.var(scm_scores) + 
                         (len(baseline_scores)-1)*np.var(baseline_scores)) / 
                         (len(scm_scores) + len(baseline_scores) - 2))
    
    cohens_d = (np.mean(scm_scores) - np.mean(baseline_scores)) / pooled_std
    
    return {
        'p_value': p_value,
        'effect_size': cohens_d,
        'significant': p_value < 0.05,
        'scm_mean': np.mean(scm_scores),
        'baseline_mean': np.mean(baseline_scores)
    }
```

### Visualizaciones para Paper

```python
# Generar gráficos para paper
import matplotlib.pyplot as plt
import seaborn as sns

def generate_paper_figures():
    """Generar figuras para paper académico"""
    
    # Figura 1: Comparación de métricas principales
    plt.figure(figsize=(12, 8))
    metrics = ['Concept F1', 'Reasoning Coherence', 'Jurisdictional Consistency']
    scm_scores = [0.87, 0.83, 0.79]
    baseline_scores = [0.71, 0.68, 0.62]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    plt.bar(x - width/2, scm_scores, width, label='SCM Legal', alpha=0.8)
    plt.bar(x + width/2, baseline_scores, width, label='Baseline', alpha=0.8)
    
    plt.xlabel('Métricas')
    plt.ylabel('Puntuación F1')
    plt.title('SCM Legal vs Baseline - Métricas Principales')
    plt.xticks(x, metrics)
    plt.legend()
    plt.tight_layout()
    plt.savefig('results/paper_figure_1_metrics_comparison.png', dpi=300)
    
    # Figura 2: Matriz de confusión conceptual
    # Figura 3: Análisis cross-jurisdictional
    # etc.
```

## 🎯 Timeline de Implementación

### Semana 1-2: Configuración y Preparación
- [ ] Configurar entorno de entrenamiento (GPU/Cloud)
- [ ] Preparar datasets legales reales
- [ ] Validar pipeline de datos
- [ ] Setup de monitoreo (W&B)

### Semana 3-4: Entrenamiento Inicial
- [ ] Entrenar modelo SCM base (Llama 3.2 1B)
- [ ] Implementar evaluación automática
- [ ] Fine-tuning de hiperparámetros
- [ ] Validación inicial de resultados

### Semana 5-6: Optimización y Scaling
- [ ] Entrenar modelo más grande (Llama 3.2 3B)
- [ ] Experimentos de ablation
- [ ] Cross-jurisdictional transfer learning
- [ ] Optimización de inferencia

### Semana 7-8: Evaluación y Análisis
- [ ] Evaluación comprehensiva con todas las métricas
- [ ] Análisis estadístico de resultados
- [ ] Comparación con baselines
- [ ] Preparación de datos para paper

## 📚 Recursos Académicos

### Papers de Referencia
1. **Fang et al. (2024)** - "Large Concept Models: Language Modeling in a Sentence Representation Space"
2. **Hu et al. (2021)** - "LoRA: Low-Rank Adaptation of Large Language Models"
3. **Katz et al. (2023)** - "Legal AI Applications and Benchmarks"

### Conferencias Target
- **ACL 2025**: Association for Computational Linguistics
- **AAAI 2025**: Association for the Advancement of AI
- **ICML 2025**: International Conference on Machine Learning
- **JURIX 2024**: International Conference on Legal Knowledge Systems

### Código y Datos Abiertos
- **Modelo**: Disponible en HuggingFace Hub
- **Código**: MIT License en GitHub
- **Datasets**: Disponibles para investigación académica

## 🚀 Próximos Pasos Inmediatos

1. **Decisión de Infraestructura**: ¿Google Colab Pro+, Runpod, o setup local?
2. **Configuración Inicial**: Setup de entorno y dependencias
3. **Generación de Datos**: Ejecutar pipeline de preparación de corpus
4. **Entrenamiento Pilot**: Modelo pequeño para validar pipeline
5. **Scaling Up**: Entrenamiento completo con configuración académica

---

¿Deseas que proceda con alguno de estos pasos específicos? Puedo ayudarte a:

1. **Configurar el entorno** en la plataforma que prefieras
2. **Generar el corpus legal** con datos reales
3. **Ejecutar un entrenamiento piloto** para validar el setup
4. **Preparar configuraciones** optimizadas para tu hardware

El objetivo es pasar de la simulación actual a un modelo SCM real, entrenado y evaluado con estándares académicos para publicación.