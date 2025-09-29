# Province-aware retrieval (AR)

## Funcionalidad

- Selecciona índice por jurisdicción ISO 3166-2:AR → fallback a AR nacional → ES → GLOBAL.
- Sustituir `searchIndex()` por llamadas reales a:
  1) GraphRAG (comunidades + hubs) y
  2) vectorial (embeddings multilingües).
- Registro `jurisdictionTried` para trazabilidad (auditoría).

## Flujo de Recuperación

### Orden Jerárquico
1. **Índice Provincial** (si disponible): `idx_ar_cordoba`, `idx_ar_mendoza`, etc.
2. **Índice Nacional AR**: `idx_ar_nacional` (CSJN, SAIJ, BORA, InfoLEG)
3. **Índice España**: `idx_es_espana` (doctrina comparada en castellano)
4. **Índice Global**: `idx_global_es_latam_eu` (LatAm + UE)

### Ejemplo de Uso
```typescript
const result = await retrieveProvinceAware(
  "¿Qué dice sobre conflictos de interés?", 
  "AR-X"  // Córdoba
);

// Resultado:
// {
//   jurisdictionTried: ["idx_ar_cordoba", "idx_ar_nacional", "idx_es_espana", "idx_global_es_latam_eu"],
//   hits: [...]
// }
```

## Índices Configurados

| Jurisdicción | Handle | Descripción |
|-------------|--------|-------------|
| AR | `idx_ar_nacional` | Nacional (CSJN, SAIJ, BORA, InfoLEG) |
| AR-C | `idx_ar_caba` | Ciudad Autónoma de Buenos Aires |
| AR-B | `idx_ar_pba` | Provincia de Buenos Aires |
| AR-X | `idx_ar_cordoba` | Provincia de Córdoba |
| AR-M | `idx_ar_mendoza` | Provincia de Mendoza |
| AR-S | `idx_ar_santafe` | Provincia de Santa Fe |
| ES | `idx_es_espana` | España (doctrina comparada) |
| GLOBAL | `idx_global_es_latam_eu` | LatAm + UE general |

## Integración con GraphRAG

### Stub Actual
```typescript
async function searchIndex(indexHandle: string, query: string, k = 12): Promise<RetrievalHit[]> {
  // STUB: reemplazar por llamada real
  return [{ id: `${indexHandle}::stub`, score: 0.42, meta: { preview: query.slice(0, 60) } }];
}
```

### Implementación Objetivo
```typescript
async function searchIndex(indexHandle: string, query: string, k = 12): Promise<RetrievalHit[]> {
  // 1. GraphRAG: búsqueda en comunidades legales específicas
  const graphResults = await queryGraphCommunities(indexHandle, query);
  
  // 2. Vectorial: embeddings multilingües con semantic search
  const vectorResults = await queryVectorIndex(indexHandle, query, k);
  
  // 3. Fusión y reranking por relevancia legal
  return fuseAndRerank(graphResults, vectorResults);
}
```

## Trazabilidad y Auditoría

### Registro de Intentos
- **Campo**: `jurisdictionTried: string[]`
- **Propósito**: Auditoría completa de fuentes consultadas
- **Uso**: Compliance y explicabilidad de respuestas

### Métricas de Calidad
- **Cobertura**: % de consultas con hits relevantes por jurisdicción
- **Precisión**: Relevancia de hits por índice específico
- **Latencia**: Tiempo de respuesta por tipo de índice
- **Fallback rate**: Frecuencia de uso de índices de respaldo

## Extensibilidad

### Agregar Nueva Provincia
1. Actualizar `INDEX_HANDLES` con nuevo código ISO
2. Crear índice correspondiente en infrastructure
3. Configurar ingestor provincial específico
4. Testing con casos de la nueva jurisdicción

### Ejemplo: Neuquén (AR-Q)
```typescript
const INDEX_HANDLES: Record<string, string> = {
  // ... existentes ...
  "AR-Q": "idx_ar_neuquen",  // Nuevo
  // ...
};
```