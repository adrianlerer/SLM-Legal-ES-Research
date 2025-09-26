// ⚡ Context Degradation Manager - 32K Token Limit Handling
// Paul Iusztin Framework Implementation for Legal AI Context Engineering
// Proactive context management and degradation prevention

import { YAMLLegalDocument } from './yaml-legal-corpus.js';
import { worldClassContextAssembler } from './context-assembly-pipeline.js';

// =============================================================================
// 📊 DEGRADATION MONITORING INTERFACES
// =============================================================================

interface ContextDegradationMetrics {
  currentTokens: number;
  maxTokens: number;
  utilizationRate: number;
  degradationRisk: 'low' | 'medium' | 'high' | 'critical';
  projectedDegradation: number;
  recommendedAction: DegradationAction;
}

interface DegradationAction {
  action: 'maintain' | 'compress' | 'trim' | 'rebuild';
  priority: 'low' | 'medium' | 'high';
  description: string;
  estimatedSavings: number;
}

interface ContextWindow {
  documents: YAMLLegalDocument[];
  tokens: number;
  quality: number;
  timestamp: number;
}

interface DegradationStrategy {
  name: string;
  threshold: number;
  action: (context: ContextWindow) => ContextWindow;
  description: string;
}

// =============================================================================
// 🔍 CONTEXT DEGRADATION DETECTOR
// =============================================================================

export class ContextDegradationDetector {
  
  // Paul Iusztin's 32K degradation point - we use conservative 28K
  private readonly DEGRADATION_START = 28000;
  private readonly CRITICAL_LIMIT = 31000;
  private readonly OPTIMAL_RANGE = 24000;
  
  public analyzeContextDegradation(
    currentTokens: number,
    maxTokens: number = 32000
  ): ContextDegradationMetrics {
    
    const utilizationRate = (currentTokens / maxTokens) * 100;
    
    let degradationRisk: 'low' | 'medium' | 'high' | 'critical' = 'low';
    let projectedDegradation = 0;
    let recommendedAction: DegradationAction;
    
    if (currentTokens >= this.CRITICAL_LIMIT) {
      degradationRisk = 'critical';
      projectedDegradation = 0.4; // 40% quality loss expected
      recommendedAction = {
        action: 'rebuild',
        priority: 'high',
        description: 'Critical degradation detected. Full context rebuild required.',
        estimatedSavings: currentTokens - this.OPTIMAL_RANGE
      };
    } else if (currentTokens >= this.DEGRADATION_START) {
      degradationRisk = 'high';
      projectedDegradation = ((currentTokens - this.DEGRADATION_START) / (this.CRITICAL_LIMIT - this.DEGRADATION_START)) * 0.3;
      recommendedAction = {
        action: 'compress',
        priority: 'high',
        description: 'Degradation threshold exceeded. Apply aggressive compression.',
        estimatedSavings: Math.ceil((currentTokens - this.OPTIMAL_RANGE) * 0.7)
      };
    } else if (currentTokens >= this.OPTIMAL_RANGE) {
      degradationRisk = 'medium';
      projectedDegradation = ((currentTokens - this.OPTIMAL_RANGE) / (this.DEGRADATION_START - this.OPTIMAL_RANGE)) * 0.15;
      recommendedAction = {
        action: 'trim',
        priority: 'medium',
        description: 'Approaching degradation zone. Trim low-priority documents.',
        estimatedSavings: currentTokens - this.OPTIMAL_RANGE
      };
    } else {
      degradationRisk = 'low';
      projectedDegradation = 0;
      recommendedAction = {
        action: 'maintain',
        priority: 'low',
        description: 'Context within optimal range. No action required.',
        estimatedSavings: 0
      };
    }
    
    return {
      currentTokens,
      maxTokens,
      utilizationRate,
      degradationRisk,
      projectedDegradation,
      recommendedAction
    };
  }
  
