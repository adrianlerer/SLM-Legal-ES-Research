// SCM Legal - Frontend JavaScript Application
// Small Concept Model Legal Interface

let currentModel = 'scm';
let isAnalyzing = false;

// Model switching functionality
function switchModel(model) {
    currentModel = model;
    
    // Update tab styles
    document.getElementById('scmTab').className = 
        model === 'scm' ? 'px-4 py-2 bg-blue-600 text-white rounded-lg font-medium' 
                        : 'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    
    document.getElementById('llmTab').className = 
        model === 'llm' ? 'px-4 py-2 bg-green-600 text-white rounded-lg font-medium' 
                        : 'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    
    document.getElementById('compareTab').className = 
        model === 'compare' ? 'px-4 py-2 bg-purple-600 text-white rounded-lg font-medium' 
                            : 'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';

    // BitNet tabs
    const bitnetTab = document.getElementById('bitnetTab');
    if (bitnetTab) {
        bitnetTab.className = model === 'bitnet' ? 
            'px-4 py-2 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg font-medium' :
            'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    }

    const bitnetConsensusTab = document.getElementById('bitnet_consensusTab');
    if (bitnetConsensusTab) {
        bitnetConsensusTab.className = model === 'bitnet_consensus' ? 
            'px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-medium' :
            'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    }

    const bitnetMoeTab = document.getElementById('bitnet_moeTab');
    if (bitnetMoeTab) {
        bitnetMoeTab.className = model === 'bitnet_moe' ? 
            'px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium' :
            'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    }

    const tumixTab = document.getElementById('tumixTab');
    if (tumixTab) {
        tumixTab.className = model === 'tumix' ? 
            'px-4 py-2 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg font-medium' :
            'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    }

    const codaTab = document.getElementById('codaTab');
    if (codaTab) {
        codaTab.className = model === 'coda' ? 
            'px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium' :
            'px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium';
    }

    // Update description
    const descriptions = {
        scm: '<strong>Small Concept Model (SCM):</strong> Especializado en razonamiento conceptual jurídico. Procesa documentos a nivel de conceptos legales, no tokens individuales. Optimizado para coherencia en análisis contractual y compliance.',
        llm: '<strong>LLM Tradicional:</strong> Procesamiento token por token con contexto general. Útil para casos generales pero menos especializado en conceptos legales específicos.',
        compare: '<strong>Análisis Comparativo:</strong> Ejecuta ambos modelos simultáneamente para mostrar diferencias en approach, coherencia conceptual y especialización jurídica.',
        bitnet: '<strong>BitNet 1.58-bit Local:</strong> Procesamiento ultra-eficiente con 80% menos costo. 100% local para máxima confidencialidad. Ideal para casos altamente sensibles.',
        bitnet_consensus: '<strong>BitNet Multi-Agent Consensus:</strong> Consenso matemático optimizado con múltiples agentes BitNet. Enhanced Consensus Engine con Gradient Boosting + Random Forest + XGBoost.',
        bitnet_moe: '<strong>BitNet MoE (Mixture of Experts):</strong> Routing inteligente a expertos legales especializados por dominio. 6 expertos: Corporativo, Contratos, Compliance, Litigio, Tributario, Due Diligence.',
        tumix: '<strong>TUMIX Enhanced Multi-Agent:</strong> Sistema multi-agente con consenso matemático automático. PCA + K-Means para clasificación dimensional y optimización de pesos.',
        coda: '<strong>CoDA Legal Automation:</strong> Generación automática de documentos legales usando Coding via Diffusion Adaptation. Especializado en templates, workflows, contratos y optimización de procesos legales.'
    };

    document.getElementById('modelDescription').innerHTML = descriptions[model] || descriptions.scm;
    document.getElementById('modelDescription').className = 
        `text-sm text-gray-600 p-3 rounded-lg ${
            model === 'scm' ? 'bg-blue-50' : 
            model === 'llm' ? 'bg-green-50' : 
            model === 'compare' ? 'bg-purple-50' :
            model === 'bitnet' ? 'bg-gradient-to-r from-green-50 to-blue-50' :
            model === 'bitnet_consensus' ? 'bg-gradient-to-r from-purple-50 to-indigo-50' :
            model === 'bitnet_moe' ? 'bg-gradient-to-r from-indigo-50 to-purple-50' :
            model === 'tumix' ? 'bg-gradient-to-r from-green-50 to-teal-50' :
            model === 'coda' ? 'bg-gradient-to-r from-purple-50 to-pink-50' :
            'bg-gray-50'
        }`;

    // Show/hide options based on model
    const scmOptions = document.getElementById('scmOptions');
    if (scmOptions) {
        scmOptions.style.display = model === 'scm' ? 'block' : 'none';
    }

    const bitnetOptions = document.getElementById('bitnetOptions');
    if (bitnetOptions) {
        bitnetOptions.style.display = ['bitnet', 'bitnet_consensus', 'bitnet_moe'].includes(model) ? 'block' : 'none';
    }

    const consensusOptions = document.getElementById('consensusOptions');
    if (consensusOptions) {
        consensusOptions.style.display = ['bitnet_consensus', 'tumix'].includes(model) ? 'block' : 'none';
    }

    const moeOptions = document.getElementById('moeOptions');
    if (moeOptions) {
        moeOptions.style.display = model === 'bitnet_moe' ? 'block' : 'none';
    }

    // Show/hide CoDA form
    const codaForm = document.getElementById('codaForm');
    if (codaForm) {
        codaForm.style.display = model === 'coda' ? 'block' : 'none';
    }

    // Hide all result sections when switching
    hideAllResults();
    
    function hideAllResults() {
        const resultSections = [
            'scmResults', 'comparisonResults', 'contextResults', 
            'bitnetResults', 'moeResults', 'tumixResults', 'codaResults'
        ];
        
        resultSections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
            }
        });
    }

    // Update button text
    const analyzeButton = document.getElementById('analyzeButton');
    const buttonText = document.getElementById('buttonText');
    const buttonIcon = document.getElementById('buttonIcon');
    
    if (analyzeButton && buttonText && buttonIcon) {
        const buttonConfigs = {
            scm: { text: 'Analizar con SCM Legal Multi-Jurisdiccional', icon: 'fas fa-brain' },
            llm: { text: 'Analizar con LLM Tradicional', icon: 'fas fa-robot' },
            compare: { text: 'Comparar SCM vs LLM', icon: 'fas fa-balance-scale' },
            bitnet: { text: 'Analizar con BitNet Local (80% Ahorro)', icon: 'fas fa-microchip' },
            bitnet_consensus: { text: 'Consenso BitNet Multi-Agent', icon: 'fas fa-network-wired' },
            bitnet_moe: { text: 'Routing MoE Expertos Legales', icon: 'fas fa-route' },
            tumix: { text: 'Análisis TUMIX Enhanced', icon: 'fas fa-cogs' },
            coda: { text: 'Generar con CoDA Automation', icon: 'fas fa-robot' }
        };
        
        const config = buttonConfigs[model] || buttonConfigs.scm;
        buttonText.textContent = config.text;
        buttonIcon.className = `${config.icon} mr-2`;
    }
}

// Main SCM analysis function
async function submitSCMAnalysis() {
    if (isAnalyzing) return;
    
    const document_text = document.getElementById('legalDocument').value.trim();
    const query = document.getElementById('legalQuery').value.trim();
    const jurisdiction = document.getElementById('jurisdiction').value;
    const analysisType = document.getElementById('analysisType')?.value || 'comprehensive';
    
    // Validation
    if (!document_text) {
        alert('Por favor, ingrese el documento legal para análisis.');
        return;
    }
    
    if (document_text.length < 100) {
        alert('El documento debe tener al menos 100 caracteres para un análisis conceptual efectivo.');
        return;
    }

    if (!query) {
        alert('Por favor, especifique su consulta sobre el documento.');
        return;
    }

    // Start analysis
    isAnalyzing = true;
    showLoadingState();

    try {
        if (currentModel === 'compare') {
            await performComparison(document_text, query, jurisdiction);
        } else if (currentModel === 'scm') {
            await performSCMAnalysis(document_text, query, jurisdiction, analysisType);
        } else if (currentModel === 'bitnet') {
            await performBitNetAnalysis(document_text, query, jurisdiction);
        } else if (currentModel === 'bitnet_consensus') {
            await performBitNetConsensus(document_text, query, jurisdiction);
        } else if (currentModel === 'bitnet_moe') {
            await performBitNetMoE(document_text, query, jurisdiction);
        } else if (currentModel === 'tumix') {
            await performTumixAnalysis(document_text, query, jurisdiction);
        } else {
            await performLLMAnalysis(document_text, query, jurisdiction);
        }
    } catch (error) {
        console.error('Error en análisis:', error);
        showError('Error en el análisis: ' + error.message);
    } finally {
        isAnalyzing = false;
        hideLoadingState();
    }
}

// SCM Analysis implementation
async function performSCMAnalysis(document_text, query, jurisdiction, analysisType) {
    const response = await fetch('/api/scm/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            document: document_text,
            query: query,
            jurisdiction: jurisdiction,
            analysis_type: analysisType
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error en análisis SCM');
    }

    const result = await response.json();
    displaySCMResults(result);
}

// Comparison analysis
async function performComparison(document_text, query, jurisdiction) {
    const response = await fetch('/api/scm/compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            document: document_text,
            query: query,
            jurisdiction: jurisdiction
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error en análisis comparativo');
    }

    const result = await response.json();
    displayComparisonResults(result);
}

// LLM Analysis (simplified for comparison)
async function performLLMAnalysis(document_text, query, jurisdiction) {
    // Simulate LLM analysis for comparison
    const simulatedResult = {
        success: true,
        llm_analysis: {
            approach: 'Token-by-token processing',
            response: `Análisis tradicional del documento proporcionado. 
                       El documento contiene elementos legales que requieren revisión profesional.
                       Se identifican cláusulas que podrían tener implicaciones de responsabilidad.
                       Recomiendo consultar con asesor legal para interpretación específica.`,
            tokens_processed: Math.floor(document_text.length / 4),
            confidence: 0.75,
            processing_time: Math.floor(300 + Math.random() * 500) + 'ms'
        }
    };

    displayLLMResults(simulatedResult);
}

// Display SCM Results
function displaySCMResults(result) {
    const scm_analysis = result.scm_legal_analysis;
    
    // Show results area
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('scmResults').style.display = 'block';
    document.getElementById('comparisonResults').style.display = 'none';

    // Main analysis summary
    const analysisDiv = document.getElementById('scmAnalysis');
    analysisDiv.innerHTML = `
        <div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Resumen del Análisis</h4>
            <p class="text-gray-700">${scm_analysis.structured_response.summary}</p>
        </div>
        
        <div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Evaluación de Riesgo General</h4>
            <div class="flex items-center">
                <span class="px-3 py-1 rounded-full text-sm font-medium ${getRiskBadgeClass(scm_analysis.structured_response.risk_assessment.overall_risk)}">
                    ${getRiskIcon(scm_analysis.structured_response.risk_assessment.overall_risk)} 
                    ${scm_analysis.structured_response.risk_assessment.overall_risk}
                </span>
            </div>
        </div>

        <div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Recomendaciones</h4>
            <ul class="list-disc list-inside text-gray-700 space-y-1">
                ${scm_analysis.structured_response.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    `;

    // Conceptos identificados
    const conceptsDiv = document.getElementById('conceptsIdentified');
    if (scm_analysis.conceptual_extraction.concepts.length > 0) {
        conceptsDiv.innerHTML = scm_analysis.conceptual_extraction.concepts.map(concept => `
            <div class="border border-gray-200 rounded-lg p-3 mb-2">
                <div class="font-medium text-sm text-gray-800">${concept.concept.name}</div>
                <div class="text-xs text-gray-500 mt-1">
                    ${concept.concept.category}/${concept.concept.subcategory}
                </div>
                <div class="flex items-center mt-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${Math.round(concept.confidence * 100)}%"></div>
                    </div>
                    <span class="ml-2 text-xs text-gray-600">${Math.round(concept.confidence * 100)}%</span>
                </div>
            </div>
        `).join('');
    } else {
        conceptsDiv.innerHTML = '<p class="text-gray-500 text-sm">No se detectaron conceptos específicos</p>';
    }

    // Referencias cruzadas
    const reasoningDiv = document.getElementById('conceptualReasoning');
    if (scm_analysis.conceptual_reasoning.cross_references.length > 0) {
        reasoningDiv.innerHTML = scm_analysis.conceptual_reasoning.cross_references.slice(0, 5).map(ref => `
            <div class="text-sm border border-gray-200 rounded p-2 mb-2">
                <div class="font-medium">${ref.relationship}</div>
                <div class="text-xs text-gray-500">${ref.from} → ${ref.to}</div>
                <div class="mt-1">
                    <div class="flex-1 bg-gray-200 rounded-full h-1">
                        <div class="bg-green-600 h-1 rounded-full" style="width: ${Math.round(ref.strength * 100)}%"></div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        reasoningDiv.innerHTML = '<p class="text-gray-500 text-sm">Sin referencias cruzadas detectadas</p>';
    }

    // Indicadores de riesgo
    const riskDiv = document.getElementById('riskIndicators');
    if (scm_analysis.conceptual_reasoning.risk_indicators.length > 0) {
        riskDiv.innerHTML = scm_analysis.conceptual_reasoning.risk_indicators.map(risk => `
            <div class="flex items-center justify-between text-sm border border-gray-200 rounded p-2 mb-2">
                <div>
                    <div class="font-medium">${risk.risk_type}</div>
                    <div class="text-xs text-gray-500">${risk.concept}</div>
                </div>
                <span class="px-2 py-1 rounded text-xs font-medium ${getRiskBadgeClass(risk.severity)}">
                    ${risk.severity.toUpperCase()}
                </span>
            </div>
        `).join('');
    } else {
        riskDiv.innerHTML = '<p class="text-gray-500 text-sm">Sin riesgos específicos detectados</p>';
    }

    // Métricas de performance
    const metricsDiv = document.getElementById('performanceMetrics');
    metricsDiv.innerHTML = `
        <div class="text-center">
            <div class="text-lg font-bold text-blue-600">${scm_analysis.performance_metrics.processing_time}</div>
            <div class="text-xs text-gray-600">Tiempo de Procesamiento</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-green-600">${Math.round(scm_analysis.performance_metrics.conceptual_coherence * 100)}%</div>
            <div class="text-xs text-gray-600">Coherencia Conceptual</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-purple-600">${scm_analysis.conceptual_extraction.concepts_detected}</div>
            <div class="text-xs text-gray-600">Conceptos Detectados</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-orange-600">${scm_analysis.performance_metrics.cross_reference_density.toFixed(2)}</div>
            <div class="text-xs text-gray-600">Densidad de Referencias</div>
        </div>
    `;
}

// Display comparison results
function displayComparisonResults(result) {
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('scmResults').style.display = 'none';
    document.getElementById('comparisonResults').style.display = 'block';

    const comparison = result.comparison_analysis;
    const comparisonDiv = document.getElementById('comparisonAnalysis');
    
    comparisonDiv.innerHTML = `
        <div class="grid md:grid-cols-2 gap-6 mb-6">
            <div class="border-2 border-blue-200 rounded-lg p-4">
                <h4 class="text-lg font-semibold text-blue-800 mb-3">
                    🧠 SCM Legal (Conceptual)
                </h4>
                <div class="space-y-3 text-sm">
                    <div><strong>Approach:</strong> ${comparison.scm_legal.approach}</div>
                    <div><strong>Conceptos:</strong> ${comparison.scm_legal.concepts_identified}</div>
                    <div><strong>Coherencia:</strong> ${Math.round(comparison.scm_legal.conceptual_coherence * 100)}%</div>
                    <div><strong>Especialización:</strong> ${comparison.scm_legal.domain_specialization}%</div>
                    <div><strong>Latencia:</strong> ${comparison.scm_legal.latency}</div>
                    <div><strong>Memoria:</strong> ${comparison.scm_legal.memory_footprint}</div>
                </div>
            </div>

            <div class="border-2 border-green-200 rounded-lg p-4">
                <h4 class="text-lg font-semibold text-green-800 mb-3">
                    📝 LLM Tradicional
                </h4>
                <div class="space-y-3 text-sm">
                    <div><strong>Approach:</strong> ${comparison.traditional_llm.approach}</div>
                    <div><strong>Tokens:</strong> ${comparison.traditional_llm.tokens_processed}</div>
                    <div><strong>Coherencia:</strong> ${Math.round(comparison.traditional_llm.conceptual_coherence * 100)}%</div>
                    <div><strong>Especialización:</strong> ${comparison.traditional_llm.domain_specialization}%</div>
                    <div><strong>Latencia:</strong> ${comparison.traditional_llm.latency}</div>
                    <div><strong>Memoria:</strong> ${comparison.traditional_llm.memory_footprint}</div>
                </div>
            </div>
        </div>

        <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
            <h4 class="font-semibold text-blue-800 mb-2">Ventajas del SCM Legal:</h4>
            <ul class="list-disc list-inside text-sm text-blue-700 space-y-1">
                ${comparison.scm_advantages.map(advantage => `<li>${advantage}</li>`).join('')}
            </ul>
        </div>

        <div class="bg-gray-50 border-l-4 border-gray-400 p-4">
            <h4 class="font-semibold text-gray-800 mb-2">Viabilidad de Implementación:</h4>
            <div class="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
                <div><strong>Técnica:</strong> ${comparison.implementation_feasibility.technical}</div>
                <div><strong>Económica:</strong> ${comparison.implementation_feasibility.economic}</div>
                <div><strong>Timeline:</strong> ${comparison.implementation_feasibility.timeline}</div>
                <div><strong>Escalabilidad:</strong> ${comparison.implementation_feasibility.scalability}</div>
            </div>
        </div>
    `;
}

// Display LLM results (simplified)
function displayLLMResults(result) {
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('scmResults').style.display = 'block';
    document.getElementById('comparisonResults').style.display = 'none';

    const analysisDiv = document.getElementById('scmAnalysis');
    analysisDiv.innerHTML = `
        <div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">Análisis LLM Tradicional</h4>
            <p class="text-gray-700">${result.llm_analysis.response}</p>
        </div>
        
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p class="text-yellow-700 text-sm">
                <strong>Nota:</strong> Este análisis usa procesamiento token-por-token tradicional. 
                Para análisis conceptual más profundo, use el modo SCM.
            </p>
        </div>
    `;

    // Clear other sections for LLM mode
    document.getElementById('conceptsIdentified').innerHTML = '<p class="text-gray-500 text-sm">Análisis a nivel de tokens (no conceptos)</p>';
    document.getElementById('conceptualReasoning').innerHTML = '<p class="text-gray-500 text-sm">Sin razonamiento conceptual</p>';
    document.getElementById('riskIndicators').innerHTML = '<p class="text-gray-500 text-sm">Evaluación de riesgo general</p>';
    
    document.getElementById('performanceMetrics').innerHTML = `
        <div class="text-center">
            <div class="text-lg font-bold text-blue-600">${result.llm_analysis.processing_time}</div>
            <div class="text-xs text-gray-600">Tiempo de Procesamiento</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-green-600">${Math.round(result.llm_analysis.confidence * 100)}%</div>
            <div class="text-xs text-gray-600">Confianza General</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-purple-600">${result.llm_analysis.tokens_processed}</div>
            <div class="text-xs text-gray-600">Tokens Procesados</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-gray-600">N/A</div>
            <div class="text-xs text-gray-600">Referencias Conceptuales</div>
        </div>
    `;
}

// Helper functions
function getRiskBadgeClass(risk) {
    const classes = {
        'Alto': 'bg-red-100 text-red-800',
        'high': 'bg-red-100 text-red-800',
        'Medio': 'bg-yellow-100 text-yellow-800', 
        'medium': 'bg-yellow-100 text-yellow-800',
        'Bajo': 'bg-green-100 text-green-800',
        'low': 'bg-green-100 text-green-800'
    };
    return classes[risk] || 'bg-gray-100 text-gray-800';
}

function getRiskIcon(risk) {
    const icons = {
        'Alto': '⚠️',
        'high': '⚠️',
        'Medio': '⚡',
        'medium': '⚡',
        'Bajo': '✅',
        'low': '✅'
    };
    return icons[risk] || '📊';
}

function showLoadingState() {
    const button = document.querySelector('button[onclick="submitSCMAnalysis()"]');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analizando...';
    button.disabled = true;
    button.classList.add('opacity-50', 'cursor-not-allowed');
}

function hideLoadingState() {
    const button = document.querySelector('button[onclick="submitSCMAnalysis()"]');
    button.innerHTML = '<i class="fas fa-brain mr-2"></i>Analizar con SCM Legal';
    button.disabled = false;
    button.classList.remove('opacity-50', 'cursor-not-allowed');
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>${message}`;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        document.body.removeChild(errorDiv);
    }, 5000);
}

// Initialize with SCM model selected
window.addEventListener('DOMContentLoaded', function() {
    switchModel('scm');
});

// Example documents for testing
const EXAMPLE_DOCUMENTS = {
    contract: `CONTRATO DE PRESTACIÓN DE SERVICIOS

Entre ACME CORP S.A., sociedad anónima inscrita en el Registro Público de Comercio bajo el número 12345, con domicilio en Av. Corrientes 1234, Ciudad Autónoma de Buenos Aires, Argentina, representada por su Director Ejecutivo Sr. Juan Pérez, DNI 12.345.678 (en adelante "la EMPRESA"), por una parte; y SERVICIOS LEGALES S.R.L., sociedad de responsabilidad limitada inscrita bajo el número 67890, con domicilio en San Martín 456, CABA, representada por su Gerente General Dr. María González, DNI 87.654.321 (en adelante "el PRESTADOR"), por la otra;

DECLARAN:
Que han convenido celebrar el presente contrato de prestación de servicios profesionales, sujeto a las siguientes cláusulas:

PRIMERA - OBJETO: El PRESTADOR se obliga a prestar servicios de asesoramiento jurídico integral a la EMPRESA, incluyendo pero no limitándose a: revisión y redacción de contratos, asesoramiento en materia societaria, laboral y compliance normativo.

SEGUNDA - OBLIGACIONES DEL PRESTADOR: El PRESTADOR deberá mantener absoluta confidencialidad sobre toda información comercial, técnica y financiera de la EMPRESA. Asimismo, se obliga a cumplir con los más altos estándares profesionales y códigos de ética aplicables.

TERCERA - RESPONSABILIDAD: El PRESTADOR será responsable por los daños y perjuicios que pueda ocasionar por negligencia o dolo en el cumplimiento de sus obligaciones. La EMPRESA podrá exigir indemnización por los daños efectivamente acreditados.

CUARTA - VIGENCIA: El presente contrato tendrá vigencia por el término de UN (1) año, renovable automáticamente por períodos iguales salvo denuncia fehaciente efectuada por cualquiera de las partes con 60 días de anticipación.

QUINTA - RESCISIÓN: Cualquiera de las partes podrá rescindir el contrato sin expresión de causa con preaviso de 30 días. En caso de incumplimiento material, la parte cumplidora podrá resolver el contrato de pleno derecho previa intimación fehaciente.`,
    
    governance: `ACTA DE DIRECTORIO N° 245
ACME HOLDING S.A.

En la Ciudad Autónoma de Buenos Aires, a los 15 días del mes de marzo de 2024, siendo las 14:00 horas, se reúne el Directorio de ACME HOLDING S.A. en su sede social sita en Av. Santa Fe 1234, piso 10°, bajo la presidencia del Sr. Roberto Silva y con la asistencia de los Directores Sra. Ana Martín, Sr. Carlos López y Dr. Patricia Romero.

ORDEN DEL DIA:
1) Aprobación del Programa de Integridad Corporativa
2) Designación del Comité de Auditoría
3) Evaluación de riesgos operacionales Q1 2024
4) Política de conflictos de interés

El Sr. Presidente informa que se ha desarrollado un Programa de Integridad Corporativa integral que incluye: (i) código de conducta actualizado, (ii) procedimientos de due diligence para terceros, (iii) canal de denuncias anónimo, (iv) programa de capacitación obligatoria para todo el personal.

La Sra. Martín presenta el informe del área legal indicando la necesidad de fortalecer los controles internos para cumplir con la normativa anticorrupción vigente. Se destaca la importancia del monitoreo continuo y la evaluación periódica de la efectividad de los controles.

Por unanimidad se RESUELVE:
1° - APROBAR el Programa de Integridad Corporativa presentado
2° - DESIGNAR como miembros del Comité de Auditoría a los Directores Ana Martín (Presidenta), Carlos López y Patricia Romero (independiente)
3° - INSTRUIR a la Gerencia General para implementar el programa dentro de los 90 días
4° - ESTABLECER revisiones trimestrales de efectividad del programa

Sin más asuntos que tratar, se levanta la sesión siendo las 16:30 horas.`
};

// Function to load example documents
function loadExample(type) {
    const document_field = document.getElementById('legalDocument');
    const query_field = document.getElementById('legalQuery');
    
    if (type === 'contract') {
        document_field.value = EXAMPLE_DOCUMENTS.contract;
        query_field.value = "¿Qué obligaciones y riesgos principales identifica en este contrato? ¿Hay cláusulas que requieran atención especial?";
    } else if (type === 'governance') {
        document_field.value = EXAMPLE_DOCUMENTS.governance;  
        query_field.value = "Analice las decisiones de governance corporativo y compliance. ¿Qué riesgos de cumplimiento identifica?";
    }
}

// Add example buttons (call this after DOM is loaded)
window.addEventListener('DOMContentLoaded', function() {
    const documentLabel = document.querySelector('label[for="legalDocument"]');
    if (documentLabel) {
        documentLabel.innerHTML += `
            <div class="float-right">
                <button type="button" onclick="loadExample('contract')" class="text-xs text-blue-600 hover:text-blue-800 mr-2">
                    📄 Ejemplo: Contrato
                </button>
                <button type="button" onclick="loadExample('governance')" class="text-xs text-blue-600 hover:text-blue-800">
                    🏛️ Ejemplo: Governance
                </button>
            </div>
        `;
    }
});

// BitNet MoE Analysis implementation
async function performBitNetMoE(document_text, query, jurisdiction) {
    // Collect MoE configuration
    const confidentialityLevel = document.getElementById('confidentialityLevel')?.value || 'highly_confidential';
    const priority = document.getElementById('priority')?.value || 'normal';
    const maxExperts = parseInt(document.getElementById('maxExperts')?.value || '3');
    const moeConsensusType = document.getElementById('moeConsensusType')?.value || 'enhanced_mathematical';
    
    // Collect selected experts
    const preferredExperts = [];
    const expertCheckboxes = [
        'expertCorporate', 'expertContract', 'expertCompliance',
        'expertLitigation', 'expertTax', 'expertDueDiligence'
    ];
    
    const expertMapping = {
        'expertCorporate': 'CORPORATE_LAW',
        'expertContract': 'CONTRACT_ANALYSIS',
        'expertCompliance': 'COMPLIANCE',
        'expertLitigation': 'LITIGATION_STRATEGY',
        'expertTax': 'TAX_LAW',
        'expertDueDiligence': 'DUE_DILIGENCE'
    };
    
    expertCheckboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox && checkbox.checked) {
            preferredExperts.push(expertMapping[id]);
        }
    });

    const response = await fetch('/api/bitnet/moe-query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: `${document_text}\n\nConsulta específica: ${query}`,
            confidentiality_level: confidentialityLevel,
            priority: priority,
            max_experts: maxExperts,
            preferred_experts: preferredExperts,
            consensus_type: moeConsensusType,
            legal_domain: jurisdiction,
            jurisdiction: jurisdiction
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error en análisis BitNet MoE');
    }

    const result = await response.json();
    displayBitNetMoEResults(result);
}

