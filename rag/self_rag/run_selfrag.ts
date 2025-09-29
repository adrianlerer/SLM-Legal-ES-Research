/**
 * Self-RAG integrado con province-aware retrieval y clasificación de jurisdicción
 * Implementa decisión inteligente de recuperación y validación de citas
 */

import { retrieveProvinceAware, type Jurisdiction } from "../retrieval/province_router";
import { classifyJurisdictionDetailed, type JurisdictionHint } from "./jurisdiction_classify";
import { enforceCitations } from "../../tools/citation_enforcer";

export interface SelfRAGPlan {
  needRetrieve: boolean;
  type: 'article' | 'precedent' | 'regulation' | 'mixed';
  jurisdiction: string;
  confidence: number;
  retrievalStrategy: 'province_specific' | 'national_fallback' | 'comparative_law';
}

export interface SelfRAGResult {
  plan: SelfRAGPlan;
  jurisdictionHint: JurisdictionHint;
  retrieved: {
    jurisdictionTried: string[];
    hits: Array<{
      id: string;
      score: number;
      meta?: Record<string, any>;
    }>;
  };
  draftAnswer: string;
  citationsOK: boolean;
  errors: string[];
  finalAnswer?: string;
}

/**
 * Determina si la consulta requiere recuperación de documentos
 */
function needsRetrieval(userQuery: string): { needed: boolean; type: SelfRAGPlan['type'] } {
  const q = userQuery.toLowerCase();
  
  // Patrones que requieren documentos específicos
  if (/\b(ley|decreto|resolución|artículo|código)\b/i.test(q)) {
    return { needed: true, type: 'regulation' };
  }
  
  if (/\b(fallos|jurisprudencia|precedente|sentencia)\b/i.test(q)) {
    return { needed: true, type: 'precedent' };
  }
  
  if (/\b(boletín|oficial|publicación)\b/i.test(q)) {
    return { needed: true, type: 'article' };
  }
  
  // Consultas conceptuales pueden requerir múltiples tipos
  if (/\b(criterios|lineamientos|interpretación|análisis)\b/i.test(q)) {
    return { needed: true, type: 'mixed' };
  }
  
  return { needed: true, type: 'mixed' }; // Por defecto, siempre recuperar
}

/**
 * Determina estrategia de recuperación basada en jurisdicción y tipo de consulta
 */
function determineRetrievalStrategy(
  jurisdiction: string, 
  confidence: number, 
  queryType: SelfRAGPlan['type']
): SelfRAGPlan['retrievalStrategy'] {
  
  // Alta confianza en provincia específica
  if (confidence > 0.85 && jurisdiction.startsWith('AR-') && jurisdiction !== 'AR') {
    return 'province_specific';
  }
  
  // Confianza media o consulta nacional
  if (jurisdiction === 'AR' || confidence > 0.70) {
    return 'national_fallback';
  }
  
  // Baja confianza o consultas comparativas
  return 'comparative_law';
}

/**
 * Genera borrador de respuesta (stub - TODO: integrar LLM real)
 */
async function generateDraftAnswer(
  userQuery: string, 
  retrievedDocs: SelfRAGResult['retrieved'], 
  plan: SelfRAGPlan
): Promise<string> {
  
  // STUB: En implementación real, aquí iría la llamada al LLM
  // con el contexto recuperado y las instrucciones específicas por jurisdicción
  
  const jurisdictionContext = plan.jurisdiction.startsWith('AR-') 
    ? `En el ámbito de ${plan.jurisdiction}, según documentos consultados`
    : 'Conforme a la normativa aplicable';
  
  const docReferences = retrievedDocs.hits
    .slice(0, 3)
    .map(hit => `${hit.id} (score: ${hit.score.toFixed(2)})`)
    .join(', ');
  
  return `${jurisdictionContext}, y considerando los documentos relevantes (${docReferences}), se puede establecer que:

[BORRADOR] - Esta sección requiere integración con LLM para generar respuesta completa basada en:
- Query: ${userQuery}
- Jurisdicción: ${plan.jurisdiction} (confianza: ${plan.confidence})
- Documentos recuperados: ${retrievedDocs.hits.length}
- Estrategia: ${plan.retrievalStrategy}

TODO: Implementar generación real con contexto de documentos recuperados y patrones específicos de la jurisdicción argentina.`;
}

/**
 * Función principal de Self-RAG
 */
export async function runSelfRAG(
  userQuery: string, 
  jurisdictionHint?: string
): Promise<SelfRAGResult> {
  
  // 1. Clasificar jurisdicción (usar hint o clasificar automáticamente)
  const jHint = jurisdictionHint 
    ? { jurisdiction: jurisdictionHint, confidence: 1.0, matches: ['manual'], method: 'explicit_mention' as const }
    : classifyJurisdictionDetailed(userQuery);
  
  // 2. Determinar plan de recuperación
  const retrievalNeeds = needsRetrieval(userQuery);
  const plan: SelfRAGPlan = {
    needRetrieve: retrievalNeeds.needed,
    type: retrievalNeeds.type,
    jurisdiction: jHint.jurisdiction,
    confidence: jHint.confidence,
    retrievalStrategy: determineRetrievalStrategy(jHint.jurisdiction, jHint.confidence, retrievalNeeds.type)
  };
  
  let retrieved = { jurisdictionTried: [], hits: [] };
  
  // 3. Ejecutar recuperación si es necesaria
  if (plan.needRetrieve) {
    try {
      retrieved = await retrieveProvinceAware(userQuery, plan.jurisdiction as Jurisdiction);
    } catch (error) {
      console.error('Error en retrieveProvinceAware:', error);
      // Continuar con retrieval vacío en caso de error
    }
  }
  
  // 4. Generar borrador de respuesta
  const draftAnswer = await generateDraftAnswer(userQuery, retrieved, plan);
  
  // 5. Validar citas y compliance
  const citationResult = enforceCitations(draftAnswer, plan.jurisdiction);
  
  // 6. Decidir si el borrador es aceptable o necesita refinamiento
  const shouldRefine = !citationResult.ok || retrieved.hits.length === 0;
  
  return {
    plan,
    jurisdictionHint: jHint,
    retrieved,
    draftAnswer,
    citationsOK: citationResult.ok,
    errors: citationResult.errors || [],
    finalAnswer: shouldRefine ? undefined : draftAnswer
  };
}

/**
 * Versión simplificada para casos de uso básicos
 */
export async function askLegalQuestion(
  question: string, 
  jurisdiction?: string
): Promise<{ answer: string; sources: string[]; confidence: number }> {
  
  const result = await runSelfRAG(question, jurisdiction);
  
  return {
    answer: result.finalAnswer || result.draftAnswer,
    sources: result.retrieved.jurisdictionTried,
    confidence: result.plan.confidence
  };
}