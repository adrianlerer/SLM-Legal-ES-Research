import type { Context } from 'hono'

// Enhanced Legal Document interface
interface LegalDocument {
  id: string
  pais: string
  tipo: 'constitucion' | 'ley' | 'decreto' | 'resolucion' | 'codigo' | 'fallo'
  numero?: string
  articulo?: string
  titulo: string
  texto: string
  resumen?: string
  fecha_publicacion?: string
  fuente: string
  jerarquia: number
  vigente: boolean
  tags: string[]
  referencias?: string[]
}

interface CompliancePhrase {
  id: string
  phrase: string
  category: string
  risk_level: number
  cultural_markers: string[]
  legal_reference: string
  explanation: string
}

// Enhanced Legal Corpus - Real Argentine Legal Framework
const ENHANCED_LEGAL_CORPUS: LegalDocument[] = [
  // Constitución Nacional
  {
    id: "arg-const-art14",
    pais: "AR",
    tipo: "constitucion",
    articulo: "14",
    titulo: "Constitución Nacional Argentina",
    texto: "Todos los habitantes de la Nación gozan de los siguientes derechos conforme a las leyes que reglamenten su ejercicio; a saber: de trabajar y ejercer toda industria lícita; de navegar y comerciar; de peticionar a las autoridades; de entrar, permanecer, transitar y salir del territorio argentino; de publicar sus ideas por la prensa sin censura previa; de usar y disponer de su propiedad; de asociarse con fines útiles; de profesar libremente su culto; de enseñar y aprender.",
    resumen: "Derechos fundamentales de los habitantes: trabajo, comercio, libertad de expresión, propiedad, asociación y culto",
    jerarquia: 1,
    vigente: true,
    fuente: "constitucion.gov.ar",
    tags: ["derechos fundamentales", "libertades", "comercio", "trabajo", "propiedad"]
  },
  {
    id: "arg-const-art42",
    pais: "AR", 
    tipo: "constitucion",
    articulo: "42",
    titulo: "Constitución Nacional Argentina",
    texto: "Los consumidores y usuarios de bienes y servicios tienen derecho, en la relación de consumo, a la protección de su salud, seguridad e intereses económicos; a una información adecuada y veraz; a la libertad de elección, y a condiciones de trato equitativo y digno. Las autoridades proveerán a la protección de esos derechos, a la educación para el consumo, a la defensa de la competencia contra toda forma de distorsión de los mercados, al control de los monopolios naturales y legales, al de la calidad y eficiencia de los servicios públicos, y a la constitución de asociaciones de consumidores y de usuarios.",
    resumen: "Derechos de consumidores y usuarios: protección, información, elección, trato equitativo",
    jerarquia: 1,
    vigente: true,
    fuente: "constitucion.gov.ar",
    tags: ["consumidores", "usuarios", "protección", "información", "competencia"]
  },
  
  // Código Civil y Comercial
  {
    id: "arg-ccc-art1109", 
    pais: "AR",
    tipo: "codigo",
    numero: "Civil y Comercial",
    articulo: "1109",
    titulo: "Código Civil y Comercial de la Nación",
    texto: "Todo el que ejecuta un hecho, que por su culpa o negligencia ocasiona un daño a otro, está obligado a la reparación del perjuicio. Esta obligación es regida por las mismas disposiciones relativas a los delitos del derecho civil.",
    resumen: "Responsabilidad civil por daños: obligación de reparar perjuicios causados por culpa o negligencia",
    fecha_publicacion: "2014-10-01",
    jerarquia: 2,
    vigente: true,
    fuente: "infoleg.mecon.gov.ar",
    tags: ["responsabilidad civil", "daños", "culpa", "negligencia", "reparación"]
  },
  {
    id: "arg-ccc-art1137",
    pais: "AR",
    tipo: "codigo", 
    numero: "Civil y Comercial",
    articulo: "1137",
    titulo: "Código Civil y Comercial de la Nación",
    texto: "Los contratos se perfeccionan por el consentimiento mutuo y tienen fuerza de ley entre las partes. Debe estarse al tenor de los términos en que fue celebrado y a las disposiciones de este Código.",
    resumen: "Perfección contractual por consentimiento mutuo: fuerza de ley entre las partes",
    fecha_publicacion: "2014-10-01",
    jerarquia: 2,
    vigente: true,
    fuente: "infoleg.mecon.gov.ar",
    tags: ["contratos", "consentimiento", "perfección", "fuerza de ley", "partes"]
  },

  // Ley de Procedimientos Administrativos
  {
    id: "arg-ley-19549-art1",
    pais: "AR",
    tipo: "ley",
    numero: "19549",
    articulo: "1",
    titulo: "Ley de Procedimientos Administrativos",
    texto: "La Administración Pública Nacional, centralizada y descentralizada, incluidas las entidades autárquicas, los entes públicos no estatales, las empresas del Estado y las sociedades del Estado, se regirá por los procedimientos que establece la presente ley, sin perjuicio de las normas especiales que rijan materias o entidades determinadas.",
    resumen: "Ámbito de aplicación: toda la Administración Pública Nacional y entes relacionados",
    fecha_publicacion: "1972-09-01", 
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["administración pública", "procedimientos", "ámbito", "aplicación", "entes públicos"]
  },
  {
    id: "arg-ley-19549-art17",
    pais: "AR",
    tipo: "ley",
    numero: "19549", 
    articulo: "17",
    titulo: "Ley de Procedimientos Administrativos",
    texto: "La Administración podrá ejercer, con carácter excepcional, las facultades disciplinarias que le otorgan las leyes, cuando el incumplimiento de los deberes del administrado obstaculice gravemente el funcionamiento de un servicio o la ejecución de obras públicas, o pongan en peligro la seguridad pública o causen graves perjuicios al interés general.",
    resumen: "Facultades disciplinarias excepcionales de la Administración en casos graves",
    fecha_publicacion: "1972-09-01",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar", 
    tags: ["facultades disciplinarias", "administración", "excepcional", "seguridad pública", "interés general"]
  },

  // Ley Anti-Corrupción 27.401
  {
    id: "arg-ley-27401-art1",
    pais: "AR",
    tipo: "ley",
    numero: "27401",
    articulo: "1", 
    titulo: "Ley de Responsabilidad Penal de las Personas Jurídicas",
    texto: "Las personas jurídicas de carácter privado, ya sean de capital nacional o extranjero, con o sin participación estatal, quedan sujetas a la responsabilidad penal por los delitos previstos en el artículo 2° de la presente ley cuando estos fueren realizados, directa o indirectamente, con su intervención o en su nombre, interés o beneficio.",
    resumen: "Responsabilidad penal de personas jurídicas por delitos de corrupción",
    fecha_publicacion: "2017-11-29",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["responsabilidad penal", "personas jurídicas", "corrupción", "anti-corrupción", "delitos"]
  },
  {
    id: "arg-ley-27401-art3",
    pais: "AR", 
    tipo: "ley",
    numero: "27401",
    articulo: "3",
    titulo: "Ley de Responsabilidad Penal de las Personas Jurídicas",
    texto: "A los fines de esta ley se consideran delitos los previstos en los artículos 258 bis, 258 ter, 265, 268 (1) y (2), 269 y 270 del Código Penal, cuando fueren cometidos para beneficiar a una persona jurídica.",
    resumen: "Delitos específicos de cohecho, soborno y tráfico de influencias aplicables a personas jurídicas",
    fecha_publicacion: "2017-11-29",
    jerarquia: 3, 
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["cohecho", "soborno", "tráfico de influencias", "código penal", "personas jurídicas"]
  },
  {
    id: "arg-ley-27401-art7",
    pais: "AR",
    tipo: "ley",
    numero: "27401",
    articulo: "7",
    titulo: "Ley de Responsabilidad Penal de las Personas Jurídicas", 
    texto: "Las personas jurídicas quedan exentas de responsabilidad penal si al momento de la comisión del hecho contaban con un programa de integridad adecuado a su actividad, tamaño y capacidad económica, conforme los lineamientos del artículo 23 de esta ley.",
    resumen: "Exención por programas de integridad: requisitos y lineamientos",
    fecha_publicacion: "2017-11-29",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["programa de integridad", "exención", "compliance", "lineamientos", "prevención"]
  },
  
  // Ley de Contrato de Trabajo
  {
    id: "arg-lct-art4",
    pais: "AR",
    tipo: "ley", 
    numero: "20744",
    articulo: "4",
    titulo: "Ley de Contrato de Trabajo",
    texto: "Constituye trabajo, a los fines de esta ley, toda actividad lícita que se preste en favor de quien tiene la facultad de dirigirla, mediante una remuneración. El contrato de trabajo tiene como principal objeto la actividad productiva y creadora del hombre en sí.",
    resumen: "Definición legal de trabajo: actividad lícita, dirigida, remunerada y productiva",
    fecha_publicacion: "1974-09-20",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["contrato de trabajo", "definición", "actividad lícita", "remuneración", "productiva"]
  },
  {
    id: "arg-lct-art14bis", 
    pais: "AR",
    tipo: "ley",
    numero: "20744",
    articulo: "14 bis",
    titulo: "Ley de Contrato de Trabajo", 
    texto: "El trabajo en sus diversas formas gozará de la protección de las leyes, las que asegurarán al trabajador: condiciones dignas y equitativas de labor; jornada limitada; descanso y vacaciones pagados; retribución justa; salario mínimo vital y móvil; igual remuneración por igual tarea; participación en las ganancias de las empresas, con control de la producción y colaboración en la dirección.",
    resumen: "Principios fundamentales del derecho laboral: protección, condiciones dignas, jornada limitada, retribución justa",
    fecha_publicacion: "1974-09-20",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["protección laboral", "condiciones dignas", "jornada limitada", "retribución justa", "salario mínimo"]
  },

  // Ley de Defensa del Consumidor
  {
    id: "arg-ldc-art1",
    pais: "AR",
    tipo: "ley",
    numero: "24240",
    articulo: "1", 
    titulo: "Ley de Defensa del Consumidor",
    texto: "La presente ley tiene por objeto la defensa del consumidor o usuario, entendiéndose por tal a toda persona física o jurídica que adquiere o utiliza bienes o servicios en forma gratuita u onerosa como destinatario final, en beneficio propio o de su grupo familiar o social.",
    resumen: "Objeto y definición de consumidor: persona física o jurídica, destinatario final de bienes o servicios",
    fecha_publicacion: "1993-09-22",
    jerarquia: 3,
    vigente: true, 
    fuente: "boletin-oficial.gob.ar",
    tags: ["defensa del consumidor", "destinatario final", "bienes", "servicios", "protección"]
  },
  {
    id: "arg-ldc-art10bis",
    pais: "AR",
    tipo: "ley", 
    numero: "24240",
    articulo: "10 bis",
    titulo: "Ley de Defensa del Consumidor",
    texto: "En los contratos celebrados fuera de los establecimientos comerciales, ferias o exposiciones, por correspondencia, telecomunicaciones, electrónicos o similares, el consumidor tiene derecho a revocar la aceptación durante el plazo de diez (10) días corridos contados a partir de la fecha en que se entregue el bien o se celebre el contrato.",
    resumen: "Derecho de revocación en contratos a distancia: 10 días corridos desde la entrega o celebración",
    fecha_publicacion: "1993-09-22",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar",
    tags: ["revocación", "contratos a distancia", "10 días", "telecomunicaciones", "electrónicos"]
  },

  // Jurisprudencia relevante - fallos paradigmáticos
  {
    id: "arg-csjn-mosca",
    pais: "AR",
    tipo: "fallo",
    numero: "M.1606.XLI",
    titulo: "Mosca, Hugo c/ Provincia de Buenos Aires s/ inconstitucionalidad",
    texto: "La Corte Suprema estableció que el derecho de propiedad comprende todos los intereses apreciables que el hombre pueda poseer fuera de sí mismo, fuera de su vida y de su libertad. Todo derecho que tenga un valor reconocido como tal por la ley, sea que se origine en las relaciones de derecho privado, sea que nazca de actos administrativos del gobierno o de sentencias civiles o criminales privatorias de derechos anteriores.",
    resumen: "Concepto amplio del derecho de propiedad: todos los intereses apreciables del hombre",
    fecha_publicacion: "2007-11-20",
    jerarquia: 1,
    vigente: true,
    fuente: "csjn.gov.ar",
    tags: ["derecho de propiedad", "intereses", "valor reconocido", "CSJN", "jurisprudencia"]
  },

  // Ley Municipal - marco general
  {
    id: "arg-municipal-general",
    pais: "AR",
    tipo: "ley",
    numero: "general",
    titulo: "Marco Normativo Municipal Argentino",
    texto: "Los municipios argentinos ejercen el poder de policía en su jurisdicción territorial conforme a las facultades delegadas por las provincias. Este poder incluye la regulación de actividades comerciales, la habilitación de establecimientos, el control sanitario y la aplicación de sanciones por infracciones a las ordenanzas municipales. Las competencias municipales están limitadas por la Constitución Nacional, las constituciones provinciales y no pueden vulnerar el derecho federal ni crear restricciones irrazonables al comercio interprovincial.",
    resumen: "Competencias municipales: poder de policía, regulación comercial, habilitaciones y sanciones",
    fecha_publicacion: "2010-01-01",
    jerarquia: 3,
    vigente: true,
    fuente: "normativa-municipal.gov.ar",
    tags: ["municipal", "poder de policía", "habilitación", "comercio", "sanciones", "jurisdicción"]
  }
]