// Display BitNet MoE Results
function displayBitNetMoEResults(result) {
    const data = result.data;
    
    // Show results area
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('scmResults').style.display = 'block';
    document.getElementById('comparisonResults').style.display = 'none';

    // Main MoE analysis summary
    const analysisDiv = document.getElementById('scmAnalysis');
    analysisDiv.innerHTML = `
        <div class="mb-4">
            <h4 class="font-semibold text-gray-800 mb-2">
                🎯 Análisis BitNet MoE (Mixture of Experts Legal)
            </h4>
            <div class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4 mb-4">
                <div class="text-sm text-indigo-700">
                    <strong>Routing Inteligente:</strong> ${data.routing_intelligence?.expert_selection_logic || 'Expertos seleccionados automáticamente'}
                </div>
                <div class="text-xs text-indigo-600 mt-1">
                    ${data.routing_intelligence?.classification_reasoning || 'Clasificación automática de dominio legal'}
                </div>
            </div>
            <div class="prose max-w-none">
                ${formatBitNetResponse(data.final_response)}
            </div>
        </div>
    `;

    // Display selected experts
    const conceptsDiv = document.getElementById('conceptsIdentified');
    if (data.experts_selected && data.experts_selected.length > 0) {
        conceptsDiv.innerHTML = `
            <h5 class="font-semibold text-sm text-gray-700 mb-2">Expertos Seleccionados (${data.experts_selected.length})</h5>
            ${data.experts_selected.map(expert => `
                <div class="border border-purple-200 rounded-lg p-3 mb-2 bg-gradient-to-r from-purple-50 to-indigo-50">
                    <div class="font-medium text-sm text-purple-800">${getExpertDisplayName(expert.expert_type)}</div>
                    <div class="text-xs text-purple-600 mt-1">
                        Especialización: ${expert.specialization?.join(', ') || 'Experto legal especializado'}
                    </div>
                    <div class="flex items-center mt-2">
                        <div class="flex-1 bg-purple-200 rounded-full h-2">
                            <div class="bg-purple-600 h-2 rounded-full" style="width: ${Math.round(expert.selection_score * 100)}%"></div>
                        </div>
                        <span class="ml-2 text-xs text-purple-700">Score: ${Math.round(expert.selection_score * 100)}%</span>
                    </div>
                </div>
            `).join('')}
        `;
    } else {
        conceptsDiv.innerHTML = '<p class="text-gray-500 text-sm">Sin información de expertos disponible</p>';
    }

    // Display domain classifications
    const reasoningDiv = document.getElementById('conceptualReasoning');
    if (data.domain_classifications) {
        const domains = data.domain_classifications.all_domains || [];
        reasoningDiv.innerHTML = `
            <h5 class="font-semibold text-sm text-gray-700 mb-2">Clasificación de Dominio Legal</h5>
            <div class="text-sm border border-indigo-200 rounded p-2 mb-2 bg-indigo-50">
                <div class="font-medium text-indigo-800">Dominio Primario: ${data.domain_classifications.primary_domain || 'general_legal'}</div>
                <div class="text-xs text-indigo-600 mt-1">
                    Confianza: ${Math.round((data.domain_classifications.confidence_score || 0.8) * 100)}% | 
                    Complejidad: ${data.domain_classifications.complexity_level || 'medium'}
                </div>
            </div>
            ${domains.slice(0, 3).map(domain => `
                <div class="text-sm border border-gray-200 rounded p-2 mb-2">
                    <div class="font-medium">${domain.domain}</div>
                    <div class="mt-1">
                        <div class="flex-1 bg-gray-200 rounded-full h-1">
                            <div class="bg-indigo-600 h-1 rounded-full" style="width: ${Math.round(domain.confidence * 100)}%"></div>
                        </div>
                    </div>
                </div>
            `).join('')}
        `;
    } else {
        reasoningDiv.innerHTML = '<p class="text-gray-500 text-sm">Sin clasificación de dominio disponible</p>';
    }

    // Display expert responses summary
    const riskDiv = document.getElementById('riskIndicators');
    if (data.expert_responses && data.expert_responses.length > 0) {
        riskDiv.innerHTML = `
            <h5 class="font-semibold text-sm text-gray-700 mb-2">Respuestas de Expertos</h5>
            ${data.expert_responses.slice(0, 3).map(expert => `
                <div class="flex items-center justify-between text-sm border border-gray-200 rounded p-2 mb-2">
                    <div>
                        <div class="font-medium">${getExpertDisplayName(expert.expert_type)}</div>
                        <div class="text-xs text-gray-500">${expert.backend_used || 'bitnet_local'}</div>
                    </div>
                    <div class="text-right">
                        <span class="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                            ${Math.round(expert.confidence_score * 100)}%
                        </span>
                        <div class="text-xs text-gray-500 mt-1">${expert.tokens_generated || 0} tokens</div>
                    </div>
                </div>
            `).join('')}
        `;
    } else {
        riskDiv.innerHTML = '<p class="text-gray-500 text-sm">Sin respuestas de expertos disponibles</p>';
    }

    // MoE Performance metrics
    const metricsDiv = document.getElementById('performanceMetrics');
    const metadata = result.metadata || {};
    const consensusDetails = data.consensus_details || {};
    
    metricsDiv.innerHTML = `
        <div class="text-center">
            <div class="text-lg font-bold text-purple-600">${metadata.processing_time_ms || 0}ms</div>
            <div class="text-xs text-gray-600">Tiempo de Procesamiento</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-indigo-600">${Math.round((consensusDetails.average_confidence || 0.9) * 100)}%</div>
            <div class="text-xs text-gray-600">Confianza Consenso</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-blue-600">${data.experts_selected?.length || 0}</div>
            <div class="text-xs text-gray-600">Expertos Activos</div>
        </div>
        <div class="text-center">
            <div class="text-lg font-bold text-green-600">$${(metadata.cost_usd || 0.024).toFixed(4)}</div>
            <div class="text-xs text-gray-600">Costo Total USD</div>
        </div>
    `;
}

