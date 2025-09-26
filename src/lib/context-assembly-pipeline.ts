// 🏗️ Context Assembly Pipeline - World-Class Implementation
// Paul Iusztin Framework for Legal AI Context Engineering
// Optimal information selection and context compression

import { YAMLLegalDocument } from './yaml-legal-corpus.js';
import { contextMemorySystem } from './context-engineering-memory.js';

// =============================================================================
// 🎯 CONTEXT ASSEMBLY INTERFACES
// =============================================================================

interface ContextAssemblyConfig {
  maxTokens: number;
  hierarchyWeights: Record<number, number>;
  relevanceThreshold: number;
  compressionLevel: 'none' | 'light' | 'medium' | 'aggressive';
  prioritizeRecency: boolean;
}

interface AssemblyResult {
  finalContext: YAMLLegalDocument[];
  tokenUsage: number;
  utilizationRate: number;
  compressionRatio: number;
  qualityScore: number;
  assembly: {
    selected: number;
    compressed: number;
    removed: number;
    totalCandidates: number;
  };
}

interface ContextQuality {
  hierarchyCoverage: number;
  topicRelevance: number;
  temporalRelevance: number;
  legalCompleteness: number;
  overallScore: number;
}

// =============================================================================
// 🧮 CONTEXT OPTIMIZATION ALGORITHMS
// =============================================================================

export class ContextOptimizer {
  
  // Advanced semantic similarity using legal term weighting
  public calculateLegalSimilarity(query: string, document: YAMLLegalDocument): number {
    const queryTerms = this.extractLegalTerms(query.toLowerCase());
    const docTerms = this.extractLegalTerms(document.content.toLowerCase());
    
    if (queryTerms.length === 0 || docTerms.length === 0) return 0;
    
    let similarity = 0;
    let totalWeight = 0;
    
    for (const [term, weight] of queryTerms) {
      totalWeight += weight;
      if (docTerms.has(term)) {
        similarity += weight * (docTerms.get(term) || 1);
      }
    }
    
    return totalWeight > 0 ? similarity / totalWeight : 0;
  }
  
  private extractLegalTerms(text: string): Map<string, number> {
    const terms = new Map<string, number>();
    
    // High-value legal terms (weight 3.0)
    const highValueTerms = [
      'responsabilidad', 'penal', 'empresaria', 'compliance', 'integridad',
      'constitucional', 'supremacía', 'jerarquía', 'competencia', 'jurisdiccion'
    ];
    
    // Medium-value legal terms (weight 2.0)
    const mediumValueTerms = [
      'civil', 'comercial', 'administrativo', 'procedimiento', 'recurso',
      'consumidor', 'defensa', 'proteccion', 'datos', 'personales'
    ];
    
    // Standard legal terms (weight 1.0)
    const standardTerms = [
      'ley', 'decreto', 'articulo', 'codigo', 'jurisprudencia',
      'tribunal', 'corte', 'suprema', 'derecho', 'obligacion'
    ];
    
    // Count terms with their weights
    for (const term of highValueTerms) {
      const count = (text.match(new RegExp(term, 'g')) || []).length;
      if (count > 0) terms.set(term, count * 3.0);
    }
    
    for (const term of mediumValueTerms) {
      const count = (text.match(new RegExp(term, 'g')) || []).length;
      if (count > 0) terms.set(term, count * 2.0);
    }
    
    for (const term of standardTerms) {
      const count = (text.match(new RegExp(term, 'g')) || []).length;
      if (count > 0) terms.set(term, count * 1.0);
    }
    
    return terms;
  }
  
  // Hierarchy-based prioritization
  public calculateHierarchyScore(document: YAMLLegalDocument, weights: Record<number, number>): number {
    return weights[document.meta.hierarchy] || 0.1;
  }
  
  // Token estimation with YAML optimization
  public estimateTokens(document: YAMLLegalDocument): number {
    // YAML format is ~66% more efficient than JSON
    const yamlContent = this.toYAMLString(document);
    return Math.ceil(yamlContent.length / 4); // ~4 chars per token for Spanish
  }
  
  private toYAMLString(doc: YAMLLegalDocument): string {
    return `id: ${doc.id}
content: ${doc.content}
meta:
  source: ${doc.meta.source}
  type: ${doc.meta.type}
  hierarchy: ${doc.meta.hierarchy}`;
  }
}

// =============================================================================
// 🗜️ CONTEXT COMPRESSION ENGINE
// =============================================================================

export class ContextCompressor {
  
  public compressDocument(
    document: YAMLLegalDocument, 
    level: 'light' | 'medium' | 'aggressive'
  ): YAMLLegalDocument {
    switch (level) {
      case 'light':
        return this.lightCompression(document);
      case 'medium':
        return this.mediumCompression(document);
      case 'aggressive':
        return this.aggressiveCompression(document);
      default:
        return document;
    }
  }
  
