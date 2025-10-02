/**
 * Clasificación heurística de jurisdicción desde la query o metadatos (stub).
 * Prioriza AR-provincia si hay mención explícita (p.ej., "BOCBA", "Córdoba", "Mendoza").
 * TODO: mejorar con NER + diccionarios/aliases (schema/ar_iso_aliases.json).
 */

export function classifyJurisdictionHint(q: string): string {
  const ql = q.toLowerCase();
  
  // Detección específica por boletín oficial
  if (/\b(caba|bocba|ciudad de buenos aires|ciudad autónoma)\b/.test(ql)) return "AR-C";
  if (/\bprovincia de buenos aires|pba\b/.test(ql)) return "AR-B";
  
  // Detección por nombre de provincia
  if (/\bcordoba|córdoba\b/.test(ql)) return "AR-X";
  if (/\bmendoza\b/.test(ql)) return "AR-M";
  if (/\bsanta fe\b/.test(ql)) return "AR-S";
  if (/\bneuqu[eé]n\b/.test(ql)) return "AR-Q";
  if (/\br[ií]o negro\b/.test(ql)) return "AR-R";
  if (/\bsalta\b/.test(ql)) return "AR-A";
  if (/\bsan juan\b/.test(ql)) return "AR-J";
  if (/\bsan luis\b/.test(ql)) return "AR-D";
  if (/\btucum[aá]n\b/.test(ql)) return "AR-G";
  if (/\bchaco\b/.test(ql)) return "AR-H";
  if (/\bmisiones\b/.test(ql)) return "AR-N";
  if (/\bcorrientes\b/.test(ql)) return "AR-W";
  if (/\bentre r[ií]os\b/.test(ql)) return "AR-E";
  if (/\bformosa\b/.test(ql)) return "AR-P";
  if (/\bjujuy\b/.test(ql)) return "AR-Y";
  if (/\bla pampa\b/.test(ql)) return "AR-L";
  if (/\bla rioja\b/.test(ql)) return "AR-F";
  if (/\bcatamarca\b/.test(ql)) return "AR-K";
  if (/\bchubut\b/.test(ql)) return "AR-U";
  if (/\bsanta cruz\b/.test(ql)) return "AR-Z";
  if (/\bsantiago del estero\b/.test(ql)) return "AR-T";
  
  // Detección de jurisdicción nacional
  if (/\b(csjn|corte suprema|saij|bora|infoleg|naci[oó]n|nacional|federal)\b/.test(ql)) return "AR";
  
  // Detección de otras jurisdicciones
  if (/\b(españa|espa[ñn]a|madrid|barcelona|valencia)\b/.test(ql)) return "ES";
  
  // Default: jurisdicción nacional argentina
  return "AR";
}

/**
 * Clasificación avanzada con confianza y alternativas.
 * Retorna jurisdicción principal + score de confianza + alternativas posibles.
 */
export function classifyJurisdictionAdvanced(q: string): {
  primary: string;
  confidence: number;
  alternatives: Array<{ jurisdiction: string; confidence: number }>;
} {
  const ql = q.toLowerCase();
  const matches: Array<{ jurisdiction: string; pattern: string; weight: number }> = [];
  
  // Patrones con pesos (mayor peso = mayor confianza)
  const patterns = [
    // Boletines oficiales (peso alto)
    { pattern: /\b(bocba)\b/, jurisdiction: "AR-C", weight: 0.9 },
    { pattern: /\b(bora|boletín oficial.*república)\b/, jurisdiction: "AR", weight: 0.9 },
    
    // Provincias con contexto legal (peso medio-alto)
    { pattern: /\bcórdoba.*\b(ley|decreto|resolución)\b/, jurisdiction: "AR-X", weight: 0.8 },
    { pattern: /\bmendoza.*\b(ley|decreto|resolución)\b/, jurisdiction: "AR-M", weight: 0.8 },
    
    // Nombres de provincia simples (peso medio)
    { pattern: /\bcórdoba\b/, jurisdiction: "AR-X", weight: 0.6 },
    { pattern: /\bmendoza\b/, jurisdiction: "AR-M", weight: 0.6 },
    { pattern: /\bsanta fe\b/, jurisdiction: "AR-S", weight: 0.6 },
    
    // Instituciones nacionales (peso alto)
    { pattern: /\b(csjn|corte suprema)\b/, jurisdiction: "AR", weight: 0.85 },
    { pattern: /\b(saij|infoleg)\b/, jurisdiction: "AR", weight: 0.8 },
  ];
  
  // Evaluar todos los patrones
  for (const { pattern, jurisdiction, weight } of patterns) {
    if (pattern.test(ql)) {
      matches.push({ jurisdiction, pattern: pattern.source, weight });
    }
  }
  
  if (matches.length === 0) {
    return {
      primary: "AR",
      confidence: 0.3, // Baja confianza para default
      alternatives: [
        { jurisdiction: "ES", confidence: 0.2 },
        { jurisdiction: "GLOBAL", confidence: 0.1 }
      ]
    };
  }
  
  // Agrupar por jurisdicción y sumar pesos
  const scores: Record<string, number> = {};
  for (const match of matches) {
    scores[match.jurisdiction] = (scores[match.jurisdiction] || 0) + match.weight;
  }
  
  // Normalizar scores (max = 1.0)
  const maxScore = Math.max(...Object.values(scores));
  const normalizedScores = Object.entries(scores).map(([j, s]) => ({
    jurisdiction: j,
    confidence: s / maxScore
  }));
  
  // Ordenar por confianza
  normalizedScores.sort((a, b) => b.confidence - a.confidence);
  
  return {
    primary: normalizedScores[0].jurisdiction,
    confidence: normalizedScores[0].confidence,
    alternatives: normalizedScores.slice(1)
  };
}