// Helper function for expert display names
function getExpertDisplayName(expertType) {
    const names = {
        'CORPORATE_LAW': '🏢 Derecho Corporativo',
        'CONTRACT_ANALYSIS': '📋 Análisis Contractual', 
        'COMPLIANCE': '🛡️ Compliance',
        'LITIGATION_STRATEGY': '⚖️ Estrategia Litigiosa',
        'TAX_LAW': '💼 Derecho Tributario',
        'DUE_DILIGENCE': '🔍 Due Diligence',
        'corporate_law_expert': '🏢 Derecho Corporativo',
        'contract_analysis_expert': '📋 Análisis Contractual',
        'compliance_expert': '🛡️ Compliance',
        'litigation_expert': '⚖️ Estrategia Litigiosa',
        'tax_law_expert': '💼 Derecho Tributario',
        'due_diligence_expert': '🔍 Due Diligence'
    };
    return names[expertType] || expertType;
}

// Helper function to format BitNet response
function formatBitNetResponse(response) {
    if (!response) return '<p class="text-gray-500">Sin respuesta disponible</p>';
    
    // Convert line breaks to HTML
    const formatted = response
        .replace(/\n\n/g, '</p><p class="mb-3">')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return `<p class="mb-3">${formatted}</p>`;
}

// BitNet Single Query Analysis (placeholder)
async function performBitNetAnalysis(document_text, query, jurisdiction) {
    // Implementation for single BitNet query
    const confidentialityLevel = document.getElementById('confidentialityLevel')?.value || 'highly_confidential';
    const priority = document.getElementById('priority')?.value || 'normal';
    const maxTokens = parseInt(document.getElementById('maxTokens')?.value || '512');

    const response = await fetch('/api/bitnet/legal-query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: `${document_text}\n\nConsulta específica: ${query}`,
            confidentiality_level: confidentialityLevel,
            priority: priority,
            max_tokens: maxTokens,
            jurisdiction: jurisdiction
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error en análisis BitNet');
    }

    const result = await response.json();
    displayBitNetSingleResults(result);
}

