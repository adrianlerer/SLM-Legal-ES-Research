# SCM Legal API Documentation

## 🚀 Overview

The SCM Legal API provides conceptual reasoning capabilities for legal document analysis through RESTful endpoints. The system processes legal documents at the concept level rather than token level, enabling superior coherence and domain-specific reasoning.

**Base URL**: `https://your-deployment.pages.dev` or `http://localhost:3000`

---

## 🔐 Authentication

Currently, the research prototype does not require authentication. For production deployment, implement appropriate API key validation:

```typescript
// Example header for future production use
headers: {
  'Authorization': 'Bearer your-api-key',
  'Content-Type': 'application/json'
}
```

---

## 📋 Endpoints

### **1. SCM Legal Analysis**

Performs comprehensive conceptual analysis of legal documents using the Small Concept Model approach.

```http
POST /api/scm/analyze
```

#### **Request Body**
```json
{
  "document": "string",           // Legal document text (min 100 chars)
  "query": "string",              // Specific analysis question
  "jurisdiction": "string",       // "AR" | "CL" | "UY" | "ES"
  "analysis_type": "string"       // See analysis types below
}
```

#### **Analysis Types**
- `"comprehensive"`: Full conceptual analysis (default)
- `"compliance"`: Focus on regulatory compliance
- `"risk_assessment"`: Risk identification and evaluation
- `"contract_review"`: Contract-specific analysis
- `"governance"`: Corporate governance evaluation

#### **Response**
```json
{
  "success": true,
  "scm_legal_analysis": {
    "model_info": {
      "type": "Small Concept Model (SCM)",
      "specialization": "Legal Domain", 
      "parameters": "250M (simulated)",
      "jurisdiction": "AR"
    },
    "conceptual_extraction": {
      "concepts_detected": 8,
      "concepts": [
        {
          "concept": {
            "id": "gc_001",
            "name": "Deber de Diligencia del Directorio",
            "category": "commercial",
            "subcategory": "governance_corporativo",
            "related_concepts": ["gc_002", "gc_003"],
            "keywords": ["directorio", "diligencia", "administradores"]
          },
          "confidence": 0.89,
          "text_match": "directorio",
          "contextual_relevance": 0.76
        }
      ]
    },
    "conceptual_reasoning": {
      "primary_concepts": ["gc_001", "compliance_001"],
      "conceptual_clusters": [
        {
          "cluster": "commercial_governance_corporativo",
          "concepts": ["gc_001", "gc_002", "gc_003"],
          "coherence": 0.87
        }
      ],
      "cross_references": [
        {
          "from": "gc_001",
          "to": "gc_002", 
          "relationship": "sibling",
          "strength": 0.82
        }
      ],
      "risk_indicators": [
        {
          "concept": "gc_001",
          "risk_type": "regulatory",
          "severity": "medium"
        }
      ],
      "reasoning_path": [
        "gc_001",
        "gc_001 -> gc_002 (sibling)"
      ]
    },
    "structured_response": {
      "summary": "Análisis conceptual completado...",
      "key_concepts": [
        {
          "name": "Deber de Diligencia del Directorio",
          "relevance": "commercial/governance_corporativo",
          "citation": "Concepto ID: gc_001 - Jurisdicciones: AR, CL, UY, ES"
        }
      ],
      "risk_assessment": {
        "overall_risk": "Medio",
        "specific_risks": ["regulatory (medium)"]
      },
      "recommendations": [
        "Revisar la documentación contractual específica...",
        "Considerar implementar controles de compliance preventivos"
      ],
      "cross_jurisdictional_notes": []
    },
    "performance_metrics": {
      "processing_time": "120ms",
      "conceptual_coherence": 0.87,
      "cross_reference_density": 1.5
    }
  }
}
```

#### **Error Responses**
```json
{
  "error": "Documento muy corto para análisis conceptual (mínimo 100 caracteres)"
}
```

**Status Codes**: `400` (Bad Request), `500` (Internal Server Error)

---

### **2. SCM vs LLM Comparison**

Compares SCM conceptual approach against traditional LLM token-based processing.

```http
POST /api/scm/compare
```

#### **Request Body**
```json
{
  "document": "string",     // Legal document text
  "query": "string",        // Analysis question
  "jurisdiction": "string"  // Optional, defaults to "AR"
}
```

#### **Response**
```json
{
  "success": true,
  "document_analysis": {
    // Full SCM analysis (same as /api/scm/analyze)
  },
  "performance_comparison": {
    "scm_legal": {
      "approach": "Conceptual reasoning on legal ontology",
      "concepts_identified": 8,
      "conceptual_coherence": 0.87,
      "domain_specialization": 95,
      "cross_references": 6,
      "jurisdiction_awareness": "Native multi-jurisdictional",
      "risk_indicators": 3,
      "memory_footprint": "~300MB",
      "latency": "<200ms",
      "deployment": "Cloudflare Workers compatible"
    },
    "traditional_llm": {
      "approach": "Token-by-token text generation",
      "tokens_processed": 1250,
      "conceptual_coherence": 0.72,
      "domain_specialization": 60,
      "cross_references": 0,
      "jurisdiction_awareness": "Limited, requires prompting",
      "risk_indicators": 0,
      "memory_footprint": "~2-14GB", 
      "latency": ">500ms",
      "deployment": "Requires GPU infrastructure"
    },
    "scm_advantages": [
      "Razonamiento conceptual especializado en dominio jurídico",
      "Ontología legal estructurada con cross-references",
      "Detección automática de riesgos y compliance",
      "Deployment eficiente en edge computing",
      "Trazabilidad completa del razonamiento",
      "Adaptación nativa multi-jurisdiccional"
    ],
    "implementation_feasibility": {
      "technical": "Altamente viable con tecnologías actuales",
      "economic": "ROI positivo dentro de 6-12 meses",
      "timeline": "4-6 semanas para prototipo funcional",
      "scalability": "Horizontal via Cloudflare Edge Network"
    }
  },
  "recommendation": "SCM Legal ofrece ventajas significativas para casos de uso jurídicos específicos con viabilidad técnica superior a LCMs generales"
}
```

