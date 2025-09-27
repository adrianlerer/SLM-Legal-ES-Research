import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { serveStatic } from 'hono/cloudflare-workers'
import { renderer } from './renderer'
import { legalQueryHandler } from './routes/legal-enhanced'
import { contextEngineeringLegalHandler, contextEngineeringStatusHandler } from './routes/context-engineering-legal'
import { hallucinationGuard } from './lib/hallucination-guard'
import { scmLegalHandler, scmComparisonHandler } from './routes/scm-legal'

const app = new Hono()

// CORS for API routes
app.use('/api/*', cors())

// Serve static files
app.use('/static/*', serveStatic({ root: './public' }))

// JSX renderer for main page
app.use(renderer)

// Legal AI API routes
app.post('/api/legal/query', legalQueryHandler)
app.post('/api/legal/validate', hallucinationGuard)

// Context Engineering API routes (World-Class)
app.post('/api/context-engineering/query', contextEngineeringLegalHandler)
app.get('/api/context-engineering/status', contextEngineeringStatusHandler)

// Small Concept Model (SCM) Legal API routes
app.post('/api/scm/analyze', scmLegalHandler)
app.post('/api/scm/compare', scmComparisonHandler)

// Main page with legal interface
app.get('/', (c) => {
  return c.render(
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🧠 SLM Legal - Small Concept Model (SCM) Edition
          </h1>
          <p className="text-xl text-gray-600 mb-4">
            Specialized Legal AI con Razonamiento Conceptual Avanzado
          </p>
          <div className="flex justify-center space-x-4 mb-4">
            <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
              🧠 Conceptual Reasoning
            </span>
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
              ⚡ 250M Parameters
            </span>
            <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
              🎯 Legal Domain Specialized
            </span>
            <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium">
              🌐 Multi-Jurisdictional
            </span>
          </div>
          <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6 text-left max-w-4xl mx-auto">
            <div className="flex">
              <div className="flex-shrink-0">
                <i className="fas fa-exclamation-triangle text-amber-400"></i>
              </div>
              <div className="ml-3">
                <p className="text-sm text-amber-700">
                  <strong>AVISO LEGAL:</strong> Este sistema es experimental y no constituye asesoramiento legal profesional. 
                  Siempre consulte con un abogado matriculado para asuntos legales específicos.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Model Selection Tabs */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex space-x-4 mb-4">
            <button 
              id="scmTab" 
              onclick="switchModel('scm')" 
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium active-tab"
            >
              🧠 SCM Legal (Conceptual)
            </button>
            <button 
              id="llmTab" 
              onclick="switchModel('llm')" 
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium"
            >
              📝 LLM Tradicional
            </button>
            <button 
              id="compareTab" 
              onclick="switchModel('compare')" 
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium"
            >
              ⚖️ Comparación
            </button>
          </div>
          <div id="modelDescription" className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
            <strong>Small Concept Model (SCM):</strong> Especializado en razonamiento conceptual jurídico. 
            Procesa documentos a nivel de conceptos legales, no tokens individuales.
            Optimizado para coherencia en análisis contractual y compliance.
          </div>
        </div>

        {/* Query Interface */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            <i className="fas fa-gavel mr-2"></i>
            Análisis Legal
          </h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Jurisdicción:
            </label>
            <select id="jurisdiction" className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="AR">🇦🇷 Argentina</option>
              <option value="CL" disabled>🇨🇱 Chile (Próximamente)</option>
              <option value="UY" disabled>🇺🇾 Uruguay (Próximamente)</option>
              <option value="ES" disabled>🇪🇸 España (Próximamente)</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Documento Legal para Análisis:
            </label>
            <textarea 
              id="legalDocument" 
              placeholder="Ej: Paste del contrato, cláusula, o documento legal a analizar..."
              className="w-full p-3 border border-gray-300 rounded-md h-32 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Consulta Específica:
            </label>
            <textarea 
              id="legalQuery" 
              placeholder="Ej: ¿Qué riesgos y obligaciones identifica en este documento?"
              className="w-full p-3 border border-gray-300 rounded-md h-20 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <div className="mb-4" id="scmOptions">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Análisis SCM:
            </label>
            <select id="analysisType" className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="comprehensive">🔍 Análisis Conceptual Integral</option>
              <option value="compliance">🛡️ Enfoque en Compliance</option>
              <option value="risk_assessment">⚠️ Evaluación de Riesgos</option>
              <option value="contract_review">📋 Revisión Contractual</option>
              <option value="governance">🏛️ Gobierno Corporativo</option>
            </select>
          </div>

          <div className="mb-4">
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input type="checkbox" id="enableConceptualReasoning" checked className="mr-2" />
                <span className="text-sm text-gray-700">Razonamiento Conceptual Avanzado</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" id="crossJurisdictional" className="mr-2" />
                <span className="text-sm text-gray-700">Análisis Cross-Jurisdiccional</span>
              </label>
            </div>
          </div>

          <button 
            onclick="submitSCMAnalysis()" 
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition duration-200 font-medium"
          >
            <i className="fas fa-brain mr-2"></i>
            Analizar con SCM Legal
          </button>
        </div>

        {/* Results Area */}
        <div id="results" className="hidden">
          {/* SCM Analysis Results */}
          <div id="scmResults" className="space-y-6">
            {/* Main Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">
                <i className="fas fa-brain mr-2"></i>
                Análisis Conceptual SCM
              </h3>
              <div id="scmAnalysis" className="prose max-w-none"></div>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Conceptos Identificados */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h4 className="text-lg font-semibold mb-3 text-gray-800">
                  <i className="fas fa-lightbulb mr-2"></i>
                  Conceptos Legales
                </h4>
                <div id="conceptsIdentified" className="space-y-2"></div>
              </div>

              {/* Razonamiento Conceptual */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h4 className="text-lg font-semibold mb-3 text-gray-800">
                  <i className="fas fa-project-diagram mr-2"></i>
                  Referencias Cruzadas
                </h4>
                <div id="conceptualReasoning" className="space-y-2"></div>
              </div>

              {/* Evaluación de Riesgos */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h4 className="text-lg font-semibold mb-3 text-gray-800">
                  <i className="fas fa-exclamation-triangle mr-2"></i>
                  Indicadores de Riesgo
                </h4>
                <div id="riskIndicators" className="space-y-2"></div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-semibold mb-3 text-gray-800">
                <i className="fas fa-chart-bar mr-2"></i>
                Métricas de Performance SCM
              </h4>
              <div id="performanceMetrics" className="grid md:grid-cols-4 gap-4 text-sm"></div>
            </div>
          </div>

          {/* Comparison Results */}
          <div id="comparisonResults" className="hidden space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">
                <i className="fas fa-balance-scale mr-2"></i>
                SCM vs LLM Tradicional
              </h3>
              <div id="comparisonAnalysis" className="prose max-w-none"></div>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="mt-12 bg-gray-100 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">
            <i className="fas fa-cogs mr-2"></i>
            Detalles Técnicos
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <strong>Modelo Base:</strong> SCM Legal 250M (Conceptual Reasoning)
            </div>
            <div>
              <strong>Arquitectura:</strong> Small Concept Model + Legal Ontology + Edge Optimization
            </div>
            <div>
              <strong>Especialización:</strong> Dominio Jurídico Hispanoamericano + Multi-Jurisdictional
            </div>
          </div>
        </div>
      </div>

      <script src="/static/scm-legal-app.js"></script>
    </div>
  )
})

export default app
