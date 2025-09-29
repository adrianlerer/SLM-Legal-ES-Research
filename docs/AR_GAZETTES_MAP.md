# Mapa de Boletines Oficiales (Argentina)

## Archivo Fuente
- **Ubicación**: `schema/ar_boletines_map.json`
- **Formato**: JSON Schema con validación estricta
- **Propósito**: Mapeo centralizado de boletines oficiales por jurisdicción ISO 3166-2:AR

## Regla Crítica
**VERIFICAR MANUALMENTE** cada `url_base` antes de habilitar fetchers.

## Estructura del Schema

### Nacional (AR)
```json
"AR": {
  "BORA": {
    "name": "Boletín Oficial de la República Argentina",
    "url_base": "https://www.boletinoficial.gob.ar/"
  }
}
```

### Provincias Principales

| Jurisdicción | Código | Boletín | URL Base | Estado |
|-------------|--------|---------|----------|--------|
| AR-C | BOCBA | Boletín Oficial CABA | https://boletinoficial.buenosaires.gob.ar/ | VERIFICAR |
| AR-B | PBA | Boletín Oficial PBA | https://boletinoficial.gba.gob.ar/ | VERIFICAR |
| AR-S | SANTAFE | Boletín Oficial Santa Fe | https://www.santafe.gob.ar/boletinoficial/ | VERIFICAR |
| AR-X | CORDOBA | Boletín Oficial Córdoba | TODO | PENDIENTE |
| AR-M | MENDOZA | Boletín Oficial Mendoza | TODO | PENDIENTE |

## Uso en Ingestors

### Patrón de Integración
Los ingestors provinciales/nacionales deben:

1. **Cargar el mapa**:
```typescript
import boletinesMap from "../schema/ar_boletines_map.json";
```

2. **Construir URLs**:
```typescript
const baseUrl = boletinesMap["AR-X"]["CORDOBA"]["url_base"];
const searchUrl = `${baseUrl}/search?q=${query}&date=${date}`;
```

3. **Normalizar fuentes en ELI**:
```typescript
const source = boletinesMap["AR-X"]["CORDOBA"]["name"];
const eliDoc = normalizeToELI({ 
  jurisdiction: "AR-X", 
  source,
  // ... otros campos
});
```

### Ejemplo en Fetcher
```typescript
// ingest/ar_provincias/cordoba_boletin.ts
import boletinesMap from "../../schema/ar_boletines_map.json";

export async function searchCordoba(params: {from?: string; to?: string; texto?: string}) {
  // TODO: verificar que url_base no sea "TODO"
  const config = boletinesMap["AR-X"]["CORDOBA"];
  if (config.url_base.startsWith("TODO")) {
    throw new Error("URL de Córdoba no verificada aún");
  }
  
  // TODO: implementar fetch real con la URL verificada
  return { 
    jurisdiction: "AR-X", 
    source: config.name,
    items: [] 
  };
}
```

## Proceso de Verificación

### Pasos Obligatorios
1. **Investigación manual**: Verificar URL oficial del boletín
2. **Testing de acceso**: Confirmar que la URL funciona y permite búsquedas
3. **Análisis de estructura**: Estudiar formato HTML/API disponible
4. **Respeto de ToS**: Revisar términos de servicio y robots.txt
5. **Actualización del schema**: Reemplazar "TODO" con URL verificada

### Criterios de Verificación
- ✅ **URL accesible**: Responde sin errores 4xx/5xx
- ✅ **Contenido oficial**: Boletín oficial gubernamental verificado
- ✅ **Búsqueda funcional**: Permite filtros por fecha/texto
- ✅ **Rate limiting**: Respeta límites de consultas por segundo
- ✅ **ToS compliance**: No viola términos de servicio

## Extensión a Nuevas Provincias

### Template para Nueva Jurisdicción
```json
"AR-{CÓDIGO}": {
  "type": "object", 
  "properties": {
    "{NOMBRE}": { 
      "type": "object", 
      "properties": {
        "name": { 
          "type": "string", 
          "const": "Boletín Oficial de la Provincia de {Nombre}" 
        },
        "url_base": { 
          "type": "string", 
          "description": "TODO (VERIFICAR URL OFICIAL)" 
        }
      }, 
      "required": ["name","url_base"] 
    }
  }
}
```

### Ejemplo: Neuquén (AR-Q)
```json
"AR-Q": {
  "type": "object", 
  "properties": {
    "NEUQUEN": { 
      "type": "object", 
      "properties": {
        "name": { "type": "string", "const": "Boletín Oficial de la Provincia del Neuquén" },
        "url_base": { "type": "string", "description": "TODO (VERIFICAR URL OFICIAL)" }
      }, 
      "required": ["name","url_base"] 
    }
  }
}
```

## Integración con Citation Enforcer

### Validación de Fuentes
El citation enforcer usa este mapa para:
- **Verificar nombres oficiales** de boletines en citas
- **Validar jurisdicciones** según códigos ISO
- **Sugerir correcciones** cuando hay errores en nombres

### Ejemplo de Validación
```typescript
// Usuario cita: "Boletín de Córdoba"
// Sistema sugiere: "Boletín Oficial de la Provincia de Córdoba" (nombre oficial del mapa)
```

## Consideraciones de Mantenimiento

### Updates Periódicos
- **Frecuencia**: Trimestral para URLs principales
- **Método**: Verificación automatizada de HTTP status
- **Alertas**: Notificar si URL cambia o deja de funcionar

### Backup de Configuración
- **Versionado**: Git tracking de cambios en el schema
- **Rollback**: Posibilidad de volver a configuración anterior
- **Testing**: Suite de tests para validar integridad del mapa

### Monitoreo de Cambios
- **Web scraping changes**: Detectar modificaciones en estructura HTML
- **API deprecations**: Monitorear cambios en endpoints oficiales
- **Legal updates**: Seguir cambios normativos que afecten publicación oficial