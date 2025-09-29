/**
 * Citation Enforcer - Garantiza citas obligatorias con pinpoint en respuestas legales
 * Integra patrones argentinos y validación provincial específica
 */

import { AR_PATTERNS, validateArgentineCitation } from './citation_patterns_ar';
import { validateProvincePinpoint } from "./ar/pinpoint_by_province";

export interface CitationResult {
  ok: boolean;
  errors: string[];
  warnings?: string[];
  patterns?: string[];
}

export function enforceCitations(answer: string, jurisdictionHint?: string): CitationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Validación básica de longitud
  if (!answer || answer.trim().length < 10) {
    errors.push("Respuesta demasiado corta para contener citas válidas");
    return { ok: false, errors };
  }

  // Validación específica para jurisdicciones argentinas
  if (jurisdictionHint && jurisdictionHint.startsWith("AR")) {
    const argValidation = validateArgentineCitation(answer);
    
    if (!argValidation.valid) {
      errors.push("Falta cita válida según patrones argentinos (Ley/Decreto/Resolución/Fallos/Boletín + pinpoint)");
    }
    
    // Validación provincial específica si es una provincia
    if (jurisdictionHint !== "AR" && jurisdictionHint.length > 3) {
      const res = validateProvincePinpoint(answer, jurisdictionHint as any);
      if (!res.ok) {
        errors.push("Cita provincial AR incompleta (boletín + artículo/capítulo/sección).");
      } else {
        warnings.push(`Cita provincial válida: ${res.hits.join(", ")}`);
      }
    } else {
      // Verificar pinpoint genérico (Art./Cap./Secc.) para jurisdicción nacional
      const hasPinpoint = /Art\.?|Cap\.?|Secc\.?|Artículo|Capítulo|Sección/i.test(answer);
      if (!hasPinpoint) {
        errors.push("Falta pinpoint específico (Artículo/Capítulo/Sección)");
      }
    }
    
    return {
      ok: errors.length === 0,
      errors,
      warnings,
      patterns: argValidation.patterns
    };
  }

  // Validación genérica para otras jurisdicciones
  const hasGeneralCitation = /\b(art|artículo|ley|decreto|resolución|código)\b/i.test(answer);
  if (!hasGeneralCitation) {
    errors.push("Falta referencia legal específica");
  }

  return {
    ok: errors.length === 0,
    errors,
    warnings
  };
}