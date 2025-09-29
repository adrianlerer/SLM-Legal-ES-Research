/**
 * Normalización a formato ELI (European Legislation Identifier) extendido para Argentina
 * Soporte para jurisdicciones subnacionales ISO 3166-2:AR con alias automáticos
 */

import aliases from "./ar_iso_aliases.json";

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
  // Normalización automática de alias humanos a códigos ISO
  let j = input.jurisdiction || input.iso || "AR";
  const ha = aliases.human_alias as Record<string,string>;
  if (ha[j]) j = ha[j];
  
  const dateObj = input.date ? new Date(input.date) : new Date();
  
  return {
    jurisdiction: j,
    type: input.type || "unknown",
    year: dateObj.getFullYear().toString(),
    month: (dateObj.getMonth() + 1).toString().padStart(2, '0'),
    day: dateObj.getDate().toString().padStart(2, '0'),
    number: input.number || "",
    title: input.title || "",
    source: input.source || ""
  };
}