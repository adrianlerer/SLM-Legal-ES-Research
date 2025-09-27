#!/usr/bin/env python3
"""
SCM Legal Training Script - Main entry point for training
Academic research implementation for paper publication

This script orchestrates the complete SCM Legal training pipeline:
1. Data preparation and corpus building
2. Model fine-tuning with LoRA/QLoRA 
3. Evaluation and benchmarking
4. Model deployment and optimization

Usage:
    python train_scm_legal.py --config config/scm_training_config.yaml --mode [prepare|train|evaluate|all]
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import yaml
from omegaconf import OmegaConf
import torch
import wandb
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Custom imports
from data_preparation import LegalCorpusBuilder
from scm_trainer import SCMLegalTrainer
from evaluation_metrics import LegalEvaluationMetrics, ConceptEvaluationSample

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SCMLegalPipeline:
    """
    Complete SCM Legal training and evaluation pipeline
    """
    
    def __init__(self, config_path: str):
        self.config = OmegaConf.load(config_path)
        self.setup_directories()
        self.setup_logging()
        
    def setup_directories(self):
        """Create necessary directories"""
        
        directories = [
            self.config.dataset.get('output_dir', 'data'),
            self.config.training.output_dir,
            'logs',
            'results',
            'checkpoints'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def setup_logging(self):
        """Setup logging and experiment tracking"""
        
        # File logging
        log_file = f"logs/scm_legal_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        # Weights & Biases setup
        if self.config.logging.use_wandb:
            wandb.init(
                project=self.config.logging.wandb_project,
                name=self.config.logging.experiment_name,
                config=OmegaConf.to_yaml(self.config),
                tags=['scm-legal', 'concept-reasoning', 'multi-jurisdictional']
            )
            
    def prepare_data(self):
        """Prepare legal corpus for training"""
        
        logger.info("Starting data preparation phase...")
        
        # Data preparation configuration
        data_config = {
            'output_dir': self.config.dataset.get('output_dir', 'data'),
            'data_augmentation': {
                'enable': True,
                'enable_paraphrasing': True,
                'enable_concept_substitution': True,
                'enable_cross_jurisdictional': True,
                'augmentation_ratio': 0.2
            },
            'quality_criteria': {
                'min_confidence': 0.5,
                'min_concepts': 1,
                'min_text_length': 50,
                'max_text_length': self.config.dataset.max_length
            }
        }
        
        # Initialize corpus builder
        corpus_builder = LegalCorpusBuilder(data_config)
        
        # Build corpus
        train_samples, val_samples, test_samples = corpus_builder.build_corpus()
        
        logger.info(f"Data preparation completed:")
        logger.info(f"  Train samples: {len(train_samples)}")
        logger.info(f"  Validation samples: {len(val_samples)}")  
        logger.info(f"  Test samples: {len(test_samples)}")
        
        # Log to wandb
        if self.config.logging.use_wandb:
            wandb.log({
                'data_prep/train_samples': len(train_samples),
                'data_prep/val_samples': len(val_samples),
                'data_prep/test_samples': len(test_samples),
                'data_prep/total_samples': len(train_samples) + len(val_samples) + len(test_samples)
            })
        
        return train_samples, val_samples, test_samples
        
    def train_model(self):
        """Train SCM Legal model"""
        
        logger.info("Starting model training phase...")
        
        # Initialize trainer
        trainer = SCMLegalTrainer(self.config)
        
        # Train model
        training_results = trainer.train()
        
        logger.info("Model training completed")
        logger.info(f"Training results: {training_results}")
        
        # Log results to wandb
        if self.config.logging.use_wandb:
            wandb.log({
                'training/final_loss': training_results.get('eval_loss', 0),
                'training/training_time': training_results.get('train_runtime', 0),
                'training/final_perplexity': training_results.get('eval_perplexity', 0)
            })
            
        return training_results
        
    def evaluate_model(self):
        """Comprehensive model evaluation"""
        
        logger.info("Starting model evaluation phase...")
        
        # Initialize evaluator
        evaluator = LegalEvaluationMetrics(self.config.evaluation)
        
        # Load test data (in real implementation, load from saved files)
        test_samples = self._load_evaluation_samples()
        
        # Run comprehensive evaluation
        evaluation_results = evaluator.evaluate_comprehensive(test_samples)
        
        # Log results
        self._log_evaluation_results(evaluation_results)
        
        # Save detailed results
        self._save_evaluation_results(evaluation_results)
        
        return evaluation_results
        
    def _load_evaluation_samples(self) -> list:
        """Load evaluation samples - placeholder implementation"""
        
        # In real implementation, this would load from the test dataset
        # For now, return empty list - this would be populated with actual predictions
        
        logger.warning("Using placeholder evaluation samples - implement real evaluation data loading")
        
        return []
        
    def _log_evaluation_results(self, results: dict):
        """Log evaluation results to console and wandb"""
        
        logger.info("Evaluation Results:")
        logger.info("=" * 50)
        
        for metric_name, result in results.items():
            logger.info(f"{result.metric_name}: {result.score:.3f}")
            
            if self.config.logging.use_wandb:
                wandb.log({f"evaluation/{metric_name}": result.score})
                
                # Log confidence intervals if available
                if result.confidence_interval:
                    ci_low, ci_high = result.confidence_interval
                    wandb.log({
                        f"evaluation/{metric_name}_ci_low": ci_low,
                        f"evaluation/{metric_name}_ci_high": ci_high
                    })
        
        # Overall score
        if 'overall_score' in results:
            overall = results['overall_score']
            logger.info(f"\nOverall SCM Legal Score: {overall.score:.3f}")
            
            if self.config.logging.use_wandb:
                wandb.log({"evaluation/overall_score": overall.score})
                
    def _save_evaluation_results(self, results: dict):
        """Save detailed evaluation results"""
        
        results_file = f"results/scm_legal_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert results to serializable format
        serializable_results = {}
        
        for metric_name, result in results.items():
            serializable_results[metric_name] = {
                'metric_name': result.metric_name,
                'score': result.score,
                'confidence_interval': result.confidence_interval,
                'details': result.details
            }
            
        import json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Detailed evaluation results saved to {results_file}")
        
    def run_full_pipeline(self):
        """Run complete SCM Legal training pipeline"""
        
        logger.info("Starting complete SCM Legal training pipeline...")
        
        pipeline_start_time = datetime.now()
        
        try:
            # Phase 1: Data Preparation
            logger.info("Phase 1/3: Data Preparation")
            train_samples, val_samples, test_samples = self.prepare_data()
            
            # Phase 2: Model Training
            logger.info("Phase 2/3: Model Training")
            training_results = self.train_model()
            
            # Phase 3: Model Evaluation
            logger.info("Phase 3/3: Model Evaluation")
            evaluation_results = self.evaluate_model()
            
            # Pipeline completion
            pipeline_end_time = datetime.now()
            pipeline_duration = pipeline_end_time - pipeline_start_time
            
            logger.info("SCM Legal training pipeline completed successfully!")
            logger.info(f"Total pipeline duration: {pipeline_duration}")
            
            # Final summary
            self._generate_final_report(training_results, evaluation_results, pipeline_duration)
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
            
            if self.config.logging.use_wandb:
                wandb.log({"pipeline/status": "failed", "pipeline/error": str(e)})
                
            raise
            
        finally:
            if self.config.logging.use_wandb:
                wandb.finish()
                
    def _generate_final_report(self, training_results: dict, evaluation_results: dict, duration):
        """Generate final training report"""
        
        report_file = f"results/scm_legal_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_content = f"""# SCM Legal Training Report
        