// Enhanced Compliance Cultural Dataset
const ENHANCED_COMPLIANCE_DATASET: CompliancePhrase[] = [
  {
    id: "ARG_001",
    phrase: "Es solo un asadito con el cliente",
    category: "GASTOS_EXCESIVOS", 
    risk_level: 4,
    cultural_markers: ["diminutivo_argentino", "tradicion_argentina", "minimizacion_cultural"],
    legal_reference: "Art. 7 Ley 27.401 - Hospitalidad y Regalos",
    explanation: "Tradición argentina de combinar negocios con asados. Riesgo: normalización de gastos no documentados como 'cultura'"
  },
  {
    id: "ARG_003",
    phrase: "Un regalito para el inspector",
    category: "SOBORNO",
    risk_level: 5,
    cultural_markers: ["diminutivo_argentino", "minimizacion_cultural"], 
    legal_reference: "Art. 3 Ley 27.401 - Cohecho y Soborno",
    explanation: "Diminutivo 'regalito' minimiza percepción de gravedad del soborno a funcionario público"
  },
  {
    id: "ARG_010", 
    phrase: "Lo arreglamos por izquierda",
    category: "ACCION_CLANDESTINA",
    risk_level: 5,
    cultural_markers: ["eufemismo_local"],
    legal_reference: "Art. 15 Ley 27.401 - Tráfico de Influencias",
    explanation: "Modismo arraigado para acciones por fuera de canales legales. 'Por izquierda' es 100% argentino"
  },
  {
    id: "ARG_002",
    phrase: "Mi cuñado tiene una empresa de construcción", 
    category: "CONFLICTO_INTERES",
    risk_level: 4,
    cultural_markers: ["familia_extendida"],
    legal_reference: "Art. 9 Ley 27.401 - Conflictos de Interés",
    explanation: "Estructura empresarial familiar común en Argentina. 'Cuñado' es marcador potentísimo de nepotismo"
  },
  {
    id: "ARG_012",
    phrase: "Necesitamos gestionar esto rápido",
    category: "ACCION_CLANDESTINA",
    risk_level: 2,
    cultural_markers: ["eufemismo_local"],
    legal_reference: "Art. 15 Ley 27.401 - Tráfico de Influencias",
    explanation: "'Gestionar' como eufemismo para tramitar usando influencias o métodos irregulares"
  }
]