  public predictDegradationPoint(
    currentTokens: number,
    additionRate: number
  ): {
    tokensUntilDegradation: number;
    estimatedQueries: number;
    timeToDegrade: string;
  } {
    
    const tokensUntilDegradation = Math.max(0, this.DEGRADATION_START - currentTokens);
    const estimatedQueries = additionRate > 0 ? Math.floor(tokensUntilDegradation / additionRate) : Infinity;
    
    let timeToDegrade = 'No degradation expected';
    if (estimatedQueries < 10) {
      timeToDegrade = 'Immediate action required';
    } else if (estimatedQueries < 50) {
      timeToDegrade = 'Within next 10-15 queries';
    } else if (estimatedQueries < 100) {
      timeToDegrade = 'Within next 50+ queries';
    }
    
    return {
      tokensUntilDegradation,
      estimatedQueries,
      timeToDegrade
    };
  }
}

// =============================================================================
// 🛠️ PROACTIVE CONTEXT OPTIMIZER
// =============================================================================

export class ProactiveContextOptimizer {
  
  private strategies: DegradationStrategy[] = [];
  
  constructor() {
    this.initializeStrategies();
  }
  
  private initializeStrategies(): void {
    
    // Strategy 1: Smart Trimming (75% threshold)
    this.strategies.push({
      name: 'smart_trim',
      threshold: 0.75,
      action: (context: ContextWindow) => {
        // Remove lowest hierarchy documents first
        const sorted = context.documents.sort((a, b) => b.meta.hierarchy - a.meta.hierarchy);
        const trimmed = sorted.slice(0, Math.ceil(sorted.length * 0.8));
        
        return {
          ...context,
          documents: trimmed,
          tokens: trimmed.reduce((sum, doc) => sum + this.estimateTokens(doc), 0)
        };
      },
      description: 'Remove 20% of lowest hierarchy documents'
    });
    
    // Strategy 2: Aggressive Compression (85% threshold)
    this.strategies.push({
      name: 'aggressive_compress',
      threshold: 0.85,
      action: (context: ContextWindow) => {
        const compressed = context.documents.map(doc => {
          const compressedContent = this.aggressiveCompress(doc.content);
          return { ...doc, content: compressedContent };
        });
        
        return {
          ...context,
          documents: compressed,
          tokens: compressed.reduce((sum, doc) => sum + this.estimateTokens(doc), 0)
        };
      },
      description: 'Apply aggressive content compression'
    });
    
    // Strategy 3: Hierarchical Reduction (90% threshold)
    this.strategies.push({
      name: 'hierarchical_reduction',
      threshold: 0.90,
      action: (context: ContextWindow) => {
        // Keep only Constitution (1), Codes (2), and highest-priority Laws (3)
        const essential = context.documents.filter(doc => 
          doc.meta.hierarchy <= 2 || 
          (doc.meta.hierarchy === 3 && this.isHighPriorityLaw(doc))
        );
        
        return {
          ...context,
          documents: essential,
          tokens: essential.reduce((sum, doc) => sum + this.estimateTokens(doc), 0)
        };
      },
      description: 'Keep only essential high-hierarchy documents'
    });
    
    // Strategy 4: Emergency Rebuild (95% threshold)
    this.strategies.push({
      name: 'emergency_rebuild',
      threshold: 0.95,
      action: (context: ContextWindow) => {
        // Keep only top 3 most relevant documents
        const top3 = context.documents
          .sort((a, b) => a.meta.hierarchy - b.meta.hierarchy)
          .slice(0, 3);
        
        return {
          ...context,
          documents: top3,
          tokens: top3.reduce((sum, doc) => sum + this.estimateTokens(doc), 0),
          quality: context.quality * 0.6 // Mark quality reduction
        };
      },
      description: 'Emergency: Keep only top 3 essential documents'
    });
  }
  
  private estimateTokens(doc: YAMLLegalDocument): number {
    return Math.ceil(doc.content.length / 4);
  }
  
  private aggressiveCompress(content: string): string {
    return content
      .replace(/\s+/g, ' ')
      .replace(/\b(de conformidad con|en virtud de|a los efectos de)\b/gi, '')
      .replace(/\b(sin perjuicio de lo establecido en|en el marco de)\b/gi, '')
      .split('. ')
      .filter(sentence => sentence.length > 30) // Keep substantial sentences
      .join('. ')
      .trim();
  }
  
  private isHighPriorityLaw(doc: YAMLLegalDocument): boolean {
    const highPriorityLaws = ['27401', '24240', '25326', '19549'];
    return highPriorityLaws.includes(doc.meta.numero || '');
  }
  
