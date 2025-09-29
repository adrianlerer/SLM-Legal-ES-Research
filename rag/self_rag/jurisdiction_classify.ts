/**
 * Clasificación heurística de jurisdicción desde la query o metadatos (stub).
 * Prioriza AR-provincia si hay mención explícita (p.ej., "BOCBA", "Córdoba", "Mendoza").
 * TODO: mejorar con NER + diccionarios/aliases (schema/ar_iso_aliases.json).
 */

import aliases from "../../schema/ar_iso_aliases.json";

export interface JurisdictionHint {
  jurisdiction: string;
  confidence: number;
  matches: string[];
  method: 'explicit_mention' | 'bulletin_reference' | 'geographic_name' | 'default_fallback';
}

// Patrones específicos de boletines oficiales
const BULLETIN_PATTERNS = [
  { pattern: /\b(bocba|boletín oficial.*ciudad autónoma)\b/i, jurisdiction: "AR-C", confidence: 0.95 },
  { pattern: /\b(boletín oficial.*provincia de buenos aires|pba)\b/i, jurisdiction: "AR-B", confidence: 0.95 },
  { pattern: /\b(boletín oficial.*córdoba)\b/i, jurisdiction: "AR-X", confidence: 0.95 },
  { pattern: /\b(boletín oficial.*mendoza)\b/i, jurisdiction: "AR-M", confidence: 0.95 },
  { pattern: /\b(boletín oficial.*santa fe)\b/i, jurisdiction: "AR-S", confidence: 0.95 },
  { pattern: /\b(boletín oficial.*neuquén)\b/i, jurisdiction: "AR-Q", confidence: 0.95 },
  { pattern: /\b(boletín oficial.*río negro)\b/i, jurisdiction: "AR-R", confidence: 0.95 },
  { pattern: /\b(bora|boletín oficial.*república argentina)\b/i, jurisdiction: "AR", confidence: 0.90 }
];

// Patrones geográficos (menor confianza que referencias a boletines)
const GEOGRAPHIC_PATTERNS = [
  { pattern: /\b(caba|ciudad de buenos aires|capital federal)\b/i, jurisdiction: "AR-C", confidence: 0.80 },
  { pattern: /\b(provincia de buenos aires|gran buenos aires)\b/i, jurisdiction: "AR-B", confidence: 0.75 },
  { pattern: /\b(córdoba|cordoba)\b/i, jurisdiction: "AR-X", confidence: 0.70 },
  { pattern: /\b(mendoza)\b/i, jurisdiction: "AR-M", confidence: 0.70 },
  { pattern: /\b(santa fe)\b/i, jurisdiction: "AR-S", confidence: 0.70 },
  { pattern: /\b(neuquén|neuquen)\b/i, jurisdiction: "AR-Q", confidence: 0.70 },
  { pattern: /\b(río negro|rio negro|rionegro)\b/i, jurisdiction: "AR-R", confidence: 0.70 },
  { pattern: /\b(salta)\b/i, jurisdiction: "AR-A", confidence: 0.70 },
  { pattern: /\b(san juan)\b/i, jurisdiction: "AR-J", confidence: 0.70 },
  { pattern: /\b(san luis)\b/i, jurisdiction: "AR-D", confidence: 0.70 },
  { pattern: /\b(tucumán|tucuman)\b/i, jurisdiction: "AR-G", confidence: 0.70 }
];

// Patrones de códigos ISO explícitos
const ISO_PATTERNS = [
  { pattern: /\b(ar-c|ar_c)\b/i, jurisdiction: "AR-C", confidence: 0.95 },
  { pattern: /\b(ar-b|ar_b)\b/i, jurisdiction: "AR-B", confidence: 0.95 },
  { pattern: /\b(ar-x|ar_x)\b/i, jurisdiction: "AR-X", confidence: 0.95 },
  { pattern: /\b(ar-m|ar_m)\b/i, jurisdiction: "AR-M", confidence: 0.95 },
  { pattern: /\b(ar-s|ar_s)\b/i, jurisdiction: "AR-S", confidence: 0.95 }
];

/**
 * Clasificación simple (compatibilidad con prompt original)
 */
export function classifyJurisdictionHint(q: string): string {
  const result = classifyJurisdictionDetailed(q);
  return result.jurisdiction;
}

/**
 * Clasificación detallada con confianza y contexto
 */
export function classifyJurisdictionDetailed(q: string): JurisdictionHint {
  const ql = q.toLowerCase();
  
  // 1. Buscar referencias explícitas a boletines (mayor confianza)
  for (const { pattern, jurisdiction, confidence } of BULLETIN_PATTERNS) {
    const match = ql.match(pattern);
    if (match) {
      return {
        jurisdiction,
        confidence,
        matches: [match[0]],
        method: 'bulletin_reference'
      };
    }
  }

  // 2. Buscar códigos ISO explícitos
  for (const { pattern, jurisdiction, confidence } of ISO_PATTERNS) {
    const match = ql.match(pattern);
    if (match) {
      return {
        jurisdiction,
        confidence,
        matches: [match[0]],
        method: 'explicit_mention'
      };
    }
  }

  // 3. Buscar menciones geográficas (menor confianza)
  for (const { pattern, jurisdiction, confidence } of GEOGRAPHIC_PATTERNS) {
    const match = ql.match(pattern);
    if (match) {
      return {
        jurisdiction,
        confidence,
        matches: [match[0]],
        method: 'geographic_name'
      };
    }
  }

  // 4. Verificar alias desde schema (usando diccionario)
  const aliasEntries = Object.entries(aliases.human_alias);
  for (const [humanAlias, isoCode] of aliasEntries) {
    if (ql.includes(humanAlias.toLowerCase())) {
      return {
        jurisdiction: isoCode,
        confidence: 0.85,
        matches: [humanAlias],
        method: 'explicit_mention'
      };
    }
  }

  // 5. Default fallback - nacional argentino
  return {
    jurisdiction: "AR",
    confidence: 0.50,
    matches: [],
    method: 'default_fallback'
  };
}

/**
 * Clasificación con múltiples jurisdicciones (para casos complejos)
 */
export function classifyMultipleJurisdictions(q: string): JurisdictionHint[] {
  const results: JurisdictionHint[] = [];
  const ql = q.toLowerCase();

  // Buscar todas las coincidencias posibles
  const allPatterns = [
    ...BULLETIN_PATTERNS.map(p => ({...p, method: 'bulletin_reference' as const})),
    ...ISO_PATTERNS.map(p => ({...p, method: 'explicit_mention' as const})),
    ...GEOGRAPHIC_PATTERNS.map(p => ({...p, method: 'geographic_name' as const}))
  ];

  for (const { pattern, jurisdiction, confidence, method } of allPatterns) {
    const match = ql.match(pattern);
    if (match) {
      // Evitar duplicados
      if (!results.some(r => r.jurisdiction === jurisdiction)) {
        results.push({
          jurisdiction,
          confidence,
          matches: [match[0]],
          method
        });
      }
    }
  }

  // Ordenar por confianza descendente
  return results.sort((a, b) => b.confidence - a.confidence);
}

/**
 * Validación de jurisdicción (verificar si es válida)
 */
export function isValidJurisdiction(j: string): boolean {
  const validCodes = Object.keys(aliases.iso_3166_2);
  const validAliases = Object.keys(aliases.human_alias);
  
  return validCodes.includes(j) || 
         validAliases.includes(j) || 
         j === "AR" || 
         j === "ES" || 
         j === "GLOBAL";
}