## Training Configuration
- Model: {self.config.model.base_model}
- Training epochs: {self.config.training.num_train_epochs}
- Learning rate: {self.config.training.learning_rate}
- LoRA rank: {self.config.lora.r}

## Training Results
- Final loss: {training_results.get('eval_loss', 'N/A')}
- Training time: {training_results.get('train_runtime', 'N/A')} seconds
- Total training steps: {training_results.get('train_steps', 'N/A')}

## Evaluation Results
"""
        
        for metric_name, result in evaluation_results.items():
            report_content += f"- {result.metric_name}: {result.score:.3f}\n"
            
        report_content += f"""
## Pipeline Summary
- Total duration: {duration}
- Status: Completed successfully
- Timestamp: {datetime.now().isoformat()}

## Next Steps for Academic Publication
1. **Model Validation**: Conduct additional validation with legal experts
2. **Benchmarking**: Compare with existing legal AI models
3. **Statistical Analysis**: Perform significance testing on results
4. **Paper Writing**: Document methodology and results for publication
5. **Code Release**: Prepare code and data for open source release
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.info(f"Final report generated: {report_file}")

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="SCM Legal Training Pipeline")
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/scm_training_config.yaml',
        help='Path to training configuration file'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['prepare', 'train', 'evaluate', 'all'],
        default='all',
        help='Pipeline mode to run'
    )
    
    parser.add_argument(
        '--gpu',
        type=str,
        default='auto',
        help='GPU device to use (auto, 0, 1, etc.)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Set GPU device
    if args.gpu != 'auto':
        os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
        
    # Check for configuration file
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
        
    # Initialize pipeline
    pipeline = SCMLegalPipeline(args.config)
    
    # Run selected mode
    try:
        if args.mode == 'prepare':
            pipeline.prepare_data()
        elif args.mode == 'train':
            pipeline.train_model()
        elif args.mode == 'evaluate':
            pipeline.evaluate_model()
        elif args.mode == 'all':
            pipeline.run_full_pipeline()
            
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()