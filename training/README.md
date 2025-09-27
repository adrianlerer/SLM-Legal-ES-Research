# SCM Legal Training Framework
## Small Concept Models for Legal Domain - Training Implementation

Esta carpeta contiene la implementación completa del framework de entrenamiento para SCM Legal, diseñado para la investigación académica y publicación de papers.

## 🚀 Visión General

El framework SCM Legal implementa **Small Concept Models** especializados para el dominio legal, con capacidades avanzadas de:

- **Razonamiento Conceptual**: Operaciones a nivel de concepto en lugar de tokens
- **Extracción de Conceptos Legales**: Identificación automática de conceptos jurídicos
- **Cadenas de Razonamiento**: Generación de inferencias legales multi-paso
- **Multi-jurisdiccional**: Soporte para Argentina, Chile, Uruguay y España
- **Evaluación Académica**: Métricas especializadas para investigación

## 📁 Estructura del Proyecto

```
training/
├── config/
│   └── scm_training_config.yaml      # Configuración completa del entrenamiento
├── data/                             # Datos generados automáticamente
│   ├── legal_corpus_train.jsonl      # Dataset de entrenamiento
│   ├── legal_corpus_validation.jsonl # Dataset de validación  
│   └── legal_corpus_test.jsonl       # Dataset de prueba
├── results/                          # Resultados de entrenamiento y evaluación
├── logs/                            # Logs de entrenamiento
├── checkpoints/                     # Checkpoints del modelo
├── concept_extractor.py             # Extractor de conceptos legales avanzado
├── concept_reasoner.py              # Motor de razonamiento conceptual
├── evaluation_metrics.py            # Métricas de evaluación especializadas
├── data_preparation.py              # Pipeline de preparación de datos
├── scm_trainer.py                   # Entrenador principal del modelo
├── train_scm_legal.py              # Script principal de entrenamiento
├── requirements-training.txt        # Dependencias para entrenamiento
└── README.md                       # Esta documentación
```

## 🔧 Instalación y Configuración

### Requisitos del Sistema

- **GPU**: NVIDIA GPU con al menos 8GB VRAM (16GB+ recomendado)
- **RAM**: Mínimo 16GB, recomendado 32GB+
- **Storage**: 50GB+ espacio libre
- **Python**: 3.8+ (recomendado 3.10)

### Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv scm_legal_env
source scm_legal_env/bin/activate  # Linux/Mac
# scm_legal_env\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements-training.txt

# Instalar modelos de SpaCy
python -m spacy download es_core_news_lg
python -m spacy download es_core_news_sm
```

### Configuración de Hugging Face

```bash
# Login a Hugging Face (para acceso a Llama 3.2)
huggingface-cli login
# Ingresa tu token de HF Hub
```

### Configuración de Weights & Biases (Opcional)

```bash
# Login a W&B para tracking de experimentos
wandb login
# Ingresa tu API key de W&B
```

## 🎯 Uso del Framework

### 1. Entrenamiento Completo (Recomendado)

```bash
# Ejecutar pipeline completo: preparación de datos + entrenamiento + evaluación
python train_scm_legal.py --config config/scm_training_config.yaml --mode all
```

### 2. Pasos Individuales

```bash
# Solo preparación de datos
python train_scm_legal.py --config config/scm_training_config.yaml --mode prepare

# Solo entrenamiento (requiere datos preparados)
python train_scm_legal.py --config config/scm_training_config.yaml --mode train

# Solo evaluación (requiere modelo entrenado)
python train_scm_legal.py --config config/scm_training_config.yaml --mode evaluate
```

### 3. Configuraciones Específicas

```bash
# Entrenamiento con GPU específica
python train_scm_legal.py --config config/scm_training_config.yaml --gpu 0

# Modo debug con logs detallados
python train_scm_legal.py --config config/scm_training_config.yaml --debug

# Configuración personalizada
python train_scm_legal.py --config config/my_custom_config.yaml --mode all
```

## 📊 Configuración del Entrenamiento

El archivo `config/scm_training_config.yaml` contiene todos los parámetros configurables:

### Modelo Base
- **Llama 3.2 1B/3B**: Modelos base optimizados para concepto-nivel
- **Quantización 4-bit**: Reducción de memoria con QLoRA
- **LoRA**: Fine-tuning eficiente con parámetros reducidos

### Datasets
- **Corpus Legal Multi-jurisdiccional**: Textos de Argentina, Chile, Uruguay, España
- **Anotación Automática**: Conceptos y cadenas de razonamiento
- **Augmentación de Datos**: Parafraseo y sustitución conceptual

### Evaluación
- **Métricas Académicas**: Precisión conceptual, coherencia de razonamiento
- **Consistencia Multi-jurisdiccional**: Evaluación cross-jurisdictional
- **Benchmarking**: Comparación con modelos tradicionales

## 🧠 Componentes Principales

### 1. Extractor de Conceptos Legales (`concept_extractor.py`)

```python
from concept_extractor import LegalConceptExtractor

# Inicializar extractor
extractor = LegalConceptExtractor(config)

# Extraer conceptos de texto legal
texto = "El contrato de compraventa requiere consentimiento válido..."
conceptos = extractor.extract_concepts(texto, jurisdiction='argentina')

for concepto in conceptos:
    print(f"Concepto: {concepto.concept_name}")
    print(f"Confianza: {concepto.confidence}")
```

### 2. Motor de Razonamiento (`concept_reasoner.py`)

```python
from concept_reasoner import ConceptualReasoningEngine, ReasoningType

# Inicializar motor de razonamiento
reasoner = ConceptualReasoningEngine(config)