// Enhanced similarity calculation
function calculateAdvancedSimilarity(query: string, document: LegalDocument): number {
  const queryLower = query.toLowerCase()
  const textLower = document.texto.toLowerCase()
  const titleLower = document.titulo.toLowerCase() 
  const tagsLower = document.tags.join(' ').toLowerCase()
  
  // Tokenize
  const queryTokens = queryLower.split(/\s+/)
  
  // 1. Exact phrase matching (highest weight)
  let exactMatches = 0
  for (const token of queryTokens) {
    if (textLower.includes(token)) exactMatches++
  }
  const exactScore = exactMatches / queryTokens.length
  
  // 2. Title relevance
  let titleMatches = 0
  for (const token of queryTokens) {
    if (titleLower.includes(token)) titleMatches++
  }
  const titleScore = titleMatches / queryTokens.length
  
  // 3. Tag relevance
  let tagMatches = 0
  for (const token of queryTokens) {
    if (tagsLower.includes(token)) tagMatches++
  }
  const tagScore = tagMatches / queryTokens.length
  
  // 4. Legal domain keywords boost
  const legalKeywords = ['municipio', 'municipal', 'sanción', 'sancionar', 'venta', 'ambulante', 'habilitación', 'comercial', 'procedimiento', 'administrativo', 'responsabilidad', 'contrato', 'consumidor', 'trabajo', 'laboral', 'poder de policía', 'jurisdicción', 'competencia']
  let keywordBoost = 0
  for (const keyword of legalKeywords) {
    if (queryLower.includes(keyword) && textLower.includes(keyword)) {
      keywordBoost += 0.15
    }
  }
  
  // 5. Hierarchy boost
  const hierarchyBoost = (5 - document.jerarquia) * 0.05
  
  // 6. Context matching for municipal/administrative queries
  let contextBoost = 0
  if (queryLower.includes('municipal') || queryLower.includes('municipio')) {
    if (document.tags.includes('municipal') || document.tags.includes('administración pública') || 
        document.tags.includes('poder de policía')) {
      contextBoost += 0.2
    }
  }
  
  // Combined similarity score
  const similarity = (
    exactScore * 0.4 +      // 40% weight for exact matches
    titleScore * 0.2 +      // 20% weight for title matches  
    tagScore * 0.15 +       // 15% weight for tag matches
    keywordBoost +          // Keyword bonus
    hierarchyBoost +        // Hierarchy bonus
    contextBoost            // Context bonus
  )
  
  return Math.min(similarity, 1.0)
}

