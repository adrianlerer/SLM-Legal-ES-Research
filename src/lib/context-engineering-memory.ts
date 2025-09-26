// 🧠 Context Engineering - 5-Memory Architecture 
// Paul Iusztin Framework Implementation for Legal AI
// World-class implementation for SLM-Legal-Spanish

import { YAMLLegalDocument, loadYAMLLegalCorpus, calculateLegalContextWindow } from './yaml-legal-corpus.js';

// =============================================================================
// 🏗️ MEMORY ARCHITECTURE INTERFACES
// =============================================================================

interface LegalQuery {
  query: string;
  jurisdiction: string;
  context?: string;
  sessionId?: string;
  timestamp: number;
}

interface LegalResponse {
  answer: string;
  citations: string[];
  confidence: number;
  riskMetrics: RiskMetrics;
}

interface RiskMetrics {
  rohBound: number;
  isrRatio: number;
  informationBudget: number;
  decision: 'ANSWER' | 'ABSTAIN';
  rationale: string;
}

interface ConsultationPattern {
  queryType: 'corporate' | 'compliance' | 'constitutional' | 'procedural';
  frequency: number;
  successRate: number;
  avgConfidence: number;
}

// =============================================================================
// 1️⃣ LONG-TERM MEMORY: Legal Knowledge Base
// =============================================================================

export class LegalLongTermMemory {
  private legalCorpus: YAMLLegalDocument[];
  private hierarchyIndex: Map<number, YAMLLegalDocument[]>;
  private topicIndex: Map<string, YAMLLegalDocument[]>;
  
  constructor() {
    this.legalCorpus = loadYAMLLegalCorpus();
    this.hierarchyIndex = new Map();
    this.topicIndex = new Map();
    this.buildIndexes();
  }
  
  private buildIndexes(): void {
    // Hierarchy index (Constitution > Code > Law > Decree > Jurisprudence)
    for (const doc of this.legalCorpus) {
      const hierarchy = doc.meta.hierarchy;
      if (!this.hierarchyIndex.has(hierarchy)) {
        this.hierarchyIndex.set(hierarchy, []);
      }
      this.hierarchyIndex.get(hierarchy)!.push(doc);
    }
    
    // Topic index (basic keyword extraction)
    for (const doc of this.legalCorpus) {
      const keywords = this.extractLegalKeywords(doc.content);
      for (const keyword of keywords) {
        if (!this.topicIndex.has(keyword)) {
          this.topicIndex.set(keyword, []);
        }
        this.topicIndex.get(keyword)!.push(doc);
      }
    }
  }
  
  private extractLegalKeywords(content: string): string[] {
    // Advanced legal keyword extraction for Argentine law
    const legalTerms = [
      'responsabilidad', 'penal', 'civil', 'administrativo', 'constitucional',
      'consumidor', 'defensa', 'competencia', 'monopolio', 'servicio', 'publico',
      'persona', 'juridica', 'empresa', 'compliance', 'integridad', 'supervision',
      'daño', 'reparacion', 'culpa', 'negligencia', 'riesgo', 'objetiva',
      'homicidio', 'delito', 'pena', 'prision', 'reclusión',
      'acto', 'legitimidad', 'ejecutoria', 'recurso', 'procedimiento',
      'datos', 'personales', 'privacidad', 'informacion', 'tratamiento',
      'concurso', 'quiebra', 'cesacion', 'pagos', 'acreedores',
      'tributario', 'afip', 'verificacion', 'determinacion', 'impuesto'
    ];
    
    return legalTerms.filter(term => 
      content.toLowerCase().includes(term.toLowerCase())
    );
  }
  
  public retrieveByHierarchy(hierarchy: number[]): YAMLLegalDocument[] {
    const results: YAMLLegalDocument[] = [];
    for (const h of hierarchy) {
      const docs = this.hierarchyIndex.get(h) || [];
      results.push(...docs);
    }
    return results;
  }
  
  public retrieveByTopic(topics: string[]): YAMLLegalDocument[] {
    const results: YAMLLegalDocument[] = [];
    const seen = new Set<string>();
    
    for (const topic of topics) {
      const docs = this.topicIndex.get(topic) || [];
      for (const doc of docs) {
        if (!seen.has(doc.id)) {
          results.push(doc);
          seen.add(doc.id);
        }
      }
    }
    
    return results.sort((a, b) => a.meta.hierarchy - b.meta.hierarchy);
  }
  
