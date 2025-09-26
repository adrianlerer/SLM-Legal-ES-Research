// 🚀 Context Engineering Frontend - World-Class Implementation
// Paul Iusztin Framework Integration UI

let currentSession = `session-${Date.now()}`;

async function submitQuery() {
    const query = document.getElementById('legalQuery').value.trim();
    const jurisdiction = document.getElementById('jurisdiction').value;
    const enableHallGuard = document.getElementById('enableHallGuard').checked;
    const requireCitations = document.getElementById('requireCitations').checked;
    
    // Get complexity level from new UI element
    const complexity = document.getElementById('complexity')?.value || 'medium';
    
    if (!query) {
        alert('Por favor, ingrese una consulta legal.');
        return;
    }
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch('/api/context-engineering/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                jurisdiction,
                sessionId: currentSession,
                complexity,
                enableAdvancedOptimization: true,
                enableHallGuard,
                requireCitations
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayContextEngineeringResults(data);
        } else {
            displayError(data.error || 'Error desconocido');
        }
        
    } catch (error) {
        console.error('Error:', error);
        displayError('Error de conexión con el servidor');
    }
}

function showLoading() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.className = 'block';
    resultsDiv.innerHTML = `
        <div class="bg-white rounded-lg shadow-lg p-6 text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p class="text-gray-600">🧠 Context Engineering procesando...</p>
            <p class="text-sm text-gray-500 mt-2">5-Memory System • YAML Optimization • Degradation Prevention</p>
        </div>
    `;
}

