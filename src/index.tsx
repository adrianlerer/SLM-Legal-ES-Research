/**
 * SCM Legal - Main Application Entry Point
 * World-class implementation integrating best practices from:
 * - Tolgee (multi-jurisdictional architecture)
 * - System Design Primer (microservices patterns)
 * - Public APIs (data integration framework)
 * - Developer Roadmap (technology optimization)
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { compress } from 'hono/compress';
import { secureHeaders } from 'hono/secure-headers';
import { serveStatic } from 'hono/cloudflare-workers';
import { renderer } from './renderer';
import { legalQueryHandler } from './routes/legal-enhanced';
import { contextEngineeringLegalHandler, contextEngineeringStatusHandler } from './routes/context-engineering-legal';
import { hallucinationGuard } from './lib/hallucination-guard';
import { scmLegalHandler, scmComparisonHandler } from './routes/scm-legal';
import { JurisdictionManager, defaultJurisdictionConfig } from './core/jurisdiction/manager';
import { LegalDataSourceManager } from './integrations/legal-data-sources';
import { darwinSCMIntegrationApp } from './integrations/darwin-writer-integration';
import type { LegalContextRequest, LegalContextResponse } from './core/jurisdiction/types';

// Type definitions for Cloudflare bindings
type Bindings = {
  DB: D1Database;
  KV: KVNamespace;
  R2: R2Bucket;
  VECTOR_DB?: VectorizeIndex;
  AI_GATEWAY?: any;
  ANALYTICS?: AnalyticsEngine;
};

type Variables = {
  requestId: string;
  userId?: string;
  jurisdiction: string;
};

const app = new Hono<{ Bindings: Bindings; Variables: Variables }>();

// Initialize services
let jurisdictionManager: JurisdictionManager;
let dataSourceManager: LegalDataSourceManager;

// Security headers for production-ready deployment
app.use('*', secureHeaders({
  contentSecurityPolicy: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdn.tailwindcss.com"],
    styleSrc: ["'self'", "'unsafe-inline'", "cdn.tailwindcss.com", "cdn.jsdelivr.net"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'", "https:"],
  },
}));

// Compression for optimal performance
app.use('*', compress());

// Enhanced CORS configuration for multi-jurisdictional access
app.use('*', cors({
  origin: (origin) => {
    const allowedOrigins = [
      'https://scm-legal.pages.dev',
      'https://scm-legal-enterprise.pages.dev',
      'http://localhost:3000',
      'http://localhost:5173', // Vite dev server
    ];
    return allowedOrigins.includes(origin || '') || !origin;
  },
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Jurisdiction', 'X-Client-ID', 'X-Request-ID'],
  exposeHeaders: ['X-Request-ID', 'X-Processing-Time', 'X-Served-By'],
  maxAge: 86400, // 24 hours
}));

// Structured logging middleware
app.use('*', logger((message, ...rest) => {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level: 'info',
    service: 'scm-legal-main',
    message,
    data: rest,
  };
  console.log(JSON.stringify(logEntry));
}));

// Request ID and performance tracking
app.use('*', async (c, next) => {
  const requestId = c.req.header('x-request-id') || 
                   `req_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  c.set('requestId', requestId);
  c.header('x-request-id', requestId);
  
  const start = Date.now();
  await next();
  const processingTime = Date.now() - start;
  c.header('x-processing-time', processingTime.toString());
});

// Initialize services with Cloudflare bindings
app.use('*', async (c, next) => {
  if (!jurisdictionManager) {
    jurisdictionManager = new JurisdictionManager(defaultJurisdictionConfig);
  }
  if (!dataSourceManager) {
    dataSourceManager = new LegalDataSourceManager();
  }
  await next();
});

// JSX renderer for React-like components
app.use(renderer);

// Serve static files with caching headers
app.use('/static/*', serveStatic({ 
  root: './public',
  onNotFound: (path, c) => {
    console.log(`Static file not found: ${path}`);
  }
}));

// Health check endpoint for monitoring
app.get('/health', (c) => {
  return c.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    service: 'scm-legal-main',
    features: {
      multiJurisdictional: true,
      microservices: true,
      dataIntegration: true,
      academicStructure: true,
      optimizedStack: true,
      scmAnalysis: true,
      contextEngineering: true,
    },
  });
});

// Readiness probe for Kubernetes/container orchestration
app.get('/ready', (c) => {
  const ready = jurisdictionManager && dataSourceManager;
  return c.json(
    { 
      status: ready ? 'ready' : 'not-ready', 
      timestamp: new Date().toISOString(),
      services: {
        jurisdictionManager: !!jurisdictionManager,
        dataSourceManager: !!dataSourceManager,
      }
    }, 
    ready ? 200 : 503
  );
});

// Enhanced legal analysis API with multi-jurisdictional support
app.post('/api/legal/analyze', async (c) => {
  try {
    const request: LegalContextRequest = await c.req.json();
    
    // Validate request
    if (!request.query || !request.jurisdiction) {
      return c.json({ error: 'Query and jurisdiction are required' }, 400);
    }

    // Set jurisdiction context
    c.set('jurisdiction', request.jurisdiction);

    // Process legal context with enhanced features
    const response = await jurisdictionManager.processLegalContext(request);

    // Add metadata
    const enhancedResponse: LegalContextResponse = {
      ...response,
      metadata: {
        ...response.metadata,
        requestId: c.get('requestId'),
        version: '1.0.0',
        features: ['multi-jurisdictional', 'comparative-analysis', 'ai-enhanced'],
      },
    };

    return c.json(enhancedResponse);

  } catch (error) {
    console.error('Legal analysis error:', error);
    return c.json({
      error: 'Analysis failed',
      requestId: c.get('requestId'),
      message: error instanceof Error ? error.message : 'Unknown error',
    }, 500);
  }
});

// Jurisdiction management API
app.get('/api/jurisdictions', (c) => {
  const jurisdictions = jurisdictionManager.getEnabledJurisdictions();
  return c.json({ 
    jurisdictions,
    metadata: {
      total: jurisdictions.length,
      requestId: c.get('requestId'),
    },
  });
});

app.get('/api/jurisdictions/:code', (c) => {
  const code = c.req.param('code');
  try {
    const jurisdiction = jurisdictionManager.getJurisdiction(code);
    return c.json({ 
      jurisdiction,
      metadata: {
        requestId: c.get('requestId'),
      },
    });
  } catch (error) {
    return c.json({ 
      error: 'Jurisdiction not found',
      code,
      requestId: c.get('requestId'),
    }, 404);
  }
});

// Legal data sources health check
app.get('/api/data-sources/health', async (c) => {
  try {
    const healthReport = await dataSourceManager.getSourceHealth();
    return c.json({
      ...healthReport,
      requestId: c.get('requestId'),
    });
  } catch (error) {
    return c.json({
      error: 'Failed to check data source health',
      requestId: c.get('requestId'),
    }, 500);
  }
});

// Legacy API routes (maintaining compatibility)
app.post('/api/legal/query', legalQueryHandler);
app.post('/api/legal/validate', hallucinationGuard);

// Darwin-SCM Hybrid Integration Routes
app.route('/api/hybrid', darwinSCMIntegrationApp);

// Context Engineering API routes (World-Class)
app.post('/api/context-engineering/query', contextEngineeringLegalHandler);
app.get('/api/context-engineering/status', contextEngineeringStatusHandler);

// Small Concept Model (SCM) Legal API routes
app.post('/api/scm/analyze', scmLegalHandler);
app.post('/api/scm/compare', scmComparisonHandler);

// Main page with enhanced UI and world-class architecture features
app.get('/', (c) => {
  return c.render(
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Enhanced Header with World-Class Branding */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <i className="fas fa-balance-scale text-3xl text-blue-600 mr-4"></i>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SCM Legal</h1>
                <p className="text-sm text-gray-600">Small Concept Models para Análisis Legal Multi-Jurisdiccional</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Jurisdicciones:</span>
                <div className="flex space-x-1">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">AR</span>
                  <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium">ES</span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">CL</span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">UY</span>
                </div>
              </div>
              <a href="https://github.com/adrianlerer/SLM-Legal-Spanish" target="_blank" 
                 className="text-gray-600 hover:text-blue-600 transition-colors">
                <i className="fab fa-github text-xl"></i>
              </a>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* World-Class Features Banner */}
        <div className="text-center mb-8">
          <h2 className="text-4xl font-extrabold text-gray-900 mb-4">
            🧠 Análisis Legal Inteligente
            <span className="text-blue-600"> Multi-Jurisdiccional</span>
          </h2>
          <p className="text-xl text-gray-600 mb-4">
            Plataforma de IA especializada con Small Concept Models (SCM) optimizados para el dominio legal
          </p>
          <div className="flex justify-center flex-wrap gap-2 mb-4">
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
            <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
              🏗️ Microservices Architecture
            </span>
            <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium">
              📊 World-Class Integration
            </span>
          </div>
          <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6 text-left max-w-4xl mx-auto">
            <div className="flex">
              <div className="flex-shrink-0">
                <i className="fas fa-exclamation-triangle text-amber-400"></i>
              </div>
              <div className="ml-3">
                <p className="text-sm text-amber-700">
                  <strong>AVISO LEGAL:</strong> Este sistema es experimental y de investigación académica. No constituye asesoramiento legal profesional. 
                  Siempre consulte con un abogado matriculado para asuntos legales específicos.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Model Selection with Architecture Info */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-wrap gap-2 mb-4">
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
            <button 
              id="architectureTab" 
              onclick="switchModel('architecture')" 
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium"
            >
              🏗️ Arquitectura
            </button>
            <button 
              id="darwinTab" 
              onclick="window.open('/static/darwin-scm-demo.html', '_blank')" 
              className="px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-blue-600 transition-all"
              title="Abrir Demo de Integración Darwin Writer + SCM Legal"
            >
              🧬 Darwin-SCM Hybrid
            </button>
          </div>
          <div id="modelDescription" className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
            <strong>Small Concept Model (SCM):</strong> Arquitectura distribuida con microservicios, 
            integración multi-jurisdiccional (AR/ES/CL/UY), y patrones de clase mundial para análisis legal especializado.
            Procesa documentos a nivel de conceptos legales con razonamiento contextual avanzado.
          </div>
        </div>

        {/* Enhanced Query Interface */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            <i className="fas fa-gavel mr-2"></i>
            Análisis Legal Multi-Jurisdiccional
          </h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Jurisdicción:
            </label>
            <select id="jurisdiction" className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              <option value="AR">🇦🇷 Argentina (Activo)</option>
              <option value="ES">🇪🇸 España (Integración Avanzada)</option>
              <option value="CL">🇨🇱 Chile (Integración Avanzada)</option>
              <option value="UY">🇺🇾 Uruguay (Integración Avanzada)</option>
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
              <option value="cross_jurisdictional">🌐 Análisis Cross-Jurisdiccional</option>
            </select>
          </div>

          <div className="mb-4">
            <div className="flex flex-wrap gap-4">
              <label className="flex items-center">
                <input type="checkbox" id="enableConceptualReasoning" checked className="mr-2" />
                <span className="text-sm text-gray-700">Razonamiento Conceptual Avanzado</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" id="crossJurisdictional" className="mr-2" />
                <span className="text-sm text-gray-700">Análisis Cross-Jurisdiccional</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" id="enableDataSources" className="mr-2" />
                <span className="text-sm text-gray-700">Integración Fuentes Oficiales</span>
              </label>
            </div>
          </div>

          <button 
            onclick="submitSCMAnalysis()" 
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition duration-200 font-medium"
          >
            <i className="fas fa-brain mr-2"></i>
            Analizar con SCM Legal Multi-Jurisdiccional
          </button>
        </div>

        {/* Results Area - Enhanced with World-Class Features */}
        <div id="results" className="hidden">
          {/* SCM Analysis Results */}
          <div id="scmResults" className="space-y-6">
            {/* Main Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">
                <i className="fas fa-brain mr-2"></i>
                Análisis Conceptual SCM Multi-Jurisdiccional
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

            {/* Enhanced Performance Metrics with Architecture Info */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-semibold mb-3 text-gray-800">
                <i className="fas fa-chart-bar mr-2"></i>
                Métricas de Performance SCM & Arquitectura
              </h4>
              <div id="performanceMetrics" className="grid md:grid-cols-4 gap-4 text-sm"></div>
            </div>
          </div>

          {/* Comparison Results */}
          <div id="comparisonResults" className="hidden space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">
                <i className="fas fa-balance-scale mr-2"></i>
                SCM vs LLM Tradicional - Análisis Comparativo
              </h3>
              <div id="comparisonAnalysis" className="prose max-w-none"></div>
            </div>
          </div>

          {/* Architecture Details */}
          <div id="architectureDetails" className="hidden space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">
                <i className="fas fa-sitemap mr-2"></i>
                Arquitectura de Clase Mundial
              </h3>
              <div id="architectureInfo" className="prose max-w-none"></div>
            </div>
          </div>
        </div>

        {/* Enhanced Technical Details with World-Class Architecture */}
        <div className="mt-12 bg-gradient-to-r from-gray-100 to-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">
            <i className="fas fa-cogs mr-2"></i>
            Arquitectura Técnica de Clase Mundial
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
            <div>
              <strong>Modelo Base:</strong> SCM Legal 250M (Conceptual Reasoning + LoRA Fine-tuning)
            </div>
            <div>
              <strong>Arquitectura:</strong> Microservicios + API Gateway + Load Balancing + Circuit Breakers
            </div>
            <div>
              <strong>Jurisdicciones:</strong> Multi-jurisdiccional AR/ES/CL/UY con mapeo conceptual cross-border
            </div>
            <div>
              <strong>Integración:</strong> Fuentes oficiales (BOE, InfoLEG, LeyChile) + Vector DB + Edge Computing
            </div>
          </div>
        </div>

        {/* World-Class Features Overview */}
        <div className="mt-8 grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-globe text-blue-600 text-xl"></i>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Multi-Jurisdiccional</h4>
            <p className="text-gray-600 text-sm">Arquitectura inspirada en Tolgee para análisis legal comparativo</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-network-wired text-green-600 text-xl"></i>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Microservicios</h4>
            <p className="text-gray-600 text-sm">Patrones del System Design Primer para escalabilidad</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-database text-purple-600 text-xl"></i>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">APIs Públicas</h4>
            <p className="text-gray-600 text-sm">Framework de integración con fuentes legales oficiales</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-yellow-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-graduation-cap text-yellow-600 text-xl"></i>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Estructura Académica</h4>
            <p className="text-gray-600 text-sm">Documentación y metodología de clase mundial</p>
          </div>
        </div>
      </div>

      <script src="/static/scm-legal-app.js"></script>
    </div>
  )
});

// Error handler with enhanced logging
app.onError((error, c) => {
  console.error('Application error:', {
    error: error.message,
    stack: error.stack,
    requestId: c.get('requestId'),
    url: c.req.url,
    method: c.req.method,
  });

  return c.json({
    error: 'Internal server error',
    requestId: c.get('requestId'),
    message: error.message,
    timestamp: new Date().toISOString(),
  }, 500);
});

// 404 handler with request tracking
app.notFound((c) => {
  return c.json({
    error: 'Not found',
    path: c.req.url,
    method: c.req.method,
    requestId: c.get('requestId'),
    suggestion: 'Check available endpoints: /health, /api/jurisdictions, /api/legal/analyze',
  }, 404);
});

export default app;