# Realizar razonamiento deductivo
conceptos_iniciales = ['contrato_compraventa', 'vicios_consentimiento']
cadenas = reasoner.reason(
    initial_concepts=conceptos_iniciales,
    target_concept='contrato_nulo',
    jurisdiction='argentina',
    reasoning_type=ReasoningType.DEDUCTIVE
)

for cadena in cadenas:
    print(f"Conclusión: {cadena.final_conclusion}")
    print(f"Confianza: {cadena.overall_confidence}")
```

### 3. Evaluación Especializada (`evaluation_metrics.py`)

```python
from evaluation_metrics import LegalEvaluationMetrics

# Inicializar evaluador
evaluator = LegalEvaluationMetrics(config)

# Evaluar muestras predichas vs ground truth
resultados = evaluator.evaluate_comprehensive(samples)

print(f"F1 Extracción de Conceptos: {resultados['concept_extraction_f1'].score}")
print(f"Coherencia de Razonamiento: {resultados['legal_reasoning_coherence'].score}")
```

## 📈 Monitoreo y Resultados

### Weights & Biases Dashboard

Si tienes configurado W&B, puedes monitorear en tiempo real:

- **Métricas de Entrenamiento**: Loss, learning rate, gradient norms
- **Evaluación**: Precisión conceptual, coherencia de razonamiento
- **Recursos**: Uso de GPU/memoria, tiempo de entrenamiento
- **Comparaciones**: Múltiples experimentos y configuraciones

### Archivos de Resultados

Los resultados se guardan automáticamente en:

```
results/
├── scm_legal_evaluation_20241127_143022.json    # Resultados detallados
├── scm_legal_final_report_20241127_143500.md    # Reporte final
└── corpus_statistics.json                       # Estadísticas del corpus
```

### Logs de Entrenamiento

```
logs/
└── scm_legal_training_20241127_140000.log       # Log completo del proceso
```

## 🎓 Para Investigación Académica

### Configuraciones Recomendadas para Papers

```yaml
# config/academic_paper_config.yaml
model:
  base_model: "meta-llama/Llama-3.2-3B"  # Modelo más potente para resultados académicos
  
training:
  num_train_epochs: 5                     # Más épocas para convergencia
  per_device_train_batch_size: 2          # Batch size para resultados consistentes
  learning_rate: 1e-4                     # LR conservativo
  
evaluation:
  metrics: ["concept_extraction_f1", "legal_reasoning_coherence", 
           "jurisdictional_consistency", "domain_accuracy"]
           
logging:
  use_wandb: true                         # Tracking completo para paper
  experiment_name: "SCM-Legal-Academic-v1"
```

### Métricas Clave para Publicación

1. **Concept Extraction F1**: Precisión en identificación de conceptos legales
2. **Legal Reasoning Coherence**: Calidad del razonamiento jurídico generado
3. **Multi-jurisdictional Consistency**: Consistencia entre jurisdicciones
4. **Domain-specific Accuracy**: Precisión por área legal específica

### Benchmarking

El framework incluye comparación automática con:
- **Modelos base sin fine-tuning**
- **Modelos fine-tuned tradicionales** (token-level)
- **Modelos legales existentes**

## 🚀 Implementación de Producción

### Exportar Modelo Entrenado

```bash
# El modelo se guarda automáticamente en formato HuggingFace
# Ubicación: results/scm-legal-llama-3.2-1b/

# Para deployment, usar el modelo cuantizado
# Soporta ONNX, TensorRT, y formatos de edge computing
```

### Integración con Cloudflare Workers

El modelo entrenado puede integrarse con la aplicación web existente:

```typescript
// En src/routes/scm-legal.ts - reemplazar simulación con modelo real
const realModel = await loadSCMModel('path/to/trained/model');
const conceptos = await realModel.extractConcepts(texto);
const razonamiento = await realModel.reason(conceptos);
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Out of Memory (OOM)**
   ```bash
   # Reducir batch size en config
   per_device_train_batch_size: 1
   gradient_accumulation_steps: 16
   ```

2. **CUDA no disponible**
   ```bash
   # Verificar instalación de PyTorch con CUDA
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **Modelo Llama no accesible**
   ```bash
   # Verificar acceso a Llama 3.2 en HuggingFace
   huggingface-cli whoami
   ```

4. **Dependencias faltantes**
   ```bash
   # Reinstalar dependencias específicas
   pip install transformers>=4.35.0 peft>=0.7.0
   ```

### Logs de Debug

```bash
# Ejecutar con logs detallados
python train_scm_legal.py --debug --config config/scm_training_config.yaml
```

## 📚 Referencias Académicas

Este framework implementa conceptos de:

- **Large Concept Models (LCMs)**: Fang et al. (2024)
- **Legal AI Reasoning**: Katz et al. (2023) 
- **Multi-jurisdictional Legal NLP**: Various legal NLP research
- **Parameter-Efficient Fine-tuning**: Hu et al. (2021) - LoRA

## 🤝 Contribución

Para contribuir al proyecto académico:

1. Fork el repositorio
2. Crear branch para tu feature: `git checkout -b feature/nueva-metrica`
3. Commit cambios: `git commit -am 'Añadir nueva métrica de evaluación'`
4. Push al branch: `git push origin feature/nueva-metrica`
5. Crear Pull Request

## 📄 Licencia

Este código está disponible bajo licencia MIT para uso académico y de investigación.

---

## 🎯 Próximos Pasos

Una vez completado el entrenamiento, los siguientes pasos para la investigación académica:

1. **Validación Experta**: Validación de resultados con expertos legales
2. **Benchmarking Extenso**: Comparación con más modelos base
3. **Análisis Estadístico**: Pruebas de significancia estadística
4. **Redacción del Paper**: Documentación de metodología y resultados
5. **Código Abierto**: Preparación para release público

Para más información o asistencia, consultar la documentación principal del proyecto o contactar al equipo de investigación.