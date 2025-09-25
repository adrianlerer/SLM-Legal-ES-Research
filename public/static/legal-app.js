// Legal SLM Frontend Application
class LegalSLMApp {
  constructor() {
    this.isQuerying = false
    this.initializeEventListeners()
  }

  initializeEventListeners() {
    // Submit on Enter key
    document.getElementById('legalQuery')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        this.submitQuery()
      }
    })
  }

  async submitQuery() {
    if (this.isQuerying) return
    
    const query = document.getElementById('legalQuery')?.value?.trim()
    const jurisdiction = document.getElementById('jurisdiction')?.value || 'AR'
    const enableHallGuard = document.getElementById('enableHallGuard')?.checked ?? true
    const requireCitations = document.getElementById('requireCitations')?.checked ?? true

    if (!query) {
      this.showError('Por favor, ingrese una consulta legal.')
      return
    }

    this.isQuerying = true
    this.showLoading()

    try {
      const response = await fetch('/api/legal/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          jurisdiction,
          enableHallGuard,
          requireCitations
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Error en la consulta')
      }

      this.displayResults(data)
      
    } catch (error) {
      console.error('Query error:', error)
      this.showError(`Error: ${error.message}`)
    } finally {
      this.isQuerying = false
      this.hideLoading()
    }
  }

  showLoading() {
    const button = document.querySelector('button')
    if (button) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...'
      button.disabled = true
    }
  }

  hideLoading() {
    const button = document.querySelector('button')
    if (button) {
      button.innerHTML = '<i class="fas fa-search mr-2"></i>Consultar SLM Legal'
      button.disabled = false
    }
  }

  displayResults(data) {
    // Show results section
    const resultsSection = document.getElementById('results')
    if (resultsSection) {
      resultsSection.classList.remove('hidden')
    }

    // Display legal answer
    this.displayAnswer(data.answer, data.warning)
    
    // Display citations
    this.displayCitations(data.citations || [])
    
    // Display risk metrics
    this.displayRiskMetrics(data.riskMetrics)
    
    // Scroll to results
    resultsSection?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  displayAnswer(answer, warning) {
    const answerDiv = document.getElementById('legalAnswer')
    if (!answerDiv) return

    let html = ''
    
    if (warning) {
      html += `
        <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <i class="fas fa-exclamation-triangle text-red-400"></i>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-700"><strong>ADVERTENCIA:</strong> ${warning}</p>
            </div>
          </div>
        </div>
      `
    }

    // Convert markdown-like formatting to HTML
    const formattedAnswer = answer
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '</p><p class="mb-3">')
      .replace(/\n/g, '<br>')

    html += `<div class="text-gray-800 leading-relaxed"><p class="mb-3">${formattedAnswer}</p></div>`
    
    answerDiv.innerHTML = html
  }

  displayCitations(citations) {
    const citationsDiv = document.getElementById('citations')
    if (!citationsDiv) return

    if (citations.length === 0) {
      citationsDiv.innerHTML = `
        <div class="text-gray-500 italic">
          <i class="fas fa-info-circle mr-2"></i>
          No se encontraron citas específicas
        </div>
      `
      return
    }

    const citationsHtml = citations
      .sort((a, b) => a.hierarchy - b.hierarchy) // Sort by legal hierarchy
      .map(citation => {
        const hierarchyLabel = this.getHierarchyLabel(citation.hierarchy)
        const hierarchyColor = this.getHierarchyColor(citation.hierarchy)
        
        return `
          <div class="border-l-4 ${hierarchyColor} bg-gray-50 p-3 mb-2">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="font-medium text-gray-900">${citation.text}</div>
                <div class="text-sm text-gray-600 mt-1">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                    ${hierarchyLabel}
                  </span>
                  <span class="text-gray-500">Relevancia: ${citation.relevance}%</span>
                </div>
              </div>
            </div>
          </div>
        `
      })
      .join('')

    citationsDiv.innerHTML = citationsHtml
  }

  displayRiskMetrics(metrics) {
    const metricsDiv = document.getElementById('riskMetrics')
    if (!metricsDiv || !metrics) return

    const riskColor = this.getRiskColor(metrics.rohBound)
    const decisionColor = metrics.decision === 'ANSWER' ? 'text-green-600' : 'text-red-600'
    const decisionIcon = metrics.decision === 'ANSWER' ? 'fa-check-circle' : 'fa-times-circle'

    const metricsHtml = `
      <div class="space-y-3">
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <span class="text-sm font-medium">Decisión:</span>
          <span class="${decisionColor} font-bold">
            <i class="fas ${decisionIcon} mr-1"></i>
            ${metrics.decision}
          </span>
        </div>
        
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <span class="text-sm font-medium">Riesgo de Alucinación:</span>
          <span class="${riskColor} font-bold">
            ${(metrics.rohBound * 100).toFixed(1)}%
          </span>
        </div>
        
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <span class="text-sm font-medium">Presupuesto Info:</span>
          <span class="text-gray-800 font-mono text-sm">
            ${metrics.informationBudget?.toFixed(2)} bits
          </span>
        </div>
        
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
          <span class="text-sm font-medium">ISR Ratio:</span>
          <span class="text-gray-800 font-mono text-sm">
            ${metrics.isrRatio?.toFixed(2)}
          </span>
        </div>
        
        <div class="text-xs text-gray-600 p-3 bg-gray-50 rounded">
          <strong>Análisis:</strong> ${metrics.rationale}
        </div>
        
        <div class="text-xs text-gray-500 p-2 bg-gray-100 rounded font-mono">
          Certificado: ${metrics.certificateHash}
        </div>
      </div>
    `

    metricsDiv.innerHTML = metricsHtml
  }

  getHierarchyLabel(hierarchy) {
    switch (hierarchy) {
      case 1: return 'Constitución'
      case 2: return 'Código'
      case 3: return 'Ley'
      case 4: return 'Decreto'
      case 5: return 'Resolución'
      default: return 'Norma'
    }
  }

  getHierarchyColor(hierarchy) {
    switch (hierarchy) {
      case 1: return 'border-purple-500'
      case 2: return 'border-blue-500' 
      case 3: return 'border-green-500'
      case 4: return 'border-yellow-500'
      case 5: return 'border-gray-500'
      default: return 'border-gray-400'
    }
  }

  getRiskColor(rohBound) {
    if (rohBound <= 0.05) return 'text-green-600'
    if (rohBound <= 0.15) return 'text-yellow-600'
    return 'text-red-600'
  }

  showError(message) {
    const resultsSection = document.getElementById('results')
    if (resultsSection) {
      resultsSection.classList.remove('hidden')
      resultsSection.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-6">
          <div class="flex items-center">
            <i class="fas fa-exclamation-triangle text-red-500 mr-3"></i>
            <div>
              <h3 class="text-lg font-medium text-red-800">Error</h3>
              <p class="text-red-700">${message}</p>
            </div>
          </div>
        </div>
      `
      resultsSection.scrollIntoView({ behavior: 'smooth' })
    }
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.legalSLM = new LegalSLMApp()
})

// Global function for button onclick
function submitQuery() {
  if (window.legalSLM) {
    window.legalSLM.submitQuery()
  }
}