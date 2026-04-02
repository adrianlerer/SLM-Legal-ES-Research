# LLS SKaaS: Legal Skills as a Service

## Interpretable Legal AI Infrastructure for the LATAM Mid-Market

**Author:** Ignacio Adrián Lerer  
**Affiliation:** Lerer Legal Skills — Buenos Aires, Argentina  
**Contact:** adrian.lerer@slm-legal-spanish.com  
**Repository:** https://github.com/adrianlerer/SLM-Legal-ES-Research  
**Version:** 1.0 — April 2026  
**License:** CC-BY 4.0

---

## Abstract

We present **Lerer Legal Skills SKaaS** (Legal Skills as a Service), a production-deployed legal AI infrastructure designed for Argentine and LATAM law firms that cannot access enterprise-tier solutions such as Harvey AI. The system implements a hybrid architecture where a centralized inference server running quantized large language models (Qwen2.5-7B-Instruct-4bit) on Apple Silicon serves lightweight, cross-platform client tools. Key contributions include: (1) a deployed **Small Concept Model (SCM)** v2 pipeline that projects legal texts onto a fixed 24-dimensional space of Universal Legal Principles, returning structured scores with textual *evidence*, per-principle *confidence*, and automatic detection of *dialectical tensions* between principles; (2) semantic search over a 241,318-document corpus in **839ms** end-to-end; (3) **PII-isolation by design** — personally identifiable information is anonymized locally on the client device and never reaches the inference server; and (4) a multi-tenant architecture separating a shared LLS base corpus from per-client private corpora. We report empirical benchmarks on verified cases, discuss design decisions around temperature and dimensional reduction, and make limitations explicit in every API response. The system achieves full data sovereignty over sensitive legal documents while remaining economically accessible to the 15,000+ PyME-scale Argentine law firms currently underserved by existing solutions.

**Keywords:** legal AI, small concept model, interpretable AI, legal information retrieval, multi-tenant architecture, PII anonymization, Argentina, LATAM, LegalTech

---

## 1. Introduction

### 1.1 The Market Gap

The global legal AI market is experiencing rapid consolidation around enterprise-licensed, cloud-hosted platforms. Harvey AI, the current market leader for AI-assisted legal work, targets firms in the Am100 and Magic Circle at pricing exceeding \$50,000 per firm annually. This pricing structure effectively excludes **89% of the Argentine legal market**: the approximately 15,000 small-to-medium law firms employing between 2 and 50 attorneys that collectively handle the overwhelming majority of legal matters in the country.

Beyond cost, existing solutions present a second structural barrier: they are designed around Anglo-Saxon legal systems (US, UK). The Argentine legal framework — anchored in the *Código Civil y Comercial* (CCyC 2015) and *Ley General de Sociedades* 19.550, interpreted through *Corte Suprema de Justicia de la Nación* (CSJN) jurisprudence — requires domain-specific understanding that general-purpose legal AI tools do not provide.

A third barrier is **data sovereignty**. Argentine law firms handling sensitive commercial matters, M&A transactions, and family patrimony cases face significant professional and ethical constraints on transmitting client documents to foreign cloud infrastructure. No existing solution provides PII guarantees that satisfy the practical risk tolerance of Argentine legal practitioners.

### 1.2 Contributions of This Paper

This paper presents **LLS SKaaS** (*Lerer Legal Skills — Skills as a Service*), a production-deployed system that addresses all three barriers simultaneously. Our specific contributions are:

1. **A hybrid inference architecture** that centralizes computationally intensive AI operations on local Apple Silicon hardware (accessible to any Argentine attorney at Mac Mini M4 Pro price points) while serving lightweight cross-platform clients (Windows and macOS).

2. **SCM v2** — a second-generation Small Concept Model pipeline that maps legal texts onto 24 Universal Legal Principles while returning structured evidence citations, per-principle confidence scores, and automatic dialectical tension alerts.