  public getCorpusStats(): {
    totalDocuments: number;
    byHierarchy: Map<number, number>;
    tokenCount: number;
  } {
    const byHierarchy = new Map<number, number>();
    let tokenCount = 0;
    
    for (const doc of this.legalCorpus) {
      const hierarchy = doc.meta.hierarchy;
      byHierarchy.set(hierarchy, (byHierarchy.get(hierarchy) || 0) + 1);
      tokenCount += Math.ceil(doc.content.length / 4);
    }
    
    return {
      totalDocuments: this.legalCorpus.length,
      byHierarchy,
      tokenCount
    };
  }
}

// =============================================================================
// 2️⃣ SHORT-TERM MEMORY: Current Query Context
// =============================================================================

export class LegalShortTermMemory {
  private currentQuery: LegalQuery | null = null;
  private retrievedDocs: YAMLLegalDocument[] = [];
  private contextWindow: YAMLLegalDocument[] = [];
  private contextTokens: number = 0;
  
  public setQuery(query: LegalQuery): void {
    this.currentQuery = query;
    this.contextWindow = [];
    this.contextTokens = 0;
  }
  
  public addRetrievedDocuments(docs: YAMLLegalDocument[]): void {
    this.retrievedDocs = docs;
    // Optimize context window based on token limits
    const optimization = calculateLegalContextWindow(docs, 8000); // 8K tokens for context
    this.contextWindow = optimization.selectedDocs;
    this.contextTokens = optimization.totalTokens;
  }
  
  public getContextSummary(): {
    query: LegalQuery | null;
    documentCount: number;
    tokenUsage: number;
    utilizationRate: number;
  } {
    return {
      query: this.currentQuery,
      documentCount: this.contextWindow.length,
      tokenUsage: this.contextTokens,
      utilizationRate: (this.contextTokens / 8000) * 100
    };
  }
  
  public getOptimizedContext(): YAMLLegalDocument[] {
    return this.contextWindow;
  }
}

// =============================================================================
// 3️⃣ WORKING MEMORY: EDFL Processing State
// =============================================================================

export class LegalWorkingMemory {
  private informationBudget: number = 0;
  private isrRatio: number = 0;
  private rohBound: number = 0;
  private processingState: 'IDLE' | 'RETRIEVING' | 'PROCESSING' | 'VALIDATING' = 'IDLE';
  private startTime: number = 0;
  
  public startProcessing(): void {
    this.processingState = 'RETRIEVING';
    this.startTime = Date.now();
  }
  
  public updateEDFLMetrics(
    informationBudget: number,
    isrRatio: number,
    rohBound: number
  ): void {
    this.informationBudget = informationBudget;
    this.isrRatio = isrRatio;
    this.rohBound = rohBound;
    this.processingState = 'PROCESSING';
  }
  
  public validateDecision(): RiskMetrics {
    this.processingState = 'VALIDATING';
    
    const decision: 'ANSWER' | 'ABSTAIN' = 
      this.isrRatio >= 1.0 && this.rohBound <= 0.05 ? 'ANSWER' : 'ABSTAIN';
    
    const rationale = decision === 'ANSWER' 
      ? `Evidence sufficient: ISR ${this.isrRatio.toFixed(2)}, RoH ${(this.rohBound * 100).toFixed(1)}%`
      : `Insufficient evidence: ISR ${this.isrRatio.toFixed(2)}, RoH ${(this.rohBound * 100).toFixed(1)}%`;
    
    return {
      rohBound: this.rohBound,
      isrRatio: this.isrRatio,
      informationBudget: this.informationBudget,
      decision,
      rationale
    };
  }
  
  public getProcessingTime(): number {
    return Date.now() - this.startTime;
  }
  
  public reset(): void {
    this.processingState = 'IDLE';
    this.informationBudget = 0;
    this.isrRatio = 0;
    this.rohBound = 0;
  }
}

// =============================================================================
// 4️⃣ EPISODIC MEMORY: Legal Consultation History
// =============================================================================

