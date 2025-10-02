/**
 * Province-aware retrieval router (AR).
 * Selecciona índice según jurisdiction ISO 3166-2:AR (p.ej., "AR-C", "AR-B", "AR-X"...).
 * Fallback: índice nacional (AR) y luego índice ES-LatAm-EU general.
 * TODO: conectar con indexadores reales (GraphRAG y vectorial) cuando estén listos.
 */

export type Jurisdiction =
  | "AR" | "AR-C" | "AR-B" | "AR-K" | "AR-H" | "AR-U" | "AR-X" | "AR-W" | "AR-E" | "AR-P" | "AR-Y"
  | "AR-L" | "AR-F" | "AR-M" | "AR-N" | "AR-Q" | "AR-R" | "AR-A" | "AR-J" | "AR-D" | "AR-Z" | "AR-S" | "AR-T" | "AR-G";

export interface RetrievalHit { 
  id: string; 
  score: number; 
  meta?: Record<string, any>; 
}

export interface RetrievalResult { 
  jurisdictionTried: string[]; 
  hits: RetrievalHit[]; 
}

const INDEX_HANDLES: Record<string, string> = {
  "AR": "idx_ar_nacional",
  "AR-C": "idx_ar_caba",
  "AR-B": "idx_ar_pba",
  "AR-X": "idx_ar_cordoba",
  "AR-M": "idx_ar_mendoza",
  "AR-S": "idx_ar_santafe",
  // añadir más provincias cuando estén indexadas…
  "ES": "idx_es_espana",
  "GLOBAL": "idx_global_es_latam_eu"
};

async function searchIndex(indexHandle: string, query: string, k = 12): Promise<RetrievalHit[]> {
  // STUB: reemplazar por llamada a GraphRAG/query_graph + vectorial
  return [{ id: `${indexHandle}::stub`, score: 0.42, meta: { preview: query.slice(0, 60) } }];
}

/** Orden preferente para AR: provincia → nacional AR → ES → GLOBAL */
export async function retrieveProvinceAware(query: string, j: Jurisdiction): Promise<RetrievalResult> {
  const tried: string[] = [];
  const hits: RetrievalHit[] = [];

  const pushTry = async (handle: string) => {
    tried.push(handle);
    const r = await searchIndex(handle, query);
    if (r && r.length) hits.push(...r);
  };

  // 1) Provincia (si hay índice dedicado)
  if (INDEX_HANDLES[j]) await pushTry(INDEX_HANDLES[j]);

  // 2) Nacional AR
  await pushTry(INDEX_HANDLES["AR"]);

  // 3) España (apoya consultas en castellano con doctrina/códigos comparados)
  await pushTry(INDEX_HANDLES["ES"]);

  // 4) Global ES-LatAm-EU
  await pushTry(INDEX_HANDLES["GLOBAL"]);

  return { jurisdictionTried: tried, hits };
}