3. **PII-isolation by design** — a client-side anonymization layer (Presidio, CPU-only, no ML models) that ensures personally identifiable information never leaves the client device before analysis.

4. **Empirical benchmarks** on a 241,318-document Argentine legal corpus, including semantic search latency (839ms), NER entity extraction, and SCM scoring verified against known legal cases.

5. **Explicit, machine-readable limitations** in every API response — a design decision responding to methodological critiques of AI systems operating in high-stakes professional contexts.

### 1.3 Paper Organization

Section 2 reviews related work. Section 3 describes the system architecture. Section 4 details the SCM v2 design and its empirical performance. Section 5 discusses the PII isolation mechanism. Section 6 presents the multi-tenant corpus model. Section 7 reports empirical benchmarks. Section 8 addresses limitations and methodological boundaries. Section 9 discusses future work, and Section 10 concludes.

---

## 2. Related Work

### 2.1 Large Language Models in Legal Practice

The application of large language models to legal tasks has progressed rapidly since the introduction of GPT-3 (Brown et al., 2020). CUAD (Hendrycks et al., 2021) established contract understanding as a benchmark task; subsequent work demonstrated that models fine-tuned on legal text outperform general-purpose LLMs on targeted legal NLP tasks (Chalkidis et al., 2020). However, these systems share a common limitation: their outputs are not directly interpretable in terms of legal concepts familiar to practicing attorneys.

Harvey AI (unreferenced — commercial system) addresses this by integrating large context-window models with proprietary legal document retrieval. Its architecture remains undisclosed. What is documented publicly is its pricing model and geographic focus, which together define the gap this work addresses.

### 2.2 Concept Bottleneck Models

Koh et al. (2020) introduced Concept Bottleneck Models (CBMs) as a mechanism for interpretable prediction: rather than mapping inputs directly to outputs, predictions flow through an intermediate layer of human-interpretable concepts. CBMs enable practitioners to intervene at the concept level, making the reasoning process auditable.

Our SCM adapts this approach to legal text: the "output" of a CBM trained on general tasks is replaced by a structured query to a large language model, constrained to produce scores over a fixed concept space (the 24 Universal Legal Principles). This avoids training a task-specific model from scratch while retaining the interpretability benefits of a concept bottleneck.

### 2.3 Legal Knowledge Bases and Retrieval

Legal question-answering systems have increasingly combined dense retrieval with generative models (Lewis et al., 2020). For Argentine law specifically, no publicly documented large-scale retrieval system exists. Our corpus of 241,318 documents indexed with pgvector/HNSW represents, to our knowledge, the largest publicly benchmarked Argentine legal retrieval corpus to date.

### 2.4 PII in Legal AI Systems

The intersection of PII protection and legal AI remains understudied. Existing work focuses primarily on de-identification of medical records (Stubbs et al., 2015). The particular requirements of legal practice — where PII includes not just personal names but also case numbers, entity structures, and financial terms — motivate a custom recognition approach. We build on Microsoft Presidio (open source) extended with Argentine-specific recognizers (CUIL, CUIT, DNI patterns).

---

## 3. System Architecture

### 3.1 Design Principles

The architecture is guided by four non-negotiable constraints:

1. **Data sovereignty**: client documents must not leave client infrastructure until PII-stripped
2. **Intellectual property protection**: inference logic resides on the Lerer server; clients receive results via API
3. **Cross-platform client**: clients may run Windows or macOS; no Apple Silicon required client-side
4. **Economic accessibility**: total infrastructure cost must be viable at PyME law firm scale