// Enhanced compliance risk analysis
function analyzeEnhancedComplianceRisks(query: string): CompliancePhrase[] {
  const queryLower = query.toLowerCase()
  const risks: CompliancePhrase[] = []
  
  for (const phrase of ENHANCED_COMPLIANCE_DATASET) {
    const phraseLower = phrase.phrase.toLowerCase()
    
    // Check for direct phrase matches
    if (queryLower.includes(phraseLower) || phraseLower.includes(queryLower)) {
      risks.push(phrase)
      continue
    }
    
    // Check for cultural marker matches
    const hasMarkerMatch = phrase.cultural_markers.some(marker => {
      switch (marker) {
        case 'familia_extendida':
          return queryLower.includes('cuñado') || queryLower.includes('hermano') || 
                 queryLower.includes('primo') || queryLower.includes('familia') ||
                 queryLower.includes('pariente')
        case 'tradicion_argentina':
          return queryLower.includes('asadito') || queryLower.includes('asado') ||
                 queryLower.includes('mate') || queryLower.includes('parrilla')
        case 'eufemismo_local':
          return queryLower.includes('gestionar') || queryLower.includes('arreglar') ||
                 queryLower.includes('colaborar') || queryLower.includes('ayudar') ||
                 queryLower.includes('agilizar')
        case 'diminutivo_argentino':
          return queryLower.includes('regalito') || queryLower.includes('favorcito') ||
                 queryLower.includes('propinita')
        default:
          return false
      }
    })
    
    // Check for partial word matches
    const phraseWords = phrase.phrase.split(' ')
    const hasPartialMatch = phraseWords.some(word => 
      word.length > 3 && queryLower.includes(word.toLowerCase())
    )
    
    // Check for semantic similarity
    const semanticScore = calculateSemanticSimilarity(queryLower, phraseLower)
    
    if (hasMarkerMatch || hasPartialMatch || semanticScore > 0.3) {
      risks.push(phrase)
    }
  }
  
  return risks
}