export class LegalEpisodicMemory {
  private consultationHistory: Map<string, Array<{query: LegalQuery, response: LegalResponse, timestamp: number}>> = new Map();
  private patternAnalysis: Map<string, ConsultationPattern> = new Map();
  
  public addConsultation(query: LegalQuery, response: LegalResponse): void {
    const sessionId = query.sessionId || 'default';
    
    if (!this.consultationHistory.has(sessionId)) {
      this.consultationHistory.set(sessionId, []);
    }
    
    this.consultationHistory.get(sessionId)!.push({
      query,
      response,
      timestamp: Date.now()
    });
    
    this.updatePatternAnalysis(query, response);
  }
  
  private updatePatternAnalysis(query: LegalQuery, response: LegalResponse): void {
    const queryType = this.classifyQuery(query.query);
    
    if (!this.patternAnalysis.has(queryType)) {
      this.patternAnalysis.set(queryType, {
        queryType: queryType as any,
        frequency: 0,
        successRate: 0,
        avgConfidence: 0
      });
    }
    
    const pattern = this.patternAnalysis.get(queryType)!;
    pattern.frequency += 1;
    
    // Update success rate (ANSWER decisions)
    const isSuccess = response.riskMetrics.decision === 'ANSWER';
    pattern.successRate = (pattern.successRate * (pattern.frequency - 1) + (isSuccess ? 1 : 0)) / pattern.frequency;
    
    // Update average confidence
    pattern.avgConfidence = (pattern.avgConfidence * (pattern.frequency - 1) + response.confidence) / pattern.frequency;
  }
  
  private classifyQuery(query: string): string {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('empresa') || lowerQuery.includes('sociedad') || lowerQuery.includes('compliance')) {
      return 'corporate';
    } else if (lowerQuery.includes('constitucion') || lowerQuery.includes('derecho')) {
      return 'constitutional';
    } else if (lowerQuery.includes('procedimiento') || lowerQuery.includes('recurso')) {
      return 'procedural';
    } else {
      return 'compliance';
    }
  }
  
  public getSessionHistory(sessionId: string): Array<{query: LegalQuery, response: LegalResponse, timestamp: number}> {
    return this.consultationHistory.get(sessionId) || [];
  }
  
  public getPatternInsights(): ConsultationPattern[] {
    return Array.from(this.patternAnalysis.values());
  }
  
  public getRelevantHistory(currentQuery: string, limit: number = 3): Array<{query: LegalQuery, response: LegalResponse}> {
    const allHistory: Array<{query: LegalQuery, response: LegalResponse, timestamp: number}> = [];
    
    for (const sessionHistory of this.consultationHistory.values()) {
      allHistory.push(...sessionHistory);
    }
    
    // Sort by timestamp (most recent first) and return relevant queries
    return allHistory
      .sort((a, b) => b.timestamp - a.timestamp)
      .filter(item => this.isRelevantQuery(currentQuery, item.query.query))
      .slice(0, limit)
      .map(item => ({ query: item.query, response: item.response }));
  }
  
  private isRelevantQuery(currentQuery: string, historyQuery: string): boolean {
    // Simple relevance check - can be enhanced with semantic similarity
    const currentWords = currentQuery.toLowerCase().split(' ');
    const historyWords = historyQuery.toLowerCase().split(' ');
    
    let commonWords = 0;
    for (const word of currentWords) {
      if (historyWords.includes(word) && word.length > 3) {
        commonWords++;
      }
    }
    
    return commonWords >= 2;
  }
}

// =============================================================================
// 5️⃣ PROCEDURAL MEMORY: Legal Validation Rules
// =============================================================================

export class LegalProceduralMemory {
  private validationRules: Map<string, (docs: YAMLLegalDocument[]) => boolean> = new Map();
  private hierarchyRules: Map<number, string> = new Map();
  private complianceRules: Array<(query: string, docs: YAMLLegalDocument[]) => {valid: boolean, reason: string}> = [];
  
  constructor() {
    this.initializeValidationRules();
    this.initializeHierarchyRules();
    this.initializeComplianceRules();
  }
  
