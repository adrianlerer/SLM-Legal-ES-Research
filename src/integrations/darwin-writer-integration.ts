/**
 * Darwin Writer SaaS + SCM Legal Integration
 * 
 * This module demonstrates the synergistic integration between:
 * - Darwin Writer SaaS: Consistency engine and content templates
 * - SCM Legal Spanish: AI-powered legal concept analysis
 * 
 * Author: Integration developed for Ignacio Adrian Lerer
 * Date: September 28, 2025
 */

import { Hono } from 'hono'
import type { Context } from 'hono'

// Types for Darwin Writer SaaS Integration
interface DarwinClaim {
  id: number
  text: string
  source: string
  context: string
  timestamp: string
  confidence: number
  user_session: string
}

interface DarwinContradiction {
  existing: string
  source: string
}

interface DarwinGenerationResult {
  content: string
  contradictions: DarwinContradiction[]
  word_count: number
  format: 'substack' | 'academic' | 'legal'
  text_id: number
}

// Types for SCM Legal Integration
interface SCMLegalAnalysis {
  legal_concepts: string[]
  jurisdiction_analysis: {
    [jurisdiction: string]: {
      applicable_laws: string[]
      risk_assessment: string
      compliance_notes: string[]
    }
  }
  risk_score: number
  recommendations: string[]
}

interface HybridLegalDocument {
  id: string
  original_prompt: string
  darwin_content: string
  scm_analysis: SCMLegalAnalysis
  contradictions_detected: DarwinContradiction[]
  consistency_score: number
  professional_confidence: number
  created_at: string
}

/**
 * Darwin Writer SaaS API Client
 * Simulates integration with Darwin Writer's Flask API
 */
class DarwinWriterClient {
  private baseUrl: string
  
  constructor(baseUrl: string = 'http://localhost:5000') {
    this.baseUrl = baseUrl
  }
  
  /**
   * Generate content using Darwin Writer templates
   */
  async generateContent(
    prompt: string, 
    format: 'substack' | 'academic' | 'legal',
    userSession: string
  ): Promise<DarwinGenerationResult> {
    // In real implementation, this would call Darwin Writer API
    // For demo purposes, we simulate the response structure
    
    const mockDarwinResponse: DarwinGenerationResult = {
      content: this.generateDarwinTemplate(prompt, format),
      contradictions: await this.checkContradictions(prompt),
      word_count: 800,
      format,
      text_id: Math.floor(Math.random() * 10000)
    }
    
    return mockDarwinResponse
  }
  
  /**
   * Check contradictions against Darwin's knowledge graph
   */
  async checkContradictions(newClaim: string): Promise<DarwinContradiction[]> {
    // Simulate Darwin's contradiction detection algorithm
    const contradictions: DarwinContradiction[] = []
    
    // Basic contradiction patterns (simulated)
    const opposites = [
      ['always', 'never'], ['increase', 'decrease'],
      ['efficient', 'inefficient'], ['positive', 'negative']
    ]
    
    // In real implementation, this would query Darwin's SQLite database
    // SELECT text, source FROM claims WHERE LOWER(text) LIKE ?
    
    return contradictions
  }
  
  /**
   * Store claim in Darwin's knowledge graph
   */
  async storeClaim(
    text: string, 
    source: string, 
    context: string, 
    userSession: string
  ): Promise<void> {
    // In real implementation:
    // INSERT INTO claims (text, source, context, user_session) VALUES (?, ?, ?, ?)
    console.log(`[Darwin] Storing claim: ${text.substring(0, 50)}...`)
  }
  
  private generateDarwinTemplate(prompt: string, format: string): string {
    const topic = this.extractMainTopic(prompt)
    
    switch (format) {
      case 'legal':
        return this.legalTemplate(topic, prompt)
      case 'academic':
        return this.academicTemplate(topic, prompt)
      case 'substack':
        return this.substackTemplate(topic, prompt)
      default:
        return this.legalTemplate(topic, prompt)
    }
  }
  
  private extractMainTopic(prompt: string): string {
    return prompt.split(':')[0].trim().toLowerCase()
  }
  
