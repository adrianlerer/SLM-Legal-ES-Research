#!/usr/bin/env python3
"""
SCM Legal LoRA Trainer
======================

Implementación clase mundial de Small Concept Models (SCM) especializados 
para dominio legal usando LoRA (Low-Rank Adaptation).

Basado en:
- Paper: LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)
- Repo: https://github.com/microsoft/LoRA
- Hugging Face PEFT: https://github.com/huggingface/peft

Autor: Ignacio Adrian Lerer
Proyecto: SCM-Legal-Spanish para publicación académica
"""

import os
import json
import torch
import wandb
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from peft import (
    LoraConfig, 
    get_peft_model, 
    PeftModel, 
    TaskType,
    prepare_model_for_kbit_training
)
from datasets import Dataset, load_dataset
import bitsandbytes as bnb
from transformers import BitsAndBytesConfig
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
import yaml
from rich.console import Console
from rich.progress import Progress
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

@dataclass 
class SCMLegalConfig:
    """Configuración para entrenamiento SCM Legal con LoRA"""
    
    # Modelo base
    model_name: str = "meta-llama/Llama-3.2-1B"
    model_type: str = "llama"
    
    # Configuración LoRA (basada en paper Microsoft)
    lora_r: int = 8  # Rank - empezar con 8, optimal según paper
    lora_alpha: int = 16  # Scaling factor (típicamente 2*r)
    lora_dropout: float = 0.1
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "v_proj"  # Optimal según paper: aplicar a query y value
    ])
    
    # Quantización para eficiencia (QLoRA)
    load_in_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_use_double_quant: bool = True
    
    # Entrenamiento
    output_dir: str = "./results/scm-legal-llama-3.2-1b"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8  # Effective batch size = 8
    learning_rate: float = 2e-4  # Optimal para LoRA según paper
    weight_decay: float = 0.01
    max_length: int = 2048
    
    # Conceptos legales especializados
    legal_concepts: List[str] = field(default_factory=lambda: [
        "constitutional_law",
        "civil_law", 
        "commercial_law",
        "administrative_law",
        "labor_law",
        "compliance",
        "corporate_governance",
        "risk_management"
    ])
    
    # Jurisdicciones
    jurisdictions: List[str] = field(default_factory=lambda: [
        "argentina", "chile", "uruguay", "españa"
    ])
    
    # Logging
    use_wandb: bool = True
    wandb_project: str = "scm-legal-research"
    experiment_name: str = "llama-3.2-1b-legal-lora"

class LegalConceptExtractor:
    """Extractor de conceptos legales para dataset construction"""
    
    def __init__(self, config: SCMLegalConfig):
        self.config = config
        self.concept_keywords = {
            "constitutional_law": [
                "constitución", "derechos fundamentales", "supremacía constitucional",
                "control de constitucionalidad", "amparo", "habeas corpus"
            ],
            "civil_law": [
                "código civil", "contratos", "responsabilidad civil", "daños y perjuicios",
                "derecho de familia", "sucesiones", "propiedad", "obligaciones"
            ],
            "commercial_law": [
                "código de comercio", "sociedades comerciales", "quiebras", "concursos",
                "títulos valores", "contratos comerciales", "derecho empresarial"
            ],
            "administrative_law": [
                "acto administrativo", "procedimiento administrativo", "servicio público",
                "contratación pública", "responsabilidad del estado", "poder de policía"
            ],
            "labor_law": [
                "contrato de trabajo", "convenio colectivo", "sindicalismo",
                "seguridad social", "accidentes de trabajo", "despido", "salario"
            ],
            "compliance": [
                "cumplimiento normativo", "lavado de dinero", "anticorrupción",
                "debida diligencia", "riesgo regulatorio", "programa de integridad"
            ]
        }
    
    def extract_concepts_from_text(self, text: str) -> Dict[str, float]:
        """Extrae conceptos legales de un texto con scores de confianza"""
        text_lower = text.lower()
        concept_scores = {}
        
        for concept, keywords in self.concept_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1.0
            
            # Normalizar por número de keywords
            concept_scores[concept] = min(score / len(keywords), 1.0)
        
        return concept_scores

