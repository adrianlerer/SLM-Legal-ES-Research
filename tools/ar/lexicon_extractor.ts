/**
 * Extrae fórmulas argentinas típicas:
 * Legislación: "VISTO", "CONSIDERANDO", "POR ELLO", "RESUELVE:", "ARTÍCULO [0-9]º", "Regístrese, comuníquese, publíquese..."
 * Judicial (CSJN/tribunales): "Considerando:", "Por ello, se resuelve:", "Voto del Sr./Sra. Ministro/a", "Fallos: <vol>:<pág>"
 * Devuelve lista de fórmulas y conteos (para prompts de estilo y features de reranking).
 */

export interface LexiconFormula {
  type: 'legislative' | 'judicial' | 'administrative';
  pattern: string;
  frequency: number;
  context?: string;
}

export interface LexiconExtraction {
  formulae: LexiconFormula[];
  counts: Record<string, number>;
  style_indicators: {
    is_legislative: boolean;
    is_judicial: boolean;
    is_administrative: boolean;
    confidence: number;
  };
}

// Patrones legislativos típicos argentinos
const LEGISLATIVE_PATTERNS = [
  /VISTO\s*:/i,
  /CONSIDERANDO\s*:/i,
  /POR\s+ELLO\s*:/i,
  /RESUELVE\s*:/i,
  /ARTÍCULO\s+\d+[°º]?\s*[.-]/i,
  /Regístrese,?\s*comuníquese,?\s*publíquese/i,
  /Dése\s+al?\s+Registro\s+Oficial/i
];

// Patrones judiciales típicos argentinos
const JUDICIAL_PATTERNS = [
  /Considerando\s*:/i,
  /Por\s+ello,?\s+se\s+resuelve\s*:/i,
  /Voto\s+del?\s+Sr\.?\/?Sra\.?\s+Ministro?\/a/i,
  /Fallos:\s*\d{1,3}:\d{1,5}/i,
  /Autos:\s*[""].*[""].*c\/.*[""].*s\/.*[""].*$/i,
  /En\s+Buenos\s+Aires,?.*de.*de.*\d{4}/i
];

// Patrones administrativos
const ADMINISTRATIVE_PATTERNS = [
  /Disposición\s+(N[°º])?\s*\d+\/\d{4}/i,
  /Instructivo\s+(N[°º])?\s*\d+\/\d{4}/i,
  /Circular\s+(N[°º])?\s*\d+\/\d{4}/i
];

export function extractFormulae(text: string): LexiconExtraction {
  const formulae: LexiconFormula[] = [];
  const counts: Record<string, number> = {};
  
  let legislativeCount = 0;
  let judicialCount = 0;
  let administrativeCount = 0;

  // Procesar patrones legislativos
  LEGISLATIVE_PATTERNS.forEach(pattern => {
    const matches = text.match(new RegExp(pattern.source, 'gi'));
    if (matches) {
      legislativeCount += matches.length;
      formulae.push({
        type: 'legislative',
        pattern: pattern.source,
        frequency: matches.length,
        context: matches[0]
      });
      counts[`legislative_${pattern.source}`] = matches.length;
    }
  });

  // Procesar patrones judiciales
  JUDICIAL_PATTERNS.forEach(pattern => {
    const matches = text.match(new RegExp(pattern.source, 'gi'));
    if (matches) {
      judicialCount += matches.length;
      formulae.push({
        type: 'judicial',
        pattern: pattern.source,
        frequency: matches.length,
        context: matches[0]
      });
      counts[`judicial_${pattern.source}`] = matches.length;
    }
  });

  // Procesar patrones administrativos
  ADMINISTRATIVE_PATTERNS.forEach(pattern => {
    const matches = text.match(new RegExp(pattern.source, 'gi'));
    if (matches) {
      administrativeCount += matches.length;
      formulae.push({
        type: 'administrative',
        pattern: pattern.source,
        frequency: matches.length,
        context: matches[0]
      });
      counts[`administrative_${pattern.source}`] = matches.length;
    }
  });

  // Determinar tipo dominante y confianza
  const total = legislativeCount + judicialCount + administrativeCount;
  const maxCount = Math.max(legislativeCount, judicialCount, administrativeCount);
  const confidence = total > 0 ? maxCount / total : 0;

  return {
    formulae,
    counts,
    style_indicators: {
      is_legislative: legislativeCount === maxCount && legislativeCount > 0,
      is_judicial: judicialCount === maxCount && judicialCount > 0,
      is_administrative: administrativeCount === maxCount && administrativeCount > 0,
      confidence
    }
  };
}