function displayContextEngineeringResults(data) {
    const resultsDiv = document.getElementById('results');
    
    // Main answer section
    const answerHtml = `
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-xl font-semibold text-gray-800">
                    <i class="fas fa-balance-scale mr-2"></i>
                    Respuesta Legal - Context Engineering
                </h3>
                <div class="flex space-x-2">
                    <span class="bg-${getDecisionColor(data.decision)}-100 text-${getDecisionColor(data.decision)}-800 px-3 py-1 rounded-full text-sm font-medium">
                        ${data.decision}
                    </span>
                    <span class="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">
                        ${data.contextEngineering.framework}
                    </span>
                </div>
            </div>
            
            <div class="prose max-w-none mb-4">
                ${formatLegalAnswer(data.answer)}
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">${data.confidence.toFixed(2)}</div>
                    <div class="text-sm text-gray-500">Confidence</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">${data.contextEngineering.performance.processingTime}ms</div>
                    <div class="text-sm text-gray-500">Processing</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">${data.contextEngineering.performance.tokenEfficiency.toFixed(1)}%</div>
                    <div class="text-sm text-gray-500">Token Efficiency</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-orange-600">${data.contextEngineering.performance.qualityScore.toFixed(2)}</div>
                    <div class="text-sm text-gray-500">Context Quality</div>
                </div>
            </div>
        </div>
    `;
    
    // Context Engineering metrics
    const contextMetricsHtml = `
        <div class="grid md:grid-cols-3 gap-6 mb-6">
            <!-- 5-Memory System -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h4 class="text-lg font-semibold mb-3 text-gray-800">
                    <i class="fas fa-brain mr-2"></i>
                    5-Memory System
                </h4>
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Long-term:</span>
                        <span class="text-sm font-medium">${data.contextEngineering.memory.longTerm.corpusSize} docs</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Short-term:</span>
                        <span class="text-sm font-medium">${data.contextEngineering.memory.shortTerm.contextDocs} docs</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Episodic:</span>
                        <span class="text-sm font-medium">${data.contextEngineering.memory.episodic.patterns} patterns</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Working:</span>
                        <span class="text-sm font-medium">${data.contextEngineering.memory.working.informationBudget.toFixed(0)} budget</span>
                    </div>
                    <div class="pt-2 border-t">
                        <span class="text-xs text-green-600 font-medium">✅ All memory types active</span>
                    </div>
                </div>
            </div>
            
            <!-- Optimization Results -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h4 class="text-lg font-semibold mb-3 text-gray-800">
                    <i class="fas fa-rocket mr-2"></i>
                    Optimization Results
                </h4>
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">YAML Savings:</span>
                        <span class="text-sm font-medium text-green-600">${data.contextEngineering.optimization.yamlTokenSavings}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Docs Optimized:</span>
                        <span class="text-sm font-medium">${data.contextEngineering.optimization.documentsOptimized}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Tokens Saved:</span>
                        <span class="text-sm font-medium text-blue-600">${data.contextEngineering.optimization.tokensSaved}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Strategies:</span>
                        <span class="text-sm font-medium">${data.contextEngineering.optimization.strategiesApplied.length}</span>
                    </div>
                    ${data.contextEngineering.optimization.strategiesApplied.length > 0 ? 
                        `<div class="pt-2 border-t">
                            <div class="text-xs text-blue-600">Applied: ${data.contextEngineering.optimization.strategiesApplied.join(', ')}</div>
                        </div>` : ''
                    }
                </div>
            </div>
            
            <!-- Risk Metrics Enhanced -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h4 class="text-lg font-semibold mb-3 text-gray-800">
                    <i class="fas fa-shield-alt mr-2"></i>
                    EDFL + Context Risk
                </h4>
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">RoH Bound:</span>
                        <span class="text-sm font-medium ${data.riskMetrics.rohBound <= 0.05 ? 'text-green-600' : 'text-red-600'}">
                            ${(data.riskMetrics.rohBound * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">ISR Ratio:</span>
                        <span class="text-sm font-medium ${data.riskMetrics.isrRatio >= 1.0 ? 'text-green-600' : 'text-orange-600'}">
                            ${data.riskMetrics.isrRatio.toFixed(2)}
                        </span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Info Budget:</span>
                        <span class="text-sm font-medium">${data.riskMetrics.informationBudget.toFixed(0)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Context Quality:</span>
                        <span class="text-sm font-medium text-purple-600">${(data.riskMetrics.contextQuality * 100).toFixed(1)}%</span>
                    </div>
                    <div class="pt-2 border-t">
                        <div class="text-xs text-gray-600">${data.riskMetrics.rationale}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Citations with hierarchy info
    const citationsHtml = `
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h4 class="text-lg font-semibold mb-3 text-gray-800">
                <i class="fas fa-book mr-2"></i>
                Citas Jurídicas con Jerarquía
            </h4>
            <div class="space-y-3">
                ${data.citations.map((citation, index) => `
                    <div class="flex items-center p-3 bg-gray-50 rounded-lg">
                        <span class="w-6 h-6 bg-blue-600 text-white rounded-full text-xs flex items-center justify-center mr-3">
                            ${index + 1}
                        </span>
                        <span class="flex-1 text-sm font-medium text-gray-700">${citation}</span>
                        <span class="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                            Jerarquía Legal
                        </span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // System insights
    const insightsHtml = `
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
            <h4 class="text-lg font-semibold mb-3 text-gray-800">
                <i class="fas fa-lightbulb mr-2"></i>
                Context Engineering Insights
            </h4>
            
            <div class="grid md:grid-cols-2 gap-6 mb-4">
                <div>
                    <h5 class="font-medium text-gray-700 mb-2">Token Utilization</h5>
                    <div class="bg-white rounded p-3 space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span>Used:</span> <span class="font-medium">${data.insights.tokenUtilization.used}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Saved:</span> <span class="font-medium text-green-600">${data.insights.tokenUtilization.saved}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Efficiency:</span> <span class="font-medium text-blue-600">${data.insights.tokenUtilization.efficiency}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Utilization:</span> <span class="font-medium">${data.insights.tokenUtilization.utilizationRate.toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h5 class="font-medium text-gray-700 mb-2">System Health</h5>
                    <div class="bg-white rounded p-3 space-y-1 text-sm">
                        <div class="flex justify-between">
                            <span>Status:</span> 
                            <span class="font-medium ${getHealthColor(data.insights.systemHealth.status)}">${data.insights.systemHealth.status}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Avg Tokens:</span> 
                            <span class="font-medium">${data.insights.systemHealth.metrics.averageTokens || 'N/A'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Peak Tokens:</span> 
                            <span class="font-medium">${data.insights.systemHealth.metrics.peakTokens || 'N/A'}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded p-4">
                <h6 class="font-medium text-gray-700 mb-2">Recommendations</h6>
                <ul class="text-sm text-gray-600 space-y-1">
                    ${data.insights.recommendations.map(rec => `
                        <li class="flex items-start">
                            <i class="fas fa-check-circle text-green-500 mr-2 mt-0.5 text-xs"></i>
                            ${rec}
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <div class="mt-4 p-3 bg-blue-100 rounded text-sm">
                <strong>🧠 Context Engineering Certification:</strong> 
                Framework ${data.certification.framework} | 
                Hash: <code>${data.certification.hash}</code> | 
                Timestamp: ${new Date(data.certification.timestamp).toLocaleString()}
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = answerHtml + contextMetricsHtml + citationsHtml + insightsHtml;
    resultsDiv.className = 'block';
}

function getDecisionColor(decision) {
    return decision === 'ANSWER' ? 'green' : 'red';
}

function getHealthColor(status) {
    const colors = {
        'optimal': 'text-green-600',
        'good': 'text-blue-600', 
        'warning': 'text-yellow-600',
        'critical': 'text-red-600'
    };
    return colors[status] || 'text-gray-600';
}

function formatLegalAnswer(answer) {
    return answer
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^(.*)$/, '<p>$1</p>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/Context Engineering/g, '<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">Context Engineering</span>');
}

function displayError(error) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-6">
            <div class="flex">
                <i class="fas fa-exclamation-triangle text-red-400 mr-3"></i>
                <div>
                    <h3 class="text-lg font-medium text-red-800">Error en Context Engineering</h3>
                    <p class="text-red-700 mt-1">${error}</p>
                </div>
            </div>
        </div>
    `;
    resultsDiv.className = 'block';
}

// Check system status on page load
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/context-engineering/status');
        const data = await response.json();
        
        console.log('Context Engineering System Status:', data);
        
        // Update UI with system status if there's a status indicator
        const statusIndicator = document.getElementById('systemStatus');
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <span class="text-green-600">✅ Context Engineering Active</span>
                <span class="text-xs text-gray-500 ml-2">
                    ${data.capabilities['5MemoryArchitecture']} | 
                    ${data.capabilities['YAMLOptimization']}
                </span>
            `;
        }
    } catch (error) {
        console.warn('Could not check Context Engineering status:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    checkSystemStatus();
    
    // Add complexity selector if not exists
    const querySection = document.querySelector('.bg-white.rounded-lg.shadow-lg .mb-4:last-of-type');
    if (querySection && !document.getElementById('complexity')) {
        const complexityHtml = `
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Complejidad de Consulta (Context Engineering):
                </label>
                <select id="complexity" class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                    <option value="simple">Simple - 4K tokens, compresión media</option>
                    <option value="medium" selected>Media - 8K tokens, compresión ligera</option>
                    <option value="complex">Compleja - 16K tokens, sin compresión</option>
                </select>
            </div>
        `;
        querySection.insertAdjacentHTML('beforebegin', complexityHtml);
    }
    
    // Add system status indicator
    const header = document.querySelector('h1');
    if (header && !document.getElementById('systemStatus')) {
        header.insertAdjacentHTML('afterend', '<div id="systemStatus" class="text-center mb-4"></div>');
    }
});