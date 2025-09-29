import assert from "node:assert";
import { classifyJurisdictionHint, classifyJurisdictionAdvanced } from "../rag/self_rag/jurisdiction_classify.js";

(() => {
  // Test básico de clasificación heurística
  assert.strictEqual(classifyJurisdictionHint("¿Qué dice el BOCBA sobre obsequios?"), "AR-C");
  assert.strictEqual(classifyJurisdictionHint("Normas de la Provincia de Buenos Aires (PBA) sobre regalos"), "AR-B");
  assert.strictEqual(classifyJurisdictionHint("Lineamientos en Córdoba sobre conflictos de interés"), "AR-X");
  assert.strictEqual(classifyJurisdictionHint("Últimas resoluciones de Mendoza"), "AR-M");
  assert.strictEqual(classifyJurisdictionHint("Criterios Santa Fe para terceros"), "AR-S");
  assert.strictEqual(classifyJurisdictionHint("Beneficios en especie y compliance"), "AR"); // default
  
  // Test de clasificación avanzada con confianza
  const advanced = classifyJurisdictionAdvanced("Según el BOCBA, Artículo 12...");
  assert.ok(advanced.primary === "AR-C", "Debe detectar CABA como jurisdicción primaria");
  assert.ok(advanced.confidence > 0.7, "Debe tener alta confianza para BOCBA");
  assert.ok(Array.isArray(advanced.alternatives), "Debe incluir alternativas");
  
  // Test de fallback
  const fallback = classifyJurisdictionAdvanced("Consulta general sin menciones específicas");
  assert.ok(fallback.primary === "AR", "Debe usar AR como fallback");
  assert.ok(fallback.confidence <= 0.5, "Debe tener baja confianza para fallback");

  console.log("✔ jurisdiction_classify: heurísticas y confianza OK");
})();