/**
 * Patrones de cita argentinos para guardrails de compliance
 * Detecta referencias legales estándar en Argentina (nacional y provincial)
 */

export const AR_PATTERNS = [
  /Ley\s(N[°º]\s*)?\d{2,5}(\.\d+)?/i,
  /Decreto\s\d{3,5}\/\d{4}/i,
  /Resoluci[óo]n(\sGeneral)?(\s[A-Z]+)?\s?\d{3,5}\/\d{4}/i,
  /Fallos:\s?\d{1,3}:\d{1,5}/i,
  /(BORA|BOCBA|PBA|C[óo]rdoba|Mendoza|Santa\sFe)[^\n]+(Art\.?|Cap\.?|Secc\.?)/i
];

export function validateArgentineCitation(text: string): { valid: boolean; patterns: string[] } {
  const foundPatterns: string[] = [];
  
  for (const pattern of AR_PATTERNS) {
    const matches = text.match(pattern);
    if (matches) {
      foundPatterns.push(matches[0]);
    }
  }
  
  return {
    valid: foundPatterns.length > 0,
    patterns: foundPatterns
  };
}