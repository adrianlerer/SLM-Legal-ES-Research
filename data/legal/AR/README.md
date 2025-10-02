# Datos AR (placeholder)

Estructura para pruebas de pipeline (sin contenido protegido):

## Archivos de ejemplo

### Nacional
- `BORA_EJEMPLO_2024_12_15.md` (plantilla con "VISTO/CONSIDERANDO/RESUELVE")
- `CSJN_Fallos_330_563.md` (plantilla con referencia "Fallos: 330:563")

### Provinciales
- `BOCBA_EJEMPLO.md` - Ciudad Autónoma de Buenos Aires
- `PBA_EJEMPLO.md` - Provincia de Buenos Aires  
- `CORDOBA_EJEMPLO.md` - Provincia de Córdoba
- `MENDOZA_EJEMPLO.md` - Provincia de Mendoza
- `SANTAFE_EJEMPLO.md` - Provincia de Santa Fe
- `NEUQUEN_EJEMPLO.md` - Provincia de Neuquén
- `RIONEGRO_EJEMPLO.md` - Provincia de Río Negro

Placeholders adicionales disponibles para todas las provincias según ISO 3166-2:AR.

## Metadatos

Cada archivo incluye:
- Metadatos ELI simulados (ID, fecha, status)
- Hash ficticio para testing
- Estructura típica argentina (VISTO/CONSIDERANDO/RESUELVE)
- **Validación de pinpoint**: Boletín + Artículo/Capítulo/Sección

## Propósito

Estos ejemplos sintéticos sirven para:
1. Pruebas de estructura y pipeline
2. **Validación de patrones de cita provincial**
3. Testing de normalización ELI con alias ISO
4. Desarrollo de extractores de léxico
5. **Testing del verificador de pinpoint**

## Integración con Validadores

- **Citation enforcer**: Pruebas automáticas de compliance
- **Province pinpoint**: Validación específica por jurisdicción ISO
- **Alias normalization**: Testing de conversión automática de alias

**IMPORTANTE**: No contienen información legal real, solo estructuras para desarrollo y testing del sistema anti-sesgo.