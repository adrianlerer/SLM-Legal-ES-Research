# SCM Legal ES→Multi (Small/Smart Concept Model)

## Visión General

Sistema de IA Legal especializado en español con extensión multiregional, basado en arquitectura SCM (Small/Smart Concept Model) con integración de técnicas de vanguardia para procesamiento legal.

## Arquitectura Tecnológica

### Pilares Fundamentales [Verificado]
- **Transformer/Attention**: Base arquitectural moderna
- **BERT (MLM)**: Masked Language Modeling para comprensión contextual
- **GPT-3 (few-shot)**: Aprendizaje con pocos ejemplos
- **Scaling Laws**: Principios de escalabilidad eficiente
- **Chain-of-Thought/Self-Consistency**: Razonamiento estructurado
- **LLaMA/open**: Modelos abiertos como base

### Extensiones SCM/LCM [Verificado]
- **Ventanas largas**: RoPE con YaRN (64k–128k) y LongRoPE para casos extremos
- **Razonamiento controlado**: Self-Consistency + Tree-of-Thoughts + thought rollback
- **RAG moderno**: GraphRAG (comunidades/hubs) + Self-RAG (recuperación inteligente)
- **Ajuste eficiente**: QLoRA (NF4, double quant.) + DPO para estilo jurídico
- **Curación de datos**: Calidad sobre volumen + desduplicación + índice externo

### Arquitectura Objetivo [Inferencia]
**SCM Legal**: LLM 7B–13B ajustado en ES-AR + GraphRAG + Self-RAG + cita obligatoria + YaRN 64k, expandible a ES LatAm/EU y multilenguaje.

## Argentina (federal)

### Cobertura Jurisdiccional
- **Jurisdicción canónica**: ISO 3166-2:AR (subnacional) con alias prácticos
- **Ingesta Nacional**: CSJN/SAIJ/BORA/InfoLEG  
- **Ingesta Provincial**: CABA/PBA/Santa Fe/Córdoba/Mendoza (stubs activos)
- **Normalización ELI**: European Legislation Identifier adaptado
- **Política de cita obligatoria**: Pinpoint por artículo/capítulo o sumario oficial

### Retrieval por Jurisdicción (AR)
- **Province-aware router**: Selección automática de índice por ISO 3166-2:AR
- **Fallback jerárquico**: Provincia → Nacional AR → España → Global ES-LatAm-EU
- **Clasificación heurística**: Detección automática de jurisdicción desde query
- **Self-RAG integration**: Decisión inteligente de recuperación + citation enforcer

### Retrieval por Jurisdicción (AR)
- **Province-aware router**: Selección automática de índice por ISO 3166-2:AR
- **Fallback jerárquico**: Provincia → AR nacional → ES → GLOBAL  
- **Clasificación inteligente**: Detección heurística desde query (boletín/geográfico/ISO)
- **Trazabilidad completa**: Logging de jurisdicciones consultadas para auditoría

### Características Específicas
- **Patrones legislativos**: VISTO/CONSIDERANDO/RESUELVE/ARTÍCULO Nº
- **Fórmulas judiciales**: "Considerando:", "Fallos: vol:pág", votos ministeriales
- **Compliance preservation**: Mantenimiento de información crítica legal
- **Trazabilidad completa**: Mapeo de atribución desde fuente hasta respuesta

### Componentes Anti-Sesgo
1. **Detección de Sesgo Ideológico**: Análisis multi-dimensional con lexicones españoles
2. **Preservación de Compliance**: 8 tipos de entidades legales especializadas  
3. **Motor de Trazabilidad**: Attribution mapping con detección de alucinaciones
4. **Framework de Evaluación**: 15+ métricas especializadas para IA legal

## Expansión Regional (Roadmap)

### España
- Integración con normativa europea (EU)
- Patrones de cita específicos del ordenamiento español
- Compatibilidad con sistema de fuentes jurídicas español

