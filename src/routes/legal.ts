import type { Context } from 'hono'

// Mock legal corpus for MVP
const MOCK_LEGAL_CORPUS = [
  {
    id: "arg-ley-19549-art17",
    pais: "AR",
    tipo: "ley", 
    numero: "19549",
    articulo: "17",
    titulo: "Ley de Procedimientos Administrativos",
    texto: "La Administración podrá ejercer, con carácter excepcional, las facultades disciplinarias que le otorgan las leyes...",
    jerarquia: 3,
    vigente: true,
    fuente: "boletin-oficial.gob.ar"
  },
  {
    id: "arg-const-art42",
    pais: "AR", 
    tipo: "constitucion",
    articulo: "42",
    titulo: "Constitución Nacional Argentina",
    texto: "Los consumidores y usuarios de bienes y servicios tienen derecho, en la relación de consumo, a la protección de su salud, seguridad e intereses económicos...",
    jerarquia: 1,
    vigente: true,
    fuente: "constitucion.gov.ar"
  },
  {
    id: "arg-codigo-civil-art1109",
    pais: "AR",
    tipo: "codigo",
    numero: "Civil y Comercial",
    articulo: "1109", 
    titulo: "Código Civil y Comercial de la Nación",
    texto: "Todo el que ejecuta un hecho, que por su culpa o negligencia ocasiona un daño a otro, está obligado a la reparación del perjuicio...",
    jerarquia: 2,
    vigente: true,
    fuente: "infoleg.mecon.gov.ar"
  }
]

// Simple similarity function for demo purposes
function calculateSimilarity(query: string, text: string): number {
  const queryWords = query.toLowerCase().split(/\s+/)
  const textWords = text.toLowerCase().split(/\s+/)
  
  let matches = 0
  for (const word of queryWords) {
    if (textWords.some(textWord => textWord.includes(word) || word.includes(textWord))) {
      matches++
    }
  }
  
  return matches / queryWords.length
}

// Mock RAG retrieval
function retrieveRelevantChunks(query: string, jurisdiction = "AR"): any[] {
  return MOCK_LEGAL_CORPUS
    .filter(chunk => chunk.pais === jurisdiction && chunk.vigente)
    .map(chunk => ({
      ...chunk,
      similarity: calculateSimilarity(query, chunk.texto)
    }))
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, 3) // Top 3 results
}

// Mock SLM response generation
function generateLegalResponse(query: string, context: any[]): string {
  if (context.length === 0) {
    return "No se encontraron normas relevantes en el corpus legal para esta consulta."
  }

  const relevantChunks = context.filter(c => c.similarity > 0.1)
  
  if (relevantChunks.length === 0) {
    return "No se encuentra información suficiente en el corpus legal vigente para responder esta consulta."
  }

  // Generate a basic response based on the most relevant chunk
  const topChunk = relevantChunks[0]
  
  let response = `Según la normativa argentina vigente:\n\n`
  
  if (query.toLowerCase().includes('municipio') || query.toLowerCase().includes('municipal')) {
    response += `En materia de competencias municipales, debe considerarse que los municipios tienen facultades de regulación en su jurisdicción territorial, conforme al régimen municipal establecido por cada provincia.\n\n`
  }
  
  if (query.toLowerCase().includes('sanción') || query.toLowerCase().includes('sancionar')) {
    response += `Respecto al poder sancionatorio, el artículo 17 de la Ley 19.549 establece que "La Administración podrá ejercer, con carácter excepcional, las facultades disciplinarias que le otorgan las leyes".\n\n`
  }
  
  if (query.toLowerCase().includes('venta') || query.toLowerCase().includes('comercio')) {
    response += `En materia comercial, debe considerarse la protección de los derechos de consumidores establecida en el artículo 42 de la Constitución Nacional, que garantiza "la protección de su salud, seguridad e intereses económicos".\n\n`
  }

  response += `**Fundamento legal:** ${topChunk.titulo}, ${topChunk.articulo ? `Artículo ${topChunk.articulo}` : topChunk.numero}\n\n`
  response += `**Importante:** Esta respuesta se basa en el corpus legal disponible. Para una opinión legal definitiva, consulte con un abogado matriculado.`

  return response
}

export const legalQueryHandler = async (c: Context) => {
  try {
    const { query, jurisdiction = "AR", enableHallGuard = true, requireCitations = true } = await c.req.json()
    
    if (!query || query.trim().length === 0) {
      return c.json({ error: "Consulta requerida" }, 400)
    }

    // Step 1: Retrieve relevant chunks (RAG)
    const relevantChunks = retrieveRelevantChunks(query, jurisdiction)
    
    // Step 2: Generate legal response
    const answer = generateLegalResponse(query, relevantChunks)
    
    // Step 3: Extract citations
    const citations = relevantChunks
      .filter(chunk => chunk.similarity > 0.1)
      .map(chunk => ({
        id: chunk.id,
        text: `${chunk.titulo}${chunk.articulo ? `, Art. ${chunk.articulo}` : chunk.numero ? `, ${chunk.numero}` : ''}`,
        type: chunk.tipo,
        hierarchy: chunk.jerarquia,
        source: chunk.fuente,
        relevance: Math.round(chunk.similarity * 100)
      }))

    // Step 4: Mock hallucination risk metrics
    const riskMetrics = {
      decision: citations.length > 0 ? "ANSWER" : "REFUSE",
      rohBound: citations.length > 0 ? 0.031 : 0.95,
      informationBudget: citations.length * 2.4 + Math.random() * 1.2,
      isrRatio: citations.length > 0 ? 1.8 + Math.random() * 0.5 : 0.3,
      rationale: citations.length > 0 
        ? `Evidence lift ${(citations.length * 2.1).toFixed(1)} nats, ISR ${(1.8 + Math.random() * 0.5).toFixed(1)} → safe`
        : "Insufficient evidence, high hallucination risk → refuse",
      certificateHash: "sha256:" + Math.random().toString(36).substring(2, 15)
    }

    // Step 5: Apply hallucination guard
    if (enableHallGuard && riskMetrics.decision === "REFUSE") {
      return c.json({
        answer: "No se puede proporcionar una respuesta confiable con el corpus legal disponible. Se requiere revisión por abogado especialista.",
        citations: [],
        riskMetrics,
        warning: "Consulta rechazada por alto riesgo de alucinación"
      })
    }

    return c.json({
      answer,
      citations,
      riskMetrics,
      metadata: {
        jurisdiction,
        timestamp: new Date().toISOString(),
        chunksAnalyzed: relevantChunks.length,
        model: "llama-3.2-3b-legal-arg",
        version: "mvp-1.0"
      }
    })

  } catch (error) {
    console.error("Legal query error:", error)
    return c.json({ error: "Error interno del servidor" }, 500)
  }
}