---

## 🧠 Legal Concept Ontology

### **Available Concept Categories**

#### **1. Governance Corporativo (`governance_corporativo`)**
- `gc_001`: Deber de Diligencia del Directorio
- `gc_002`: Deber de Lealtad  
- `gc_003`: Comité de Auditoría

#### **2. Compliance (`compliance`)**
- `compliance_001`: Programa de Integridad
- `compliance_002`: Due Diligence Corporativo

#### **3. Gestión de Riesgos (`gestion_riesgo`)**
- `risk_001`: Riesgo Operacional
- `risk_002`: Riesgo Reputacional

#### **4. Contratos (`contratos`)**
- `contract_001`: Cláusula de Indemnidad
- `contract_002`: Garantía de Cumplimiento

### **Concept Relationships**
- `sibling`: Same category and subcategory
- `cousin`: Same category, different subcategory  
- `regulatory_compliance`: Cross-domain compliance relationship
- `cross_domain`: General cross-category relationship

---

## 🌍 Multi-Jurisdictional Support

### **Supported Jurisdictions**
- **`AR`**: Argentina (CCyC, LSC, CNV, BCRA normativa)
- **`CL`**: Chile (Código Civil, Ley Sociedades Anónimas)
- **`UY`**: Uruguay (Código Civil, normativa BROU/BSE)  
- **`ES`**: España (planned - Código Civil, LSC, CNMV)

### **Jurisdiction-Specific Features**
- Concept availability varies by jurisdiction
- Legal keywords adapted to local terminology
- Cross-jurisdictional analysis for multinational compliance

---

## 📊 Performance Metrics

### **Conceptual Coherence Score (CCS)**
- **Range**: 0.0 - 1.0
- **Interpretation**: Higher values indicate better conceptual consistency
- **Benchmark**: >0.8 considered excellent for legal domain

### **Cross-Reference Density (CRD)**  
- **Formula**: Number of cross-references / Number of concepts
- **Range**: 0.0 - ∞
- **Interpretation**: Higher density indicates richer conceptual connectivity

### **Processing Time**
- **Target**: <200ms for real-time professional workflows
- **Factors**: Document length, complexity, analysis type
- **Optimization**: Edge deployment for minimal latency

---

## 🛡️ Risk Assessment

### **Risk Types**
- **`operational`**: Process and system risks
- **`regulatory`**: Compliance and legal risks
- **`reputational`**: Image and stakeholder risks
- **`compliance`**: Specific compliance violations

### **Severity Levels**
- **`low`**: Minor issues, routine monitoring
- **`medium`**: Moderate attention required  
- **`high`**: Immediate action recommended

---

## 🔍 Usage Examples

### **Contract Risk Analysis**
```bash
curl -X POST http://localhost:3000/api/scm/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "document": "CONTRATO DE PRESTACIÓN DE SERVICIOS... [contract text]",
    "query": "¿Qué riesgos contractuales identifica en este documento?",
    "jurisdiction": "AR",
    "analysis_type": "risk_assessment"
  }'
```

### **Governance Evaluation**
```bash
curl -X POST http://localhost:3000/api/scm/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "document": "ACTA DE DIRECTORIO... [board minutes text]",
    "query": "Evalúe las decisiones de governance corporativo",
    "jurisdiction": "AR", 
    "analysis_type": "governance"
  }'
```

### **Comparative Analysis**
```bash
curl -X POST http://localhost:3000/api/scm/compare \
  -H "Content-Type: application/json" \
  -d '{
    "document": "Legal document text for comparison...",
    "query": "Compare conceptual vs traditional analysis approaches"
  }'
```

---

## ⚠️ Limitations and Disclaimers

### **Current Implementation**
- **Research Prototype**: Simulated SCM reasoning using heuristics
- **Limited Ontology**: 15+ concepts vs. thousands needed for production
- **Simulated Metrics**: Performance indicators are projected, not measured
- **No Real ML Model**: Uses rule-based classification, not trained model

### **Legal Disclaimers**
- **Not Legal Advice**: Outputs are for research purposes only
- **Professional Review Required**: Always consult qualified legal counsel
- **No Liability**: Authors disclaim responsibility for decisions based on outputs
- **Experimental Status**: Technology under active research and development

### **Future Production Features**
- Real fine-tuned models (Llama 3.2 1B/3B base)
- Expanded legal ontology (500+ concepts)
- True conceptual embeddings (SONAR-style)
- Professional validation and certification

---

## 📞 Support and Contributing

### **Research Collaboration**
- **Issues**: Report bugs or feature requests via GitHub Issues
- **Pull Requests**: Contribute improvements with detailed descriptions
- **Academic Use**: Cite repository if used in research publications

### **Contact Information**
- **Repository**: https://github.com/adrianlerer/SLM-Legal-Spanish
- **Author**: Ignacio Adrian Lerer (Senior Corporate Lawyer)
- **Research Focus**: LCM to SCM adaptation for legal domain specialization

---

*This API documentation reflects the current research prototype. Production deployment will include authentication, rate limiting, and enhanced error handling.*