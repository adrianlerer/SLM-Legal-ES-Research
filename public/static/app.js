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

// Run health check on load
checkServiceHealth();