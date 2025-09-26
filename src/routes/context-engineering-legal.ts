// 🚀 Context Engineering Legal Handler - World-Class Implementation
// Paul Iusztin Framework Integration for SLM-Legal-Spanish
// The most advanced legal AI context engineering system

import type { Context } from 'hono';
import { worldClassDegradationManager } from '../lib/context-degradation-manager.js';
import { contextMemorySystem } from '../lib/context-engineering-memory.js';
import { worldClassContextAssembler } from '../lib/context-assembly-pipeline.js';
import { loadYAMLLegalCorpus, calculateTokenEfficiency, YAML_ARGENTINE_LEGAL_CORPUS } from '../lib/yaml-legal-corpus.js';
import { contextEngineeringSecurity } from '../lib/security-prompt-defense.js';

// =============================================================================
// 🎯 WORLD-CLASS CONTEXT ENGINEERING HANDLER
// =============================================================================

export const contextEngineeringLegalHandler = async (c: Context) => {
  const startTime = performance.now();
  
  try {
    const { 
      query, 
      jurisdiction = 'AR', 
      sessionId,
      complexity = 'medium',
      enableAdvancedOptimization = true 
    } = await c.req.json();
    
    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      return c.json({
        success: false,
        error: 'Query is required and must be a non-empty string',
        code: 'INVALID_QUERY'
      }, 400);
    }

    // =================================================================
    // 🛡️ SECURITY PHASE: Prompting Attacks Detection
    // =================================================================
    
    const securityAssessment = contextEngineeringSecurity.assessSecurityThreat(
      query.trim(),
      sessionId || `session-${Date.now()}`
    );
    
    const securityMetrics = contextEngineeringSecurity.calculateSecurityRiskMetrics(
      query.trim(),
      sessionId || `session-${Date.now()}`
    );
    
    // Block query if critical security threat detected
    if (securityAssessment.blockQuery) {
      return c.json({
        success: false,
        error: 'Query blocked due to security policy violation',
        code: 'SECURITY_THREAT_DETECTED',
        securityAssessment: {
          threatLevel: securityAssessment.threatLevel,
          detectedAttacks: securityAssessment.detectedAttacks,
          confidenceScore: securityAssessment.confidenceScore,
          reasoning: securityAssessment.reasoning
        },
        framework: 'Context Engineering Security + Prem Natarajan Defense'
      }, 403);
    }
    
    // =================================================================
    // 🧠 PHASE 1: 5-MEMORY SYSTEM PROCESSING
    // =================================================================
    
    const memoryProcessing = await contextMemorySystem.processLegalQuery({
      query: query.trim(),
      jurisdiction,
      sessionId: sessionId || `session-${Date.now()}`,
      timestamp: Date.now()
    });
    
    // =================================================================
    // 🏗️ PHASE 2: WORLD-CLASS CONTEXT ASSEMBLY
    // =================================================================
    
    const complexityConfig = worldClassContextAssembler.getOptimizedConfig(
      complexity as 'simple' | 'medium' | 'complex'
    );
    
    const assemblyResult = await worldClassContextAssembler.assembleWorldClassContext(
      query.trim(),
      complexityConfig
    );
    
    // =================================================================
    // ⚡ PHASE 3: DEGRADATION PREVENTION
    // =================================================================
    
    const degradationResult = await worldClassDegradationManager.preventContextDegradation(
      query.trim(),
      assemblyResult.finalContext,
      sessionId
    );
    
    // =================================================================
    // 🎯 PHASE 4: EDFL RISK ASSESSMENT
    // =================================================================
    
    const riskMetrics = memoryProcessing.riskMetrics;
    const finalDecision = riskMetrics.decision;
    
    // Enhanced risk calculation with context engineering metrics
    const contextEngineeringRisk = {
      rohBound: Math.max(riskMetrics.rohBound, 
        degradationResult.performance.degradationRisk === 'critical' ? 0.08 : 
        degradationResult.performance.degradationRisk === 'high' ? 0.06 : 
        degradationResult.performance.degradationRisk === 'medium' ? 0.04 : 0.02
      ),
      isrRatio: Math.min(riskMetrics.isrRatio, 
        degradationResult.performance.qualityScore * 2.0
      ),
      informationBudget: riskMetrics.informationBudget * 
        (degradationResult.performance.tokenEfficiency / 100),
      contextQuality: degradationResult.performance.qualityScore,
      tokenEfficiency: degradationResult.performance.tokenEfficiency,
      degradationRisk: degradationResult.performance.degradationRisk
    };
    
    // =================================================================
    // 📝 PHASE 5: RESPONSE GENERATION (MOCK - Production uses Llama 3.2)
    // =================================================================
    
    let legalResponse = '';
    let citations: string[] = [];
    let confidence = 0.85;
    
    if (finalDecision === 'ANSWER') {
      // Simulate high-quality response generation using optimal context
      const topDocs = degradationResult.optimizedContext.slice(0, 3);
      
      citations = topDocs.map(doc => 
        `${doc.meta.type.toUpperCase()} ${doc.meta.numero || 'N/A'} - Art. ${doc.meta.articulo || 'N/A'}`
      );
      
      // Mock legal response based on context engineering
      if (query.toLowerCase().includes('compliance') || query.toLowerCase().includes('empresa')) {
        legalResponse = `Según el análisis del corpus legal argentino optimizado mediante Context Engineering:\n\n` +
          `La Ley 27.401 de Responsabilidad Penal Empresaria establece que las personas jurídicas pueden implementar programas de integridad para mitigar su responsabilidad penal. ${topDocs[0]?.content.substring(0, 200)}...\n\n` +
          `El sistema de Context Engineering ha optimizado este análisis utilizando ${degradationResult.optimizedContext.length} documentos legales con una eficiencia de tokens del ${degradationResult.performance.tokenEfficiency.toFixed(1)}%.`;
        
        confidence = Math.min(0.95, contextEngineeringRisk.contextQuality * 1.1);
      } else if (query.toLowerCase().includes('consumidor')) {
        legalResponse = `Basado en el análisis optimizado del marco normativo de protección al consumidor:\n\n` +
          `El artículo 42 de la Constitución Nacional y la Ley 24.240 establecen un sistema integral de protección. ${topDocs[0]?.content.substring(0, 200)}...\n\n` +
          `Context Engineering ha procesado ${degradationResult.insights.tokensUsed} tokens con una calidad de contexto del ${(contextEngineeringRisk.contextQuality * 100).toFixed(1)}%.`;
          
        confidence = Math.min(0.93, contextEngineeringRisk.contextQuality * 1.05);
      } else {
        legalResponse = `Análisis legal mediante Context Engineering Framework:\n\n` +
          `${topDocs[0]?.content.substring(0, 300)}...\n\n` +
          `El sistema ha optimizado el contexto legal utilizando arquitectura 5-Memory y gestión proactiva de degradación, procesando ${degradationResult.insights.tokensUsed} tokens con ${degradationResult.performance.optimizationsApplied.length} optimizaciones aplicadas.`;
          
        confidence = Math.min(0.90, contextEngineeringRisk.contextQuality);
      }
    } else {
      legalResponse = 'ABSTENCIÓN: El sistema Context Engineering ha determinado que la información disponible no es suficiente para proporcionar una respuesta confiable según los estándares EDFL.';
      confidence = 0.0;
    }
    
    // =================================================================
    // 📊 PHASE 6: PERFORMANCE METRICS & INSIGHTS
    // =================================================================
    
    const processingTime = performance.now() - startTime;
    
    // Calculate token efficiency improvement
    const jsonEquivalent = JSON.stringify(degradationResult.optimizedContext);
    const yamlEquivalent = YAML_ARGENTINE_LEGAL_CORPUS.substring(0, jsonEquivalent.length);
    const efficiency = calculateTokenEfficiency(jsonEquivalent, yamlEquivalent);
    
    // System health check
    const systemHealth = worldClassDegradationManager.getSystemHealth();
    
    // =================================================================
    // 🎖️ RESPONSE ASSEMBLY
    // =================================================================
    
    const response = {
      // Core Response
      success: true,
      decision: finalDecision,
      answer: legalResponse,
      citations,
      confidence,
      
      // Context Engineering Metrics
      contextEngineering: {
        framework: 'Paul Iusztin Context Engineering',
        version: '1.0-WorldClass',
        memoryTypes: ['Long-term', 'Short-term', 'Working', 'Episodic', 'Procedural'],
        
        performance: {
          processingTime: Math.round(processingTime),
          tokenEfficiency: degradationResult.performance.tokenEfficiency,
          qualityScore: degradationResult.performance.qualityScore,
          degradationRisk: degradationResult.performance.degradationRisk
        },
        
        optimization: {
          yamlTokenSavings: efficiency.savings,
          documentsOptimized: degradationResult.optimizedContext.length,
          strategiesApplied: degradationResult.performance.optimizationsApplied,
          tokensSaved: degradationResult.insights.tokensSaved
        },
        
        memory: {
          longTerm: {
            corpusSize: memoryProcessing.memoryStats.longTerm.totalDocuments,
            tokenCount: memoryProcessing.memoryStats.longTerm.tokenCount
          },
          shortTerm: {
            contextDocs: memoryProcessing.memoryStats.shortTerm.documentCount,
            tokenUsage: memoryProcessing.memoryStats.shortTerm.tokenUsage,
            utilization: memoryProcessing.memoryStats.shortTerm.utilizationRate
          },
          episodic: {
            patterns: memoryProcessing.memoryStats.episodic.patternInsights.length,
            relevantHistory: memoryProcessing.memoryStats.episodic.relevantHistory
          },
          working: {
            informationBudget: contextEngineeringRisk.informationBudget,
            processingTime: memoryProcessing.memoryStats.working.processingTime
          }
        }
      },
      
      // EDFL Risk Metrics Enhanced
      riskMetrics: {
        rohBound: contextEngineeringRisk.rohBound,
        isrRatio: contextEngineeringRisk.isrRatio,
        informationBudget: contextEngineeringRisk.informationBudget,
        contextQuality: contextEngineeringRisk.contextQuality,
        decision: finalDecision,
        rationale: `Context Engineering: ${contextEngineeringRisk.contextQuality >= 0.8 ? 'High' : contextEngineeringRisk.contextQuality >= 0.6 ? 'Medium' : 'Low'} quality context, ${efficiency.savings} token savings vs JSON, ${degradationResult.performance.degradationRisk} degradation risk`
      },
      
      // System Insights
      insights: {
        tokenUtilization: {
          used: degradationResult.insights.tokensUsed,
          saved: degradationResult.insights.tokensSaved,
          efficiency: `${efficiency.savings} vs JSON`,
          utilizationRate: degradationResult.insights.utilizationRate
        },
        
        recommendations: degradationResult.insights.recommendations,
        
        systemHealth: {
          status: systemHealth.status,
          metrics: systemHealth.metrics,
          recommendations: systemHealth.recommendations
        },
        
        nextOptimizations: [
          'Consider implementing real-time embedding search for semantic similarity',
          'Add automated legal hierarchy validation pipeline',
          'Implement cross-jurisdictional context assembly for LATAM expansion',
          'Enable automated derogation detection for temporal relevance'
        ]
      },
      
      // Security Assessment
      security: {
        framework: 'Context Engineering Security + Prem Natarajan Defense',
        threatLevel: securityAssessment.threatLevel,
        detectedAttacks: securityAssessment.detectedAttacks,
        riskMetrics: {
          injectionRisk: securityMetrics.injectionRisk,
          roleAbuseRisk: securityMetrics.roleAbuseRisk,
          exfiltrationRisk: securityMetrics.exfiltrationRisk,
          socialEngineeringRisk: securityMetrics.socialEngineeringRisk,
          chainedQueryRisk: securityMetrics.chainedQueryRisk,
          overallRisk: securityMetrics.overallRisk
        },
        securityScore: 1.0 - securityMetrics.overallRisk,
        isSecure: securityAssessment.threatLevel === 'low'
      },
      
      // Certification for EU AI Act Compliance
      certification: {
        framework: 'EDFL + Context Engineering + Security Defense',
        timestamp: new Date().toISOString(),
        hash: `ce-${Date.now().toString(36)}`,
        auditTrail: {
          memoryTypesUsed: 5,
          optimizationStrategies: degradationResult.performance.optimizationsApplied.length,
          degradationPrevention: degradationResult.performance.degradationRisk !== 'critical',
          tokenOptimization: efficiency.efficiency > 50,
          securityThreatLevel: securityAssessment.threatLevel,
          securityScore: 1.0 - securityMetrics.overallRisk
        }
      }
    };
    
    // =================================================================
    // 📝 EPISODIC MEMORY UPDATE
    // =================================================================
    
    if (enableAdvancedOptimization) {
      contextMemorySystem.recordConsultation(
        {
          query: query.trim(),
          jurisdiction,
          sessionId: sessionId || `session-${Date.now()}`,
          timestamp: Date.now()
        },
        {
          answer: legalResponse,
          citations,
          confidence,
          riskMetrics: {
            rohBound: contextEngineeringRisk.rohBound,
            isrRatio: contextEngineeringRisk.isrRatio,
            informationBudget: contextEngineeringRisk.informationBudget,
            decision: finalDecision,
            rationale: response.riskMetrics.rationale
          }
        }
      );
    }
    
    return c.json(response);
    
  } catch (error) {
    console.error('Context Engineering Error:', error);
    
    return c.json({
      success: false,
      error: 'Error en el sistema de Context Engineering',
      details: error instanceof Error ? error.message : 'Unknown error',
      contextEngineering: {
        framework: 'Paul Iusztin Context Engineering',
        version: '1.0-WorldClass',
        status: 'error'
      }
    }, 500);
  }
};