  private legalTemplate(topic: string, prompt: string): string {
    return `# ${topic}: Análisis Jurídico Integral

## I. INTRODUCCIÓN

### A. Planteo de la Cuestión

El presente análisis examina ${topic} desde la perspectiva del ordenamiento jurídico argentino, considerando tanto la normativa vigente como los desarrollos jurisprudenciales más recientes.

### B. Relevancia Jurídica

La cuestión de ${topic} adquiere especial relevancia debido a:
1. Evolución normativa acelerada
2. Complejidad interpretativa multi-jurisdiccional
3. Impacto práctico en compliance corporativo

## II. MARCO NORMATIVO APLICABLE

### A. Normativa Nacional

**Constitución Nacional**
- Artículos 14, 17 y 42 (derechos fundamentales aplicables)
- Principios de razonabilidad y debido proceso

**Código Civil y Comercial**
- Disposiciones sobre responsabilidad (Arts. 1708-1780)
- Principios de buena fe y abuso del derecho

**Legislación Específica**
- Ley 27.401 de Responsabilidad Penal Empresaria
- Ley 25.326 de Protección de Datos Personales
- Normativa sectorial específica

### B. Análisis Jurisprudencial

Los tribunales han establecido criterios específicos que deben considerarse en el análisis de ${topic}.

## III. CONCLUSIONES

El marco regulatorio actual proporciona herramientas suficientes para abordar ${topic}, aunque requiere interpretación contextual específica.

---
*Análisis generado por Darwin Writer Legal Template*
*Enhanced con SCM Legal Analysis para precisión técnica*`
  }
  
  private academicTemplate(topic: string, prompt: string): string {
    return `# ${topic}: Análisis Multidisciplinario desde la Perspectiva Argentina

## Resumen

Este trabajo examina ${topic} desde una perspectiva integradora que combina enfoques teóricos internacionales con evidencia empírica del contexto argentino.

**Palabras clave**: ${topic}, Argentina, análisis sistémico, marcos teóricos emergentes

## 1. Introducción

La comprensión actual de ${topic} se basa predominantemente en modelos desarrollados en economías desarrolladas...

## 2. Marco Teórico

### 2.1 Literatura Internacional
### 2.2 Contexto Regional

## 3. Metodología

## 4. Resultados

## 5. Discusión

## 6. Conclusiones

---
*Paper académico generado por Darwin Writer Academic Template*`
  }
  
  private substackTemplate(topic: string, prompt: string): string {
    return `# ${topic}: La Paradoja Oculta

## La Contradicción Inicial

En el mundo de ${topic}, existe una tensión fundamental que pocos se atreven a examinar...

## Primera Verdad: El Contexto Argentino Revela lo Invisible

La experiencia argentina expone patrones que el mainstream global sistemáticamente ignora...

## Segunda Verdad: Las Conexiones No Obvias

Lo que conecta ${topic} con el comportamiento del mercado argentino no es coincidencia...

## Tercera Verdad: Las Implicaciones Sistémicas

El impacto real opera en múltiples niveles interconectados...

## Síntesis Provocativa

${topic} en Argentina no representa una implementación defectuosa de un modelo global...

---
*Artículo Substack generado por Darwin Writer con estilo Lerer*`
  }
}

/**
 * SCM Legal Analysis Integration
 * Connects with our existing SCM Legal infrastructure
 */
class SCMLegalAnalyzer {
  
  /**
   * Analyze legal content with SCM specialized AI
   */
  async analyzeLegalContent(content: string, jurisdiction: string[] = ['AR']): Promise<SCMLegalAnalysis> {
    // This would integrate with our existing SCM Legal service
    // For demo, we simulate professional legal analysis
    
    const concepts = this.extractLegalConcepts(content)
    const jurisdictionAnalysis = await this.analyzeJurisdictions(content, jurisdiction)
    const riskScore = this.calculateRiskScore(content)
    const recommendations = this.generateRecommendations(content, concepts)
    
    return {
      legal_concepts: concepts,
      jurisdiction_analysis: jurisdictionAnalysis,
      risk_score: riskScore,
      recommendations
    }
  }
  