class SCMLegalTrainer:
    """Trainer principal para SCM Legal con LoRA"""
    
    def __init__(self, config: SCMLegalConfig):
        self.config = config
        self.console = Console()
        self.concept_extractor = LegalConceptExtractor(config)
        
        # Setup logging
        if config.use_wandb:
            wandb.init(
                project=config.wandb_project,
                name=config.experiment_name,
                config=config.__dict__
            )
    
    def setup_model_and_tokenizer(self):
        """Setup del modelo base con quantización y LoRA"""
        
        self.console.print(f"[bold blue]Loading model: {self.config.model_name}[/bold blue]")
        
        # Configuración de quantización (QLoRA)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=self.config.load_in_4bit,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
            bnb_4bit_quant_type="nf4"  # Optimal según paper QLoRA
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
            padding_side="right"  # Important para causal LM
        )
        
        # Add pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Configuración LoRA (basada en paper Microsoft)
        lora_config = LoraConfig(
            r=self.config.lora_r,  # Rank 8 es optimal según paper
            lora_alpha=self.config.lora_alpha,  # 2*r scaling
            target_modules=self.config.lora_target_modules,  # q_proj, v_proj optimal
            lora_dropout=self.config.lora_dropout,
            bias="none",  # No bias training inicialmente
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False
        )
        
        # Apply LoRA to model
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters (should be ~0.35M como en paper)
        self.model.print_trainable_parameters()
        
        self.console.print("[green]✓ Model and tokenizer loaded successfully[/green]")
    
    def create_legal_dataset(self, texts: List[str]) -> Dataset:
        """Crea dataset de entrenamiento con conceptos legales"""
        
        self.console.print("[bold blue]Processing legal corpus...[/bold blue]")
        
        processed_data = []
        
        with Progress() as progress:
            task = progress.add_task("[green]Processing texts...", total=len(texts))
            
            for text in texts:
                # Extract legal concepts
                concepts = self.concept_extractor.extract_concepts_from_text(text)
                
                # Tokenize text
                tokens = self.tokenizer(
                    text,
                    max_length=self.config.max_length,
                    truncation=True,
                    padding="max_length",
                    return_tensors="pt"
                )
                
                processed_data.append({
                    "input_ids": tokens["input_ids"].squeeze(),
                    "attention_mask": tokens["attention_mask"].squeeze(),
                    "labels": tokens["input_ids"].squeeze().clone(),  # For causal LM
                    "legal_concepts": concepts,
                    "text": text
                })
                
                progress.advance(task)
        
        self.console.print(f"[green]✓ Processed {len(processed_data)} legal texts[/green]")
        return Dataset.from_list(processed_data)
    
    def compute_metrics(self, eval_pred):
        """Métricas específicas para SCM Legal"""
        predictions, labels = eval_pred
        
        # Basic language modeling metrics
        shift_preds = predictions[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        
        # Calculate perplexity
        loss_fct = torch.nn.CrossEntropyLoss()
        shift_preds = shift_preds.view(-1, shift_preds.size(-1))
        shift_labels = shift_labels.view(-1)
        
        perplexity = torch.exp(loss_fct(shift_preds, shift_labels))
        
        return {
            "perplexity": perplexity.item(),
        }
    
    def train_concept_adapter(self, concept: str, training_data: List[str]):
        """Entrena un adapter LoRA para un concepto legal específico"""
        
        self.console.print(f"[bold yellow]Training adapter for concept: {concept}[/bold yellow]")
        
        # Filter data relevant to this concept
        concept_data = []
        for text in training_data:
            concepts = self.concept_extractor.extract_concepts_from_text(text)
            if concepts.get(concept, 0) > 0.3:  # Threshold for relevance
                concept_data.append(text)
        
        if len(concept_data) < 10:
            self.console.print(f"[red]Insufficient data for concept {concept}: {len(concept_data)} samples[/red]")
            return None
        
        # Create dataset
        dataset = self.create_legal_dataset(concept_data)
        train_size = int(0.8 * len(dataset))
        
        train_dataset = dataset.select(range(train_size))
        eval_dataset = dataset.select(range(train_size, len(dataset)))
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, not MLM
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=f"{self.config.output_dir}/{concept}",
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            logging_steps=10,
            eval_steps=100,
            save_steps=100,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=True,
            dataloader_num_workers=4,
            remove_unused_columns=False,
            report_to="wandb" if self.config.use_wandb else None,
            run_name=f"{self.config.experiment_name}-{concept}"
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train
        trainer.train()
        
        # Save adapter (only LoRA parameters - ~35MB according to paper)
        adapter_path = f"{self.config.output_dir}/{concept}/adapter"
        trainer.model.save_pretrained(adapter_path)
        
        self.console.print(f"[green]✓ Adapter saved for {concept}: {adapter_path}[/green]")
        
        return adapter_path
    
    def evaluate_concept_reasoning(self, concept: str, test_texts: List[str]) -> Dict[str, float]:
        """Evalúa capacidades de razonamiento conceptual"""
        
        self.console.print(f"[bold blue]Evaluating concept reasoning: {concept}[/bold blue]")
        
        # Load concept adapter
        adapter_path = f"{self.config.output_dir}/{concept}/adapter"
        if not os.path.exists(adapter_path):
            self.console.print(f"[red]Adapter not found for concept: {concept}[/red]")
            return {}
        
        # Load model with adapter
        model_with_adapter = PeftModel.from_pretrained(self.model, adapter_path)
        model_with_adapter.eval()
        
        results = []
        
        for text in test_texts:
            # Generate conceptual analysis
            inputs = self.tokenizer(
                f"Analiza los conceptos legales en el siguiente texto:\n{text}\nConceptos:",
                return_tensors="pt",
                max_length=1024,
                truncation=True
            )
            
            with torch.no_grad():
                outputs = model_with_adapter.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract concept accuracy (simplified evaluation)
            true_concepts = self.concept_extractor.extract_concepts_from_text(text)
            concept_mentioned = concept in generated.lower()
            concept_relevant = true_concepts.get(concept, 0) > 0.3
            
            if concept_relevant and concept_mentioned:
                accuracy = 1.0
            elif not concept_relevant and not concept_mentioned:
                accuracy = 1.0
            else:
                accuracy = 0.0
            
            results.append(accuracy)
        
        avg_accuracy = np.mean(results) if results else 0.0
        
        return {
            f"{concept}_accuracy": avg_accuracy,
            f"{concept}_samples": len(results)
        }
    
    def train_multi_concept_scm(self, legal_corpus: List[str]):
        """Entrena SCM completo con múltiples conceptos legales"""
        
        self.console.print("[bold green]Starting SCM Legal Training Pipeline[/bold green]")
        
        # Setup model and tokenizer
        self.setup_model_and_tokenizer()
        
        # Train concept-specific adapters
        adapter_paths = {}
        
        for concept in self.config.legal_concepts:
            adapter_path = self.train_concept_adapter(concept, legal_corpus)
            if adapter_path:
                adapter_paths[concept] = adapter_path
        
        # Evaluate multi-concept reasoning
        test_corpus = legal_corpus[-100:]  # Use last 100 for testing
        evaluation_results = {}
        
        for concept in adapter_paths.keys():
            concept_results = self.evaluate_concept_reasoning(concept, test_corpus)
            evaluation_results.update(concept_results)
        
        # Save final results
        results_path = f"{self.config.output_dir}/final_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                "adapter_paths": adapter_paths,
                "evaluation_results": evaluation_results,
                "config": self.config.__dict__
            }, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"[green]✓ SCM Legal training completed![/green]")
        self.console.print(f"[green]✓ Results saved: {results_path}[/green]")
        
        if self.config.use_wandb:
            wandb.log(evaluation_results)
            wandb.finish()
        
        return adapter_paths, evaluation_results

