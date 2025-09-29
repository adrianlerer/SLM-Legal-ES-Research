# Notas de fetch Argentina (Nación + Provincias)

## Principios generales
- Mantener rate-limit (p.ej., 1 req/s), cache local y respeto de robots/ToS. [Verificado]
- Todos los fetchers deben implementar manejo de errores y retry con backoff exponencial
- Cache local obligatorio para evitar requests duplicados

## Fuentes nacionales
- **CSJN (Fallos)**: Jurisprudencia de la Corte Suprema de Justicia de la Nación
- **SAIJ (jurisprudencia)**: Sistema Argentino de Información Jurídica  
- **BORA (legislación)**: Boletín Oficial de la República Argentina
- **InfoLEG (normativa consolidada)**: Información Legislativa y Documental
- Sin API unificada disponible - requiere web scraping controlado [Verificado]

## Fuentes provinciales (ejemplos implementados)
- **CABA (BOCBA)**: Boletín Oficial de la Ciudad Autónoma de Buenos Aires
- **PBA**: Boletín Oficial de la Provincia de Buenos Aires  
- **Santa Fe**: Portal oficial de Santa Fe
- **Córdoba**: Boletín Oficial de la Provincia de Córdoba
- **Mendoza**: Boletín Oficial de la Provincia de Mendoza
- Cada provincia mantiene portales oficiales independientes [Verificado]

## Objetivo del sistema
Capturar léxico/estructura argentinos (nacional/federal/provincial) para:
1. **Estilo**: Patrones "VISTO/CONSIDERANDO/RESUELVE" y fórmulas judiciales
2. **Citas pinpoint**: Referencias específicas por artículo/capítulo + fuente/ID
3. **Compliance**: Trazabilidad completa desde fuente hasta respuesta final

## Consideraciones técnicas
- Rate limiting: máximo 1 request/segundo por dominio
- Cache TTL: 24 horas para contenido estático, 1 hora para búsquedas
- User-Agent: identificación como herramienta académica/investigación
- Respeto total de robots.txt y términos de servicio

## Próximos pasos
1. Implementar fetchers reales con verificación de URLs oficiales
2. Integrar con sistema de cache distribuido
3. Establecer monitoring de cambios en estructuras web
4. Crear pipeline de validación de integridad de datos