### 3.2 Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CLIENT LAYER (Windows/macOS)                               │
│  – Presidio anonymization (CPU-only, no ML models)          │
│  – sk_live_* license token                                  │
│  – MCP tools: lightweight wrappers over API calls           │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS — anonymized text + token
┌───────────────────────▼─────────────────────────────────────┐
│  INFERENCE SERVER (Apple Silicon — centralized)             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  License API (Supabase Edge Function / Deno)        │    │
│  │  – sk_live_* validation                             │    │
│  │  – Rate limiting, watermarking, audit log           │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Engine API (FastAPI / Python)                      │    │
│  │  POST /v1/ner   POST /v1/embed  POST /v1/search     │    │
│  │  POST /v1/scm   POST /v1/index                      │    │
│  └──────────────────────────┬──────────────────────────┘    │
│  ┌─────────────────────────▼──────────────────────────┐    │
│  │  oMLX — Local Inference (Apple Silicon MPS)         │    │
│  │  – Qwen2.5-7B-Instruct-4bit (NER, SCM)             │    │
│  │  – multilingual-e5-large (embeddings)               │    │
│  │  – Fallback: OpenAI API (cold start / dim mismatch) │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ PostgREST / pgvector
┌───────────────────────▼─────────────────────────────────────┐
│  SUPABASE / POSTGRESQL                                      │
│  – thoughts (241,318 docs, vector(1536), HNSW)             │
│  – client_<id> (per-firm private corpus)                    │
│  – tenants, licenses, audit_log, rate_limit_buckets         │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Inference Backend: oMLX

