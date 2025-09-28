# Small Concept Models for Multi-Jurisdictional Legal AI: A Crisis Response to Academic Data Restrictions

**Authors**: Ignacio Adrian Lerer¹  
¹Director Independiente & Consultor Ejecutivo en Gobierno Corporativo, Buenos Aires, Argentina

## Abstract

This paper introduces Small Concept Models (SCM), a novel adaptation of Meta's Large Concept Models for specialized legal applications in multi-jurisdictional environments. In response to the crisis caused by OpenAlex abstract restrictions limiting AI training data access, we developed an emergency response framework that prioritizes Open Access (OA) sources while maintaining world-class performance for legal concept understanding across Argentina, Spain, Chile, and Uruguay jurisdictions. Our SCM approach achieves comparable legal concept accuracy to larger models while requiring significantly fewer computational resources and training data. The implementation demonstrates resilient AI development strategies that can adapt to academic data scarcity while preserving research continuity and innovation capacity.

**Keywords**: Small Language Models, Legal AI, Multi-Jurisdictional Analysis, Crisis Response, Open Access, LoRA Fine-tuning

## 1. Introduction

The recent restriction of abstract access in OpenAlex, affecting major publishers like Elsevier (~22.5% availability) and Springer (~35.8% availability), has created an unprecedented crisis for AI research development. This restriction threatens the foundation of academic AI systems that depend on comprehensive access to scientific literature for training and validation.

In this context, we present Small Concept Models (SCM) - a specialized adaptation of large language models optimized for domain-specific understanding with minimal data requirements. Our case study focuses on multi-jurisdictional legal AI for Spanish-speaking countries, demonstrating how targeted fine-tuning can achieve professional-grade performance even under data scarcity conditions.

### 1.1 Research Objectives

1. **Crisis Response**: Develop robust AI systems resilient to academic data restrictions
2. **Domain Specialization**: Create legal AI capable of multi-jurisdictional analysis
3. **Resource Efficiency**: Achieve professional performance with minimal computational requirements
4. **Open Access Strategy**: Establish OA-first development methodology

### 1.2 Contributions

- Novel SCM architecture for legal domain specialization
- Crisis mitigation framework for academic data restrictions
- Multi-jurisdictional legal AI system for AR/ES/CL/UY
- OA-first training methodology with emergency harvesting protocols
- Production-ready deployment architecture using Cloudflare Workers

## 2. Related Work

### 2.1 Large Concept Models

Meta's Large Concept Models represent a significant advancement in conceptual understanding, focusing on abstract reasoning rather than mere pattern matching. However, their computational requirements and data dependencies make them unsuitable for crisis scenarios and specialized domains.

### 2.2 Small Language Models

Recent work on small language models has demonstrated that targeted fine-tuning can achieve domain-specific performance competitive with larger models. Our SCM approach extends this paradigm specifically for conceptual understanding in constrained environments.

### 2.3 Legal AI Systems

Existing legal AI systems typically focus on single jurisdictions or require extensive training corpora. Our multi-jurisdictional approach addresses the unique challenges of comparative legal analysis across civil law systems.

## 3. Methodology

### 3.1 SCM Architecture

Our SCM implementation builds upon Llama-2-7B-Chat with the following optimizations:

```
Base Model: meta-llama/Llama-2-7b-chat-hf
Fine-tuning: QLoRA 4-bit quantization
Target Modules: ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
LoRA Configuration:
  - Rank (r): 16
  - Alpha: 32
  - Dropout: 0.1
Training Parameters:
  - Batch Size: 4 (effective: 16 with gradient accumulation)
  - Learning Rate: 2e-4
  - Epochs: 3
  - Optimizer: paged_adamw_8bit
```

### 3.2 Crisis Response Framework

#### 3.2.1 Emergency Data Harvesting

In response to OpenAlex restrictions, we implemented an emergency harvesting protocol:

1. **Primary Sources**: OpenAlex API (returned 0 results due to restrictions)
2. **Fallback Sources**: arXiv, SciELO, LA Referencia
3. **Harvesting Results**: 50 legal papers from arXiv (2024)
4. **Quality Metrics**: Average abstract length 1,244 characters

#### 3.2.2 OA-First Strategy

Our Open Access-first methodology prioritizes:
- arXiv.org (computer science and interdisciplinary legal research)
- SciELO (Latin American academic publications)
- DOAJ (Directory of Open Access Journals)
- Institutional repositories with open access policies

### 3.3 Multi-Jurisdictional Training Design

#### 3.3.1 Jurisdiction Coverage

| Jurisdiction | Code | Legal System | Integration Source |
|-------------|------|--------------|-------------------|
| Argentina | AR | Civil Law | InfoLEG |
| Spain | ES | Civil Law | BOE (Boletín Oficial del Estado) |
| Chile | CL | Civil Law | LeyChile |
| Uruguay | UY | Civil Law | IMPO |

#### 3.3.2 Legal Concept Categories

Our training focuses on corporate law and compliance concepts:
- Corporate Governance (gobierno_corporativo)
- Compliance (compliance)
- Risk Management (gestion_riesgo)
- Financial Regulation (regulacion_financiera)
- Labor Law (derecho_laboral)
- Intellectual Property (propiedad_intelectual)
- Contracts (contratos)
- Civil Liability (responsabilidad_civil)

### 3.4 Training Data Preparation

#### 3.4.1 Conversation Format

We formatted legal documents as instruction-following conversations:

```
System: "Eres un experto en derecho corporativo y compliance con más de 30 años de experiencia en jurisdicciones de Argentina, España, Chile y Uruguay."

User: "Analiza los conceptos legales clave en el siguiente texto: [LEGAL_TEXT]"