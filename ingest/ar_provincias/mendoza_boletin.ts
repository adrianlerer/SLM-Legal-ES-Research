/**
 * Provincia de Mendoza — Boletín Oficial (stub).
 * TODO: implementar fetch HTML con respeto de robots/ToS, rate-limit y cache local.
 * TODO: búsqueda por rango de fechas y texto; extraer tipo/número/fecha y enlaces a sumarios.
 * TODO: cargar schema/ar_boletines_map.json y usar url_base verificada para construir endpoints de búsqueda.
 */

// import boletinesMap from "../../schema/ar_boletines_map.json";

export async function searchMendoza(params:{from?:string; to?:string; texto?:string}){ 
  // TODO: const config = boletinesMap["AR-M"].MENDOZA;
  // TODO: const searchUrl = `${config.url_base}${config.search_endpoint}`;
  // TODO: implementar rate limiting: await sleep(config.rate_limit_ms);
  
  return { 
    jurisdiction:"AR-M", // Corregido a código ISO correcto
    items:[] 
  }; 
}