  private initializeValidationRules(): void {
    // Constitutional supremacy validation
    this.validationRules.set('constitutional_supremacy', (docs: YAMLLegalDocument[]) => {
      const constitutionalDocs = docs.filter(d => d.meta.hierarchy === 1);
      const lowerDocs = docs.filter(d => d.meta.hierarchy > 1);
      
      // If constitutional docs exist, they should be prioritized
      return constitutionalDocs.length === 0 || constitutionalDocs.length >= lowerDocs.length * 0.3;
    });
    
    // Hierarchy consistency validation
    this.validationRules.set('hierarchy_consistency', (docs: YAMLLegalDocument[]) => {
      const hierarchies = docs.map(d => d.meta.hierarchy).sort();
      // Ensure reasonable hierarchy distribution
      return new Set(hierarchies).size <= 3; // Max 3 different hierarchies in context
    });
    
    // Current validity validation
    this.validationRules.set('validity_check', (docs: YAMLLegalDocument[]) => {
      return docs.every(d => d.meta.vigente === true);
    });
  }
  
  private initializeHierarchyRules(): void {
    this.hierarchyRules.set(1, 'Constitución Nacional - Supremacía absoluta');
    this.hierarchyRules.set(2, 'Códigos - Ley fundamental sectorial');
    this.hierarchyRules.set(3, 'Leyes - Normativa específica');
    this.hierarchyRules.set(4, 'Jurisprudencia - Interpretación judicial');
    this.hierarchyRules.set(5, 'Decretos - Reglamentación ejecutiva');
  }
  
  private initializeComplianceRules(): void {
    // Ley 27.401 compliance detection
    this.complianceRules.push((query: string, docs: YAMLLegalDocument[]) => {
      const hasComplianceQuery = query.toLowerCase().includes('compliance') || 
                                query.toLowerCase().includes('programa de integridad') ||
                                query.toLowerCase().includes('responsabilidad penal empresaria');
      
      const hasLey27401 = docs.some(d => d.meta.numero === '27401');
      
      if (hasComplianceQuery && !hasLey27401) {
        return {
          valid: false,
          reason: 'Consulta de compliance sin incluir Ley 27.401 (Responsabilidad Penal Empresaria)'
        };
      }
      
      return { valid: true, reason: 'Compliance check passed' };
    });
    
    // Consumer protection compliance
    this.complianceRules.push((query: string, docs: YAMLLegalDocument[]) => {
      const hasConsumerQuery = query.toLowerCase().includes('consumidor') || 
                              query.toLowerCase().includes('defensa del consumidor');
      
      const hasConsumerLaw = docs.some(d => d.meta.numero === '24240' || d.meta.articulo === '42');
      
      if (hasConsumerQuery && !hasConsumerLaw) {
        return {
          valid: false,
          reason: 'Consulta de defensa del consumidor sin marco normativo adecuado'
        };
      }
      
      return { valid: true, reason: 'Consumer protection check passed' };
    });
  }
  
  public validateLegalContext(
    query: string, 
    docs: YAMLLegalDocument[]
  ): {
    isValid: boolean;
    violations: string[];
    recommendations: string[];
  } {
    const violations: string[] = [];
    const recommendations: string[] = [];
    
    // Run validation rules
    for (const [ruleName, rule] of this.validationRules) {
      if (!rule(docs)) {
        violations.push(`Violation: ${ruleName}`);
      }
    }
    
    // Run compliance rules
    for (const complianceRule of this.complianceRules) {
      const result = complianceRule(query, docs);
      if (!result.valid) {
        violations.push(result.reason);
      }
    }
    
    // Generate recommendations
    if (violations.length > 0) {
      recommendations.push('Revisar selección de documentos legales');
      recommendations.push('Verificar jerarquía normativa');
      recommendations.push('Incluir normativa de mayor jerarquía si está disponible');
    }
    
    return {
      isValid: violations.length === 0,
      violations,
      recommendations
    };
  }
  
  public getHierarchyExplanation(hierarchy: number): string {
    return this.hierarchyRules.get(hierarchy) || 'Jerarquía no reconocida';
  }
  
  public suggestMissingNorms(query: string): string[] {
    const suggestions: string[] = [];
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('empresa') && !lowerQuery.includes('27401')) {
      suggestions.push('Considerar Ley 27.401 (Responsabilidad Penal Empresaria)');
    }
    
    if (lowerQuery.includes('consumidor') && !lowerQuery.includes('24240')) {
      suggestions.push('Considerar Ley 24.240 (Defensa del Consumidor)');
    }
    
