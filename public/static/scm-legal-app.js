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

    // Update description
    const descriptions = {
        scm: '<strong>Small Concept Model (SCM):</strong> Especializado en razonamiento conceptual jurídico. Procesa documentos a nivel de conceptos legales, no tokens individuales. Optimizado para coherencia en análisis contractual y compliance.',
        llm: '<strong>LLM Tradicional:</strong> Procesamiento token por token con contexto general. Útil para casos generales pero menos especializado en conceptos legales específicos.',
        compare: '<strong>Análisis Comparativo:</strong> Ejecuta ambos modelos simultáneamente para mostrar diferencias en approach, coherencia conceptual y especialización jurídica.'
    };

    document.getElementById('modelDescription').innerHTML = descriptions[model];
    document.getElementById('modelDescription').className = 
        `text-sm text-gray-600 p-3 rounded-lg ${
            model === 'scm' ? 'bg-blue-50' : 
            model === 'llm' ? 'bg-green-50' : 'bg-purple-50'
        }`;

    // Show/hide options based on model
    const scmOptions = document.getElementById('scmOptions');
    if (scmOptions) {
        scmOptions.style.display = model === 'scm' ? 'block' : 'none';
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