### LatAm
- Extensión gradual por países (MX, CO, CL, PE)
- Adaptación a sistemas jurídicos locales
- Mantenimiento de consistencia terminológica

## Principios de Diseño

### Cita Obligatoria y Trazabilidad
- **Política de cita**: Toda respuesta debe incluir referencias específicas
- **Pinpoint requerido**: Artículo/Capítulo/Sección + fuente/ID
- **Logs de trazabilidad**: Auditoría completa del proceso de generación
- **Detección de alucinaciones**: Verificación automática de coherencia

### Eficiencia y Escalabilidad
- **Modelo base**: 7B-13B parámetros (edge-deployable)
- **Índices especializados**: GraphRAG + vectorial por jurisdicción
- **Cache inteligente**: Optimización de consultas frecuentes  
- **Rate limiting**: Respeto de términos de servicio de fuentes oficiales

### Compliance y Auditoría
- **GDPR compliance**: Cumplimiento de regulaciones de privacidad
- **Audit trails**: Trazabilidad completa de decisiones del modelo
- **Bias monitoring**: Monitoreo continuo de sesgos potenciales
- **Quality assurance**: Validación automática de calidad de respuestas

### Testing y CI/CD
- **Unit tests TS**: Suite de tests minimalista sin frameworks (tsx + node:assert)
- **GitHub Actions**: CI automático con matriz Node 18/20 + cache npm
- **Type checking**: Validación TypeScript integrada (tsc --noEmit)
- **Test coverage**: Province router + jurisdiction classifier + citation enforcer
- **Fixtures**: Casos de prueba para citas válidas/inválidas argentinas

## Metodología de Implementación

### Fase 1: Fundación Argentina (Completada)
- ✅ Framework MLOps integral basado en Made-With-ML
- ✅ Sistema anti-sesgo revolucionario (110,000+ líneas)
- ✅ Ingestors provinciales (CABA, PBA, Córdoba, Mendoza, Santa Fe)
- ✅ Normalización ELI y patrones de cita argentinos

### Fase 2: Integración RAG (Completada)
- ✅ **Province-aware retrieval**: Router inteligente por jurisdicción ISO 3166-2:AR
- ✅ **Clasificador heurístico**: Detección automática de jurisdicción (boletín/geográfico/ISO)
- ✅ **Self-RAG integrado**: Decisión inteligente de recuperación con validación
- ✅ **Mapa de boletines**: Configuración centralizada con rate limiting
- 🔄 GraphRAG con comunidades legales especializadas (pendiente conexión real)
- 🔄 Citation enforcer con validación provincial (base implementada)

### Fase 3: Producción y Escalabilidad
- 📅 Deployment en Cloudflare Workers/Pages
- 📅 Monitoring y alertas automatizadas
- 📅 API pública con rate limiting
- 📅 Interfaz web para usuarios finales

### Fase 4: Expansión Regional
- 📅 Integración España (normativa UE)
- 📅 Extensión LatAm (México, Colombia, Chile)
- 📅 Soporte multilenguaje (catalán, gallego, euskera)
- 📅 Federación de índices regionales

## Métricas de Éxito

### Técnicas
- **Precisión de citas**: >95% de referencias verificables
- **Cobertura jurisdiccional**: 100% provincias argentinas principales
- **Latencia de respuesta**: <2s para consultas estándar
- **Uptime del sistema**: >99.9% disponibilidad

### Científicas  
- **Bias detection accuracy**: >90% detección de sesgos ideológicos
- **Compliance preservation**: >95% mantenimiento de información crítica
- **Traceability score**: 100% mapeo de atribución verificable
- **Hallucination detection**: <5% falsos positivos

### Impacto
- **Adopción académica**: Publicaciones en AAAI/ACL/ICML 2025
- **Validación legal**: Revisión por expertos en derecho argentino
- **Transferencia tecnológica**: Implementación en estudios jurídicos
- **Estándares industriales**: Referencia para IA legal ética