    if (lowerQuery.includes('datos') && !lowerQuery.includes('25326')) {
      suggestions.push('Considerar Ley 25.326 (Protección de Datos Personales)');
    }
    
    return suggestions;
  }
}

// =============================================================================
// 🧠 CONTEXT ENGINEERING ORCHESTRATOR
// =============================================================================

export class ContextEngineeringMemorySystem {
  private longTermMemory: LegalLongTermMemory;
  private shortTermMemory: LegalShortTermMemory;
  private workingMemory: LegalWorkingMemory;
  private episodicMemory: LegalEpisodicMemory;
  private proceduralMemory: LegalProceduralMemory;
  
  constructor() {
    this.longTermMemory = new LegalLongTermMemory();
    this.shortTermMemory = new LegalShortTermMemory();
    this.workingMemory = new LegalWorkingMemory();
    this.episodicMemory = new LegalEpisodicMemory();
    this.proceduralMemory = new LegalProceduralMemory();
  }
  
  public async processLegalQuery(query: LegalQuery): Promise<{
    contextAssembly: YAMLLegalDocument[];
    riskMetrics: RiskMetrics;
    memoryStats: any;
    validation: any;
  }> {
    // Start processing
    this.workingMemory.startProcessing();
    this.shortTermMemory.setQuery(query);
    
    // 1. Long-term: Retrieve relevant legal documents
    const keywords = query.query.toLowerCase().split(' ');
    const topicDocs = this.longTermMemory.retrieveByTopic(keywords);
    const hierarchyDocs = this.longTermMemory.retrieveByHierarchy([1, 2, 3]); // Prefer higher hierarchy
    
    // Combine and deduplicate
    const allDocs = [...topicDocs, ...hierarchyDocs];
    const uniqueDocs = Array.from(new Map(allDocs.map(d => [d.id, d])).values());
    
    // 2. Short-term: Optimize context window
    this.shortTermMemory.addRetrievedDocuments(uniqueDocs);
    const contextAssembly = this.shortTermMemory.getOptimizedContext();
    
    // 3. Episodic: Get relevant history
    const relevantHistory = this.episodicMemory.getRelevantHistory(query.query);
    
    // 4. Working: Calculate EDFL metrics
    const informationBudget = contextAssembly.reduce((sum, doc) => sum + doc.content.length, 0) / 4;
    const isrRatio = Math.min(2.0, informationBudget / 1000); // Simplified ISR calculation
    const rohBound = Math.max(0.01, 0.08 - (isrRatio * 0.03)); // Simplified RoH calculation
    
    this.workingMemory.updateEDFLMetrics(informationBudget, isrRatio, rohBound);
    const riskMetrics = this.workingMemory.validateDecision();
    
    // 5. Procedural: Validate legal context
    const validation = this.proceduralMemory.validateLegalContext(query.query, contextAssembly);
    
    // Collect memory statistics
    const memoryStats = {
      longTerm: this.longTermMemory.getCorpusStats(),
      shortTerm: this.shortTermMemory.getContextSummary(),
      episodic: {
        patternInsights: this.episodicMemory.getPatternInsights(),
        relevantHistory: relevantHistory.length
      },
      working: {
        processingTime: this.workingMemory.getProcessingTime(),
        informationBudget,
        isrRatio,
        rohBound
      }
    };
    
    return {
      contextAssembly,
      riskMetrics,
      memoryStats,
      validation
    };
  }
  
  public recordConsultation(query: LegalQuery, response: LegalResponse): void {
    this.episodicMemory.addConsultation(query, response);
    this.workingMemory.reset();
  }
  
  public getSystemStatus(): {
    memoryTypes: string[];
    isHealthy: boolean;
    performance: any;
  } {
    return {
      memoryTypes: ['Long-term', 'Short-term', 'Working', 'Episodic', 'Procedural'],
      isHealthy: true,
      performance: {
        corpusSize: this.longTermMemory.getCorpusStats().totalDocuments,
        patternCount: this.episodicMemory.getPatternInsights().length,
        lastProcessingTime: this.workingMemory.getProcessingTime()
      }
    };
  }
}

// Export singleton instance
export const contextMemorySystem = new ContextEngineeringMemorySystem();