  private lightCompression(doc: YAMLLegalDocument): YAMLLegalDocument {
    // Remove redundant whitespace and normalize punctuation
    const compressedContent = doc.content
      .replace(/\s+/g, ' ')
      .replace(/\s*([,.;:])\s*/g, '$1 ')
      .trim();
    
    return {
      ...doc,
      content: compressedContent
    };
  }
  
  private mediumCompression(doc: YAMLLegalDocument): YAMLLegalDocument {
    let compressed = this.lightCompression(doc);
    
    // Remove common legal boilerplate
    compressed.content = compressed.content
      .replace(/en virtud de lo establecido en/gi, 'según')
      .replace(/de conformidad con lo dispuesto por/gi, 'conforme')
      .replace(/sin perjuicio de lo establecido en/gi, 'salvo')
      .replace(/a los efectos de/gi, 'para')
      .replace(/en el marco de/gi, 'bajo');
    
    return compressed;
  }
  
  private aggressiveCompression(doc: YAMLLegalDocument): YAMLLegalDocument {
    let compressed = this.mediumCompression(doc);
    
    // Extract only essential legal content
    const sentences = compressed.content.split(/[.!?]+/);
    const essentialSentences = sentences.filter(sentence => {
      const s = sentence.trim().toLowerCase();
      return s.includes('será') || s.includes('debe') || s.includes('podrá') ||
             s.includes('obligación') || s.includes('derecho') || s.includes('responsabilidad') ||
             s.length > 20; // Keep substantial sentences
    });
    
    compressed.content = essentialSentences.join('. ').trim() + '.';
    
    return compressed;
  }
  
  public calculateCompressionRatio(original: YAMLLegalDocument, compressed: YAMLLegalDocument): number {
    const originalLength = original.content.length;
    const compressedLength = compressed.content.length;
    return originalLength > 0 ? (originalLength - compressedLength) / originalLength : 0;
  }
}

// =============================================================================
// 📊 CONTEXT QUALITY ANALYZER
// =============================================================================

export class ContextQualityAnalyzer {
  
  public analyzeContextQuality(
    query: string,
    context: YAMLLegalDocument[]
  ): ContextQuality {
    const hierarchyCoverage = this.calculateHierarchyCoverage(context);
    const topicRelevance = this.calculateTopicRelevance(query, context);
    const temporalRelevance = this.calculateTemporalRelevance(context);
    const legalCompleteness = this.calculateLegalCompleteness(query, context);
    
    const overallScore = (
      hierarchyCoverage * 0.25 +
      topicRelevance * 0.35 +
      temporalRelevance * 0.15 +
      legalCompleteness * 0.25
    );
    
    return {
      hierarchyCoverage,
      topicRelevance,
      temporalRelevance,
      legalCompleteness,
      overallScore
    };
  }
  
  private calculateHierarchyCoverage(context: YAMLLegalDocument[]): number {
    const hierarchies = new Set(context.map(doc => doc.meta.hierarchy));
    const totalHierarchies = 5; // Constitution, Code, Law, Jurisprudence, Decree
    return Math.min(1.0, hierarchies.size / totalHierarchies);
  }
  
  private calculateTopicRelevance(query: string, context: YAMLLegalDocument[]): number {
    const optimizer = new ContextOptimizer();
    const relevanceScores = context.map(doc => 
      optimizer.calculateLegalSimilarity(query, doc)
    );
    
    return relevanceScores.length > 0 
      ? relevanceScores.reduce((sum, score) => sum + score, 0) / relevanceScores.length 
      : 0;
  }
  
  private calculateTemporalRelevance(context: YAMLLegalDocument[]): number {
    // All documents in corpus are currently valid (vigente: true)
    // In production, this would consider document age and amendments
    const validDocs = context.filter(doc => doc.meta.vigente);
    return context.length > 0 ? validDocs.length / context.length : 0;
  }
  
  private calculateLegalCompleteness(query: string, context: YAMLLegalDocument[]): number {
    const lowerQuery = query.toLowerCase();
    let completenessScore = 0.5; // Base score
    
    // Check for constitutional foundation
    if (context.some(doc => doc.meta.hierarchy === 1)) {
      completenessScore += 0.2;
    }
    
    // Check for specific legal domains
    if (lowerQuery.includes('empresa') || lowerQuery.includes('compliance')) {
      if (context.some(doc => doc.meta.numero === '27401')) {
        completenessScore += 0.15;
      }
    }
    
    if (lowerQuery.includes('consumidor')) {
      if (context.some(doc => doc.meta.numero === '24240' || doc.meta.articulo === '42')) {
        completenessScore += 0.15;
      }
    }
    
    return Math.min(1.0, completenessScore);
  }
}