The inference server uses **oMLX** (https://github.com/adrianlerer/omlx), a local model runner optimized for Apple Silicon. At time of writing, the server runs:

- **Qwen2.5-7B-Instruct-4bit**: serves NER and SCM endpoints. 4-bit MLX quantization reduces memory footprint while maintaining sufficient inference quality for structured JSON extraction tasks.
- **multilingual-e5-large**: serves embedding generation for languages including Spanish. Produces 1024-dimensional vectors; when corpus compatibility requires 1536 dimensions (OpenAI text-embedding-3-small compatible), the system falls back to OpenAI API automatically.

**Fallback mechanism**: every inference path implements automatic fallback. If oMLX is unavailable or returns incompatible dimensions, the system transparently routes to OpenAI API (gpt-4o-mini for SCM/NER, text-embedding-3-small for embeddings). This ensures availability without requiring the client to handle backend transitions.

### 3.4 Licensing Infrastructure

License management is handled by an existing Supabase Edge Function (`license-api`) operating independently of the inference layer:

- Tokens follow the format `sk_live_<32 bytes entropy>`
- Validation includes: token hash lookup → rate limiting check → watermark generation → audit log write
- Revocation is instantaneous via `revoke_license.sh` (kill switch)
- Tenant provisioning via `create_tenant.sh` + `provision_license.sh`

The Engine API delegates all authentication to this pre-existing function; it does not re-implement license logic.

---

## 4. Small Concept Model v2

### 4.1 Motivation: Interpretability Over Accuracy-Only

The dominant criticism of AI in legal practice is the "black box" problem: when a system recommends a legal position or flags a contractual risk, practitioners cannot audit the reasoning chain. This is not merely a technical limitation — in many jurisdictions, attorney obligations of professional responsibility require that advice be grounded in articulable legal principles.

The SCM addresses this by making the *concept space explicit*. Rather than asking a model "is this contract risky?", we ask "score each of these 24 named legal principles for relevance to this text, and cite the specific text fragment that activates each score." The output is not a prediction but a structured map of how the input text relates to a declared conceptual framework.

### 4.2 The 24 Universal Legal Principles

The SCM's concept space consists of 24 principles derived from comparative constitutional and private law scholarship, selected to cover the intersection of Argentine domestic law (CCyC 2015, Ley 19.550, constitutional text) and international legal standards:

| # | Principle | Primary Branch |
|---|---|---|
| 1 | *Legalidad* (Legality) | Public Law |
| 2 | *Igualdad ante la ley* (Equality before the law) | Constitutional |
| 3 | *Proporcionalidad* (Proportionality) | Administrative / Criminal |
| 4 | *Razonabilidad* (Reasonableness) | Constitutional |
| 5 | *Debido proceso* (Due process) | Procedural |
| 6 | *Defensa en juicio* (Right to be heard) | Procedural |
| 7 | *Presunción de inocencia* (Presumption of innocence) | Criminal |
| 8 | *Non bis in idem* (Double jeopardy prohibition) | Criminal |
| 9 | *Irretroactividad* (Non-retroactivity) | Civil / Criminal |
| 10 | *Buena fe* (Good faith) | Civil / Commercial |
| 11 | *Autonomía de la voluntad* (Freedom of contract) | Contract |
| 12 | *Pacta sunt servanda* (Binding force of contracts) | Contract |
| 13 | *Rebus sic stantibus* (Changed circumstances) | Contract |
| 14 | *Enriquecimiento sin causa* (Unjust enrichment) | Civil |
| 15 | *Responsabilidad* (Liability) | Civil / Criminal |
| 16 | *Causalidad* (Causation) | Civil / Criminal |
| 17 | *Solidaridad* (Solidarity) | Labor / Social |
| 18 | *Subsidiariedad* (Subsidiarity) | Administrative |
| 19 | *Cosa juzgada* (Res judicata) | Procedural |
| 20 | *Seguridad jurídica* (Legal certainty) | Transversal |
| 21 | *Congruencia* (Congruence) | Procedural |
| 22 | *Motivación del acto* (Duty to give reasons) | Administrative |
| 23 | *Control judicial* (Judicial review) | Constitutional |
| 24 | *Transparencia* (Transparency) | Administrative |

**On dimensional reduction**: the compression of legal reasoning to 24 dimensions invites legitimate criticism. We address it directly: the 24-dimensional space is an *intentional* design choice that prioritizes interpretability over comprehensiveness. As with a 12-lead ECG — which reduces complex cardiac physiology to twelve measurements — the value lies not in capturing everything but in producing a structured, reproducible, comparable output that a practitioner can read and critique. The SCM does not decide cases; it orients practitioners.

### 4.3 SCM v2 Output Schema

SCM v2 extends the original scoring output with three new fields responding to methodological feedback:

```json
{
  "scores": {
    "<principle>": "<float 0.0–1.0>"
  },
  "top_principles": ["<top 5 by score>"],
  "details": {
    "<principle>": {
      "score":      "<float 0.0–1.0>",
      "confidence": "<float 0.0–1.0>",
      "evidence":   "<verbatim text fragment from input that activates this principle>"
    }
  },
  "tensions": [
    {
      "principles": ["<principle A>", "<principle B>"],
      "message": "<human-readable tension description requiring professional judgment>"
    }
  ],
  "low_confidence_flags": ["<principles with score > 0.3 but confidence < 0.3>"],
  "jurisdiction": "<e.g. Argentina/CCyC-2015>",
  "backend": "<e.g. oMLX:Qwen2.5-7B-Instruct-4bit>",
  "limitations": ["<array of explicit methodological caveats>"]
}
```

**Score scale**: 0.0 = not relevant; 0.3 = tangentially related; 0.7 = clearly applicable; 1.0 = central principle of the case.

**Confidence scale**: 0.0 = highly uncertain (ambiguous or insufficient text); 0.5 = moderate certainty; 1.0 = unambiguous in the input text.

### 4.4 Dialectical Tension Detection

Legal principles often operate in tension with one another. A contract unilaterally terminated by one party may simultaneously engage *Pacta sunt servanda* (contracts bind) and *Rebus sic stantibus* (changed circumstances may excuse non-performance). Failing to flag this tension would mislead a practitioner into treating a high score on one principle as dispositive.

SCM v2 monitors eight pre-defined dialectical pairs:

| Pair | Nature of tension |
|---|---|
| Autonomía de la voluntad ↔ Buena fe | Freedom to contract vs. limits of that freedom |
| Autonomía de la voluntad ↔ Rebus sic stantibus | Binding will vs. changed circumstances |
| Pacta sunt servanda ↔ Rebus sic stantibus | Contractual fidelity vs. equity in hardship |
| Seguridad jurídica ↔ Razonabilidad | Predictability vs. case-by-case fairness |
| Debido proceso ↔ Congruencia | Right to full hearing vs. procedural exactness |
| Legalidad ↔ Razonabilidad | Formal law vs. substantive reasonableness |
| Cosa juzgada ↔ Control judicial | Finality vs. judicial oversight |
| Subsidiariedad ↔ Control judicial | Administrative primacy vs. court access |

When both principles in a pair score above 0.55, a `TensionAlert` is appended to the response with a message directing the practitioner to apply casuistic professional judgment. The system takes no position on how the tension resolves — that is the attorney's function.

### 4.5 Temperature Design: Determinism by Choice

The SCM uses `temperature = 0.1`. This is a deliberate design decision, not a default.

Legal AI systems used for auditability require **reproducibility**: the same legal text must produce the same vector of principle scores across different analysts, different time periods, and different model calls. High temperature would introduce variance that undermines the system's core value proposition — providing a stable, comparable conceptual map that practitioners can discuss, contest, and build upon over time.

This contrasts with the appropriate use of higher temperature in **generative** legal tasks (drafting, brainstorming arguments), where creative variation is productive. The SCM is not a generative system; it is a structured classification system. Determinism is correct for classification.

---

## 5. PII Isolation by Design

### 5.1 The Problem

Argentine law firms routinely handle documents containing high-density PII: party names, DNI/CUIL/CUIT identifiers, addresses, financial account numbers, case numbers cross-referenceable to court records. Transmitting these to a third-party AI service creates professional liability exposure under *Ley 25.326* (Personal Data Protection) and risks violating attorney-client confidentiality.

The standard industry approach — relying on contractual representations from AI vendors — does not provide the practical risk protection that Argentine practitioners require.

### 5.2 The Architecture Solution

PII isolation is achieved architecturally, not contractually. The client-side tool (cross-platform, Windows-compatible) runs **Microsoft Presidio** locally before any network transmission:

1. Document arrives at the client tool
2. Presidio (CPU-only, no ML models required on client) detects and replaces PII with typed placeholders: `[PERSON_1]`, `[ORGANIZATION_1]`, `[CUIL_1]`, etc.
3. A session-keyed mapping `{placeholder → original value}` is stored exclusively on the client device
4. The anonymized text is transmitted to the LLS SKaaS API
5. Results return with placeholders; the client tool optionally re-substitutes original values for display

**The inference server never receives raw PII.** This guarantee holds structurally — it cannot be violated by a server-side configuration change or a future policy update.

Custom Presidio recognizers handle Argentine-specific identifiers: CUIL (11-digit labor ID), CUIT (taxpayer ID), DNI (national identity document), and Argentine corporate entity naming patterns (*S.A.*, *S.R.L.*, *S.A.S.*, etc.).

---

## 6. Multi-Tenant Corpus Architecture

### 6.1 Two-Corpus Model

The system maintains two distinct corpus namespaces per client interaction:

**LLS Base Corpus** (`thoughts` table): 241,318 documents comprising Argentine legal doctrine, statute text, CSJN jurisprudence, and commercial practice materials. Indexed with HNSW on `vector(1536)`. Shared across all clients; maintained and curated by Lerer Legal Skills.

**Client Corpus** (`client_<tenant_id>` tables): per-firm document corpus indexed with the same schema. Firms contribute their own anonymized documents; the resulting corpus captures institutional knowledge (precedent analyses, draft repositories, negotiation histories) proprietary to that firm. Client corpora are never accessible cross-tenant.

### 6.2 Vector Search Implementation

Semantic search uses the `match_thoughts` PostgreSQL function:

```sql
match_thoughts(
  query_embedding vector,
  match_threshold float,
  match_count     integer
) RETURNS TABLE (
  id         uuid,
  content    text,
  metadata   jsonb,
  similarity double precision
)
```

The HNSW index parameters (`m=16`, `ef_construction=64`) were selected to balance recall and query latency at the 241k document scale. At the current corpus size, this achieves sub-300ms database query time.

### 6.3 Embedding Compatibility

The base corpus was indexed with OpenAI `text-embedding-ada-002` / `text-embedding-3-small` (1536 dimensions). The oMLX `multilingual-e5-large` model produces 1024-dimensional embeddings, which are incompatible. The system resolves this automatically: when querying the base corpus, embedding generation falls back to OpenAI API, adding approximately 540ms but preserving dimensional compatibility. Client corpora may be indexed with either embedding model; if indexed with 1024-dim embeddings, they use a separate `match_client_<id>` function.

---

## 7. Empirical Results

### 7.1 Infrastructure Benchmarks

All measurements taken on the production server (Apple Silicon, M-series) under single-user load. Cold start refers to the first inference call after server restart (model loading into MPS memory). Warm refers to subsequent calls with the model cached.

| Operation | Latency | Notes |
|---|---|---|
| Health check | 3ms | — |
| Supabase connection | 140ms | Local Supabase CLI |
| oMLX connection | 660ms | Model list enumeration |
| **Semantic search (241k docs)** | **839ms** | Embedding: 540ms; DB: 299ms |
| NER extraction (~100 token input) | 31,515ms (cold) | Qwen2.5-7B first load to MPS |
| SCM scoring (6 principles) | ~28,400ms (cold) | Expected <8,000ms warm |

**On NER/SCM latency**: the 30-second cold-start latency reflects model initialization on MPS, not inferencing speed per se. In production deployment, the model remains resident in memory. Warm latency (model cached) is estimated at 6,000–8,000ms for a 100-token input on 7B parameters — consistent with published MLX inference benchmarks.

**Semantic search** is the most latency-critical operation for daily legal research workflows. At 839ms total (including a network round-trip to OpenAI for embedding generation), this is already within interactive-response territory for document retrieval.

### 7.2 SCM v2 Case Study: AySA v. Accell S.A. (2024)

**Input text:**
> *"La Resolución 3-2024 de AySA rescinde unilateralmente el contrato con Accell S.A. invocando causa de fuerza mayor sin haber dado audiencia previa al contratista ni motivado debidamente el acto administrativo."*

**Translation:** *"Resolution 3-2024 of AySA unilaterally terminates the contract with Accell S.A. invoking force majeure without having granted prior hearing to the contractor or adequately stating reasons for the administrative act."*

**Context:** Public service concession contract  
**Jurisdiction:** Argentina/CCyC-2015  
**Backend:** oMLX:Qwen2.5-7B-Instruct-4bit  
**Temperature:** 0.1

**Results:**

| Principle | Score | Confidence | Evidence (verbatim fragment) |
|---|---|---|---|
| *Motivación del acto* | **1.00** | 1.00 | "sin... motivado debidamente el acto administrativo" |
| *Defensa en juicio* | **0.70** | 1.00 | "sin haber dado audiencia previa al contratista" |
| *Pacta sunt servanda* | **0.70** | 1.00 | "rescinde unilateralmente el contrato" |
| *Buena fe* | 0.30 | 0.00 | *(no specific text fragment; low confidence flagged)* |
| *Autonomía de la voluntad* | 0.30 | 0.00 | *(low confidence)* |
| *Debido proceso* | 0.00 | 0.00 | — |

**Interpretation:** The model correctly identifies the administrative law dimension of the dispute: the core violations are the failure to give reasons for the administrative act (*Motivación del acto* = 1.0) and the failure to grant prior hearing (*Defensa en juicio* = 0.70). Both scores are supported by verbatim text evidence. *Pacta sunt servanda* registers the contractual dimension of the unilateral termination. The low-confidence scores on *Buena fe* and *Autonomía de la voluntad* correctly reflect that the text is insufficient to evaluate good faith — an invitation to the practitioner to investigate further.

No dialectical tensions were flagged, which is consistent with the legal analysis: this is not a *Pacta servanda* vs. *Rebus sic stantibus* dispute (the resolutory clause is an administrative act, not a contractual renegotiation).

### 7.3 NER Case Study

**Input:**
> *"El Dr. Carlos Méndez, representante de Accell S.A., firmó contrato con AySA en Buenos Aires el 15/03/2024."*

**Entities extracted:**

| Entity | Type | Confidence |
|---|---|---|
| Dr. Carlos Méndez | PERSON | 0.85 |
| Accell S.A. | ORGANIZATION | 0.85 |
| AySA | ORGANIZATION | 0.85 |
| Buenos Aires | LOCATION | 0.85 |
| 15/03/2024 | DATE_TIME | 0.85 |

5/5 entities correctly identified. Note that in PII-isolation mode (production), this call would receive already-anonymized text; NER is available as a standalone tool for corpus analysis workflows that do not involve client data.

---

## 8. Limitations and Methodological Boundaries

We structure this section around concerns raised in formal external evaluation. Rather than treating these as objections to be minimized, we adopt them as design inputs.

### 8.1 Dimensional Reduction and Informational Loss

**Concern:** Legal reasoning cannot be adequately compressed into 24 dimensions without significant informational loss.

**Our position:** This is correct — and is the intended trade-off. The SCM does not claim to *resolve* legal questions; it claims to *orient* practitioners toward applicable principles with traceable evidence. A 24-dimensional vector over named principles is auditable, comparable, and buildable-upon. A black-box probability over thousands of latent dimensions is not.

The 24 principles were selected to maximize coverage of Argentine private and public law's most frequently litigated conceptual intersections. Coverage gaps exist and are documented (see §8.4).

### 8.2 Determinism vs. Interpretive Flexibility

**Concern:** Law requires contextual interpretation; a deterministic system may rigidify analysis requiring casuistic weighing.

**Our position:** The SCM is not a decision system. It is a *structured reading aid*. The temperature-0.1 design ensures reproducibility of the conceptual map, not fixity of legal interpretation. Two attorneys reading the same SCM output are expected to weigh the principles differently given their professional judgment of the specific case.

The tension detection mechanism explicitly flags where principles require irresolvable weighing, directing practitioners *toward* professional judgment rather than away from it.

### 8.3 Formal Validation Against Expert Judgment

**Concern:** The system lacks formal benchmarking against analyses performed by licensed practitioners.

**Our honest response:** This is the most significant open item. The benchmarks reported in this paper are **infrastructure benchmarks** (latency, entity accuracy on clear cases, dimensional consistency) — not **legal accuracy benchmarks**. A formal evaluation study, with 50+ cases annotated independently by multiple licensed Argentine attorneys (inter-rater reliability reported as Cohen's κ), is planned as the next research milestone but is not reported here.

This paper makes an implementation claim, not a performance claim. We do not assert that SCM v2 matches or exceeds human expert accuracy on Argentine legal reasoning tasks.

### 8.4 Geographic and Temporal Corpus Bias

The base corpus (241,318 documents) covers primarily:
- Argentine civil and commercial law: CCyC 2015, Ley 19.550, CSJN jurisprudence (**high coverage**)
- Commercial contracts: M&A, leases, services (**high coverage**)
- International private law, non-Argentine LATAM jurisdictions (**low coverage**)
- Case law post-2024 (**not yet indexed**)

Every API response includes an explicit `jurisdiction` field and a machine-readable `limitations` array declaring these coverage boundaries. Corpus versioning (indexed timestamp per document) is implemented but not yet exposed via API — a planned extension.

### 8.5 Professional Responsibility

The system does not constitute legal advice. All outputs require expert review by the attorney of record. The attorney's professional responsibility to their client is unaffected by the use of AI assistance tools. This caveat appears in every API response's `limitations` array.

---

## 9. Future Work

The following extensions are planned:

1. **Formal validation study**: 50 cases with annotated ground truth from multiple licensed Argentine attorneys; inter-rater reliability and SCM agreement reported statistically.

2. **Corpus versioning API**: each analysis response will cite the corpus version (timestamp) used, enabling temporal reproducibility of analyses.

3. **Jurisdictional expansion**: Chile (Código Civil 1855), Uruguay (*Código General del Proceso*), Mexico (*Código Civil Federal*) — each requiring dedicated corpus development and principle weighting.

4. **Warm inference pipeline**: persistent model server reducing NER/SCM latency from ~30s (cold) to <8s (warm) for interactive usage.

5. **Role-specific interfaces** (three parallel tracks, 6-month roadmap):
   - **Senior attorney**: full SCM pipeline + evidence citations + semantic search for substantive legal analysis
   - **Compliance officer**: regulatory risk scoring + normative mapping (regulatory framework vs. internal policy gaps)
   - **Legal researcher**: jurisprudential trend analysis + principle evolution tracking across the corpus
   - *Junior attorney tooling is explicitly deprioritized in this phase* — the system is designed to augment expert judgment, not provide guardrails for inexperienced practitioners.

6. **Adversarial robustness**: evaluation of SCM scores under adversarial prompt injection and document manipulation.

---

## 10. Conclusion

LLS SKaaS demonstrates that economically accessible, interpretable legal AI infrastructure is technically feasible for the Argentine mid-market. The system's core design commitment — that every AI output must be traceable to a named legal principle, supported by verbatim textual evidence, and accompanied by explicit confidence and limitation disclosures — represents a substantive alternative to black-box AI assistance in high-stakes professional practice.

The tension between algorithmic determinism and interpretive flexibility is not resolved by the system; it is made legible. The SCM produces a structured map. The attorney reads the map, applies professional judgment, and takes responsibility. This is the correct division of labor between AI systems and legal professionals operating under obligations of professional responsibility.

We release the system specification, empirical benchmarks, and the 24-principle framework under CC-BY 4.0. The inference engine, multi-tenant schema, and client corpus remain proprietary to protect the institutional investment that makes sustainable deployment possible.

---

## References

Brown, T., et al. (2020). Language Models are Few-Shot Learners. *NeurIPS 2020*.

Chalkidis, I., et al. (2020). LEGAL-BERT: The Muppets straight out of Law School. *EMNLP 2020 Findings*.

Hendrycks, D., et al. (2021). CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review. *NeurIPS 2021*.

Koh, P.W., et al. (2020). Concept Bottleneck Models. *ICML 2020*.

Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS 2020*.

Peeperkorn, M., et al. (2024). Is Temperature the Creativity Parameter of Large Language Models? *arXiv:2405.00492*.

Stubbs, A., et al. (2015). Automated systems for the de-identification of longitudinal clinical narratives. *Journal of Biomedical Informatics*.

---

## Appendix A: API Endpoint Reference

| Method | Path | Description |
|---|---|---|
| GET | /health | Service health check |
| POST | /v1/ner | Named entity recognition (PERSON, ORG, LOCATION, DATE) |
| POST | /v1/embed | Text embedding generation |
| POST | /v1/search | Semantic search over base + client corpus |
| POST | /v1/scm | SCM v2 scoring with evidence, confidence, tensions |
| POST | /v1/index | Index documents into client corpus |

Full specification: `docs/scm_v2_spec.md` in companion repository.

## Appendix B: Benchmark Data

Machine-readable benchmark results: `docs/benchmark_results.json` in companion repository  
(https://github.com/adrianlerer/SLM-Legal-ES-Research)
