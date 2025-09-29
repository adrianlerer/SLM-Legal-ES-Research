/**
 * Self-RAG implementation with province-aware retrieval for Argentina
 * Integrates jurisdiction classification + province router + citation enforcer
 */

import { retrieveProvinceAware } from "../retrieval/province_router";
import { classifyJurisdictionHint, classifyJurisdictionAdvanced } from "./jurisdiction_classify";
import { enforceCitations } from "../../tools/citation_enforcer";

export interface SelfRAGPlan {
  needRetrieve: boolean;
  type: "article" | "jurisprudence" | "legislation" | "general";
  jurisdiction: string;
  confidence: number;
  alternatives?: Array<{ jurisdiction: string; confidence: number }>;
}

export interface SelfRAGResult {
  plan: SelfRAGPlan;
  retrieved: any;
  draftAnswer: string;
  citationsOK: boolean;
  errors: string[];
  warnings?: string[];
  metadata: {
    jurisdictionTried: string[];
    retrievalHits: number;
    processingTimeMs: number;
  };
}

export async function runSelfRAG(userQuery: string, jurisdictionHint?: string): Promise<SelfRAGResult> {
  const startTime = Date.now();
  
  // 1. Planificación: ¿necesitamos recuperar información?
  const needRetrieve = shouldRetrieve(userQuery);
  const queryType = classifyQueryType(userQuery);
  
  // 2. Clasificación inteligente de jurisdicción
  let jurisdiction: string;
  let confidence: number;
  let alternatives: Array<{ jurisdiction: string; confidence: number }> = [];
  
  if (jurisdictionHint) {
    jurisdiction = jurisdictionHint;
    confidence = 0.95; // Alta confianza si viene como hint explícito
  } else {
    const classification = classifyJurisdictionAdvanced(userQuery);
    jurisdiction = classification.primary;
    confidence = classification.confidence;
    alternatives = classification.alternatives;
  }
  
  const plan: SelfRAGPlan = {
    needRetrieve,
    type: queryType,
    jurisdiction,
    confidence,
    alternatives
  };
  
  // 3. Recuperación province-aware (si es necesaria)
  let retrieved: any = { jurisdictionTried: [], hits: [] };
  if (needRetrieve) {
    retrieved = await retrieveProvinceAware(userQuery, jurisdiction as any);
  }
  
  // 4. Generación de respuesta draft
  const draftAnswer = await generateDraftAnswer(userQuery, retrieved, jurisdiction);
  
  // 5. Validación de citas con enforcer
  const citationResult = enforceCitations(draftAnswer, jurisdiction);
  
  // 6. Compilar resultado final
  const result: SelfRAGResult = {
    plan,
    retrieved,
    draftAnswer,
    citationsOK: citationResult.ok,
    errors: citationResult.errors || [],
    warnings: citationResult.warnings,
    metadata: {
      jurisdictionTried: retrieved.jurisdictionTried || [],
      retrievalHits: retrieved.hits?.length || 0,
      processingTimeMs: Date.now() - startTime
    }
  };
  
  return result;
}

/**
 * Determina si la consulta requiere recuperación de información externa
 */
function shouldRetrieve(query: string): boolean {
  const q = query.toLowerCase();
  
  // Siempre recuperar si menciona normativa específica
  if (/\b(ley|decreto|resolución|código|artículo|reglamento)\b/.test(q)) return true;
  
  // Recuperar para consultas sobre procedimientos legales
  if (/\b(cómo|qué dice|cuál es|según|de acuerdo|establece)\b/.test(q)) return true;
  
  // No recuperar para consultas muy generales o definiciones básicas
  if (/\b(qué es|define|concepto de)\b/.test(q) && q.split(' ').length < 5) return false;
  
  // Default: recuperar para mayor precisión
  return true;
}

/**
 * Clasifica el tipo de consulta para optimizar la búsqueda
 */
function classifyQueryType(query: string): "article" | "jurisprudence" | "legislation" | "general" {
  const q = query.toLowerCase();
  
  if (/\b(fallos|jurisprudencia|sentencia|tribunal|corte|ministro)\b/.test(q)) return "jurisprudence";
  if (/\b(ley|decreto|resolución|reglamento|código)\b/.test(q)) return "legislation";
  if (/\b(artículo|art\.|cap\.|capítulo|sección|secc\.)\b/.test(q)) return "article";
  
  return "general";
}

/**
 * Genera respuesta draft basada en información recuperada
 * TODO: integrar con LLM real (GPT-4, Claude, Llama, etc.)
 */
async function generateDraftAnswer(query: string, retrieved: any, jurisdiction: string): Promise<string> {
  // STUB: reemplazar por llamada a LLM real
  const hits = retrieved.hits || [];
  const jurisdictionName = getJurisdictionDisplayName(jurisdiction);
  
  if (hits.length === 0) {
    return `Borrador de respuesta para "${query}" (jurisdicción: ${jurisdictionName}). ` +
           `No se encontraron referencias específicas en los índices consultados. ` +
           `TODO: integrar con LLM real para generar respuesta completa con citas obligatorias.`;
  }
  
  const hitsSummary = hits.slice(0, 3).map((h: any) => h.id).join(", ");
  return `Borrador basado en "${query}" (jurisdicción: ${jurisdictionName}). ` +
         `Fuentes consultadas: ${hitsSummary}. ` +
         `Art. 1º - TODO: integrar con LLM real para análisis completo. ` +
         `Según normativa aplicable en ${jurisdictionName}... ` +
         `TODO: generar citas pinpoint específicas y análisis detallado.`;
}

/**
 * Convierte código de jurisdicción a nombre legible
 */
function getJurisdictionDisplayName(jurisdiction: string): string {
  const names: Record<string, string> = {
    "AR": "Argentina (Nacional)",
    "AR-C": "Ciudad Autónoma de Buenos Aires",
    "AR-B": "Provincia de Buenos Aires",
    "AR-X": "Provincia de Córdoba",
    "AR-M": "Provincia de Mendoza",
    "AR-S": "Provincia de Santa Fe",
    "AR-Q": "Provincia del Neuquén",
    "AR-R": "Provincia de Río Negro",
    "ES": "España",
    "GLOBAL": "Global (ES-LatAm-EU)"
  };
  
  return names[jurisdiction] || jurisdiction;
}