// =============================================================================
// 🏗️ MAIN CONTEXT ASSEMBLY PIPELINE
// =============================================================================

export class ContextAssemblyPipeline {
  private optimizer: ContextOptimizer;
  private compressor: ContextCompressor;
  private qualityAnalyzer: ContextQualityAnalyzer;
  
  constructor() {
    this.optimizer = new ContextOptimizer();
    this.compressor = new ContextCompressor();
    this.qualityAnalyzer = new ContextQualityAnalyzer();
  }
  
  public async assembleOptimalContext(
    query: string,
    candidates: YAMLLegalDocument[],
    config: ContextAssemblyConfig
  ): Promise<AssemblyResult> {
    
    // Step 1: Score and rank candidates
    const scoredCandidates = this.scoreDocuments(query, candidates, config);
    
    // Step 2: Select documents within token budget
    const selectedDocs = this.selectOptimalDocuments(scoredCandidates, config.maxTokens);
    
    // Step 3: Apply compression if needed
    const compressedDocs = this.applyCompression(selectedDocs, config.compressionLevel);
    
    // Step 4: Final optimization and quality check
    const finalContext = this.finalOptimization(compressedDocs, config.maxTokens);
    
    // Calculate metrics
    const tokenUsage = finalContext.reduce((sum, doc) => 
      sum + this.optimizer.estimateTokens(doc), 0
    );
    
    const utilizationRate = (tokenUsage / config.maxTokens) * 100;
    
    const compressionRatio = this.calculateOverallCompressionRatio(
      selectedDocs, 
      finalContext
    );
    
    const qualityScore = this.qualityAnalyzer.analyzeContextQuality(
      query, 
      finalContext
    ).overallScore;
    
    return {
      finalContext,
      tokenUsage,
      utilizationRate,
      compressionRatio,
      qualityScore,
      assembly: {
        selected: selectedDocs.length,
        compressed: compressedDocs.length,
        removed: candidates.length - finalContext.length,
        totalCandidates: candidates.length
      }
    };
  }
  
  private scoreDocuments(
    query: string,
    candidates: YAMLLegalDocument[],
    config: ContextAssemblyConfig
  ): Array<{document: YAMLLegalDocument, score: number}> {
    
    return candidates.map(doc => {
      let score = 0;
      
      // Semantic relevance (40%)
      const similarity = this.optimizer.calculateLegalSimilarity(query, doc);
      score += similarity * 0.4;
      
      // Hierarchy importance (35%)
      const hierarchyScore = this.optimizer.calculateHierarchyScore(doc, config.hierarchyWeights);
      score += hierarchyScore * 0.35;
      
      // Validity and recency (15%)
      if (doc.meta.vigente) {
        score += 0.15;
      }
      
      // Topic specificity (10%)
      const specificityBonus = this.calculateSpecificityBonus(query, doc);
      score += specificityBonus * 0.1;
      
      return { document: doc, score };
    })
    .sort((a, b) => b.score - a.score);
  }
  
  private calculateSpecificityBonus(query: string, doc: YAMLLegalDocument): number {
    const lowerQuery = query.toLowerCase();
    
    // Corporate compliance specificity
    if (lowerQuery.includes('compliance') && doc.meta.numero === '27401') {
      return 1.0;
    }
    
    // Consumer protection specificity
    if (lowerQuery.includes('consumidor') && 
        (doc.meta.numero === '24240' || doc.meta.articulo === '42')) {
      return 1.0;
    }
    
    // Data protection specificity
    if (lowerQuery.includes('datos') && doc.meta.numero === '25326') {
      return 1.0;
    }
    
    return 0.0;
  }
  
  private selectOptimalDocuments(
    scoredDocs: Array<{document: YAMLLegalDocument, score: number}>,
    maxTokens: number
  ): YAMLLegalDocument[] {
    
    const selected: YAMLLegalDocument[] = [];
    let currentTokens = 0;
    
    // Greedy selection with hierarchy balance
    const hierarchySelected = new Map<number, number>();
    
    for (const {document, score} of scoredDocs) {
      const docTokens = this.optimizer.estimateTokens(document);
      
      if (currentTokens + docTokens <= maxTokens) {
        // Ensure hierarchy balance
        const hierarchy = document.meta.hierarchy;
        const hierarchyCount = hierarchySelected.get(hierarchy) || 0;
        
        // Limit documents per hierarchy to maintain balance
        if (hierarchyCount < 3 || hierarchy === 1) { // Always include Constitution
          selected.push(document);
          currentTokens += docTokens;
          hierarchySelected.set(hierarchy, hierarchyCount + 1);
        }
      }
    }
    
    return selected;
  }
  
