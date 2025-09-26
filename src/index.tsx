import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { serveStatic } from 'hono/cloudflare-workers'
import { renderer } from './renderer'
import { legalQueryHandler } from './routes/legal-enhanced'
import { contextEngineeringLegalHandler, contextEngineeringStatusHandler } from './routes/context-engineering-legal'
import { hallucinationGuard } from './lib/hallucination-guard'

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

// Main page with legal interface
app.get('/', (c) => {
  return c.render(
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🧠 SLM Legal - Context Engineering Edition
          </h1>
          <p className="text-xl text-gray-600 mb-4">
            World-Class Legal AI con Paul Iusztin Context Engineering Framework
          </p>
          <div className="flex justify-center space-x-4 mb-4">
            <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
              ✅ 5-Memory Architecture
            </span>
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
              ⚡ YAML 66% Optimization
            </span>
            <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
              🛡️ 32K Degradation Prevention
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

        {/* Query Interface */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            <i className="fas fa-gavel mr-2"></i>
            Consulta Legal
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
              Consulta:
            </label>
            <textarea 
              id="legalQuery" 
              placeholder="Ej: ¿Puede un municipio sancionar la venta ambulante sin habilitación comercial?"
              className="w-full p-3 border border-gray-300 rounded-md h-32 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <div className="mb-4">
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input type="checkbox" id="enableHallGuard" checked className="mr-2" />
                <span className="text-sm text-gray-700">Activar Hallucination Guard (RoH ≤ 5%)</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" id="requireCitations" checked className="mr-2" />
                <span className="text-sm text-gray-700">Exigir citas exactas</span>
              </label>
            </div>
          </div>

          <button 
            onclick="submitQuery()" 
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition duration-200 font-medium"
          >
            <i className="fas fa-search mr-2"></i>
            Consultar SLM Legal
          </button>
        </div>

        {/* Results Area */}
        <div id="results" className="hidden">
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">
              <i className="fas fa-balance-scale mr-2"></i>
              Respuesta Legal
            </h3>
            <div id="legalAnswer" className="prose max-w-none"></div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Citations */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h4 className="text-lg font-semibold mb-3 text-gray-800">
                <i className="fas fa-book mr-2"></i>
                Citas Jurídicas
              </h4>
              <div id="citations" className="space-y-2"></div>
            </div>

            {/* Hallucination Risk */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h4 className="text-lg font-semibold mb-3 text-gray-800">
                <i className="fas fa-shield-alt mr-2"></i>
                Control de Alucinación
              </h4>
              <div id="riskMetrics" className="space-y-2"></div>
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
              <strong>Modelo Base:</strong> Llama 3.2 3B (local)
            </div>
            <div>
              <strong>Arquitectura:</strong> Context Engineering + WorldClass RAG + EDFL
            </div>
            <div>
              <strong>Framework:</strong> Paul Iusztin Context Engineering + 5-Memory System
            </div>
          </div>
        </div>
      </div>

      <script src="/static/context-engineering-app.js"></script>
    </div>
  )
})

export default app