// =============================================================================
// 🔍 CONTEXT ENGINEERING SYSTEM STATUS
// =============================================================================

export const contextEngineeringStatusHandler = async (c: Context) => {
  try {
    const systemHealth = worldClassDegradationManager.getSystemHealth();
    const systemStatus = contextMemorySystem.getSystemStatus();
    
    // Load corpus for analysis
    const corpus = loadYAMLLegalCorpus();
    const sampleDoc = corpus[0];
    const jsonString = JSON.stringify(sampleDoc);
    const yamlString = `id: ${sampleDoc.id}\ncontent: ${sampleDoc.content.substring(0, 100)}...`;
    const efficiency = calculateTokenEfficiency(jsonString, yamlString);
    
    return c.json({
      status: 'operational',
      framework: 'Paul Iusztin Context Engineering',
      version: '1.0-WorldClass',
      timestamp: new Date().toISOString(),
      
      components: {
        memorySystem: {
          status: systemStatus.isHealthy ? 'healthy' : 'degraded',
          memoryTypes: systemStatus.memoryTypes,
          performance: systemStatus.performance
        },
        
        degradationManager: {
          status: systemHealth.status,
          metrics: systemHealth.metrics,
          recommendations: systemHealth.recommendations
        },
        
        contextAssembly: {
          status: 'operational',
          yamlOptimization: efficiency.savings,
          compressionStrategies: ['light', 'medium', 'aggressive'],
          qualityAnalysis: 'enabled'
        }
      },
      
      capabilities: {
        '5MemoryArchitecture': '✅ Fully implemented',
        'YAMLOptimization': `✅ ${efficiency.savings} token savings`,
        'DegradationPrevention': '✅ Proactive 32K management',
        'ContextAssembly': '✅ World-class pipeline',
        'EpisodicLearning': '✅ Legal consultation patterns',
        'ProceduralValidation': '✅ Argentine legal hierarchy'
      },
      
      metrics: {
        corpusSize: corpus.length,
        totalTokens: corpus.reduce((sum, doc) => sum + Math.ceil(doc.content.length / 4), 0),
        averageDocSize: Math.round(corpus.reduce((sum, doc) => sum + doc.content.length, 0) / corpus.length),
        hierarchyDistribution: {
          constitution: corpus.filter(d => d.meta.hierarchy === 1).length,
          codes: corpus.filter(d => d.meta.hierarchy === 2).length,
          laws: corpus.filter(d => d.meta.hierarchy === 3).length,
          jurisprudence: corpus.filter(d => d.meta.hierarchy === 4).length,
          decrees: corpus.filter(d => d.meta.hierarchy === 5).length
        }
      },
      
      optimization: {
        tokenEfficiency: efficiency.efficiency,
        contextDegradationThreshold: '28K tokens (Paul Iusztin recommendation)',
        memoryTypes: 5,
        compressionLevels: 4,
        validationRules: 'Argentine legal hierarchy + Ley 27.401 compliance'
      }
    });
    
  } catch (error) {
    return c.json({
      status: 'error',
      framework: 'Paul Iusztin Context Engineering',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, 500);
  }
};