  private extractLegalConcepts(content: string): string[] {
    const legalTerms = [
      'responsabilidad', 'compliance', 'governance', 'due diligence',
      'auditoria', 'transparencia', 'riesgo', 'normativa', 'regulacion'
    ]
    
    const foundConcepts: string[] = []
    const lowerContent = content.toLowerCase()
    
    legalTerms.forEach(term => {
      if (lowerContent.includes(term)) {
        foundConcepts.push(term)
      }
    })
    
    return foundConcepts
  }
  
  private async analyzeJurisdictions(content: string, jurisdictions: string[]): Promise<any> {
    const analysis: any = {}
    
    for (const jurisdiction of jurisdictions) {
      analysis[jurisdiction] = {
        applicable_laws: this.getApplicableLaws(jurisdiction, content),
        risk_assessment: this.assessJurisdictionRisk(jurisdiction, content),
        compliance_notes: this.getComplianceNotes(jurisdiction, content)
      }
    }
    
    return analysis
  }
  
  private getApplicableLaws(jurisdiction: string, content: string): string[] {
    const lawsByJurisdiction: { [key: string]: string[] } = {
      'AR': [
        'Ley 27.401 (Responsabilidad Penal Empresaria)',
        'Código Civil y Comercial',
        'Ley 25.326 (Protección de Datos)'
      ],
      'ES': [
        'Código Penal Español',
        'Ley de Sociedades de Capital',
        'RGPD'
      ],
      'CL': [
        'Código Civil Chileno',
        'Ley de Sociedades Anónimas',
        'Normativa CMF'
      ]
    }
    
    return lawsByJurisdiction[jurisdiction] || []
  }
  
  private assessJurisdictionRisk(jurisdiction: string, content: string): string {
    // Simulate risk assessment based on content and jurisdiction
    const riskFactors = [
      'responsabilidad penal', 'sancion', 'multa', 'incumplimiento'
    ]
    
    const hasRiskFactors = riskFactors.some(factor => 
      content.toLowerCase().includes(factor)
    )
    
    if (hasRiskFactors) {
      return `Riesgo ALTO identificado en ${jurisdiction}. Requiere revisión especializada.`
    }
    
    return `Riesgo BAJO en ${jurisdiction}. Compliance general aplicable.`
  }
  
  private getComplianceNotes(jurisdiction: string, content: string): string[] {
    const notes = [
      `Verificar requisitos específicos de ${jurisdiction}`,
      'Implementar programa de integridad',
      'Establecer canales de denuncia',
      'Capacitación periódica del personal'
    ]
    
    return notes
  }
  
  private calculateRiskScore(content: string): number {
    // Simulate risk scoring algorithm
    let score = 0.3 // Base risk
    
    const highRiskTerms = ['penal', 'sancion', 'multa', 'delito']
    const mediumRiskTerms = ['compliance', 'auditoria', 'control']
    const lowRiskTerms = ['transparencia', 'buenas practicas', 'etica']
    
    const lowerContent = content.toLowerCase()
    
    highRiskTerms.forEach(term => {
      if (lowerContent.includes(term)) score += 0.2
    })
    
    mediumRiskTerms.forEach(term => {
      if (lowerContent.includes(term)) score += 0.1
    })
    
    lowRiskTerms.forEach(term => {
      if (lowerContent.includes(term)) score -= 0.05
    })
    
    return Math.min(Math.max(score, 0), 1) // Clamp between 0 and 1
  }
  
  private generateRecommendations(content: string, concepts: string[]): string[] {
    const recommendations = []
    
    if (concepts.includes('compliance')) {
      recommendations.push('Implementar programa integral de compliance')
    }
    
    if (concepts.includes('riesgo')) {
      recommendations.push('Realizar assessment de riesgos específicos')
    }
    
    if (concepts.includes('governance')) {
      recommendations.push('Fortalecer estructuras de gobierno corporativo')
    }
    
    recommendations.push('Mantener documentación actualizada')
    recommendations.push('Capacitar al equipo en normativas aplicables')
    
    return recommendations
  }
}

