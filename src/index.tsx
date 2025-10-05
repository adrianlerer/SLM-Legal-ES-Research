import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { serveStatic } from 'hono/cloudflare-workers'
import { renderer } from './renderer'

const app = new Hono()

// Enable CORS for API routes
app.use('/api/*', cors())

// Serve static files from public directory
app.use('/static/*', serveStatic({ root: './public' }))

// JSX renderer middleware
app.use(renderer)

// API Routes for legal document analysis
app.get('/api/health', (c) => {
  return c.json({ 
    status: 'ok', 
    service: 'SLM-Legal-Spanish',
    timestamp: new Date().toISOString()
  })
})

// Document analysis endpoint
app.post('/api/analyze-document', async (c) => {
  try {
    const body = await c.req.json()
    const { document_url, analysis_type = 'general' } = body

    if (!document_url) {
      return c.json({ error: 'document_url es requerido' }, 400)
    }

    // Simulated analysis response - will integrate with AI services
    const analysis = {
      document_id: Math.random().toString(36).substring(7),
      analysis_type,
      status: 'completed',
      summary: 'Análisis del documento completado exitosamente',
      key_findings: [
        'Documento académico sobre transformers y composición de funciones',
        'Enfoque teórico en aprendizaje automático y optimización',
        'Aplicaciones potenciales en análisis legal y procesamiento de texto'
      ],
      legal_implications: [
        'Tecnología emergente con potencial impacto regulatorio',
        'Consideraciones de propiedad intelectual en IA',
        'Necesidad de marco normativo para IA en sector legal'
      ],
      compliance_notes: 'Pendiente revisión de normativas específicas de IA',
      processed_at: new Date().toISOString()
    }

    return c.json(analysis)
  } catch (error) {
    return c.json({ error: 'Error procesando el documento' }, 500)
  }
})

// Legal compliance check endpoint
app.post('/api/compliance-check', async (c) => {
  try {
    const body = await c.req.json()
    const { text, jurisdiction = 'ES' } = body

    if (!text) {
      return c.json({ error: 'text es requerido' }, 400)
    }

    const compliance_check = {
      check_id: Math.random().toString(36).substring(7),
      jurisdiction,
      status: 'completed',
      risk_level: 'medium',
      findings: [
        'Uso de terminología técnica especializada',
        'Posibles implicaciones regulatorias en IA',
        'Recomendación de revisión por especialista'
      ],
      recommendations: [
        'Evaluar conformidad con GDPR en procesamiento de datos',
        'Considerar aspectos de responsabilidad en sistemas de IA',
        'Revisar normativas específicas del sector'
      ],
      checked_at: new Date().toISOString()
    }

    return c.json(compliance_check)
  } catch (error) {
    return c.json({ error: 'Error en verificación de compliance' }, 500)
  }
})

// Main page
app.get('/', (c) => {
  return c.render(
    <div>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              <i className="fas fa-balance-scale mr-3 text-blue-600"></i>
              SLM Legal Spanish
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Sistema Inteligente de Análisis Legal y Compliance para Documentos Académicos y Corporativos
            </p>
            <div className="mt-4 text-sm text-gray-500">
              Especializado en Gobierno Corporativo, Compliance y Gestión de Riesgos
            </div>
          </header>

          {/* Main Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {/* Document Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="text-center mb-4">
                <i className="fas fa-file-alt text-3xl text-blue-600 mb-3"></i>
                <h3 className="text-xl font-semibold text-gray-800">Análisis de Documentos</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Análisis inteligente de documentos académicos, contratos y normativas con IA especializada.
              </p>
              <button 
                id="analyze-btn" 
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
              >
                Analizar Documento
              </button>
            </div>

            {/* Compliance Check */}
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="text-center mb-4">
                <i className="fas fa-shield-alt text-3xl text-green-600 mb-3"></i>
                <h3 className="text-xl font-semibold text-gray-800">Verificación de Compliance</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Evaluación automática de cumplimiento normativo según jurisdicción y sector específico.
              </p>
              <button 
                id="compliance-btn" 
                className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
              >
                Verificar Compliance
              </button>
            </div>

            {/* Risk Assessment */}
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="text-center mb-4">
                <i className="fas fa-chart-line text-3xl text-orange-600 mb-3"></i>
                <h3 className="text-xl font-semibold text-gray-800">Evaluación de Riesgos</h3>
              </div>
              <p className="text-gray-600 mb-4">
                Identificación y análisis de riesgos legales, corporativos y regulatorios en tiempo real.
              </p>
              <button 
                id="risk-btn" 
                className="w-full bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition-colors"
              >
                Evaluar Riesgos
              </button>
            </div>
          </div>

          {/* Document Upload Section */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
              <i className="fas fa-upload mr-2 text-blue-600"></i>
              Subir Documento para Análisis
            </h2>
            <div className="max-w-2xl mx-auto">
              <div 
                id="drop-zone" 
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
              >
                <i className="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                <p className="text-lg text-gray-600 mb-2">
                  Arrastra un documento aquí o haz clic para seleccionar
                </p>
                <p className="text-sm text-gray-500">
                  Formatos admitidos: PDF, DOC, DOCX, TXT (máx. 10MB)
                </p>
                <input type="file" id="file-input" className="hidden" accept=".pdf,.doc,.docx,.txt" />
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div id="results-section" className="hidden bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              <i className="fas fa-chart-bar mr-2 text-green-600"></i>
              Resultados del Análisis
            </h2>
            <div id="results-content" className="space-y-4">
              {/* Results will be populated by JavaScript */}
            </div>
          </div>

          {/* Footer */}
          <footer className="text-center mt-12 pt-8 border-t border-gray-200">
            <p className="text-gray-600">
              <strong>SLM Legal Spanish</strong> - Powered by AI • Especializado en Derecho Corporativo
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Desarrollado para profesionales del derecho con más de 30 años de experiencia
            </p>
          </footer>
        </div>
      </div>
    </div>
  )
})

export default app