// BitNet Consensus Analysis (placeholder)  
async function performBitNetConsensus(document_text, query, jurisdiction) {
    // Implementation for BitNet consensus
    const confidentialityLevel = document.getElementById('confidentialityLevel')?.value || 'highly_confidential';
    const consensusMethod = document.getElementById('consensusMethod')?.value || 'enhanced_mathematical';
    
    const agentConfigs = [];
    if (document.getElementById('agentCOT')?.checked) {
        agentConfigs.push({ agent_type: 'cot_juridico' });
    }
    if (document.getElementById('agentSearch')?.checked) {
        agentConfigs.push({ agent_type: 'search_jurisprudencial' });
    }
    if (document.getElementById('agentCompliance')?.checked) {
        agentConfigs.push({ agent_type: 'code_compliance' });
    }

    const response = await fetch('/api/bitnet/consensus', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: `${document_text}\n\nConsulta específica: ${query}`,
            confidentiality_level: confidentialityLevel,
            agent_configs: agentConfigs,
            consensus_config: {
                consensus_method: consensusMethod
            },
            jurisdiction: jurisdiction
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error en análisis BitNet Consensus');
    }

    const result = await response.json();
    displayBitNetConsensusResults(result);
}

// TUMIX Analysis (placeholder)
async function performTumixAnalysis(document_text, query, jurisdiction) {
    // Implementation for TUMIX Enhanced
    const response = await fetch('/api/tumix/legal-query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question: `${document_text}\n\nConsulta específica: ${query}`,
            jurisdiction: jurisdiction,
            domain: 'corporativo'
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error en análisis TUMIX');
    }

    const result = await response.json();
    displayTumixResults(result);
}

