/**
 * Normalización a formato ELI (European Legislation Identifier) extendido para Argentina
 * Soporte para jurisdicciones subnacionales ISO 3166-2:AR
 */

export interface ELIDocument {
  jurisdiction: string;
  type: string;
  year: string;
  month?: string;
  day?: string;
  number?: string;
  title?: string;
  source?: string;
}

export function normalizeToELI(input: {
  jurisdiction?: string;
  iso?: string;
  type?: string;
  date?: string;
  number?: string;
  title?: string;
  source?: string;
}): ELIDocument {
  // Soporte subnacional con mapeo de alias
  const jurisdiction = input.jurisdiction || input.iso || "AR";
  
  const dateObj = input.date ? new Date(input.date) : new Date();
  
  return {
    jurisdiction,
    type: input.type || "unknown",
    year: dateObj.getFullYear().toString(),
    month: (dateObj.getMonth() + 1).toString().padStart(2, '0'),
    day: dateObj.getDate().toString().padStart(2, '0'),
    number: input.number || "",
    title: input.title || "",
    source: input.source || ""
  };
}