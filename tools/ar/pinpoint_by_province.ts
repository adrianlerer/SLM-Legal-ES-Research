/**
 * Verificador de 'pinpoint' por jurisdicción AR (ISO 3166-2).
 * Objetivo: detectar referencias con artículo/capítulo/sección o identificador oficial.
 * TODO: afinar patrones con casos reales de cada boletín.
 */

export type ProvinceCode =
  | "AR-C" | "AR-B" | "AR-K" | "AR-H" | "AR-U" | "AR-X" | "AR-W" | "AR-E" | "AR-P" | "AR-Y"
  | "AR-L" | "AR-F" | "AR-M" | "AR-N" | "AR-Q" | "AR-R" | "AR-A" | "AR-J" | "AR-D" | "AR-Z"
  | "AR-S" | "AR-T" | "AR-G";

const ART = /(Art\.?|Artículo)\s?\d+[º°]?/i;
const CAP = /(Cap\.?|Capítulo)\s?[IVXLC]+/i;
const SECC = /(Secc\.?|Sección)\s?[\w\.]+/i;

// Patrones por boletín/denominación usual. Añada más a medida que integre fetchers.
const PATTERNS: Record<ProvinceCode, RegExp[]> = {
  "AR-C": [/(BOCBA|Bolet[ií]n Oficial.*Ciudad Aut[oó]noma)/i, ART, CAP, SECC],
  "AR-B": [/(Bolet[ií]n Oficial.*Provincia de Buenos Aires|PBA)/i, ART, CAP, SECC],
  "AR-K": [/(Bolet[ií]n Oficial.*Catamarca)/i, ART],
  "AR-H": [/(Bolet[ií]n Oficial.*Chaco)/i, ART],
  "AR-U": [/(Bolet[ií]n Oficial.*Chubut)/i, ART],
  "AR-X": [/(Bolet[ií]n Oficial.*C[oó]rdoba)/i, ART, CAP, SECC],
  "AR-W": [/(Bolet[ií]n Oficial.*Corrientes)/i, ART],
  "AR-E": [/(Bolet[ií]n Oficial.*Entre R[ií]os)/i, ART],
  "AR-P": [/(Bolet[ií]n Oficial.*Formosa)/i, ART],
  "AR-Y": [/(Bolet[ií]n Oficial.*Jujuy)/i, ART],
  "AR-L": [/(Bolet[ií]n Oficial.*La Pampa)/i, ART],
  "AR-F": [/(Bolet[ií]n Oficial.*La Rioja)/i, ART],
  "AR-M": [/(Bolet[ií]n Oficial.*Mendoza)/i, ART, CAP],
  "AR-N": [/(Bolet[ií]n Oficial.*Misiones)/i, ART],
  "AR-Q": [/(Bolet[ií]n Oficial.*Neuqu[eé]n)/i, ART, CAP],
  "AR-R": [/(Bolet[ií]n Oficial.*R[ií]o Negro)/i, ART],
  "AR-A": [/(Bolet[ií]n Oficial.*Salta)/i, ART],
  "AR-J": [/(Bolet[ií]n Oficial.*San Juan)/i, ART],
  "AR-D": [/(Bolet[ií]n Oficial.*San Luis)/i, ART],
  "AR-Z": [/(Bolet[ií]n Oficial.*Santa Cruz)/i, ART],
  "AR-S": [/(Bolet[ií]n Oficial.*Santa Fe)/i, ART, CAP],
  "AR-T": [/(Bolet[ií]n Oficial.*Santiago del Estero)/i, ART],
  "AR-G": [/(Bolet[ií]n Oficial.*Tucum[aá]n)/i, ART]
};

export function validateProvincePinpoint(answer: string, province: ProvinceCode): { ok: boolean; hits: string[] } {
  const pats = PATTERNS[province] || [];
  const hits: string[] = [];
  for (const rx of pats) {
    const m = answer.match(rx);
    if (m) hits.push(m[0]);
  }
  // Aprobamos si hay mención al boletín + al menos un pinpoint (art/cap/secc)
  const hasBoletin = pats.length > 0 ? !!(answer.match(pats[0])) : false;
  const hasPinpoint = [ART, CAP, SECC].some(rx => rx.test(answer));
  return { ok: hasBoletin && hasPinpoint, hits };
}