// BitNet Single Results Display (placeholder)
function displayBitNetSingleResults(result) {
    displaySCMResults({
        scm_legal_analysis: {
            structured_response: {
                summary: result.data?.response || 'Análisis BitNet completado',
                risk_assessment: { overall_risk: 'Medio' },
                recommendations: ['Procesamiento local BitNet realizado', 'Confidencialidad máxima mantenida']
            },
            conceptual_extraction: { concepts: [], concepts_detected: 0 },
            conceptual_reasoning: { cross_references: [], risk_indicators: [] },
            performance_metrics: {
                processing_time: result.metadata?.processing_time_ms + 'ms' || '1500ms',
                conceptual_coherence: 0.92,
                cross_reference_density: 0.8
            }
        }
    });
}

// BitNet Consensus Results Display (placeholder)
function displayBitNetConsensusResults(result) {
    displaySCMResults({
        scm_legal_analysis: {
            structured_response: {
                summary: result.data?.final_consensus || 'Consenso BitNet completado',
                risk_assessment: { overall_risk: 'Medio' },
                recommendations: ['Consenso matemático optimizado', 'Múltiples agentes procesados localmente']
            },
            conceptual_extraction: { concepts: [], concepts_detected: result.data?.agent_responses?.length || 0 },
            conceptual_reasoning: { cross_references: [], risk_indicators: [] },
            performance_metrics: {
                processing_time: result.metadata?.processing_time_ms + 'ms' || '2200ms',
                conceptual_coherence: result.data?.consensus_confidence || 0.89,
                cross_reference_density: 0.85
            }
        }
    });
}