def load_sample_legal_corpus() -> List[str]:
    """Carga corpus legal de ejemplo para demostración"""
    
    # Textos legales de ejemplo (en producción, usar corpus real)
    sample_texts = [
        """
        El artículo 14 bis de la Constitución Nacional establece que el trabajo en sus diversas formas 
        gozará de la protección de las leyes, las que asegurarán al trabajador condiciones dignas y 
        equitativas de labor, jornada limitada, descanso y vacaciones pagados, retribución justa, 
        salario mínimo vital móvil, igual remuneración por igual tarea, participación en las ganancias 
        de las empresas, con control de la producción y colaboración en la dirección.
        """,
        """
        Las sociedades anónimas se constituyen por instrumento público o privado, y en este último caso 
        las firmas deben ser certificadas por escribano público. El estatuto debe contener las menciones 
        del artículo 11 y además la clase de acciones que se autoriza a emitir y, en su caso, las 
        limitaciones a su transmisibilidad.
        """,
        """
        Los programas de cumplimiento normativo (compliance) son herramientas esenciales para prevenir 
        y detectar violaciones a la legislación anticorrupción. Deben incluir la debida diligencia 
        sobre terceros, canales de denuncia, capacitación del personal y monitoreo continuo de riesgos.
        """,
        """
        El procedimiento administrativo se rige por los principios de debido proceso, economía procesal, 
        sencillez, eficacia, informalismo a favor del administrado, gratuidad y celeridad. Los actos 
        administrativos deben ser motivados, con expresión de los hechos y derecho aplicable.
        """
    ]
    
    # En implementación real, agregar más textos del corpus legal argentino/español
    return sample_texts * 25  # Duplicar para tener más datos de ejemplo

def main():
    """Función principal para entrenar SCM Legal"""
    
    # Load configuration
    config = SCMLegalConfig()
    
    # Initialize trainer
    trainer = SCMLegalTrainer(config)
    
    # Load legal corpus (en producción, cargar desde archivos/API)
    legal_corpus = load_sample_legal_corpus()
    
    console = Console()
    console.print(f"[bold blue]Starting SCM Legal Training with {len(legal_corpus)} texts[/bold blue]")
    
    # Train multi-concept SCM
    adapter_paths, results = trainer.train_multi_concept_scm(legal_corpus)
    
    console.print("[bold green]Training completed successfully![/bold green]")
    console.print(f"[green]Trained adapters: {list(adapter_paths.keys())}[/green]")
    console.print(f"[green]Evaluation results: {results}[/green]")

if __name__ == "__main__":
    main()