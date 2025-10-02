# Guía de 'pinpoint' por provincia (AR)

## Objetivo

Reforzar que cada respuesta con jurisdicción AR cite:
1. **El Boletín Oficial correspondiente** (BOCBA, PBA, Córdoba, etc.)
2. **Un pinpoint específico** (Artículo/Capítulo/Sección)

## Validación Automática

### Herramienta Principal
- **Archivo**: `tools/ar/pinpoint_by_province.ts`
- **Función**: `validateProvincePinpoint(answer: string, province: ProvinceCode)`
- **Integración**: Citation enforcer automático

### Códigos de Provincia Soportados

| Código ISO | Provincia | Boletín Oficial |
|------------|-----------|----------------|
| AR-C | Ciudad Autónoma de Buenos Aires | BOCBA |
| AR-B | Buenos Aires | Boletín Oficial PBA |
| AR-X | Córdoba | Boletín Oficial Córdoba |
| AR-M | Mendoza | Boletín Oficial Mendoza |
| AR-S | Santa Fe | Boletín Oficial Santa Fe |
| AR-Q | Neuquén | Boletín Oficial Neuquén |
| AR-R | Río Negro | Boletín Oficial Río Negro |
| ... | (resto de provincias) | (respectivos boletines) |

## Patrones de Validación

### Elementos Requeridos

1. **Mención del Boletín Oficial**
   - Patrón: `/(BOCBA|Boletín Oficial.*Córdoba|etc.)/i`
   - Ejemplo: "Boletín Oficial de la Ciudad Autónoma de Buenos Aires"

2. **Pinpoint Específico**
   - **Artículo**: `/(Art\.?|Artículo)\s?\d+[º°]?/i`
   - **Capítulo**: `/(Cap\.?|Capítulo)\s?[IVXLC]+/i`
   - **Sección**: `/(Secc\.?|Sección)\s?[\w\.]+/i`

### Ejemplos de Citas Válidas

#### CABA (AR-C)
```
"Según el BOCBA (Boletín Oficial de la Ciudad Autónoma de Buenos Aires), 
Art. 12, Sección II, se establece..."
```

#### Córdoba (AR-X)
```
"De acuerdo al Boletín Oficial de Córdoba, Capítulo IV, 
Artículo 7º, se dispone..."
```

#### Buenos Aires (AR-B)
```
"El Boletín Oficial de la Provincia de Buenos Aires, 
Cap. III, Art. 15, indica que..."
```

## Integración con Citation Enforcer

### Flujo de Validación

1. **Detección de jurisdicción**: Si `jurisdictionHint` empieza con "AR-"
2. **Validación provincial**: Llamada a `validateProvincePinpoint()`
3. **Resultado**: 
   - `ok: true` → Cita válida
   - `ok: false` → Error: "Cita provincial AR incompleta"

### Respuesta del Validador

```typescript
{
  ok: boolean;           // true si pasa validación
  hits: string[];        // Array de matches encontrados
}
```

## Datos de Ejemplo

### Estructura Recomendada
- **Ubicación**: `data/legal/AR/*`
- **Contenido**: Ejemplos sintéticos por provincia
- **Metadatos**: ELI (ID, fecha, estado) para testing

### Archivos de Ejemplo
- `BOCBA_EJEMPLO.md` - Ciudad Autónoma de Buenos Aires
- `CORDOBA_EJEMPLO.md` - Provincia de Córdoba
- `MENDOZA_EJEMPLO.md` - Provincia de Mendoza
- `PBA_EJEMPLO.md` - Provincia de Buenos Aires
- `SANTAFE_EJEMPLO.md` - Provincia de Santa Fe

## Consideraciones Técnicas

### Refinamiento de Patrones
- **TODO**: Afinar regex con casos reales de cada boletín
- **Método**: Análisis de corpus provincial específico
- **Objetivo**: Maximizar precisión sin falsos positivos

### Extensibilidad
- **Nuevas provincias**: Agregar a `PATTERNS` en `pinpoint_by_province.ts`
- **Nuevos tipos**: Extender `ART`, `CAP`, `SECC` según necesidades
- **Alias**: Actualizar `ar_iso_aliases.json` para nuevas variantes

## Métricas de Calidad

### Objetivos de Precisión
- **Detección de boletín**: >95% accuracy
- **Validación pinpoint**: >90% accuracy  
- **Falsos positivos**: <5%
- **Cobertura provincial**: 100% jurisdicciones principales

### Monitoreo Continuo
- **Logs de validación**: Tracking de errores por provincia
- **Feedback loop**: Mejora iterativa de patrones
- **Testing automatizado**: Suite de casos de prueba por jurisdicción