  private applyCompression(
    documents: YAMLLegalDocument[],
    level: 'none' | 'light' | 'medium' | 'aggressive'
  ): YAMLLegalDocument[] {
    
    if (level === 'none') return documents;
    
    return documents.map(doc => 
      this.compressor.compressDocument(doc, level)
    );
  }
  
  private finalOptimization(
    documents: YAMLLegalDocument[],
    maxTokens: number
  ): YAMLLegalDocument[] {
    
    let currentTokens = documents.reduce((sum, doc) => 
      sum + this.optimizer.estimateTokens(doc), 0
    );
    
    if (currentTokens <= maxTokens) {
      return documents;
    }
    
    // Remove lowest hierarchy documents first
    const sorted = documents.sort((a, b) => a.meta.hierarchy - b.meta.hierarchy);
    const optimized: YAMLLegalDocument[] = [];
    currentTokens = 0;
    
    for (const doc of sorted) {
      const docTokens = this.optimizer.estimateTokens(doc);
      if (currentTokens + docTokens <= maxTokens) {
        optimized.push(doc);
        currentTokens += docTokens;
      }
    }
    
    return optimized;
  }
  
  private calculateOverallCompressionRatio(
    original: YAMLLegalDocument[],
    compressed: YAMLLegalDocument[]
  ): number {
    
    const originalTokens = original.reduce((sum, doc) => 
      sum + this.optimizer.estimateTokens(doc), 0
    );
    
    const compressedTokens = compressed.reduce((sum, doc) => 
      sum + this.optimizer.estimateTokens(doc), 0
    );
    
    return originalTokens > 0 ? (originalTokens - compressedTokens) / originalTokens : 0;
  }
}

// =============================================================================
// 🎯 CONTEXT ENGINEERING ORCHESTRATOR
// =============================================================================

export class WorldClassContextAssembler {
  private pipeline: ContextAssemblyPipeline;
  
  // Default configuration optimized for legal AI
  private defaultConfig: ContextAssemblyConfig = {
    maxTokens: 8000,
    hierarchyWeights: {
      1: 1.0,    // Constitution - Highest priority
      2: 0.8,    // Codes - High priority  
      3: 0.6,    // Laws - Medium priority
      4: 0.4,    // Jurisprudence - Lower priority
      5: 0.2     // Decrees - Lowest priority
    },
    relevanceThreshold: 0.3,
    compressionLevel: 'light',
    prioritizeRecency: true
  };
  
  constructor() {
    this.pipeline = new ContextAssemblyPipeline();
  }
  
  public async assembleWorldClassContext(
    query: string,
    customConfig?: Partial<ContextAssemblyConfig>
  ): Promise<AssemblyResult> {
    
    const config = { ...this.defaultConfig, ...customConfig };
    
    // Use context memory system to get candidates
    const memoryResult = await contextMemorySystem.processLegalQuery({
      query,
      jurisdiction: 'AR',
      sessionId: 'worldclass-session',
      timestamp: Date.now()
    });
    
    // Assemble optimal context using candidates
    const result = await this.pipeline.assembleOptimalContext(
      query,
      memoryResult.contextAssembly,
      config
    );
    
    return result;
  }
  
  public getOptimizedConfig(queryComplexity: 'simple' | 'medium' | 'complex'): ContextAssemblyConfig {
    switch (queryComplexity) {
      case 'simple':
        return {
          ...this.defaultConfig,
          maxTokens: 4000,
          compressionLevel: 'medium'
        };
      
      case 'complex':
        return {
          ...this.defaultConfig,
          maxTokens: 16000,
          compressionLevel: 'light'
        };
      
      default:
        return this.defaultConfig;
    }
  }
  
  public analyzeContextEfficiency(result: AssemblyResult): {
    efficiency: 'excellent' | 'good' | 'fair' | 'poor';
    recommendations: string[];
  } {
    const { utilizationRate, qualityScore, compressionRatio } = result;
    
    let efficiency: 'excellent' | 'good' | 'fair' | 'poor' = 'poor';
    const recommendations: string[] = [];
    
    if (utilizationRate > 85 && qualityScore > 0.8 && compressionRatio < 0.3) {
      efficiency = 'excellent';
    } else if (utilizationRate > 70 && qualityScore > 0.65) {
      efficiency = 'good';
    } else if (utilizationRate > 50 && qualityScore > 0.5) {
      efficiency = 'fair';
      recommendations.push('Consider increasing compression level');
      recommendations.push('Review document selection criteria');
    } else {
      efficiency = 'poor';
      recommendations.push('Optimize query-document matching');
      recommendations.push('Increase compression level');
      recommendations.push('Review hierarchy weights');
    }
    
    return { efficiency, recommendations };
  }
}

// Export singleton instance
export const worldClassContextAssembler = new WorldClassContextAssembler();