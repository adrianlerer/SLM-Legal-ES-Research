import assert from "node:assert";
import { enforceCitations } from "../tools/citation_enforcer.js";

(() => {
  // Test CABA - cita válida con BOCBA + pinpoint
  const okCABA = "Según el BOCBA (Boletín Oficial de la Ciudad Autónoma de Buenos Aires), Art. 12, Sección II, se dispone...";
  const passCABA = enforceCitations(okCABA, "AR-C");
  assert.ok(passCABA.ok, "Debería aprobar: BOCBA + Art. + Sección");
  
  // Test CABA - falta pinpoint
  const failCABA = "De acuerdo con normativa local en CABA se establece...";
  const failResultCABA = enforceCitations(failCABA, "AR-C");
  assert.ok(!failResultCABA.ok, "Debería fallar: falta pinpoint y referencia al boletín");
  
  // Test PBA - cita válida con boletín + pinpoint múltiple
  const okPBA = "Boletín Oficial de la Provincia de Buenos Aires, Cap. IV, Artículo 7º — se dispone...";
  const passPBA = enforceCitations(okPBA, "AR-B");
  assert.ok(passPBA.ok, "PBA con Capítulo + Artículo debe aprobar");
  
  // Test Córdoba - cita válida
  const okCordoba = "Boletín Oficial de Córdoba, Artículo 15, establece que...";
  const passCordoba = enforceCitations(okCordoba, "AR-X");
  assert.ok(passCordoba.ok, "Córdoba con boletín + artículo debe aprobar");
  
  // Test jurisdicción nacional - solo requiere pinpoint genérico
  const okNacional = "Según Ley 25.188, Art. 3º, se prohíbe...";
  const passNacional = enforceCitations(okNacional, "AR");
  assert.ok(passNacional.ok, "Nacional con Ley + Art. debe aprobar");
  
  // Test respuesta muy corta
  const tooShort = "Sí.";
  const failShort = enforceCitations(tooShort, "AR-C");
  assert.ok(!failShort.ok, "Respuesta muy corta debe fallar");
  
  // Test jurisdicción no argentina - validación genérica
  const okGeneral = "Según el código civil, artículo 123...";
  const passGeneral = enforceCitations(okGeneral, "ES");
  assert.ok(passGeneral.ok, "Jurisdicción no-AR con cita genérica debe aprobar");

  console.log("✔ citation_enforcer: provincial AR + nacional + genérico OK");
})();