  public optimizeContext(
    context: ContextWindow,
    maxTokens: number = 32000
  ): {
    optimizedContext: ContextWindow;
    appliedStrategies: string[];
    tokensSaved: number;
  } {
    
    const utilizationRate = context.tokens / maxTokens;
    let currentContext = { ...context };
    const appliedStrategies: string[] = [];
    const originalTokens = context.tokens;
    
    for (const strategy of this.strategies) {
      if (utilizationRate >= strategy.threshold) {
        currentContext = strategy.action(currentContext);
        appliedStrategies.push(strategy.name);
        
        // Check if we're now within acceptable range
        if (currentContext.tokens <= maxTokens * 0.8) {
          break;
        }
      }
    }
    
    const tokensSaved = originalTokens - currentContext.tokens;
    
    return {
      optimizedContext: currentContext,
      appliedStrategies,
      tokensSaved
    };
  }
}

// =============================================================================
// 📈 ADAPTIVE CONTEXT MANAGER
// =============================================================================

export class AdaptiveContextManager {
  
  private detector: ContextDegradationDetector;
  private optimizer: ProactiveContextOptimizer;
  private contextHistory: ContextWindow[] = [];
  
  constructor() {
    this.detector = new ContextDegradationDetector();
    this.optimizer = new ProactiveContextOptimizer();
  }
  
  public async manageContext(
    currentContext: YAMLLegalDocument[],
    query: string,
    sessionId?: string
  ): Promise<{
    optimizedContext: YAMLLegalDocument[];
    degradationMetrics: ContextDegradationMetrics;
    optimizationReport: {
      appliedStrategies: string[];
      tokensSaved: number;
      qualityImpact: number;
    };
    recommendations: string[];
  }> {
    
    // Calculate current token usage
    const currentTokens = currentContext.reduce((sum, doc) => 
      sum + Math.ceil(doc.content.length / 4), 0
    );
    
    // Analyze degradation risk
    const degradationMetrics = this.detector.analyzeContextDegradation(currentTokens);
    
    // Create context window
    const contextWindow: ContextWindow = {
      documents: currentContext,
      tokens: currentTokens,
      quality: 1.0, // Initial quality
      timestamp: Date.now()
    };
    
    // Apply optimization if needed
    let optimizedContext = currentContext;
    let appliedStrategies: string[] = [];
    let tokensSaved = 0;
    let qualityImpact = 0;
    
    if (degradationMetrics.degradationRisk !== 'low') {
      const optimization = this.optimizer.optimizeContext(contextWindow);
      optimizedContext = optimization.optimizedContext.documents;
      appliedStrategies = optimization.appliedStrategies;
      tokensSaved = optimization.tokensSaved;
      qualityImpact = optimization.optimizedContext.quality - contextWindow.quality;
    }
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(
      degradationMetrics,
      appliedStrategies
    );
    
    // Store in history for learning
    this.contextHistory.push(contextWindow);
    if (this.contextHistory.length > 100) {
      this.contextHistory.shift(); // Keep last 100 contexts
    }
    
    return {
      optimizedContext,
      degradationMetrics,
      optimizationReport: {
        appliedStrategies,
        tokensSaved,
        qualityImpact
      },
      recommendations
    };
  }
  
  private generateRecommendations(
    metrics: ContextDegradationMetrics,
    appliedStrategies: string[]
  ): string[] {
    
    const recommendations: string[] = [];
    
    if (metrics.degradationRisk === 'critical') {
      recommendations.push('🚨 Critical: Implement full context rebuild pipeline');
      recommendations.push('📊 Monitor token usage in real-time');
      recommendations.push('🔧 Consider increasing compression levels globally');
    } else if (metrics.degradationRisk === 'high') {
      recommendations.push('⚠️ High risk: Apply aggressive compression to all documents');
      recommendations.push('📉 Reduce context window size for next queries');
      recommendations.push('🎯 Focus on highest hierarchy documents only');
    } else if (metrics.degradationRisk === 'medium') {
      recommendations.push('📋 Medium risk: Proactively trim lower-priority documents');
      recommendations.push('🔄 Consider implementing sliding window approach');
      recommendations.push('📊 Monitor query complexity to predict token usage');
    }
    
    if (appliedStrategies.length > 0) {
      recommendations.push(`✅ Applied optimization: ${appliedStrategies.join(', ')}`);
    }
    
    recommendations.push(`💡 Current utilization: ${metrics.utilizationRate.toFixed(1)}%`);
    
    return recommendations;
  }
  