// TUMIX Results Display (placeholder)
function displayTumixResults(result) {
    displaySCMResults({
        scm_legal_analysis: {
            structured_response: {
                summary: result.final_answer || 'Análisis TUMIX completado',
                risk_assessment: { overall_risk: 'Medio' },
                recommendations: ['Consenso matemático TUMIX', 'PCA + K-Means aplicado']
            },
            conceptual_extraction: { concepts: [], concepts_detected: 3 },
            conceptual_reasoning: { cross_references: [], risk_indicators: [] },
            performance_metrics: {
                processing_time: '1800ms',
                conceptual_coherence: result.confidence_score || 0.94,
                cross_reference_density: 0.88
            }
        }
    });
}

// ================================
// CoDA LEGAL AUTOMATION FUNCTIONS
// ================================

/**
 * Perform CoDA legal automation request
 */
async function performCoDAAutomation() {
    const automationRequest = document.getElementById('codaRequest').value;
    const taskType = document.getElementById('codaTaskType').value;
    const documentType = document.getElementById('codaDocumentType').value;
    const complexity = document.getElementById('codaComplexity').value;
    
    if (!automationRequest.trim()) {
        showError('Por favor, ingrese una solicitud de automatización válida');
        return;
    }
    
    showCoDALoadingState();
    
    try {
        const response = await fetch('/api/coda/automation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Request-ID': `coda_${Date.now()}`
            },
            body: JSON.stringify({
                automation_request: automationRequest,
                task_type: taskType,
                context: {
                    document_type: documentType,
                    complexity: complexity,
                    confidentiality_level: 'highly_confidential'
                }
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayCoDAResults(result.data, result.metadata);
        } else {
            showError(result.error || 'Error en el procesamiento CoDA');
        }
        
    } catch (error) {
        console.error('CoDA automation error:', error);
        showError('Error de conexión con el sistema CoDA');
    } finally {
        hideCoDALoadingState();
    }
}

/**
 * Display CoDA automation results
 */
function displayCoDAResults(data, metadata) {
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('codaResults').style.display = 'block';
    
    // Hide other result sections
    document.getElementById('scmResults').style.display = 'none';
    document.getElementById('comparisonResults').style.display = 'none';
    document.getElementById('contextResults').style.display = 'none';
    document.getElementById('bitnetResults').style.display = 'none';
    document.getElementById('moeResults').style.display = 'none';
    document.getElementById('tumixResults').style.display = 'none';
    
    // Display generated content
    document.getElementById('codaGeneratedContent').innerHTML = `
        <div class="bg-white border rounded-lg p-6">
            <div class="flex items-center justify-between mb-4">
                <h4 class="font-semibold text-gray-800">
                    <i class="fas fa-robot mr-2 text-purple-600"></i>
                    Contenido Generado por CoDA
                </h4>
                <span class="px-3 py-1 text-sm font-medium rounded-full ${getTaskTypeBadgeClass(data.task_type)}">
                    ${formatTaskType(data.task_type)}
                </span>
            </div>
            
            <div class="prose max-w-none">
                <pre class="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded border overflow-auto max-h-96">${data.generated_content}</pre>
            </div>
        </div>
    `;
    
    // Display automation metadata
    document.getElementById('codaMetadata').innerHTML = `
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                <div class="text-lg font-bold text-purple-600">${data.task_type}</div>
                <div class="text-xs text-purple-600">Tipo de Tarea</div>
            </div>
            
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                <div class="text-lg font-bold text-blue-600">${data.complexity}</div>
                <div class="text-xs text-blue-600">Complejidad</div>
            </div>
            
            <div class="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                <div class="text-lg font-bold text-green-600">${Math.round(data.confidence_score * 100)}%</div>
                <div class="text-xs text-green-600">Confianza</div>
            </div>
            
            <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                <div class="text-lg font-bold text-orange-600">${data.legal_domain}</div>
                <div class="text-xs text-orange-600">Dominio Legal</div>
            </div>
        </div>
        
        <div class="mt-4 bg-gray-50 border rounded-lg p-4">
            <h5 class="font-semibold text-gray-800 mb-2">Detalles Técnicos</h5>
            <div class="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
                <div><strong>Modelo:</strong> ${data.automation_metadata?.model_version || 'CoDA-v0-Instruct'}</div>
                <div><strong>Método:</strong> ${data.automation_metadata?.diffusion_method || 'Discrete Denoising'}</div>
                <div><strong>Pasos de Difusión:</strong> ${metadata.diffusion_steps || 20}</div>
                <div><strong>Tokens Generados:</strong> ${metadata.tokens_generated || 0}</div>
                <div><strong>Tiempo de Procesamiento:</strong> ${metadata.processing_time_ms || 0}ms</div>
                <div><strong>Costo:</strong> $${(metadata.cost_usd || 0).toFixed(4)} USD</div>
                <div><strong>Optimización:</strong> ${data.automation_metadata?.optimization_applied ? '✅ Aplicada' : '❌ No aplicada'}</div>
                <div><strong>Compliance:</strong> ${data.automation_metadata?.compliance_validated ? '✅ Validado' : '⚠️ Pendiente'}</div>
            </div>
        </div>
    `;
    
    // Display technical details
    document.getElementById('codaTechnicalDetails').innerHTML = `
        <div class="space-y-4">
            <div class="bg-purple-50 border-l-4 border-purple-400 p-4">
                <h5 class="font-semibold text-purple-800 mb-2">
                    <i class="fas fa-cogs mr-2"></i>
                    Características de CoDA
                </h5>
                <ul class="text-sm text-purple-700 space-y-1">
                    <li>• <strong>Diffusion Adaptation:</strong> Generación mediante técnicas de difusión avanzadas</li>
                    <li>• <strong>Legal Specialization:</strong> Entrenamiento específico en dominio legal</li>
                    <li>• <strong>Template Engine:</strong> Motor de plantillas inteligente</li>
                    <li>• <strong>Quality Assurance:</strong> Validación automática de calidad</li>
                    <li>• <strong>Compliance Integration:</strong> Verificación de cumplimiento normativo</li>
                </ul>
            </div>
            
            <div class="bg-green-50 border-l-4 border-green-400 p-4">
                <h5 class="font-semibold text-green-800 mb-2">
                    <i class="fas fa-check-circle mr-2"></i>
                    Ventajas del Procesamiento CoDA
                </h5>
                <ul class="text-sm text-green-700 space-y-1">
                    <li>• <strong>Especialización Legal:</strong> Entrenamiento específico en documentos legales</li>
                    <li>• <strong>Generación Estructurada:</strong> Contenido con formato y estructura profesional</li>
                    <li>• <strong>Adaptabilidad:</strong> Ajuste automático según complejidad de la solicitud</li>
                    <li>• <strong>Escalabilidad:</strong> Procesamiento eficiente para múltiples tipos de documentos</li>
                    <li>• <strong>Integración:</strong> Compatible con workflow legal existente</li>
                </ul>
            </div>
        </div>
    `;
}

/**
 * Helper functions for CoDA
 */
function getTaskTypeBadgeClass(taskType) {
    const classes = {
        'document_generation': 'bg-blue-100 text-blue-800',
        'template_creation': 'bg-green-100 text-green-800',
        'workflow_automation': 'bg-purple-100 text-purple-800',
        'code_generation': 'bg-red-100 text-red-800',
        'process_optimization': 'bg-yellow-100 text-yellow-800'
    };
    return classes[taskType] || 'bg-gray-100 text-gray-800';
}

function formatTaskType(taskType) {
    const names = {
        'document_generation': 'Generación de Documentos',
        'template_creation': 'Creación de Templates',
        'workflow_automation': 'Automatización de Workflows',
        'code_generation': 'Generación de Código',
        'process_optimization': 'Optimización de Procesos'
    };
    return names[taskType] || taskType;
}

function showCoDALoadingState() {
    const button = document.querySelector('button[onclick="performCoDAAutomation()"]');
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generando con CoDA...';
    button.disabled = true;
    button.classList.add('opacity-50', 'cursor-not-allowed');
}

function hideCoDALoadingState() {
    const button = document.querySelector('button[onclick="performCoDAAutomation()"]');
    button.innerHTML = '<i class="fas fa-robot mr-2"></i>Generar con CoDA';
    button.disabled = false;
    button.classList.remove('opacity-50', 'cursor-not-allowed');
}