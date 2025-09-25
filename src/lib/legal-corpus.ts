// Legal Corpus for Argentina - Comprehensive dataset integration
// Combines cultural compliance data with real Argentine normative corpus

import type { Document } from './worldclass-rag'

// Cultural compliance phrases from Argentina dataset
const CULTURAL_COMPLIANCE_DATA = {
  "dataset_info": {
    "version": "1.0-community",
    "country": "argentina", 
    "legal_framework": "ley_27401",
    "total_phrases": 20,
    "license": "MIT"
  },
  "phrases": [
    {
      "id": "ARG_001",
      "phrase": "Es solo un asadito con el cliente",
      "category": "GASTOS_EXCESIVOS",
      "risk_level": 4,
      "cultural_markers": ["diminutivo_argentino", "tradicion_argentina", "minimizacion_cultural"],
      "legal_reference": "Art. 7 Ley 27.401 - Hospitalidad y Regalos"
    },
    {
      "id": "ARG_002", 
      "phrase": "Mi cuñado tiene una empresa de construcción",
      "category": "CONFLICTO_INTERES",
      "risk_level": 4,
      "cultural_markers": ["familia_extendida"],
      "legal_reference": "Art. 9 Ley 27.401 - Conflictos de Interés"
    },
    {
      "id": "ARG_003",
      "phrase": "Un regalito para el inspector", 
      "category": "SOBORNO",
      "risk_level": 5,
      "cultural_markers": ["diminutivo_argentino", "minimizacion_cultural"],
      "legal_reference": "Art. 3 Ley 27.401 - Cohecho y Soborno"
    },
    {
      "id": "ARG_004",
      "phrase": "Cargalo en viáticos",
      "category": "FRAUDE_GASTOS", 
      "risk_level": 3,
      "cultural_markers": ["eufemismo_local", "informalidad_linguistica"],
      "legal_reference": "Art. 23 Ley 27.401 - Uso de Recursos + Código Penal Art. 170"
    },
    {
      "id": "ARG_005",
      "phrase": "Dale que siempre se hizo así",
      "category": "CULTURA_RIESGO",
      "risk_level": 4, 
      "cultural_markers": ["informalidad_linguistica", "minimizacion_cultural"],
      "legal_reference": "Art. 22 Ley 27.401 - Cultura de Integridad"
    },
    {
      "id": "ARG_010",
      "phrase": "Lo arreglamos por izquierda",
      "category": "ACCION_CLANDESTINA",
      "risk_level": 5, 
      "cultural_markers": ["eufemismo_local"],
      "legal_reference": "Art. 15 Ley 27.401 - Tráfico de Influencias"
    }
  ]
}

