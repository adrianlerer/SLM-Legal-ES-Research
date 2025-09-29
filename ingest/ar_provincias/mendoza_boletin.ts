/**
 * Provincia de Mendoza — Boletín Oficial (stub).
 * TODO: implementar fetch HTML con respeto de robots/ToS, rate-limit y cache local.
 * TODO: búsqueda por rango de fechas y texto; extraer tipo/número/fecha y enlaces a sumarios.
 */
export async function searchMendoza(params:{from?:string; to?:string; texto?:string}){ 
  return { 
    jurisdiction:"AR-MZA", 
    items:[] 
  }; 
}