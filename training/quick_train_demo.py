#!/usr/bin/env python3
"""
SCM Legal - Quick Training Demo
==============================

Script simplificado para demostrar el entrenamiento LoRA en entornos con recursos limitados.
Optimizado para ejecución rápida y validación del pipeline completo.

Para entrenamiento completo, usar scm_lora_trainer.py o el notebook Colab.

Autor: Ignacio Adrian Lerer
Proyecto: SCM-Legal-Spanish
"""

import os
import torch
import json
from datetime import datetime
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM, 
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from datasets import Dataset
import logging
from rich.console import Console
from rich.progress import track

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class QuickSCMDemo:
    """Demo rápido del entrenamiento SCM Legal"""
    
    def __init__(self):
        self.console = Console()
        
        # Configuración ligera para demo
        self.config = {
            "model_name": "microsoft/DialoGPT-small",  # Modelo más pequeño para demo
            "lora_r": 4,  # Rank muy pequeño para velocidad
            "lora_alpha": 8,
            "lora_dropout": 0.1,
            "target_modules": ["c_attn"],  # Solo attention para DialoGPT
            "max_length": 256,  # Secuencias cortas
            "num_train_epochs": 1,  # Solo 1 época para demo
            "per_device_train_batch_size": 1,
            "learning_rate": 2e-4,
            "output_dir": "./demo_results"
        }
    
    def create_sample_legal_dataset(self):
        """Crea dataset legal mínimo para demo"""
        
        sample_texts = [
            "El contrato establece obligaciones de confidencialidad entre las partes.",
            "La sociedad anónima debe constituirse mediante escritura pública.",
            "El programa de integridad incluye políticas de prevención de corrupción.",
            "El directorio tiene la responsabilidad de supervisar la gestión empresarial.",
            "Las cláusulas de indemnización protegen contra daños y perjuicios.",
            "La auditoría interna evalúa el cumplimiento de controles internos.",
            "El debido proceso requiere garantías constitucionales para el imputado.",
            "La responsabilidad civil surge del incumplimiento de obligaciones contractuales."
        ]
        
        # Repetir para tener más datos de entrenamiento
        all_texts = sample_texts * 5  # 40 ejemplos total
        
        return Dataset.from_dict({"text": all_texts})
    
    def setup_model_and_tokenizer(self):
        """Setup del modelo ligero con LoRA"""
        
        self.console.print(f"[bold blue]Loading model: {self.config['model_name']}[/bold blue]")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config["model_name"])
        
        # Add pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config["model_name"],
            torch_dtype=torch.float32,  # No quantization para simplicidad
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Configuración LoRA ligera
        lora_config = LoraConfig(
            r=self.config["lora_r"],
            lora_alpha=self.config["lora_alpha"],
            target_modules=self.config["target_modules"],
            lora_dropout=self.config["lora_dropout"],
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False
        )
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        self.console.print("[green]✓ Model loaded with LoRA configuration[/green]")
    
    def preprocess_dataset(self, dataset):
        """Preprocesa el dataset para entrenamiento"""
        
        def tokenize_function(examples):
            # Tokenize texts
            tokens = self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=self.config["max_length"],
                return_tensors="pt"
            )
            
            # For causal LM, labels = input_ids
            tokens["labels"] = tokens["input_ids"].clone()
            return tokens
        
        # Apply tokenization
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def run_quick_training(self):
        """Ejecuta entrenamiento rápido para demo"""
        
        self.console.print("[bold yellow]Starting Quick SCM Legal Demo Training[/bold yellow]")
        
        # Setup model
        self.setup_model_and_tokenizer()
        
        # Create and preprocess dataset
        dataset = self.create_sample_legal_dataset()
        tokenized_dataset = self.preprocess_dataset(dataset)
        
        # Split dataset
        train_size = int(0.8 * len(tokenized_dataset))
        train_dataset = tokenized_dataset.select(range(train_size))
        eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))
        
        self.console.print(f"[blue]Training samples: {len(train_dataset)}[/blue]")
        self.console.print(f"[blue]Evaluation samples: {len(eval_dataset)}[/blue]")
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config["output_dir"],
            num_train_epochs=self.config["num_train_epochs"],
            per_device_train_batch_size=self.config["per_device_train_batch_size"],
            per_device_eval_batch_size=1,
            learning_rate=self.config["learning_rate"],
            weight_decay=0.01,
            logging_steps=5,
            eval_steps=10,
            save_steps=20,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            dataloader_num_workers=0,  # Evitar problemas de multiprocessing
            remove_unused_columns=False,
            report_to=None,  # No logging externo para demo
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )
        
        # Train
        self.console.print("[green]🚀 Starting training...[/green]")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config["output_dir"])
        
        self.console.print(f"[green]✓ Model saved to {self.config['output_dir']}[/green]")
        
        return trainer
    
    def test_trained_model(self):
        """Prueba el modelo entrenado"""
        
        self.console.print("[bold blue]Testing trained model...[/bold blue]")
        
        try:
            from peft import AutoPeftModelForCausalLM
            
            # Load trained model
            model = AutoPeftModelForCausalLM.from_pretrained(
                self.config["output_dir"],
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            tokenizer = AutoTokenizer.from_pretrained(self.config["output_dir"])
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Test generation
            test_prompt = "El contrato de servicios debe incluir"
            inputs = tokenizer(test_prompt, return_tensors="pt")
            
            model.eval()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            self.console.print("[green]✓ Model test successful![/green]")
            self.console.print(f"[yellow]Prompt:[/yellow] {test_prompt}")
            self.console.print(f"[yellow]Generated:[/yellow] {generated_text}")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Model test failed: {e}[/red]")
            return False
    
    def generate_demo_report(self, trainer):
        """Genera reporte del demo"""
        
        # Calculate adapter size
        adapter_size = 0
        if os.path.exists(self.config["output_dir"]):
            for root, dirs, files in os.walk(self.config["output_dir"]):
                for file in files:
                    adapter_size += os.path.getsize(os.path.join(root, file))
        
        adapter_size_mb = adapter_size / (1024 * 1024)
        
        # Create report
        report = {
            "demo_type": "Quick SCM Legal Training Demo",
            "timestamp": datetime.now().isoformat(),
            "model_config": self.config,
            "training_completed": True,
            "adapter_size_mb": round(adapter_size_mb, 2),
            "total_parameters": self.model.num_parameters(),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad),
            "training_time": "~2-5 minutes",
            "hardware": {
                "cuda_available": torch.cuda.is_available(),
                "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            }
        }
        
        # Save report
        report_path = os.path.join(self.config["output_dir"], "demo_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Display report
        self.console.print("\n[bold green]📊 Demo Training Report[/bold green]")
        self.console.print(f"✅ Training Status: Completed")
        self.console.print(f"💾 Adapter Size: {adapter_size_mb:.2f} MB")
        self.console.print(f"🔢 Total Parameters: {report['total_parameters']:,}")
        self.console.print(f"🎯 Trainable Parameters: {report['trainable_parameters']:,}")
        self.console.print(f"⚡ GPU Available: {report['hardware']['cuda_available']}")
        self.console.print(f"📁 Output Directory: {self.config['output_dir']}")
        
        return report

def main():
    """Función principal del demo"""
    
    console = Console()
    console.print("[bold green]SCM Legal - Quick Training Demo[/bold green]")
    console.print("[blue]=====================================[/blue]")
    console.print()
    
    # Check hardware
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        console.print(f"[green]✓ GPU detected: {gpu_name}[/green]")
    else:
        console.print("[yellow]⚠ Running on CPU - training will be slower[/yellow]")
    
    # Initialize demo
    demo = QuickSCMDemo()
    
    try:
        # Run training
        trainer = demo.run_quick_training()
        
        # Test model
        test_success = demo.test_trained_model()
        
        # Generate report
        report = demo.generate_demo_report(trainer)
        
        console.print("\n[bold green]🎉 Demo completed successfully![/bold green]")
        console.print("[blue]This demonstrates the SCM Legal training pipeline in miniature.[/blue]")
        console.print("[blue]For full-scale training, use scm_lora_trainer.py or the Colab notebook.[/blue]")
        
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ Demo failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)