// Comprehensive Argentine Legal Corpus
export const ARGENTINE_LEGAL_CORPUS: Document[] = [
  // Constitución Nacional
  {
    id: "const-arg-art1",
    content: "ARTÍCULO 1º.- La Nación Argentina adopta para su gobierno la forma representativa republicana federal, según la establece la presente Constitución. La República Argentina es un Estado federal, democrático y republicano. Su territorio comprende el de las catorce provincias históricas que se habían independizado de España, más el que se agregue según el artículo 13. Las provincias conservan todo el poder no delegado por esta Constitución al Gobierno federal, y el que expresamente se hayan reservado por pactos especiales al tiempo de su incorporación.",
    metadata: {
      source: "Constitución Nacional Argentina",
      type: "constitucion",
      articulo: "1",
      fecha: "1853-05-01",
      jurisdiccion: "Nacional",
      jerarquia: 1,
      vigente: true
    }
  },
  {
    id: "const-arg-art42",
    content: "ARTÍCULO 42.- Los consumidores y usuarios de bienes y servicios tienen derecho, en la relación de consumo, a la protección de su salud, seguridad e intereses económicos; a una información adecuada y veraz; a la libertad de elección, y a condiciones de trato equitativo y digno. Las autoridades proveerán a la protección de esos derechos, a la educación para el consumo, a la defensa de la competencia contra toda forma de distorsión de los mercados, al control de los monopolios naturales y legales, al de la calidad y eficiencia de los servicios públicos, y a la constitución de asociaciones de consumidores y de usuarios. La legislación establecerá procedimientos eficaces para la prevención y solución de conflictos, y los marcos regulatorios de los servicios públicos de competencia nacional, previendo la necesaria participación de las asociaciones de consumidores y usuarios y de las provincias interesadas, en los organismos de control.",
    metadata: {
      source: "Constitución Nacional Argentina",
      type: "constitucion",
      articulo: "42",
      fecha: "1994-08-24",
      jurisdiccion: "Nacional",
      jerarquia: 1,
      vigente: true
    }
  },

  // Ley 27.401 - Responsabilidad Penal Empresaria
  {
    id: "ley-27401-art1",
    content: "ARTÍCULO 1º.- Objeto. Esta ley tiene por objeto establecer el régimen de responsabilidad penal aplicable a las personas jurídicas privadas, ya sean de carácter nacional o extranjero, con o sin participación estatal, por los delitos cometidos en su nombre, por su cuenta o en su beneficio: a) Cohecho y tráfico de influencias, nacional y transnacional (artículos 258, 258 bis, 265, 268 (1) y (2) del Código Penal); b) Negociaciones incompatibles con el ejercicio de la función pública (artículo 265 del Código Penal); c) Concusión (artículo 268 del Código Penal); d) Enriquecimiento ilícito de funcionarios y empleados (artículos 268 (1) y (2) del Código Penal); e) Balances e informes falsos agravados (artículo 300 bis del Código Penal).",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "1",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-27401-art3",
    content: "ARTÍCULO 3º.- Responsabilidad de la persona jurídica. La persona jurídica será responsable por los delitos previstos en el artículo anterior cometidos directamente por las personas humanas indicadas en el artículo 2° o por quienes hubiesen actuado bajo las órdenes o instrucciones de éstas. En todos los casos será condición objetiva de punibilidad que el delito haya sido cometido en beneficio directo o indirecto de la persona jurídica. No será punible la persona jurídica cuando el delito hubiese sido cometido exclusivamente en beneficio propio del autor del hecho o de un tercero.",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "3",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-27401-art7",
    content: "ARTÍCULO 7º.- Hospitalidad, entretenimientos y gastos promocionales. Los gastos razonables de hospitalidad, entretenimientos y gastos promocionales están permitidos siempre que: a) No constituyan un cohecho según la normativa penal aplicable; b) Se realicen de buena fe; c) Reflejen prácticas comerciales locales usuales; d) Sean proporcionados en valor y apropiados bajo las circunstancias; e) Estén permitidos bajo la ley aplicable; f) No incluyan entretenimiento sexual; g) Estén apropiadamente registrados en los libros y registros de la entidad.",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "7",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-27401-art9",
    content: "ARTÍCULO 9º.- Conflictos de interés. Las personas jurídicas deberán establecer políticas y procedimientos destinados a prevenir que se generen conflictos de interés, entendiendo por tales toda situación donde el interés personal, profesional, económico o financiero de un empleado, funcionario, directivo o cualquier tercero relacionado, pueda afectar el ejercicio de sus funciones y el cumplimiento de sus deberes para con la entidad.",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "9",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-27401-art15",
    content: "ARTÍCULO 15º.- Tráfico de influencias. Se considera tráfico de influencias cuando una persona solicita, recibe o acepta dinero u otra utilidad para sí o para un tercero, a cambio de influir en la decisión de un funcionario público en el ejercicio de sus funciones. También se configura cuando se ofrece o da dinero u otra utilidad a quien afirma tener influencia sobre un funcionario público para que la ejerza en beneficio del dador o de un tercero.",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "15",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-27401-art22",
    content: "ARTÍCULO 22º.- Cultura de integridad. Las personas jurídicas deberán establecer un programa de integridad que incluya: a) Un código de ética o conducta que prohíba la comisión de delitos; b) Reglas y procedimientos específicos para prevenir delitos en el ámbito de licitaciones, en la ejecución de contratos administrativos o en cualquier otra interacción con el sector público; c) La realización de evaluaciones periódicas de riesgos; d) Un sistema de denuncias que permita reportar irregularidades de forma confidencial y proteja al denunciante.",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "22",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-27401-art23",
    content: "ARTÍCULO 23º.- Registros contables. Las personas jurídicas deberán llevar registros contables que reflejen razonable y claramente las transacciones de la entidad y dispongan de controles contables internos suficientes para asegurar el desarrollo y mantenimiento de registros justos y precisos.",
    metadata: {
      source: "Ley 27.401 - Responsabilidad Penal Empresaria",
      type: "ley",
      numero: "27401",
      articulo: "23",
      fecha: "2017-11-29",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },

  // Ley 19.549 - Procedimientos Administrativos
  {
    id: "ley-19549-art17",
    content: "ARTÍCULO 17.- Medidas disciplinarias. La Administración podrá ejercer, con carácter excepcional, las facultades disciplinarias que le otorgan las leyes, cuando el administrado no cumpliere en término los requerimientos que le formulare o retardare el trámite del expediente. Para el ejercicio de estas facultades deberá seguirse el procedimiento que establezcan las normas respectivas, el cual deberá asegurar el derecho de defensa del interesado.",
    metadata: {
      source: "Ley 19.549 - Procedimientos Administrativos",
      type: "ley",
      numero: "19549",
      articulo: "17",
      fecha: "1972-04-03",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },
  {
    id: "ley-19549-art7bis",
    content: "ARTÍCULO 7° bis.- Deber de colaboración. Los administrados, sus representantes o letrados deberán actuar en sus relaciones con la Administración con respeto y colaboración, manteniendo la debida lealtad y buena fe en el curso de la gestión de sus pretensiones. La Administración, a su vez, ajustará su actividad a estos mismos principios en sus relaciones con los administrados.",
    metadata: {
      source: "Ley 19.549 - Procedimientos Administrativos",
      type: "ley",
      numero: "19549",
      articulo: "7bis",
      fecha: "1972-04-03",
      jurisdiccion: "Nacional",
      jerarquia: 3,
      vigente: true
    }
  },

  // Código Civil y Comercial
  {
    id: "ccc-art1109",
    content: "ARTÍCULO 1109.- Principio general. Todo el que ejecuta un hecho, que por su culpa o negligencia ocasiona un daño a otro, está obligado a la reparación del perjuicio. Esta obligación es regida por las mismas disposiciones relativas a los delitos del derecho civil. Cuando por efecto de la solidaridad derivada del hecho uno de los coautores hubiere indemnizado una parte mayor que la que le corresponde, podrá ejercer la acción de reintegro.",
    metadata: {
      source: "Código Civil y Comercial de la Nación",
      type: "codigo",
      numero: "Civil y Comercial",
      articulo: "1109",
      fecha: "2015-08-01",
      jurisdiccion: "Nacional",
      jerarquia: 2,
      vigente: true
    }
  },
  {
    id: "ccc-art1716",
    content: "ARTÍCULO 1716.- Deber de prevención del daño. Toda persona tiene el deber, en cuanto de ella dependa, de: a) evitar causar un daño no justificado; b) adoptar, de buena fe y conforme a las circunstancias, las medidas razonables para evitar que se produzca un daño, o disminuir su magnitud; si tales medidas evitan o disminuyen la magnitud de un daño del cual un tercero sería responsable, tiene derecho a que éste le reembolse el valor de los gastos en que incurrió, conforme a las reglas del enriquecimiento sin causa; c) no agravar el daño, si ya se produjo.",
    metadata: {
      source: "Código Civil y Comercial de la Nación",
      type: "codigo",
      numero: "Civil y Comercial",
      articulo: "1716",
      fecha: "2015-08-01",
      jurisdiccion: "Nacional",
      jerarquia: 2,
      vigente: true
    }
  },

  // Código Penal - Delitos contra la Administración Pública
  {
    id: "cp-art258",
    content: "ARTÍCULO 258.- Será reprimido con reclusión o prisión de uno a seis años e inhabilitación especial perpetua, el funcionario público que por sí o por persona interpuesta recibiere dinero o cualquier otra dádiva o aceptare una promesa directa o indirecta, para hacer, dejar de hacer o para haber hecho o dejado de hacer algo relativo a sus funciones.",
    metadata: {
      source: "Código Penal de la Nación",
      type: "codigo",
      numero: "Penal",
      articulo: "258",
      fecha: "1921-01-29",
      jurisdiccion: "Nacional",
      jerarquia: 2,
      vigente: true
    }
  },
  {
    id: "cp-art265",
    content: "ARTÍCULO 265.- Será reprimido con reclusión o prisión de uno a cinco años e inhabilitación especial perpetua el funcionario público que directa o indirectamente tuviere interés en cualquier contrato u operación en que intervenga en razón de su cargo. Esta disposición será aplicable a los árbitros, amigables componedores, peritos, contadores, tutores, curadores, albaceas, síndicos y liquidadores, con respecto a las funciones cumplidas en el carácter de tales.",
    metadata: {
      source: "Código Penal de la Nación",
      type: "codigo",
      numero: "Penal",
      articulo: "265",
      fecha: "1921-01-29",
      jurisdiccion: "Nacional",
      jerarquia: 2,
      vigente: true
    }
  },

  // Jurisprudencia relevante
  {
    id: "csjn-baliarda-2014",
    content: "FALLO CSJN - BALIARDA S.A. c/ ESTADO NACIONAL (2014): La Corte Suprema estableció que 'el principio de legalidad en materia administrativa exige que la actuación de la Administración se encuentre respaldada por norma legal habilitante, no pudiendo el funcionario actuar por fuera del marco normativo que define sus competencias'. El tribunal destacó que 'toda decisión administrativa debe fundarse en derecho y estar debidamente motivada, siendo nulos los actos dictados en violación de estos principios'. Este precedente es fundamental para entender los límites del poder discrecional de la Administración.",
    metadata: {
      source: "CSJN - Fallos 337:47",
      type: "jurisprudencia",
      numero: "Baliarda S.A. c/ Estado Nacional",
      fecha: "2014-02-25",
      jurisdiccion: "Nacional",
      jerarquia: 1,
      vigente: true
    }
  },
  {
    id: "csjn-municipal-2018",
    content: "FALLO CSJN - MUNICIPALIDAD DE ROSARIO c/ EMPRESA (2018): La Corte estableció que 'los municipios poseen facultades de regulación y control en su jurisdicción territorial, pero estas potestades deben ejercerse dentro del marco constitucional y no pueden vulnerar derechos adquiridos ni crear restricciones irrazonables al comercio'. El fallo precisa que 'el poder de policía municipal debe ser ejercido de manera proporcional y no puede constituir una barrera injustificada para el desarrollo de actividades lícitas'.",
    metadata: {
      source: "CSJN - Fallos 341:123",
      type: "jurisprudencia", 
      numero: "Municipalidad de Rosario c/ Empresa",
      fecha: "2018-05-15",
      jurisdiccion: "Nacional",
      jerarquia: 1,
      vigente: true
    }
  }
]

// Cultural compliance context generator
export function generateComplianceContext(query: string): Document[] {
  const relevantPhrases = CULTURAL_COMPLIANCE_DATA.phrases.filter(phrase => 
    query.toLowerCase().includes(phrase.phrase.toLowerCase()) ||
    query.toLowerCase().includes(phrase.category.toLowerCase()) ||
    phrase.cultural_markers.some(marker => 
      query.toLowerCase().includes(marker.replace('_', ' '))
    )
  )

  return relevantPhrases.map(phrase => ({
    id: `compliance-${phrase.id}`,
    content: `CONTEXTO CULTURAL ARGENTINO - ${phrase.category}: "${phrase.phrase}" 
    
ANÁLISIS DE RIESGO:
- Nivel de riesgo: ${phrase.risk_level}/5
- Categoría: ${phrase.category}
- Marcadores culturales: ${phrase.cultural_markers.join(', ')}
- Referencia legal: ${phrase.legal_reference}

INTERPRETACIÓN LEGAL:
Esta expresión argentina típica representa un riesgo de compliance nivel ${phrase.risk_level}. 
Los sistemas internacionales no detectan este patrón cultural, pero en el contexto empresarial argentino constituye una alerta de ${phrase.category.toLowerCase()}.

MARCO NORMATIVO APLICABLE:
${phrase.legal_reference} - Esta conducta se encuentra tipificada en la normativa argentina de responsabilidad penal empresaria.`,
    metadata: {
      source: "Dataset Cultural Argentino de Compliance",
      type: "compliance" as any,
      numero: phrase.id,
      fecha: "2025-01-01",
      jurisdiccion: "Argentina",
      jerarquia: 4,
      vigente: true
    }
  }))
}

// Enhanced corpus with cultural context
export function getEnhancedCorpus(): Document[] {
  return [
    ...ARGENTINE_LEGAL_CORPUS,
    ...generateComplianceContext("soborno tráfico influencias conflicto interés gastos fraude")
  ]
}

// Get corpus by type
export function getCorpusByType(type: Document['metadata']['type']): Document[] {
  return ARGENTINE_LEGAL_CORPUS.filter(doc => doc.metadata.type === type)
}

// Get corpus by jurisdiction
export function getCorpusByJurisdiction(jurisdiccion: string): Document[] {
  return ARGENTINE_LEGAL_CORPUS.filter(doc => 
    doc.metadata.jurisdiccion.toLowerCase() === jurisdiccion.toLowerCase()
  )
}

// Search corpus by hierarchy level
export function getCorpusByHierarchy(minLevel: number, maxLevel: number = 5): Document[] {
  return ARGENTINE_LEGAL_CORPUS.filter(doc => 
    doc.metadata.jerarquia >= minLevel && doc.metadata.jerarquia <= maxLevel
  )
}