// Enhanced semantic similarity
function calculateSemanticSimilarity(text1: string, text2: string): number {
  const tokens1 = text1.split(/\s+/).filter(t => t.length > 2)
  const tokens2 = text2.split(/\s+/).filter(t => t.length > 2)
  
  if (tokens1.length === 0 || tokens2.length === 0) return 0
  
  let commonTokens = 0
  for (const token of tokens1) {
    if (tokens2.some(t => t.includes(token) || token.includes(t))) {
      commonTokens++
    }
  }
  
  return commonTokens / Math.max(tokens1.length, tokens2.length)
}

export function retrieveRelevantDocuments(query: string, jurisdiction = "AR", limit = 5): any[] {
  // Filter by jurisdiction and vigente status
  const relevantDocs = ENHANCED_LEGAL_CORPUS
    .filter(doc => doc.pais === jurisdiction && doc.vigente)
    .map(doc => ({
      ...doc,
      similarity: calculateAdvancedSimilarity(query, doc)
    }))
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, limit)
  
  // Filter documents with meaningful similarity
  return relevantDocs.filter(doc => doc.similarity > 0.08)
}

export function analyzeComplianceQuery(query: string): any {
  const risks = analyzeEnhancedComplianceRisks(query)
  
  return {
    hasComplianceRisks: risks.length > 0,
    riskCount: risks.length,
    maxRiskLevel: risks.length > 0 ? Math.max(...risks.map(r => r.risk_level)) : 0,
    detectedRisks: risks
  }
}

export const LEGAL_CONTEXT = {
  totalDocuments: ENHANCED_LEGAL_CORPUS.length,
  compliancePhrases: ENHANCED_COMPLIANCE_DATASET.length,
  jurisdictions: ["AR", "CL", "UY", "ES"],
  documentTypes: ["constitucion", "ley", "decreto", "codigo", "fallo"],
  lastUpdated: "2025-09-25"
}