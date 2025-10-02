import assert from "node:assert";
import { retrieveProvinceAware } from "../rag/retrieval/province_router.js";

(async () => {
  const q = "Consulta sobre contratación pública en CABA";
  const res = await retrieveProvinceAware(q, "AR-C");

  // Debe intentar provincia → AR → ES → GLOBAL (en ese orden)
  assert.ok(Array.isArray(res.jurisdictionTried) && res.jurisdictionTried.length >= 3, 
    "Debe intentar al menos 3 jurisdicciones");
  
  const tried = res.jurisdictionTried.join("|");
  assert.ok(tried.indexOf("idx_ar_caba") >= 0, "Debe intentar índice CABA");
  assert.ok(tried.indexOf("idx_ar_nacional") >= 0, "Debe intentar índice AR nacional");
  assert.ok(tried.indexOf("idx_es_espana") >= 0, "Debe intentar índice ES");
  assert.ok(tried.indexOf("idx_global_es_latam_eu") >= 0, "Debe intentar índice GLOBAL");
  assert.ok(res.hits.length > 0, "Debe retornar al menos un hit (stub)");

  console.log("✔ province_router: orden y hits OK");
})();