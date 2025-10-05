// SLM Legal Spanish - Frontend Application Logic

class LegalAnalyzer {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupDropZone();
    this.showWelcomeMessage();
  }

  setupEventListeners() {
    // Analyze document button
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', () => this.handleAnalyzeDocument());
    }

    // Compliance check button
    const complianceBtn = document.getElementById('compliance-btn');
    if (complianceBtn) {
      complianceBtn.addEventListener('click', () => this.handleComplianceCheck());
    }

    // Risk assessment button
    const riskBtn = document.getElementById('risk-btn');
    if (riskBtn) {
      riskBtn.addEventListener('click', () => this.handleRiskAssessment());
    }

    // Guardrails button
    const guardrailsBtn = document.getElementById('guardrails-btn');
    if (guardrailsBtn) {
      guardrailsBtn.addEventListener('click', () => this.handleGuardrailsValidation());
    }

    // Safe analysis button
    const safeAnalysisBtn = document.getElementById('safe-analysis-btn');
    if (safeAnalysisBtn) {
      safeAnalysisBtn.addEventListener('click', () => this.handleSafeAnalysis());
    }

    // Metrics button
    const metricsBtn = document.getElementById('metrics-btn');
    if (metricsBtn) {
      metricsBtn.addEventListener('click', () => this.handleGuardrailsMetrics());
    }

    // File input change
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
      fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
    }
  }

  setupDropZone() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    
    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drop-zone-active');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('drop-zone-active');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drop-zone-active');
      
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    });
  }

  showWelcomeMessage() {
    console.log('🏛️ SLM Legal Spanish - Sistema iniciado');
    console.log('📋 Especializado en Análisis Legal y Compliance');
    
    // Show a subtle notification
    this.showNotification('Sistema legal inteligente activado', 'info', 3000);
  }

  async handleAnalyzeDocument() {
    const btn = document.getElementById('analyze-btn');
    const originalText = btn.textContent;
    
    try {
      btn.innerHTML = '<span class="loading-spinner mr-2"></span>Analizando...';
      btn.disabled = true;

      // Simulate document analysis with the uploaded PDF
      const response = await axios.post('/api/analyze-document', {
        document_url: 'https://page.gensparksite.com/get_upload_url/28364bd1e30b64e4fd23279a4e6d423eef56d2fe805b76bdf82f987083319dbe/default/e1b72850-1384-4716-9cff-02945f95e3ef',
        analysis_type: 'academic_legal'
      });

      this.displayResults('Análisis de Documento Académico', response.data);
      
    } catch (error) {
      console.error('Error analyzing document:', error);
      this.showNotification('Error al analizar el documento', 'error');
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

  async handleComplianceCheck() {
    const btn = document.getElementById('compliance-btn');
    const originalText = btn.textContent;
    
    try {
      btn.innerHTML = '<span class="loading-spinner mr-2"></span>Verificando...';
      btn.disabled = true;

      const sampleText = `
        Transformer-based language models have demonstrated impressive capabilities 
        across a range of complex reasoning tasks. This research explores the 
        learnability of compositional functions and their application in legal analysis.
      `;

      const response = await axios.post('/api/compliance-check', {
        text: sampleText,
        jurisdiction: 'ES'
      });

      this.displayResults('Verificación de Compliance', response.data);
      
    } catch (error) {
      console.error('Error in compliance check:', error);
      this.showNotification('Error en verificación de compliance', 'error');
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

  async handleRiskAssessment() {
    this.showNotification('Evaluación de riesgos - Funcionalidad en desarrollo', 'warning');
    
    const mockRiskData = {
      assessment_id: Math.random().toString(36).substring(7),
      risk_level: 'medium',
      categories: [
        { name: 'Riesgo Regulatorio', level: 'medium', description: 'Normativas emergentes en IA' },
        { name: 'Riesgo Operacional', level: 'low', description: 'Procesos establecidos' },
        { name: 'Riesgo Reputacional', level: 'high', description: 'Impacto potencial significativo' }
      ],
      recommendations: [
        'Establecer comité de governance para IA',
        'Implementar políticas de transparencia',
        'Desarrollar framework de auditoría'
      ],
      assessed_at: new Date().toISOString()
    };

    this.displayResults('Evaluación de Riesgos', mockRiskData);
  }

  async handleGuardrailsValidation() {
    const btn = document.getElementById('guardrails-btn');
    const originalText = btn.textContent;
    
    try {
      btn.innerHTML = '<span class="loading-spinner mr-2"></span>Validando...';
      btn.disabled = true;

      const sampleOutput = {
        summary: 'Análisis legal completado con IA',
        findings: ['Aplicación correcta de normativas', 'Identificación de riesgos apropiada'],
        legal_implications: ['Cumplimiento de marcos regulatorios', 'Transparencia en procesos']
      };

      const response = await axios.post('/api/guardrails/validate', {
        output_text: JSON.stringify(sampleOutput),
        analysis_type: 'comprehensive',
        guardrail_specs: ['legal_accuracy', 'compliance_safety', 'corporate_governance']
      });

      this.displayGuardrailResults('Validación de Guardrails', response.data);
      
    } catch (error) {
      console.error('Error in guardrails validation:', error);
      this.showNotification('Error en validación de guardrails', 'error');
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

  async handleSafeAnalysis() {
    const btn = document.getElementById('safe-analysis-btn');
    const originalText = btn.textContent;
    
    try {
      btn.innerHTML = '<span class="loading-spinner mr-2"></span>Analizando con Guardrails...';
      btn.disabled = true;

      const sampleContent = `
        El presente documento establece el marco de gobierno corporativo aplicable 
        a sociedades cotizadas conforme a la Ley de Sociedades de Capital y el 
        Código de Buen Gobierno. Se analizan las responsabilidades del consejo de 
        administración en materia de supervisión y control de riesgos corporativos.
      `;

      const response = await axios.post('/api/guardrails/safe-analysis', {
        document_content: sampleContent,
        analysis_type: 'comprehensive',
        jurisdiction: 'ES',
        enable_guardrails: true
      });

      this.displaySafeAnalysisResults('Análisis Seguro con Guardrails', response.data);
      
    } catch (error) {
      console.error('Error in safe analysis:', error);
      this.showNotification('Error en análisis seguro', 'error');
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

  async handleGuardrailsMetrics() {
    const btn = document.getElementById('metrics-btn');
    const originalText = btn.textContent;
    
    try {
      btn.innerHTML = '<span class="loading-spinner mr-2"></span>Cargando métricas...';
      btn.disabled = true;

      const response = await axios.get('/api/guardrails/metrics');
      this.displayMetrics('Métricas de Rendimiento de Guardrails', response.data);
      
    } catch (error) {
      console.error('Error loading metrics:', error);
      this.showNotification('Error cargando métricas', 'error');
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  }

  handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
      this.processFile(file);
    }
  }

  processFile(file) {
    // Validate file
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    
    if (file.size > maxSize) {
      this.showNotification('El archivo es demasiado grande (máx. 10MB)', 'error');
      return;
    }

    if (!allowedTypes.includes(file.type)) {
      this.showNotification('Formato de archivo no admitido', 'error');
      return;
    }

    this.showNotification(`Archivo "${file.name}" cargado correctamente`, 'success');
    
    // Simulate file processing
    setTimeout(() => {
      this.showNotification('Procesando documento con IA...', 'info');
      setTimeout(() => {
        this.handleAnalyzeDocument();
      }, 1000);
    }, 500);
  }

  displayResults(title, data) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    if (!resultsSection || !resultsContent) return;

    let html = `<h3 class="text-xl font-semibold text-gray-800 mb-4">${title}</h3>`;
    
    if (data.summary) {
      html += `
        <div class="result-item bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
          <h4 class="font-semibold text-blue-800 mb-2">
            <i class="fas fa-info-circle mr-2"></i>Resumen
          </h4>
          <p class="text-blue-700">${data.summary}</p>
        </div>
      `;
    }

    if (data.key_findings) {
      html += `
        <div class="result-item bg-green-50 border-l-4 border-green-400 p-4 mb-4">
          <h4 class="font-semibold text-green-800 mb-2">
            <i class="fas fa-search mr-2"></i>Hallazgos Principales
          </h4>
          <ul class="text-green-700 space-y-1">
            ${data.key_findings.map(finding => `<li>• ${finding}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (data.legal_implications) {
      html += `
        <div class="result-item bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
          <h4 class="font-semibold text-yellow-800 mb-2">
            <i class="fas fa-balance-scale mr-2"></i>Implicaciones Legales
          </h4>
          <ul class="text-yellow-700 space-y-1">
            ${data.legal_implications.map(implication => `<li>• ${implication}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (data.findings) {
      html += `
        <div class="result-item bg-orange-50 border-l-4 border-orange-400 p-4 mb-4">
          <h4 class="font-semibold text-orange-800 mb-2">
            <i class="fas fa-exclamation-triangle mr-2"></i>Observaciones de Compliance
          </h4>
          <ul class="text-orange-700 space-y-1">
            ${data.findings.map(finding => `<li>• ${finding}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (data.recommendations) {
      html += `
        <div class="result-item bg-purple-50 border-l-4 border-purple-400 p-4 mb-4">
          <h4 class="font-semibold text-purple-800 mb-2">
            <i class="fas fa-lightbulb mr-2"></i>Recomendaciones
          </h4>
          <ul class="text-purple-700 space-y-1">
            ${data.recommendations.map(rec => `<li>• ${rec}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (data.risk_level) {
      const riskColor = data.risk_level === 'high' ? 'red' : data.risk_level === 'medium' ? 'yellow' : 'green';
      html += `
        <div class="result-item bg-gray-50 border-l-4 border-gray-400 p-4 mb-4">
          <h4 class="font-semibold text-gray-800 mb-2">
            <i class="fas fa-chart-line mr-2"></i>Nivel de Riesgo
          </h4>
          <span class="compliance-badge ${data.risk_level}">
            <i class="fas fa-shield-alt"></i>
            ${data.risk_level.toUpperCase()}
          </span>
        </div>
      `;
    }

    // Add timestamp
    const timestamp = data.processed_at || data.checked_at || data.assessed_at || new Date().toISOString();
    html += `
      <div class="text-sm text-gray-500 mt-6">
        <i class="fas fa-clock mr-1"></i>
        Procesado: ${dayjs(timestamp).format('DD/MM/YYYY HH:mm:ss')}
      </div>
    `;

    resultsContent.innerHTML = html;
    resultsSection.classList.remove('hidden');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  showNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `
      fixed top-4 right-4 z-50 max-w-sm bg-white border-l-4 rounded-lg shadow-lg p-4 
      transform translate-x-full transition-transform duration-300
      ${type === 'success' ? 'border-green-400' : ''}
      ${type === 'error' ? 'border-red-400' : ''}
      ${type === 'warning' ? 'border-yellow-400' : ''}
      ${type === 'info' ? 'border-blue-400' : ''}
    `;
    
    const iconClass = {
      success: 'fas fa-check-circle text-green-500',
      error: 'fas fa-exclamation-circle text-red-500',
      warning: 'fas fa-exclamation-triangle text-yellow-500',
      info: 'fas fa-info-circle text-blue-500'
    }[type] || 'fas fa-info-circle text-blue-500';
    
    notification.innerHTML = `
      <div class="flex items-start">
        <i class="${iconClass} mr-3 mt-1"></i>
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-800">${message}</p>
        </div>
        <button class="ml-3 text-gray-400 hover:text-gray-600" onclick="this.parentElement.parentElement.remove()">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto hide
    if (duration > 0) {
      setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
      }, duration);
    }
  }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new LegalAnalyzer();
});

// Global error handler
window.addEventListener('error', (e) => {
  console.error('Application error:', e.error);
});

// Service health check
async function checkServiceHealth() {
  try {
    const response = await axios.get('/api/health');
    console.log('✅ Service health:', response.data);
  } catch (error) {
    console.error('❌ Service health check failed:', error);
  }
}

  displayGuardrailResults(title, data) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    if (!resultsSection || !resultsContent) return;

    let html = `<h3 class="text-xl font-semibold text-gray-800 mb-4">${title}</h3>`;
    
    // Overall validation status
    const overallStatus = data.overall_valid ? 'passed' : 'failed';
    const statusColor = overallStatus === 'passed' ? 'green' : 'red';
    
    html += `
      <div class="result-item bg-${statusColor}-50 border-l-4 border-${statusColor}-400 p-4 mb-4">
        <h4 class="font-semibold text-${statusColor}-800 mb-2">
          <i class="fas fa-shield-alt mr-2"></i>Estado General de Validación
        </h4>
        <p class="text-${statusColor}-700">
          <span class="font-bold">${overallStatus.toUpperCase()}</span> - 
          ${data.guardrails_applied.length} guardrails aplicados
        </p>
      </div>
    `;

    // Individual guardrail results
    if (data.results && data.results.length > 0) {
      html += `
        <div class="result-item bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
          <h4 class="font-semibold text-blue-800 mb-3">
            <i class="fas fa-list-check mr-2"></i>Resultados Detallados
          </h4>
      `;
      
      data.results.forEach((result, index) => {
        const resultColor = result.is_valid ? 'text-green-600' : 'text-red-600';
        const icon = result.is_valid ? 'fa-check-circle' : 'fa-exclamation-triangle';
        
        html += `
          <div class="mb-3 p-3 bg-white rounded border">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium ${resultColor}">
                <i class="fas ${icon} mr-1"></i>
                Guardrail ${index + 1}
              </span>
              <span class="text-sm text-gray-600">
                Confianza: ${Math.round(result.confidence * 100)}%
              </span>
            </div>
            
            ${result.violations && result.violations.length > 0 ? `
              <div class="text-sm text-red-600 mb-1">
                <strong>Violaciones:</strong>
                <ul class="list-disc list-inside ml-2">
                  ${result.violations.map(v => `<li>${v}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
            
            ${result.recommendations && result.recommendations.length > 0 ? `
              <div class="text-sm text-blue-600">
                <strong>Recomendaciones:</strong>
                <ul class="list-disc list-inside ml-2">
                  ${result.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
          </div>
        `;
      });
      
      html += `</div>`;
    }

    // Add timestamp
    html += `
      <div class="text-sm text-gray-500 mt-6">
        <i class="fas fa-clock mr-1"></i>
        Validado: ${dayjs(data.timestamp).format('DD/MM/YYYY HH:mm:ss')}
      </div>
    `;

    resultsContent.innerHTML = html;
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  displaySafeAnalysisResults(title, data) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    if (!resultsSection || !resultsContent) return;

    let html = `<h3 class="text-xl font-semibold text-gray-800 mb-4">${title}</h3>`;
    
    // Safety score
    const safetyScore = Math.round(data.guardrails.safety_score * 100);
    const scoreColor = safetyScore >= 80 ? 'green' : safetyScore >= 60 ? 'yellow' : 'red';
    
    html += `
      <div class="result-item bg-${scoreColor}-50 border-l-4 border-${scoreColor}-400 p-4 mb-4">
        <h4 class="font-semibold text-${scoreColor}-800 mb-2">
          <i class="fas fa-shield-alt mr-2"></i>Puntuación de Seguridad
        </h4>
        <div class="flex items-center space-x-4">
          <span class="text-2xl font-bold text-${scoreColor}-700">${safetyScore}%</span>
          <span class="text-${scoreColor}-700">
            ${data.guardrails.validation_passed ? 'Todas las validaciones pasadas' : 'Algunas validaciones fallaron'}
          </span>
        </div>
      </div>
    `;

    // Analysis results
    if (data.analysis) {
      this.displayResults('Análisis Principal', data.analysis);
      return; // Use existing display method for main analysis
    }

    // Guardrails logs
    if (data.guardrails.logs && data.guardrails.logs.length > 0) {
      html += `
        <div class="result-item bg-purple-50 border-l-4 border-purple-400 p-4 mb-4">
          <h4 class="font-semibold text-purple-800 mb-3">
            <i class="fas fa-clipboard-list mr-2"></i>Log de Guardrails
          </h4>
      `;
      
      data.guardrails.logs.forEach(log => {
        const logColor = log.status === 'passed' ? 'text-green-600' : 'text-red-600';
        const icon = log.status === 'passed' ? 'fa-check' : 'fa-times';
        
        html += `
          <div class="mb-2 p-2 bg-white rounded border flex items-center justify-between">
            <span class="font-medium ${logColor}">
              <i class="fas ${icon} mr-1"></i>
              ${log.guardrail}
            </span>
            <span class="text-sm text-gray-600">
              ${Math.round(log.confidence * 100)}% confianza
            </span>
          </div>
        `;
      });
      
      html += `</div>`;
    }

    resultsContent.innerHTML = html;
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  displayMetrics(title, data) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    if (!resultsSection || !resultsContent) return;

    let html = `<h3 class="text-xl font-semibold text-gray-800 mb-4">${title}</h3>`;
    
    // Overall metrics
    html += `
      <div class="grid md:grid-cols-3 gap-4 mb-6">
        <div class="bg-blue-50 p-4 rounded-lg text-center">
          <div class="text-2xl font-bold text-blue-700">${data.total_validations.toLocaleString()}</div>
          <div class="text-sm text-blue-600">Total Validaciones</div>
        </div>
        <div class="bg-green-50 p-4 rounded-lg text-center">
          <div class="text-2xl font-bold text-green-700">${Math.round(data.success_rate * 100)}%</div>
          <div class="text-sm text-green-600">Tasa de Éxito</div>
        </div>
        <div class="bg-purple-50 p-4 rounded-lg text-center">
          <div class="text-2xl font-bold text-purple-700">${Math.round(data.average_confidence * 100)}%</div>
          <div class="text-sm text-purple-600">Confianza Promedio</div>
        </div>
      </div>
    `;

    // Guardrail performance
    html += `
      <div class="result-item bg-gray-50 border-l-4 border-gray-400 p-4 mb-4">
        <h4 class="font-semibold text-gray-800 mb-3">
          <i class="fas fa-chart-bar mr-2"></i>Rendimiento por Guardrail
        </h4>
        <div class="space-y-3">
    `;
    
    Object.entries(data.guardrail_performance).forEach(([name, perf]) => {
      html += `
        <div class="bg-white p-3 rounded border">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium capitalize">${name.replace('_', ' ')}</span>
            <span class="text-sm text-green-600">${Math.round(perf.success_rate * 100)}% éxito</span>
          </div>
          <div class="text-xs text-gray-600 grid grid-cols-2 gap-2">
            <span>Invocaciones: ${perf.invocations.toLocaleString()}</span>
            <span>Tiempo promedio: ${perf.avg_processing_time}</span>
          </div>
        </div>
      `;
    });
    
    html += `
        </div>
      </div>
    `;

    // Fail actions
    html += `
      <div class="result-item bg-orange-50 border-l-4 border-orange-400 p-4 mb-4">
        <h4 class="font-semibold text-orange-800 mb-3">
          <i class="fas fa-exclamation-triangle mr-2"></i>Acciones de Fallo
        </h4>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
    `;
    
    Object.entries(data.fail_actions_taken).forEach(([action, count]) => {
      html += `
        <div class="bg-white p-2 rounded text-center border">
          <div class="font-bold text-orange-700">${count}</div>
          <div class="text-orange-600 capitalize">${action}</div>
        </div>
      `;
    });
    
    html += `
        </div>
      </div>
    `;

    resultsContent.innerHTML = html;
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }
}

// Run health check on load
checkServiceHealth();