  public getContextStatistics(): {
    averageTokens: number;
    peakTokens: number;
    degradationEvents: number;
    averageQuality: number;
  } {
    
    if (this.contextHistory.length === 0) {
      return {
        averageTokens: 0,
        peakTokens: 0,
        degradationEvents: 0,
        averageQuality: 1.0
      };
    }
    
    const avgTokens = this.contextHistory.reduce((sum, ctx) => sum + ctx.tokens, 0) / this.contextHistory.length;
    const peakTokens = Math.max(...this.contextHistory.map(ctx => ctx.tokens));
    const degradationEvents = this.contextHistory.filter(ctx => ctx.tokens > 28000).length;
    const avgQuality = this.contextHistory.reduce((sum, ctx) => sum + ctx.quality, 0) / this.contextHistory.length;
    
    return {
      averageTokens: Math.round(avgTokens),
      peakTokens,
      degradationEvents,
      averageQuality: Math.round(avgQuality * 100) / 100
    };
  }
}

// =============================================================================
// 🎯 WORLD-CLASS DEGRADATION MANAGEMENT SYSTEM
// =============================================================================

export class WorldClassDegradationManager {
  
  private adaptiveManager: AdaptiveContextManager;
  
  constructor() {
    this.adaptiveManager = new AdaptiveContextManager();
  }
  
  public async preventContextDegradation(
    query: string,
    candidates: YAMLLegalDocument[],
    sessionId?: string
  ): Promise<{
    optimizedContext: YAMLLegalDocument[];
    performance: {
      degradationRisk: string;
      tokenEfficiency: number;
      qualityScore: number;
      optimizationsApplied: string[];
    };
    insights: {
      utilizationRate: number;
      tokensUsed: number;
      tokensSaved: number;
      recommendations: string[];
    };
  }> {
    
    // First, get optimal context from world-class assembler
    const assemblyResult = await worldClassContextAssembler.assembleWorldClassContext(
      query,
      { maxTokens: 28000 } // Conservative limit to prevent degradation
    );
    
    // Then apply degradation management
    const managementResult = await this.adaptiveManager.manageContext(
      assemblyResult.finalContext,
      query,
      sessionId
    );
    
    return {
      optimizedContext: managementResult.optimizedContext,
      performance: {
        degradationRisk: managementResult.degradationMetrics.degradationRisk,
        tokenEfficiency: managementResult.degradationMetrics.utilizationRate,
        qualityScore: assemblyResult.qualityScore,
        optimizationsApplied: managementResult.optimizationReport.appliedStrategies
      },
      insights: {
        utilizationRate: managementResult.degradationMetrics.utilizationRate,
        tokensUsed: managementResult.degradationMetrics.currentTokens,
        tokensSaved: managementResult.optimizationReport.tokensSaved,
        recommendations: managementResult.recommendations
      }
    };
  }
  
  public getSystemHealth(): {
    status: 'optimal' | 'good' | 'warning' | 'critical';
    metrics: any;
    recommendations: string[];
  } {
    
    const stats = this.adaptiveManager.getContextStatistics();
    
    let status: 'optimal' | 'good' | 'warning' | 'critical' = 'optimal';
    const recommendations: string[] = [];
    
    if (stats.averageTokens > 30000) {
      status = 'critical';
      recommendations.push('🚨 Average token usage too high - implement global compression');
    } else if (stats.averageTokens > 25000) {
      status = 'warning';
      recommendations.push('⚠️ Monitor token usage closely');
    } else if (stats.averageTokens > 20000) {
      status = 'good';
      recommendations.push('📊 System performing well');
    } else {
      recommendations.push('✅ System in optimal range');
    }
    
    if (stats.degradationEvents > stats.averageTokens * 0.1) {
      recommendations.push('🔧 Too many degradation events - optimize context assembly');
    }
    
    return {
      status,
      metrics: stats,
      recommendations
    };
  }
}

// Export singleton instance
export const worldClassDegradationManager = new WorldClassDegradationManager();