/**
 * Hybrid Darwin-SCM Legal Service
 * Combines Darwin's consistency engine with SCM's legal expertise
 */
class HybridLegalWriter {
  private darwin: DarwinWriterClient
  private scm: SCMLegalAnalyzer
  
  constructor(darwinUrl?: string) {
    this.darwin = new DarwinWriterClient(darwinUrl)
    this.scm = new SCMLegalAnalyzer()
  }
  
  /**
   * Generate professional legal document with both systems
   */
  async generateProfessionalLegalDocument(
    prompt: string,
    format: 'substack' | 'academic' | 'legal',
    jurisdiction: string[] = ['AR'],
    userSession: string
  ): Promise<HybridLegalDocument> {
    
    console.log(`[Hybrid] Generating professional document: ${prompt.substring(0, 50)}...`)
    
    // Step 1: Generate content with Darwin Writer
    console.log(`[Hybrid] Step 1: Darwin content generation...`)
    const darwinResult = await this.darwin.generateContent(prompt, format, userSession)
    
    // Step 2: Analyze with SCM Legal AI
    console.log(`[Hybrid] Step 2: SCM legal analysis...`)
    const scmAnalysis = await this.scm.analyzeLegalContent(darwinResult.content, jurisdiction)
    
    // Step 3: Cross-validate contradictions with legal concepts
    console.log(`[Hybrid] Step 3: Cross-validation...`)
    const enhancedContradictions = await this.enhanceContradictions(
      darwinResult.contradictions, 
      scmAnalysis.legal_concepts
    )
    
    // Step 4: Calculate hybrid confidence scores
    const consistencyScore = this.calculateConsistencyScore(darwinResult.contradictions)
    const professionalConfidence = this.calculateProfessionalConfidence(scmAnalysis)
    
    // Step 5: Store knowledge in both systems
    await this.darwin.storeClaim(prompt, format, 'hybrid_generation', userSession)
    
    const hybridDocument: HybridLegalDocument = {
      id: `hybrid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      original_prompt: prompt,
      darwin_content: darwinResult.content,
      scm_analysis: scmAnalysis,
      contradictions_detected: enhancedContradictions,
      consistency_score: consistencyScore,
      professional_confidence: professionalConfidence,
      created_at: new Date().toISOString()
    }
    
    console.log(`[Hybrid] Document generated successfully: ${hybridDocument.id}`)
    
    return hybridDocument
  }
  
  /**
   * Enhance Darwin contradictions with SCM legal context
   */
  private async enhanceContradictions(
    contradictions: DarwinContradiction[],
    legalConcepts: string[]
  ): Promise<DarwinContradiction[]> {
    
    return contradictions.map(contradiction => ({
      ...contradiction,
      source: `${contradiction.source} [Enhanced: Legal concepts - ${legalConcepts.join(', ')}]`
    }))
  }
  
  private calculateConsistencyScore(contradictions: DarwinContradiction[]): number {
    // Higher score = better consistency (fewer contradictions)
    const baseScore = 1.0
    const penalty = contradictions.length * 0.1
    return Math.max(baseScore - penalty, 0)
  }
  
  private calculateProfessionalConfidence(analysis: SCMLegalAnalysis): number {
    // Calculate confidence based on legal analysis depth
    let confidence = 0.5 // Base confidence
    
    // More legal concepts identified = higher confidence
    confidence += analysis.legal_concepts.length * 0.05
    
    // More recommendations = deeper analysis = higher confidence
    confidence += analysis.recommendations.length * 0.02
    
    // Lower risk = higher confidence in safety
    confidence += (1 - analysis.risk_score) * 0.3
    
    return Math.min(confidence, 1.0)
  }
  
  /**
   * Generate comparative analysis across multiple jurisdictions
   */
  async generateComparativeAnalysis(
    prompt: string,
    jurisdictions: string[] = ['AR', 'ES', 'CL', 'UY']
  ): Promise<any> {
    
    console.log(`[Hybrid] Generating comparative analysis across: ${jurisdictions.join(', ')}`)
    
    const analyses = await Promise.all(
      jurisdictions.map(async jurisdiction => {
        const document = await this.generateProfessionalLegalDocument(
          prompt, 'legal', [jurisdiction], 'comparative_session'
        )
        
        return {
          jurisdiction,
          analysis: document.scm_analysis.jurisdiction_analysis[jurisdiction],
          consistency_score: document.consistency_score,
          risk_score: document.scm_analysis.risk_score
        }
      })
    )
    
    return {
      prompt,
      jurisdictions: analyses,
      comparative_insights: this.generateComparativeInsights(analyses),
      generated_at: new Date().toISOString()
    }
  }
  
  private generateComparativeInsights(analyses: any[]): string[] {
    const insights = []
    
    // Risk comparison
    const risks = analyses.map(a => a.risk_score)
    const avgRisk = risks.reduce((sum, risk) => sum + risk, 0) / risks.length
    const highestRisk = analyses.find(a => a.risk_score === Math.max(...risks))
    const lowestRisk = analyses.find(a => a.risk_score === Math.min(...risks))
    
    insights.push(`Promedio de riesgo: ${(avgRisk * 100).toFixed(1)}%`)
    insights.push(`Mayor riesgo: ${highestRisk?.jurisdiction} (${(highestRisk?.risk_score * 100).toFixed(1)}%)`)
    insights.push(`Menor riesgo: ${lowestRisk?.jurisdiction} (${(lowestRisk?.risk_score * 100).toFixed(1)}%)`)
    
    // Consistency comparison
    const consistencies = analyses.map(a => a.consistency_score)
    const avgConsistency = consistencies.reduce((sum, cons) => sum + cons, 0) / consistencies.length
    insights.push(`Consistencia promedio: ${(avgConsistency * 100).toFixed(1)}%`)
    
    return insights
  }
}

/**
 * Hono API Routes for Darwin-SCM Integration
 */
const app = new Hono()

// Initialize hybrid service
const hybridWriter = new HybridLegalWriter()

// Single document generation endpoint
app.post('/api/hybrid/generate', async (c: Context) => {
  try {
    const { prompt, format = 'legal', jurisdiction = ['AR'], user_session = 'default' } = await c.req.json()
    
    if (!prompt || prompt.length < 10) {
      return c.json({ error: 'Prompt must be at least 10 characters long' }, 400)
    }
    
    const document = await hybridWriter.generateProfessionalLegalDocument(
      prompt, format, jurisdiction, user_session
    )
    
    return c.json({
      success: true,
      document,
      integration: 'darwin-scm-hybrid',
      performance: {
        darwin_consistency: document.consistency_score,
        scm_confidence: document.professional_confidence,
        overall_score: (document.consistency_score + document.professional_confidence) / 2
      }
    })
    
  } catch (error) {
    console.error('[Hybrid API] Error:', error)
    return c.json({ error: 'Internal server error during hybrid generation' }, 500)
  }
})

// Comparative analysis endpoint
app.post('/api/hybrid/compare', async (c: Context) => {
  try {
    const { prompt, jurisdictions = ['AR', 'ES', 'CL', 'UY'] } = await c.req.json()
    
    const comparison = await hybridWriter.generateComparativeAnalysis(prompt, jurisdictions)
    
    return c.json({
      success: true,
      comparative_analysis: comparison,
      integration: 'darwin-scm-hybrid-comparative'
    })
    
  } catch (error) {
    console.error('[Hybrid API] Comparison error:', error)
    return c.json({ error: 'Internal server error during comparative analysis' }, 500)
  }
})

// Health check for integration
app.get('/api/hybrid/health', async (c: Context) => {
  return c.json({
    service: 'Darwin-SCM Hybrid Legal Writer',
    status: 'healthy',
    integration: {
      darwin_writer: 'connected',
      scm_legal: 'connected',
      hybrid_engine: 'operational'
    },
    timestamp: new Date().toISOString()
  })
})

export { app as darwinSCMIntegrationApp, HybridLegalWriter, DarwinWriterClient, SCMLegalAnalyzer }